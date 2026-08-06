# Repository Guidelines

## Project Structure & Module Organization

This monorepo contains a React 19/Vite frontend in `frontend/` and a FastAPI backend in `backend/`. Frontend application code lives in `frontend/src`: route screens belong in `pages/`, shared layouts in `layouts/`, reusable controls in `components/`, API clients in `api/`, shared state in `stores/`, and pure helpers in `lib/`. Backend endpoints are under `backend/app/api/v1/endpoints`, with schemas, services, and models separated into their corresponding `backend/app/` directories. Keep tests beside the affected package or in its established test directory; keep static frontend assets in the existing public/assets locations.

## Build, Test, and Development Commands

Use `pnpm` for JavaScript and `uv` for Python; do not create npm, Yarn, pip, or Poetry lockfiles.

- `pnpm setup`: install frontend and backend dependencies.
- `pnpm dev`: run both applications; use `pnpm dev:frontend` or `pnpm dev:backend` for one side.
- `pnpm typecheck`: validate frontend TypeScript.
- `pnpm lint`: run configured linters.
- `pnpm build`: produce a production build.
- `cd backend && uv run ruff check .`: lint Python.
- `cd backend && uv run ruff format --check .`: verify Python formatting.

## Coding Style & Naming Conventions

Use TypeScript function components, the `@/` import alias, semantic Tailwind theme classes, and existing shadcn/Base UI primitives. Component names use PascalCase; hooks start with `use` and use `use-kebab-case.ts` filenames. Keep user-facing text Vietnamese unless the feature establishes another language. Python uses modern 3.12 typing, absolute `app` imports, Ruff formatting, and an 88-character line limit. Keep business logic out of route components and endpoint handlers.

## Testing Guidelines

Add regression tests for behavior changes when the affected package has test infrastructure. Frontend tests should query accessible roles and labels and exercise user behavior. Backend tests should cover successful responses, validation failures, and mapped `AppException` errors. Run the narrowest relevant checks during development, then `pnpm typecheck`, applicable lint, and affected tests before handoff.

## Commit & Pull Request Guidelines

Use scoped Conventional Commits, for example `feat(auth): add password visibility toggle`. Keep commits focused and exclude secrets, generated output, and local environment files. Pull requests should explain the change, identify verification performed, link relevant issues, and include screenshots for visible UI changes. Call out migrations, configuration changes, and unrelated pre-existing check failures explicitly.

## Security & Configuration

Read backend settings through `backend/app/core/config.py`. Never commit tokens or expose raw backend exception details to users.
