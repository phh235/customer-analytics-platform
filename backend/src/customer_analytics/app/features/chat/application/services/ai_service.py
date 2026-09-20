"""Application service for provider-independent chat orchestration."""

from __future__ import annotations

from collections.abc import AsyncIterator

from customer_analytics.app.features.chat.domain.providers.llm_provider import (
    ChatMessage,
    LLMProvider,
)

SYSTEM_PROMPT = (
    "You are a helpful assistant for a customer analytics platform. "
    "Answer clearly and concisely. If the user asks for data you cannot access, "
    "say so instead of inventing results."
)


class AIService:
    """Build prompts and delegate generation to the configured LLM provider."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    @staticmethod
    def _messages(message: str) -> list[ChatMessage]:
        # Generic chat chỉ gửi system prompt và câu hỏi cho provider.
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

    async def chat(self, message: str) -> str:
        """Generate one complete assistant response."""
        # Trả về toàn bộ câu trả lời trong một lần.
        return await self._provider.complete(self._messages(message))

    async def stream_chat(self, message: str) -> AsyncIterator[str]:
        """Stream assistant response deltas."""
        # Stream từng phần để giao diện hiển thị sớm hơn.
        async for delta in self._provider.stream(self._messages(message)):
            yield delta
