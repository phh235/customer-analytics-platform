import { describe, expect, it } from "vitest"
import { buildDemoDashboard } from "@/mocks/dashboard"
import { DEFAULT_DASHBOARD_FILTERS, getDashboardRange } from "@/lib/dashboard"
import type { DashboardFilters } from "@/types/dashboard"

describe("Dashboard demo contract", () => {
  it.each(["30d", "90d", "6m", "12m"] as const)(
    "tổng hợp nhất quán cho kỳ %s",
    (period) => {
      const data = buildDemoDashboard({ ...DEFAULT_DASHBOARD_FILTERS, period })
      expect(data.trend.reduce((sum, point) => sum + point.revenue, 0)).toBe(
        data.metrics.revenue.current
      )
      expect(
        data.trend.reduce((sum, point) => sum + point.previous_revenue, 0)
      ).toBe(data.metrics.revenue.previous)
      expect(data.trend.reduce((sum, point) => sum + point.orders, 0)).toBe(
        data.metrics.orders.current
      )
      expect(
        data.categories.reduce((sum, category) => sum + category.revenue, 0)
      ).toBe(data.metrics.revenue.current)
      expect(
        data.segments.reduce((sum, segment) => sum + segment.count, 0)
      ).toBe(data.metrics.customers.current)
      expect(
        data.potential.distribution.reduce(
          (sum, bucket) => sum + bucket.count,
          0
        ) + data.potential.insufficient_count
      ).toBe(data.metrics.customers.current)
      expect(
        data.predictions.distribution.reduce(
          (sum, bucket) => sum + bucket.count,
          0
        ) + data.predictions.insufficient_count
      ).toBe(data.metrics.customers.current)
      expect(Date.parse(data.period.to) - Date.parse(data.period.from)).toBe(
        Date.parse(data.period.previous_to) -
          Date.parse(data.period.previous_from)
      )
      expect(data.metrics.aov.current).toBe(
        Math.round(data.metrics.revenue.current / data.metrics.orders.current)
      )
    }
  )

  it("các bộ lọc áp dụng cùng lúc vào toàn bộ kết quả", () => {
    const filters: DashboardFilters = {
      ...DEFAULT_DASHBOARD_FILTERS,
      employee: "nv-01",
      potential: "HIGH",
      category: "phone",
    }
    const data = buildDemoDashboard(filters)
    expect(data.metrics.customers.current).toBeLessThan(
      buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS).metrics.customers.current
    )
    expect(data.categories.map((category) => category.id)).toEqual(["phone"])
    expect(data.potential.eligible_count).toBe(data.potential.high_count)
    expect(
      data.priority_customers.every(
        (customer) =>
          customer.employee_name === "Nguyễn Ngọc Mai" &&
          customer.potential_score >= 80
      )
    ).toBe(true)
    expect(data.priority_customers.length).toBeLessThanOrEqual(10)
    expect(data.opportunity_customers.length).toBeGreaterThan(0)
    expect(
      data.opportunity_customers.every(
        (customer) =>
          customer.potential_score >= 0 &&
          customer.purchase_probability >= 0 &&
          customer.purchase_probability <= 1
      )
    ).toBe(true)
  })

  it("thiếu dữ liệu không bị biến thành điểm hoặc xác suất bằng 0", () => {
    const data = buildDemoDashboard({
      ...DEFAULT_DASHBOARD_FILTERS,
      potential: "INSUFFICIENT_DATA",
    })
    expect(data.metrics.customers.current).toBeGreaterThan(0)
    expect(data.potential.average_score).toBeNull()
    expect(
      data.potential.distribution.every((bucket) => bucket.count === 0)
    ).toBe(true)
    expect(data.predictions.status).toBe("insufficient_data")
    expect(data.predictions.model_version).toBeNull()
    expect(data.metrics.aov.current).toBe(0)
    expect(data.priority_customers).toEqual([])
  })

  it("giữ Potential Score độc lập với xác suất ML", () => {
    const data = buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS)
    expect(
      data.priority_customers.some(
        (customer) =>
          customer.purchase_probability !== null &&
          customer.purchase_probability * 100 !== customer.potential_score
      )
    ).toBe(true)
    expect(
      Object.values(data.potential.weights).reduce(
        (sum, value) => sum + value,
        0
      )
    ).toBeCloseTo(1)
    expect(buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS)).toEqual(data)
  })

  it("trả trạng thái rỗng khi các điều kiện lọc mâu thuẫn", () => {
    const data = buildDemoDashboard({
      ...DEFAULT_DASHBOARD_FILTERS,
      potential: "HIGH",
      segment: "INSUFFICIENT_DATA",
    })
    expect(data.metrics.customers.current).toBe(0)
    expect(data.metrics.aov.current).toBe(0)
    expect(data.metrics.revenue.change_percent).toBeNull()
    expect(data.priority_customers).toEqual([])
  })

  it.each([
    { from: "2026-09-20", to: "2026-09-19" },
    { from: "2026-02-30", to: "2026-03-10" },
    { from: "2026-09-01", to: "2026-10-01" },
    { from: "2024-01-01", to: "2026-09-19" },
  ])("kiểm tra khoảng ngày tùy chọn", (dates) => {
    expect(() =>
      getDashboardRange({
        ...DEFAULT_DASHBOARD_FILTERS,
        period: "custom",
        ...dates,
      })
    ).toThrow()
  })
})
