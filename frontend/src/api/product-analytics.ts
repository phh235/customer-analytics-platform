import apiClient from "@/api/client"

interface ProductInterestApiResponse {
  product_id: string
  product_code: string | null
  product_name: string
  total_views: number
  unique_viewers: number
  from_date: string
  to_date: string
}

interface ProductViewsApiResponse {
  total_views: number
}

interface ProductUniqueViewersApiResponse {
  unique_viewers: number
}

interface ProductViewerApiResponse {
  customer_id: string
  customer_code: string | null
  customer_name: string
  views: number
  last_view_at: string
}

interface ProductViewersApiResponse {
  product_id: string
  records: ProductViewerApiResponse[]
}

interface ProductViewTrendApiResponse {
  product_id: string
  group_by: "day" | "week" | "month"
  points: { period_start: string; views: number }[]
}

interface TrendingProductsApiResponse {
  records: {
    product_id: string
    product_code: string | null
    product_name: string
    current_period_views: number
    previous_period_views: number
    growth_percent: number | null
    trend_status:
      "NEW_TREND" | "STRONG_TRENDING" | "TRENDING" | "STABLE" | "DECLINING"
  }[]
}

export interface ProductInterestOverview {
  productId: string
  productCode: string | null
  productName: string
  totalViews: number
  uniqueViewers: number
  from: string
  to: string
}

export interface ProductViews {
  totalViews: number
}

export interface ProductUniqueViewers {
  uniqueViewers: number
}

export interface ProductViewTrendItem {
  period: string
  views: number
}

export interface ProductViewTrendResponse {
  productId: string
  groupBy: "DAY" | "WEEK" | "MONTH"
  items: ProductViewTrendItem[]
}

export interface InterestedCustomer {
  customerId: string
  customerCode: string | null
  customerName: string
  viewCount: number
  lastViewedAt: string
}

export interface ProductViewersResponse {
  productId: string
  items: InterestedCustomer[]
}

export interface TrendingProduct {
  productId: string
  productCode: string | null
  productName: string
  currentViews: number
  previousViews: number
  growthPercent: number | null
  trendStatus:
    "NEW_TREND" | "STRONG_TRENDING" | "TRENDING" | "STABLE" | "DECLINING"
}

export interface TrendingProductsResponse {
  period: "7D" | "30D"
  items: TrendingProduct[]
}

interface DateRange {
  from: string
  to: string
}

const recentProductViews = new Map<string, number>()
const PRODUCT_VIEW_DEDUPLICATION_MS = 2_000

const toDateParams = ({ from, to }: DateRange) => ({
  from_date: from,
  to_date: to,
})

const mapViewer = (viewer: ProductViewerApiResponse): InterestedCustomer => ({
  customerId: viewer.customer_id,
  customerCode: viewer.customer_code,
  customerName: viewer.customer_name,
  viewCount: viewer.views,
  lastViewedAt: viewer.last_view_at,
})

export async function recordProductView(productId: string) {
  const now = Date.now()
  const lastRecordedAt = recentProductViews.get(productId) ?? 0

  if (now - lastRecordedAt < PRODUCT_VIEW_DEDUPLICATION_MS) return
  recentProductViews.set(productId, now)

  try {
    await apiClient.post(`/products/${productId}/view`)
  } catch (error) {
    recentProductViews.delete(productId)
    throw error
  }
}

export async function getProductInterest(
  productId: string,
  params: DateRange,
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductInterestApiResponse>(
    `/analytics/products/${productId}/interest`,
    { params: toDateParams(params), signal }
  )
  return {
    productId: data.product_id,
    productCode: data.product_code,
    productName: data.product_name,
    totalViews: data.total_views,
    uniqueViewers: data.unique_viewers,
    from: data.from_date,
    to: data.to_date,
  } satisfies ProductInterestOverview
}

export async function getProductViews(
  productId: string,
  params: DateRange,
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductViewsApiResponse>(
    `/analytics/products/${productId}/views`,
    { params: toDateParams(params), signal }
  )
  return { totalViews: data.total_views } satisfies ProductViews
}

export async function getProductUniqueViewers(
  productId: string,
  params: DateRange,
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductUniqueViewersApiResponse>(
    `/analytics/products/${productId}/unique-viewers`,
    { params: toDateParams(params), signal }
  )
  return { uniqueViewers: data.unique_viewers } satisfies ProductUniqueViewers
}

export async function getProductViewers(
  productId: string,
  params: DateRange & { limit: number },
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductViewersApiResponse>(
    `/analytics/products/${productId}/viewers`,
    { params: { ...toDateParams(params), limit: params.limit }, signal }
  )
  return {
    productId: data.product_id,
    items: data.records.map(mapViewer),
  } satisfies ProductViewersResponse
}

export async function getProductViewTrend(
  productId: string,
  params: DateRange & { groupBy: "DAY" | "WEEK" | "MONTH" },
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductViewTrendApiResponse>(
    `/analytics/products/${productId}/trend`,
    {
      params: {
        ...toDateParams(params),
        group_by: params.groupBy.toLowerCase(),
      },
      signal,
    }
  )
  return {
    productId: data.product_id,
    groupBy: data.group_by.toUpperCase() as "DAY" | "WEEK" | "MONTH",
    items: data.points.map((point) => ({
      period: point.period_start,
      views: point.views,
    })),
  } satisfies ProductViewTrendResponse
}

export async function getTopInterestedCustomers(
  productId: string,
  params: DateRange & { limit: number },
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<ProductViewersApiResponse>(
    `/analytics/products/${productId}/top-interested-customers`,
    { params: { ...toDateParams(params), limit: params.limit }, signal }
  )
  return {
    productId: data.product_id,
    items: data.records.map(mapViewer),
  } satisfies ProductViewersResponse
}

export async function getTrendingProducts(
  period: "7D" | "30D",
  limit = 10,
  signal?: AbortSignal
) {
  const periodDays = period === "7D" ? 7 : 30
  const { data } = await apiClient.get<TrendingProductsApiResponse>(
    "/analytics/products/trending",
    { params: { period_days: periodDays, limit }, signal }
  )
  return {
    period,
    items: data.records.map((product) => ({
      productId: product.product_id,
      productCode: product.product_code,
      productName: product.product_name,
      currentViews: product.current_period_views,
      previousViews: product.previous_period_views,
      growthPercent: product.growth_percent,
      trendStatus: product.trend_status,
    })),
  } satisfies TrendingProductsResponse
}
