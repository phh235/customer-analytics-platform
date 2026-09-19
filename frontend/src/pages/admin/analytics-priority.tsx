import { useEffect, useState } from "react"
import { ListChecksIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import { getPriorityList, type PriorityCustomerRecord } from "@/api/analytics"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import { formatEnumLabel, SCORE_LEVEL_LABELS } from "@/lib/admin-management"

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
  const [customers, setCustomers] = useState<PriorityCustomerRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getPriorityList()
      .then((response) => {
        if (cancelled) return
        setCustomers(response)
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
  }, [])

  const columns: CommonTableColumn<PriorityCustomerRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      cell: (customer) => <span>{customer.name}</span>,
    },
    {
      id: "potential_score",
      header: "Điểm tiềm năng",
      cell: (customer) => (
        <span>
          {customer.potential_score.toFixed(1)} / 100
          <Badge
            className="ml-2"
            variant={
              customer.potential_level === "HIGH" ? "success" : "secondary"
            }
          >
            {formatEnumLabel(customer.potential_level, SCORE_LEVEL_LABELS)}
          </Badge>
        </span>
      ),
    },
    {
      id: "purchase_probability",
      header: "Xác suất mua lại",
      cell: (customer) =>
        `${(customer.purchase_probability * 100).toFixed(1)}%`,
    },
    {
      id: "preferred_product_category",
      header: "Danh mục ưa thích",
      cell: (customer) => customer.preferred_product_category ?? "—",
    },
    {
      id: "purchase_cycle_days",
      header: "Chu kỳ mua",
      cell: (customer) =>
        customer.purchase_cycle_days === null
          ? "—"
          : `${customer.purchase_cycle_days.toFixed(1)} ngày`,
    },
    {
      id: "recommendation",
      header: "Khuyến nghị",
      cell: (customer) => (
        <span
          title={customer.recommendation}
          className="block max-w-sm truncate text-muted-foreground"
        >
          {customer.recommendation}
        </span>
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <div className="flex items-center gap-2">
          <ListChecksIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Danh sách ưu tiên</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Khách hàng có điểm tiềm năng từ 80 hoặc xác suất mua lại vượt ngưỡng.
        </p>
      </header>

      <section aria-label="Danh sách khách hàng">
        {error ? (
          <p className="py-8 text-center text-sm text-destructive">{error}</p>
        ) : (
          <CommonTable
            data={customers}
            columns={columns}
            loading={loading}
            getRowId={(customer) => customer.customer_id}
            emptyMessage="Chưa có khách hàng trong danh sách ưu tiên."
            itemLabel="khách hàng"
            pagination={{
              page,
              pageSize: PAGE_SIZE,
              onPageChange: setPage,
            }}
          />
        )}
      </section>
    </div>
  )
}

export default Component
