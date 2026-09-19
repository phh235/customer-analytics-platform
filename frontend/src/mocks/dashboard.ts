import {
  DASHBOARD_CATEGORIES,
  DASHBOARD_EMPLOYEES,
  DASHBOARD_SEGMENTS,
  DEMO_ANALYSIS_DATE,
  getDashboardRange,
  shiftDate,
} from "@/lib/dashboard"
import type {
  DashboardBucket,
  DashboardFilters,
  DashboardMetric,
  DashboardOverview,
  DashboardSegment,
  PotentialLevel,
} from "@/types/dashboard"

// Deterministic demo fixtures only. Scoring, segmentation and ML are backend responsibilities.
const names = [
  "Nguyễn Minh Anh",
  "Trần Quốc Huy",
  "Lê Thu Hà",
  "Đỗ Khánh Linh",
  "Phạm Gia Bảo",
  "Vũ Ngọc Lan",
  "Bùi Đức Anh",
  "Hoàng Thảo Vy",
  "Đặng Tuấn Minh",
  "Phan Bảo Ngọc",
  "Ngô Hoài Nam",
  "Đinh Hà My",
]
const segments: DashboardSegment[] = [
  "HIGH_VALUE",
  "LOYAL",
  "AT_RISK",
  "POTENTIAL",
  "NEW_CUSTOMER",
  "NORMAL",
]
const customers = Array.from({ length: 240 }, (_, i) => ({
  id: `demo-customer-${i + 1}`,
  code: `KH-${1001 + i}`,
  name: names[i % names.length],
  email: `khachhang${i + 1}@example.com`,
  employee: DASHBOARD_EMPLOYEES[i % 4],
  since: shiftDate(
    DEMO_ANALYSIS_DATE,
    -(i % 5 === 0 ? 12 + ((i * 7) % 70) : 480 + ((i * 13) % 200))
  ),
  segment: (i % 9 === 0
    ? "INSUFFICIENT_DATA"
    : segments[i % 6]) as DashboardSegment,
  score: i % 9 === 0 ? null : 35 + ((i * 17) % 65),
  probability: i % 9 === 0 || i % 11 === 0 ? null : (4 + ((i * 37) % 91)) / 100,
}))
const orders = customers.flatMap((customer, i) => {
  if (customer.score === null) return []
  const maxAge = Math.round(
    (Date.parse(DEMO_ANALYSIS_DATE) - Date.parse(customer.since)) / 86400000
  )
  return Array.from({ length: 8 + ((i * 3) % 17) }, (_, j) => {
    const age = (i * 71 + j * 43 + j * j * 11) % (maxAge + 1)
    const category = DASHBOARD_CATEGORIES[(i * 3 + j) % 5]
    const units = 1 + ((i + j) % 3)
    return {
      customer_id: customer.id,
      date: shiftDate(DEMO_ANALYSIS_DATE, -age),
      category: category.value,
      units,
      amount: (390000 + ((i * 7 + j * 13) % 30) * 190000) * units,
      valid: (i + j) % 13 !== 0,
    }
  })
})

function metric(current: number, previous: number): DashboardMetric {
  return {
    current,
    previous,
    change_percent:
      previous > 0
        ? Math.round(((current - previous) / previous) * 1000) / 10
        : null,
  }
}
function potentialLevel(score: number | null): PotentialLevel {
  return score === null
    ? "INSUFFICIENT_DATA"
    : score >= 80
      ? "HIGH"
      : score >= 60
        ? "POTENTIAL"
        : "NORMAL"
}
function histogram(values: number[], probability = false): DashboardBucket[] {
  return [0, 20, 40, 60, 80].map((min) => ({
    label: probability
      ? `${min}–${min + 20}%`
      : `${min}–${min === 80 ? 100 : min + 19}`,
    min,
    max: min + 20,
    count: values.filter(
      (value) => value >= min && (min === 80 ? value <= 100 : value < min + 20)
    ).length,
  }))
}

export function buildDemoDashboard(
  filters: DashboardFilters
): DashboardOverview {
  const { from, to } = getDashboardRange(filters)
  const days = Math.round((Date.parse(to) - Date.parse(from)) / 86400000) + 1
  const previousFrom = shiftDate(from, -days)
  const previousTo = shiftDate(from, -1)
  const snapshots = customers.map((customer) => {
    const hasHistory = orders.some(
      (order) =>
        order.customer_id === customer.id && order.valid && order.date <= to
    )
    return hasHistory
      ? customer
      : {
          ...customer,
          score: null,
          probability: null,
          segment: "INSUFFICIENT_DATA" as const,
        }
  })
  const scopedCustomers = snapshots.filter(
    (customer) =>
      customer.since <= to &&
      (filters.employee === "all" ||
        customer.employee.value === filters.employee) &&
      (filters.segment === "all" || customer.segment === filters.segment) &&
      (filters.potential === "all" ||
        potentialLevel(customer.score) === filters.potential) &&
      (filters.category === "all" ||
        orders.some(
          (order) =>
            order.customer_id === customer.id &&
            order.category === filters.category &&
            order.valid &&
            order.date >= from &&
            order.date <= to
        ))
  )
  const ids = new Set(scopedCustomers.map((customer) => customer.id))
  const scopedOrders = orders.filter(
    (order) =>
      ids.has(order.customer_id) &&
      (filters.category === "all" || order.category === filters.category)
  )
  const current = scopedOrders.filter(
    (order) => order.valid && order.date >= from && order.date <= to
  )
  const previous = scopedOrders.filter(
    (order) =>
      order.valid && order.date >= previousFrom && order.date <= previousTo
  )
  const revenue = (rows: typeof current) =>
    rows.reduce((sum, order) => sum + order.amount, 0)
  const currentRevenue = revenue(current)
  const previousRevenue = revenue(previous)
  const scores = scopedCustomers.flatMap((customer) =>
    customer.score === null ? [] : [customer.score]
  )
  const probabilities = scopedCustomers.flatMap((customer) =>
    customer.probability === null ? [] : [customer.probability * 100]
  )
  const highCustomers = scopedCustomers.filter(
    (customer) => customer.score !== null && customer.score >= 80
  )
  const currentByCustomer = new Map<
    string,
    { revenue: number; order_count: number }
  >()
  current.forEach((order) => {
    const stats = currentByCustomer.get(order.customer_id) ?? {
      revenue: 0,
      order_count: 0,
    }
    stats.revenue += order.amount
    stats.order_count += 1
    currentByCustomer.set(order.customer_id, stats)
  })

  return {
    meta: {
      source: "mock",
      generated_at: `${DEMO_ANALYSIS_DATE}T09:30:00+07:00`,
      analysis_date: to,
      run_id: "demo-run-20260919",
      config_version: "potential-v1-demo",
      currency: "VND",
      timezone: "Asia/Ho_Chi_Minh",
    },
    period: { from, to, previous_from: previousFrom, previous_to: previousTo },
    filters,
    metrics: {
      customers: metric(
        scopedCustomers.length,
        scopedCustomers.filter((customer) => customer.since <= previousTo)
          .length
      ),
      orders: metric(current.length, previous.length),
      revenue: metric(currentRevenue, previousRevenue),
      aov: metric(
        current.length ? Math.round(currentRevenue / current.length) : 0,
        previous.length ? Math.round(previousRevenue / previous.length) : 0
      ),
    },
    trend: Array.from({ length: days }, (_, index) => {
      const date = shiftDate(from, index)
      const previousDate = shiftDate(previousFrom, index)
      const dayOrders = current.filter((order) => order.date === date)
      const priorOrders = previous.filter(
        (order) => order.date === previousDate
      )
      return {
        date,
        previous_date: previousDate,
        revenue: revenue(dayOrders),
        previous_revenue: revenue(priorOrders),
        orders: dayOrders.length,
        previous_orders: priorOrders.length,
      }
    }),
    segments: (
      Object.entries(DASHBOARD_SEGMENTS) as [DashboardSegment, string][]
    ).map(([key, label]) => ({
      key,
      label,
      count: scopedCustomers.filter((customer) => customer.segment === key)
        .length,
    })),
    potential: {
      distribution: histogram(scores),
      high_count: highCustomers.length,
      eligible_count: scores.length,
      insufficient_count: scopedCustomers.length - scores.length,
      average_score: scores.length
        ? Math.round(
            (scores.reduce((sum, score) => sum + score, 0) / scores.length) * 10
          ) / 10
        : null,
      thresholds: { high: 80, potential: 60 },
      weights: {
        recency: 0.35,
        frequency: 0.3,
        monetary: 0.2,
        interaction: 0.15,
      },
    },
    categories: DASHBOARD_CATEGORIES.map((category) => {
      const rows = current.filter((order) => order.category === category.value)
      return {
        id: category.value,
        name: category.label,
        revenue: revenue(rows),
        orders: rows.length,
        units: rows.reduce((sum, row) => sum + row.units, 0),
        customers: new Set(rows.map((row) => row.customer_id)).size,
      }
    })
      .filter((category) => category.orders > 0)
      .sort((a, b) => b.revenue - a.revenue),
    predictions: {
      status: probabilities.length ? "available" : "insufficient_data",
      model_version: probabilities.length ? "purchase-repeat-v1" : null,
      prediction_date: probabilities.length ? to : null,
      horizon_days: 90,
      feature_window: days,
      evaluated_customers: probabilities.length,
      insufficient_count: scopedCustomers.length - probabilities.length,
      distribution: histogram(probabilities, true),
    },
    opportunity_customers: scopedCustomers
      .filter(
        (customer) => customer.score !== null && customer.probability !== null
      )
      .map((customer) => ({
        id: customer.id,
        name: customer.name,
        segment: customer.segment,
        potential_score: customer.score!,
        purchase_probability: customer.probability!,
        revenue: currentByCustomer.get(customer.id)?.revenue ?? 0,
      }))
      .sort((first, second) => {
        const opportunityDifference =
          second.potential_score * second.purchase_probability -
          first.potential_score * first.purchase_probability
        return opportunityDifference || first.id.localeCompare(second.id)
      })
      .slice(0, 80),
    priority_total: highCustomers.length,
    priority_customers: highCustomers
      .sort((a, b) => b.score! - a.score!)
      .slice(0, 10)
      .map((customer) => ({
        id: customer.id,
        name: customer.name,
        segment: customer.segment,
        potential_score: customer.score!,
        purchase_probability: customer.probability,
        revenue: currentByCustomer.get(customer.id)?.revenue ?? 0,
        employee_id: customer.employee.value,
      })),
    data_quality: {
      valid_orders: current.length,
      excluded_orders: scopedOrders.filter(
        (order) => !order.valid && order.date >= from && order.date <= to
      ).length,
      unscored_customers: scopedCustomers.length - scores.length,
      interaction_source: "simulated",
    },
  }
}
