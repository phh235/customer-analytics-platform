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

Every page has a visible title and a short Vietnamese description. Admin pages
use the same 12px top/left/right content inset on desktop and mobile, including
the overview dashboard. Do not add breakpoint-dependent outer page padding
such as `p-4 lg:p-6`. Keep card-internal padding separate from page insets.
Page titles are text-only, without decorative icons before the heading. Admin list pages
use a `header` with `px-3 pt-3`, an `h1` with `text-2xl font-semibold`, and a
description with `mt-1 text-sm text-muted-foreground` above the filters/table.
Use one `gap-4` (16px) between the header, filter toolbar, and table. Toolbar
wrappers use horizontal padding only (`px-3`); do not add vertical padding on
top of the section gap. Keep the title-to-description gap at `mt-1` (4px).
Keep filter wrappers overflow-visible so the focus ring is not clipped. Rounded
table clipping belongs inside `CommonTable`, not around the page or toolbar.

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

Server-backed screens keep endpoint calls in `api/` and expose them through
TanStack Query hooks in `hooks/`. Share query keys with mutations so successful
writes invalidate the related cache. Use Zustand only for global client state,
such as the authenticated session, and keep URL filters in `nuqs`.

Forms use React Hook Form with Zod validation and display errors through
`FieldError`. Reuse a field component when its validation and presentation are
shared; image uploads use `ImageFileField`. Keep feature-specific field groups
inside their form instead of splitting every visual section into a component.
