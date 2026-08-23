from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserStatusUpdate,
    UserDetailResponse,
    UserPaginatedResponse
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "",
    response_model=UserDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user with optional profile (Admin only)",
    description="Creates a new ADMIN, TEACHER, or STUDENT user along with required profile data. Protected by ADMIN role guard."
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to create a user and linked Teacher/Student profile.
    """
    return user_service.create_user_with_profile(db, user_in)


@router.get(
    "",
    response_model=UserPaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="List users with pagination and filtering (Admin only)",
    description="Retrieves a paginated list of users. Supports filtering by role, active status, and search query. Protected by ADMIN role guard."
)
def list_users(
    skip: int = Query(0, ge=0, description="Page offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by User Role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search term for username, email, name, or IDs"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to list users.
    """
    users, total = user_service.list_users(
        db, skip=skip, limit=limit, role=role, is_active=is_active, search=search
    )
    # Compute page number (1-indexed)
    page = (skip // limit) + 1 if limit > 0 else 1
    return UserPaginatedResponse(
        items=users,
        total=total,
        page=page,
        page_size=limit
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user details by ID (Admin only)",
    description="Returns full safe details for a specific user ID including attached profile details. Protected by ADMIN role guard."
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to fetch a single user by ID.
    """
    return user_service.get_user_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user details and profile (Admin only)",
    description="Updates allowed user fields and associated profile fields. Protected by ADMIN role guard."
)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to update user and profile fields.
    """
    return user_service.update_user_and_profile(db, user_id, user_in)


@router.patch(
    "/{user_id}/status",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate or deactivate user account (Admin only)",
    description="Toggles user active status (`is_active`). Deactivated users cannot log in. Protected by ADMIN role guard."
)
def update_user_status(
    user_id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Admin-only endpoint to activate or deactivate a user account.
    """
    return user_service.update_user_status(db, user_id, status_in.is_active)
