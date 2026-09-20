import { useMemo } from "react"
import { FilterXIcon, SearchIcon } from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  useQueryStates,
} from "nuqs"

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
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { useDebounce } from "@/hooks/use-debounce"
import { useProducts } from "@/hooks/use-products"
import { PRODUCT_CATEGORIES } from "@/lib/products"
import { useAuthStore } from "@/stores/use-auth-store"

const clientProductQueryParsers = {
  search: parseAsString.withDefault(""),
  category: parseAsString.withDefault("all"),
  page: parseAsInteger.withDefault(1),
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
  "nine",
  "ten",
  "eleven",
  "twelve",
] as const
const PRODUCT_PAGE_SIZE = 12

export const Component = () => {
  const isSessionPending = useAuthStore(
    (state) => state.status === "unknown" || state.status === "loading"
  )
  const [{ search, category, page }, setQuery] = useQueryStates(
    clientProductQueryParsers,
    clientProductQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const currentPage = Math.max(page, 1)
  const productsQuery = useProducts({
    page: currentPage,
    size: PRODUCT_PAGE_SIZE,
    search: debouncedSearch || undefined,
    category: category === "all" ? undefined : category,
  })
  const products = useMemo(
    () => productsQuery.data?.records ?? [],
    [productsQuery.data?.records]
  )
  const loading = productsQuery.isPending

  const categories = PRODUCT_CATEGORIES
  const totalPages = productsQuery.data?.pages ?? 1

  const resetFilters = () => {
    void setQuery({ search: "", category: "all", page: 1 })
  }

  const updateSearch = (value: string) => {
    void setQuery(
      { search: value, page: 1 },
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
          {isSessionPending || loading ? (
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
          {isSessionPending || loading ? (
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
                  void setQuery({ category: value || "all", page: 1 })
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
        {isSessionPending || loading ? (
          <div className="grid grid-cols-2 gap-3 p-3 md:grid-cols-3 lg:grid-cols-4">
            {PRODUCT_SKELETON_IDS.map((id) => (
              <ProductCardSkeleton key={id} />
            ))}
          </div>
        ) : products.length > 0 ? (
          <div className="grid grid-cols-2 gap-3 p-3 md:grid-cols-3 lg:grid-cols-4">
            {products.map((product) => (
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
        {!loading && totalPages > 1 ? (
          <div className="screen-border-top p-3">
            <Pagination aria-label="Phân trang sản phẩm">
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    text="Trước"
                    aria-disabled={currentPage <= 1}
                    className={
                      currentPage <= 1
                        ? "pointer-events-none opacity-50"
                        : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (currentPage > 1) {
                        void setQuery({ page: currentPage - 1 })
                      }
                    }}
                  />
                </PaginationItem>
                {Array.from(
                  { length: totalPages },
                  (_, index) => index + 1
                ).map((pageNumber) => (
                  <PaginationItem key={pageNumber}>
                    <PaginationLink
                      href="#"
                      isActive={pageNumber === currentPage}
                      aria-label={`Trang ${pageNumber}`}
                      onClick={(event) => {
                        event.preventDefault()
                        void setQuery({ page: pageNumber })
                      }}
                    >
                      {pageNumber}
                    </PaginationLink>
                  </PaginationItem>
                ))}
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    text="Sau"
                    aria-disabled={currentPage >= totalPages}
                    className={
                      currentPage >= totalPages
                        ? "pointer-events-none opacity-50"
                        : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (currentPage < totalPages) {
                        void setQuery({ page: currentPage + 1 })
                      }
                    }}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        ) : null}
      </Panel>

      <Separator />
    </ClientPageLayout>
  )
}

export default Component
