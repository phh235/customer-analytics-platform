import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { ConfirmDeleteDialog } from "@/components/admin/management/confirm-delete-dialog"

describe("ConfirmDeleteDialog", () => {
  it("gọi callback xác nhận hoặc đóng dialog", async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    const onOpenChange = vi.fn()

    render(
      <ConfirmDeleteDialog
        target={{ type: "product", id: "product-1", name: "Laptop Nova" }}
        onOpenChange={onOpenChange}
        onConfirm={onConfirm}
      />
    )

    expect(screen.getByRole("dialog")).toHaveTextContent("Laptop Nova")

    await user.click(screen.getByRole("button", { name: "Huỷ" }))
    await user.click(screen.getByRole("button", { name: "Xác nhận xoá" }))

    expect(onOpenChange).toHaveBeenCalledWith(false)
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it("đổi nội dung xác nhận khi vô hiệu hóa tài khoản", () => {
    render(
      <ConfirmDeleteDialog
        target={{ type: "user", id: "user-1", name: "Nguyễn An" }}
        onOpenChange={vi.fn()}
        onConfirm={vi.fn()}
      />
    )

    expect(
      screen.getByRole("heading", {
        name: "Xác nhận vô hiệu hóa tài khoản",
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole("button", { name: "Vô hiệu hóa" })
    ).toBeInTheDocument()
  })
})
