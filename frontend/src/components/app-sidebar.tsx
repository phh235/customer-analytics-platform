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
import { navMain } from "@/config/navigation"
import { BRAND_NAME } from "@/lib/brand"
import { MainLogo } from "@/lib/svg"

const data = {
  user: {
    name: "phh235",
    email: "phanhuyhoang.dev@gmail.com",
  },
  navMain,
}

export const AppSidebar = ({
  ...props
}: React.ComponentProps<typeof Sidebar>) => {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex h-14 items-center justify-center overflow-hidden border-b whitespace-nowrap text-primary [&>svg]:size-7 [&>svg]:shrink-0 group-data-[collapsible=icon]:[&>svg]:size-7">
          <MainLogo />
          <span className="ml-2 grid grid-cols-[1fr] opacity-100 transition-[grid-template-columns,margin,opacity] duration-150 ease-linear group-data-[collapsible=icon]:ml-0 group-data-[collapsible=icon]:grid-cols-[0fr] group-data-[collapsible=icon]:opacity-0">
            <span className="min-w-0 overflow-hidden text-base font-medium md:text-lg">
              {BRAND_NAME}
            </span>
          </span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter className="border-t border-border">
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
