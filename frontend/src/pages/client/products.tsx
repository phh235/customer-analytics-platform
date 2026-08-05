import { ProductCard } from "@/components/product-card"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { products } from "@/lib/products"

export const Component = () => {
  return (
    <main className="max-w-screen overflow-x-clip">
      <div className="[--separator-height:--spacing(8)]">
        <div className="mx-auto max-w-5xl">
          <Panel className="screen-border-bottom-none screen-border-top-none">
            <PanelContent className="p-4">
              <h1 className="text-xl font-bold">Sản phẩm</h1>
              <p className="text-sm text-muted-foreground">
                Khám phá những sản phẩm được lựa chọn dành cho bạn.
              </p>
            </PanelContent>
          </Panel>

          <Panel>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {products.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </Panel>

          <Separator />
        </div>
      </div>
    </main>
  )
}
