import { cn } from "@/lib/utils"
import * as React from "react"

/**
 * Apple-style squircle silhouette. The shape comes from a CSS `shape()` clip-path
 * (with `corner-shape: squircle` where supported) - continuous-curvature corners
 * instead of circular arcs.
 */
const cardClipPath =
  "shape(from var(--card-clip-radius) 0px, line to calc(100% - var(--card-clip-radius)) 0px, curve to 100% var(--card-clip-radius) with calc(100% - var(--card-clip-handle)) 0px / 100% var(--card-clip-handle), line to 100% calc(100% - var(--card-clip-radius)), curve to calc(100% - var(--card-clip-radius)) 100% with 100% calc(100% - var(--card-clip-handle)) / calc(100% - var(--card-clip-handle)) 100%, line to var(--card-clip-radius) 100%, curve to 0px calc(100% - var(--card-clip-radius)) with var(--card-clip-handle) 100% / 0px calc(100% - var(--card-clip-handle)), line to 0px var(--card-clip-radius), curve to var(--card-clip-radius) 0px with 0px var(--card-clip-handle) / var(--card-clip-handle) 0px, close)"

type CardStyle = React.CSSProperties & {
  "--card-clip-handle"?: string
  "--card-clip-path"?: string
  "--card-clip-radius"?: string
}

/** Bare squircle-clipped box - the primitive both card layers are built on. */
export const SquircleSurface = ({
  className,
  style,
  children,
  ...props
}: React.ComponentProps<"div">) => {
  return (
    <div
      className={cn(
        "relative flex min-w-0 flex-col rounded-[26px] bg-card text-card-foreground [--card-clip-handle:2.25px] [--card-clip-radius:14px] [clip-path:var(--card-clip-path)] [corner-shape:squircle] not-dark:bg-clip-padding before:pointer-events-none before:absolute before:inset-0 before:[clip-path:var(--card-clip-path)] sm:rounded-[50px] sm:[--card-clip-handle:3px] sm:[--card-clip-radius:20px]",
        className
      )}
      style={
        {
          "--card-clip-path": cardClipPath,
          ...style,
        } as CardStyle
      }
      data-slot="squircle-surface"
      {...props}
    >
      {children}
    </div>
  )
}

export function SquircleCard({
  className,
  size = "default",
  ...props
}: React.ComponentProps<"div"> & { size?: "default" | "sm" }) {
  return (
    <SquircleSurface
      data-slot="card"
      data-size={size}
      className={cn(
        "group/card min-w-0 gap-0 overflow-hidden rounded-[22px] border border-border/80 bg-[#f6f6f6] p-1 text-sm text-card-foreground shadow-sm [--card-clip-handle:2.25px] [--card-clip-radius:14px] [--card-spacing:--spacing(4)] data-[size=sm]:[--card-spacing:--spacing(3)] dark:border-border/60 dark:bg-[#191919] [&>[data-slot=card-header]]:py-2.5",
        className
      )}
      {...props}
    />
  )
}

export function SquircleCardBody({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <SquircleSurface
      data-slot="squircle-card-body"
      className={cn(
        "min-h-0 flex-1 gap-(--card-spacing) overflow-hidden rounded-[18px] border border-border/60 bg-white py-(--card-spacing) shadow-xs [--card-clip-handle:2.25px] [--card-clip-radius:11px] dark:bg-[#212121]",
        className
      )}
      {...props}
    />
  )
}
