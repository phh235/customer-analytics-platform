import * as React from "react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
  icon?: React.ReactNode
}

export interface AppSelectProps {
  options: SelectOption[]
  value?: string
  defaultValue?: string
  onChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  size?: "sm" | "default"
  className?: string
  contentClassName?: string
  name?: string
  id?: string
  "aria-label"?: string
}

export const AppSelect = ({
  options,
  value,
  defaultValue,
  onChange,
  placeholder = "Select an option",
  disabled,
  size = "default",
  className,
  contentClassName,
  name,
  id,
  "aria-label": ariaLabel,
}: AppSelectProps) => {
  return (
    <Select
      value={value}
      defaultValue={defaultValue}
      onValueChange={(val) => onChange?.(val ?? "")}
      disabled={disabled}
      name={name}
    >
      <SelectTrigger
        id={id}
        aria-label={ariaLabel}
        size={size}
        className={className}
      >
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent className={contentClassName}>
        {options.map((option) => (
          <SelectItem
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            <span className="flex items-center gap-2">
              {option.icon && <span className="shrink-0">{option.icon}</span>}
              <span>{option.label}</span>
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
