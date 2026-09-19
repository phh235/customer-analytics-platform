import { useEffect, useState } from "react"
import { ArrowLeftRightIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import { getCustomers, type CustomerRecord } from "@/api/customers"
import { getOrders, type OrderRecord } from "@/api/orders"
import { getProducts, type ProductRecord } from "@/api/products"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatCurrency,
  formatDate,
  formatEnumLabel,
  ORDER_CHANNEL_LABELS,
  ORDER_STATUS_LABELS,
} from "@/lib/admin-management"

const PAGE_SIZE = 10

type CustomerLookup = Record<string, CustomerRecord>
type ProductLookup = Record<string, ProductRecord>

const toLookup = <T extends { id: string }>(records: T[]) =>
  Object.fromEntries(records.map((record) => [record.id, record])) as Record<
    string,
    T
  >

export const Component = () => {
  const [orders, setOrders] = useState<OrderRecord[]>([])
  const [customers, setCustomers] = useState<CustomerLookup>({})
  const [products, setProducts] = useState<ProductLookup>({})
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    void Promise.all([
      getOrders({ page, size: PAGE_SIZE }),
      getCustomers({ page: 1, size: 100 }),
      getProducts({ page: 1, size: 100 }),
    ])
      .then(([orderResponse, customerResponse, productResponse]) => {
        if (cancelled) return
        setOrders(orderResponse.records)
        setTotal(orderResponse.total)
        setPages(orderResponse.pages)
        setCustomers(toLookup(customerResponse.records))
        setProducts(toLookup(productResponse.records))
        setError(null)
      })
      .catch((requestError: unknown) => {
        if (!cancelled) setError(getApiErrorMessage(requestError))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [page])

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
        return (
          <div className="min-w-40">
            <div className="font-medium">
              {customer?.name ?? "Chưa xác định tên"}
            </div>
            <div className="text-xs text-muted-foreground">
              {customer?.customer_code ?? order.customer_id}
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
          <Badge variant="outline">
            {formatEnumLabel(order.status, ORDER_STATUS_LABELS)}
          </Badge>
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
        <div className="min-w-36 space-y-1 text-right">
          <div className="font-medium">
            {formatCurrency(Number(order.net_amount))}
          </div>
          <div className="text-xs text-muted-foreground">
            Tổng: {formatCurrency(Number(order.total_amount))}
          </div>
          {Number(order.refund_amount) > 0 ? (
            <div className="text-xs text-destructive">
              Hoàn: {formatCurrency(Number(order.refund_amount))}
            </div>
          ) : null}
        </div>
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4">
      <header>
        <div className="flex items-center gap-2">
          <ArrowLeftRightIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Giao dịch</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Theo dõi đơn hàng, khách hàng, sản phẩm và giá trị thực thu.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Danh sách đơn hàng</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <p className="py-8 text-center text-sm text-destructive">{error}</p>
          ) : (
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
                onPageChange: (nextPage) => {
                  setLoading(true)
                  setPage(nextPage)
                },
              }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Component
