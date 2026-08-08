import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { CategoryFormSheet } from "@/components/admin/management/category-form-sheet"

describe("CategoryFormSheet", () => {
  it("trim dữ liệu trước khi gọi onSave", async () => {
    const user = userEvent.setup()
    const onSave = vi.fn()

    render(
      <CategoryFormSheet
        open
        category={null}
        onOpenChange={vi.fn()}
        onSave={onSave}
      />
    )

    await user.type(screen.getByLabelText("Tên danh mục"), "  Điện thoại  ")
    await user.type(screen.getByLabelText("Mã danh mục"), "  PHONE  ")
    await user.click(screen.getByRole("button", { name: "Thêm danh mục" }))

    expect(onSave).toHaveBeenCalledWith({
      name: "Điện thoại",
      code: "PHONE",
    })
  })

  it("nạp dữ liệu hiện tại khi chỉnh sửa", async () => {
    render(
      <CategoryFormSheet
        open
        category={{
          id: "cat-1",
          code: "PHONE",
          name: "Điện thoại",
          productCount: 4,
          updatedAt: "2026-08-01",
        }}
        onOpenChange={vi.fn()}
        onSave={vi.fn()}
      />
    )

    await waitFor(() => {
      expect(screen.getByLabelText("Tên danh mục")).toHaveValue("Điện thoại")
      expect(screen.getByLabelText("Mã danh mục")).toHaveValue("PHONE")
    })
    expect(
      screen.getByRole("button", { name: "Lưu thay đổi" })
    ).toBeInTheDocument()
  })
})
