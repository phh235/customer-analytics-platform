import { ImageOffIcon } from "lucide-react"

import { cn } from "@/lib/utils"

export function ProductImagePlaceholder({
  productName,
  className,
  iconClassName,
}: {
  productName: string
  className?: string
  iconClassName?: string
}) {
  return (
    <div
      role="img"
      aria-label={`Chưa có ảnh ${productName}`}
      className={cn(
        "flex items-center justify-center bg-muted text-muted-foreground",
        className
      )}
    >
      <ImageOffIcon
        className={cn("size-5", iconClassName)}
        aria-hidden="true"
      />
    </div>
  )
}
