import { Link } from "react-router"

import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { products } from "@/lib/products"
import { ArrowRight } from "lucide-react"

export const Component = () => {
  return (
    <main className="max-w-screen overflow-x-clip">
      <div className="[--separator-height:--spacing(8)]">
        <div className="mx-auto max-w-5xl">
          <Panel className="screen-border-top-none">
            <PanelContent className="flex flex-col items-center justify-center text-center">
              <h1 className="text-2xl font-bold">
                Chào mừng bạn đến với Customer Analytics Platform!
              </h1>
              <p className="text-muted-foreground">
                Hệ thống phân tích khách hàng đa chiều hỗ trợ theo dõi hành vi,
                doanh thu, và tối ưu hóa chuyển đổi.
              </p>
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
        </div>
      </div>
    </main>
  )
}
