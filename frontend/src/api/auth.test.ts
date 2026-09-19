import { describe, expect, it, vi } from "vitest"
import { authClient } from "@/api/client"
import {
  getCurrentUser,
  registerAccount,
  requestForgotPassword,
  resetForgottenPassword,
  verifyForgotPassword,
} from "@/api/auth"

vi.mock("@/api/client", () => ({
  authClient: { get: vi.fn(), post: vi.fn() },
}))

describe("current user response", () => {
  it.each(["ADMIN", "MANAGER", "ANALYST", "SALES", "CSKH", "USER", "CLIENT"])(
    "chấp nhận vai trò %s",
    async (role_code) => {
      vi.mocked(authClient.get).mockResolvedValue({ data: { role_code } })
      expect((await getCurrentUser()).role_code).toBe(role_code)
    }
  )

  it.each([{ role_code: "UNKNOWN" }, {}, null])(
    "từ chối phản hồi không có vai trò được hỗ trợ",
    async (data) => {
      vi.mocked(authClient.get).mockResolvedValue({ data })
      await expect(getCurrentUser()).rejects.toThrow(
        "Vai trò của tài khoản chưa được hỗ trợ"
      )
    }
  )
})

describe("public auth flows", () => {
  it("đăng ký chỉ gửi email, password và full_name", async () => {
    vi.mocked(authClient.post).mockResolvedValue({
      data: { message: "Đăng ký tài khoản thành công.", user: {} },
    })

    await registerAccount({
      email: "user@example.com",
      password: "StrongPassword123!",
      full_name: "Nguyen Van A",
    })
    expect(authClient.post).toHaveBeenCalledWith("/auth/register", {
      email: "user@example.com",
      password: "StrongPassword123!",
      full_name: "Nguyen Van A",
    })
  })

  it("gọi đúng chuỗi endpoint quên mật khẩu", async () => {
    vi.mocked(authClient.post)
      .mockResolvedValueOnce({ data: { retry_after: 60 } })
      .mockResolvedValueOnce({ data: { reset_token: "rt_token" } })
      .mockResolvedValueOnce({ data: { message: "Đổi mật khẩu thành công." } })

    await requestForgotPassword("user@example.com")
    await verifyForgotPassword("user@example.com", "482913")
    await resetForgottenPassword("rt_token", "NewStrongPassword123!")

    expect(authClient.post).toHaveBeenNthCalledWith(
      1,
      "/auth/password/forgot/request",
      { email: "user@example.com" }
    )
    expect(authClient.post).toHaveBeenNthCalledWith(
      2,
      "/auth/password/forgot/verify",
      { email: "user@example.com", otp: "482913" }
    )
    expect(authClient.post).toHaveBeenNthCalledWith(3, "/auth/password/reset", {
      reset_token: "rt_token",
      new_password: "NewStrongPassword123!",
    })
  })
})
