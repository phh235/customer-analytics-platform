import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { AppDropdown } from "@/components/common/app-dropdown"

describe("AppDropdown", () => {
  it("mở menu khi click trigger và kích hoạt callback khi chọn item", async () => {
    const handleEdit = vi.fn()
    const handleDelete = vi.fn()

    render(
      <AppDropdown
        aria-label="Thao tác với mục 1"
        items={[
          {
            key: "edit",
            label: "Chỉnh sửa",
            onClick: handleEdit,
          },
          {
            key: "delete",
            label: "Xoá",
            variant: "destructive",
            disabled: true,
            onClick: handleDelete,
          },
        ]}
      />
    )

    const trigger = screen.getByRole("button", { name: "Thao tác với mục 1" })
    fireEvent.click(trigger)

    const editItem = await screen.findByRole("menuitem", { name: "Chỉnh sửa" })
    const deleteItem = screen.getByRole("menuitem", { name: "Xoá" })

    expect(editItem).not.toHaveAttribute("data-disabled")
    expect(deleteItem).toHaveAttribute("data-disabled")

    fireEvent.click(editItem)
    expect(handleEdit).toHaveBeenCalledTimes(1)
  })

  it("hiển thị header trước danh sách thao tác", async () => {
    render(
      <AppDropdown
        header={<span>admin@example.com</span>}
        items={[{ key: "logout", label: "Đăng xuất" }]}
      />
    )

    fireEvent.click(screen.getByRole("button", { name: "Tùy chọn thao tác" }))
    expect(await screen.findByText("admin@example.com")).toBeInTheDocument()
    expect(
      screen.getByRole("menuitem", { name: "Đăng xuất" })
    ).toBeInTheDocument()
  })
})
