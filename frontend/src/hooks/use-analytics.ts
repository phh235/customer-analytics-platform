import { useQuery } from "@tanstack/react-query"

import {
  getModels,
  getPriorityList,
  getPurchasePredictions,
  getSegments,
} from "@/api/analytics"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const analyticsQueryKeys = {
  all: ["analytics"] as const,
  segments: (days: number) => ["analytics", "segments", days] as const,
  predictions: (days: number, horizonDays: number) =>
    ["analytics", "predictions", days, horizonDays] as const,
  priority: (days: number, horizonDays: number) =>
    ["analytics", "priority", days, horizonDays] as const,
  models: ["analytics", "models"] as const,
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

export function useSegments(days = 365) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.segments(days),
      queryFn: () => getSegments(days),
    },
    "Không thể tải kết quả phân khúc."
  )
}

export function usePurchasePredictions(days = 365, horizonDays = 90) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.predictions(days, horizonDays),
      queryFn: () => getPurchasePredictions(days, horizonDays),
    },
    "Không thể tải kết quả dự đoán."
  )
}

export function usePriorityCustomers(days = 365, horizonDays = 90) {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.priority(days, horizonDays),
      queryFn: () => getPriorityList(days, horizonDays),
    },
    "Không thể tải danh sách ưu tiên."
  )
}

export function useModels() {
  return useAnalyticsQuery(
    {
      queryKey: analyticsQueryKeys.models,
      queryFn: getModels,
    },
    "Không thể tải danh sách mô hình."
  )
}
