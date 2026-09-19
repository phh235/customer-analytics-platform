# Repository Guidelines

## Project Overview

Customer Analytics Platform is a pnpm/uv monorepo for customer segmentation and
purchase-value prediction. The React/Vite frontend is only partially backed by
the API today: authentication and user management use the FastAPI backend;
several product, customer, category, and dashboard screens still use local
sample data.

## Architecture & Data Flow

The normal server-backed path is:

`frontend/src/main.tsx` → global providers and React Router → route guards,
Zustand auth, TanStack Query hooks, and typed Axios clients → FastAPI routers →
permission dependencies and application use cases → domain repository
interfaces → async SQLAlchemy repositories/ORM models → PostgreSQL.

### Frontend

- `frontend/src/main.tsx` mounts `AppProviders` and `RouterProvider`.
- `frontend/src/router.tsx` defines lazy-loaded layouts and role-protected
  routes. Authorization policy lives in
  `frontend/src/lib/auth-routing.ts`; guards are in
  `frontend/src/features/auth/route-guards.tsx`.
- `frontend/src/api/client.ts` uses `VITE_API_URL` or `/api/v1`, sends
  credentials, keeps access tokens in memory, and performs one shared refresh
  request for concurrent 401 responses. Refresh tokens are HTTP-only backend
  cookies.
- `frontend/src/hooks/use-user-management.ts` is the representative
  server-backed query/mutation pattern. Use typed API modules plus hooks for new
  backend-backed screens; do not extend the static sample-data pattern.

### Backend

The active package is `backend/src/customer_analytics` (not `backend/app`).
`customer_analytics.main:app` re-exports the app composed in
`customer_analytics.app.main`.

Each feature under `app/features/` follows four layers:

1. `presentation`: routes, request/response schemas, and FastAPI dependencies.
2. `application`: use cases and DTOs; orchestrates business operations.
3. `domain`: entities, enums, exceptions, and repository interfaces; keep it
   framework-independent.
4. `infrastructure`: SQLAlchemy models, repository implementations, and
   external services.

`app/main.py` registers health, identity/auth, customer, product, order,
analytics, and import routers, plus middleware and centralized exception
handlers. `core/` owns database, middleware, logging, repositories, unit of
work, and shared infrastructure.

## Key Directories

- `frontend/src/pages/`: route-level auth, client, and admin screens.
- `frontend/src/layouts/`: route shells and `Outlet` layouts.
- `frontend/src/features/`: feature-local UI and auth guards.
- `frontend/src/components/ui/`: shadcn/Base UI primitives;
  `components/common/` and feature folders hold shared controls.
- `frontend/src/api/`: Axios client and typed endpoint modules.
- `frontend/src/hooks/`, `stores/`, `lib/`, `types/`: reusable hooks, Zustand
  state, pure/domain helpers, and shared types.
- `backend/src/customer_analytics/app/features/`: identity, customer, product,
  order, analytics, and `import_data` vertical slices.
- `backend/src/customer_analytics/app/shared/`: error codes, exception
  handlers, health, and shared Pydantic schemas.
- `backend/src/customer_analytics/core/`: async database/session setup,
  middleware, structured logging, generic repositories, and unit of work.
- `backend/migrations/`: Alembic environment and revisions.
- `backend/tests/`: pytest unit tests and health endpoint tests.
- `backend/scripts/`: test-data generation and database inspection helpers.
- `backend/src/customer_analytics/scripts/`: application seed data.

## Development Commands

Run root commands from the repository root:

```bash
pnpm setup
pnpm dev                 # frontend :4000 and backend :8000
pnpm dev:frontend
pnpm dev:backend
pnpm lint                # ESLint + Ruff
pnpm format              # Prettier + Ruff formatter
pnpm typecheck           # frontend TypeScript only
pnpm build               # frontend production build only
```

Backend setup requires a local `backend/.env` copied from
`backend/.env.example`, plus a reachable PostgreSQL instance:

```bash
cd backend
uv sync
uv run uvicorn customer_analytics.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```

For schema changes:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe migration"
uv run alembic upgrade head
```

`backend/docker-compose.yml` defines only the backend service; it does not
provision PostgreSQL or Redis. Do not assume `docker compose up` supplies the
database.

## Code Conventions & Common Patterns

### Frontend

- TypeScript function components; components/types in PascalCase, hooks named
  `useThing`, and files generally kebab-case (`product-card.tsx`).
- Use the `@/` alias for `frontend/src` imports. Keep API calls in `api/` and
  server state in TanStack Query; use Zustand for auth/global client state and
  `nuqs` for URL-backed filters.
- Follow the existing Prettier contract: two-space indentation, LF, no
  semicolons, double quotes, ES5 trailing commas, 80-column width. Tailwind
  classes are sorted by the configured Prettier plugin.
- Prefer existing shadcn/Base UI primitives and semantic Tailwind theme
  classes. Preserve accessible labels and roles in interactive controls.

### Backend

- Use absolute imports from `customer_analytics.*`; do not use `from app`
  or relative imports. Keep `from __future__ import annotations` in modules.
- Keep route handlers thin: validate/translate HTTP schemas, call a use case,
  and map the result to a response schema. Do not query the database directly
  from routers or access ORM models from application use cases.
- Domain code must not import infrastructure. Define repository interfaces in
  `domain/repositories/` and implementations in
  `infrastructure/repositories/`.
- Use `AsyncSession` through the request dependency. Repositories do not
  commit; transaction ownership belongs to the use case/unit-of-work flow.
- Raise domain/application errors through `AppException` and `ErrorCode` in
  `app/shared/errors.py`; rely on centralized handlers for consistent error
  responses. Do not hard-code status codes or expose raw exception details.
- Load all settings and secrets through `app/config.py` and environment
  variables. Never log passwords, tokens, or other sensitive values.
- Ruff enforces E/F/I/UP/B with an 88-character line length; mypy is strict.

## Important Files

- `package.json`: root pnpm orchestration scripts.
- `pnpm-workspace.yaml`: frontend-only pnpm workspace declaration.
- `frontend/vite.config.ts`: port 4000, `/api` proxy to backend port 8000, and
  `@` alias.
- `frontend/src/router.tsx`: route graph, lazy loading, and guards.
- `frontend/src/api/client.ts`: API base URL, credentials, token injection, and
  refresh/retry behavior.
- `backend/pyproject.toml`: Python 3.13 requirement and Ruff, mypy, pytest,
  coverage, and package configuration.
- `backend/src/customer_analytics/app/main.py`: backend composition root.
- `backend/src/customer_analytics/app/config.py`: strict environment-backed
  settings and analytics score weights.
- `backend/src/customer_analytics/app/shared/exceptions.py`: error handlers.
- `backend/src/customer_analytics/core/database/session.py`: request-scoped
  async sessions and rollback behavior.
- `backend/migrations/env.py` and `backend/alembic.ini`: migration wiring.
- `backend/docs/API.md`: API base URLs, health, Swagger/ReDoc, auth, and RBAC
  examples.

## Runtime/Tooling Preferences

- Use Node.js 22+ and pnpm 10+ for JavaScript. `pnpm-lock.yaml` is the
  canonical JavaScript lockfile; use pnpm rather than npm, Yarn, or pip.
- Use Python 3.13 for the backend (`backend/.python-version` and
  `backend/pyproject.toml`) and uv for environments/dependencies. The root
  README's Python 3.12 statement is stale relative to backend configuration.
- Run backend commands from `backend/` so `.env` is loaded correctly.
- Keep secrets in ignored `.env` files. Placeholder values in
  `backend/.env.example` are not production credentials.
- `backend/Dockerfile` runs production dependencies and migrations before
  Uvicorn, but its entrypoint logs and continues after migration failure;
  verify migrations separately.

## Testing & QA

- Backend testing is pytest-based (`pytest`, `pytest-asyncio`, `httpx`);
  `backend/pyproject.toml` discovers `backend/tests` with automatic async mode.
  Active coverage is concentrated in unit tests and `/health`; integration and
  e2e directories currently contain only package markers.
- Use focused tests for behavior changes, then run `cd backend && uv run
  pytest` when the backend is affected. Cover successful responses, validation
  failures, and mapped `AppException` errors where applicable. Prefer
  observable behavior, async endpoint tests through `httpx.AsyncClient`, and
  lightweight fakes for isolated use-case tests.
- Frontend has no configured test runner, test script, or coverage threshold.
  Current quality gates are `pnpm typecheck`, `pnpm lint`, and `pnpm build`.
  If a frontend test framework is introduced, add focused `*.test.ts` or
  `*.test.tsx` tests that exercise accessible user behavior.
- `pytest-cov` is installed and coverage source is configured, but no minimum
  threshold or canonical coverage command is enforced.
- No CI workflow is configured in the repository; do not claim CI coverage or
  passing checks without running the relevant commands.
