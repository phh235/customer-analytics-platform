"""User command models — Input models for user operations."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserCreateModel(BaseModel):
    """Model for creating a new user."""

    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    role_code: str = Field(default="ANALYST", max_length=50, description="Role code")
    team_id: str | None = Field(default=None, max_length=36, description="Team ID")


class UserUpdateModel(BaseModel):
    """Model for updating user information."""

    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    role_code: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None)
    team_id: str | None = Field(default=None, max_length=36, description="Team ID")


class UserDisableModel(BaseModel):
    """Model for disabling a user."""

    user_id: str
    current_user_id: str


class UserEnableModel(BaseModel):
    """Model for enabling a user."""

    user_id: str
