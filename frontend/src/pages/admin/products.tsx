import { useCallback, useMemo, useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
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
  createProduct,
  deleteProduct,
  updateProduct,
  uploadProductImage,
  type ProductRecord,
} from "@/api/products"
import { getApiErrorMessage } from "@/api/errors"
import { useAuthStore } from "@/stores/use-auth-store"
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
import { TableActions } from "@/components/common/table-actions"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { Switch } from "@/components/ui/switch"
import { useDebounce } from "@/hooks/use-debounce"
import { productQueryKeys, useProducts } from "@/hooks/use-products"
import { hasPermission } from "@/lib/authorization"
import {
  type Product,
  type ProductFormData,
  type ProductStatus,
} from "@/lib/admin-management"
import { formatDate } from "@/lib/date"
import { formatCurrency, normalizeText } from "@/lib/format"
import { toastError, toastSuccess } from "@/utils/toast"
const mapProduct = (product: ProductRecord): Product => ({
  id: product.id,
  productCode: product.product_code,
  name: product.name,
  sku: product.sku ?? "",
  category: product.category,
  imageUrl: product.image_url,
  price: Number(product.price),
  status: product.status === "ACTIVE" ? "active" : "inactive",
  updatedAt: product.updated_at,
})

const PRODUCT_SORT_KEYS = ["name", "category", "price"] as const
const SORT_DIRECTIONS = ["asc", "desc"] as const
const PRODUCT_STATUSES = ["all", "active", "inactive"] as const

type ProductSortKey = (typeof PRODUCT_SORT_KEYS)[number]
const PRODUCT_PAGE_SIZE = 10

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
  const queryClient = useQueryClient()
  const [{ search, category, status, sort, direction, page }, setQuery] =
    useQueryStates(productQueryParsers, productQueryOptions)
  const debouncedSearch = useDebounce(search, 300)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const [statusTarget, setStatusTarget] = useState<{
    id: string
    name: string
    nextStatus: ProductStatus
  } | null>(null)
  const currentUser = useAuthStore((state) => state.user)
  const canCreateProduct = hasPermission(currentUser, "products:create")
  const canUpdateProduct = hasPermission(currentUser, "products:update")
  const canDeleteProduct = hasPermission(currentUser, "products:delete")
  const productsQuery = useProducts({ page: 1, size: 100 })
  const products = useMemo(
    () => (productsQuery.data?.records ?? []).map(mapProduct),
    [productsQuery.data?.records]
  )
  const loading = productsQuery.isPending

  const categories = useMemo(
    () =>
      Array.from(new Set(products.map((product) => product.category))).sort(
        (first, second) => first.localeCompare(second, "vi")
      ),
    [products]
  )

  const filteredProducts = useMemo(() => {
    const query = normalizeText(debouncedSearch.trim())

    return products
      .filter((product) => {
        const matchesSearch =
          !query ||
          [product.name, product.sku, product.category].some((value) =>
            normalizeText(value).includes(query)
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

  const openProductSheet = useCallback((product: Product | null = null) => {
    setEditingProduct(product)
    setSheetOpen(true)
  }, [])

  const saveProductMutation = useMutation({
    mutationFn: async ({
      product,
      data,
    }: {
      product: Product | null
      data: ProductFormData
    }) => {
      const payload = {
        name: data.name,
        sku: data.sku,
        category: data.category,
        price: data.price,
        status:
          data.status === "active"
            ? ("ACTIVE" as const)
            : ("INACTIVE" as const),
      }
      const savedProduct = product
        ? await updateProduct(product.id, payload)
        : await createProduct(payload)
      return data.image
        ? await uploadProductImage(savedProduct.id, data.image)
        : savedProduct
    },
    onSuccess: async (_, variables) => {
      toastSuccess(
        variables.product ? "Đã cập nhật sản phẩm" : "Đã thêm sản phẩm mới"
      )
      await queryClient.invalidateQueries({ queryKey: productQueryKeys.all })
    },
    onError: (error) => {
      toastError(getApiErrorMessage(error))
    },
  })

  const deleteProductMutation = useMutation({
    mutationFn: (productId: string) => deleteProduct(productId),
    onSuccess: async () => {
      toastSuccess("Đã xoá sản phẩm")
      setDeleteTarget(null)
      await queryClient.invalidateQueries({ queryKey: productQueryKeys.all })
    },
    onError: (error) => toastError(getApiErrorMessage(error)),
  })

  const updateStatusMutation = useMutation({
    mutationFn: (target: NonNullable<typeof statusTarget>) =>
      updateProduct(target.id, {
        status: target.nextStatus === "active" ? "ACTIVE" : "INACTIVE",
      }),
    onSuccess: async (_, target) => {
      toastSuccess(
        target.nextStatus === "active"
          ? "Đã hiển thị sản phẩm"
          : "Đã ẩn sản phẩm"
      )
      setStatusTarget(null)
      await queryClient.invalidateQueries({ queryKey: productQueryKeys.all })
    },
    onError: (error) => toastError(getApiErrorMessage(error)),
  })

  const handleSave = (data: ProductFormData) =>
    saveProductMutation.mutateAsync({ product: editingProduct, data })

  const handleDelete = () => {
    if (deleteTarget && !deleteProductMutation.isPending) {
      deleteProductMutation.mutate(deleteTarget.id)
    }
  }

  const handleStatusChange = () => {
    if (statusTarget && !updateStatusMutation.isPending) {
      updateStatusMutation.mutate(statusTarget)
    }
  }

  const toggleSort = useCallback(
    (key: ProductSortKey) => {
      void setQuery({
        sort: key,
        direction: sort === key && direction === "asc" ? "desc" : "asc",
        page: 1,
      })
    },
    [direction, setQuery, sort]
  )

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
        id: "image",
        header: "Ảnh",
        className: "w-16",
        cell: (product) =>
          product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className="size-10 rounded-md object-cover"
              loading="lazy"
            />
          ) : (
            <div
              aria-label={`Chưa có ảnh ${product.name}`}
              className="flex size-10 items-center justify-center rounded-md bg-muted text-xs font-semibold text-muted-foreground"
            >
              {product.name.slice(0, 1).toUpperCase()}
            </div>
          ),
      },
      {
        id: "productCode",
        header: "Mã sản phẩm",
        className: "min-w-28 whitespace-nowrap",
        cell: (product) => (
          <span className="text-sm whitespace-nowrap">
            {product.productCode}
          </span>
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
          <span className="text-sm whitespace-nowrap">
            {product.sku || "-"}
          </span>
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
                disabled={!canUpdateProduct}
                onCheckedChange={(checked) =>
                  setStatusTarget({
                    id: product.id,
                    name: product.name,
                    nextStatus: checked ? "active" : "inactive",
                  })
                }
                aria-label={isActive ? "Ẩn" : "Hiển thị"}
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
        header: "Thao tác",
        className: "w-24 text-right",
        cell: (product) => (
          <TableActions
            actions={[
              {
                key: "edit",
                label: "Chỉnh sửa",
                icon: <EditIcon />,
                disabled: !canUpdateProduct,
                onClick: () => openProductSheet(product),
              },
              {
                key: "delete",
                label: "Xoá",
                icon: <Trash2Icon />,
                disabled: !canDeleteProduct,
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
        ),
      },
    ],
    [
      canDeleteProduct,
      canUpdateProduct,
      direction,
      openProductSheet,
      sort,
      toggleSort,
    ]
  )

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Sản phẩm</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Quản lý sản phẩm, danh mục, giá bán và trạng thái hiển thị.
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
          {canCreateProduct && (
            <Button onClick={() => openProductSheet()} className="ml-auto">
              <PlusIcon />
              Thêm sản phẩm
            </Button>
          )}
        </div>
        <CommonTable
          data={filteredProducts}
          columns={columns}
          loading={loading}
          itemLabel="sản phẩm"
          getRowId={(product) => product.id}
          emptyMessage={
            <EmptyTableState
              title="Không tìm thấy sản phẩm"
              description="Thử đổi từ khóa hoặc xoá bớt bộ lọc để xem lại dữ liệu."
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
        isLoading={deleteProductMutation.isPending}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null)
        }}
        onConfirm={handleDelete}
      />
      <ConfirmProductStatusDialog
        target={statusTarget}
        isLoading={updateStatusMutation.isPending}
        onOpenChange={(open) => {
          if (!open) setStatusTarget(null)
        }}
        onConfirm={handleStatusChange}
      />
    </div>
  )
}

export default Component
