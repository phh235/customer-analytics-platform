# React + TypeScript + Vite + shadcn/ui

This is a template for a new Vite project with React, TypeScript, and shadcn/ui.

## Local API and login sessions

In development, the browser calls `/api/v1` on the frontend origin so the
HttpOnly SameSite refresh cookie remains available. Vite proxies those requests
to the origin configured by `VITE_API_URL` in `.env.development`. The Network
panel therefore shows `localhost:4000/api/...`, while the actual upstream is
the configured backend tunnel. Restart the development server after changing
the target URL.

Supported account roles match the backend: `ADMIN`, `MANAGER`, `ANALYST`,
`SALES`, `CSKH`, and `USER`. `USER` opens the customer area; staff roles open
the dashboard. Legacy `CLIENT` sessions are still accepted as customer users.

## Adding components

To add components to your app, run the following command:

```bash
npx shadcn@latest add button
```

This will place the ui components in the `src/components` directory.

## Using components

To use the components in your app, import them as follows:

```tsx
import { Button } from "@/components/ui/button"
```
