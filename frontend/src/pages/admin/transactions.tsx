import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  useQueryStates,
} from "nuqs"

import type { CustomerRecord } from "@/api/customers"
import type { OrderRecord } from "@/api/orders"
import type { ProductRecord } from "@/api/products"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { TableSearch } from "@/components/common/table-search"
import { UserAvatar } from "@/components/common/user-avatar"
import { OrderStatusBadge } from "@/components/admin/management/status-badge"
import { useCustomers } from "@/hooks/use-customers"
import { useDebounce } from "@/hooks/use-debounce"
import { useOrders } from "@/hooks/use-orders"
import { useProducts } from "@/hooks/use-products"
import { ORDER_CHANNEL_LABELS } from "@/lib/admin-management"
import { formatDate } from "@/lib/date"
import { formatCurrency, formatEnumLabel } from "@/lib/format"

const PAGE_SIZE = 10

type CustomerLookup = Record<string, CustomerRecord>
type ProductLookup = Record<string, ProductRecord>

const toLookup = <T extends { id: string }>(records: T[]) =>
  Object.fromEntries(records.map((record) => [record.id, record])) as Record<
    string,
    T
  >

export const Component = () => {
  const [{ page, search }, setQuery] = useQueryStates(
    {
      page: parseAsInteger.withDefault(1),
      search: parseAsString.withDefault(""),
    },
    { urlKeys: { search: "q" } }
  )
  const debouncedSearch = useDebounce(search, 300)
  const ordersQuery = useOrders({
    page,
    size: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const customersQuery = useCustomers({ page: 1, size: 100 })
  const productsQuery = useProducts({ page: 1, size: 100 })
  const orders = ordersQuery.data?.records ?? []
  const total = ordersQuery.data?.total ?? 0
  const pages = ordersQuery.data?.pages ?? 1
  const customers: CustomerLookup = toLookup(customersQuery.data?.records ?? [])
  const products: ProductLookup = toLookup(productsQuery.data?.records ?? [])
  const loading =
    ordersQuery.isPending || customersQuery.isPending || productsQuery.isPending

  const columns: CommonTableColumn<OrderRecord>[] = [
    {
      id: "order",
      header: "Đơn hàng",
      cell: (order) => (
        <div className="min-w-28">
          <div className="font-medium">{order.order_number}</div>
          <div className="text-xs text-muted-foreground">
            {formatDate(order.order_date)}
          </div>
        </div>
      ),
    },
    {
      id: "customer",
      header: "Khách hàng",
      cell: (order) => {
        const customer = customers[order.customer_id]
        const customerName = customer?.name ?? "Chưa xác định tên"
        return (
          <div className="flex min-w-48 items-center gap-3">
            {customer?.image_url ? (
              <img
                src={customer.image_url}
                alt={customerName}
                className="size-8 shrink-0 rounded-full object-cover"
                loading="lazy"
              />
            ) : (
              <UserAvatar
                email={customer?.email ?? undefined}
                name={customerName}
              />
            )}
            <div className="min-w-0">
              <div className="truncate font-medium">{customerName}</div>
              <div className="text-xs text-muted-foreground">
                {customer?.customer_code ?? order.customer_id}
              </div>
            </div>
          </div>
        )
      },
    },
    {
      id: "items",
      header: "Sản phẩm",
      cell: (order) => (
        <div className="min-w-48 space-y-1">
          {order.items.length > 0 ? (
            order.items.map((item) => {
              const product = products[item.product_id]
              return (
                <div key={item.id} className="text-sm">
                  <span>{product?.name ?? item.product_id}</span>
                  <span className="ml-1 text-muted-foreground">
                    × {item.quantity}
                  </span>
                </div>
              )
            })
          ) : (
            <span className="text-sm text-muted-foreground">
              Không có sản phẩm
            </span>
          )}
        </div>
      ),
    },
    {
      id: "status",
      header: "Trạng thái / kênh",
      cell: (order) => (
        <div className="min-w-32 space-y-1">
          <OrderStatusBadge status={order.status} />
          <div className="text-xs text-muted-foreground">
            {formatEnumLabel(order.channel, ORDER_CHANNEL_LABELS)}
          </div>
        </div>
      ),
    },
    {
      id: "amounts",
      header: "Giá trị",
      className: "text-right",
      cell: (order) => (
        <span className="min-w-36 text-right font-medium whitespace-nowrap">
          {formatCurrency(Number(order.net_amount))}
        </span>
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Giao dịch</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Theo dõi đơn hàng, khách hàng, sản phẩm và giá trị thực thu.
        </p>
      </header>

      <TableSearch
        value={search}
        onChange={(value) => {
          void setQuery(
            { search: value, page: 1 },
            { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
          )
        }}
        placeholder="Tìm mã đơn, khách hàng hoặc sản phẩm..."
        ariaLabel="Tìm kiếm giao dịch"
      />

      <section aria-label="Danh sách đơn hàng">
        <CommonTable
          data={orders}
          columns={columns}
          loading={loading}
          getRowId={(order) => order.id}
          summary={`Đang hiển thị ${orders.length} trên ${total} đơn hàng`}
          pagination={{
            page,
            pageSize: PAGE_SIZE,
            total,
            totalPages: pages,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </section>
    </div>
  )
}

export default Component
