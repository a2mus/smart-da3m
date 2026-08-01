"""
Authentication API endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_pin_hash,
    verify_password,
    verify_pin,
    verify_token,
)
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.organization import Organization, OrganizationMember, OrganizationType
from app.models.user import Language, User, UserRole
from app.schemas.user import (
    LoginRequest,
    ParentRegisterRequest,
    RefreshRequest,
    StudentCreate,
    StudentPinLogin,
    Token,
    UserResponse,
)

router = APIRouter()


async def get_user_organizations_claims(
    user: User,
    db: AsyncSession,
) -> list[dict]:
    """Retrieve organization membership claims [{id, role, type}] for user.

    If a parent/user has no organization memberships, auto-create a HOUSEHOLD org.
    If a student has no organization memberships, link to parent's household org.
    """
    stmt = (
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.organization))
        .where(OrganizationMember.user_id == user.id)
        .execution_options(skip_tenant_filter=True)
    )
    result = await db.execute(stmt)
    memberships = result.scalars().all()

    if not memberships:
        if user.role == UserRole.STUDENT and user.parent_id:
            parent_stmt = (
                select(OrganizationMember)
                .options(selectinload(OrganizationMember.organization))
                .where(OrganizationMember.user_id == user.parent_id)
                .execution_options(skip_tenant_filter=True)
            )
            parent_res = await db.execute(parent_stmt)
            parent_memberships = parent_res.scalars().all()
            parent_org_id = None
            for pm in parent_memberships:
                if pm.organization and pm.organization.type == OrganizationType.HOUSEHOLD:
                    parent_org_id = pm.organization_id
                    break
            if not parent_org_id and parent_memberships:
                parent_org_id = parent_memberships[0].organization_id

            if not parent_org_id:
                parent_user_res = await db.execute(select(User).where(User.id == user.parent_id))
                parent_user = parent_user_res.scalar_one_or_none()
                parent_name = parent_user.email if (parent_user and parent_user.email) else "Parent"
                household_org = Organization(
                    name=f"{parent_name}'s Household",
                    type=OrganizationType.HOUSEHOLD,
                )
                db.add(household_org)
                await db.flush()

                parent_member = OrganizationMember(
                    user_id=user.parent_id,
                    organization_id=household_org.id,
                    role=UserRole.PARENT,
                )
                db.add(parent_member)
                parent_org_id = household_org.id

            student_member = OrganizationMember(
                user_id=user.id,
                organization_id=parent_org_id,
                role=UserRole.STUDENT,
            )
            db.add(student_member)
            await db.commit()

            result = await db.execute(stmt)
            memberships = result.scalars().all()
        else:
            org_name = f"{user.email}'s Household" if user.email else "Household Organization"
            household_org = Organization(
                name=org_name,
                type=OrganizationType.HOUSEHOLD,
            )
            db.add(household_org)
            await db.flush()

            new_member = OrganizationMember(
                user_id=user.id,
                organization_id=household_org.id,
                role=user.role,
            )
            db.add(new_member)
            await db.commit()

            result = await db.execute(stmt)
            memberships = result.scalars().all()

    claims = []
    for m in memberships:
        claims.append(
            {
                "id": str(m.organization_id),
                "role": m.role.value if hasattr(m.role, "value") else str(m.role),
                "type": m.organization.type.value
                if (m.organization and hasattr(m.organization.type, "value"))
                else str(m.organization.type if m.organization else "HOUSEHOLD"),
            }
        )
    return claims


@router.post("/login/email", response_model=Token)
async def login_with_email(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with email and password.

    For parents and experts.
    """
    result = await db.execute(
        select(User).where(
            User.email == credentials.email,
            User.role.in_([UserRole.PARENT, UserRole.EXPERT]),
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    org_claims = await get_user_organizations_claims(user, db)
    additional_claims = {
        "role": user.role.value,
        "language": user.language.value,
        "organizations": org_claims,
    }
    access_token = create_access_token(
        subject=str(user.id), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/pin", response_model=Token)
async def login_with_pin(
    credentials: StudentPinLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate student with PIN code.

    For students logging in via parent-generated PIN.
    """
    result = await db.execute(
        select(User).where(
            User.role == UserRole.STUDENT,
            User.pin_code_hash.isnot(None),
        )
    )
    students = result.scalars().all()

    student = None
    for s in students:
        if verify_pin(credentials.pin_code, s.pin_code_hash):
            student = s
            break

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PIN code",
            headers={"WWW-Authenticate": "Bearer"},
        )

    org_claims = await get_user_organizations_claims(student, db)
    additional_claims = {
        "role": student.role.value,
        "language": student.language.value,
        "parent_id": str(student.parent_id) if student.parent_id else None,
        "organizations": org_claims,
    }
    access_token = create_access_token(
        subject=str(student.id), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(subject=str(student.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    payload = verify_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_raw = payload.get("sub")
    try:
        user_id = UUID(str(user_id_raw)) if user_id_raw else None
    except ValueError:
        user_id = None

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    org_claims = await get_user_organizations_claims(user, db)
    additional_claims = {
        "role": user.role.value,
        "language": user.language.value,
        "organizations": org_claims,
    }
    access_token = create_access_token(
        subject=str(user.id), additional_claims=additional_claims
    )
    new_refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout():
    """Logout user.

    Note: With JWTs, actual token revocation requires a blacklist.
    For MVP, clients simply discard tokens.
    """
    return {"message": "Successfully logged out"}


@router.post("/register/parent", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_parent(
    request: ParentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new parent account."""
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_parent = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=UserRole.PARENT,
        language=Language.AR if request.language == "AR" else Language.FR,
    )

    db.add(new_parent)
    await db.flush()

    household_org = Organization(
        name=f"{request.email}'s Household",
        type=OrganizationType.HOUSEHOLD,
    )
    db.add(household_org)
    await db.flush()

    org_member = OrganizationMember(
        user_id=new_parent.id,
        organization_id=household_org.id,
        role=UserRole.PARENT,
    )
    db.add(org_member)
    await db.commit()
    await db.refresh(new_parent)

    return new_parent


@router.post("/register/student", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_student(
    request: StudentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new student (child) account.

    Requires parent to be authenticated (parent_id is set from token in real implementation).
    """
    result = await db.execute(
        select(User).where(
            User.id == request.parent_id,
            User.role == UserRole.PARENT,
        )
    )
    parent = result.scalar_one_or_none()

    if not parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent not found",
        )

    new_student = User(
        parent_id=request.parent_id,
        pin_code_hash=get_pin_hash(request.pin_code),
        role=UserRole.STUDENT,
        language=parent.language,
    )

    db.add(new_student)
    await db.flush()

    parent_stmt = (
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.organization))
        .where(OrganizationMember.user_id == request.parent_id)
        .execution_options(skip_tenant_filter=True)
    )
    parent_res = await db.execute(parent_stmt)
    parent_memberships = parent_res.scalars().all()
    parent_org_id = None
    for pm in parent_memberships:
        if pm.organization and pm.organization.type == OrganizationType.HOUSEHOLD:
            parent_org_id = pm.organization_id
            break
    if not parent_org_id and parent_memberships:
        parent_org_id = parent_memberships[0].organization_id

    if not parent_org_id:
        household_org = Organization(
            name=f"{parent.email}'s Household" if parent.email else "Household",
            type=OrganizationType.HOUSEHOLD,
        )
        db.add(household_org)
        await db.flush()

        parent_member = OrganizationMember(
            user_id=parent.id,
            organization_id=household_org.id,
            role=UserRole.PARENT,
        )
        db.add(parent_member)
        parent_org_id = household_org.id

    student_member = OrganizationMember(
        user_id=new_student.id,
        organization_id=parent_org_id,
        role=UserRole.STUDENT,
    )
    db.add(student_member)
    await db.commit()
    await db.refresh(new_student)

    return new_student


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current authenticated user information."""
    return current_user
