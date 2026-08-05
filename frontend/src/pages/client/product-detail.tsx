import { ArrowLeftIcon } from "lucide-react"
import { Link, Navigate, useParams } from "react-router"

import { ProductCard } from "@/components/product-card"
import { Button } from "@/components/ui/button"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { getProductById, productPriceFormatter, products } from "@/lib/products"

export const Component = () => {
  const { productId } = useParams()
  const product = productId ? getProductById(productId) : undefined

  if (!product) {
    return <Navigate replace to="/products" />
  }

  const relatedProducts = products
    .filter((p) => p.id !== product.id)
    .slice(0, 4)

  return (
    <main className="max-w-screen overflow-x-clip">
      <div className="[--separator-height:--spacing(8)]">
        <div className="mx-auto max-w-5xl">
          <Panel className="screen-border-top-none">
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

          <Separator />

          <Panel>
            <div className="grid md:grid-cols-2">
              <div className="h-85 w-full overflow-hidden border-b border-border bg-muted md:h-100 md:border-r md:border-b-0">
                <img
                  alt={product.name}
                  className="h-full w-full object-cover"
                  src={product.image}
                />
              </div>
              <div className="flex flex-col justify-center gap-4 p-6 md:p-8">
                <p className="text-sm text-muted-foreground">
                  Chi tiết sản phẩm
                </p>
                <h1 className="text-2xl font-bold">{product.name}</h1>
                <p className="text-xl font-semibold">
                  {productPriceFormatter.format(product.price)}
                </p>
                <p className="leading-7 text-muted-foreground">
                  {product.description}
                </p>
              </div>
            </div>
          </Panel>

          <Separator />

          <Panel>
            <PanelContent>
              <h2 className="text-xl font-bold">Sản phẩm liên quan</h2>
              <p className="text-sm text-muted-foreground">
                Có thể bạn cũng thích những sản phẩm này.
              </p>
            </PanelContent>
          </Panel>

          <Panel className="screen-border-top-none">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {relatedProducts.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          </Panel>

          <Separator />
        </div>
      </div>
    </main>
  )
}
