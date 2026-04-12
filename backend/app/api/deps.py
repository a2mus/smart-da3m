"""
API endpoint dependencies.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to get current active user."""
    # Add any additional checks here (e.g., user banned, etc.)
    return current_user


async def get_current_parent(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is a parent."""
    from app.models.user import UserRole

    if current_user.role != UserRole.PARENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Parent access required.",
        )
    return current_user


async def get_current_expert(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is an expert."""
    from app.models.user import UserRole

    if current_user.role != UserRole.EXPERT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Expert access required.",
        )
    return current_user


# Alias for consistency with naming conventions
get_current_expert_user = get_current_expert


async def get_current_student(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is a student."""
    from app.models.user import UserRole

    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Student access required.",
        )
    return current_user


async def get_current_parent_or_expert(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to ensure user is a parent or expert."""
    from app.models.user import UserRole

    if current_user.role not in [UserRole.PARENT, UserRole.EXPERT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Parent or Expert access required.",
        )
    return current_user
