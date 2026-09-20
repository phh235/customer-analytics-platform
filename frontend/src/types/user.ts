export const USER_ROLES = [
  "ADMIN",
  "MANAGER",
  "ANALYST",
  "SALES",
  "CSKH",
  "USER",
] as const
export const MANAGEABLE_USER_ROLES = USER_ROLES.filter(
  (role): role is Exclude<(typeof USER_ROLES)[number], "ADMIN"> =>
    role !== "ADMIN"
)
// Older API versions used CLIENT for customer-facing accounts.
export type UserRole = (typeof USER_ROLES)[number] | "CLIENT"

export const isUserRole = (value: unknown): value is UserRole =>
  value === "CLIENT" || USER_ROLES.some((role) => role === value)

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Quản trị viên hệ thống",
  MANAGER: "Quản lý",
  ANALYST: "Phân tích viên",
  SALES: "Nhân viên kinh doanh",
  CSKH: "Chăm sóc khách hàng",
  USER: "Người dùng",
  CLIENT: "Khách hàng",
}

export const USER_STATUSES = ["ACTIVE", "DISABLED", "LOCKED"] as const
export type UserStatus = (typeof USER_STATUSES)[number]

export interface User {
  id: string
  email: string
  full_name: string
  status: UserStatus
  role_code: UserRole
  permissions: string[]
  created_at: string
  last_login_at: string | null
}
