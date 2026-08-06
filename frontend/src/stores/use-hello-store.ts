import { create } from "zustand"
import { getHello } from "@/api"
import { toastSuccess, toastError } from "@/utils"
import { useLoadingStore } from "./use-loading-store"

interface HelloState {
  message: string
  error: string | null
  fetchHello: (showToast?: boolean) => Promise<boolean>
}

export const useHelloStore = create<HelloState>((set) => ({
  message: "",
  error: null,
  fetchHello: async (showToast = false) => {
    const { setLoading } = useLoadingStore.getState()
    setLoading(true)
    set({ error: null })
    try {
      const data = await getHello()
      set({ message: data.message })
      if (showToast) {
        toastSuccess("Kết nối đến máy chủ thành công!")
      }
      return true
    } catch {
      set({ error: "Failed to connect to backend" })
      if (showToast) {
        toastError("Không thể kết nối đến máy chủ")
      }
      return false
    } finally {
      setLoading(false)
    }
  },
}))



