import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { ProbabilityValue } from "@/components/admin/management/probability-value"

describe("ProbabilityValue", () => {
  it.each([
    [0.6, "60.0%", "text-emerald-600"],
    [0.4, "40.0%", "text-emerald-600"],
    [0.399, "39.9%", "text-destructive"],
  ])("hiển thị màu theo xác suất %s", (value, label, colorClass) => {
    render(<ProbabilityValue value={value} />)
    const probability = screen.getByText(label)

    if (value >= 0.6 || value < 0.4) {
      expect(probability).toHaveClass(colorClass)
    } else {
      expect(probability).not.toHaveClass(colorClass)
    }
  })

  it("hiển thị trạng thái thiếu dữ liệu", () => {
    render(<ProbabilityValue value={null} />)
    expect(screen.getByText("Chưa đủ dữ liệu")).toBeInTheDocument()
  })
})
