import { create } from "zustand"
import { getHello } from "@/api"

interface HelloState {
  message: string
  isLoading: boolean
  error: string | null
  fetchHello: () => Promise<void>
}

export const useHelloStore = create<HelloState>((set) => ({
  message: "",
  isLoading: false,
  error: null,
  fetchHello: async () => {
    set({ isLoading: true, error: null })
    try {
      const data = await getHello()
      set({ message: data.message })
    } catch {
      set({ error: "Failed to connect to backend" })
    } finally {
      set({ isLoading: false })
    }
  },
}))
