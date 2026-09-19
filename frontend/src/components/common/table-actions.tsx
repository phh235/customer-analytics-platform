import type { ReactNode } from "react"

import { AppDropdown } from "@/components/common/app-dropdown"

interface TableAction {
  key: string
  label: string
  icon: ReactNode
  onClick: () => void
  disabled?: boolean
  variant?: "outline" | "destructive"
}

export function TableActions({ actions }: { actions: TableAction[] }) {
  return (
    <div className="flex justify-end">
      <AppDropdown
        items={actions.map((action) => ({
          ...action,
          variant: action.variant === "destructive" ? "destructive" : "default",
        }))}
      />
    </div>
  )
}
