# React + TypeScript + Vite + shadcn/ui

This is a template for a new Vite project with React, TypeScript, and shadcn/ui.

## Local API and login sessions

All browser requests, including authentication and refresh, call
`VITE_API_URL` directly. The backend must allow the current frontend origin,
enable credentialed CORS, and issue a cookie compatible with the frontend and
backend origins. Restart the development server after changing the API URL.

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
