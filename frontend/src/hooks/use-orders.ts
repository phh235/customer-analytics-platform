import { queryOptions, useQuery } from "@tanstack/react-query"

import { getOrders } from "@/api/orders"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const orderQueryKeys = {
  all: ["orders"] as const,
  list: (params: {
    page?: number
    size?: number
    search?: string
    status?: string
  }) => ["orders", "list", params] as const,
}

export function useOrders(
  params: {
    page?: number
    size?: number
    search?: string
    status?: string
  } = {}
) {
  const query = useQuery(
    queryOptions({
      queryKey: orderQueryKeys.list(params),
      queryFn: () => getOrders(params),
    })
  )
  useQueryErrorToast(query.error, "Không thể tải danh sách giao dịch.")
  return query
}
