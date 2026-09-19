import { useMemo } from "react"
import { ArrowLeftIcon } from "lucide-react"
import { Link, Navigate, useParams } from "react-router"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuthStore } from "@/stores/use-auth-store"
import { useProduct } from "@/hooks/use-products"
import { formatCurrency } from "@/lib/format"

export const Component = () => {
  const { productId } = useParams()
  const isSessionPending = useAuthStore(
    (state) => state.status === "unknown" || state.status === "loading"
  )
  const productQuery = useProduct(productId)
  const product = productQuery.data ?? null
  const loading = productQuery.isPending

  const relatedProducts = useMemo(
    () => product?.related_products ?? [],
    [product?.related_products]
  )

  if (!isSessionPending && !loading && !product) {
    return <Navigate replace to="/products" />
  }

  return (
    <ClientPageLayout>
      <Panel className="screen-border-bottom-none screen-border-top-none">
        <PanelContent className="p-2 px-4">
          <Button
            className="-ml-2"
            nativeButton={false}
            render={<Link to="/products" />}
            variant="ghost"
          >
            <ArrowLeftIcon aria-hidden="true" />
            Quay lại sản phẩm
          </Button>
        </PanelContent>
      </Panel>

      <Panel>
        {isSessionPending || loading ? (
          <div className="grid md:grid-cols-2">
            <Skeleton className="h-85 w-full md:h-100" />
            <div className="flex flex-col gap-4 p-6 md:p-8">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-7 w-40" />
            </div>
          </div>
        ) : product ? (
          <div className="grid md:grid-cols-2">
            <div className="relative flex h-85 items-end overflow-hidden border-b border-border bg-muted p-8 md:h-100 md:border-r md:border-b-0">
              {product.image_url ? (
                <img
                  alt={product.name}
                  className="absolute inset-0 h-full w-full object-cover"
                  draggable={false}
                  src={product.image_url}
                />
              ) : (
                <span className="text-8xl font-black tracking-tight text-foreground/15 uppercase">
                  {product.category.slice(0, 2)}
                </span>
              )}
            </div>
            <div className="flex flex-col justify-center gap-4 p-6 md:p-8">
              <p className="text-sm text-muted-foreground">
                {product.category}
              </p>
              <h1 className="text-2xl font-bold">{product.name}</h1>
              <p className="text-xl font-semibold">
                {formatCurrency(Number(product.price))}
              </p>
              <p className="text-sm leading-7 text-muted-foreground md:text-base">
                {product.description ||
                  `Sản phẩm đang được cung cấp trong danh mục ${product.category}.`}
              </p>
              <p className="text-xs text-muted-foreground">
                Trạng thái:{" "}
                {product.status === "ACTIVE" ? "Đang bán" : "Tạm ẩn"}
              </p>
            </div>
          </div>
        ) : null}
      </Panel>

      <Separator />

      <Panel>
        <PanelContent>
          <h2 className="text-xl font-bold">Sản phẩm liên quan</h2>
          <p className="text-sm text-muted-foreground">
            Các sản phẩm khác trong cùng danh mục.
          </p>
        </PanelContent>
      </Panel>

      <Panel className="screen-border-top-none">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {relatedProducts.map((relatedProduct) => (
            <ProductCard key={relatedProduct.id} product={relatedProduct} />
          ))}
        </div>
      </Panel>

      <Separator />
    </ClientPageLayout>
  )
}
