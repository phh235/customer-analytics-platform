import { useEffect, useState } from "react"

import { getApiErrorMessage } from "@/api/errors"
import {
  getAnalyticsDashboard,
  type DashboardResponse,
} from "@/api/analytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatCurrency,
  formatEnumLabel,
  SEGMENT_LABELS,
} from "@/lib/admin-management"

export const Component = () => {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getAnalyticsDashboard()
      .then((response) => {
        if (!cancelled) {
          setDashboard(response)
          setError(null)
        }
      })
      .catch((requestError: unknown) => {
        if (!cancelled) setError(getApiErrorMessage(requestError))
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4">
      <header>
        <h1 className="text-2xl font-semibold">Tổng quan</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Tổng hợp hiệu suất khách hàng và giao dịch trong 365 ngày gần nhất.
        </p>
      </header>

      {error ? (
        <p className="py-8 text-center text-sm text-destructive">{error}</p>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ["Khách hàng", dashboard?.total_customers ?? "—"],
              ["Đơn hàng", dashboard?.total_orders ?? "—"],
              [
                "Doanh thu",
                dashboard
                  ? formatCurrency(Number(dashboard.total_revenue))
                  : "—",
              ],
              [
                "Giá trị đơn trung bình",
                dashboard ? formatCurrency(Number(dashboard.aov)) : "—",
              ],
            ].map(([label, value]) => (
              <Card key={label}>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {label}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-2xl font-semibold">
                  {value}
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Phân bố phân khúc</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(dashboard?.segment_distribution ?? {}).map(
                ([segment, count]) => (
                  <div
                    key={segment}
                    className="rounded-lg border p-3 text-sm"
                  >
                    <div className="text-muted-foreground">
                      {formatEnumLabel(segment, SEGMENT_LABELS)}
                    </div>
                    <div className="mt-1 text-xl font-semibold">{count}</div>
                  </div>
                )
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}

export default Component
