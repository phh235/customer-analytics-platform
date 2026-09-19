import type { UserRole } from "@/types/user"

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface RegisterResponse {
  message: string
  user: {
    id: string
    email: string
    full_name: string
    status: string
    role_code: "USER"
    created_at: string
  }
}

export interface ForgotPasswordRequestResponse {
  message: string
  expires_in: number
  retry_after: number
}

export interface VerifyForgotPasswordResponse {
  reset_token: string
  expires_in: number
}

export interface TokenResponse {
  access_token: string
  role_code: UserRole
}

export interface MessageResponse {
  message: string
}
