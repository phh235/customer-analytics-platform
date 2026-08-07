import apiClient from "@/api/client"
import type { User } from "@/types/user"
import type {
  CreateUserRequest,
  ListUsersParams,
  PaginatedUsersResponse,
  UpdateUserRequest,
} from "@/types/user-management"

export async function listUsers(params: ListUsersParams = {}) {
  const { data } = await apiClient.get<PaginatedUsersResponse>("/users", {
    params: {
      page: params.page,
      size: params.size,
      search: params.search?.trim() || undefined,
      role_code: params.role_code,
      status: params.status,
      sort_by: params.sort_by,
      sort_order: params.sort_order,
    },
  })
  return data
}

export async function createUser(payload: CreateUserRequest) {
  const { data } = await apiClient.post<User>("/users", payload)
  return data
}

export async function updateUser(userId: string, payload: UpdateUserRequest) {
  const { data } = await apiClient.patch<User>(`/users/${userId}`, payload)
  return data
}

export async function deleteUser(userId: string) {
  const { data } = await apiClient.delete<User>(`/users/${userId}`)
  return data
}
