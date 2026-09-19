import { useEffect, useState } from "react"
import { ArrowLeftRightIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import { getOrders, type OrderRecord } from "@/api/orders"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatCurrency,
  formatEnumLabel,
  ORDER_CHANNEL_LABELS,
  ORDER_STATUS_LABELS,
} from "@/lib/admin-management"

const PAGE_SIZE = 10

export const Component = () => {
  const [orders, setOrders] = useState<OrderRecord[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    void getOrders({ page, size: PAGE_SIZE })
      .then((response) => {
        if (cancelled) return
        setOrders(response.records)
        setTotal(response.total)
        setPages(response.pages)
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
      id: "order_number",
      header: "Mã đơn",
      cell: (order) => <span className="font-medium">{order.order_number}</span>,
    },
    {
      id: "channel",
      header: "Kênh",
      cell: (order) =>
        formatEnumLabel(order.channel, ORDER_CHANNEL_LABELS),
    },
    {
      id: "status",
      header: "Trạng thái",
      cell: (order) => (
        <Badge variant="outline">
          {formatEnumLabel(order.status, ORDER_STATUS_LABELS)}
        </Badge>
      ),
    },
    {
      id: "total_amount",
      header: "Giá trị",
      className: "text-right",
      cell: (order) => (
        <span className="font-medium">
          {formatCurrency(Number(order.total_amount))}
        </span>
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
          Theo dõi các đơn hàng đã ghi nhận trong hệ thống.
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
                onPageChange: setPage,
              }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Component
