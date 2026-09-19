import * as React from "react"
import { MoreHorizontalIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

export interface AppDropdownItem {
  key: string
  label: React.ReactNode
  icon?: React.ReactNode
  endIcon?: React.ReactNode
  disabled?: boolean
  variant?: "default" | "destructive"
  onClick?: () => void
}

export interface AppDropdownProps {
  items: AppDropdownItem[]
  header?: React.ReactNode
  trigger?: React.ReactElement
  triggerVariant?: "ghost" | "outline" | "default"
  triggerSize?: "icon-sm" | "icon" | "sm" | "default"
  align?: "start" | "center" | "end"
  sideOffset?: number
  contentClassName?: string
  className?: string
  "aria-label"?: string
}

export const AppDropdown = ({
  items,
  header,
  trigger,
  triggerVariant = "ghost",
  triggerSize = "icon-sm",
  align = "end",
  sideOffset = 4,
  contentClassName,
  className,
  "aria-label": ariaLabel = "Tùy chọn thao tác",
}: AppDropdownProps) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          trigger ?? (
            <Button
              type="button"
              variant={triggerVariant}
              size={triggerSize}
              className={className}
              aria-label={ariaLabel}
            />
          )
        }
      >
        {!trigger ? <MoreHorizontalIcon /> : null}
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align={align}
        sideOffset={sideOffset}
        className={cn("w-fit min-w-32", contentClassName)}
      >
        {header ? (
          <>
            <DropdownMenuGroup>
              <DropdownMenuLabel className="font-normal">
                {header}
              </DropdownMenuLabel>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
          </>
        ) : null}
        <DropdownMenuGroup>
          {items.map((item) => (
            <DropdownMenuItem
              key={item.key}
              variant={item.variant}
              disabled={item.disabled}
              onClick={item.onClick}
            >
              {item.icon}
              <span className="flex-1">{item.label}</span>
              {item.endIcon}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
