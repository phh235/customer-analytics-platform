import { useQuery } from "@tanstack/react-query"

import {
  getProductInterest,
  getProductUniqueViewers,
  getProductViewTrend,
  getProductViewers,
  getProductViews,
  getTopInterestedCustomers,
  getTrendingProducts,
} from "@/api/product-analytics"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export function useProductAnalytics(
  productId: string | undefined,
  filters: {
    from: string
    to: string
    groupBy: "DAY" | "WEEK" | "MONTH"
    size: number
  }
) {
  const enabled = Boolean(productId)
  const interestQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "interest",
      filters.from,
      filters.to,
    ],
    queryFn: ({ signal }) => getProductInterest(productId!, filters, signal),
    enabled,
  })
  const trendQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "trend",
      filters.from,
      filters.to,
      filters.groupBy,
    ],
    queryFn: ({ signal }) => getProductViewTrend(productId!, filters, signal),
    enabled,
  })
  const viewsQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "views",
      filters.from,
      filters.to,
    ],
    queryFn: ({ signal }) => getProductViews(productId!, filters, signal),
    enabled,
  })
  const uniqueViewersQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "unique-viewers",
      filters.from,
      filters.to,
    ],
    queryFn: ({ signal }) =>
      getProductUniqueViewers(productId!, filters, signal),
    enabled,
  })
  const viewersQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "viewers",
      filters.from,
      filters.to,
    ],
    queryFn: ({ signal }) =>
      getProductViewers(productId!, { ...filters, limit: 100 }, signal),
    enabled,
  })
  const customersQuery = useQuery({
    queryKey: [
      "product-analytics",
      productId,
      "top-customers",
      filters.from,
      filters.to,
      filters.size,
    ],
    queryFn: ({ signal }) =>
      getTopInterestedCustomers(
        productId!,
        { ...filters, limit: filters.size },
        signal
      ),
    enabled,
  })

  useQueryErrorToast(
    interestQuery.error ??
      viewsQuery.error ??
      uniqueViewersQuery.error ??
      viewersQuery.error ??
      trendQuery.error ??
      customersQuery.error,
    "Không thể tải phân tích mức độ quan tâm sản phẩm."
  )

  return {
    interestQuery,
    viewsQuery,
    uniqueViewersQuery,
    viewersQuery,
    trendQuery,
    customersQuery,
  }
}

export function useTrendingProducts(period: "7D" | "30D", limit = 10) {
  const query = useQuery({
    queryKey: ["product-analytics", "trending", period, limit],
    queryFn: ({ signal }) => getTrendingProducts(period, limit, signal),
  })
  useQueryErrorToast(query.error, "Không thể tải sản phẩm xu hướng.")
  return query
}
