import { useCallback, useMemo, useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
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
  createCustomer,
  deleteCustomer,
  updateCustomer,
  uploadCustomerImage,
  type CustomerRecord,
} from "@/api/customers"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { AppSelect } from "@/components/common/app-select"
import { TableActions } from "@/components/common/table-actions"
import { UserAvatar } from "@/components/common/user-avatar"
import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"
import { CustomerFormSheet } from "@/components/admin/management/customer-form-sheet"
import { EmptyTableState } from "@/components/admin/management/empty-table-state"
import { SortButton } from "@/components/admin/management/sort-button"
import { StatusBadge } from "@/components/admin/management/status-badge"
import type { DeleteTarget } from "@/components/admin/management/types"
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { getApiErrorMessage } from "@/api/errors"
import { useDebounce } from "@/hooks/use-debounce"
import { customerQueryKeys, useCustomers } from "@/hooks/use-customers"
import { hasPermission } from "@/lib/authorization"
import type { Customer, CustomerFormData } from "@/lib/admin-management"
import { formatDate } from "@/lib/date"
import { useAuthStore } from "@/stores/use-auth-store"
import { toastError, toastSuccess } from "@/utils/toast"
const mapCustomer = (customer: CustomerRecord): Customer => ({
  id: customer.id,
  customerCode: customer.customer_code,
  name: customer.name,
  imageUrl: customer.image_url,
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
const CUSTOMER_PAGE_SIZE = 10

const customerQueryParsers = {
  search: parseAsString.withDefault(""),
  status: parseAsStringLiteral(CUSTOMER_STATUSES).withDefault("all"),
  sort: parseAsStringLiteral(CUSTOMER_SORT_KEYS).withDefault("name"),
  direction: parseAsStringLiteral(SORT_DIRECTIONS).withDefault("asc"),
  page: parseAsInteger.withDefault(1),
}
const customerQueryOptions = { urlKeys: { search: "q" } }

export const Component = () => {
  const queryClient = useQueryClient()
  const [{ search, status, sort, direction, page }, setQuery] = useQueryStates(
    customerQueryParsers,
    customerQueryOptions
  )
  const debouncedSearch = useDebounce(search, 300)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null)
  const currentUser = useAuthStore((state) => state.user)
  const canCreateCustomer = hasPermission(currentUser, "customers:create")
  const canUpdateCustomer = hasPermission(currentUser, "customers:update")
  const canDeleteCustomer = hasPermission(currentUser, "customers:delete")
  const canManageCustomers = canUpdateCustomer || canDeleteCustomer
  const currentPage = Math.max(page, 1)
  const customersQuery = useCustomers({
    page: currentPage,
    size: CUSTOMER_PAGE_SIZE,
    search: debouncedSearch.trim() || undefined,
  })
  const customers = useMemo(
    () => (customersQuery.data?.records ?? []).map(mapCustomer),
    [customersQuery.data?.records]
  )
  const loading = customersQuery.isPending

  const filteredCustomers = useMemo(() => {
    return customers
      .filter((customer) => {
        const matchesStatus = status === "all" || customer.status === status
        return matchesStatus
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
  }, [customers, direction, sort, status])

  const openCustomerSheet = useCallback((customer: Customer | null = null) => {
    setEditingCustomer(customer)
    setSheetOpen(true)
  }, [])

  const saveCustomerMutation = useMutation({
    mutationFn: async ({
      customer,
      data,
    }: {
      customer: Customer | null
      data: CustomerFormData
    }) => {
      const payload = {
        name: data.name,
        email: data.email || null,
        phone: data.phone || null,
        status:
          data.status === "active"
            ? ("ACTIVE" as const)
            : ("INACTIVE" as const),
      }
      const savedCustomer = customer
        ? await updateCustomer(customer.id, payload)
        : await createCustomer(payload)
      return data.image
        ? await uploadCustomerImage(savedCustomer.id, data.image)
        : savedCustomer
    },
    onSuccess: async (_, variables) => {
      toastSuccess(
        variables.customer ? "Đã cập nhật khách hàng" : "Đã thêm khách hàng mới"
      )
      await queryClient.invalidateQueries({ queryKey: customerQueryKeys.all })
    },
    onError: (error) => {
      toastError(getApiErrorMessage(error))
    },
  })

  const deleteCustomerMutation = useMutation({
    mutationFn: (customerId: string) => deleteCustomer(customerId),
    onSuccess: async () => {
      toastSuccess("Đã xoá khách hàng")
      setDeleteTarget(null)
      await queryClient.invalidateQueries({ queryKey: customerQueryKeys.all })
    },
    onError: (error) => toastError(getApiErrorMessage(error)),
  })

  const handleSave = (data: CustomerFormData) =>
    saveCustomerMutation.mutateAsync({ customer: editingCustomer, data })

  const handleDelete = () => {
    if (deleteTarget && !deleteCustomerMutation.isPending) {
      deleteCustomerMutation.mutate(deleteTarget.id)
    }
  }

  const toggleSort = useCallback(
    (key: CustomerSortKey) => {
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
    void setQuery({ search: "", status: "all", page: 1 })
  }

  const columns: CommonTableColumn<Customer>[] = useMemo(
    () => [
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
            {customer.imageUrl ? (
              <img
                src={customer.imageUrl}
                alt={customer.name}
                className="size-8 shrink-0 rounded-full object-cover"
                loading="lazy"
              />
            ) : (
              <UserAvatar email={customer.email} name={customer.name} />
            )}
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
        cell: (customer) =>
          canManageCustomers ? (
            <TableActions
              actions={[
                {
                  key: "edit",
                  label: "Chỉnh sửa",
                  icon: <EditIcon />,
                  disabled: !canUpdateCustomer,
                  onClick: () => openCustomerSheet(customer),
                },
                {
                  key: "delete",
                  label: "Xoá",
                  icon: <Trash2Icon />,
                  variant: "destructive",
                  disabled: !canDeleteCustomer,
                  onClick: () =>
                    setDeleteTarget({
                      type: "customer",
                      id: customer.id,
                      name: customer.name,
                    }),
                },
              ]}
            />
          ) : null,
      },
    ],
    [
      canDeleteCustomer,
      canManageCustomers,
      canUpdateCustomer,
      direction,
      openCustomerSheet,
      sort,
      toggleSort,
    ]
  )

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Khách hàng</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Quản lý hồ sơ, thông tin liên hệ và trạng thái khách hàng.
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
                status: (value || "all") as (typeof CUSTOMER_STATUSES)[number],
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
          {canCreateCustomer && (
            <Button onClick={() => openCustomerSheet()} className="ml-auto">
              <PlusIcon />
              Thêm khách hàng
            </Button>
          )}
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
              description="Thử đổi từ khóa hoặc xoá bớt bộ lọc để xem lại dữ liệu."
            />
          }
          pagination={{
            page: customersQuery.data?.current ?? currentPage,
            pageSize: CUSTOMER_PAGE_SIZE,
            total: customersQuery.data?.total ?? 0,
            totalPages: customersQuery.data?.pages ?? 1,
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
        isLoading={deleteCustomerMutation.isPending}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null)
        }}
        onConfirm={handleDelete}
      />
    </div>
  )
}

export default Component
