import {
  ArrowLeftRightIcon,
  ChartNoAxesCombinedIcon,
  LayoutDashboardIcon,
  MegaphoneIcon,
  PackageIcon,
  SettingsIcon,
  UsersIcon,
} from "lucide-react"

export const navMain = [
  {
    title: "Tổng quan",
    url: "/dashboard",
    icon: <LayoutDashboardIcon />,
  },
  {
    title: "Sản phẩm & danh mục",
    url: "/dashboard/products",
    icon: <PackageIcon />,
  },
  {
    title: "Khách hàng",
    url: "/dashboard/customers",
    icon: <UsersIcon />,
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
