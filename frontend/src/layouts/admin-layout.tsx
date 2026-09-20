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
import { AiChatWidget } from "@/components/ai-chat-widget"

export const AdminLayout = () => {
  return (
    <SidebarProvider className="h-svh min-h-0 overflow-hidden">
      <AppSidebar />
      <SidebarInset className="min-h-0 min-w-0 overflow-hidden">
        <header className="sticky top-0 z-40 flex h-14 shrink-0 items-center justify-between gap-2 border-b bg-background px-3">
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
        <div className="flex min-h-0 min-w-0 flex-1 flex-col gap-4 overflow-y-auto p-0">
          <Outlet />
        </div>
        <AiChatWidget />
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AdminLayout
