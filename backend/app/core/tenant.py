"""
Tenant context management and automatic ORM query filtering.
"""

from contextvars import ContextVar, Token
from typing import Optional
from uuid import UUID

from sqlalchemy import event, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# Request-scoped active organization context variable
_active_organization_id: ContextVar[Optional[UUID]] = ContextVar(
    "active_organization_id", default=None
)

_listener_registered = False


def get_active_organization_id() -> UUID:
    """
    Retrieve the current request's active organization ID.
    Raises RuntimeError if no active organization context is set.
    """
    org_id = _active_organization_id.get()
    if org_id is None:
        raise RuntimeError("No active organization context set")
    return org_id


def get_optional_active_organization_id() -> Optional[UUID]:
    """
    Retrieve the current active organization ID, or None if not set.
    """
    return _active_organization_id.get()


def set_active_organization_id(org_id: Optional[UUID]) -> Token:
    """
    Set the request-scoped active organization ID. Returns context token for reset.
    """
    return _active_organization_id.set(org_id)


def reset_active_organization_id(token: Token) -> None:
    """
    Reset the active organization ID context to its previous state.
    """
    _active_organization_id.reset(token)


def setup_tenant_query_filter() -> None:
    """
    Register automatic tenant query filter event listener on SQLAlchemy ORM sessions.
    """
    global _listener_registered
    if _listener_registered:
        return

    @event.listens_for(Session, "do_orm_execute")
    def _tenant_query_filter(execute_state):
        if (
            execute_state.is_select
            and not execute_state.execution_options.get("skip_tenant_filter", False)
        ):
            for mapper in execute_state.all_mappers:
                cls = mapper.class_
                if hasattr(cls, "organization_id"):
                    org_id = get_active_organization_id()
                    if hasattr(cls, "is_shared"):
                        filter_cond = or_(
                            cls.organization_id == org_id, cls.is_shared == True
                        )
                    else:
                        filter_cond = cls.organization_id == org_id
                    execute_state.statement = execute_state.statement.where(
                        filter_cond
                    )

    _listener_registered = True
