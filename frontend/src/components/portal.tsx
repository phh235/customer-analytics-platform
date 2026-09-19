import * as React from "react"
import { createPortal } from "react-dom"

import { cn } from "@/lib/utils"

function Portal({ className, ...props }: React.ComponentProps<"div">) {
  React.useEffect(() => {
    const originalOverflow = window.getComputedStyle(document.body).overflow
    const originalPaddingRight = document.body.style.paddingRight
    const scrollbarWidth =
      window.innerWidth - document.documentElement.clientWidth

    document.body.style.overflow = "hidden"

    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`
    }

    return () => {
      document.body.style.overflow = originalOverflow
      document.body.style.paddingRight = originalPaddingRight
    }
  }, [])

  if (typeof document === "undefined") {
    return null
  }

  return createPortal(
    <div
      className={cn("fixed inset-0 isolate z-40 flex flex-col", className)}
      {...props}
    />,
    document.body
  )
}

function PortalBackdrop({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "fixed inset-0 -z-1 bg-background/95 backdrop-blur-sm supports-backdrop-filter:bg-background/60",
        className
      )}
      {...props}
    />
  )
}

export { Portal, PortalBackdrop }
