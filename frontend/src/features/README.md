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

Tables use `CommonTable` from `components/common/common-table.tsx`: one rounded
border, a muted header, 48px data rows, and the shared summary/pagination below.
Keep tables outside additional Cards so every screen has the same spacing.
Supply `itemLabel` for the Vietnamese row count. For server pagination, pass
`total` and `totalPages`; for a complete local result set, omit `total` so the
table slices the rows. Use `TableActions` for row actions. It renders
`AppDropdown` internally with the shared horizontal three-dot trigger;
screens continue to pass the `actions` prop. Keep action labels short (for example,
"Chỉnh sửa" or "Xoá"); do not append the record name or model version to the
label or tooltip.

Selection controls use `AppSelect` from `components/common/app-select.tsx`.
Do not use native selects or import the Select/Table primitives in feature
screens. ESLint checks these boundaries. Form labels must point to each
control's `id`; reuse `Field`, `FieldGroup`, and `Input` for adjacent controls.
