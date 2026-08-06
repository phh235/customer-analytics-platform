import * as React from "react"

export function useDebounce<T>(value: T, delay = 300) {
  const [debouncedValue, setDebouncedValue] = React.useState(value)

  React.useEffect(() => {
    const timeout = window.setTimeout(
      () => setDebouncedValue(value),
      Math.max(0, delay)
    )

    return () => window.clearTimeout(timeout)
  }, [delay, value])

  return debouncedValue
}
