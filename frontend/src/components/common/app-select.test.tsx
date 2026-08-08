import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import { AppSelect } from "@/components/common/app-select"

describe("AppSelect", () => {
  it("mở danh sách và trả về value khi chọn option", async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(
      <AppSelect
        aria-label="Danh mục"
        defaultValue="all"
        onChange={onChange}
        options={[
          { value: "all", label: "Tất cả danh mục" },
          { value: "laptop", label: "Laptop" },
        ]}
      />
    )

    const trigger = screen.getByRole("combobox", { name: "Danh mục" })

    expect(trigger).toHaveTextContent("Tất cả danh mục")

    await user.click(trigger)
    await user.click(screen.getByRole("option", { name: "Laptop" }))

    expect(onChange).toHaveBeenCalledWith("laptop")
    expect(trigger).toHaveTextContent("Laptop")
  })
})
