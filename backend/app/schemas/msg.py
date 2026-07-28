from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Message(BaseModel):
    message: str


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ErrorDetailsSchema(BaseModel):
    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetailsSchema
