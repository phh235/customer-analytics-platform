import type { User } from "@/types/user"

export function hasPermission(user: User | null, permission: string) {
  return (
    user?.role_code === "ADMIN" ||
    user?.permissions.includes(permission) === true
  )
}

export function isAdmin(user: User | null) {
  return user?.role_code === "ADMIN"
}
