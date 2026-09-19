import apiClient from "@/api/client"

export interface OrderItem {
  id: string
  order_id: string
  product_id: string
  quantity: number
  unit_price: number | string
  subtotal: number | string
}

export interface OrderRecord {
  id: string
  customer_id: string
  order_number: string
  order_date: string
  total_amount: number | string
  refund_amount: number | string
  net_amount: number | string
  status: string
  channel: string | null
  notes: string | null
  items: OrderItem[]
  created_at: string
  updated_at: string
}

export interface PaginatedOrdersResponse {
  current: number
  size: number
  total: number
  pages: number
  records: OrderRecord[]
}

export async function getOrders(
  params: {
    page?: number
    size?: number
    search?: string
    status?: string
  } = {}
) {
  const { data } = await apiClient.get<PaginatedOrdersResponse>("/orders", {
    params: {
      ...params,
      search: params.search?.trim() || undefined,
    },
  })
  return data
}
