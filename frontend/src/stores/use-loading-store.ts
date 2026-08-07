import { create } from "zustand"

interface LoadingState {
  isLoading: boolean
  pendingCount: number
  setLoading: (loading: boolean) => void
  startLoading: () => void
  stopLoading: () => void
}

export const useLoadingStore = create<LoadingState>((set) => ({
  isLoading: false,
  pendingCount: 0,
  setLoading: (loading) =>
    set({ isLoading: loading, pendingCount: loading ? 1 : 0 }),
  startLoading: () =>
    set((state) => ({
      isLoading: true,
      pendingCount: state.pendingCount + 1,
    })),
  stopLoading: () =>
    set((state) => {
      const pendingCount = Math.max(0, state.pendingCount - 1)
      return { isLoading: pendingCount > 0, pendingCount }
    }),
}))
