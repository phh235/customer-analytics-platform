import * as React from "react"
import {
  Combobox,
  ComboboxInput,
  ComboboxContent,
  ComboboxList,
  ComboboxItem,
  ComboboxEmpty,
  ComboboxChips,
  ComboboxChip,
  ComboboxChipsInput,
  useComboboxAnchor,
} from "@/components/ui/combobox"

export interface ComboboxOption {
  value: string
  label: string
  disabled?: boolean
}

export interface AppComboboxProps<Multiple extends boolean = false> {
  options: ComboboxOption[]
  value?: Multiple extends true ? string[] : string
  defaultValue?: Multiple extends true ? string[] : string
  onChange?: (value: Multiple extends true ? string[] : string) => void
  placeholder?: string
  disabled?: boolean
  showClear?: boolean
  className?: string
  contentClassName?: string
  emptyText?: string
  multiple?: Multiple
}

export const AppCombobox = <Multiple extends boolean = false>({
  options,
  value,
  defaultValue,
  onChange,
  placeholder = "Select option...",
  disabled = false,
  showClear = false,
  className,
  contentClassName,
  emptyText = "No results found",
  multiple = false as Multiple,
}: AppComboboxProps<Multiple>) => {
  const anchorRef = useComboboxAnchor()

  const resolvedOptionsMap = React.useMemo(() => {
    return new Map(options.map((opt) => [opt.value, opt.label]))
  }, [options])

  const itemValues = React.useMemo(() => {
    return options.map((opt) => opt.value)
  }, [options])

  const itemToStringLabel = React.useCallback(
    (val: string) => resolvedOptionsMap.get(val) || val,
    [resolvedOptionsMap]
  )

  if (multiple) {
    const selectedValues = (Array.isArray(value) ? value : []) as string[]

    return (
      <Combobox
        value={selectedValues}
        defaultValue={defaultValue as string[] | undefined}
        onValueChange={(val) => {
          ;(onChange as ((val: string[]) => void) | undefined)?.(val)
        }}
        disabled={disabled}
        multiple
        items={itemValues}
        itemToStringLabel={itemToStringLabel}
      >
        <ComboboxChips ref={anchorRef} className={className}>
          {selectedValues.map((val) => {
            const label = resolvedOptionsMap.get(val) || val
            return <ComboboxChip key={val}>{label}</ComboboxChip>
          })}
          <ComboboxChipsInput
            placeholder={selectedValues.length === 0 ? placeholder : undefined}
          />
        </ComboboxChips>
        <ComboboxContent anchor={anchorRef} className={contentClassName}>
          <ComboboxEmpty>{emptyText}</ComboboxEmpty>
          <ComboboxList>
            {(itemValue: string) => {
              const label = resolvedOptionsMap.get(itemValue) || itemValue
              const option = options.find((opt) => opt.value === itemValue)
              return (
                <ComboboxItem
                  key={itemValue}
                  value={itemValue}
                  disabled={option?.disabled}
                >
                  {label}
                </ComboboxItem>
              )
            }}
          </ComboboxList>
        </ComboboxContent>
      </Combobox>
    )
  }

  return (
    <Combobox
      value={(value as string | undefined) ?? null}
      defaultValue={(defaultValue as string | undefined) ?? null}
      onValueChange={(val) => {
        ;(onChange as ((val: string) => void) | undefined)?.(val ?? "")
      }}
      disabled={disabled}
      items={itemValues}
      itemToStringLabel={itemToStringLabel}
    >
      <ComboboxInput
        placeholder={placeholder}
        showClear={showClear}
        className={className}
      />
      <ComboboxContent className={contentClassName}>
        <ComboboxEmpty>{emptyText}</ComboboxEmpty>
        <ComboboxList>
          {(itemValue: string) => {
            const label = resolvedOptionsMap.get(itemValue) || itemValue
            const option = options.find((opt) => opt.value === itemValue)
            return (
              <ComboboxItem
                key={itemValue}
                value={itemValue}
                disabled={option?.disabled}
              >
                {label}
              </ComboboxItem>
            )
          }}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  )
}
