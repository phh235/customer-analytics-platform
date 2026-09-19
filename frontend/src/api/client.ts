import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios"

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/api/access-token"

// In development, keep auth requests same-origin so the browser can send the
// HttpOnly SameSite refresh cookie. Vite proxies /api to VITE_API_URL.
const API_URL = import.meta.env.DEV
  ? "/api/v1"
  : (import.meta.env.VITE_API_URL ?? "/api/v1")

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

// Refresh requests must not pass through the access-token retry interceptor.
const refreshClient = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

type RetriableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean
}

interface RefreshTokenResponse {
  access_token: string
}

let refreshPromise: Promise<string | null> | null = null

const isAuthEndpoint = (url?: string) =>
  ["/auth/login", "/auth/refresh", "/auth/logout"].some((path) =>
    url?.includes(path)
  )

async function refreshAccessTokenOnce() {
  if (!refreshPromise) {
    refreshPromise = refreshClient
      .post<RefreshTokenResponse>("/auth/refresh")
      .then(({ data }) => {
        setAccessToken(data.access_token)
        return data.access_token
      })
      .catch(() => {
        clearAccessToken()
        return null
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableRequestConfig | undefined

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      isAuthEndpoint(originalRequest.url)
    ) {
      return Promise.reject(error)
    }

    const token = await refreshAccessTokenOnce()
    if (!token) {
      clearAccessToken()
      if (window.location.pathname !== "/login") {
        window.location.assign("/login")
      }
      return Promise.reject(error)
    }

    originalRequest._retry = true
    originalRequest.headers.Authorization = `Bearer ${token}`
    return apiClient(originalRequest)
  }
)

export default apiClient
