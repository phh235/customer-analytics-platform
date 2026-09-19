import { Skeleton } from "@/components/ui/skeleton"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"

export function ProductCardSkeleton() {
  return (
    <SquircleCard aria-hidden="true" className="h-full">
      <SquircleCardBody className="h-48 flex-none py-0 sm:h-56 lg:h-64">
        <Skeleton className="size-full rounded-none" />
      </SquircleCardBody>
      <div className="flex flex-1 flex-col gap-2 px-3 py-3">
        <Skeleton className="h-4 w-2/5" />
        <Skeleton className="h-5 w-4/5" />
        <Skeleton className="h-5 w-1/2" />
      </div>
    </SquircleCard>
  )
}
