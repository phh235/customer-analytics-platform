export type DashboardPeriod = "30d" | "90d" | "6m" | "12m" | "custom"
export type DashboardSegment =
  | "HIGH_VALUE"
  | "LOYAL"
  | "AT_RISK"
  | "POTENTIAL"
  | "NEW_CUSTOMER"
  | "NORMAL"
  | "INSUFFICIENT_DATA"
export type PotentialLevel =
  "HIGH" | "POTENTIAL" | "NORMAL" | "INSUFFICIENT_DATA"

export interface DashboardFilters {
  period: DashboardPeriod
  from: string
  to: string
  segment: DashboardSegment | "all"
  potential: PotentialLevel | "all"
  category: string
  employee: string
}

export interface DashboardMetric {
  current: number
  previous: number
  change_percent: number | null
}

export interface DashboardBucket {
  label: string
  min: number
  max: number
  count: number
}

export interface DashboardPriorityCustomer {
  id: string
  code: string
  name: string
  email: string
  segment: DashboardSegment
  potential_score: number
  purchase_probability: number | null
  revenue: number
  order_count: number
  recency_days: number
  preferred_category: string | null
  employee_name: string
}

export interface DashboardOpportunityCustomer {
  id: string
  name: string
  segment: DashboardSegment
  potential_score: number
  purchase_probability: number
  revenue: number
}

export interface DashboardOverview {
  meta: {
    source: "mock" | "live"
    generated_at: string
    analysis_date: string
    run_id: string
    config_version: string
    currency: "VND"
    timezone: string
  }
  period: {
    from: string
    to: string
    previous_from: string
    previous_to: string
  }
  filters: DashboardFilters
  metrics: {
    customers: DashboardMetric
    orders: DashboardMetric
    revenue: DashboardMetric
    aov: DashboardMetric
  }
  trend: {
    date: string
    previous_date: string
    revenue: number
    previous_revenue: number
    orders: number
    previous_orders: number
  }[]
  segments: { key: DashboardSegment; label: string; count: number }[]
  potential: {
    distribution: DashboardBucket[]
    high_count: number
    eligible_count: number
    insufficient_count: number
    average_score: number | null
    thresholds: { high: number; potential: number }
    weights: {
      recency: number
      frequency: number
      monetary: number
      interaction: number
    }
  }
  categories: {
    id: string
    name: string
    revenue: number
    orders: number
    units: number
    customers: number
  }[]
  predictions: {
    status: "available" | "not_deployed" | "insufficient_data"
    model_version: string | null
    prediction_date: string | null
    horizon_days: number
    feature_window: { from: string; to: string }
    evaluated_customers: number
    insufficient_count: number
    distribution: DashboardBucket[]
  }
  opportunity_customers: DashboardOpportunityCustomer[]
  priority_customers: DashboardPriorityCustomer[]
  priority_total: number
  data_quality: {
    valid_orders: number
    excluded_orders: number
    unscored_customers: number
    interaction_source: "simulated" | "real"
  }
}
