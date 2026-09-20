import { cn } from "@/lib/utils"

export function PotentialScoreValue({
  value,
  highThreshold = 80,
  decimals = 1,
  className,
}: {
  value: number
  highThreshold?: number
  decimals?: number
  className?: string
}) {
  return (
    <span
      className={cn(
        "font-medium tabular-nums",
        value >= highThreshold
          ? "text-emerald-600 dark:text-emerald-400"
          : value >= 50
            ? "text-amber-600 dark:text-amber-400"
            : "text-destructive",
        className
      )}
    >
      {value.toLocaleString("vi-VN", {
        minimumFractionDigits: 0,
        maximumFractionDigits: decimals,
      })}
      <span className="font-normal text-muted-foreground"> / 100</span>
    </span>
  )
}
