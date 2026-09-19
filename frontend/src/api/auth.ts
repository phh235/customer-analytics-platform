import apiClient from "@/api/client"
import { isUserRole, type User } from "@/types/user"
import type { LoginRequest, MessageResponse, TokenResponse } from "@/types/auth"

export async function login(credentials: LoginRequest) {
  const { data } = await apiClient.post<TokenResponse>(
    "/auth/login",
    credentials
  )
  return data
}

export async function refreshAccessToken() {
  const { data } = await apiClient.post<TokenResponse>("/auth/refresh")
  return data
}

export async function getCurrentUser() {
  const { data } = await apiClient.get<User>("/auth/me")
  if (!isUserRole(data?.role_code)) {
    throw new Error(
      "Vai trò của tài khoản chưa được hỗ trợ. Vui lòng liên hệ quản trị viên."
    )
  }
  return data
}

export async function logout() {
  const { data } = await apiClient.post<MessageResponse>("/auth/logout")
  return data
}
