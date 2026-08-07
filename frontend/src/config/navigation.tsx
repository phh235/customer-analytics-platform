import {
  ArrowLeftRightIcon,
  ChartNoAxesCombinedIcon,
  LayoutDashboardIcon,
  MegaphoneIcon,
  PackageIcon,
  SettingsIcon,
  UsersIcon,
  UserCogIcon,
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
  }[]
}

export const navMain: NavigationItem[] = [
  {
    title: "Tổng quan",
    url: "/dashboard",
    icon: <LayoutDashboardIcon />,
  },
  {
    title: "Sản phẩm và danh mục",
    url: "/dashboard/products",
    icon: <PackageIcon />,
    items: [
      {
        title: "Quản lý sản phẩm",
        url: "/dashboard/products",
      },
      {
        title: "Danh mục",
        url: "/dashboard/categories",
      },
    ],
  },
  {
    title: "Khách hàng",
    url: "/dashboard/customers",
    icon: <UsersIcon />,
  },
  {
    title: "Quản lý tài khoản",
    url: "/dashboard/users",
    icon: <UserCogIcon />,
    requiredRoles: ["ADMIN"],
  },
  {
    title: "Giao dịch",
    url: "/dashboard/transactions",
    icon: <ArrowLeftRightIcon />,
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
    ],
  },
  {
    title: "Hành động",
    url: "/dashboard/actions",
    icon: <MegaphoneIcon />,
    items: [
      {
        title: "Chiến dịch",
        url: "/dashboard/actions/campaigns",
      },
      {
        title: "Báo cáo",
        url: "/dashboard/actions/reports",
      },
    ],
  },
  {
    title: "Hệ thống",
    url: "/dashboard/system",
    icon: <SettingsIcon />,
    items: [
      {
        title: "Nhập dữ liệu",
        url: "/dashboard/system/import",
      },
    ],
  },
]
