# Frontend modules

Source code is organized by shared responsibilities and UI features:

- `api/` contains the API client and endpoint functions.
- `hooks/` contains business hooks and TanStack Query logic.
- `stores/` contains shared Zustand stores.
- `types/` contains domain models and API types.
- `features/` groups components and route guards by business feature.
- `pages/` only maps routes to feature-level components.

Import files directly and avoid barrel `index.ts` files. Features must not import
from pages or layouts, and shared API clients must not depend on components.
