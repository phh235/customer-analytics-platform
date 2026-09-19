import { useEffect, useMemo, useState } from "react"
import { SearchIcon } from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from "nuqs"

import { getApiErrorMessage } from "@/api/errors"
import { getProducts, type ProductRecord } from "@/api/products"
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
import { formatDate, normalize, type Category } from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

const CATEGORY_SORT_KEYS = ["name", "productCount", "updatedAt"] as const
const SORT_DIRECTIONS = ["asc", "desc"] as const
const CATEGORY_PAGE_SIZE = 6

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
  const [categories, setCategories] = useState<Category[]>([])
  const [{ search, sort, direction, page }, setQuery] = useQueryStates(
    categoryQueryParsers,
    categoryQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    void getProducts({ page: 1, size: 100 })
      .then((response) => {
        if (!cancelled) setCategories(mapCategories(response.records))
      })
      .catch((error: unknown) => {
        if (!cancelled) toastError(getApiErrorMessage(error))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const filteredCategories = useMemo(() => {
    const query = normalize(debouncedSearch.trim())

    return categories
      .filter(
        (category) =>
          !query ||
          [category.name, category.code].some((value) =>
            normalize(value).includes(query)
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

  const columns: CommonTableColumn<Category>[] = useMemo(
    () => [
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
    ],
    [direction, sort]
  )

  return (
    <div className="mx-auto flex w-full flex-col gap-6">
      <div className="overflow-hidden">
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2 p-3 lg:flex-row">
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
        </div>
        <CommonTable
          data={filteredCategories}
          columns={columns}
          loading={loading}
          summary={
            loading
              ? "Đang tải danh mục..."
              : `Hiển thị ${filteredCategories.length === 0 ? "0" : `${(currentPage - 1) * CATEGORY_PAGE_SIZE + 1}–${Math.min(currentPage * CATEGORY_PAGE_SIZE, filteredCategories.length)}`} / ${filteredCategories.length} danh mục`
          }
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
