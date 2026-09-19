import { useMemo } from "react"
import { SearchIcon } from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from "nuqs"

import type { ProductRecord } from "@/api/products"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { SortButton } from "@/components/admin/management/sort-button"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { useDebounce } from "@/hooks/use-debounce"
import { useProducts } from "@/hooks/use-products"
import type { Category } from "@/lib/admin-management"
import { formatDate } from "@/lib/date"
import { normalizeText } from "@/lib/format"

const CATEGORY_SORT_KEYS = ["name", "productCount", "updatedAt"] as const
const SORT_DIRECTIONS = ["asc", "desc"] as const
const CATEGORY_PAGE_SIZE = 10

type CategorySortKey = (typeof CATEGORY_SORT_KEYS)[number]

const categoryQueryParsers = {
  search: parseAsString.withDefault(""),
  sort: parseAsStringLiteral(CATEGORY_SORT_KEYS).withDefault("name"),
  direction: parseAsStringLiteral(SORT_DIRECTIONS).withDefault("asc"),
  page: parseAsInteger.withDefault(1),
}
const categoryQueryOptions = { urlKeys: { search: "q" } }

const mapCategories = (products: ProductRecord[]): Category[] => {
  const categoryMap = new Map<string, Category>()

  for (const product of products) {
    const current = categoryMap.get(product.category)
    if (current) {
      current.productCount += 1
      if (product.updated_at > current.updatedAt) {
        current.updatedAt = product.updated_at
      }
      continue
    }

    categoryMap.set(product.category, {
      id: `category:${product.category}`,
      code: product.category,
      name: product.category,
      productCount: 1,
      updatedAt: product.updated_at,
    })
  }

  return Array.from(categoryMap.values())
}

export const Component = () => {
  const [{ search, sort, direction, page }, setQuery] = useQueryStates(
    categoryQueryParsers,
    categoryQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const productsQuery = useProducts({ page: 1, size: 100 })
  const categories = useMemo(
    () => mapCategories(productsQuery.data?.records ?? []),
    [productsQuery.data?.records]
  )
  const loading = productsQuery.isPending

  const filteredCategories = useMemo(() => {
    const query = normalizeText(debouncedSearch.trim())

    return categories
      .filter(
        (category) =>
          !query ||
          [category.name, category.code].some((value) =>
            normalizeText(value).includes(query)
          )
      )
      .sort((first, second) => {
        const sortMultiplier = direction === "asc" ? 1 : -1
        const comparison =
          sort === "productCount"
            ? first.productCount - second.productCount
            : sort === "updatedAt"
              ? first.updatedAt.localeCompare(second.updatedAt)
              : first.name.localeCompare(second.name, "vi", { numeric: true })

        return comparison * sortMultiplier
      })
  }, [categories, debouncedSearch, direction, sort])

  const toggleSort = (key: CategorySortKey) => {
    void setQuery({
      sort: key,
      direction: sort === key && direction === "asc" ? "desc" : "asc",
      page: 1,
    })
  }

  const updateSearch = (value: string) => {
    void setQuery(
      { search: value, page: 1 },
      { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
    )
  }

  const currentPage = Math.max(page, 1)

  const columns: CommonTableColumn<Category>[] = [
    {
      id: "category",
      header: (
        <SortButton
          label="Danh mục"
          sortKey="name"
          activeKey={sort}
          direction={direction}
          onClick={() => toggleSort("name")}
        />
      ),
      className: "min-w-56 whitespace-nowrap",
      cell: (category) => (
        <span className="whitespace-nowrap">{category.name}</span>
      ),
      skeletonClassName: "h-6 w-4/5",
    },
    {
      id: "code",
      header: "Mã danh mục",
      className: "min-w-32 whitespace-nowrap",
      cell: (category) => (
        <span className="text-sm whitespace-nowrap">{category.code}</span>
      ),
    },
    {
      id: "productCount",
      header: (
        <SortButton
          label="Số sản phẩm"
          sortKey="productCount"
          activeKey={sort}
          direction={direction}
          onClick={() => toggleSort("productCount")}
        />
      ),
      className: "min-w-32 whitespace-nowrap",
      cell: (category) => (
        <span className="whitespace-nowrap">
          {category.productCount} sản phẩm
        </span>
      ),
    },
    {
      id: "updatedAt",
      header: (
        <SortButton
          label="Cập nhật"
          sortKey="updatedAt"
          activeKey={sort}
          direction={direction}
          onClick={() => toggleSort("updatedAt")}
        />
      ),
      className: "min-w-32 whitespace-nowrap",
      cell: (category) => (
        <span className="whitespace-nowrap">
          {formatDate(category.updatedAt)}
        </span>
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Danh mục</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Xem các nhóm sản phẩm và số lượng sản phẩm trong từng danh mục.
        </p>
      </header>
      <div className="flex min-w-0 flex-col gap-4">
        <div className="flex flex-col gap-2 px-3 lg:flex-row">
          <InputGroup className="lg:max-w-sm">
            <InputGroupAddon>
              <SearchIcon />
            </InputGroupAddon>
            <InputGroupInput
              value={search}
              onChange={(event) => updateSearch(event.target.value)}
              placeholder="Tìm tên hoặc mã danh mục..."
              aria-label="Tìm kiếm danh mục"
            />
          </InputGroup>
          {(search || categories.length !== filteredCategories.length) && (
            <Button
              type="button"
              variant="ghost"
              onClick={() => updateSearch("")}
            >
              Xoá lọc
            </Button>
          )}
        </div>
        <CommonTable
          data={filteredCategories}
          columns={columns}
          loading={loading}
          itemLabel="danh mục"
          getRowId={(category) => category.id}
          emptyMessage={
            <EmptyTableState
              title="Không tìm thấy danh mục"
              description="Danh mục được tổng hợp từ sản phẩm trong hệ thống."
            />
          }
          pagination={{
            page: currentPage,
            pageSize: CATEGORY_PAGE_SIZE,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </div>
    </div>
  )
}

export default Component
