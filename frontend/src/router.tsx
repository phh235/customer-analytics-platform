import { createBrowserRouter, Navigate } from "react-router"
import { PrivateRoute } from "@/components/common/private-route"
import AdminLayout from "@/layouts/admin-layout"
import AuthLayout from "@/layouts/auth-layout"

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    element: <AuthLayout />,
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
        element: <AdminLayout />,
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
