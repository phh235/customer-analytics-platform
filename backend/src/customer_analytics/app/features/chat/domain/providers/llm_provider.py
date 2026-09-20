"""Provider contract for chat-capable language models."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, TypedDict


class ChatMessage(TypedDict):
    """A message accepted by a chat completion provider."""

    role: str
    content: str


class LLMProvider(Protocol):
    """Async interface used by the application chat service."""

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Return a complete assistant response."""
        ...

    def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Yield assistant response deltas as they are generated."""
        ...
