import type { UserRole } from "@/types/user"

export const ADMIN_ROLES = ["ADMIN"] as const satisfies readonly UserRole[]
export const STAFF_ROLES = [
  "ADMIN",
  "ANALYST",
] as const satisfies readonly UserRole[]
export const CLIENT_ROLES = ["USER"] as const satisfies readonly UserRole[]

interface RedirectLocation {
  pathname: string
  search?: string
  hash?: string
}

function isPathWithin(pathname: string, root: string) {
  return pathname === root || pathname.startsWith(`${root}/`)
}

function isRedirectLocation(value: unknown): value is RedirectLocation {
  if (!value || typeof value !== "object") return false

  const pathname = Reflect.get(value, "pathname")
  return (
    typeof pathname === "string" &&
    pathname.startsWith("/") &&
    !pathname.startsWith("//")
  )
}

export function getHomePathForRole(role: UserRole) {
  switch (role) {
    case "ADMIN":
    case "ANALYST":
      return "/dashboard"
    case "USER":
      return "/"
    default:
      return "/login"
  }
}

export function canRoleAccessPath(role: UserRole, pathname: string) {
  if (isPathWithin(pathname, "/dashboard/users")) return role === "ADMIN"
  if (isPathWithin(pathname, "/dashboard")) {
    return role === "ADMIN" || role === "ANALYST"
  }
  if (pathname === "/" || isPathWithin(pathname, "/products")) {
    return role === "USER"
  }

  return false
}

export function getPostLoginPath(role: UserRole, locationState: unknown) {
  if (!locationState || typeof locationState !== "object") {
    return getHomePathForRole(role)
  }

  const from = Reflect.get(locationState, "from")
  if (!isRedirectLocation(from) || !canRoleAccessPath(role, from.pathname)) {
    return getHomePathForRole(role)
  }

  return `${from.pathname}${from.search ?? ""}${from.hash ?? ""}`
}
