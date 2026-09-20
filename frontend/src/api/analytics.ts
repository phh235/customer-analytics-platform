import apiClient from "@/api/client"

export interface PaginatedAnalyticsResponse<T> {
  current: number
  size: number
  total: number
  pages: number
  records: T[]
}

export interface AnalyticsListParams {
  page?: number
  size?: number
  search?: string
}

const normalizePaginatedResponse = <T>(
  data: T[] | PaginatedAnalyticsResponse<T>,
  page = 1,
  size = 10
): PaginatedAnalyticsResponse<T> => {
  if (!Array.isArray(data)) return data

  const total = data.length
  return {
    current: page,
    size,
    total,
    pages: Math.max(1, Math.ceil(total / size)),
    records: data.slice((page - 1) * size, page * size),
  }
}

export interface SegmentRecord {
  customer_id: string
  customer_code: string
  name: string
  segment_type: string
  potential_score: number
  reason: string
  calculated_at: string
}

export interface PurchasePredictionRecord {
  customer_id: string
  customer_code: string
  name: string
  prediction_date: string
  prediction_horizon_days: number
  feature_window_days: number
  purchase_probability: number
  model_version: string
}

export interface DashboardResponse {
  days: number
  filters: {
    channel: string | null
    category: string | null
    segment: string | null
    level: string | null
  }
  total_customers: number
  total_orders: number
  total_revenue: number | string
  aov: number | string
  segment_distribution: Record<string, number>
  potential_distribution: Record<string, number>
}

export async function getSegments(
  params: AnalyticsListParams & { days?: number; analysis_date?: string } = {}
) {
  const page = params.page ?? 1
  const size = params.size ?? 10
  const { data } = await apiClient.get<
    SegmentRecord[] | PaginatedAnalyticsResponse<SegmentRecord>
  >("/analytics/segments", {
    params: { days: 365, ...params, page, size },
  })
  return normalizePaginatedResponse(data, page, size)
}

export async function getPurchasePredictions(
  params: AnalyticsListParams & {
    days?: number
    horizon_days?: number
    analysis_date?: string
  } = {}
) {
  const page = params.page ?? 1
  const size = params.size ?? 10
  const { data } = await apiClient.get<
    | PurchasePredictionRecord[]
    | PaginatedAnalyticsResponse<PurchasePredictionRecord>
  >("/analytics/predictions/purchase-repeat", {
    params: {
      days: 365,
      horizon_days: 90,
      ...params,
      page,
      size,
    },
  })
  return normalizePaginatedResponse(data, page, size)
}

export async function getAnalyticsDashboard(days = 365) {
  const { data } = await apiClient.get<DashboardResponse>(
    "/analytics/dashboard",
    { params: { days } }
  )
  return data
}

export interface PriorityCustomerRecord {
  customer_id: string
  customer_code: string
  name: string
  potential_score: number
  potential_level: string
  purchase_probability: number
  preferred_product_category: string | null
  purchase_cycle_days: number | null
  recommendation: string
  priority_reason: string
}

export interface ModelLifecycleRecord {
  version: string
  status: string
  model_type: string | null
  feature_window_days: number | null
  prediction_horizon_days: number | null
  precision: number | string | null
  recall: number | string | null
  f1_score: number | string | null
  roc_auc: number | string | null
  pr_auc: number | string | null
  lift_top10: number | string | null
  precision_top10: number | string | null
  baseline_pr_auc: number | string
  artifact_uri: string | null
  metrics: Record<string, number> | null
  evaluated_at: string | null
}

export async function getPriorityList(
  params: AnalyticsListParams & {
    days?: number
    horizon_days?: number
    analysis_date?: string
  } = {}
) {
  const page = params.page ?? 1
  const size = params.size ?? 10
  const { data } = await apiClient.get<
    | PriorityCustomerRecord[]
    | PaginatedAnalyticsResponse<PriorityCustomerRecord>
  >("/analytics/priority-list", {
    params: {
      days: 365,
      horizon_days: 90,
      ...params,
      page,
      size,
    },
  })
  return normalizePaginatedResponse(data, page, size)
}

export async function getModels(params: AnalyticsListParams = {}) {
  const page = params.page ?? 1
  const size = params.size ?? 10
  const { data } = await apiClient.get<
    ModelLifecycleRecord[] | PaginatedAnalyticsResponse<ModelLifecycleRecord>
  >("/analytics/models", { params: { ...params, page, size } })
  return normalizePaginatedResponse(data, page, size)
}

export async function trainModel(payload: {
  version: string
  model_type: "LOGISTIC_REGRESSION" | "RANDOM_FOREST"
  feature_window_days: number
  prediction_horizon_days: number
  analysis_date?: string
}) {
  const { data } = await apiClient.post<ModelLifecycleRecord>(
    "/analytics/models/train",
    payload
  )
  return data
}

export async function deployModel(version: string) {
  const { data } = await apiClient.post<ModelLifecycleRecord>(
    `/analytics/models/${encodeURIComponent(version)}/deploy`
  )
  return data
}
