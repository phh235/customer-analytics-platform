# BACKEND — FastAPI

**Python 3.13 / uv / ruff / mypy**

## OVERVIEW
FastAPI backend for customer analytics API. Src layout (`src/customer_analytics`), async SQLAlchemy 2 + PostgreSQL, structlog, centralized errors. 4-layer DDD architecture: Presentation → Application → Domain → Infrastructure.

## STRUCTURE (4-Layer DDD)
```
backend/
├── src/customer_analytics/
│   ├── main.py                    # App entry → register_middleware + exception handlers + routers
│   ├── app/                       # Application layer
│   │   ├── config.py              # Settings (pydantic-settings, env-driven, extra="forbid")
│   │   ├── dependencies.py        # DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db)]
│   │   ├── main.py                # FastAPI app, middleware, handlers, router registration
│   │   ├── features/              # Domain features (each follows 4-layer DDD)
│   │   │   ├── identity/          # Auth/RBAC domain
│   │   │   │   ├── presentation/  # Routes, schema, dependencies
│   │   │   │   ├── application/   # Use cases, DTOs
│   │   │   │   ├── domain/        # Entities, repositories, enums, exceptions
│   │   │   │   └── infrastructure/# Models, repos impl, JWT, password hasher
│   │   │   ├── analytics/         # Analytics domain
│   │   │   ├── customer/          # Customer domain
│   │   │   ├── product/           # Product domain
│   │   │   ├── order/             # Order domain
│   │   │   └── import_data/       # Import & Data Quality domain
│   │   └── shared/                # Cross-feature shared code
│   │       ├── errors.py          # ErrorCode enum → status_code + message
│   │       ├── exceptions.py      # AppException + 3 handlers (app/validation/general)
│   │       ├── health.py          # GET /health, GET /api/v1/health
│   │       └── schemas.py         # Shared Pydantic schemas
│   └── core/                      # Infrastructure layer
│       ├── database/              # Async engine, session, base model, mixins
│       │   ├── engine.py          # create_async_engine singleton (pool, pre-ping)
│       │   ├── base.py            # Base(DeclarativeBase) + naming convention
│       │   ├── session.py         # AsyncSessionFactory + get_db + check_db_connection
│       │   └── mixins.py          # UUIDPrimaryKeyMixin + TimestampMixin
│       ├── middleware/             # HTTP middleware (one file per middleware)
│       │   ├── cors.py            # CORSMiddleware builder (from settings)
│       │   ├── request_id.py      # X-Request-ID + structlog context
│       │   ├── rate_limit.py      # Rate limiting middleware
│       │   └── gzip.py            # Gzip compression
│       ├── logging/               # Structured logging
│       │   ├── sanitizers.py      # _sanitize_sensitive_data (password/token/redaction)
│       │   └── __init__.py        # configure_logging() + get_logger()
│       ├── repositories/          # Base repository pattern
│       │   └── base_repository.py # Generic CRUD operations
│       ├── unit_of_work/          # Unit of Work pattern
│       │   └── unit_of_work.py    # Transaction management
│       ├── use_cases/             # Base use case pattern
│       │   └── use_case.py        # Abstract use case class
│       └── dependencies.py        # Core FastAPI dependencies
├── migrations/                    # Alembic (async env.py, naming conventions)
├── tests/                         # pytest: unit/ integration/ e2e/ + test_health.py
├── scripts/                      # Standalone maintenance/test-data scripts
│   ├── check_data.py
│   └── seed_test_data.py
├── src/customer_analytics/scripts/
│   └── seed_data.py              # Seed roles, permissions, admin user
├── docs/
│   └── API.md                    # API documentation
├── docker-compose.yml            # postgres:17 + redis:7 + backend
├── alembic.ini                   # script_location + ruff post-write hook
└── pyproject.toml                # deps, ruff, mypy strict, pytest config
```

## DDD LAYERS

### Presentation Layer (`presentation/`)
- **Routes**: HTTP endpoints, request/response handling
- **Schema**: Pydantic models for API request/response
- **Dependencies**: FastAPI dependencies (auth, permissions)

### Application Layer (`application/`)
- **Use Cases**: Business logic orchestration
- **DTOs**: Data Transfer Objects (command/query models)
- Calls domain layer, never directly accesses infrastructure

### Domain Layer (`domain/`)
- **Entities**: Core business objects (UserEntity)
- **Repositories**: Interfaces/ports (UserRepository, UserUnitOfWork)
- **Enums**: Domain enumerations (UserStatus, PermissionAction)
- **Exceptions**: Domain-specific errors
- Pure business logic, no framework dependencies

### Infrastructure Layer (`infrastructure/`)
- **Models**: SQLAlchemy ORM models
- **Repositories**: Repository implementations (UserRepositoryImpl)
- **Services**: External service implementations (JWT, password hashing)
- Implements domain interfaces

## WHERE TO LOOK
| Task | Location |
|------|----------|
| Add new domain | `app/features/{domain}/` — own 4 layers |
| Add route | domain's `presentation/routes/` + register in `app/main.py` |
| Add use case | domain's `application/usecases/` |
| Add entity | domain's `domain/entities/` |
| Add repository | domain's `domain/repositories/` (interface) + `infrastructure/repositories/` (impl) |
| New error code | `app/shared/errors.py` |
| Business errors | domain's `domain/exceptions.py` — raise domain exceptions |
| Config/settings | `app/config.py` — env vars, `extra="forbid"` |
| DB session | `app/dependencies.py` — `db: DatabaseSessionDep` |
| Migration | `uv run alembic revision --autogenerate -m "..."` then `uv run alembic upgrade head` |
| Model base | `core/database/base.py` — `Base` + naming convention |
| Model mixins | `core/database/mixins.py` — `UUIDPrimaryKeyMixin` + `TimestampMixin` |
| Middleware | `core/middleware/` — one file per middleware, `register_middleware(app)` |
| Logging | `core/logging/` — `get_logger(__name__)` |
| RBAC permissions | `features/identity/infrastructure/models/user.py` — PermissionModel, RolePermissionModel |
| Seed data | `src/customer_analytics/scripts/seed_data.py` — roles, permissions, admin user |
| Import/CSV | `features/import_data/` — upload, preview, process, consolidate |

## FEATURES
| Feature | Routes | Use Cases | Status |
|---------|--------|-----------|--------|
| Identity | Auth + User CRUD | 7 use cases | ✅ Complete |
| Customer | CRUD | 5 use cases | ✅ Complete |
| Product | CRUD | 5 use cases | ✅ Complete |
| Order | CRUD | 5 use cases | ✅ Complete |
| Analytics | RFM/Segment/Score/360/Dashboard/Predictions + CSV/XLSX export | 4 use cases | ✅ Complete |
| Import | Upload/Preview/Process/Consolidate | 4 use cases | ✅ Complete |

## CONVENTIONS
- Imports: `from customer_analytics.{module}` — absolute, never relative, never `from app.`
- Error response: `{"success": false, "error": {"code", "message", "details", "trace_id"}}`
- Success response: `{"success": true, "data": ...}`
- Use `ErrorCode` enum + `.status_code`, never raw HTTP codes
- Business errors via domain exceptions; validation handled centrally (422, field-level)
- Transaction: use case controls commit via UnitOfWork; repositories never commit
- Session-per-request via `AsyncSessionFactory`; `expire_on_commit=False`
- Docstrings Vietnamese/English mix; Vietnamese comments common
- ruff: E, F, I, UP, B selected; 88 cols; double quotes; LF; `tests/**` ignores B
- mypy strict + `disallow_untyped_defs`
- `__future__ import annotations` at top of modules

## ANTI-PATTERNS
- Raw `except Exception` — raise domain exceptions; let general handler catch the rest
- Import `from app.` or relative — always `from customer_analytics.`
- Hardcoded status codes — use `ErrorCode.status_code`
- Hardcoded secrets — env only via `config.py`
- Logging passwords/tokens — redacted by `_sanitize_sensitive_data`
- Routers querying DB directly — use application use cases + repositories
- Domain layer importing infrastructure — use dependency inversion
- Use cases directly accessing ORM models — go through repository interfaces
