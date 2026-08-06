import { Link } from "react-router"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { products } from "@/lib/products"
import CarouselClient from "@/components/carousel"
import { ArrowRight } from "lucide-react"

export const Component = () => {
  return (
    <ClientPageLayout>
      <Panel className="screen-border-top-none">
        <PanelContent className="flex flex-col items-start justify-center gap-4 p-0 text-left md:flex-row md:items-center">
          <div className="flex flex-col gap-4 px-4 pt-4 md:pt-0">
            <h1 className="text-2xl font-bold">
              Chào mừng bạn đến với Customer Analytics Platform!
            </h1>
            <p className="text-muted-foreground">
              Hệ thống phân tích khách hàng đa chiều hỗ trợ theo dõi hành vi,
              doanh thu, và tối ưu hóa chuyển đổi.
            </p>
          </div>
          <CarouselClient />
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
    </ClientPageLayout>
  )
}
