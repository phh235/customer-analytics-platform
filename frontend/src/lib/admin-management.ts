export type ProductStatus = "active" | "inactive"
export type CustomerStatus = "active" | "inactive"

export interface Product {
  id: string
  name: string
  sku: string
  category: string
  price: number
  status: ProductStatus
  updatedAt: string
}

export interface Customer {
  id: string
  name: string
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
}

export interface CustomerFormData {
  name: string
  email: string
  phone: string
  status: CustomerStatus
}

export interface Category {
  id: string
  name: string
  productCount: number
  updatedAt: string
}

export interface CategoryFormData {
  name: string
}

export const PRODUCT_CATEGORIES = [
  "Điện thoại",
  "Laptop",
  "Phụ kiện",
  "Thiết bị nhà thông minh",
]

export const SAMPLE_PRODUCTS: Product[] = [
  {
    id: "SP-1001",
    name: "Tai nghe chống ồn AirFlow",
    sku: "AF-1001",
    category: "Phụ kiện",
    price: 2490000,
    status: "active",
    updatedAt: "2026-07-28",
  },
  {
    id: "SP-1002",
    name: "Laptop Nova Pro 14",
    sku: "NP-1402",
    category: "Laptop",
    price: 28990000,
    status: "active",
    updatedAt: "2026-07-25",
  },
  {
    id: "SP-1003",
    name: "Điện thoại PixelPeak X",
    sku: "PP-X003",
    category: "Điện thoại",
    price: 17990000,
    status: "active",
    updatedAt: "2026-07-22",
  },
  {
    id: "SP-1004",
    name: "Bàn phím cơ Lite 75",
    sku: "LT-7504",
    category: "Phụ kiện",
    price: 1690000,
    status: "inactive",
    updatedAt: "2026-07-19",
  },
  {
    id: "SP-1005",
    name: "Camera Home View 360",
    sku: "HV-3605",
    category: "Thiết bị nhà thông minh",
    price: 1290000,
    status: "active",
    updatedAt: "2026-07-16",
  },
  {
    id: "SP-1006",
    name: "Màn hình ViewMax 27 4K",
    sku: "VM-2706",
    category: "Phụ kiện",
    price: 8490000,
    status: "active",
    updatedAt: "2026-07-12",
  },
]

export const SAMPLE_CUSTOMERS: Customer[] = [
  {
    id: "KH-2001",
    name: "Nguyễn Minh Anh",
    email: "minhanh.nguyen@example.com",
    phone: "0901 234 567",
    orders: 12,
    totalSpent: 42890000,
    status: "active",
    joinedAt: "2025-11-08",
  },
  {
    id: "KH-2002",
    name: "Trần Quốc Huy",
    email: "quochuy.tran@example.com",
    phone: "0912 345 678",
    orders: 8,
    totalSpent: 21650000,
    status: "active",
    joinedAt: "2026-01-17",
  },
  {
    id: "KH-2003",
    name: "Lê Thu Hà",
    email: "thuha.le@example.com",
    phone: "0987 654 321",
    orders: 5,
    totalSpent: 9850000,
    status: "active",
    joinedAt: "2026-02-24",
  },
  {
    id: "KH-2004",
    name: "Phạm Gia Bảo",
    email: "giabao.pham@example.com",
    phone: "0933 111 222",
    orders: 2,
    totalSpent: 3790000,
    status: "inactive",
    joinedAt: "2026-03-12",
  },
  {
    id: "KH-2005",
    name: "Đỗ Khánh Linh",
    email: "khanhlinh.do@example.com",
    phone: "0978 222 333",
    orders: 15,
    totalSpent: 55750000,
    status: "active",
    joinedAt: "2025-09-30",
  },
]

export const normalize = (value: string) => value.toLocaleLowerCase("vi-VN")

export const formatCurrency = (value: number) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(value)

export const formatDate = (value: string) =>
  new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(value))

export const createId = (prefix: string) =>
  `${prefix}-${String(Date.now()).slice(-6)}`
