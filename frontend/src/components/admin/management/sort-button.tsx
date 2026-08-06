import { ArrowDownIcon, ArrowUpDownIcon, ArrowUpIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

interface SortButtonProps {
  label: string
  sortKey: string
  activeKey: string
  direction: "asc" | "desc"
  onClick: () => void
}

export function SortButton({
  label,
  sortKey,
  activeKey,
  direction,
  onClick,
}: SortButtonProps) {
  return (
    <Button type="button" variant="ghost" onClick={onClick} className="-ml-3">
      {label}
      {sortKey === activeKey ? (
        direction === "asc" ? (
          <ArrowUpIcon data-icon="inline-end" />
        ) : (
          <ArrowDownIcon data-icon="inline-end" />
        )
      ) : (
        <ArrowUpDownIcon data-icon="inline-end" />
      )}
    </Button>
  )
}
