import { Outlet } from "react-router"
import { AppSidebar } from "@/components/app-sidebar"

import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { ThemeToggle } from "@/components/common/theme-toggle"
import { CommandPalette } from "@/components/command-palette"
import { Separator } from "@/components/ui/separator"

export const AdminLayout = () => {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b px-3">
          <div className="flex items-center gap-2">
            <SidebarTrigger />
            <Separator
              className="h-5 data-vertical:self-center"
              orientation="vertical"
            />
            <CommandPalette />
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-0">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AdminLayout
