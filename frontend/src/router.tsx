import { createBrowserRouter } from "react-router"
import { PrivateRoute } from "@/components/common/private-route"

export const router = createBrowserRouter([
  {
    path: "/",
    lazy: async () => {
      const { default: Component } = await import("@/layouts/client-layout")

      return { Component }
    },
    children: [
      {
        index: true,
        lazy: () => import("@/pages/client/home"),
      },
      {
        path: "products",
        lazy: () => import("@/pages/client/products"),
      },
      {
        path: "products/:productId",
        lazy: () => import("@/pages/client/product-detail"),
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
        path: "/login",
        lazy: () => import("@/pages/auth/login"),
      },
      {
        path: "/register",
        lazy: () => import("@/pages/auth/register"),
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
