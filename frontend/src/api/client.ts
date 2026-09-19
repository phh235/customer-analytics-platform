import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios"

import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/api/access-token"

const DATA_API_URL = import.meta.env.VITE_API_URL ?? "/api/v1"
const AUTH_API_URL = import.meta.env.VITE_API_URL ?? "/api/v1"

const apiClient = axios.create({
  baseURL: DATA_API_URL,
  timeout: 30000,
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
})

// Auth calls the configured backend directly and includes the refresh cookie.
export const authClient = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
})

const refreshClient = axios.create({
  baseURL: AUTH_API_URL,
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

function attachAuthInterceptors(client: AxiosInstance) {
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = getAccessToken()
      if (token) config.headers.Authorization = `Bearer ${token}`
      return config
    },
    (error) => Promise.reject(error)
  )

  client.interceptors.response.use(
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
      return client(originalRequest)
    }
  )
}

attachAuthInterceptors(apiClient)
attachAuthInterceptors(authClient)

export default apiClient
