import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router"
import { describe, expect, it, vi } from "vitest"

import { registerAccount } from "@/api/auth"
import { Component } from "@/pages/auth/register"

vi.mock("@/api/auth", () => ({ registerAccount: vi.fn() }))
vi.mock("@/utils/toast", () => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}))

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

  it("gửi đúng payload public registration", async () => {
    const user = userEvent.setup()
    vi.mocked(registerAccount).mockResolvedValue({
      message: "Đăng ký tài khoản thành công.",
      user: {
        id: "user-1",
        email: "an@example.com",
        full_name: "Nguyễn An",
        status: "ACTIVE",
        role_code: "USER",
        created_at: "2026-03-10T10:00:00Z",
      },
    })

    render(
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    )
    await user.type(screen.getByLabelText("Họ và tên"), " Nguyễn An ")
    await user.type(screen.getByLabelText("Email"), "AN@EXAMPLE.COM")
    await user.type(screen.getByLabelText("Mật khẩu"), "password123")
    await user.type(screen.getByLabelText("Xác nhận mật khẩu"), "password123")
    await user.click(screen.getByRole("button", { name: "Đăng ký" }))

    expect(registerAccount).toHaveBeenCalledWith({
      email: "an@example.com",
      password: "password123",
      full_name: "Nguyễn An",
    })
  })
})
