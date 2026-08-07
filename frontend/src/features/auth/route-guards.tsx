import { useEffect, useRef } from "react"
import { Navigate, Outlet, useLocation, useNavigate } from "react-router"

import { DashboardSessionSkeleton } from "@/components/common/dashboard-session-skeleton"
import { Spinner } from "@/components/ui/spinner"
import { getHomePathForRole } from "@/lib/auth-routing"
import { useAuthStore } from "@/stores/use-auth-store"
import type { UserRole } from "@/types/user"

function ClientSessionPending() {
  return (
    <main
      aria-busy="true"
      aria-label="Đang xác thực phiên đăng nhập"
      className="flex min-h-[calc(100vh-3.5rem)] items-center justify-center"
      role="status"
    >
      <Spinner />
    </main>
  )
}

interface AuthenticatedRouteProps {
  dashboardFallback?: boolean
  renderPendingOutlet?: boolean
}

export function AuthenticatedRoute({
  dashboardFallback = false,
  renderPendingOutlet = false,
}: AuthenticatedRouteProps) {
  const status = useAuthStore((state) => state.status)
  const user = useAuthStore((state) => state.user)
  const accessToken = useAuthStore((state) => state.accessToken)
  const initializeSession = useAuthStore((state) => state.initializeSession)
  const location = useLocation()

  useEffect(() => {
    if (status === "unknown") void initializeSession()
  }, [initializeSession, status])

  if (status === "unknown" || status === "loading") {
    if (renderPendingOutlet) return <Outlet />

    return dashboardFallback ? (
      <DashboardSessionSkeleton />
    ) : (
      <ClientSessionPending />
    )
  }

  if (status !== "authenticated" || !accessToken || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

export function DefaultRoute() {
  const status = useAuthStore((state) => state.status)
  const user = useAuthStore((state) => state.user)
  const accessToken = useAuthStore((state) => state.accessToken)
  const initializeSession = useAuthStore((state) => state.initializeSession)
  const location = useLocation()

  useEffect(() => {
    if (status === "unknown") void initializeSession()
  }, [initializeSession, status])

  if (status === "unknown" || status === "loading") {
    return <Outlet />
  }

  if (status !== "authenticated" || !accessToken || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  const homePath = getHomePathForRole(user.role_code)

  if (homePath !== "/") {
    return <Navigate to={homePath} replace />
  }

  return <Outlet />
}

export function GuestRoute() {
  const status = useAuthStore((state) => state.status)
  const user = useAuthStore((state) => state.user)
  const initializeSession = useAuthStore((state) => state.initializeSession)

  useEffect(() => {
    if (status === "unknown") void initializeSession()
  }, [initializeSession, status])

  if (status === "unknown" || status === "loading") {
    return <Outlet />
  }

  if (status === "authenticated" && user) {
    return <Navigate to={getHomePathForRole(user.role_code)} replace />
  }

  return <Outlet />
}

interface RoleRouteProps {
  allowedRoles: readonly UserRole[]
  redirectToPrevious?: boolean
}

export function RoleRoute({
  allowedRoles,
  redirectToPrevious = false,
}: RoleRouteProps) {
  const status = useAuthStore((state) => state.status)
  const user = useAuthStore((state) => state.user)
  const location = useLocation()
  const navigate = useNavigate()
  const hasRedirected = useRef(false)
  const isAllowed = user ? allowedRoles.includes(user.role_code) : false

  useEffect(() => {
    if (!user || isAllowed || !redirectToPrevious || hasRedirected.current) {
      return
    }

    hasRedirected.current = true

    if (location.key !== "default") {
      navigate(-1)
    } else {
      navigate(getHomePathForRole(user.role_code), { replace: true })
    }
  }, [isAllowed, location.key, navigate, redirectToPrevious, user])

  if (status === "unknown" || status === "loading") {
    return <Outlet />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!isAllowed) {
    return redirectToPrevious ? (
      <DashboardSessionSkeleton />
    ) : (
      <Navigate to={getHomePathForRole(user.role_code)} replace />
    )
  }

  return <Outlet />
}
