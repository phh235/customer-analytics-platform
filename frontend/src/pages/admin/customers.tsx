import { useEffect, useMemo, useState } from "react"
import {
  FilterXIcon,
  EditIcon,
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
import { UserAvatar } from "@/components/common/user-avatar"
import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { CustomerFormSheet } from "@/components/admin/management/customer-form-sheet"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
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
import { useDebounce } from "@/hooks/use-debounce"
import {
  createId,
  formatDate,
  normalize,
  SAMPLE_CUSTOMERS,
  type Customer,
  type CustomerFormData,
} from "@/lib/admin-management"
import { toastSuccess } from "@/utils/toast"

const CUSTOMER_SORT_KEYS = ["name", "orders", "totalSpent", "joinedAt"] as const
const SORT_DIRECTIONS = ["asc", "desc"] as const
const CUSTOMER_STATUSES = ["all", "active", "inactive"] as const

type CustomerSortKey = (typeof CUSTOMER_SORT_KEYS)[number]
const CUSTOMER_PAGE_SIZE = 4

const customerQueryParsers = {
  search: parseAsString.withDefault(""),
  status: parseAsStringLiteral(CUSTOMER_STATUSES).withDefault("all"),
  sort: parseAsStringLiteral(CUSTOMER_SORT_KEYS).withDefault("name"),
  direction: parseAsStringLiteral(SORT_DIRECTIONS).withDefault("asc"),
  page: parseAsInteger.withDefault(1),
}
const customerQueryOptions = { urlKeys: { search: "q" } }

export const Component = () => {
  const [customers, setCustomers] = useState(SAMPLE_CUSTOMERS)
  const [{ search, status, sort, direction, page }, setQuery] = useQueryStates(
    customerQueryParsers,
    customerQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const [loading, setLoading] = useState(true)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 650)
    return () => window.clearTimeout(timer)
  }, [])

  const filteredCustomers = useMemo(() => {
    const query = normalize(debouncedSearch.trim())

    return customers
      .filter((customer) => {
        const matchesSearch =
          !query ||
          [customer.name, customer.email, customer.phone].some((value) =>
            normalize(value).includes(query)
          )
        const matchesStatus = status === "all" || customer.status === status

        return matchesSearch && matchesStatus
      })
      .sort((first, second) => {
        const sortMultiplier = direction === "asc" ? 1 : -1
        const comparison =
          sort === "orders" || sort === "totalSpent"
            ? first[sort] - second[sort]
            : sort === "joinedAt"
              ? first.joinedAt.localeCompare(second.joinedAt)
              : first.name.localeCompare(second.name, "vi", { numeric: true })

        return comparison * sortMultiplier
      })
  }, [customers, debouncedSearch, direction, sort, status])

  const openCustomerSheet = (customer: Customer | null = null) => {
    setEditingCustomer(customer)
    setSheetOpen(true)
  }

  const handleSave = (data: CustomerFormData) => {
    if (editingCustomer) {
      setCustomers((current) =>
        current.map((customer) =>
          customer.id === editingCustomer.id
            ? { ...customer, ...data }
            : customer
        )
      )
      toastSuccess("Đã cập nhật khách hàng")
    } else {
      setCustomers((current) => [
        {
          id: createId("KH"),
          ...data,
          orders: 0,
          totalSpent: 0,
          joinedAt: new Date().toISOString(),
        },
        ...current,
      ])
      toastSuccess("Đã thêm khách hàng mới")
    }

    setSheetOpen(false)
    setEditingCustomer(null)
  }

  const handleDelete = () => {
    if (!deleteTarget) return

    setCustomers((current) =>
      current.filter((customer) => customer.id !== deleteTarget.id)
    )
    toastSuccess("Đã xoá khách hàng")
    setDeleteTarget(null)
  }

  const toggleSort = (key: CustomerSortKey) => {
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
    void setQuery({ search: "", status: "all", page: 1 })
  }

  const currentPage = Math.max(page, 1)

  const columns: CommonTableColumn<Customer>[] = useMemo(
    () => [
      {
        id: "id",
        header: "Mã khách hàng",
        className: "min-w-28 whitespace-nowrap",
        cell: (customer) => (
          <span className="text-sm whitespace-nowrap">{customer.id}</span>
        ),
      },
      {
        id: "customer",
        header: (
          <SortButton
            label="Khách hàng"
            sortKey="name"
            activeKey={sort}
            direction={direction}
            onClick={() => toggleSort("name")}
          />
        ),
        className: "min-w-52 whitespace-nowrap",
        cell: (customer) => (
          <div className="flex min-w-48 items-center gap-3 whitespace-nowrap">
            <UserAvatar email={customer.email} />
            <span className="truncate">{customer.name}</span>
          </div>
        ),
        skeletonClassName: "h-8 w-4/5",
      },
      {
        id: "email",
        header: "Email",
        className: "min-w-64 whitespace-nowrap",
        cell: (customer) => (
          <span className="whitespace-nowrap">{customer.email}</span>
        ),
      },
      {
        id: "phone",
        header: "Số điện thoại",
        className: "min-w-36 whitespace-nowrap",
        cell: (customer) => (
          <span className="whitespace-nowrap">{customer.phone}</span>
        ),
      },
      {
        id: "status",
        header: "Trạng thái",
        className: "min-w-32 whitespace-nowrap",
        cell: (customer) => (
          <StatusBadge status={customer.status} entity="customer" />
        ),
      },
      {
        id: "joinedAt",
        header: (
          <SortButton
            label="Tham gia"
            sortKey="joinedAt"
            activeKey={sort}
            direction={direction}
            onClick={() => toggleSort("joinedAt")}
          />
        ),
        className: "min-w-28 whitespace-nowrap",
        cell: (customer) => (
          <span className="whitespace-nowrap">
            {formatDate(customer.joinedAt)}
          </span>
        ),
      },
      {
        id: "actions",
        header: <span className="sr-only">Thao tác</span>,
        className: "w-14 text-right",
        cell: (customer) => (
          <div className="flex justify-end">
            <AppDropdown
              aria-label={`Thao tác với ${customer.name}`}
              items={[
                {
                  key: "edit",
                  label: "Chỉnh sửa",
                  icon: <EditIcon />,
                  onClick: () => openCustomerSheet(customer),
                },
                {
                  key: "delete",
                  label: "Xoá",
                  icon: <Trash2Icon />,
                  variant: "destructive",
                  onClick: () =>
                    setDeleteTarget({
                      type: "customer",
                      id: customer.id,
                      name: customer.name,
                    }),
                },
              ]}
            />
          </div>
        ),
      },
    ],
    [direction, openCustomerSheet, sort, toggleSort]
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
                placeholder="Tìm tên, email, số điện thoại..."
                aria-label="Tìm kiếm khách hàng"
              />
            </InputGroup>
            <AppSelect
              options={[
                { value: "all", label: "Tất cả trạng thái" },
                { value: "active", label: "Đang hoạt động" },
                { value: "inactive", label: "Không hoạt động" },
              ]}
              value={status}
              onChange={(value) =>
                void setQuery({
                  status: (value ||
                    "all") as (typeof CUSTOMER_STATUSES)[number],
                  page: 1,
                })
              }
              className="w-full lg:w-48"
              aria-label="Lọc theo trạng thái"
            />
            {(search || status !== "all") && (
              <Button type="button" variant="ghost" onClick={resetFilters}>
                <FilterXIcon />
                Xoá lọc
              </Button>
            )}
            <Button onClick={() => openCustomerSheet()} className="ml-auto">
              <PlusIcon />
              Thêm khách hàng
            </Button>
          </div>
        </div>
        <CommonTable
          data={filteredCustomers}
          columns={columns}
          loading={loading}
          summary={
            loading
              ? "Đang tải khách hàng..."
              : `Hiển thị ${filteredCustomers.length === 0 ? "0" : `${(currentPage - 1) * CUSTOMER_PAGE_SIZE + 1}–${Math.min(currentPage * CUSTOMER_PAGE_SIZE, filteredCustomers.length)}`} / ${filteredCustomers.length} khách hàng`
          }
          getRowId={(customer) => customer.id}
          emptyMessage={
            <EmptyTableState
              title="Không tìm thấy khách hàng"
              description="Thử đổi từ khoá hoặc xoá bớt bộ lọc để xem lại dữ liệu."
            />
          }
          pagination={{
            page: currentPage,
            pageSize: CUSTOMER_PAGE_SIZE,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </div>

      <CustomerFormSheet
        open={sheetOpen}
        onOpenChange={(open) => {
          setSheetOpen(open)
          if (!open) setEditingCustomer(null)
        }}
        customer={editingCustomer}
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
