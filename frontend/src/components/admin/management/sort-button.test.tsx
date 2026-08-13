import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { SortButton } from "@/components/admin/management/sort-button"

describe("SortButton", () => {
  it("gọi callback khi người dùng chọn cột", async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()

    render(
      <SortButton
        label="Tên sản phẩm"
        sortKey="name"
        activeKey="price"
        direction="asc"
        onClick={onClick}
      />
    )

    const button = screen.getByRole("button", { name: "Tên sản phẩm" })

    expect(button).toBeEnabled()
    await user.click(button)

    expect(onClick).toHaveBeenCalledOnce()
  })

  it("vẫn hiển thị nút khi cột đang được sắp xếp", () => {
    render(
      <SortButton
        label="Giá"
        sortKey="price"
        activeKey="price"
        direction="desc"
        onClick={vi.fn()}
      />
    )

    const button = screen.getByRole("button", { name: "Giá" })

    expect(button.querySelector("svg")).toBeInTheDocument()
  })
})
