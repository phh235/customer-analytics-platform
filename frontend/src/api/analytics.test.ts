import { describe, expect, it, vi } from "vitest"

import apiClient from "@/api/client"
import { getModels, getSegments, type SegmentRecord } from "@/api/analytics"

vi.mock("@/api/client", () => ({ default: { get: vi.fn() } }))

const segment = (id: string): SegmentRecord => ({
  customer_id: id,
  customer_code: `KH${id.padStart(3, "0")}`,
  name: `Khách ${id}`,
  segment_type: "HIGH_VALUE",
  potential_score: 86.8,
  reason: "Potential score is at least 80.",
  calculated_at: "2026-09-19T15:18:53Z",
})

describe("analytics paginated api", () => {
  it("giữ nguyên response phân trang và gửi search lên API", async () => {
    const response = {
      current: 2,
      size: 10,
      total: 80,
      pages: 8,
      records: [segment("1")],
    }
    vi.mocked(apiClient.get).mockResolvedValue({ data: response })

    await expect(
      getSegments({ page: 2, size: 10, search: "Vũ Văn" })
    ).resolves.toEqual(response)
    expect(apiClient.get).toHaveBeenCalledWith("/analytics/segments", {
      params: expect.objectContaining({
        page: 2,
        size: 10,
        search: "Vũ Văn",
      }),
    })
  })

  it("chuẩn hóa endpoint array cũ để CommonTable luôn nhận records", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: Array.from({ length: 12 }, (_, index) => segment(`${index + 1}`)),
    })

    const result = await getSegments({ page: 2, size: 10 })
    expect(result).toMatchObject({ current: 2, total: 12, pages: 2 })
    expect(result.records).toHaveLength(2)
  })

  it("gửi page, size và search cho danh sách mô hình", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: { current: 1, size: 10, total: 0, pages: 1, records: [] },
    })

    await getModels({ page: 1, size: 10, search: "random forest" })
    expect(apiClient.get).toHaveBeenCalledWith("/analytics/models", {
      params: { page: 1, size: 10, search: "random forest" },
    })
  })
})
