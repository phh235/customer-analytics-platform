import * as React from "react"
import { useState } from "react"
import { ArrowUpIcon } from "lucide-react"
import { useMotionValueEvent, useScroll } from "motion/react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export function ScrollToTop({
  className,
  ...props
}: React.ComponentProps<"button">) {
  const { scrollY } = useScroll()

  const [visible, setVisible] = useState(false)

  useMotionValueEvent(scrollY, "change", (latestValue) => {
    setVisible(latestValue >= 400)
  })

  return (
    <Button
      data-visible={visible}
      className={cn(
        "[--bottom:0.5rem] sm:[--bottom:1rem] lg:[--bottom:2rem]",
        "fixed right-4 bottom-[calc(var(--bottom,0.5rem)+env(safe-area-inset-bottom,0))] z-50 lg:right-8",
        "transition-[background-color,opacity] duration-300 data-[visible=false]:pointer-events-none data-[visible=false]:opacity-0",
        className
      )}
      variant="outline"
      size="icon-sm"
      aria-label="Scroll to top"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      {...props}
    >
      <ArrowUpIcon />
    </Button>
  )
}
