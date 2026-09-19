import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router"
import { afterEach, beforeEach, describe, expect, it } from "vitest"

import { Component } from "@/features/auth/login-page"
import { useAuthStore } from "@/stores/use-auth-store"

describe("LoginPage", () => {
  beforeEach(() => {
    useAuthStore.setState({ status: "unauthenticated" })
  })

  afterEach(() => {
    useAuthStore.setState({ status: "unknown" })
  })

  it("hiển thị lỗi khi email và mật khẩu không hợp lệ", async () => {
    const user = userEvent.setup()

    render(
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    )

    await user.type(screen.getByLabelText("Email"), "not-an-email")
    await user.type(screen.getByLabelText("Mật khẩu"), "123")
    await user.click(screen.getByRole("button", { name: "Đăng nhập" }))

    expect(
      await screen.findByText("Địa chỉ email không hợp lệ")
    ).toBeInTheDocument()
    expect(
      await screen.findByText("Mật khẩu phải dài ít nhất 8 ký tự")
    ).toBeInTheDocument()
  })

  it("khóa các liên kết khi đang đăng nhập", () => {
    useAuthStore.setState({ status: "loading" })

    render(
      <MemoryRouter>
        <Component />
      </MemoryRouter>
    )

    for (const name of ["Quên mật khẩu?", "Đăng ký", "tìm hiểu thêm"]) {
      expect(screen.getByRole("link", { name })).toHaveAttribute(
        "aria-disabled",
        "true"
      )
      expect(screen.getByRole("link", { name })).toHaveAttribute(
        "tabindex",
        "-1"
      )
    }
  })
})
