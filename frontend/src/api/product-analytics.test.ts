import { beforeEach, describe, expect, it, vi } from "vitest"

import apiClient from "@/api/client"
import {
  getProductInterest,
  getProductUniqueViewers,
  getProductViewTrend,
  getProductViewers,
  getProductViews,
  getTopInterestedCustomers,
  getTrendingProducts,
  recordProductView,
} from "@/api/product-analytics"

vi.mock("@/api/client", () => ({
  default: { get: vi.fn(), post: vi.fn() },
}))

describe("product analytics api", () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it("ghi nhận lượt xem khi Product Detail mở thành công", async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { success: true } })

    await recordProductView("product-view-test")

    expect(apiClient.post).toHaveBeenCalledWith(
      "/products/product-view-test/view"
    )
  })

  it("gửi đúng date filter cho các KPI và danh sách người xem", async () => {
    const signal = new AbortController().signal
    const range = { from: "2026-09-01", to: "2026-09-30" }
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({
        data: {
          product_id: "product-1",
          product_code: "SP001",
          product_name: "Tai nghe",
          total_views: 12,
          unique_viewers: 7,
          from_date: range.from,
          to_date: range.to,
        },
      })
      .mockResolvedValueOnce({ data: { total_views: 12 } })
      .mockResolvedValueOnce({ data: { unique_viewers: 7 } })
      .mockResolvedValueOnce({
        data: { product_id: "product-1", records: [] },
      })

    await getProductInterest("product-1", range, signal)
    await getProductViews("product-1", range, signal)
    await getProductUniqueViewers("product-1", range, signal)
    await getProductViewers("product-1", { ...range, limit: 100 }, signal)

    const dateParams = {
      from_date: "2026-09-01",
      to_date: "2026-09-30",
    }
    expect(apiClient.get).toHaveBeenNthCalledWith(
      1,
      "/analytics/products/product-1/interest",
      { params: dateParams, signal }
    )
    expect(apiClient.get).toHaveBeenNthCalledWith(
      2,
      "/analytics/products/product-1/views",
      { params: dateParams, signal }
    )
    expect(apiClient.get).toHaveBeenNthCalledWith(
      3,
      "/analytics/products/product-1/unique-viewers",
      { params: dateParams, signal }
    )
    expect(apiClient.get).toHaveBeenNthCalledWith(
      4,
      "/analytics/products/product-1/viewers",
      { params: { ...dateParams, limit: 100 }, signal }
    )
  })

  it("đổi schema trend và top customers sang dữ liệu UI", async () => {
    const signal = new AbortController().signal
    const range = { from: "2026-09-01", to: "2026-09-30" }
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({
        data: {
          product_id: "product-1",
          group_by: "day",
          points: [{ period_start: "2026-09-01", views: 8 }],
        },
      })
      .mockResolvedValueOnce({
        data: {
          product_id: "product-1",
          records: [
            {
              customer_id: "customer-1",
              customer_code: "KH001",
              customer_name: "Nguyễn An",
              views: 5,
              last_view_at: "2026-09-20T10:00:00+07:00",
            },
          ],
        },
      })

    const trend = await getProductViewTrend(
      "product-1",
      { ...range, groupBy: "DAY" },
      signal
    )
    const customers = await getTopInterestedCustomers(
      "product-1",
      { ...range, limit: 10 },
      signal
    )

    expect(apiClient.get).toHaveBeenNthCalledWith(
      1,
      "/analytics/products/product-1/trend",
      {
        params: {
          from_date: range.from,
          to_date: range.to,
          group_by: "day",
        },
        signal,
      }
    )
    expect(trend.items).toEqual([{ period: "2026-09-01", views: 8 }])
    expect(customers.items[0]).toMatchObject({
      customerCode: "KH001",
      viewCount: 5,
    })
  })

  it("gửi period_days và đổi schema trending sang dữ liệu UI", async () => {
    const signal = new AbortController().signal
    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        records: [
          {
            product_id: "product-1",
            product_code: "SP001",
            product_name: "Tai nghe",
            current_period_views: 20,
            previous_period_views: 10,
            growth_percent: 100,
            trend_status: "STRONG_TRENDING",
          },
        ],
      },
    })

    const result = await getTrendingProducts("30D", 10, signal)

    expect(apiClient.get).toHaveBeenCalledWith("/analytics/products/trending", {
      params: { period_days: 30, limit: 10 },
      signal,
    })
    expect(result.items[0]).toMatchObject({
      currentViews: 20,
      trendStatus: "STRONG_TRENDING",
    })
  })
})
