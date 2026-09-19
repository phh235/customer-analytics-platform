import { screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { NuqsTestingAdapter } from "nuqs/adapters/testing"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  deleteCustomer,
  getCustomers,
  type CustomerRecord,
} from "@/api/customers"
import { Component } from "@/pages/admin/customers"
import { useAuthStore } from "@/stores/use-auth-store"
import { renderWithQueryClient } from "@/test/render"

vi.mock("@/api/customers", () => ({
  getCustomers: vi.fn(),
  createCustomer: vi.fn(),
  updateCustomer: vi.fn(),
  deleteCustomer: vi.fn(),
}))

const customer: CustomerRecord = {
  id: "customer-1",
  customer_code: "KH-001",
  name: "Nguyễn Minh Anh",
  image_url: null,
  email: "minhanh@example.com",
  phone: "0901234567",
  address: null,
  status: "ACTIVE",
  gender: null,
  date_of_birth: null,
  region: null,
  customer_since: "2026-01-01",
  total_orders: 1,
  total_spent: 1000000,
  avg_order_value: 1000000,
  last_purchase_date: "2026-09-01",
  created_at: "2026-01-01",
  updated_at: "2026-09-01",
}

describe("Customer table actions", () => {
  beforeEach(() => {
    vi.mocked(getCustomers).mockResolvedValue({
      current: 1,
      size: 100,
      total: 1,
      pages: 1,
      records: [customer],
    })
    useAuthStore.setState({
      user: {
        id: "admin-1",
        full_name: "Admin",
        email: "admin@example.com",
        role_code: "ADMIN",
        permissions: [],
        status: "ACTIVE",
        created_at: "2026-01-01",
        last_login_at: null,
      },
    })
  })
  afterEach(() => useAuthStore.setState({ user: null }))

  it("mở sửa và xác nhận xoá từ menu của đúng khách hàng", async () => {
    const user = userEvent.setup()
    renderWithQueryClient(
      <NuqsTestingAdapter>
        <Component />
      </NuqsTestingAdapter>
    )
    const row = within(
      await screen.findByRole(
        "row",
        { name: /Nguyễn Minh Anh/ },
        { timeout: 5000 }
      )
    )
    expect(
      row.queryByRole("button", { name: "Chỉnh sửa" })
    ).not.toBeInTheDocument()
    await user.click(row.getByRole("button", { name: "Tùy chọn thao tác" }))
    await user.click(await screen.findByRole("menuitem", { name: "Chỉnh sửa" }))
    const dialog = await screen.findByRole("dialog", {
      name: "Chỉnh sửa khách hàng",
    })
    expect(within(dialog).getByLabelText("Họ và tên")).toHaveValue(
      customer.name
    )
    await user.click(within(dialog).getByRole("button", { name: "Huỷ" }))
    await waitFor(() =>
      expect(
        screen.queryByRole("dialog", { name: "Chỉnh sửa khách hàng" })
      ).not.toBeInTheDocument()
    )
    await user.click(row.getByRole("button", { name: "Tùy chọn thao tác" }))
    await user.click(await screen.findByRole("menuitem", { name: "Xoá" }))
    expect(
      await screen.findByRole("heading", { name: "Xác nhận xoá khách hàng" })
    ).toBeInTheDocument()
    expect(deleteCustomer).not.toHaveBeenCalled()
  })

  it("không hiện thao tác quản lý khi người dùng không có quyền", async () => {
    useAuthStore.setState({
      user: { ...useAuthStore.getState().user!, role_code: "ANALYST" },
    })
    renderWithQueryClient(
      <NuqsTestingAdapter>
        <Component />
      </NuqsTestingAdapter>
    )
    await screen.findByRole(
      "row",
      { name: /Nguyễn Minh Anh/ },
      { timeout: 5000 }
    )
    expect(
      screen.queryByRole("button", { name: "Tùy chọn thao tác" })
    ).not.toBeInTheDocument()
  })
})
