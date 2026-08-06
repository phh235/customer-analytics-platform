"""User common models — Shared models for user operations."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TokenModel(BaseModel):
    """Token response model."""

    token_type: str = Field(default="Bearer", description="Token type")
    access_token: str = Field(..., description="JWT access token")
    expires_in: int = Field(..., description="Token expiration in seconds")
    refresh_token: str = Field(..., description="Refresh token")


class LoginModel(BaseModel):
    """Login request model."""

    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class MessageModel(BaseModel):
    """Generic message response model."""

    message: str = Field(..., description="Response message")
