import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { AiChatWidget } from "@/components/ai-chat-widget"
import { streamChatMessage } from "@/api/chat"

vi.mock("@/api/chat", () => ({ streamChatMessage: vi.fn() }))

describe("AiChatWidget", () => {
  beforeEach(() => {
    vi.mocked(streamChatMessage).mockImplementation(
      async (_message, { onChunk }) => {
        onChunk("Đây là phản hồi từ AI.")
      }
    )
  })

  it("mở chat, gửi tin nhắn mẫu, làm mới và đóng panel", async () => {
    const user = userEvent.setup()
    render(<AiChatWidget />)

    await user.click(screen.getByRole("button", { name: "Mở trợ lý AI" }))
    expect(
      await screen.findByRole(
        "dialog",
        { name: "Trợ lý AI 3CS Store" },
        { timeout: 10_000 }
      )
    ).toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Phóng to trợ lý AI" }))
    expect(
      screen.getByRole("button", { name: "Thu nhỏ trợ lý AI" })
    ).toHaveAttribute("aria-pressed", "true")
    await user.click(screen.getByRole("button", { name: "Thu nhỏ trợ lý AI" }))

    const input = screen.getByPlaceholderText("Nhập câu hỏi cho trợ lý AI...")
    input.blur()
    await user.click(
      screen.getByRole("form", {
        name: "Khung nhập câu hỏi cho trợ lý AI",
      })
    )
    expect(input).toHaveFocus()
    await user.type(input, "Khách hàng nào có điểm tiềm năng cao?")
    await user.click(screen.getByRole("button", { name: "Gửi tin nhắn" }))

    expect(
      screen.getByText("Khách hàng nào có điểm tiềm năng cao?")
    ).toBeInTheDocument()
    expect(
      await screen.findByText("Đây là phản hồi từ AI.")
    ).toBeInTheDocument()
    expect(streamChatMessage).toHaveBeenCalledWith(
      "Khách hàng nào có điểm tiềm năng cao?",
      expect.objectContaining({
        signal: expect.any(AbortSignal),
        onChunk: expect.any(Function),
      })
    )

    await user.click(
      screen.getByRole("button", { name: "Bắt đầu cuộc trò chuyện mới" })
    )
    expect(
      screen.queryByText("Khách hàng nào có điểm tiềm năng cao?")
    ).not.toBeInTheDocument()

    await user.click(screen.getByRole("button", { name: "Đóng trợ lý AI" }))
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Mở trợ lý AI" })).toBeVisible()
    )
  })
})
