import { Link } from "react-router"

import { productPriceFormatter, type Product } from "@/lib/products"

type ProductCardProps = {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      aria-label={`Xem chi tiết ${product.name}`}
      className="group flex h-full flex-col border-r border-b border-border max-md:nth-[2n]:border-r-0 max-md:nth-last-[-n+2]:border-b-0 md:max-lg:nth-[3n]:border-r-0 md:max-lg:nth-last-[-n+3]:border-b-0 lg:nth-[4n]:border-r-0 lg:nth-last-[-n+4]:border-b-0"
      to={`/products/${product.id}`}
    >
      <div className="h-48 w-full shrink-0 overflow-hidden border-b border-border bg-muted sm:h-56 lg:h-64">
        <img
          alt={product.name}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
          src={product.image}
        />
      </div>
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        <h3 className="line-clamp-1 text-sm font-medium text-foreground">
          {product.name}
        </h3>
        <span className="text-sm font-semibold">
          {productPriceFormatter.format(product.price)}
        </span>
        <p className="line-clamp-2 text-xs text-muted-foreground">
          {product.shortDescription}
        </p>
      </div>
    </Link>
  )
}
