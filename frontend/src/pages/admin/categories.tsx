import { useEffect, useMemo, useState } from "react"
import { EditIcon, PlusIcon, SearchIcon, Trash2Icon } from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  parseAsStringLiteral,
  useQueryStates,
} from "nuqs"

import { CategoryFormSheet } from "@/components/admin/management/category-form-sheet"
import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { SortButton } from "@/components/admin/management/sort-button"
import type { DeleteTarget } from "@/components/admin/management/types"
import { AppDropdown } from "@/components/common/app-dropdown"
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
import {
  createId,
  formatDate,
  normalize,
  PRODUCT_CATEGORIES,
  SAMPLE_PRODUCTS,
  type Category,
  type CategoryFormData,
} from "@/lib/admin-management"
import { toastSuccess } from "@/utils/toast"

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

const createInitialCategories = (): Category[] =>
  PRODUCT_CATEGORIES.map((name, index) => ({
    id: `DM-${String(index + 1).padStart(4, "0")}`,
    code: `DM-${String(index + 1).padStart(4, "0")}`,
    name,
    productCount: SAMPLE_PRODUCTS.filter((product) => product.category === name)
      .length,
    updatedAt: "2026-07-28",
  }))

export const Component = () => {
  const [categories, setCategories] = useState(createInitialCategories)
  const [{ search, sort, direction, page }, setQuery] = useQueryStates(
    categoryQueryParsers,
    categoryQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const [loading, setLoading] = useState(true)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 650)
    return () => window.clearTimeout(timer)
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

  const openCategorySheet = (category: Category | null = null) => {
    setEditingCategory(category)
    setSheetOpen(true)
  }

  const handleSave = (data: CategoryFormData) => {
    if (editingCategory) {
      setCategories((current) =>
        current.map((category) =>
          category.id === editingCategory.id
            ? {
                ...category,
                ...data,
                updatedAt: new Date().toISOString(),
              }
            : category
        )
      )
      toastSuccess("Đã cập nhật danh mục")
    } else {
      setCategories((current) => [
        {
          id: createId("DM"),
          ...data,
          productCount: 0,
          updatedAt: new Date().toISOString(),
        },
        ...current,
      ])
      toastSuccess("Đã thêm danh mục mới")
    }

    setSheetOpen(false)
    setEditingCategory(null)
  }

  const handleDelete = () => {
    if (!deleteTarget) return

    setCategories((current) =>
      current.filter((category) => category.id !== deleteTarget.id)
    )
    toastSuccess("Đã xoá danh mục")
    setDeleteTarget(null)
  }

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
      {
        id: "actions",
        header: <span className="sr-only">Thao tác</span>,
        className: "w-14 text-right whitespace-nowrap",
        cell: (category) => (
          <div className="flex justify-end">
            <AppDropdown
              aria-label={`Thao tác với ${category.name}`}
              items={[
                {
                  key: "edit",
                  label: "Chỉnh sửa",
                  icon: <EditIcon />,
                  onClick: () => openCategorySheet(category),
                },
                {
                  key: "delete",
                  label: "Xoá",
                  icon: <Trash2Icon />,
                  variant: "destructive",
                  onClick: () =>
                    setDeleteTarget({
                      type: "category",
                      id: category.id,
                      name: category.name,
                    }),
                },
              ]}
            />
          </div>
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
            <Button onClick={() => openCategorySheet()} className="ml-auto">
              <PlusIcon />
              Thêm danh mục
            </Button>
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
              description="Thử đổi từ khoá hoặc xoá bộ lọc để xem lại dữ liệu."
            />
          }
          pagination={{
            page: currentPage,
            pageSize: CATEGORY_PAGE_SIZE,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </div>

      <CategoryFormSheet
        open={sheetOpen}
        onOpenChange={(open) => {
          setSheetOpen(open)
          if (!open) setEditingCategory(null)
        }}
        category={editingCategory}
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
