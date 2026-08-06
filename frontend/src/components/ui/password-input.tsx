import * as React from "react"
import { EyeIcon, EyeOffIcon } from "lucide-react"

import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@/components/ui/input-group"

function PasswordInput({
  className,
  disabled,
  ...props
}: Omit<React.ComponentProps<"input">, "type">) {
  const [isVisible, setIsVisible] = React.useState(false)

  return (
    <InputGroup className={className} data-disabled={disabled || undefined}>
      <InputGroupInput
        type={isVisible ? "text" : "password"}
        disabled={disabled}
        {...props}
      />
      <InputGroupAddon align="inline-end">
        <InputGroupButton
          aria-label={isVisible ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
          aria-pressed={isVisible}
          disabled={disabled}
          onClick={() => setIsVisible((visible) => !visible)}
          size="icon-xs"
        >
          {isVisible ? <EyeOffIcon /> : <EyeIcon />}
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  )
}

export { PasswordInput }
