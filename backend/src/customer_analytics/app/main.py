"""FastAPI application entry point — New DDD structure."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from customer_analytics.app.config import settings
from customer_analytics.app.features.identity.presentation.routes.auth_routes import (
    router as auth_router,
)
from customer_analytics.app.features.identity.presentation.routes.user_routes import (
    router as admin_router,
)
from customer_analytics.app.shared.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from customer_analytics.app.shared.health import router as health_router
from customer_analytics.core.logging import configure_logging
from customer_analytics.core.middleware import register_middleware

# Cấu hình logging ngay khi app được import
configure_logging()

# ── OpenAPI Metadata ────────────────────────────────────────
openapi_tags = [
    {
        "name": "Health",
        "description": "Health check endpoints",
    },
    {
        "name": "Authentication",
        "description": "Login, logout, and token management",
    },
    {
        "name": "User Management",
        "description": "User CRUD operations (ADMIN only)",
    },
]

app = FastAPI(
    title="Customer Analytics API",
    version=settings.APP_VERSION,
    description="""
## Customer Analytics Platform API

Backend API for customer segmentation and purchase value prediction.

### Authentication
All protected endpoints require a Bearer token in the Authorization header.
Get a token via `POST /api/v1/auth/login`.

### Roles
- **ADMIN**: Full access to all endpoints
- **CLIENT**: Read-only access to customer data and analytics
    """,
    openapi_tags=openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Middleware ──────────────────────────────────────
# Thứ tự: CORS (outermost) → RequestID (innermost)
register_middleware(app)

# ── Exception Handlers ──────────────────────────────
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ── Routers ─────────────────────────────────────────
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
