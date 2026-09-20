import { useEffect, useMemo } from "react"
import { ArrowLeftIcon } from "lucide-react"
import { Link, Navigate, useParams } from "react-router"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductImagePlaceholder } from "@/components/common/product-image-placeholder"
import { ProductCard } from "@/components/product-card"
import { ProductCardSkeleton } from "@/features/product-catalog/product-card-skeleton"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Panel,
  PanelContent,
  Separator as ScreenSeparator,
} from "@/components/ui/panel"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { useAuthStore } from "@/stores/use-auth-store"
import { useProduct, useProducts } from "@/hooks/use-products"
import { formatCurrency } from "@/lib/format"
import { recordProductView } from "@/api/product-analytics"

export const Component = () => {
  const { productId } = useParams()
  const sessionStatus = useAuthStore((state) => state.status)
  const isSessionPending =
    sessionStatus === "unknown" || sessionStatus === "loading"
  const productQuery = useProduct(productId)
  const productsQuery = useProducts(
    { page: 1, size: 12 },
    "Không thể tải sản phẩm liên quan."
  )
  const product = productQuery.data ?? null
  const resolvedProductId = product?.id
  const loading = productQuery.isPending

  useEffect(() => {
    if (!resolvedProductId || sessionStatus !== "authenticated") return
    void recordProductView(resolvedProductId).catch(() => undefined)
  }, [resolvedProductId, sessionStatus])

  const relatedProducts = useMemo(() => {
    if (!product) return []

    const seenIds = new Set([product.id])
    return [
      ...(product.related_products ?? []),
      ...(productsQuery.data?.records ?? []),
    ]
      .filter((candidate) => {
        if (seenIds.has(candidate.id)) return false
        seenIds.add(candidate.id)
        return true
      })
      .slice(0, 4)
  }, [product, productsQuery.data?.records])
  const relatedProductsLoading =
    isSessionPending || productQuery.isPending || productsQuery.isPending
  const relatedSkeletonCount = relatedProductsLoading
    ? Math.max(0, 4 - relatedProducts.length)
    : 0

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
        <div className="p-3 sm:p-4">
          {isSessionPending || loading ? (
            <SquircleCard className="grid w-full gap-1 lg:grid-cols-[22rem_minmax(0,1fr)]">
              <div className="relative h-72 overflow-hidden rounded-xl sm:h-80 lg:h-[22rem]">
                <Skeleton className="size-full rounded-none" />
                <div className="pointer-events-none absolute inset-0 rounded-xl inset-ring-1 inset-ring-black/10 dark:inset-ring-white/10" />
              </div>
              <SquircleCardBody className="justify-center gap-3 border-0! bg-transparent! px-6 py-5 sm:px-8 sm:py-6 lg:h-[22rem]">
                <div className="flex gap-2">
                  <Skeleton className="h-5 w-20" />
                  <Skeleton className="h-5 w-24" />
                </div>
                <Skeleton className="h-10 w-4/5" />
                <Skeleton className="h-9 w-40" />
                <Skeleton className="h-px w-full" />
                <Skeleton className="h-20 w-full" />
              </SquircleCardBody>
            </SquircleCard>
          ) : product ? (
            <SquircleCard className="grid w-full gap-1 lg:grid-cols-[22rem_minmax(0,1fr)]">
              <div className="relative h-72 overflow-hidden rounded-xl sm:h-80 lg:h-[22rem]">
                {product.image_url ? (
                  <img
                    alt={product.name}
                    className="absolute inset-0 size-full object-contain"
                    draggable={false}
                    src={product.image_url}
                  />
                ) : (
                  <ProductImagePlaceholder
                    productName={product.name}
                    className="absolute inset-0"
                    iconClassName="size-16 text-muted-foreground/60"
                  />
                )}
                <div className="pointer-events-none absolute inset-0 rounded-xl inset-ring-1 inset-ring-black/10 dark:inset-ring-white/10" />
              </div>

              <SquircleCardBody className="justify-center gap-3 border-0! bg-transparent! px-6 py-5 sm:px-8 sm:py-6 lg:h-[22rem]">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="secondary">{product.category}</Badge>
                  <Badge
                    variant={
                      product.status === "ACTIVE" ? "success" : "secondary"
                    }
                  >
                    {product.status === "ACTIVE" ? "Đang bán" : "Tạm ẩn"}
                  </Badge>
                </div>

                <div className="flex flex-col gap-2">
                  <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                    {product.product_code}
                  </p>
                  <h1 className="text-2xl leading-tight font-semibold tracking-tight sm:text-3xl">
                    {product.name}
                  </h1>
                </div>

                <p className="text-2xl font-semibold tracking-tight text-primary">
                  {formatCurrency(Number(product.price))}
                </p>

                <Separator />

                <div className="flex flex-col gap-2">
                  <h2 className="text-sm font-medium">Thông tin sản phẩm</h2>
                  <p className="text-sm leading-6 text-muted-foreground sm:text-base">
                    {product.description ||
                      `Sản phẩm đang được cung cấp trong danh mục ${product.category}.`}
                  </p>
                </div>

                <dl className="grid grid-cols-2 gap-4 rounded-xl bg-muted/50 p-3 text-sm">
                  <div className="flex flex-col gap-1">
                    <dt className="text-xs text-muted-foreground">
                      Mã sản phẩm
                    </dt>
                    <dd className="font-medium">{product.product_code}</dd>
                  </div>
                  <div className="flex flex-col gap-1">
                    <dt className="text-xs text-muted-foreground">SKU</dt>
                    <dd className="font-medium">
                      {product.sku || "Chưa cập nhật"}
                    </dd>
                  </div>
                </dl>
              </SquircleCardBody>
            </SquircleCard>
          ) : null}
        </div>
      </Panel>

      <ScreenSeparator />

      <Panel>
        <PanelContent>
          <h2 className="text-xl font-semibold">Sản phẩm liên quan</h2>
          <p className="text-sm text-muted-foreground">
            Các sản phẩm khác có thể bạn quan tâm.
          </p>
        </PanelContent>
        <PanelContent className="screen-border-top grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
          {relatedProducts.map((relatedProduct) => (
            <ProductCard key={relatedProduct.id} product={relatedProduct} />
          ))}
          {Array.from({ length: relatedSkeletonCount }, (_, index) => (
            <ProductCardSkeleton key={`related-product-skeleton-${index}`} />
          ))}
        </PanelContent>
      </Panel>

      <ScreenSeparator />
    </ClientPageLayout>
  )
}
