import type { UserRole } from "@/types/user"

export const ADMIN_ROLES = ["ADMIN"] as const satisfies readonly UserRole[]
export const STAFF_ROLES = [
  "ADMIN",
  "ANALYST",
  "MANAGER",
  "SALES",
  "CSKH",
] as const satisfies readonly UserRole[]
export const CLIENT_ROLES = [
  "CLIENT",
  "USER",
] as const satisfies readonly UserRole[]

interface RedirectLocation {
  pathname: string
  search?: string
  hash?: string
}

const isPathWithin = (pathname: string, root: string): boolean =>
  pathname === root || pathname.startsWith(`${root}/`)

const isRedirectLocation = (value: unknown): value is RedirectLocation => {
  if (!value || typeof value !== "object") return false

  const pathname = Reflect.get(value, "pathname")
  return (
    typeof pathname === "string" &&
    pathname.startsWith("/") &&
    !pathname.startsWith("//")
  )
}

export const getHomePathForRole = (role: UserRole): string => {
  switch (role) {
    case "ADMIN":
    case "ANALYST":
    case "MANAGER":
    case "SALES":
    case "CSKH":
      return "/dashboard"
    case "USER":
    case "CLIENT":
      return "/"
    default:
      return "/login"
  }
}

export const canRoleAccessPath = (
  role: UserRole,
  pathname: string
): boolean => {
  if (isPathWithin(pathname, "/dashboard/users")) return role === "ADMIN"
  if (isPathWithin(pathname, "/dashboard")) {
    return STAFF_ROLES.some((allowedRole) => allowedRole === role)
  }
  if (pathname === "/" || isPathWithin(pathname, "/products")) {
    return CLIENT_ROLES.some((allowedRole) => allowedRole === role)
  }
  return false
}

export const getPostLoginPath = (
  role: UserRole,
  locationState: unknown
): string => {
  if (!locationState || typeof locationState !== "object") {
    return getHomePathForRole(role)
  }

  const from = Reflect.get(locationState, "from")
  if (!isRedirectLocation(from) || !canRoleAccessPath(role, from.pathname)) {
    return getHomePathForRole(role)
  }

  return `${from.pathname}${from.search ?? ""}${from.hash ?? ""}`
}
