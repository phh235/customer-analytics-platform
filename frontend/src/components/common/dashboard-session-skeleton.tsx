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
import { cn } from "@/lib/utils"

const SKELETON_NAV_ITEMS = [
  "w-full",
  "w-11/12",
  "w-4/5",
  "w-10/12",
  "w-full",
  "w-9/12",
]

export function DashboardSessionSkeleton() {
  return (
    <SidebarProvider
      aria-busy="true"
      aria-label="Đang xác thực phiên đăng nhập"
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
            {SKELETON_NAV_ITEMS.map((width, index) => (
              <Skeleton
                className={cn("h-9 rounded-lg", width)}
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
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b px-3">
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
        <main className="flex flex-1 p-4">
          <Skeleton className="min-h-72 w-full flex-1 rounded-xl" />
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
