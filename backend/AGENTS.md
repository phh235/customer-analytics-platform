# BACKEND — FastAPI

**Python 3.13 / uv / ruff / mypy**

## OVERVIEW
FastAPI backend for customer analytics API. Src layout (`src/customer_analytics`), async SQLAlchemy 2 + PostgreSQL, structlog, centralized errors. 4-layer DDD architecture: Presentation → Application → Domain → Infrastructure.

## STRUCTURE (4-Layer DDD)
```
backend/
├── src/customer_analytics/
│   ├── main.py           # App entry → register_middleware + exception handlers + routers
│   ├── configuration/    # Cross-cutting infra
│   │   ├── __init__.py   # Re-export: settings, engine, Base, get_db, register_middleware
│   │   ├── settings.py   # pydantic-settings, env-driven, extra="forbid"
│   │   ├── dependencies.py # DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db)]
│   │   ├── database/     # async engine, session, base model, mixins
│   │   │   ├── engine.py       # create_async_engine singleton (pool, pre-ping)
│   │   │   ├── base.py         # Base(DeclarativeBase) + naming convention
│   │   │   ├── session.py      # AsyncSessionFactory + get_db + check_db_connection
│   │   │   ├── mixins.py       # UUIDPrimaryKeyMixin + TimestampMixin
│   │   │   └── __init__.py     # Re-export all public API
│   │   ├── middleware/   # HTTP middleware (one file per middleware)
│   │   │   ├── cors.py         # CORSMiddleware builder (from settings)
│   │   │   ├── request_id.py   # X-Request-ID + structlog context
│   │   │   └── __init__.py     # register_middleware(app) + re-exports
│   │   └── logging/     # Structured logging
│   │       ├── sanitizers.py   # _sanitize_sensitive_data (password/token/redaction)
│   │       └── __init__.py     # configure_logging() + get_logger()
│   ├── shared/
│   │   ├── domain/       # Empty — shared DDD domain layer
│   │   ├── application/  # Empty — shared use cases
│   │   ├── infrastructure/ # Empty — shared adapters
│   │   └── presentation/
│   │       ├── errors.py     # ErrorCode enum → status_code + message
│   │       ├── exceptions.py # AppException + 3 handlers (app/validation/general)
│   │       └── health.py     # GET /health, GET /api/v1/health
│   └── features/
│       └── identity/     # Auth/RBAC domain (4-layer DDD)
│           ├── presentation/     # Presentation Layer
│           │   ├── routes/       # API endpoints (auth_routes, user_routes)
│           │   ├── schema/       # Pydantic request/response schemas
│           │   └── dependencies.py # FastAPI dependencies (CurrentUserDep, AdminDep)
│           ├── application/      # Application Layer
│           │   ├── usecases/     # Use cases (LoginUser, CreateUser, GetUsers, etc.)
│           │   └── dto/          # Data Transfer Objects (UserCreateModel, UserReadModel)
│           ├── domain/           # Domain Layer
│           │   ├── entities/     # Domain entities (UserEntity)
│           │   ├── repositories/ # Repository interfaces (UserRepository, UserUnitOfWork)
│           │   ├── enums.py      # Domain enums (UserStatus, PermissionAction)
│           │   └── exceptions.py # Domain exceptions (UserNotFoundError, etc.)
│           └── infrastructure/   # Infrastructure Layer
│               ├── models/       # SQLAlchemy models (UserModel, RoleModel, etc.)
│               ├── repositories/ # Repository implementations (UserRepositoryImpl)
│               ├── jwt_service.py    # JWT token creation/verification
│               └── password_hasher.py # Password hashing (argon2)
├── migrations/           # Alembic (async env.py, naming conventions)
├── tests/                # pytest: unit/ integration/ e2e/ + test_health.py
├── scripts/
│   └── seed_data.py      # Seed roles, permissions, admin user
├── docs/
│   └── API.md            # API documentation
├── compose.yml           # postgres:17 + redis:7 + backend
├── alembic.ini           # script_location + ruff post-write hook
└── pyproject.toml        # deps, ruff, mypy strict, pytest config
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
| Add new domain | `src/customer_analytics/features/{domain}/` — own 4 layers |
| Add route | domain's `presentation/routes/` + register in `main.py` |
| Add use case | domain's `application/usecases/` |
| Add entity | domain's `domain/entities/` |
| Add repository | domain's `domain/repositories/` (interface) + `infrastructure/repositories/` (impl) |
| New error code | `shared/presentation/errors.py` |
| Business errors | domain's `domain/exceptions.py` — raise domain exceptions |
| Config/settings | `configuration/settings.py` — env vars, `extra="forbid"` |
| DB session | `configuration/dependencies.py` — `db: DatabaseSessionDep` |
| Migration | `uv run alembic revision --autogenerate -m "..."` then `uv run alembic upgrade head` |
| Model base | `configuration/database/base.py` — `Base` + naming convention |
| Model mixins | `configuration/database/mixins.py` — `UUIDPrimaryKeyMixin` + `TimestampMixin` |
| Middleware | `configuration/middleware/` — one file per middleware, `register_middleware(app)` |
| Logging | `configuration/logging/` — `get_logger(__name__)` |
| RBAC permissions | `features/identity/infrastructure/models/user.py` — PermissionModel, RolePermissionModel |
| Seed data | `scripts/seed_data.py` — roles, permissions, admin user |

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
- Hardcoded secrets — env only via `settings.py`
- Logging passwords/tokens — redacted by `_sanitize_sensitive_data`
- Routers querying DB directly — use application use cases + repositories
- Domain layer importing infrastructure — use dependency inversion
- Use cases directly accessing ORM models — go through repository interfaces
