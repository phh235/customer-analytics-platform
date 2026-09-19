import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { ProductFormSheet } from "@/components/admin/management/product-form-sheet"

describe("ProductFormSheet", () => {
  it("định dạng giá khi nhập và chuyển về number lúc lưu", async () => {
    const user = userEvent.setup()
    const onSave = vi.fn()

    render(
      <ProductFormSheet
        open
        product={null}
        categories={["Điện thoại"]}
        onOpenChange={vi.fn()}
        onSave={onSave}
      />
    )

    await user.type(
      screen.getByLabelText("Tên sản phẩm"),
      "  Điện thoại Nova  "
    )
    await user.type(screen.getByLabelText("Mã SKU"), "  NOVA-1  ")
    await user.type(screen.getByLabelText("Giá bán (VNĐ)"), "1290000")

    expect(screen.getByLabelText("Giá bán (VNĐ)")).toHaveValue("1,290,000")

    await user.click(screen.getByRole("button", { name: "Thêm sản phẩm" }))

    expect(onSave).toHaveBeenCalledWith({
      name: "Điện thoại Nova",
      sku: "NOVA-1",
      category: "Điện thoại",
      price: 1290000,
      status: "active",
      image: null,
    })
  })
})
