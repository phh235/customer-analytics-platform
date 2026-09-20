import { useState } from "react"
import { Link } from "react-router"

import { type ProductRecord } from "@/api/products"
import { ProductImagePlaceholder } from "@/components/common/product-image-placeholder"
import { Skeleton } from "@/components/ui/skeleton"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { formatCurrency } from "@/lib/format"
import { cn } from "@/lib/utils"

type ProductCardProps = {
  product: ProductRecord
}

export function ProductCard({ product }: ProductCardProps) {
  const [loadedImageUrl, setLoadedImageUrl] = useState<string | null>(null)
  const [failedImageUrl, setFailedImageUrl] = useState<string | null>(null)
  const imageLoaded = loadedImageUrl === product.image_url
  const imageFailed = failedImageUrl === product.image_url

  return (
    <Link
      aria-label={`Xem chi tiết ${product.name}`}
      className="h-full cursor-pointer rounded-[22px] outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background sm:rounded-[28px]"
      to={`/products/${product.id}`}
    >
      <SquircleCard className="h-full not-dark:bg-muted/50">
        <SquircleCardBody className="relative h-48 flex-none border-0! bg-muted py-0 sm:h-56 lg:h-64">
          {product.image_url && !imageFailed ? (
            <>
              {!imageLoaded ? (
                <Skeleton className="absolute inset-0 size-full rounded-none" />
              ) : null}
              <img
                alt={product.name}
                className={cn(
                  "absolute inset-0 size-full object-cover transition-opacity duration-200",
                  imageLoaded ? "opacity-100" : "opacity-0"
                )}
                draggable={false}
                loading="lazy"
                onError={() => setFailedImageUrl(product.image_url)}
                onLoad={() => setLoadedImageUrl(product.image_url)}
                src={product.image_url}
              />
            </>
          ) : (
            <ProductImagePlaceholder
              productName={product.name}
              className="absolute inset-0"
              iconClassName="size-10 text-muted-foreground/60"
            />
          )}
          <div className="pointer-events-none absolute inset-0 rounded-[inherit] inset-ring-1 inset-ring-black/10 dark:inset-ring-white/10" />
        </SquircleCardBody>
        <div className="flex flex-1 flex-col gap-0.5 px-3 py-2.5">
          <p className="text-xs leading-4 text-muted-foreground">
            {product.category}
          </p>
          <h3 className="line-clamp-1 text-sm leading-5 font-medium text-foreground md:text-base">
            {product.name}
          </h3>
          <span className="mt-0.5 text-sm leading-5 font-semibold text-primary md:text-base">
            {formatCurrency(Number(product.price))}
          </span>
        </div>
      </SquircleCard>
    </Link>
  )
}
