import { Link } from "react-router"

import { type ProductRecord } from "@/api/products"

const productPriceFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
})

type ProductCardProps = {
  product: ProductRecord
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      aria-label={`Xem chi tiết ${product.name}`}
      className="group flex h-full flex-col border-r border-b border-border max-md:nth-[2n]:border-r-0 max-md:nth-last-[-n+2]:border-b-0 md:max-lg:nth-[3n]:border-r-0 md:max-lg:nth-last-[-n+3]:border-b-0 lg:nth-[4n]:border-r-0 lg:nth-last-[-n+4]:border-b-0"
      to={`/products/${product.id}`}
    >
      <div className="relative flex h-48 w-full shrink-0 items-end overflow-hidden border-b border-border bg-muted p-4 sm:h-56 lg:h-64">
        {product.image_url ? (
          <img
            alt={product.name}
            className="absolute inset-0 h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            draggable={false}
            loading="lazy"
            src={product.image_url}
          />
        ) : (
          <span className="text-4xl font-black uppercase tracking-tight text-foreground/15 transition-transform duration-300 group-hover:scale-105 sm:text-5xl">
            {product.category.slice(0, 2)}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-1 p-3">
        <p className="text-xs text-muted-foreground">{product.category}</p>
        <h3 className="line-clamp-1 text-sm font-medium text-foreground md:text-base">
          {product.name}
        </h3>
        <span className="text-sm font-semibold md:text-base">
          {productPriceFormatter.format(Number(product.price))}
        </span>
      </div>
    </Link>
  )
}
