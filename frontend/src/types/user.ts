export const USER_ROLES = ["ADMIN", "ANALYST", "USER"] as const
export type UserRole = (typeof USER_ROLES)[number]

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  ADMIN: "Quản trị viên",
  ANALYST: "Phân tích viên",
  USER: "Người dùng",
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
