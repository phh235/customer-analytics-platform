import { afterEach, describe, expect, it, vi } from "vitest"

import { clearAccessToken, setAccessToken } from "@/api/access-token"
import { streamChatMessage } from "@/api/chat"

describe("streamChatMessage", () => {
  afterEach(() => {
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("gửi bearer token và ghép các SSE chunk", async () => {
    setAccessToken("test-token")
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"delta":"Xin"}\n\n'))
        controller.enqueue(encoder.encode('data: {"content":" chào"}\n\n'))
        controller.enqueue(encoder.encode("data: [DONE]\n\n"))
        controller.close()
      },
    })
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(stream, {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      })
    )
    vi.stubGlobal("fetch", fetchMock)
    const chunks: string[] = []

    await streamChatMessage("Xin chào", {
      onChunk: (chunk) => chunks.push(chunk),
    })

    expect(chunks).toEqual(["Xin", " chào"])
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/v1\/chat\/stream$/),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Accept: "text/event-stream",
          Authorization: "Bearer test-token",
        }),
        body: JSON.stringify({ message: "Xin chào" }),
      })
    )
  })
})
