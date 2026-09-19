import { describe, expect, it, vi } from "vitest"

import apiClient from "@/api/client"
import { getOrders } from "@/api/orders"

vi.mock("@/api/client", () => ({ default: { get: vi.fn() } }))

describe("orders api", () => {
  it("gửi page, size và search đã chuẩn hóa", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: { current: 2, size: 10, total: 20, pages: 2, records: [] },
    })

    await getOrders({ page: 2, size: 10, search: "  DH00152  " })
    expect(apiClient.get).toHaveBeenCalledWith("/orders", {
      params: { page: 2, size: 10, search: "DH00152" },
    })
  })
})
