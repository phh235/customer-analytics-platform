import { queryOptions, useQuery } from "@tanstack/react-query"

import { getProduct, getProducts } from "@/api/products"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const productQueryKeys = {
  all: ["products"] as const,
  list: (params: {
    page?: number
    size?: number
    category?: string
    search?: string
  }) => ["products", "list", params] as const,
  detail: (productId: string) => ["products", "detail", productId] as const,
}

export function productsQueryOptions(
  params: {
    page?: number
    size?: number
    category?: string
    search?: string
  } = {}
) {
  return queryOptions({
    queryKey: productQueryKeys.list(params),
    queryFn: () => getProducts(params),
  })
}

export function useProducts(
  params: {
    page?: number
    size?: number
    category?: string
    search?: string
  } = {},
  fallback = "Không thể tải danh sách sản phẩm."
) {
  const query = useQuery(productsQueryOptions(params))
  useQueryErrorToast(query.error, fallback)
  return query
}

export function useProduct(productId?: string) {
  const query = useQuery({
    queryKey: productQueryKeys.detail(productId ?? ""),
    queryFn: () => getProduct(productId!),
    enabled: Boolean(productId),
  })
  useQueryErrorToast(query.error, "Không thể tải thông tin sản phẩm.")
  return query
}
