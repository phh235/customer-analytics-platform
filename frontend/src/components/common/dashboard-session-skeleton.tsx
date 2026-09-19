import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarInset,
  SidebarProvider,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"

const SKELETON_NAV_ITEMS = 6

export function DashboardSessionSkeleton() {
  return (
    <SidebarProvider
      aria-busy="true"
      aria-label="Đang xác thực phiên đăng nhập"
      className="h-svh min-h-0 overflow-hidden"
    >
      <Sidebar collapsible="icon" variant="inset">
        <SidebarHeader>
          <div className="flex h-14 items-center overflow-hidden px-2">
            <Skeleton className="size-7 shrink-0 rounded-lg" />
            <Skeleton className="ml-2 h-5 w-28 group-data-[collapsible=icon]:ml-0 group-data-[collapsible=icon]:w-0" />
          </div>
        </SidebarHeader>
        <SidebarContent>
          <div className="flex flex-col gap-2 p-2">
            {Array.from({ length: SKELETON_NAV_ITEMS }, (_, index) => (
              <Skeleton
                className="h-9 w-full rounded-lg"
                key={`sidebar-nav-${index}`}
              />
            ))}
          </div>
        </SidebarContent>
        <SidebarFooter>
          <div className="flex items-center gap-2 p-2">
            <Skeleton className="size-8 shrink-0 rounded-full" />
            <div className="grid min-w-0 flex-1 gap-1 group-data-[collapsible=icon]:hidden">
              <Skeleton className="h-3 w-24" />
              <Skeleton className="h-3 w-32" />
            </div>
          </div>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
      <SidebarInset className="min-h-0 overflow-hidden">
        <header className="sticky top-0 z-40 flex h-14 shrink-0 items-center justify-between gap-2 border-b bg-background px-3">
          <div className="flex items-center gap-2">
            <Skeleton className="size-8 rounded-lg" />
            <Separator
              className="h-5 data-vertical:self-center"
              orientation="vertical"
            />
            <Skeleton className="h-8 w-40 rounded-lg" />
          </div>
          <Skeleton className="size-8 rounded-lg" />
        </header>
        <main className="flex min-h-0 flex-1 overflow-hidden p-4">
          <Skeleton className="min-h-72 w-full flex-1 rounded-xl" />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
