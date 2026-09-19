import { queryOptions, useQuery } from "@tanstack/react-query"

import { getCustomers } from "@/api/customers"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const customerQueryKeys = {
  all: ["customers"] as const,
  list: (params: { page?: number; size?: number; search?: string }) =>
    ["customers", "list", params] as const,
}

export function customersQueryOptions(
  params: { page?: number; size?: number; search?: string } = {}
) {
  return queryOptions({
    queryKey: customerQueryKeys.list(params),
    queryFn: () => getCustomers(params),
  })
}

export function useCustomers(
  params: { page?: number; size?: number; search?: string } = {},
  fallback = "Không thể tải danh sách khách hàng."
) {
  const query = useQuery(customersQueryOptions(params))
  useQueryErrorToast(query.error, fallback)
  return query
}
