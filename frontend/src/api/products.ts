import apiClient from "@/api/client"

export type ProductStatus = "ACTIVE" | "INACTIVE"

export interface ProductRecord {
  id: string
  product_code: string
  name: string
  sku: string | null
  category: string
  description: string | null
  image_url: string | null
  price: number | string
  status: ProductStatus | string
  created_at: string
  updated_at: string
  related_products?: ProductRecord[]
}

export interface PaginatedProductsResponse {
  current: number
  size: number
  total: number
  pages: number
  records: ProductRecord[]
}

export interface ProductPayload {
  name: string
  sku?: string | null
  category: string
  description?: string | null
  image_url?: string | null
  price: number
  status: ProductStatus
}

export async function getProducts(params: {
  page?: number
  size?: number
  category?: string
} = {}) {
  const { data } = await apiClient.get<PaginatedProductsResponse>("/products", {
    params,
  })
  return data
}

export async function getProduct(productId: string) {
  const { data } = await apiClient.get<ProductRecord>(`/products/${productId}`)
  return data
}

export async function createProduct(payload: ProductPayload) {
  const { data } = await apiClient.post<ProductRecord>("/products", payload)
  return data
}

export async function updateProduct(
  productId: string,
  payload: Partial<ProductPayload>
) {
  const { data } = await apiClient.patch<ProductRecord>(
    `/products/${productId}`,
    payload
  )
  return data
}

export async function deleteProduct(productId: string) {
  const { data } = await apiClient.delete<ProductRecord>(
    `/products/${productId}`
  )
  return data
}

export async function uploadProductImage(
  productId: string,
  image: File
) {
  const formData = new FormData()
  formData.append("image", image)
  const { data } = await apiClient.post<ProductRecord>(
    `/products/${productId}/image`,
    formData,
    {
      headers: {
        "Content-Type": undefined,
      },
    }
  )
  return data
}
