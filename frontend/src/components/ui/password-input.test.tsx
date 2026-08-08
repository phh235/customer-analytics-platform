import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"

import { PasswordInput } from "@/components/ui/password-input"

describe("PasswordInput", () => {
  it("cho phép chuyển đổi giữa mật khẩu ẩn và hiện", async () => {
    const user = userEvent.setup()

    render(<PasswordInput aria-label="Mật khẩu" />)

    const input = screen.getByLabelText("Mật khẩu")
    const toggle = screen.getByRole("button", { name: "Hiện mật khẩu" })

    expect(input).toHaveAttribute("type", "password")
    expect(toggle).toHaveAttribute("aria-pressed", "false")

    await user.click(toggle)

    expect(input).toHaveAttribute("type", "text")
    expect(screen.getByRole("button", { name: "Ẩn mật khẩu" })).toHaveAttribute(
      "aria-pressed",
      "true"
    )

    await user.click(screen.getByRole("button", { name: "Ẩn mật khẩu" }))

    expect(input).toHaveAttribute("type", "password")
  })

  it("không cho thao tác khi bị disabled", async () => {
    const user = userEvent.setup()

    render(<PasswordInput aria-label="Mật khẩu" disabled />)

    const input = screen.getByLabelText("Mật khẩu")
    const toggle = screen.getByRole("button", { name: "Hiện mật khẩu" })

    expect(input).toBeDisabled()
    expect(toggle).toBeDisabled()

    await user.click(toggle)

    expect(input).toHaveAttribute("type", "password")
  })
})
