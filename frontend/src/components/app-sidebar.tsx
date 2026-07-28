import * as React from "react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
import {
  ArrowLeftRightIcon,
  ChartNoAxesCombinedIcon,
  LayoutDashboardIcon,
  MegaphoneIcon,
  SettingsIcon,
  UsersIcon,
} from "lucide-react"
import { MainLogo } from "@/lib/svg"
const data = {
  user: {
    name: "phh235",
    email: "phanhuyhoang.dev@gmail.com",
    avatar: "https://github.com/phh235.png",
  },
  navMain: [
    {
      title: "Tổng quan",
      url: "/dashboard",
      icon: <LayoutDashboardIcon />,
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
  ],
}

export const AppSidebar = ({
  ...props
}: React.ComponentProps<typeof Sidebar>) => {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex h-14 items-center justify-center overflow-hidden text-lg font-semibold whitespace-nowrap text-primary md:border-b [&>svg]:size-10 [&>svg]:shrink-0 group-data-[collapsible=icon]:[&>svg]:size-8">
          <MainLogo />
        </div>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
