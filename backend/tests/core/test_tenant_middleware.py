"""
Unit and integration tests for tenant middleware, context lifecycle, and automatic ORM query filtering.
"""

import uuid
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from fastapi import FastAPI, Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token
from app.core.tenant import (
    get_active_organization_id,
    get_optional_active_organization_id,
    reset_active_organization_id,
    set_active_organization_id,
    setup_tenant_query_filter,
)
from app.core.tenant_middleware import TenantMiddleware
from app.db.session import Base
from app.models.content import Module
from app.models.organization import Organization, OrganizationType


@pytest.fixture(autouse=True)
def setup_filter():
    setup_tenant_query_filter()


def test_contextvar_lifecycle():
    assert get_optional_active_organization_id() is None
    with pytest.raises(RuntimeError, match="No active organization context set"):
        get_active_organization_id()

    org_id = uuid.uuid4()
    token = set_active_organization_id(org_id)
    assert get_active_organization_id() == org_id
    assert get_optional_active_organization_id() == org_id

    reset_active_organization_id(token)
    assert get_optional_active_organization_id() is None


@pytest.fixture
def app_with_tenant_middleware() -> FastAPI:
    app = FastAPI()
    app.add_middleware(TenantMiddleware)

    @app.get("/test-tenant")
    async def test_endpoint():
        org_id = get_active_organization_id()
        return {"active_organization_id": str(org_id)}

    @app.get("/public")
    async def public_endpoint():
        org_id = get_optional_active_organization_id()
        return {"active_organization_id": str(org_id) if org_id else None}

    return app


@pytest.mark.asyncio
async def test_tenant_middleware_valid_header_and_jwt(app_with_tenant_middleware: FastAPI):
    org_id_1 = uuid.uuid4()
    org_id_2 = uuid.uuid4()
    token = create_access_token(
        subject=str(uuid.uuid4()),
        additional_claims={
            "organizations": [
                {"id": str(org_id_1), "role": "EXPERT"},
                {"id": str(org_id_2), "role": "PARENT"},
            ]
        },
    )

    async with AsyncClient(
        transport=ASGITransport(app=app_with_tenant_middleware), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/test-tenant",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Organization-Id": str(org_id_1),
            },
        )
        assert response.status_code == 200
        assert response.json() == {"active_organization_id": str(org_id_1)}


@pytest.mark.asyncio
async def test_tenant_middleware_unauthorized_org_returns_403(app_with_tenant_middleware: FastAPI):
    allowed_org = uuid.uuid4()
    unauthorized_org = uuid.uuid4()
    token = create_access_token(
        subject=str(uuid.uuid4()),
        additional_claims={
            "organizations": [{"id": str(allowed_org), "role": "EXPERT"}]
        },
    )

    async with AsyncClient(
        transport=ASGITransport(app=app_with_tenant_middleware), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/test-tenant",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Organization-Id": str(unauthorized_org),
            },
        )
        assert response.status_code == 403
        assert "not a member" in response.json()["detail"]


@pytest.mark.asyncio
async def test_tenant_middleware_defaults_to_single_org(app_with_tenant_middleware: FastAPI):
    single_org = uuid.uuid4()
    token = create_access_token(
        subject=str(uuid.uuid4()),
        additional_claims={
            "organizations": [{"id": str(single_org), "role": "STUDENT"}]
        },
    )

    async with AsyncClient(
        transport=ASGITransport(app=app_with_tenant_middleware), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/test-tenant",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == {"active_organization_id": str(single_org)}


@pytest_asyncio.fixture
async def async_db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        async_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_automatic_query_filtering(db_session: AsyncSession):
    org_a = Organization(id=uuid.uuid4(), name="Org A", type=OrganizationType.SCHOOL)
    org_b = Organization(id=uuid.uuid4(), name="Org B", type=OrganizationType.HOUSEHOLD)
    db_session.add_all([org_a, org_b])
    await db_session.commit()

    mod_a = Module(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        subject="Math",
        grade_level="Y1-2",
        domain="Numbers",
        competency_id="MATH-01",
        is_shared=False,
    )
    mod_b = Module(
        id=uuid.uuid4(),
        organization_id=org_b.id,
        subject="Math",
        grade_level="Y1-2",
        domain="Numbers",
        competency_id="MATH-02",
        is_shared=False,
    )
    mod_shared = Module(
        id=uuid.uuid4(),
        organization_id=org_a.id,
        subject="Math",
        grade_level="Y1-2",
        domain="Numbers",
        competency_id="MATH-03",
        is_shared=True,
    )
    db_session.add_all([mod_a, mod_b, mod_shared])
    await db_session.commit()

    # Query without active context must raise RuntimeError
    token = set_active_organization_id(None)
    with pytest.raises(RuntimeError, match="No active organization context set"):
        await db_session.execute(select(Module))

    # Query with skip_tenant_filter=True bypasses RuntimeError and returns all 3 modules
    res_skip = await db_session.execute(
        select(Module).execution_options(skip_tenant_filter=True)
    )
    all_mods = res_skip.scalars().all()
    assert len(all_mods) == 3

    # Query with Org B context returns Org B module + Shared module (2 total)
    set_active_organization_id(org_b.id)
    res_b = await db_session.execute(select(Module))
    mods_b = res_b.scalars().all()
    assert len(mods_b) == 2
    mod_ids_b = {m.id for m in mods_b}
    assert mod_b.id in mod_ids_b
    assert mod_shared.id in mod_ids_b

    # Query with Org A context returns Org A module + Shared module (2 total)
    set_active_organization_id(org_a.id)
    res_a = await db_session.execute(select(Module))
    mods_a = res_a.scalars().all()
    assert len(mods_a) == 2
    mod_ids_a = {m.id for m in mods_a}
    assert mod_a.id in mod_ids_a
    assert mod_shared.id in mod_ids_a

    reset_active_organization_id(token)
