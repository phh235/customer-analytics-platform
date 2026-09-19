import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import {
  OrderStatusBadge,
  StatusBadge,
} from "@/components/admin/management/status-badge"

describe("StatusBadge", () => {
  it.each([
    ["active", "product", "Đang bán"],
    ["inactive", "product", "Tạm ẩn"],
    ["active", "customer", "Đang hoạt động"],
    ["inactive", "customer", "Không hoạt động"],
  ] as const)("hiển thị đúng nhãn cho %s %s", (status, entity, label) => {
    render(<StatusBadge status={status} entity={entity} />)

    expect(screen.getByText(label)).toBeInTheDocument()
  })
})

describe("OrderStatusBadge", () => {
  it.each([
    ["delivered", "Đã giao", "success"],
    ["processing", "Đang xử lý", "warning"],
    ["paid", "Đã thanh toán", "info"],
    ["canceled", "Đã huỷ", "destructive"],
    ["CANCELLED", "Đã huỷ", "destructive"],
  ])("hiển thị %s với màu semantic", (status, label, variant) => {
    render(<OrderStatusBadge status={status} />)
    expect(screen.getByText(label)).toHaveAttribute("data-variant", variant)
  })
})
