import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { UserTable } from "@/features/user-management/user-table"
import type { User } from "@/types/user"

const createUser = (overrides: Partial<User> = {}): User => ({
  id: "user-1",
  email: "nguyen.an@example.com",
  full_name: "Nguyễn An",
  status: "ACTIVE",
  role_code: "CLIENT",
  permissions: [],
  created_at: "2026-08-01T08:00:00Z",
  last_login_at: null,
  ...overrides,
})

describe("UserTable", () => {
  it("cho phép thao tác với người dùng hợp lệ và khóa tài khoản không được sửa", async () => {
    const editableUser = createUser()
    const currentUser = createUser({
      id: "user-current",
      email: "current@example.com",
      full_name: "Tài khoản hiện tại",
    })
    const adminUser = createUser({
      id: "user-admin",
      email: "admin@example.com",
      full_name: "Quản trị viên",
      role_code: "ADMIN",
    })
    const onEdit = vi.fn()
    const onDelete = vi.fn()

    render(
      <UserTable
        users={[editableUser, currentUser, adminUser]}
        pagination={{
          current: 1,
          size: 10,
          total: 3,
          pages: 1,
          records: [editableUser, currentUser, adminUser],
        }}
        page={1}
        pageSize={10}
        loading={false}
        currentUserId={currentUser.id}
        onPageChange={vi.fn()}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    )

    const actionButton = screen.getByRole("button", {
      name: "Thao tác với Nguyễn An",
    })
    fireEvent.click(actionButton)

    const editItem = await screen.findByRole("menuitem", {
      name: "Chỉnh sửa",
    })
    const deleteItem = screen.getByRole("menuitem", {
      name: "Vô hiệu hóa",
    })

    expect(editItem).not.toHaveAttribute("data-disabled")
    expect(deleteItem).not.toHaveAttribute("data-disabled")

    fireEvent.click(editItem)
    expect(onEdit).toHaveBeenCalledWith(editableUser)

    fireEvent.click(actionButton)
    const deleteItemReopened = await screen.findByRole("menuitem", {
      name: "Vô hiệu hóa",
    })
    fireEvent.click(deleteItemReopened)
    expect(onDelete).toHaveBeenCalledWith(editableUser)

    const currentActionBtn = screen.getByRole("button", {
      name: "Thao tác với Tài khoản hiện tại",
    })
    fireEvent.click(currentActionBtn)
    const disabledEditItem = await screen.findByRole("menuitem", {
      name: "Chỉnh sửa",
    })
    expect(disabledEditItem).toHaveAttribute("data-disabled")
    expect(
      screen.getByRole("menuitem", { name: "Vô hiệu hóa" })
    ).toHaveAttribute("data-disabled")
  })
})
