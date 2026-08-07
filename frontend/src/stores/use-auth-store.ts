import { create } from "zustand"

import {
  getCurrentUser,
  login as loginApi,
  logout as logoutApi,
  refreshAccessToken,
} from "@/api/auth"
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "@/api/access-token"
import { queryClient } from "@/app/query-client"
import { useLoadingStore } from "@/stores/use-loading-store"
import type { LoginRequest } from "@/types/auth"
import type { User } from "@/types/user"

type AuthStatus = "unknown" | "loading" | "authenticated" | "unauthenticated"

interface AuthState {
  accessToken: string | null
  user: User | null
  status: AuthStatus
  login: (credentials: LoginRequest) => Promise<User>
  initializeSession: () => Promise<boolean>
  logout: () => Promise<void>
}

let initializePromise: Promise<boolean> | null = null

function clearAuthState(set: (state: Partial<AuthState>) => void) {
  clearAccessToken()
  queryClient.clear()
  set({ accessToken: null, user: null, status: "unauthenticated" })
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  user: null,
  status: "unknown",

  login: async (credentials) => {
    const { startLoading, stopLoading } = useLoadingStore.getState()
    startLoading()
    set({ status: "loading" })

    try {
      const tokenResponse = await loginApi(credentials)
      setAccessToken(tokenResponse.access_token)

      const user = await getCurrentUser()
      set({
        accessToken: tokenResponse.access_token,
        user,
        status: "authenticated",
      })
      return user
    } catch (error) {
      try {
        if (getAccessToken()) await logoutApi()
      } catch {
        // Clear the local session even when the server cannot be reached.
      }
      clearAuthState(set)
      throw error
    } finally {
      stopLoading()
    }
  },

  initializeSession: () => {
    if (get().status === "authenticated") return Promise.resolve(true)
    if (initializePromise) return initializePromise

    initializePromise = (async () => {
      const { startLoading, stopLoading } = useLoadingStore.getState()
      startLoading()
      set({ status: "loading" })

      try {
        let token = getAccessToken()
        if (!token) {
          const tokenResponse = await refreshAccessToken()
          token = tokenResponse.access_token
          setAccessToken(token)
        }

        const user = await getCurrentUser()
        set({ accessToken: token, user, status: "authenticated" })
        return true
      } catch {
        clearAuthState(set)
        return false
      } finally {
        stopLoading()
        initializePromise = null
      }
    })()

    return initializePromise
  },

  logout: async () => {
    const { startLoading, stopLoading } = useLoadingStore.getState()
    startLoading()

    try {
      if (getAccessToken()) await logoutApi()
    } finally {
      clearAuthState(set)
      stopLoading()
    }
  },
}))
