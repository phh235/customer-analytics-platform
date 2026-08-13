import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { ConfirmProductStatusDialog } from "@/components/admin/management/confirm-product-status-dialog"

describe("ConfirmProductStatusDialog", () => {
  it("xác nhận hiển thị sản phẩm", async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()

    render(
      <ConfirmProductStatusDialog
        target={{ id: "product-1", name: "Laptop Nova", nextStatus: "active" }}
        onOpenChange={vi.fn()}
        onConfirm={onConfirm}
      />
    )

    expect(screen.getByRole("dialog")).toHaveTextContent("Laptop Nova")
    expect(
      screen.getByRole("button", { name: "Hiển thị sản phẩm" })
    ).toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Hiển thị sản phẩm" }))

    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it("đổi nội dung khi cần ẩn sản phẩm", () => {
    render(
      <ConfirmProductStatusDialog
        target={{
          id: "product-1",
          name: "Laptop Nova",
          nextStatus: "inactive",
        }}
        onOpenChange={vi.fn()}
        onConfirm={vi.fn()}
      />
    )

    expect(
      screen.getByRole("button", { name: "Ẩn sản phẩm" })
    ).toBeInTheDocument()
    expect(screen.getByText(/không còn hiển thị/u)).toBeInTheDocument()
  })
})
