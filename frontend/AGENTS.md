# Repository Guidelines

## Project Structure & Module Organization

This is a React 19 + TypeScript application built with Vite. Application code lives in `src/`:

- `pages/` contains route-level screens for auth, client, and admin flows; `layouts/` provides their shells.
- `components/` contains shared components, with reusable primitives in `components/ui/` and feature components grouped by area.
- `api/` wraps backend requests, `lib/` holds domain helpers, `hooks/` contains reusable React hooks, and `stores/` contains Zustand state.
- `router.tsx`, `config/`, and `integrations.tsx` define routing and app wiring. Put static files in `public/` and imported assets in `src/assets/`.

Use the `@/` alias for imports from `src` (for example, `@/components/ui/button`).

## Build, Test, and Development Commands

Run these from `frontend/`:

- `pnpm install` — install dependencies.
- `pnpm run dev` — start Vite on port 4000 with the browser opened; `/api` requests proxy to `127.0.0.1:8000`.
- `pnpm run typecheck` — run TypeScript checks without emitting files.
- `pnpm run lint` — run ESLint across the project.
- `pnpm run format` / `pnpm run format:check` — format or validate TypeScript and TSX files.
- `pnpm run build` — type-check and create the production bundle in `dist/`.
- `pnpm run preview` — serve the built bundle locally.

## Coding Style & Naming Conventions

Use two spaces, LF line endings, no semicolons, double quotes, an 80-character print width, and ES5 trailing commas; run Prettier before committing. Keep React components and types in PascalCase, hooks named `useThing`, and files generally kebab-case (`product-card.tsx`). Tailwind classes are sorted by the configured Prettier plugin.

## Testing Guidelines

No test runner, test script, or coverage threshold is currently configured. For new behavior, add focused `*.test.ts` or `*.test.tsx` tests when a framework is introduced, and always run `pnpm run typecheck`, `pnpm run lint`, and `pnpm run build` before opening a PR.

## Commit & Pull Request Guidelines

Use concise Conventional Commit-style subjects with an optional scope, such as `feat(client): add product filters`, `feat(Auth): init auth flow`, or `chore: update dependencies`. Keep commits focused. Pull requests should explain the change and motivation, link relevant issues when available, include screenshots or recordings for UI changes, and list verification commands plus any backend/API dependency.
