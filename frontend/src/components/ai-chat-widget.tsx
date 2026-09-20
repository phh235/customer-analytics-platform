import { useEffect, useRef, useState } from "react"

import AiChatPanel from "@/components/ai-chat-panel"
import { Button } from "@/components/ui/button"
import { MainLogo } from "@/lib/svg"

export function AiChatWidget() {
  const [open, setOpen] = useState(false)
  const [closing, setClosing] = useState(false)
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(
    () => () => {
      if (closeTimer.current) clearTimeout(closeTimer.current)
    },
    []
  )

  const closeChat = () => {
    if (closing) return
    setClosing(true)
    closeTimer.current = setTimeout(() => {
      setOpen(false)
      setClosing(false)
      closeTimer.current = null
    }, 200)
  }

  const openChat = () => {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current)
      closeTimer.current = null
    }
    setClosing(false)
    setOpen(true)
  }

  return (
    <>
      {!open || closing ? (
        <Button
          type="button"
          variant="outline"
          aria-label="Mở trợ lý AI"
          aria-expanded={open && !closing}
          className="fixed right-[calc(1rem+var(--safe-area-right))] bottom-[calc(1rem+var(--safe-area-bottom))] z-50 h-12 w-fit animate-in rounded-full bg-card! px-2 shadow-xs duration-200 zoom-in-75 fade-in hover:bg-muted!"
          onClick={openChat}
        >
          <MainLogo aria-hidden="true" className="size-9" />
          <span className="font-semibold">3CS AI</span>
        </Button>
      ) : null}
      {open ? <AiChatPanel closing={closing} onClose={closeChat} /> : null}
    </>
  )
}
