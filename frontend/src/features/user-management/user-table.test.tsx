import { render, screen, within } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import userEvent from "@testing-library/user-event"

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
  it("cho phép sửa tài khoản đã vô hiệu hóa nhưng không vô hiệu hóa lần nữa", async () => {
    const editableUser = createUser()
    const disabledUser = createUser({
      id: "user-disabled",
      email: "disabled@example.com",
      full_name: "Tài khoản đã vô hiệu hóa",
      status: "DISABLED",
    })
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
        users={[editableUser, disabledUser, currentUser, adminUser]}
        pagination={{
          current: 1,
          size: 10,
          total: 4,
          pages: 1,
          records: [editableUser, disabledUser, currentUser, adminUser],
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

    const user = userEvent.setup()
    const editableRow = within(screen.getByRole("row", { name: /Nguyễn An/ }))
    const trigger = editableRow.getByRole("button", {
      name: "Tùy chọn thao tác",
    })
    await user.click(trigger)
    await user.click(await screen.findByRole("menuitem", { name: "Chỉnh sửa" }))
    expect(onEdit).toHaveBeenCalledWith(editableUser)
    await user.click(trigger)
    await user.click(
      await screen.findByRole("menuitem", { name: "Vô hiệu hóa" })
    )
    expect(onDelete).toHaveBeenCalledWith(editableUser)

    const currentRow = within(
      screen.getByRole("row", { name: new RegExp(currentUser.full_name) })
    )
    await user.click(
      currentRow.getByRole("button", { name: "Tùy chọn thao tác" })
    )
    expect(
      await screen.findByRole("menuitem", { name: "Chỉnh sửa" })
    ).toHaveAttribute("data-disabled")
    expect(
      screen.getByRole("menuitem", { name: "Vô hiệu hóa" })
    ).toHaveAttribute("data-disabled")

    await user.keyboard("{Escape}")
    const disabledRow = within(
      screen.getByRole("row", { name: new RegExp(disabledUser.full_name) })
    )
    await user.click(
      disabledRow.getByRole("button", { name: "Tùy chọn thao tác" })
    )
    expect(
      await screen.findByRole("menuitem", { name: "Chỉnh sửa" })
    ).not.toHaveAttribute("data-disabled")
    expect(
      screen.getByRole("menuitem", { name: "Vô hiệu hóa" })
    ).toHaveAttribute("data-disabled")
    expect(screen.queryByText(adminUser.full_name)).not.toBeInTheDocument()
  })
})
