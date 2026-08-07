import { useCallback, useState } from "react"
import { useNavigate } from "react-router"

import { useAuthStore } from "@/stores/use-auth-store"
import { toastError, toastSuccess } from "@/utils/toast"

export function useLogout() {
  const navigate = useNavigate()
  const logout = useAuthStore((state) => state.logout)
  const [isLoggingOut, setIsLoggingOut] = useState(false)

  const handleLogout = useCallback(async () => {
    if (isLoggingOut) return

    setIsLoggingOut(true)
    try {
      await logout()
      toastSuccess("Đã đăng xuất")
    } catch {
      toastError("Không thể kết nối máy chủ, phiên đăng nhập đã được xoá.")
    } finally {
      setIsLoggingOut(false)
      navigate("/login", { replace: true })
    }
  }, [isLoggingOut, logout, navigate])

  return { handleLogout, isLoggingOut }
}
