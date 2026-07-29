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
import { MainLogo } from "@/lib/svg"

const data = {
  user: {
    name: "phh235",
    email: "phanhuyhoang.dev@gmail.com",
    avatar: "https://github.com/phh235.png",
  },
  navMain,
}

export const AppSidebar = ({
  ...props
}: React.ComponentProps<typeof Sidebar>) => {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex h-14 items-center justify-center overflow-hidden whitespace-nowrap text-primary md:border-b [&>svg]:size-7 [&>svg]:shrink-0 group-data-[collapsible=icon]:[&>svg]:size-7">
          <MainLogo />
          <span className="ml-2 grid grid-cols-[1fr] opacity-100 transition-[grid-template-columns,margin,opacity] duration-150 ease-linear group-data-[collapsible=icon]:ml-0 group-data-[collapsible=icon]:grid-cols-[0fr] group-data-[collapsible=icon]:opacity-0">
            <span className="min-w-0 overflow-hidden text-lg font-medium">
              Customer Analytics
            </span>
          </span>
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
