import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { createMemoryRouter, RouterProvider } from "react-router"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { login, getCurrentUser, refreshAccessToken, logout } from "@/api/auth"
import { clearAccessToken } from "@/api/access-token"
import { Component as LoginPage } from "@/features/auth/login-page"
import {
  AuthenticatedRoute,
  DefaultRoute,
  GuestRoute,
  RoleRoute,
} from "@/features/auth/route-guards"
import { STAFF_ROLES } from "@/lib/auth-routing"
import { useAuthStore } from "@/stores/use-auth-store"
import type { UserRole } from "@/types/user"

vi.mock("@/api/auth", () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
  refreshAccessToken: vi.fn(),
  logout: vi.fn(),
}))
vi.mock("@/utils/toast", () => ({ toastSuccess: vi.fn(), toastError: vi.fn() }))

function renderLogin() {
  const router = createMemoryRouter(
    [
      {
        element: <GuestRoute />,
        children: [{ path: "/login", element: <LoginPage /> }],
      },
      {
        element: <DefaultRoute />,
        children: [{ path: "/", element: <h1>Trang khách hàng</h1> }],
      },
      {
        element: <AuthenticatedRoute />,
        children: [
          {
            element: <RoleRoute allowedRoles={STAFF_ROLES} />,
            children: [
              { path: "/dashboard", element: <h1>Trang quản trị</h1> },
            ],
          },
        ],
      },
    ],
    { initialEntries: ["/login"] }
  )
  render(<RouterProvider router={router} />)
  return router
}

describe("login flow", () => {
  beforeEach(() => {
    clearAccessToken()
    useAuthStore.setState({ status: "unknown", user: null, accessToken: null })
    vi.mocked(refreshAccessToken).mockRejectedValue(
      new Error("No previous session")
    )
    vi.mocked(logout).mockResolvedValue({ message: "Đã đăng xuất" })
  })

  it.each([
    "USER",
    "MANAGER",
    "SALES",
    "CSKH",
    "ADMIN",
    "ANALYST",
  ] as UserRole[])(
    "đăng nhập %s và hiển thị trang bên trong sau khi refresh ban đầu thất bại",
    async (role_code) => {
      const user = userEvent.setup()
      vi.mocked(login).mockResolvedValue({
        access_token: "test-token",
        role_code,
      })
      vi.mocked(getCurrentUser).mockResolvedValue({
        id: "1",
        full_name: "Test User",
        email: "test@example.com",
        role_code,
        status: "ACTIVE",
        permissions: [],
        created_at: "2026-09-19",
        last_login_at: null,
      })
      const router = renderLogin()
      await waitFor(() => expect(screen.getByLabelText("Email")).toBeEnabled())
      await user.type(screen.getByLabelText("Email"), "test@example.com")
      await user.type(screen.getByLabelText("Mật khẩu"), "test-password")
      await user.click(screen.getByRole("button", { name: "Đăng nhập" }))
      const isCustomer = role_code === "USER"
      expect(
        await screen.findByRole("heading", {
          name: isCustomer ? "Trang khách hàng" : "Trang quản trị",
        })
      ).toBeInTheDocument()
      expect(router.state.location.pathname).toBe(
        isCustomer ? "/" : "/dashboard"
      )
      expect(useAuthStore.getState().status).toBe("authenticated")
    }
  )

  it("giữ lại form và xóa phiên khi thông tin tài khoản không hợp lệ", async () => {
    const user = userEvent.setup()
    vi.mocked(login).mockResolvedValue({
      access_token: "test-token",
      role_code: "USER",
    })
    vi.mocked(getCurrentUser).mockRejectedValue(
      new Error("Vai trò không được hỗ trợ")
    )
    const router = renderLogin()
    await waitFor(() => expect(screen.getByLabelText("Email")).toBeEnabled())
    await user.type(screen.getByLabelText("Email"), "test@example.com")
    await user.type(screen.getByLabelText("Mật khẩu"), "test-password")
    await user.click(screen.getByRole("button", { name: "Đăng nhập" }))
    await waitFor(() =>
      expect(useAuthStore.getState().status).toBe("unauthenticated")
    )
    expect(router.state.location.pathname).toBe("/login")
    expect(screen.getByLabelText("Email")).toBeEnabled()
    expect(useAuthStore.getState().accessToken).toBeNull()
  })
})
