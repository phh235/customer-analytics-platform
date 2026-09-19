import apiClient from "@/api/client"

export type CustomerStatus = "ACTIVE" | "INACTIVE" | "VIP"

export interface CustomerRecord {
  id: string
  customer_code: string
  name: string
  image_url: string | null
  email: string | null
  phone: string | null
  address: string | null
  status: CustomerStatus | string
  gender: string | null
  date_of_birth: string | null
  region: string | null
  customer_since: string | null
  total_orders: number
  total_spent: number | string
  avg_order_value: number | string
  last_purchase_date: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedCustomersResponse {
  current: number
  size: number
  total: number
  pages: number
  records: CustomerRecord[]
}

export interface CustomerPayload {
  name: string
  email?: string | null
  phone?: string | null
  address?: string | null
  status?: CustomerStatus
}

export async function getCustomers(
  params: {
    page?: number
    size?: number
    search?: string
  } = {}
) {
  const { data } = await apiClient.get<PaginatedCustomersResponse>(
    "/customers",
    { params }
  )
  return data
}

export async function createCustomer(payload: CustomerPayload) {
  const { data } = await apiClient.post<CustomerRecord>("/customers", payload)
  return data
}

export async function updateCustomer(
  customerId: string,
  payload: Partial<CustomerPayload>
) {
  const { data } = await apiClient.patch<CustomerRecord>(
    `/customers/${customerId}`,
    payload
  )
  return data
}

export async function deleteCustomer(customerId: string) {
  const { data } = await apiClient.delete<CustomerRecord>(
    `/customers/${customerId}`
  )
  return data
}

export async function uploadCustomerImage(customerId: string, image: File) {
  const formData = new FormData()
  formData.append("image", image)
  const { data } = await apiClient.post<CustomerRecord>(
    `/customers/${customerId}/image`,
    formData,
    {
      headers: {
        "Content-Type": undefined,
      },
    }
  )
  return data
}
