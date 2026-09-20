import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { SegmentBadge } from "@/components/admin/management/analytics-status-badge"
import { PotentialScoreValue } from "@/components/admin/management/potential-score-value"
import { ProbabilityValue } from "@/components/admin/management/probability-value"
import { UserAvatar } from "@/components/common/user-avatar"
import { Badge } from "@/components/ui/badge"
import {
  CardAction,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { DASHBOARD_SEGMENTS, formatDashboardMoney } from "@/lib/dashboard"
import type {
  DashboardOption,
  DashboardOverview,
  DashboardPriorityCustomer,
} from "@/types/dashboard"

const getColumns = (
  employeeNames: Record<string, string>,
  highThreshold: number
): CommonTableColumn<DashboardPriorityCustomer>[] => [
  {
    id: "customer",
    header: "Khách hàng",
    className: "min-w-52",
    cell: (customer) => (
      <div className="flex items-center gap-3">
        <UserAvatar name={customer.name} />
        <div className="min-w-0">
          <p className="truncate font-medium">{customer.name}</p>
          {customer.customer_code ? (
            <p className="text-xs text-muted-foreground">
              {customer.customer_code}
            </p>
          ) : null}
        </div>
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
      <PotentialScoreValue
        value={customer.potential_score}
        highThreshold={highThreshold}
      />
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
    cell: (customer) =>
      customer.employee_id
        ? (employeeNames[customer.employee_id] ?? customer.employee_id)
        : "Chưa phân công",
  },
]

export function PriorityCustomers({
  data,
  employees,
}: {
  data: DashboardOverview
  employees: DashboardOption[]
}) {
  const employeeNames = Object.fromEntries(
    employees.map((employee) => [employee.id, employee.name])
  )
  const columns = getColumns(employeeNames, data.potential.thresholds.high)

  return (
    <section aria-labelledby="priority-title" className="min-w-0">
      <SquircleCard>
        <CardHeader>
          <CardTitle id="priority-title">Khách hàng tiềm năng cao</CardTitle>
          <CardDescription>
            10 khách hàng có điểm cao nhất · Ưu tiên chăm sóc theo nhu cầu thực
            tế
          </CardDescription>
          <CardAction>
            <Badge variant="secondary">
              {data.priority_total} khách hàng đạt từ{" "}
              {data.potential.thresholds.high} điểm
            </Badge>
          </CardAction>
        </CardHeader>
        <SquircleCardBody className="py-0">
          <CommonTable
            data={data.priority_customers}
            columns={columns}
            itemLabel="khách hàng trong top 10"
            getRowId={(customer) => customer.id}
            emptyMessage="Chưa có khách hàng đạt ngưỡng tiềm năng cao."
            variant="embedded"
          />
        </SquircleCardBody>
      </SquircleCard>
    </section>
  )
}
