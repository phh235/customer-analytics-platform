export type ProductStatus = "active" | "inactive"
export type CustomerStatus = "active" | "inactive"

export const SEGMENT_LABELS: Record<string, string> = {
  HIGH_VALUE: "Khách hàng giá trị cao",
  LOYAL: "Khách hàng trung thành",
  AT_RISK: "Có nguy cơ rời bỏ",
  POTENTIAL: "Khách hàng tiềm năng",
  NEW_CUSTOMER: "Khách hàng mới",
  NORMAL: "Khách hàng thông thường",
  INSUFFICIENT_DATA: "Chưa đủ dữ liệu",
}

export const SCORE_LEVEL_LABELS: Record<string, string> = {
  HIGH: "Tiềm năng cao",
  POTENTIAL: "Tiềm năng",
  NORMAL: "Bình thường",
  INSUFFICIENT_DATA: "Chưa đủ dữ liệu",
}

export const ORDER_STATUS_LABELS: Record<string, string> = {
  PAID: "Đã thanh toán",
  COMPLETED: "Hoàn tất",
  DELIVERED: "Đã giao",
  PROCESSING: "Đang xử lý",
  CANCELED: "Đã huỷ",
  CANCELLED: "Đã huỷ",
  FAILED: "Thất bại",
  REFUNDED: "Đã hoàn tiền",
  PARTIAL_REFUNDED: "Hoàn tiền một phần",
  RETURNED: "Đã trả hàng",
}

export const ORDER_CHANNEL_LABELS: Record<string, string> = {
  ONLINE: "Trực tuyến",
  OFFLINE: "Tại cửa hàng",
  MARKETPLACE: "Sàn thương mại điện tử",
  WEBSITE: "Website",
  STORE: "Cửa hàng",
}

export const IMPORT_TYPE_LABELS: Record<string, string> = {
  CUSTOMER: "Khách hàng",
  ORDER: "Đơn hàng",
  ORDER_DETAIL: "Chi tiết đơn hàng",
  PRODUCT: "Sản phẩm",
  INTERACTION: "Tương tác",
  DATASET: "Bộ dữ liệu",
}

export const IMPORT_STATUS_LABELS: Record<string, string> = {
  PENDING: "Chờ xử lý",
  VALIDATING: "Đang kiểm tra",
  PROCESSING: "Đang xử lý",
  COMPLETED: "Hoàn tất",
  PARTIALLY_COMPLETED: "Hoàn tất một phần",
  FAILED: "Thất bại",
}

export const MODEL_STATUS_LABELS: Record<string, string> = {
  DRAFT: "Bản nháp",
  TRAINING: "Đang huấn luyện",
  TRAINED: "Đã huấn luyện",
  EVALUATING: "Đang đánh giá",
  APPROVED: "Đã duyệt",
  DEPLOYED: "Đang sử dụng",
  RETIRED: "Đã ngừng sử dụng",
  FAILED: "Thất bại",
}

export const MODEL_TYPE_LABELS: Record<string, string> = {
  LOGISTIC_REGRESSION: "Hồi quy logistic",
  RANDOM_FOREST: "Rừng ngẫu nhiên",
}

export interface Product {
  id: string
  productCode: string
  name: string
  sku: string
  category: string
  imageUrl: string | null
  price: number
  status: ProductStatus
  updatedAt: string
}
export interface Customer {
  id: string
  customerCode: string
  name: string
  imageUrl: string | null
  email: string
  phone: string
  orders: number
  totalSpent: number
  status: CustomerStatus
  joinedAt: string
}

export interface ProductFormData {
  name: string
  sku: string
  category: string
  price: number
  status: ProductStatus
  image: File | null
  removeImage: boolean
}

export interface CustomerFormData {
  name: string
  email: string
  phone: string
  status: CustomerStatus
  image: File | null
}

export interface Category {
  id: string
  code: string
  name: string
  productCount: number
  updatedAt: string
}

export interface CategoryFormData {
  name: string
  code: string
}
