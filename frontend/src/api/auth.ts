import { authClient } from "@/api/client"
import { isUserRole, type User } from "@/types/user"
import type {
  ForgotPasswordRequestResponse,
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  RegisterResponse,
  TokenResponse,
  VerifyForgotPasswordResponse,
} from "@/types/auth"

export async function login(credentials: LoginRequest) {
  const { data } = await authClient.post<TokenResponse>(
    "/auth/login",
    credentials
  )
  return data
}

export async function registerAccount(payload: RegisterRequest) {
  const { data } = await authClient.post<RegisterResponse>(
    "/auth/register",
    payload
  )
  return data
}

export async function requestForgotPassword(email: string) {
  const { data } = await authClient.post<ForgotPasswordRequestResponse>(
    "/auth/password/forgot/request",
    { email }
  )
  return data
}

export async function verifyForgotPassword(email: string, otp: string) {
  const { data } = await authClient.post<VerifyForgotPasswordResponse>(
    "/auth/password/forgot/verify",
    { email, otp }
  )
  return data
}

export async function resetForgottenPassword(
  resetToken: string,
  newPassword: string
) {
  const { data } = await authClient.post<MessageResponse>(
    "/auth/password/reset",
    { reset_token: resetToken, new_password: newPassword }
  )
  return data
}

export async function refreshAccessToken() {
  const { data } = await authClient.post<TokenResponse>("/auth/refresh")
  return data
}

export async function getCurrentUser() {
  const { data } = await authClient.get<User>("/auth/me")
  if (!isUserRole(data?.role_code)) {
    throw new Error(
      "Vai trò của tài khoản chưa được hỗ trợ. Vui lòng liên hệ quản trị viên."
    )
  }
  return data
}

export async function logout() {
  const { data } = await authClient.post<MessageResponse>("/auth/logout")
  return data
}
