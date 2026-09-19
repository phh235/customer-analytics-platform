import { describe, expect, it, vi } from "vitest"

import apiClient from "@/api/client"
import {
  exportDashboardCsv,
  getDashboardOptions,
  getDashboardOverview,
} from "@/api/dashboard"
import { DEFAULT_DASHBOARD_FILTERS } from "@/lib/dashboard"

vi.mock("@/api/client", () => ({
  default: { get: vi.fn() },
}))

describe("dashboard api", () => {
  it("gọi overview và chỉ gửi ngày khi dùng khoảng tùy chọn", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { metrics: {} } })

    await getDashboardOverview(DEFAULT_DASHBOARD_FILTERS)
    expect(apiClient.get).toHaveBeenCalledWith(
      "/analytics/dashboard/overview",
      expect.objectContaining({
        params: expect.objectContaining({
          period: "90d",
          from: undefined,
          to: undefined,
        }),
      })
    )

    await getDashboardOverview({
      ...DEFAULT_DASHBOARD_FILTERS,
      period: "custom",
    })
    expect(apiClient.get).toHaveBeenLastCalledWith(
      "/analytics/dashboard/overview",
      expect.objectContaining({
        params: expect.objectContaining({
          from: DEFAULT_DASHBOARD_FILTERS.from,
          to: DEFAULT_DASHBOARD_FILTERS.to,
        }),
      })
    )
  })

  it("gọi options và export CSV đúng endpoint", async () => {
    const blob = new Blob(["date,revenue"])
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({ data: { segments: [] } })
      .mockResolvedValueOnce({ data: blob })

    await getDashboardOptions()
    expect(apiClient.get).toHaveBeenCalledWith("/analytics/dashboard/options", {
      signal: undefined,
    })

    await expect(exportDashboardCsv(DEFAULT_DASHBOARD_FILTERS)).resolves.toBe(
      blob
    )
    expect(apiClient.get).toHaveBeenLastCalledWith(
      "/analytics/dashboard/export.csv",
      expect.objectContaining({ responseType: "blob" })
    )
  })
})
