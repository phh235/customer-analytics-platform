import { Link } from "react-router"

import { type ProductRecord } from "@/api/products"
import { ProductImagePlaceholder } from "@/components/common/product-image-placeholder"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { formatCurrency } from "@/lib/format"

type ProductCardProps = {
  product: ProductRecord
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      aria-label={`Xem chi tiết ${product.name}`}
      className="h-full cursor-pointer rounded-[22px] outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      to={`/products/${product.id}`}
    >
      <SquircleCard className="h-full">
        <SquircleCardBody className="relative h-48 flex-none bg-muted py-0 sm:h-56 lg:h-64">
          {product.image_url ? (
            <img
              alt={product.name}
              className="absolute inset-0 h-full w-full object-cover"
              draggable={false}
              loading="lazy"
              src={product.image_url}
            />
          ) : (
            <ProductImagePlaceholder
              productName={product.name}
              className="absolute inset-0"
              iconClassName="size-10 text-muted-foreground/60"
            />
          )}
        </SquircleCardBody>
        <div className="flex flex-1 flex-col gap-1 px-3 py-3">
          <p className="text-xs text-muted-foreground">{product.category}</p>
          <h3 className="line-clamp-1 text-sm font-medium text-foreground md:text-base">
            {product.name}
          </h3>
          <span className="text-sm font-semibold md:text-base">
            {formatCurrency(Number(product.price))}
          </span>
        </div>
      </SquircleCard>
    </Link>
  )
}
