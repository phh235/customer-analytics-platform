import { cn } from "@/lib/utils"

export function ProbabilityValue({
  value,
  decimals = 1,
  className,
}: {
  value: number | null
  decimals?: number
  className?: string
}) {
  if (value === null) {
    return <span className="text-muted-foreground">Chưa đủ dữ liệu</span>
  }

  const percentage = value * 100

  return (
    <span
      className={cn(
        "font-medium tabular-nums",
        percentage >= 60 && "text-emerald-600 dark:text-emerald-400",
        percentage < 40 && "text-destructive",
        className
      )}
    >
      {percentage.toFixed(decimals)}%
    </span>
  )
}
