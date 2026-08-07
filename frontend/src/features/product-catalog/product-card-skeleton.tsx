import { Skeleton } from "@/components/ui/skeleton"

export function ProductCardSkeleton() {
  return (
    <div
      aria-hidden="true"
      className="flex h-full flex-col border-r border-b border-border max-md:nth-[2n]:border-r-0 max-md:nth-last-[-n+2]:border-b-0 md:max-lg:nth-[3n]:border-r-0 md:max-lg:nth-last-[-n+3]:border-b-0 lg:nth-[4n]:border-r-0 lg:nth-last-[-n+4]:border-b-0"
    >
      <Skeleton className="h-48 w-full shrink-0 rounded-none sm:h-56 lg:h-64" />
      <div className="flex flex-1 flex-col gap-2 p-3">
        <Skeleton className="h-5 w-4/5" />
        <Skeleton className="h-5 w-2/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  )
}
