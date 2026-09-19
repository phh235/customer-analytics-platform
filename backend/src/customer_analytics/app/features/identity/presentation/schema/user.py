"""User schemas — Request/response models for user API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

# ── Request schemas ────────────────────────────────────────


class LoginRequest(BaseModel):
    """Login request body."""

    email: EmailStr = Field(
        ...,
        description="Email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Password",
        examples=["StrongPassword123!"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "StrongPassword123!",
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Refresh token request body.

    NOTE: With HTTP-only cookies, refresh token is read from cookie.
    This schema is kept for backward compatibility but is no longer used.
    """

    refresh_token: str = Field(
        ...,
        description="JWT refresh token (deprecated - now read from cookie)",
        examples=["eyJhbGciOiJIUzI1NiIs..."],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                }
            ]
        }
    }


class RegisterRequest(BaseModel):
    """Register new user (admin only)."""

    email: EmailStr = Field(
        ...,
        description="Email address",
        examples=["newuser@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (min 8 characters)",
        examples=["StrongPassword123!"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name",
        examples=["Nguyen Van A"],
    )
    role_code: str = Field(
        default="ANALYST",
        max_length=50,
        description="Role code (ADMIN, ANALYST, or MANAGER)",
        examples=["ANALYST"],
    )
    team_id: uuid.UUID | None = Field(default=None, description="Team ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newuser@example.com",
                    "password": "StrongPassword123!",
                    "full_name": "Nguyen Van A",
                    "role_code": "ANALYST",
                }
            ]
        }
    }


class UpdateUserRequest(BaseModel):
    """Update user request body (admin only)."""

    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Full name",
        examples=["Nguyen Van A Updated"],
    )
    role_code: str | None = Field(
        default=None,
        max_length=50,
        description="Role code (ADMIN, ANALYST, or MANAGER)",
        examples=["ADMIN"],
    )
    status: str | None = Field(
        default=None,
        description="Account status (ACTIVE, DISABLED)",
        examples=["ACTIVE"],
    )
    team_id: uuid.UUID | None = Field(default=None, description="Team ID")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "full_name": "Nguyen Van A Updated",
                    "role_code": "ADMIN",
                    "status": "ACTIVE",
                }
            ]
        }
    }


# ── Response schemas ───────────────────────────────────────


class UserResponse(BaseModel):
    """User info in response."""

    id: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    status: str = Field(..., description="Account status (ACTIVE, DISABLED, LOCKED)")
    role_code: str = Field(..., description="Role code")
    team_id: uuid.UUID | None = Field(default=None, description="Team ID")
    permissions: list[str] = Field(
        default_factory=list, description="List of permission codes"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")

    @classmethod
    def from_entity(cls, entity: Any) -> UserResponse:
        """Create response from entity."""
        return cls(
            id=entity.id_,
            email=entity.email,
            full_name=entity.full_name,
            status=entity.status,
            role_code=entity.role_code,
            team_id=(
                uuid.UUID(entity.team_id) if getattr(entity, "team_id", None) else None
            ),
            permissions=entity.permissions if hasattr(entity, "permissions") else [],
            created_at=entity.created_at,
            last_login_at=entity.last_login_at,
        )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "full_name": "Nguyen Van A",
                    "status": "ACTIVE",
                    "role_code": "ANALYST",
                    "permissions": [
                        "customers:read",
                        "customers:export",
                        "analytics:read",
                        "analytics:predict",
                    ],
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_login_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class TokenResponse(BaseModel):
    """Token response after login/refresh.

    access_token is returned in response body (frontend reads and stores in memory).
    refresh_token is set as HTTP-only cookie (browser auto-manages).
    """

    access_token: str = Field(..., description="JWT access token")
    role_code: str = Field(..., description="User's role code")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "role_code": "ADMIN",
                }
            ]
        },
    }


# Alias for login response
LoginResponse = TokenResponse

# Alias for refresh response
RefreshTokenResponse = TokenResponse


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Thanh cong",
                }
            ]
        },
    }


class PaginatedUsersResponse(BaseModel):
    """Paginated users list."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[UserResponse] = Field(..., description="User records")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current": 1,
                    "size": 10,
                    "total": 25,
                    "pages": 3,
                    "records": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "full_name": "Nguyen Van A",
                            "status": "ACTIVE",
                            "role_code": "ANALYST",
                            "permissions": [
                                "customers:read",
                                "customers:export",
                                "analytics:read",
                                "analytics:predict",
                            ],
                            "created_at": "2024-01-01T00:00:00Z",
                            "last_login_at": "2024-01-15T10:30:00Z",
                        }
                    ],
                }
            ]
        },
    }


# ── Error schemas ──────────────────────────────────────────


class ErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Error type")
    path: str = Field(..., description="Request path")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    details: list[dict[str, str | int | None]] | None = Field(
        default=None, description="Error details"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": 401,
                    "message": "Email hoac mat khau khong chinh xac.",
                    "error": "Unauthorized",
                    "path": "/api/v1/auth/login",
                    "timestamp": 1705312200000,
                }
            ]
        },
    }
