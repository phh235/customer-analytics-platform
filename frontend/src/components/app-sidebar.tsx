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
import { useAuthStore } from "@/stores/use-auth-store"
import { BRAND_NAME } from "@/lib/brand"
import { MainLogo } from "@/lib/svg"

export const AppSidebar = ({
  ...props
}: React.ComponentProps<typeof Sidebar>) => {
  const authUser = useAuthStore((state) => state.user)

  if (!authUser) return null
  const user = { name: authUser.full_name, email: authUser.email }

  const visibleNavItems = navMain
    .map((item) => ({
      ...item,
      items: item.items?.filter(
        (subItem) =>
          !subItem.requiredRoles ||
          subItem.requiredRoles.includes(authUser.role_code)
      ),
    }))
    .filter(
      (item) =>
        !item.requiredRoles || item.requiredRoles.includes(authUser.role_code)
    )

  return (
    <Sidebar collapsible="icon" {...props} variant="inset">
      <SidebarHeader>
        <div className="flex h-13 items-center justify-center overflow-hidden whitespace-nowrap text-foreground [&>img]:size-9 [&>img]:shrink-0 group-data-[collapsible=icon]:[&>img]:size-9">
          <MainLogo />
          <span className="ml-2 grid grid-cols-[1fr] opacity-100 transition-[grid-template-columns,margin,opacity] duration-150 ease-linear group-data-[collapsible=icon]:ml-0 group-data-[collapsible=icon]:grid-cols-[0fr] group-data-[collapsible=icon]:opacity-0">
            <span className="min-w-0 overflow-hidden text-base font-medium md:text-lg">
              {BRAND_NAME}
            </span>
          </span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={visibleNavItems} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
