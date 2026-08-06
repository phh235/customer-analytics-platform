import { useEffect, useMemo, useState } from "react"
import {
  Edit,
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
import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { ProductFormDialog } from "@/components/admin/management/product-form-dialog"
import { SortButton } from "@/components/admin/management/sort-button"
import { StatusBadge } from "@/components/admin/management/status-badge"
import type { DeleteTarget } from "@/components/admin/management/types"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)

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

  const openProductDialog = (product: Product | null = null) => {
    setEditingProduct(product)
    setDialogOpen(true)
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

    setDialogOpen(false)
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
        className: "w-[28%]",
        cell: (product) => (
          <div className="flex min-w-52 flex-col gap-1">
            <span className="font-medium">{product.name}</span>
            <span className="text-xs text-muted-foreground">
              {product.sku} · {product.id}
            </span>
          </div>
        ),
        skeletonClassName: "h-10 w-4/5",
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
        cell: (product) => <span>{product.category}</span>,
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
        cell: (product) => (
          <span className="font-medium">{formatCurrency(product.price)}</span>
        ),
      },
      {
        id: "status",
        header: "Trạng thái",
        cell: (product) => (
          <StatusBadge status={product.status} entity="product" />
        ),
      },
      {
        id: "updatedAt",
        header: "Cập nhật",
        cell: (product) => formatDate(product.updatedAt),
      },
      {
        id: "actions",
        header: "Thao tác",
        className: "w-28 text-right",
        cell: (product) => (
          <div className="flex justify-end gap-1">
            <Button
              type="button"
              variant="outline"
              size="icon"
              aria-label={`Chỉnh sửa ${product.name}`}
              onClick={() => openProductDialog(product)}
            >
              <Edit />
            </Button>
            <Button
              type="button"
              variant="destructive"
              size="icon"
              aria-label={`Xoá ${product.name}`}
              onClick={() =>
                setDeleteTarget({
                  type: "product",
                  id: product.id,
                  name: product.name,
                })
              }
            >
              <Trash2Icon />
            </Button>
          </div>
        ),
      },
    ],
    [direction, openProductDialog, sort, toggleSort]
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
            <Select
              value={category}
              onValueChange={(value) =>
                void setQuery({ category: value ?? "all", page: 1 })
              }
            >
              <SelectTrigger className="w-full lg:w-52">
                <SelectValue>
                  {category === "all" ? "Tất cả danh mục" : category}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">Tất cả danh mục</SelectItem>
                  {categories.map((item) => (
                    <SelectItem key={item} value={item}>
                      {item}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
            <Select
              value={status}
              onValueChange={(value) =>
                void setQuery({
                  status: (value ?? "all") as (typeof PRODUCT_STATUSES)[number],
                  page: 1,
                })
              }
            >
              <SelectTrigger className="w-full lg:w-44">
                <SelectValue>
                  {status === "all"
                    ? "Tất cả trạng thái"
                    : status === "active"
                      ? "Đang bán"
                      : "Tạm ẩn"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="all">Tất cả trạng thái</SelectItem>
                  <SelectItem value="active">Đang bán</SelectItem>
                  <SelectItem value="inactive">Tạm ẩn</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
            {(search || category !== "all" || status !== "all") && (
              <Button type="button" variant="ghost" onClick={resetFilters}>
                <FilterXIcon />
                Xoá lọc
              </Button>
            )}
            <Button onClick={() => openProductDialog()} className="ml-auto">
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

      <ProductFormDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open)
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
    </div>
  )
}

export default Component
