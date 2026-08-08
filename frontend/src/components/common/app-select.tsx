import * as React from "react"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export interface SelectOption<Value extends string = string> {
  value: Value
  label: string
  disabled?: boolean
  icon?: React.ReactNode
}

export interface AppSelectProps<Value extends string = string> {
  options: SelectOption<Value>[]
  value?: Value
  defaultValue?: Value
  onChange?: (value: Value) => void
  placeholder?: string
  disabled?: boolean
  size?: "sm" | "default"
  className?: string
  contentClassName?: string
  name?: string
  id?: string
  "aria-label"?: string
}

export const AppSelect = <Value extends string = string>({
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
}: AppSelectProps<Value>) => {
  const [uncontrolledValue, setUncontrolledValue] = React.useState<
    Value | undefined
  >(defaultValue)
  const selectedValue = value ?? uncontrolledValue
  const selectedOption = options.find(
    (option) => option.value === selectedValue
  )

  return (
    <Select
      value={value}
      defaultValue={defaultValue}
      onValueChange={(val) => {
        if (val !== null) {
          if (value === undefined) setUncontrolledValue(val as Value)
          onChange?.(val as Value)
        }
      }}
      disabled={disabled}
      name={name}
    >
      <SelectTrigger
        id={id}
        aria-label={ariaLabel}
        size={size}
        className={className}
      >
        <SelectValue placeholder={placeholder}>
          {selectedOption?.label}
        </SelectValue>
      </SelectTrigger>
      <SelectContent className={contentClassName}>
        <SelectGroup>
          {options.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              <span className="flex items-center gap-2">
                {option.icon ? (
                  <span className="shrink-0">{option.icon}</span>
                ) : null}
                <span>{option.label}</span>
              </span>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  )
}
