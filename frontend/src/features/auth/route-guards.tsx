import { useEffect, useRef } from "react"
import { Navigate, Outlet, useLocation, useNavigate } from "react-router"

import { DashboardSessionSkeleton } from "@/components/common/dashboard-session-skeleton"
import { Spinner } from "@/components/ui/spinner"
import { getHomePathForRole, getPostLoginPath } from "@/lib/auth-routing"
import { useAuthStore } from "@/stores/use-auth-store"
import type { UserRole } from "@/types/user"

function SessionPending() {
  return (
    <main
      aria-busy="true"
      aria-label="Đang xác thực phiên đăng nhập"
      className="flex min-h-screen items-center justify-center"
      role="status"
    >
      <Spinner />
    </main>
  )
}

function GuestRedirectPending({ to }: { to: string }) {
  const navigate = useNavigate()

  useEffect(() => {
    navigate(to, { replace: true })
  }, [navigate, to])

  return (
    <div
      aria-label="Đang chuyển trang"
      className="flex min-h-40 items-center justify-center"
      role="status"
    >
      <Spinner />
    </div>
  )
}

interface AuthenticatedRouteProps {
  dashboardFallback?: boolean
}

function useSessionInitialization() {
  const status = useAuthStore((state) => state.status)
  const initializeSession = useAuthStore((state) => state.initializeSession)

  useEffect(() => {
    if (status === "unknown") void initializeSession()
  }, [initializeSession, status])

  return status
}

export function AuthenticatedRoute({
  dashboardFallback = false,
}: AuthenticatedRouteProps) {
  const status = useSessionInitialization()
  const user = useAuthStore((state) => state.user)
  const accessToken = useAuthStore((state) => state.accessToken)
  const location = useLocation()

  if (status === "unknown" || status === "loading") {
    return dashboardFallback ? <DashboardSessionSkeleton /> : <SessionPending />
  }

  if (status !== "authenticated" || !accessToken || !user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />
}

export function DefaultRoute() {
  const status = useSessionInitialization()
  const user = useAuthStore((state) => state.user)
  const accessToken = useAuthStore((state) => state.accessToken)
  const location = useLocation()

  if (status === "unknown" || status === "loading") {
    return <SessionPending />
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
  const location = useLocation()
  const status = useSessionInitialization()
  const user = useAuthStore((state) => state.user)

  if (status === "unknown" || status === "loading") {
    return <Outlet />
  }

  if (status === "authenticated" && user) {
    return (
      <GuestRedirectPending
        to={getPostLoginPath(user.role_code, location.state)}
      />
    )
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
    return <SessionPending />
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
