"""HTTP schemas for the chat API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """A single user message sent to the assistant."""

    message: str = Field(min_length=1, max_length=10_000)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        """Reject whitespace-only prompts and trim accidental outer spaces."""
        normalized = value.strip()
        if not normalized:
            raise ValueError(
                "Message must contain at least one non-whitespace character"
            )
        return normalized


class ChatResponse(BaseModel):
    """A complete assistant response."""

    message: str = Field(min_length=1)
