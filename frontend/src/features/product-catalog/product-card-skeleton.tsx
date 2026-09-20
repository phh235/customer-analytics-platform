import { Skeleton } from "@/components/ui/skeleton"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"

export function ProductCardSkeleton() {
  return (
    <SquircleCard aria-hidden="true" className="h-full not-dark:bg-muted/50">
      <SquircleCardBody className="relative h-48 flex-none border-0! py-0 sm:h-56 lg:h-64">
        <Skeleton className="size-full rounded-none" />
        <div className="pointer-events-none absolute inset-0 rounded-[inherit] inset-ring-1 inset-ring-black/10 dark:inset-ring-white/10" />
      </SquircleCardBody>
      <div className="flex flex-1 flex-col gap-0.5 px-3 py-2.5">
        <Skeleton className="h-4 w-2/5" />
        <Skeleton className="h-5 w-4/5" />
        <Skeleton className="mt-0.5 h-5 w-1/2" />
      </div>
    </SquircleCard>
  )
}
