import {
  CalendarDaysIcon,
  DownloadIcon,
  FilterXIcon,
  RefreshCwIcon,
} from "lucide-react"
import { AppSelect } from "@/components/common/app-select"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty"
import { Input } from "@/components/ui/input"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Skeleton } from "@/components/ui/skeleton"
import { useDashboard } from "@/hooks/use-dashboard"
import {
  DASHBOARD_CATEGORIES,
  DASHBOARD_EMPLOYEES,
  DASHBOARD_SEGMENTS,
  DEMO_ANALYSIS_DATE,
  formatDashboardDate,
} from "@/lib/dashboard"
import { useAuthStore } from "@/stores/use-auth-store"
import { hasPermission } from "@/lib/authorization"
import { toastSuccess } from "@/utils/toast"
import {
  CategoryChart,
  OpportunityMatrixChart,
  PotentialChart,
  PredictionChart,
  RevenueChart,
  SegmentChart,
} from "@/features/dashboard/dashboard-charts"
import { MetricCards } from "@/features/dashboard/metric-cards"
import { PriorityCustomers } from "@/features/dashboard/priority-customers"

export function DashboardPage() {
  const { filters, setFilters, query } = useDashboard()
  const user = useAuthStore((state) => state.user)
  const data = query.data
  const canExport = hasPermission(user, "customers:export")
  const hasFilters =
    [
      filters.segment,
      filters.potential,
      filters.category,
      filters.employee,
    ].some((value) => value !== "all") || filters.period !== "90d"
  const resetFilters = () => void setFilters(null)

  function exportReport() {
    if (!data || !canExport) return
    const lines = [
      "Ngày,Doanh thu (VND),Đơn hàng,Ngày kỳ trước,Doanh thu kỳ trước (VND),Đơn hàng kỳ trước",
      ...data.trend.map((point) =>
        [
          point.date,
          point.revenue,
          point.orders,
          point.previous_date,
          point.previous_revenue,
          point.previous_orders,
        ].join(",")
      ),
    ]
    const url = URL.createObjectURL(
      new Blob(["\uFEFF" + lines.join("\r\n")], {
        type: "text/csv;charset=utf-8",
      })
    )
    const link = document.createElement("a")
    link.href = url
    link.download = `tong-quan-${data.period.from}-${data.period.to}.csv`
    document.body.appendChild(link)
    link.click()
    link.remove()
    // Let the browser start reading the blob before releasing its URL.
    window.setTimeout(() => URL.revokeObjectURL(url), 10_000)
    toastSuccess("Đã xuất báo cáo")
  }

  return (
    <div className="flex w-full min-w-0 flex-col gap-4 p-3">
      <header className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tổng quan</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Hiệu quả kinh doanh và tiềm năng khách hàng.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {hasFilters && (
            <Button variant="ghost" size="sm" onClick={resetFilters}>
              <FilterXIcon data-icon="inline-start" />
              Xoá bộ lọc
            </Button>
          )}
          <CalendarDaysIcon className="size-4 text-muted-foreground" />
          <AppSelect
            aria-label="Khoảng thời gian"
            className="w-44"
            value={filters.period}
            onChange={(period) => void setFilters({ period })}
            options={[
              { value: "30d", label: "30 ngày gần nhất" },
              { value: "90d", label: "90 ngày gần nhất" },
              { value: "6m", label: "6 tháng gần nhất" },
              { value: "12m", label: "12 tháng gần nhất" },
              { value: "custom", label: "Khoảng tùy chọn" },
            ]}
          />
          {canExport && (
            <Button disabled={!data || query.isFetching} onClick={exportReport}>
              <DownloadIcon data-icon="inline-start" />
              Xuất CSV
            </Button>
          )}
        </div>
      </header>
      <FieldGroup className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Field className="gap-1.5">
          <FieldLabel
            className="text-xs text-muted-foreground"
            htmlFor="dashboard-segment"
          >
            Phân khúc
          </FieldLabel>
          <AppSelect
            id="dashboard-segment"
            aria-label="Phân khúc"
            className="w-full"
            value={filters.segment}
            onChange={(segment) => void setFilters({ segment })}
            options={[
              { value: "all", label: "Tất cả phân khúc" },
              ...Object.entries(DASHBOARD_SEGMENTS).map(([value, label]) => ({
                value: value as typeof filters.segment,
                label,
              })),
            ]}
          />
        </Field>
        <Field className="gap-1.5">
          <FieldLabel
            className="text-xs text-muted-foreground"
            htmlFor="dashboard-potential"
          >
            Mức tiềm năng
          </FieldLabel>
          <AppSelect
            id="dashboard-potential"
            aria-label="Mức tiềm năng"
            className="w-full"
            value={filters.potential}
            onChange={(potential) => void setFilters({ potential })}
            options={[
              { value: "all", label: "Tất cả mức tiềm năng" },
              { value: "HIGH", label: "Tiềm năng cao (≥ 80)" },
              { value: "POTENTIAL", label: "Tiềm năng (60–79)" },
              { value: "NORMAL", label: "Thông thường (< 60)" },
              { value: "INSUFFICIENT_DATA", label: "Chưa đủ dữ liệu" },
            ]}
          />
        </Field>
        <Field className="gap-1.5">
          <FieldLabel
            className="text-xs text-muted-foreground"
            htmlFor="dashboard-category"
          >
            Nhóm sản phẩm
          </FieldLabel>
          <AppSelect
            id="dashboard-category"
            aria-label="Nhóm sản phẩm"
            className="w-full"
            value={filters.category}
            onChange={(category) =>
              void setFilters({ category: category as typeof filters.category })
            }
            options={[
              { value: "all", label: "Tất cả nhóm sản phẩm" },
              ...DASHBOARD_CATEGORIES,
            ]}
          />
        </Field>
        <Field className="gap-1.5">
          <FieldLabel
            className="text-xs text-muted-foreground"
            htmlFor="dashboard-employee"
          >
            Nhân viên phụ trách
          </FieldLabel>
          <AppSelect
            id="dashboard-employee"
            aria-label="Nhân viên phụ trách"
            className="w-full"
            value={filters.employee}
            onChange={(employee) =>
              void setFilters({ employee: employee as typeof filters.employee })
            }
            options={[
              { value: "all", label: "Tất cả nhân viên" },
              ...DASHBOARD_EMPLOYEES,
            ]}
          />
        </Field>
      </FieldGroup>
      {filters.period === "custom" && (
        <FieldGroup className="grid gap-3 sm:max-w-lg sm:grid-cols-2">
          <Field>
            <FieldLabel htmlFor="dashboard-from">Từ ngày</FieldLabel>
            <Input
              id="dashboard-from"
              type="date"
              className="scheme-light dark:scheme-dark"
              value={filters.from}
              max={filters.to}
              onChange={(event) =>
                void setFilters({ from: event.target.value })
              }
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="dashboard-to">Đến ngày</FieldLabel>
            <Input
              id="dashboard-to"
              type="date"
              className="scheme-light dark:scheme-dark"
              value={filters.to}
              min={filters.from}
              max={DEMO_ANALYSIS_DATE}
              onChange={(event) => void setFilters({ to: event.target.value })}
            />
          </Field>
        </FieldGroup>
      )}
      {query.isPending ? (
        <div
          aria-label="Đang tải tổng quan"
          aria-busy="true"
          className="grid gap-4"
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[0, 1, 2, 3].map((item) => (
              <Skeleton className="h-36 rounded-xl" key={item} />
            ))}
          </div>
          <Skeleton className="h-96 rounded-xl" />
        </div>
      ) : query.isError ? (
        <Alert variant="destructive">
          <AlertTitle>Không thể hiển thị tổng quan</AlertTitle>
          <AlertDescription>
            {query.error.message}
            <Button
              variant="outline"
              size="sm"
              onClick={() => void query.refetch()}
            >
              <RefreshCwIcon data-icon="inline-start" />
              Thử lại
            </Button>
          </AlertDescription>
        </Alert>
      ) : data ? (
        <>
          <MetricCards metrics={data.metrics} />
          {data.metrics.customers.current === 0 ? (
            <Empty className="min-h-80 border">
              <EmptyHeader>
                <EmptyTitle>Không có dữ liệu phù hợp</EmptyTitle>
                <EmptyDescription>
                  Thử thay đổi khoảng thời gian hoặc bỏ bớt điều kiện lọc.
                </EmptyDescription>
              </EmptyHeader>
              <EmptyContent>
                <Button variant="outline" onClick={resetFilters}>
                  Xóa bộ lọc
                </Button>
              </EmptyContent>
            </Empty>
          ) : (
            <>
              <div className="grid min-w-0 gap-4 xl:grid-cols-3">
                <RevenueChart data={data} />
                <SegmentChart data={data} />
              </div>
              <div className="grid min-w-0 gap-4 lg:grid-cols-2 2xl:grid-cols-3">
                <PotentialChart data={data} />
                <CategoryChart data={data} />
                <PredictionChart data={data} />
              </div>
              <OpportunityMatrixChart data={data} />
              <PriorityCustomers key={JSON.stringify(filters)} data={data} />
            </>
          )}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
            <p>
              {data.data_quality.excluded_orders} đơn không hợp lệ đã loại ·{" "}
              {data.data_quality.unscored_customers} khách hàng chưa thể chấm
              điểm
            </p>
            <p>
              Đối chiếu {formatDashboardDate(data.period.previous_from)} –{" "}
              {formatDashboardDate(data.period.previous_to)}
            </p>
          </div>
        </>
      ) : null}
    </div>
  )
}
