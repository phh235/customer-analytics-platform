import { useState } from "react"

import type { PriorityCustomerRecord } from "@/api/analytics"
import { PotentialLevelBadge } from "@/components/admin/management/analytics-status-badge"
import { ProbabilityValue } from "@/components/admin/management/probability-value"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { UserAvatar } from "@/components/common/user-avatar"
import { usePriorityCustomers } from "@/hooks/use-analytics"

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
  const priorityQuery = usePriorityCustomers()
  const customers = priorityQuery.data ?? []

  const columns: CommonTableColumn<PriorityCustomerRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      className: "min-w-52",
      cell: (customer) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={customer.name} />
          <span>{customer.name}</span>
        </div>
      ),
    },
    {
      id: "potential_score",
      header: "Điểm tiềm năng",
      cell: (customer) => (
        <span>
          {customer.potential_score.toFixed(1)} / 100
          <PotentialLevelBadge
            className="ml-2"
            level={customer.potential_level}
          />
        </span>
      ),
    },
    {
      id: "purchase_probability",
      header: "Xác suất mua lại",
      cell: (customer) => (
        <ProbabilityValue value={customer.purchase_probability} />
      ),
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
        <h1 className="text-2xl font-semibold">Danh sách ưu tiên</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Khách hàng có điểm tiềm năng từ 80 hoặc xác suất mua lại vượt ngưỡng.
        </p>
      </header>

      <section aria-label="Danh sách khách hàng">
        <CommonTable
          data={customers}
          columns={columns}
          loading={priorityQuery.isPending}
          getRowId={(customer) => customer.customer_id}
          emptyMessage="Chưa có khách hàng trong danh sách ưu tiên."
          itemLabel="khách hàng"
          pagination={{ page, pageSize: PAGE_SIZE, onPageChange: setPage }}
        />
      </section>
    </div>
  )
}

export default Component
