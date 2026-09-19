import { createBrowserRouter } from "react-router"
import {
  AuthenticatedRoute,
  DefaultRoute,
  GuestRoute,
  RoleRoute,
} from "@/features/auth/route-guards"
import { ADMIN_ROLES, CLIENT_ROLES, STAFF_ROLES } from "@/lib/auth-routing"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <DefaultRoute />,
    children: [
      {
        lazy: async () => {
          const { default: Component } = await import("@/layouts/client-layout")

          return { Component }
        },
        children: [
          {
            index: true,
            lazy: () => import("@/pages/client/home"),
          },
        ],
      },
    ],
  },
  {
    lazy: async () => {
      const { default: Component } = await import("@/layouts/client-layout")

      return { Component }
    },
    children: [
      {
        element: <AuthenticatedRoute />,
        children: [
          {
            element: <RoleRoute allowedRoles={CLIENT_ROLES} />,
            children: [
              {
                path: "products",
                lazy: () => import("@/pages/client/products"),
              },
            ],
          },
        ],
      },
      {
        element: <AuthenticatedRoute />,
        children: [
          {
            element: <RoleRoute allowedRoles={CLIENT_ROLES} />,
            children: [
              {
                path: "products/:productId",
                lazy: () => import("@/pages/client/product-detail"),
              },
            ],
          },
        ],
      },
    ],
  },
  {
    lazy: async () => {
      const { default: Component } = await import("@/layouts/auth-layout")

      return { Component }
    },
    children: [
      {
        element: <GuestRoute />,
        children: [
          {
            path: "/login",
            lazy: () => import("@/pages/auth/login"),
          },
          {
            path: "/register",
            lazy: () => import("@/pages/auth/register"),
          },
          {
            path: "/forgot-password",
            lazy: () => import("@/pages/auth/forgot-password"),
          },
        ],
      },
    ],
  },
  {
    path: "/dashboard",
    element: <AuthenticatedRoute dashboardFallback />,
    children: [
      {
        element: <RoleRoute allowedRoles={STAFF_ROLES} />,
        children: [
          {
            lazy: async () => {
              const { default: Component } =
                await import("@/layouts/admin-layout")

              return { Component }
            },
            children: [
              {
                index: true,
                lazy: () => import("@/pages/admin/dashboard"),
              },
              {
                path: "products",
                lazy: () => import("@/pages/admin/products"),
              },
              {
                path: "categories",
                lazy: () => import("@/pages/admin/categories"),
              },
              {
                path: "customers",
                lazy: () => import("@/pages/admin/customers"),
              },
              {
                path: "transactions",
                lazy: () => import("@/pages/admin/transactions"),
              },
              {
                path: "analytics",
                children: [
                  {
                    index: true,
                    lazy: () => import("@/pages/admin/dashboard"),
                  },
                  {
                    path: "segments",
                    lazy: () => import("@/pages/admin/analytics-segments"),
                  },
                  {
                    path: "predictions",
                    lazy: () => import("@/pages/admin/analytics-predictions"),
                  },
                  {
                    path: "models",
                    lazy: () => import("@/pages/admin/analytics-models"),
                  },
                  {
                    path: "priority",
                    lazy: () => import("@/pages/admin/analytics-priority"),
                  },
                ],
              },
              {
                path: "system/import",
                lazy: () => import("@/pages/admin/import"),
              },
              {
                element: (
                  <RoleRoute allowedRoles={ADMIN_ROLES} redirectToPrevious />
                ),
                children: [
                  {
                    path: "users",
                    lazy: () => import("@/pages/admin/users"),
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
  {
    path: "*",
    lazy: () => import("@/pages/not-found"),
  },
])
