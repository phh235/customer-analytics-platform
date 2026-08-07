import { useMemo } from "react"
import { FilterXIcon, SearchIcon } from "lucide-react"
import { debounce, defaultRateLimit, parseAsString, useQueryStates } from "nuqs"

import { ClientPageLayout } from "@/components/client-page-layout"
import { ProductCard } from "@/components/product-card"
import { ProductCardSkeleton } from "@/features/product-catalog/product-card-skeleton"
import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty"
import { AppSelect } from "@/components/common/app-select"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Panel, PanelContent, Separator } from "@/components/ui/panel"
import { Skeleton } from "@/components/ui/skeleton"
import { useDebounce } from "@/hooks/use-debounce"
import { normalizeProductText, products } from "@/lib/products"
import { useAuthStore } from "@/stores/use-auth-store"

const clientProductQueryParsers = {
  search: parseAsString.withDefault(""),
  category: parseAsString.withDefault("all"),
}
const clientProductQueryOptions = { urlKeys: { search: "q" } }
const PRODUCT_SKELETON_IDS = [
  "one",
  "two",
  "three",
  "four",
  "five",
  "six",
  "seven",
  "eight",
] as const

export const Component = () => {
  const isSessionPending = useAuthStore(
    (state) => state.status === "unknown" || state.status === "loading"
  )
  const [{ search, category }, setQuery] = useQueryStates(
    clientProductQueryParsers,
    clientProductQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)

  const categories = useMemo(
    () =>
      Array.from(new Set(products.map((product) => product.category))).sort(
        (first, second) => first.localeCompare(second, "vi")
      ),
    []
  )

  const filteredProducts = useMemo(() => {
    const query = normalizeProductText(debouncedSearch.trim())

    return products.filter((product) => {
      const matchesSearch =
        !query ||
        [product.name, product.category, product.shortDescription].some(
          (value) => normalizeProductText(value).includes(query)
        )
      const matchesCategory =
        category === "all" || product.category === category

      return matchesSearch && matchesCategory
    })
  }, [category, debouncedSearch])

  const resetFilters = () => {
    void setQuery({ search: "", category: "all" })
  }

  const updateSearch = (value: string) => {
    void setQuery(
      { search: value },
      { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
    )
  }

  return (
    <ClientPageLayout>
      {isSessionPending ? (
        <span className="sr-only" role="status">
          Đang xác thực phiên đăng nhập
        </span>
      ) : null}
      <Panel className="screen-border-bottom-none screen-border-top-none">
        <PanelContent className="p-4">
          {isSessionPending ? (
            <div className="flex flex-col gap-2">
              <Skeleton className="h-6 w-28" />
              <Skeleton className="h-4 w-80 max-w-full" />
            </div>
          ) : (
            <>
              <h1 className="text-xl font-bold">Sản phẩm</h1>
              <p className="text-sm text-muted-foreground">
                Khám phá những sản phẩm được lựa chọn dành cho bạn.
              </p>
            </>
          )}
        </PanelContent>
      </Panel>

      <Panel className="screen-border-bottom-none">
        <PanelContent className="flex flex-col gap-3 sm:flex-row sm:items-center">
          {isSessionPending ? (
            <>
              <Skeleton className="h-9 w-full sm:flex-1" />
              <Skeleton className="h-9 w-full sm:w-56" />
            </>
          ) : (
            <>
              <InputGroup className="sm:flex-1">
                <InputGroupAddon>
                  <SearchIcon />
                </InputGroupAddon>
                <InputGroupInput
                  value={search}
                  onChange={(event) => updateSearch(event.target.value)}
                  placeholder="Tìm tên sản phẩm..."
                  aria-label="Tìm kiếm sản phẩm"
                />
              </InputGroup>
              <AppSelect
                options={[
                  { value: "all", label: "Tất cả danh mục" },
                  ...categories.map((item) => ({ value: item, label: item })),
                ]}
                value={category}
                onChange={(value) =>
                  void setQuery({ category: value || "all" })
                }
                className="w-full sm:w-56"
                aria-label="Lọc theo danh mục"
              />
              {search || category !== "all" ? (
                <Button type="button" variant="ghost" onClick={resetFilters}>
                  <FilterXIcon data-icon="inline-start" />
                  Xoá lọc
                </Button>
              ) : null}
            </>
          )}
        </PanelContent>
      </Panel>

      <Panel>
        {isSessionPending ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {PRODUCT_SKELETON_IDS.map((id) => (
              <ProductCardSkeleton key={id} />
            ))}
          </div>
        ) : filteredProducts.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {filteredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <Empty className="border-0">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <SearchIcon />
              </EmptyMedia>
              <EmptyTitle>Không tìm thấy sản phẩm</EmptyTitle>
              <EmptyDescription>
                Thử đổi từ khoá hoặc chọn lại danh mục để xem thêm sản phẩm.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        )}
      </Panel>

      <Separator />
    </ClientPageLayout>
  )
}

export default Component
