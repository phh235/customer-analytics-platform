import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router"
import { describe, expect, it } from "vitest"

import { Component } from "@/pages/auth/register"

describe("RegisterPage", () => {
  it("hiển thị lỗi khi mật khẩu xác nhận không khớp", async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText("Họ và tên"), "Nguyễn An")
    await user.type(screen.getByLabelText("Email"), "an@example.com")
    await user.type(screen.getByLabelText("Mật khẩu"), "password123")
    await user.type(screen.getByLabelText("Xác nhận mật khẩu"), "password321")
    await user.click(screen.getByRole("button", { name: "Đăng ký" }))

    expect(
      await screen.findByText("Mật khẩu xác nhận không khớp")
    ).toBeInTheDocument()
  })
})
