import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  useSidebar,
} from "@/components/ui/sidebar"
import { ChevronRightIcon } from "lucide-react"
import { Link, useLocation } from "react-router"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

const ACTIVE_CLASSES =
  "data-active:bg-input/70! data-active:text-sidebar-accent-foreground data-active:hover:bg-input/70! data-active:hover:text-sidebar-accent-foreground"

export const NavMain = ({
  items,
}: {
  items: {
    title: string
    url: string
    icon?: React.ReactNode
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
}) => {
  const { state } = useSidebar()
  const location = useLocation()
  const [renderCollapsed, setRenderCollapsed] = useState(state === "collapsed")

  useEffect(() => {
    const timeout = window.setTimeout(
      () => setRenderCollapsed(state === "collapsed"),
      state === "collapsed" ? 150 : 0
    )

    return () => window.clearTimeout(timeout)
  }, [state])

  return (
    <SidebarGroup>
      <SidebarMenu>
        {items.map((item) => {
          const isParentActive =
            location.pathname === item.url ||
            item.items?.some((subItem) => location.pathname === subItem.url)

          if (!item.items || item.items.length === 0) {
            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  tooltip={item.title}
                  render={<Link to={item.url} />}
                  isActive={isParentActive}
                >
                  {item.icon}
                  <span>{item.title}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            )
          }

          if (renderCollapsed) {
            return (
              <SidebarMenuItem key={item.title}>
                <Popover>
                  <PopoverTrigger
                    render={
                      <SidebarMenuButton
                        tooltip={item.title}
                        isActive={isParentActive}
                        className={ACTIVE_CLASSES}
                      >
                        {item.icon}
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    }
                  />
                  <PopoverContent
                    side="right"
                    align="start"
                    sideOffset={14}
                    className="w-56 gap-1 bg-popover p-1.5"
                  >
                    <div className="px-2.5 pt-1.5 text-xs font-semibold text-muted-foreground">
                      {item.title}
                    </div>
                    <div className="flex flex-col gap-0.5">
                      {item.items.map((subItem) => {
                        const isSubActive = location.pathname === subItem.url
                        return (
                          <Link
                            key={subItem.title}
                            to={subItem.url}
                            className={cn(
                              "flex h-8 items-center rounded-md px-2.5 text-sm text-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                              isSubActive &&
                                "bg-input/70 text-sidebar-accent-foreground hover:bg-input/70 hover:text-sidebar-accent-foreground"
                            )}
                          >
                            {subItem.title}
                          </Link>
                        )
                      })}
                    </div>
                  </PopoverContent>
                </Popover>
              </SidebarMenuItem>
            )
          }

          return (
            <Collapsible
              key={item.title}
              defaultOpen={item.isActive || isParentActive}
              className="group/collapsible"
              render={<SidebarMenuItem />}
            >
              <CollapsibleTrigger
                render={
                  <SidebarMenuButton
                    tooltip={item.title}
                    isActive={isParentActive}
                    className={ACTIVE_CLASSES}
                  />
                }
              >
                {item.icon}
                <span>{item.title}</span>
                <ChevronRightIcon className="ml-auto transition-transform duration-150 group-data-open/collapsible:rotate-90" />
              </CollapsibleTrigger>
              <CollapsibleContent className="h-(--collapsible-panel-height) overflow-hidden opacity-100 transition-[height,opacity] duration-150 ease-out data-ending-style:h-0 data-ending-style:opacity-0 data-starting-style:h-0 data-starting-style:opacity-0">
                <SidebarMenuSub>
                  {item.items.map((subItem) => {
                    const isSubActive = location.pathname === subItem.url
                    return (
                      <SidebarMenuSubItem key={subItem.title}>
                        <SidebarMenuSubButton
                          render={<Link to={subItem.url} />}
                          isActive={isSubActive}
                          className={ACTIVE_CLASSES}
                        >
                          <span>{subItem.title}</span>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    )
                  })}
                </SidebarMenuSub>
              </CollapsibleContent>
            </Collapsible>
          )
        })}
      </SidebarMenu>
    </SidebarGroup>
  )
}
