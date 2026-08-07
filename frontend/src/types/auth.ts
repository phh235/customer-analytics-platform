import type { UserRole } from "@/types/user"

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  role_code: UserRole
}

export interface MessageResponse {
  message: string
}
