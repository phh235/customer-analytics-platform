import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import {
  PotentialLevelBadge,
  SegmentBadge,
} from "@/components/admin/management/analytics-status-badge"

describe("SegmentBadge", () => {
  it.each([
    ["AT_RISK", "Có nguy cơ rời bỏ", "bg-red-100"],
    ["HIGH_VALUE", "Khách hàng giá trị cao", "bg-emerald-100"],
    ["POTENTIAL", "Khách hàng tiềm năng", "bg-blue-100"],
  ])("hiển thị màu theo phân khúc %s", (segment, label, colorClass) => {
    render(<SegmentBadge segment={segment} />)
    expect(screen.getByText(label)).toHaveClass(colorClass)
  })
})

describe("PotentialLevelBadge", () => {
  it.each([
    ["HIGH", "Tiềm năng cao", "success"],
    ["POTENTIAL", "Tiềm năng", "warning"],
    ["NORMAL", "Bình thường", "info"],
    ["INSUFFICIENT_DATA", "Chưa đủ dữ liệu", "outline"],
  ])("hiển thị màu theo mức %s", (level, label, variant) => {
    render(<PotentialLevelBadge level={level} />)
    expect(screen.getByText(label)).toHaveAttribute("data-variant", variant)
  })
})
