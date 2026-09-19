import { screen, within } from "@testing-library/react"
import { NuqsTestingAdapter } from "nuqs/adapters/testing"
import { describe, expect, it, vi } from "vitest"

import { getProducts, type ProductRecord } from "@/api/products"
import { Component } from "@/pages/admin/categories"
import { renderWithQueryClient } from "@/test/render"

vi.mock("@/api/products", () => ({ getProducts: vi.fn() }))

describe("Danh mục", () => {
  it("hiển thị danh mục tổng hợp từ sản phẩm bằng bảng chung", async () => {
    const product: ProductRecord = {
      id: "1",
      product_code: "SP-01",
      name: "Điện thoại A",
      sku: null,
      category: "Điện thoại",
      description: null,
      image_url: null,
      price: 1000000,
      status: "ACTIVE",
      created_at: "2026-09-01",
      updated_at: "2026-09-19",
    }
    vi.mocked(getProducts).mockResolvedValue({
      current: 1,
      size: 100,
      total: 2,
      pages: 1,
      records: [product, { ...product, id: "2", product_code: "SP-02" }],
    })
    renderWithQueryClient(
      <NuqsTestingAdapter>
        <Component />
      </NuqsTestingAdapter>
    )
    expect(
      await screen.findByText("Hiển thị 1–1 / 1 danh mục")
    ).toBeInTheDocument()
    const table = screen.getByRole("table", { name: "Danh sách danh mục" })
    expect(within(table).getByText("2 sản phẩm")).toBeInTheDocument()
    expect(within(table).getByText("19/09/2026")).toBeInTheDocument()
  })
})
