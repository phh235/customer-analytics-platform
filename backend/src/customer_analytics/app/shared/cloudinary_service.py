"""Cloudinary image upload service shared by feature routes."""

from __future__ import annotations

import io
import uuid

import cloudinary
import cloudinary.uploader

from customer_analytics.app.config import settings
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class CloudinaryImageService:
    """Upload image bytes to a configured Cloudinary folder."""

    def __init__(self, folder: str) -> None:
        self.folder = folder

    async def upload(self, content: bytes, filename: str | None) -> str:
        """Upload image bytes and return its secure URL."""
        if not settings.cloudinary_is_configured:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Dịch vụ lưu trữ ảnh chưa được cấu hình.",
            )

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        try:
            result = cloudinary.uploader.upload(
                io.BytesIO(content),
                folder=self.folder,
                public_id=f"image-{uuid.uuid4().hex}",
                resource_type="image",
                use_filename=False,
                unique_filename=True,
                overwrite=False,
            )
        except Exception as error:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Không thể tải ảnh lên Cloudinary.",
            ) from error

        secure_url = result.get("secure_url")
        if not isinstance(secure_url, str) or not secure_url:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Cloudinary không trả về URL ảnh hợp lệ.",
            )
        return secure_url
