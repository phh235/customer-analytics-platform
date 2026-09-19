"""FastAPI application entry point — New DDD structure."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.middleware.sessions import SessionMiddleware

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.presentation.routes import (
    analytics_routes,
)
from customer_analytics.app.features.customer.presentation.routes import (
    customer_routes,
)
from customer_analytics.app.features.identity.presentation.routes.auth_routes import (
    router as auth_router,
)
from customer_analytics.app.features.identity.presentation.routes.oauth_routes import (
    router as oauth_router,
)
from customer_analytics.app.features.identity.presentation.routes.user_routes import (
    router as admin_router,
)
from customer_analytics.app.features.product.presentation.routes.product_routes import (
    router as product_router,
)
from customer_analytics.app.features.order.presentation.routes.order_routes import (
    router as order_router,
)
from customer_analytics.app.features.import_data.presentation.routes.import_routes import (
    router as import_router,
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
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)

# ── Exception Handlers ──────────────────────────────
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ── Routers ─────────────────────────────────────────
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(admin_router)
app.include_router(customer_routes.router)
app.include_router(analytics_routes.router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(import_router)
