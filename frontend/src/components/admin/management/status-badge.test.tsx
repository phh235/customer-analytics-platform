import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { StatusBadge } from "@/components/admin/management/status-badge"

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
