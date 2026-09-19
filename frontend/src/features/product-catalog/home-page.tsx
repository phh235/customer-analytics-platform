import { lazy, Suspense } from "react"

import { Link } from "react-router"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { ProductCardSkeleton } from "@/features/product-catalog/product-card-skeleton"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { Skeleton } from "@/components/ui/skeleton"
import { BRAND_NAME } from "@/lib/brand"
import { useProducts } from "@/hooks/use-products"
import { useAuthStore } from "@/stores/use-auth-store"
import { ArrowRight } from "lucide-react"
import { LineShadowText } from "@/components/line-shadow-text"
import azukiLogo from "@/assets/azuki-logo-primary.png"
// import Integrations from "@/integrations"

const PRODUCT_SKELETON_IDS = ["one", "two", "three", "four"] as const
const AsciiObject = lazy(() => import("@/components/ascii-object"))
export const Component = () => {
  const isSessionPending = useAuthStore(
    (state) => state.status === "unknown" || state.status === "loading"
  )
  const productsQuery = useProducts({ page: 1, size: 4 })
  const products = productsQuery.data?.records ?? []
  const loading = productsQuery.isPending

  return (
    <ClientPageLayout>
      {isSessionPending || loading ? (
        <span className="sr-only" role="status">
          Đang xác thực phiên đăng nhập
        </span>
      ) : null}
      <Panel className="screen-border-top-none">
        <PanelContent className="flex flex-col items-center justify-center p-0 text-left md:flex-row">
          {isSessionPending || loading ? (
            <>
              <div className="flex w-full max-w-xl flex-col gap-3 px-6 py-6 md:flex-1 md:px-8 md:py-8">
                <Skeleton className="h-8 w-4/5" />
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-3/4" />
              </div>
              <div className="flex w-full items-center justify-center p-4 md:flex-1">
                <Skeleton className="h-64 w-full max-w-xl md:h-72" />
              </div>
            </>
          ) : (
            <>
              <div className="flex w-full max-w-xl flex-col gap-3 px-6 py-6 md:flex-1 md:px-8 md:py-8">
                <h1 className="text-xl font-bold md:text-3xl">
                  Chào mừng bạn đến với{" "}
                  <LineShadowText
                    shadowColor="var(--color-primary)"
                    className="text-primary italic"
                  >
                    {BRAND_NAME}
                  </LineShadowText>
                </h1>
                <p className="text-muted-foreground">
                  Khám phá những sản phẩm được tuyển chọn với thiết kế hiện đại
                  và phong cách riêng dành cho bạn.
                </p>
              </div>
              <div className="flex w-full items-center justify-center md:flex-1">
                <Suspense
                  fallback={<div className="h-64 w-full max-w-xl md:h-72" />}
                >
                  <AsciiObject
                    src={azukiLogo}
                    autoRotate
                    autoRotateSpeed={2}
                    floatIntensity={2.8}
                    highlight="#91AE6E"
                    scale={3.4}
                    yOffset={-0.2}
                    className="h-64 w-full max-w-xl md:h-72"
                  />
                </Suspense>
              </div>
            </>
          )}
        </PanelContent>
      </Panel>

      <Separator />

      <Panel>
        <PanelContent>
          {isSessionPending || loading ? (
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-40" />
              <Skeleton className="h-4 w-72 max-w-full" />
            </div>
          ) : (
            <>
              <h2 className="text-xl font-bold">Sản phẩm nổi bật</h2>
              <p className="text-sm text-muted-foreground">
                Khám phá những sản phẩm mới nhất dành cho bạn.
              </p>
            </>
          )}
        </PanelContent>
      </Panel>

      <Panel className="screen-border-top-none">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {isSessionPending || loading
            ? PRODUCT_SKELETON_IDS.map((id) => <ProductCardSkeleton key={id} />)
            : products
                .slice(0, 4)
                .map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
        </div>
      </Panel>

      <Panel className="screen-border-top-none">
        <PanelContent className="flex justify-center py-4">
          {isSessionPending || loading ? (
            <Skeleton className="h-9 w-44" />
          ) : (
            <Button
              nativeButton={false}
              render={<Link to="/products" />}
              variant="outline"
            >
              Xem tất cả sản phẩm <ArrowRight />
            </Button>
          )}
        </PanelContent>
      </Panel>

      <Separator />

      {/* <Panel>
        <Integrations />
      </Panel>

      <Separator /> */}
    </ClientPageLayout>
  )
}
