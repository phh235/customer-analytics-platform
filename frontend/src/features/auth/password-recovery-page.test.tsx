import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { createMemoryRouter, RouterProvider } from "react-router"
import { beforeEach, describe, expect, it, vi } from "vitest"

import {
  requestForgotPassword,
  resetForgottenPassword,
  verifyForgotPassword,
} from "@/api/auth"
import { PasswordRecoveryPage } from "@/features/auth/password-recovery-page"
import { toastSuccess } from "@/utils/toast"

vi.mock("@/utils/toast", () => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}))
vi.mock("@/api/auth", () => ({
  requestForgotPassword: vi.fn(),
  verifyForgotPassword: vi.fn(),
  resetForgottenPassword: vi.fn(),
}))

describe("PasswordRecoveryPage", () => {
  beforeEach(() => {
    vi.mocked(requestForgotPassword).mockResolvedValue({
      message: "Nếu email tồn tại, mã OTP đã được gửi.",
      expires_in: 600,
      retry_after: 60,
    })
    vi.mocked(verifyForgotPassword).mockResolvedValue({
      reset_token: "rt_token",
      expires_in: 600,
    })
    vi.mocked(resetForgottenPassword).mockResolvedValue({
      message: "Đổi mật khẩu thành công. Vui lòng đăng nhập lại.",
    })
  })

  it("đi qua email, OTP và đặt mật khẩu mới", async () => {
    const user = userEvent.setup()
    const router = createMemoryRouter(
      [
        { path: "/forgot-password", element: <PasswordRecoveryPage /> },
        { path: "/login", element: <h1>Đăng nhập</h1> },
      ],
      { initialEntries: ["/forgot-password"] }
    )
    render(<RouterProvider router={router} />)

    await user.type(screen.getByLabelText("Email"), "user@example.com")
    await user.click(screen.getByRole("button", { name: "Tiếp tục" }))

    await user.type(screen.getByLabelText("Mã OTP"), "123456")
    await user.click(screen.getByRole("button", { name: "Xác nhận mã" }))

    await user.type(screen.getByLabelText("Mật khẩu mới"), "new-password")
    await user.type(
      screen.getByLabelText("Xác nhận mật khẩu mới"),
      "new-password"
    )
    await user.click(screen.getByRole("button", { name: "Đặt lại mật khẩu" }))

    expect(
      await screen.findByRole("heading", { name: "Đăng nhập" })
    ).toBeInTheDocument()
    expect(resetForgottenPassword).toHaveBeenCalledWith(
      "rt_token",
      "new-password"
    )
    expect(toastSuccess).toHaveBeenCalledWith(
      "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
    )
  })
})
