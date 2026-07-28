import { Navigate, Outlet } from "react-router"

export function PrivateRoute() {
  const token = localStorage.getItem("access_token")

  if (!token) return <Navigate to="/login" replace />

  return <Outlet />
}
