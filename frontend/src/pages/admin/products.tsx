import { useEffect, useMemo, useState } from "react"
import {
  EditIcon,
  FilterXIcon,
  PlusIcon,
  SearchIcon,
  Trash2Icon,
} from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from "nuqs"

import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { AppSelect } from "@/components/common/app-select"
import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { ConfirmProductStatusDialog } from "@/components/admin/management/confirm-product-status-dialog"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { ProductFormSheet } from "@/components/admin/management/product-form-sheet"
import { SortButton } from "@/components/admin/management/sort-button"
import { StatusBadge } from "@/components/admin/management/status-badge"
import type { DeleteTarget } from "@/components/admin/management/types"
import { AppDropdown } from "@/components/common/app-dropdown"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Switch } from "@/components/ui/switch"
import { useDebounce } from "@/hooks/use-debounce"
import {
  createId,
  formatCurrency,
  formatDate,
  normalize,
  PRODUCT_CATEGORIES,
  SAMPLE_PRODUCTS,
  type Product,
  type ProductFormData,
  type ProductStatus,
} from "@/lib/admin-management"
import { toastSuccess } from "@/utils/toast"

const PRODUCT_SORT_KEYS = ["name", "category", "price"] as const
const SORT_DIRECTIONS = ["asc", "desc"] as const
const PRODUCT_STATUSES = ["all", "active", "inactive"] as const

type ProductSortKey = (typeof PRODUCT_SORT_KEYS)[number]
const PRODUCT_PAGE_SIZE = 4

const productQueryParsers = {
  search: parseAsString.withDefault(""),
  category: parseAsString.withDefault("all"),
  status: parseAsStringLiteral(PRODUCT_STATUSES).withDefault("all"),
  sort: parseAsStringLiteral(PRODUCT_SORT_KEYS).withDefault("name"),
  direction: parseAsStringLiteral(SORT_DIRECTIONS).withDefault("asc"),
  page: parseAsInteger.withDefault(1),
}
const productQueryOptions = { urlKeys: { search: "q" } }

export const Component = () => {
  const [products, setProducts] = useState(SAMPLE_PRODUCTS)
  const [{ search, category, status, sort, direction, page }, setQuery] =
    useQueryStates(productQueryParsers, productQueryOptions)
  const debouncedSearch = useDebounce(search, 300)
  const [loading, setLoading] = useState(true)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const [statusTarget, setStatusTarget] = useState<{
    id: string
    name: string
    nextStatus: ProductStatus
  } | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 650)
    return () => window.clearTimeout(timer)
  }, [])

  const categories = useMemo(
    () =>
      Array.from(
        new Set([
          ...PRODUCT_CATEGORIES,
          ...products.map((product) => product.category),
        ])
      ).sort((first, second) => first.localeCompare(second, "vi")),
    [products]
  )

  const filteredProducts = useMemo(() => {
    const query = normalize(debouncedSearch.trim())

    return products
      .filter((product) => {
        const matchesSearch =
          !query ||
          [product.name, product.sku, product.category].some((value) =>
            normalize(value).includes(query)
          )
        const matchesCategory =
          category === "all" || product.category === category
        const matchesStatus = status === "all" || product.status === status

        return matchesSearch && matchesCategory && matchesStatus
      })
      .sort((first, second) => {
        const sortMultiplier = direction === "asc" ? 1 : -1
        const comparison =
          sort === "price"
            ? first[sort] - second[sort]
            : first[sort].localeCompare(second[sort], "vi", {
                numeric: true,
              })

        return comparison * sortMultiplier
      })
  }, [category, debouncedSearch, direction, products, sort, status])

  const openProductSheet = (product: Product | null = null) => {
    setEditingProduct(product)
    setSheetOpen(true)
  }

  const handleSave = (data: ProductFormData) => {
    if (editingProduct) {
      setProducts((current) =>
        current.map((product) =>
          product.id === editingProduct.id
            ? { ...product, ...data, updatedAt: new Date().toISOString() }
            : product
        )
      )
      toastSuccess("Đã cập nhật sản phẩm")
    } else {
      setProducts((current) => [
        {
          id: createId("SP"),
          ...data,
          updatedAt: new Date().toISOString(),
        },
        ...current,
      ])
      toastSuccess("Đã thêm sản phẩm mới")
    }

    setSheetOpen(false)
    setEditingProduct(null)
  }

  const handleDelete = () => {
    if (!deleteTarget) return

    setProducts((current) =>
      current.filter((product) => product.id !== deleteTarget.id)
    )
    toastSuccess("Đã xoá sản phẩm")
    setDeleteTarget(null)
  }

  const handleStatusChange = () => {
    if (!statusTarget) return

    setProducts((current) =>
      current.map((product) =>
        product.id === statusTarget.id
          ? {
              ...product,
              status: statusTarget.nextStatus,
              updatedAt: new Date().toISOString(),
            }
          : product
      )
    )
    toastSuccess(
      statusTarget.nextStatus === "active"
        ? "Đã hiển thị sản phẩm"
        : "Đã ẩn sản phẩm"
    )
    setStatusTarget(null)
  }

  const toggleSort = (key: ProductSortKey) => {
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

  const resetFilters = () => {
    void setQuery({
      search: "",
      category: "all",
      status: "all",
      page: 1,
    })
  }

  const currentPage = Math.max(page, 1)

  const columns: CommonTableColumn<Product>[] = useMemo(
    () => [
      {
        id: "id",
        header: "Mã sản phẩm",
        className: "min-w-28 whitespace-nowrap",
        cell: (product) => (
          <span className="text-sm whitespace-nowrap">{product.id}</span>
        ),
      },
      {
        id: "product",
        header: (
          <SortButton
            label="Sản phẩm"
            sortKey="name"
            activeKey={sort}
            direction={direction}
            onClick={() => toggleSort("name")}
          />
        ),
        className: "min-w-52 whitespace-nowrap",
        cell: (product) => (
          <span className="whitespace-nowrap">{product.name}</span>
        ),
        skeletonClassName: "h-6 w-4/5",
      },
      {
        id: "sku",
        header: "SKU",
        className: "min-w-28 whitespace-nowrap",
        cell: (product) => (
          <span className="text-sm whitespace-nowrap">{product.sku}</span>
        ),
      },
      {
        id: "category",
        header: (
          <SortButton
            label="Danh mục"
            sortKey="category"
            activeKey={sort}
            direction={direction}
            onClick={() => toggleSort("category")}
          />
        ),
        className: "min-w-40 whitespace-nowrap",
        cell: (product) => (
          <span className="whitespace-nowrap">{product.category}</span>
        ),
      },
      {
        id: "price",
        header: (
          <SortButton
            label="Giá bán"
            sortKey="price"
            activeKey={sort}
            direction={direction}
            onClick={() => toggleSort("price")}
          />
        ),
        className: "min-w-32 whitespace-nowrap",
        cell: (product) => (
          <span className="whitespace-nowrap">
            {formatCurrency(product.price)}
          </span>
        ),
      },
      {
        id: "status",
        header: "Trạng thái",
        className: "min-w-28 whitespace-nowrap",
        cell: (product) => {
          const isActive = product.status === "active"

          return (
            <div className="flex items-center gap-2 whitespace-nowrap">
              <Switch
                checked={isActive}
                onCheckedChange={(checked) =>
                  setStatusTarget({
                    id: product.id,
                    name: product.name,
                    nextStatus: checked ? "active" : "inactive",
                  })
                }
                aria-label={`${isActive ? "Ẩn" : "Hiển thị"} ${product.name}`}
              />
              <StatusBadge status={product.status} entity="product" />
            </div>
          )
        },
      },
      {
        id: "updatedAt",
        header: "Cập nhật",
        className: "min-w-28 whitespace-nowrap",
        cell: (product) => (
          <span className="whitespace-nowrap">
            {formatDate(product.updatedAt)}
          </span>
        ),
      },
      {
        id: "actions",
        header: <span className="sr-only">Thao tác</span>,
        className: "w-14 text-right",
        cell: (product) => (
          <div className="flex justify-end">
            <AppDropdown
              aria-label={`Thao tác với ${product.name}`}
              items={[
                {
                  key: "edit",
                  label: "Chỉnh sửa",
                  icon: <EditIcon />,
                  onClick: () => openProductSheet(product),
                },
                {
                  key: "delete",
                  label: "Xoá",
                  icon: <Trash2Icon />,
                  variant: "destructive",
                  onClick: () =>
                    setDeleteTarget({
                      type: "product",
                      id: product.id,
                      name: product.name,
                    }),
                },
              ]}
            />
          </div>
        ),
      },
    ],
    [direction, openProductSheet, sort, toggleSort]
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
                placeholder="Tìm tên, SKU, danh mục..."
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
              className="w-full lg:w-52"
              aria-label="Lọc theo danh mục"
            />
            <AppSelect
              options={[
                { value: "all", label: "Tất cả trạng thái" },
                { value: "active", label: "Đang bán" },
                { value: "inactive", label: "Tạm ẩn" },
              ]}
              value={status}
              onChange={(value) =>
                void setQuery({
                  status: (value || "all") as (typeof PRODUCT_STATUSES)[number],
                  page: 1,
                })
              }
              className="w-full lg:w-44"
              aria-label="Lọc theo trạng thái"
            />
            {(search || category !== "all" || status !== "all") && (
              <Button type="button" variant="ghost" onClick={resetFilters}>
                <FilterXIcon />
                Xoá lọc
              </Button>
            )}
            <Button onClick={() => openProductSheet()} className="ml-auto">
              <PlusIcon />
              Thêm sản phẩm
            </Button>
          </div>
        </div>
        <CommonTable
          data={filteredProducts}
          columns={columns}
          loading={loading}
          summary={
            loading
              ? "Đang tải sản phẩm..."
              : `Hiển thị ${filteredProducts.length === 0 ? "0" : `${(currentPage - 1) * PRODUCT_PAGE_SIZE + 1}–${Math.min(currentPage * PRODUCT_PAGE_SIZE, filteredProducts.length)}`} / ${filteredProducts.length} sản phẩm`
          }
          getRowId={(product) => product.id}
          emptyMessage={
            <EmptyTableState
              title="Không tìm thấy sản phẩm"
              description="Thử đổi từ khoá hoặc xoá bớt bộ lọc để xem lại dữ liệu."
            />
          }
          pagination={{
            page: currentPage,
            pageSize: PRODUCT_PAGE_SIZE,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </div>

      <ProductFormSheet
        open={sheetOpen}
        onOpenChange={(open) => {
          setSheetOpen(open)
          if (!open) setEditingProduct(null)
        }}
        product={editingProduct}
        categories={categories}
        onSave={handleSave}
      />
      <ConfirmDeleteDialog
        target={deleteTarget}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null)
        }}
        onConfirm={handleDelete}
      />
      <ConfirmProductStatusDialog
        target={statusTarget}
        onOpenChange={(open) => {
          if (!open) setStatusTarget(null)
        }}
        onConfirm={handleStatusChange}
      />
    </div>
  )
}

export default Component
