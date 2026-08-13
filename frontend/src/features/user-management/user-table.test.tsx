import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
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
    const user = userEvent.setup()
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

    const editButton = screen.getByRole("button", {
      name: "Chỉnh sửa Nguyễn An",
    })
    const deleteButton = screen.getByRole("button", {
      name: "Vô hiệu hóa Nguyễn An",
    })

    expect(editButton).toBeEnabled()
    expect(deleteButton).toBeEnabled()

    await user.click(editButton)
    await user.click(deleteButton)

    expect(onEdit).toHaveBeenCalledWith(editableUser)
    expect(onDelete).toHaveBeenCalledWith(editableUser)
    expect(
      screen.getByRole("button", { name: "Chỉnh sửa Tài khoản hiện tại" })
    ).toBeDisabled()
    expect(
      screen.getByRole("button", {
        name: "Không thể vô hiệu hóa tài khoản hiện tại",
      })
    ).toBeDisabled()
    expect(
      screen.getByRole("button", { name: "Chỉnh sửa Quản trị viên" })
    ).toBeDisabled()
  })
})
