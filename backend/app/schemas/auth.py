from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    """
    Credentials schema for authentication endpoint.
    Accepts either username or email as login identifier.
    """
    username: str = Field(..., description="Username or Email address", example="admin")
    password: str = Field(..., description="User password", example="AdminPass@123")


from app.schemas.user import TeacherResponse, StudentResponse


class UserResponse(BaseModel):
    """
    Sanitized user details schema for public API responses.
    Excludes sensitive fields like password_hash.
    """
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    teacher_profile: Optional[TeacherResponse] = None
    student_profile: Optional[StudentResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """
    JWT Access Token response structure.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifespan in seconds")
    user: UserResponse


class RoleTestResponse(BaseModel):
    """
    Response schema for role authorization testing endpoints.
    """
    message: str
    user_id: int
    username: str
    role: UserRole
