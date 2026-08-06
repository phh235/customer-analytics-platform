import * as React from "react"

type EventListenerOptions = Pick<
  AddEventListenerOptions,
  "capture" | "once" | "passive"
>

export function useEventListener<K extends keyof WindowEventMap>(
  type: K,
  listener: (event: WindowEventMap[K]) => void,
  options: EventListenerOptions = {}
) {
  const listenerRef = React.useRef(listener)

  React.useEffect(() => {
    listenerRef.current = listener
  }, [listener])

  const { capture, once, passive } = options

  React.useEffect(() => {
    const handleEvent = (event: WindowEventMap[K]) => {
      listenerRef.current(event)
    }

    window.addEventListener(type, handleEvent, { capture, once, passive })

    return () => window.removeEventListener(type, handleEvent, { capture })
  }, [capture, once, passive, type])
}
