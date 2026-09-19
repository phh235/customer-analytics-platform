import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router"
import { describe, expect, it } from "vitest"

import { ProductCard } from "@/components/product-card"

describe("ProductCard", () => {
  it("hiển thị thông tin sản phẩm và liên kết đến trang chi tiết", () => {
    render(
      <MemoryRouter>
        <ProductCard
          product={{
            id: "urban-run",
            name: "Giày thể thao Urban Run",
            category: "Giày dép",
            price: 1290000,
            product_code: "SP-001",
            sku: "UR-001",
            status: "ACTIVE",
            created_at: "2026-09-19T08:00:00Z",
            updated_at: "2026-09-19T08:00:00Z",
            description: "Mô tả chi tiết",
            image_url: "/images/urban-run.jpg",
          }}
        />
      </MemoryRouter>
    )

    const link = screen.getByRole("link", {
      name: "Xem chi tiết Giày thể thao Urban Run",
    })

    expect(link).toHaveAttribute("href", "/products/urban-run")
    expect(
      screen.getByRole("img", { name: "Giày thể thao Urban Run" })
    ).toHaveAttribute("src", "/images/urban-run.jpg")
    expect(screen.getByText("1.290.000", { exact: false })).toBeInTheDocument()
    expect(screen.getByText("Giày dép")).toBeInTheDocument()
  })

  it("hiển thị placeholder khi sản phẩm chưa có ảnh", () => {
    render(
      <MemoryRouter>
        <ProductCard
          product={{
            id: "no-image",
            name: "Sản phẩm chưa có ảnh",
            category: "Phụ kiện",
            price: 100000,
            product_code: "SP-002",
            sku: null,
            status: "ACTIVE",
            created_at: "2026-09-19T08:00:00Z",
            updated_at: "2026-09-19T08:00:00Z",
            description: null,
            image_url: null,
          }}
        />
      </MemoryRouter>
    )

    expect(
      screen.getByRole("img", { name: "Chưa có ảnh Sản phẩm chưa có ảnh" })
    ).toBeInTheDocument()
  })
})
