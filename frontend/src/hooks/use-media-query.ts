import * as React from "react"

export function useMediaQuery(query: string, defaultValue = false) {
  const subscribe = React.useCallback(
    (onStoreChange: () => void) => {
      const mediaQuery = window.matchMedia(query)
      mediaQuery.addEventListener("change", onStoreChange)

      return () => mediaQuery.removeEventListener("change", onStoreChange)
    },
    [query]
  )

  const getSnapshot = React.useCallback(
    () => window.matchMedia(query).matches,
    [query]
  )

  const getServerSnapshot = React.useCallback(
    () => defaultValue,
    [defaultValue]
  )

  return React.useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}
