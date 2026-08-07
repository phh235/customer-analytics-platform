import apiClient from "@/api/client"
import type { User } from "@/types/user"
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
  return data
}

export async function logout() {
  const { data } = await apiClient.post<MessageResponse>("/auth/logout")
  return data
}
