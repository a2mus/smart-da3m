"""
Tenant isolation middleware for header extraction and organization membership validation.
"""

from typing import List, Optional, Set
from uuid import UUID

from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import verify_token
from app.core.tenant import reset_active_organization_id, set_active_organization_id


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts X-Organization-Id header and JWT organization claims,
    validates organization membership, and sets the request-scoped active organization context.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        org_header = request.headers.get("x-organization-id") or request.headers.get(
            "X-Organization-Id"
        )
        auth_header = request.headers.get("authorization") or request.headers.get(
            "Authorization"
        )

        requested_org_id: Optional[UUID] = None
        if org_header:
            try:
                requested_org_id = UUID(org_header)
            except ValueError:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid X-Organization-Id header format"},
                )

        jwt_payload: Optional[dict] = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            jwt_payload = verify_token(token)

        allowed_org_ids: Set[UUID] = set()
        if jwt_payload and jwt_payload.get("type") == "access":
            orgs_claim = jwt_payload.get("organizations", [])
            for item in orgs_claim:
                if isinstance(item, dict) and "id" in item:
                    try:
                        allowed_org_ids.add(UUID(str(item["id"])))
                    except ValueError:
                        pass
                elif isinstance(item, (str, UUID)):
                    try:
                        allowed_org_ids.add(UUID(str(item)))
                    except ValueError:
                        pass
            
            single_org = jwt_payload.get("organization_id")
            if single_org:
                try:
                    allowed_org_ids.add(UUID(str(single_org)))
                except ValueError:
                    pass

        target_org_id: Optional[UUID] = None

        if requested_org_id:
            if jwt_payload and allowed_org_ids and requested_org_id not in allowed_org_ids:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "User is not a member of the specified organization"
                    },
                )
            target_org_id = requested_org_id
        else:
            if len(allowed_org_ids) == 1:
                target_org_id = next(iter(allowed_org_ids))
            elif jwt_payload and jwt_payload.get("organization_id"):
                try:
                    target_org_id = UUID(str(jwt_payload["organization_id"]))
                except ValueError:
                    pass

        context_token = set_active_organization_id(target_org_id)
        try:
            response = await call_next(request)
            return response
        finally:
            reset_active_organization_id(context_token)
