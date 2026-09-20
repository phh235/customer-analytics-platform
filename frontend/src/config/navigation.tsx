import {
  BriefcaseBusinessIcon,
  ChartNoAxesCombinedIcon,
  LayoutDashboardIcon,
  PackageIcon,
  SettingsIcon,
} from "lucide-react"
import type { UserRole } from "@/types/user"

export interface NavigationItem {
  title: string
  url: string
  icon?: React.ReactNode
  isActive?: boolean
  requiredRoles?: readonly UserRole[]
  items?: {
    title: string
    url: string
    requiredRoles?: readonly UserRole[]
  }[]
}

export const navMain: NavigationItem[] = [
  {
    title: "Tổng quan",
    url: "/dashboard",
    icon: <LayoutDashboardIcon />,
  },
  {
    title: "Vận hành",
    url: "/dashboard/customers",
    icon: <BriefcaseBusinessIcon />,
    items: [
      {
        title: "Khách hàng",
        url: "/dashboard/customers",
      },
      {
        title: "Giao dịch",
        url: "/dashboard/transactions",
      },
    ],
  },
  {
    title: "Sản phẩm",
    url: "/dashboard/products",
    icon: <PackageIcon />,
    items: [
      {
        title: "Danh sách sản phẩm",
        url: "/dashboard/products",
      },
      {
        title: "Danh mục",
        url: "/dashboard/categories",
      },
    ],
  },
  {
    title: "Phân tích",
    url: "/dashboard/analytics",
    icon: <ChartNoAxesCombinedIcon />,
    items: [
      {
        title: "Phân khúc",
        url: "/dashboard/analytics/segments",
      },
      {
        title: "Dự đoán",
        url: "/dashboard/analytics/predictions",
      },
      {
        title: "Danh sách ưu tiên",
        url: "/dashboard/analytics/priority",
      },
      {
        title: "Quản lý mô hình",
        url: "/dashboard/analytics/models",
        requiredRoles: ["ADMIN"],
      },
    ],
  },
  {
    title: "Hệ thống",
    url: "/dashboard/system",
    icon: <SettingsIcon />,
    items: [
      {
        title: "Quản lý tài khoản",
        url: "/dashboard/users",
        requiredRoles: ["ADMIN"],
      },
      {
        title: "Nhập dữ liệu",
        url: "/dashboard/system/import",
      },
    ],
  },
]
