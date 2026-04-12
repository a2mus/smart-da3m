"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.post("/login/email", response_model=Token)
async def login_with_email(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with email and password.

    For parents and experts.
    """
    # Look up user by email
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

    # Create tokens with role claim
    additional_claims = {"role": user.role.value, "language": user.language.value}
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
    # Look up student by PIN hash
    # Note: We need to check all students since PINs are hashed
    result = await db.execute(
        select(User).where(
            User.role == UserRole.STUDENT,
            User.pin_code_hash.isnot(None),
        )
    )
    students = result.scalars().all()

    # Find student with matching PIN
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

    # Create tokens with role claim
    additional_claims = {
        "role": student.role.value,
        "language": student.language.value,
        "parent_id": str(student.parent_id) if student.parent_id else None,
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

    user_id = payload.get("sub")

    # Verify user still exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    additional_claims = {"role": user.role.value, "language": user.language.value}
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
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new parent user
    new_parent = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=UserRole.PARENT,
        language=Language.AR if request.language == "AR" else Language.FR,
    )

    db.add(new_parent)
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
    # Verify parent exists
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

    # Create new student user
    new_student = User(
        parent_id=request.parent_id,
        pin_code_hash=get_pin_hash(request.pin_code),
        role=UserRole.STUDENT,
        language=parent.language,  # Inherit parent's language preference
    )

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    return new_student


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current authenticated user information."""
    return current_user
