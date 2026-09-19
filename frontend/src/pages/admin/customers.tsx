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

import { getApiErrorMessage } from "@/api/errors"
import {
  createCustomer,
  deleteCustomer,
  getCustomers,
  updateCustomer,
  type CustomerRecord,
} from "@/api/customers"
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
import { TableActions } from "@/components/common/table-actions"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { useDebounce } from "@/hooks/use-debounce"
import {
  formatDate,
  normalize,
  type Customer,
  type CustomerFormData,
} from "@/lib/admin-management"
import { useAuthStore } from "@/stores/use-auth-store"
import { toastError, toastSuccess } from "@/utils/toast"
const mapCustomer = (customer: CustomerRecord): Customer => ({
  id: customer.id,
  customerCode: customer.customer_code,
  name: customer.name,
  email: customer.email ?? "",
  phone: customer.phone ?? "",
  orders: customer.total_orders,
  totalSpent: Number(customer.total_spent),
  status: customer.status === "INACTIVE" ? "inactive" : "active",
  joinedAt: customer.customer_since ?? customer.created_at,
})

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
  const [customers, setCustomers] = useState<Customer[]>([])
  const [{ search, status, sort, direction, page }, setQuery] = useQueryStates(
    customerQueryParsers,
    customerQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const [loading, setLoading] = useState(true)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const currentUser = useAuthStore((state) => state.user)
  const canManageCustomers = currentUser?.role_code === "ADMIN"

  useEffect(() => {
    let cancelled = false
    void getCustomers({ page: 1, size: 100 })
      .then((response) => {
        if (!cancelled) setCustomers(response.records.map(mapCustomer))
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

  const handleSave = async (data: CustomerFormData) => {
    try {
      const payload = {
        name: data.name,
        email: data.email || null,
        phone: data.phone || null,
        status:
          data.status === "active"
            ? ("ACTIVE" as const)
            : ("INACTIVE" as const),
      }
      const savedCustomer = editingCustomer
        ? await updateCustomer(editingCustomer.id, payload)
        : await createCustomer(payload)
      const mappedCustomer = mapCustomer(savedCustomer)

      setCustomers((current) =>
        editingCustomer
          ? current.map((customer) =>
              customer.id === editingCustomer.id ? mappedCustomer : customer
            )
          : [mappedCustomer, ...current]
      )
      toastSuccess(
        editingCustomer ? "Đã cập nhật khách hàng" : "Đã thêm khách hàng mới"
      )
      setSheetOpen(false)
      setEditingCustomer(null)
    } catch (error: unknown) {
      toastError(getApiErrorMessage(error))
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    try {
      await deleteCustomer(deleteTarget.id)
      setCustomers((current) =>
        current.filter((customer) => customer.id !== deleteTarget.id)
      )
      toastSuccess("Đã xoá khách hàng")
      setDeleteTarget(null)
    } catch (error: unknown) {
      toastError(getApiErrorMessage(error))
    }
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

  const columns: CommonTableColumn<Customer>[] = [
    {
      id: "customerCode",
      header: "Mã khách hàng",
      className: "min-w-28 whitespace-nowrap",
      cell: (customer) => (
        <span className="text-sm whitespace-nowrap">
          {customer.customerCode}
        </span>
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
      header: "Thao tác",
      className: "w-24 text-right",
      cell: (customer) => (
        <TableActions
          actions={[
            {
              key: "edit",
              label: "Chỉnh sửa",
              icon: <EditIcon />,
              disabled: !canManageCustomers,
              onClick: () => openCustomerSheet(customer),
            },
            {
              key: "delete",
              label: "Xoá",
              icon: <Trash2Icon />,
              disabled: !canManageCustomers,
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
      ),
    },
  ]

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
            {canManageCustomers && (
              <Button onClick={() => openCustomerSheet()} className="ml-auto">
                <PlusIcon />
                Thêm khách hàng
              </Button>
            )}
          </div>
        </div>
        <CommonTable
          data={filteredCustomers}
          columns={columns}
          loading={loading}
          itemLabel="khách hàng"
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
