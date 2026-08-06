"""Base use case interface — Abstract base for all use cases."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseUseCase[Input, Output](ABC):
    """Abstract base use case interface.

    Defines the contract for all use cases in the application.
    """

    @abstractmethod
    async def __call__(self, args: Input) -> Output:
        """Execute the use case."""
        raise NotImplementedError()
