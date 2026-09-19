import { SearchIcon } from "lucide-react"

import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"

export function TableSearch({
  value,
  onChange,
  placeholder,
  ariaLabel = "Tìm kiếm bảng",
}: {
  value: string
  onChange: (value: string) => void
  placeholder: string
  ariaLabel?: string
}) {
  return (
    <div className="px-3">
      <InputGroup className="max-w-sm">
        <InputGroupAddon>
          <SearchIcon />
        </InputGroupAddon>
        <InputGroupInput
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          aria-label={ariaLabel}
        />
      </InputGroup>
    </div>
  )
}
