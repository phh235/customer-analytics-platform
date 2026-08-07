import type { User, UserRole, UserStatus } from "@/types/user"

export type UserRoleFilter = UserRole | "ALL"
export type UserStatusFilter = UserStatus | "ALL"
export type UserSortField = "created_at" | "full_name" | "last_login_at"
export type SortOrder = "asc" | "desc"
export type UserSortOption =
  | "created_at_desc"
  | "created_at_asc"
  | "full_name_asc"
  | "full_name_desc"
  | "last_login_at_desc"
  | "last_login_at_asc"

export interface CreateUserRequest {
  email: string
  password: string
  full_name: string
  role_code: UserRole
}

export interface UpdateUserRequest {
  full_name?: string
  role_code?: UserRole
  status?: UserStatus
}

export interface ListUsersParams {
  page?: number
  size?: number
  search?: string
  role_code?: UserRole
  status?: UserStatus
  sort_by?: UserSortField
  sort_order?: SortOrder
}

export interface PaginatedUsersResponse {
  current: number
  size: number
  total: number
  pages: number
  records: User[]
}

export interface UserFormData {
  email: string
  full_name: string
  password?: string
  role_code: UserRole
  status: UserStatus
}
