import { Badge } from "@/components/ui/badge"
import { SCORE_LEVEL_LABELS, SEGMENT_LABELS } from "@/lib/admin-management"
import { formatEnumLabel } from "@/lib/format"

const SEGMENT_STYLES: Record<string, string> = {
  HIGH_VALUE:
    "border-transparent bg-emerald-100 text-emerald-700 dark:bg-emerald-400/20 dark:text-emerald-300",
  LOYAL:
    "border-transparent bg-lime-100 text-lime-800 dark:bg-lime-400/20 dark:text-lime-300",
  AT_RISK:
    "border-transparent bg-red-100 text-red-700 dark:bg-red-400/20 dark:text-red-300",
  POTENTIAL:
    "border-transparent bg-blue-100 text-blue-700 dark:bg-blue-400/20 dark:text-blue-300",
  NEW_CUSTOMER:
    "border-transparent bg-indigo-100 text-indigo-700 dark:bg-indigo-400/20 dark:text-indigo-300",
  NORMAL:
    "border-transparent bg-zinc-100 text-zinc-700 dark:bg-zinc-400/20 dark:text-zinc-300",
  INSUFFICIENT_DATA: "border-border bg-transparent text-muted-foreground",
}

const POTENTIAL_VARIANTS = {
  HIGH: "success",
  POTENTIAL: "warning",
  NORMAL: "info",
  INSUFFICIENT_DATA: "outline",
} as const

export function SegmentBadge({
  segment,
  label,
}: {
  segment: string
  label?: string
}) {
  const normalizedSegment = segment.trim().toUpperCase()

  return (
    <Badge variant="outline" className={SEGMENT_STYLES[normalizedSegment]}>
      {label ?? formatEnumLabel(normalizedSegment, SEGMENT_LABELS)}
    </Badge>
  )
}

export function PotentialLevelBadge({
  level,
  className,
}: {
  level: string
  className?: string
}) {
  const normalizedLevel = level.trim().toUpperCase()

  return (
    <Badge
      className={className}
      variant={
        POTENTIAL_VARIANTS[
          normalizedLevel as keyof typeof POTENTIAL_VARIANTS
        ] ?? "outline"
      }
    >
      {formatEnumLabel(normalizedLevel, SCORE_LEVEL_LABELS)}
    </Badge>
  )
}
