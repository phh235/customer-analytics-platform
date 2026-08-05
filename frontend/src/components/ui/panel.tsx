import * as React from "react"

import { cn } from "@/lib/utils"

const Panel = ({ className, ...props }: React.ComponentProps<"section">) => {
  return (
    <section
      data-slot="panel"
      className={cn(
        "screen-border-top screen-border-bottom border-x border-border",
        className
      )}
      {...props}
    />
  )
}

const PanelContent = ({ className, ...props }: React.ComponentProps<"div">) => {
  return (
    <div data-slot="panel-body" className={cn("p-4", className)} {...props} />
  )
}

const Separator = ({ className }: { className?: string }) => {
  return (
    <div
      className={cn(
        "stripe-divider h-(--separator-height) w-full border-x border-border",
        className
      )}
    />
  )
}

export { Panel, PanelContent, Separator }
