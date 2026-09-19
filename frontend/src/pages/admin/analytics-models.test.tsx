import { screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { getModels, trainModel, deployModel } from "@/api/analytics"
import { Component } from "@/pages/admin/analytics-models"
import { renderWithQueryClient } from "@/test/render"

vi.mock("@/api/analytics", () => ({
  getModels: vi.fn(),
  trainModel: vi.fn(),
  deployModel: vi.fn(),
}))

describe("Quản lý mô hình", () => {
  beforeEach(() => {
    vi.mocked(getModels).mockResolvedValue([])
    vi.mocked(trainModel).mockResolvedValue(
      {} as Awaited<ReturnType<typeof trainModel>>
    )
  })

  it("chọn loại mô hình bằng AppSelect và gửi đúng dữ liệu huấn luyện", async () => {
    const user = userEvent.setup()
    renderWithQueryClient(<Component />)
    await screen.findByText("Chưa có mô hình nào được đăng ký.")
    await user.click(screen.getByRole("combobox", { name: "Loại mô hình" }))
    await user.click(screen.getByRole("option", { name: "Rừng ngẫu nhiên" }))
    expect(
      screen.getByRole("combobox", { name: "Loại mô hình" })
    ).toHaveTextContent("Rừng ngẫu nhiên")
    await user.click(
      screen.getByRole("button", { name: "Huấn luyện và đánh giá" })
    )
    await waitFor(() =>
      expect(trainModel).toHaveBeenCalledWith(
        expect.objectContaining({
          model_type: "RANDOM_FOREST",
          feature_window_days: 365,
          prediction_horizon_days: 90,
        })
      )
    )
    expect(deployModel).not.toHaveBeenCalled()
  })
})
