import { createBrowserRouter, Navigate } from "react-router"
import { PrivateRoute } from "@/components/common/private-route"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    lazy: async () => {
      const { default: Component } = await import("@/layouts/auth-layout")

      return { Component }
    },
    children: [
      {
        path: "/login",
        lazy: () => import("@/pages/auth/login"),
      },
    ],
  },
  {
    path: "/dashboard",
    element: <PrivateRoute />,
    children: [
      {
        lazy: async () => {
          const { default: Component } = await import("@/layouts/admin-layout")

          return { Component }
        },
        children: [
          {
            index: true,
            lazy: () => import("@/pages/admin/dashboard"),
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
