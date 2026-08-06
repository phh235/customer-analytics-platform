import { lazy, Suspense } from "react"

import { Link } from "react-router"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { BRAND_NAME } from "@/lib/brand"
import { products } from "@/lib/products"
import { ArrowRight } from "lucide-react"
import { LineShadowText } from "@/components/line-shadow-text"
// import Integrations from "@/integrations"

const AsciiObject = lazy(() => import("@/components/ascii-object"))

export const Component = () => {
  return (
    <ClientPageLayout>
      <Panel className="screen-border-top-none">
        <PanelContent className="flex flex-col items-center justify-center p-0 text-left md:flex-row">
          <div className="flex w-full max-w-xl flex-col gap-3 px-6 py-8 md:flex-1 md:px-8 md:py-10">
            <h1 className="text-xl font-bold md:text-3xl">
              Chào mừng bạn đến với{" "}
              <LineShadowText
                shadowColor="var(--color-foreground)"
                className="italic"
              >
                {BRAND_NAME}
              </LineShadowText>
            </h1>
            <p className="text-muted-foreground">
              Khám phá những sản phẩm được tuyển chọn với thiết kế hiện đại và
              phong cách riêng dành cho bạn.
            </p>
          </div>
          <div className="flex w-full items-center justify-center md:flex-1">
            <Suspense
              fallback={<div className="h-80 w-full max-w-xl md:h-96" />}
            >
              <AsciiObject
                autoRotate
                autoRotateSpeed={2}
                floatIntensity={2.8}
                scale={3.4}
                yOffset={-0.2}
                className="h-80 w-full max-w-xl md:h-96"
              />
            </Suspense>
          </div>
        </PanelContent>
      </Panel>

      <Separator />

      <Panel>
        <PanelContent>
          <h2 className="text-xl font-bold">Sản phẩm nổi bật</h2>
          <p className="text-sm text-muted-foreground">
            Khám phá những sản phẩm mới nhất dành cho bạn.
          </p>
        </PanelContent>
      </Panel>

      <Panel className="screen-border-top-none">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {products.slice(0, 4).map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </Panel>

      <Panel className="screen-border-top-none">
        <PanelContent className="flex justify-center py-4">
          <Button
            nativeButton={false}
            render={<Link to="/products" />}
            variant="outline"
          >
            Xem tất cả sản phẩm <ArrowRight />
          </Button>
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
