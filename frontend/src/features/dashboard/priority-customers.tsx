import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { SegmentBadge } from "@/components/admin/management/analytics-status-badge"
import { ProbabilityValue } from "@/components/admin/management/probability-value"
import { UserAvatar } from "@/components/common/user-avatar"
import { Badge } from "@/components/ui/badge"
import { DASHBOARD_SEGMENTS, formatDashboardMoney } from "@/lib/dashboard"
import type {
  DashboardOverview,
  DashboardPriorityCustomer,
} from "@/types/dashboard"

const columns: CommonTableColumn<DashboardPriorityCustomer>[] = [
  { id: "code", header: "Mã khách hàng", cell: (customer) => customer.code },
  {
    id: "customer",
    header: "Khách hàng",
    className: "min-w-52",
    cell: (customer) => (
      <div className="flex items-center gap-3">
        <UserAvatar email={customer.email} name={customer.name} />
        <span>{customer.name}</span>
      </div>
    ),
  },
  {
    id: "segment",
    header: "Phân khúc",
    cell: (customer) => (
      <SegmentBadge
        segment={customer.segment}
        label={DASHBOARD_SEGMENTS[customer.segment]}
      />
    ),
  },
  {
    id: "potential",
    header: "Điểm tiềm năng",
    cell: (customer) => (
      <span className="font-medium tabular-nums">
        {customer.potential_score}
        <span className="font-normal text-muted-foreground"> / 100</span>
      </span>
    ),
  },
  {
    id: "probability",
    header: "Xác suất mua (ML)",
    cell: (customer) => (
      <ProbabilityValue value={customer.purchase_probability} decimals={0} />
    ),
  },
  {
    id: "revenue",
    header: "Giá trị mua trong kỳ",
    className: "text-right",
    cell: (customer) => formatDashboardMoney(customer.revenue),
  },
  {
    id: "employee",
    header: "Nhân viên phụ trách",
    cell: (customer) => customer.employee_name,
  },
]

export function PriorityCustomers({ data }: { data: DashboardOverview }) {
  return (
    <section
      aria-labelledby="priority-title"
      className="-mx-3 flex min-w-0 flex-col gap-4"
    >
      <div className="flex flex-wrap items-center justify-between gap-2 px-3">
        <div>
          <h2 id="priority-title" className="text-base font-medium">
            Khách hàng tiềm năng cao
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            10 khách hàng có điểm cao nhất · Ưu tiên chăm sóc theo nhu cầu thực
            tế
          </p>
        </div>
        <Badge variant="secondary">
          {data.priority_total} khách hàng đạt từ{" "}
          {data.potential.thresholds.high} điểm
        </Badge>
      </div>
      <CommonTable
        data={data.priority_customers}
        columns={columns}
        itemLabel="khách hàng trong top 10"
        getRowId={(customer) => customer.id}
        emptyMessage="Chưa có khách hàng đạt ngưỡng tiềm năng cao."
      />
    </section>
  )
}
