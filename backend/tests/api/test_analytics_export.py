"""
Unit and integration tests for Report Export (PDF/CSV) & Tenant Isolation (Story 9.3).
"""

import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.tenant import set_active_organization_id
from app.models.diagnostic import CompetencyProfile, MasteryLevel
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import User, UserRole
from app.services.analytics_service import AnalyticsService
from app.services.report_exporter import ReportExporter


@pytest.mark.asyncio
async def test_report_exporter_csv_heatmap(db: AsyncSession):
    exporter = ReportExporter(db)
    org_id = uuid.uuid4()
    set_active_organization_id(org_id)
    student = User(
        id=uuid.uuid4(),
        email=f"student_{uuid.uuid4().hex[:8]}@example.com",
        role=UserRole.STUDENT,
        hashed_password="hash",
    )
    db.add(student)
    await db.commit()

    member = OrganizationMember(
        user_id=student.id,
        organization_id=org_id,
        role=UserRole.STUDENT,
    )
    db.add(member)
    await db.commit()

    profile = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=student.id,
        organization_id=org_id,
        competency_id="COMP_MATH_01",
        mastery_level=MasteryLevel.PROFICIENT,
        p_learned=0.85,
    )
    db.add(profile)
    await db.commit()

    filepath = await exporter.export_csv(
        report_type="heatmap",
        organization_id=org_id,
    )
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        assert "student_id,competency_id,mastery_level,p_learned,last_assessed" in content
        assert "COMP_MATH_01" in content


@pytest.mark.asyncio
async def test_report_exporter_pdf_heatmap(db: AsyncSession):
    exporter = ReportExporter(db)
    org_id = uuid.uuid4()
    set_active_organization_id(org_id)
    filepath = await exporter.export_pdf(
        report_type="heatmap",
        organization_id=org_id,
    )
    assert os.path.exists(filepath)
    assert filepath.endswith(".pdf") or filepath.endswith(".txt")


@pytest.mark.asyncio
async def test_analytics_service_export_tenant_isolation(db: AsyncSession):
    org_a = uuid.uuid4()
    org_b = uuid.uuid4()

    student_a = User(
        email=f"st_a_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
    )
    student_b = User(
        email=f"st_b_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hash",
        role=UserRole.STUDENT,
    )
    db.add_all([student_a, student_b])
    await db.commit()

    mem_a = OrganizationMember(user_id=student_a.id, organization_id=org_a, role=UserRole.STUDENT)
    mem_b = OrganizationMember(user_id=student_b.id, organization_id=org_b, role=UserRole.STUDENT)
    db.add_all([mem_a, mem_b])
    await db.commit()

    cp_a = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=student_a.id,
        organization_id=org_a,
        competency_id="COMP-ORGA",
        mastery_level=MasteryLevel.MASTERED,
        p_learned=0.95,
    )
    cp_b = CompetencyProfile(
        id=uuid.uuid4(),
        student_id=student_b.id,
        organization_id=org_b,
        competency_id="COMP-ORGB",
        mastery_level=MasteryLevel.MASTERED,
        p_learned=0.95,
    )
    db.add_all([cp_a, cp_b])
    await db.commit()

    service = AnalyticsService(db)
    file_path = await service.export_report(
        organization_id=org_a,
        report_type="heatmap",
        export_format="csv",
    )

    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert str(student_a.id) in content
    assert "COMP-ORGA" in content
    assert str(student_b.id) not in content
    assert "COMP-ORGB" not in content


@pytest.mark.asyncio
async def test_export_analytics_post_endpoint(async_client: AsyncClient, db: AsyncSession):
    org = Organization(name="Export Test Org", type=OrganizationType.SCHOOL)
    db.add(org)
    await db.commit()

    expert = User(
        email=f"expert_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.EXPERT,
    )
    db.add(expert)
    await db.commit()

    member = OrganizationMember(
        user_id=expert.id,
        organization_id=org.id,
        role=UserRole.EXPERT,
    )
    db.add(member)
    await db.commit()

    token = create_access_token(subject=expert.id, additional_claims={"org_id": str(org.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    response = await async_client.post(
        "/api/v1/analytics/export",
        json={"format": "csv", "report_type": "heatmap"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["format"] == "csv"
    assert "file_path" in data


@pytest.mark.asyncio
async def test_export_analytics_get_endpoint(async_client: AsyncClient, db: AsyncSession):
    org = Organization(name="Export GET Test Org", type=OrganizationType.SCHOOL)
    db.add(org)
    await db.commit()

    expert = User(
        email=f"expert_{uuid.uuid4().hex[:8]}@test.com",
        hashed_password="hashed_password",
        role=UserRole.EXPERT,
    )
    db.add(expert)
    await db.commit()

    member = OrganizationMember(
        user_id=expert.id,
        organization_id=org.id,
        role=UserRole.EXPERT,
    )
    db.add(member)
    await db.commit()

    token = create_access_token(subject=expert.id, additional_claims={"org_id": str(org.id)})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organization-ID": str(org.id),
    }

    response = await async_client.get(
        "/api/v1/analytics/export?format=csv&report_type=heatmap",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "student_id,competency_id,mastery_level,p_learned,last_assessed" in response.text
