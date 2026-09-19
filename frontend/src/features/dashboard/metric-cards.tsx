import {
  ArrowDownRightIcon,
  ArrowUpRightIcon,
  ReceiptTextIcon,
  ShoppingBagIcon,
  UsersIcon,
  WalletIcon,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatDashboardMoney, formatDashboardNumber } from "@/lib/dashboard"
import type { DashboardOverview } from "@/types/dashboard"

export function MetricCards({
  metrics,
}: {
  metrics: DashboardOverview["metrics"]
}) {
  const cards = [
    {
      label: "Doanh thu",
      icon: WalletIcon,
      metric: metrics.revenue,
      format: formatDashboardMoney,
    },
    {
      label: "Đơn hàng hợp lệ",
      icon: ShoppingBagIcon,
      metric: metrics.orders,
      format: formatDashboardNumber,
    },
    {
      label: "Khách hàng",
      icon: UsersIcon,
      metric: metrics.customers,
      format: formatDashboardNumber,
    },
    {
      label: "Giá trị đơn trung bình",
      icon: ReceiptTextIcon,
      metric: metrics.aov,
      format: formatDashboardMoney,
    },
  ]
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(({ label, icon: Icon, metric, format }) => (
        <Card key={label} size="sm">
          <CardContent className="flex flex-col gap-2">
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-sm text-muted-foreground">{label}</h2>
              <Icon className="size-4 text-muted-foreground" />
            </div>
            <p className="text-2xl font-semibold tracking-tight tabular-nums 2xl:text-3xl">
              {format(metric.current)}
            </p>
            <div className="flex flex-wrap items-center gap-2">
              <Badge
                variant={
                  metric.change_percent === null || metric.change_percent === 0
                    ? "secondary"
                    : metric.change_percent > 0
                      ? "success"
                      : "destructive"
                }
              >
                {metric.change_percent === null ? (
                  "Chưa có kỳ đối chiếu"
                ) : (
                  <>
                    {metric.change_percent >= 0 ? (
                      <ArrowUpRightIcon />
                    ) : (
                      <ArrowDownRightIcon />
                    )}
                    {metric.change_percent > 0 ? "+" : ""}
                    {metric.change_percent.toLocaleString("vi-VN")}%
                  </>
                )}
              </Badge>
              <span className="text-xs text-muted-foreground">
                so với kỳ trước
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
