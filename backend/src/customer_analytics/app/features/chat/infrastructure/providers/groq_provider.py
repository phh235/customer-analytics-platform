"""Groq implementation of the chat provider contract."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, cast

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncGroq,
    RateLimitError,
)

from customer_analytics.app.config import Settings
from customer_analytics.app.features.chat.domain.providers.llm_provider import (
    ChatMessage,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class GroqProvider:
    """Reuse one async Groq client for the lifetime of the application."""

    def __init__(self, config: Settings) -> None:
        if not config.GROQ_API_KEY:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is not configured.",
            )

        self._config = config
        self._client = AsyncGroq(
            api_key=config.GROQ_API_KEY,
            timeout=config.GROQ_TIMEOUT_SECONDS,
            max_retries=0,
        )

    def _request_options(
        self,
        messages: list[ChatMessage],
        *,
        stream: bool = False,
        response_format: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Build a compatible request for the configured Groq model."""
        options: dict[str, Any] = {
            "model": self._config.GROQ_MODEL,
            "messages": cast(Any, messages),
            "temperature": self._config.GROQ_TEMPERATURE,
            "max_completion_tokens": self._config.GROQ_MAX_COMPLETION_TOKENS,
            "stream": stream,
        }
        model = self._config.GROQ_MODEL
        supports_reasoning_controls = model.startswith("openai/gpt-oss-") or (
            model == "qwen/qwen3.8-27b"
        )
        if supports_reasoning_controls:
            options["reasoning_format"] = self._config.GROQ_REASONING_FORMAT
            options["reasoning_effort"] = self._config.GROQ_REASONING_EFFORT
        if response_format is not None:
            options["response_format"] = response_format
        return options

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Request a non-streaming completion from Groq."""
        try:
            response = await self._client.chat.completions.create(
                **self._request_options(messages, response_format=response_format)
            )
        except (APITimeoutError, APIConnectionError) as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily unavailable.",
            ) from exc
        except RateLimitError as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily busy. Please try again shortly.",
            ) from exc
        except APIStatusError as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service returned an error.",
            ) from exc
        except Exception as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily unavailable.",
            ) from exc

        content = cast(
            str | None,
            response.choices[0].message.content if response.choices else None,
        )
        if not content:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service returned an empty response.",
            )
        return content

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        """Yield response deltas from a Groq streaming completion."""
        try:
            stream = await self._client.chat.completions.create(
                **self._request_options(messages, stream=True)
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except (APITimeoutError, APIConnectionError) as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily unavailable.",
            ) from exc
        except RateLimitError as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily busy. Please try again shortly.",
            ) from exc
        except APIStatusError as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service returned an error.",
            ) from exc
        except Exception as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="AI service is temporarily unavailable.",
            ) from exc
