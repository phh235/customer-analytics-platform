import { useQuery } from "@tanstack/react-query"

import {
  type AnalyticsListParams,
  getModels,
  getPriorityList,
  getPurchasePredictions,
  getSegments,
} from "@/api/analytics"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const analyticsQueryKeys = {
  all: ["analytics"] as const,
  segments: (params: AnalyticsListParams & { days?: number }) =>
    ["analytics", "segments", params] as const,
  predictions: (
    params: AnalyticsListParams & { days?: number; horizon_days?: number }
  ) => ["analytics", "predictions", params] as const,
  priority: (
    params: AnalyticsListParams & { days?: number; horizon_days?: number }
  ) => ["analytics", "priority", params] as const,
  models: (params: AnalyticsListParams) =>
    ["analytics", "models", params] as const,
}

function useAnalyticsQuery<T, TQueryKey extends readonly unknown[]>(
  options: {
    queryKey: TQueryKey
    queryFn: () => Promise<T>
  },
  fallback: string
) {
  const query = useQuery(options)
  useQueryErrorToast(query.error, fallback)
  return query
}

export function useSegments(
  params: AnalyticsListParams & { days?: number } = {}
) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.segments(params),
      queryFn: () => getSegments(params),
    },
    "Không thể tải kết quả phân khúc."
  )
}

export function usePurchasePredictions(
  params: AnalyticsListParams & {
    days?: number
    horizon_days?: number
  } = {}
) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.predictions(params),
      queryFn: () => getPurchasePredictions(params),
    },
    "Không thể tải kết quả dự đoán."
  )
}

export function usePriorityCustomers(
  params: AnalyticsListParams & {
    days?: number
    horizon_days?: number
  } = {}
) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.priority(params),
      queryFn: () => getPriorityList(params),
    },
    "Không thể tải danh sách ưu tiên."
  )
}

export function useModels(params: AnalyticsListParams = {}) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.models(params),
      queryFn: () => getModels(params),
    },
    "Không thể tải danh sách mô hình."
  )
}
