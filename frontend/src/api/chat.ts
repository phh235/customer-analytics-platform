import { getAccessToken } from "@/api/access-token"

type ChatStreamPayload = {
  type?: string
  delta?: string
  content?: string
  text?: string
  token?: string
  data?: string
  message?: string
  error?: string
}

const apiBaseUrl = import.meta.env.VITE_API_URL?.replace(/\/$/, "")
const CHAT_STREAM_URL = apiBaseUrl
  ? `${apiBaseUrl}/chat/stream`
  : "/api/v1/chat/stream"

function getErrorMessage(payload: unknown, fallback: string) {
  if (typeof payload !== "object" || payload === null) return fallback

  const record = payload as Record<string, unknown>
  return typeof record.message === "string"
    ? record.message
    : typeof record.detail === "string"
      ? record.detail
      : fallback
}

function readEventData(block: string) {
  const eventName = block
    .split(/\r?\n/)
    .find((line) => line.startsWith("event:"))
    ?.slice(6)
    .trim()
  const rawData = block
    .split(/\r?\n/)
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart())
    .join("\n")

  if (!rawData || rawData === "[DONE]") return null

  try {
    const payload = JSON.parse(rawData) as ChatStreamPayload | string
    if (typeof payload === "string") return payload
    if (eventName === "error" || payload.type === "error" || payload.error) {
      throw new Error(payload.error ?? payload.message ?? "AI stream failed")
    }
    if (payload.type === "done" || payload.type === "complete") return null
    return (
      payload.delta ??
      payload.content ??
      payload.text ??
      payload.token ??
      payload.data ??
      ""
    )
  } catch (error) {
    if (error instanceof SyntaxError) return rawData
    throw error
  }
}

export async function streamChatMessage(
  message: string,
  {
    signal,
    onChunk,
  }: {
    signal?: AbortSignal
    onChunk: (chunk: string) => void
  }
) {
  const accessToken = getAccessToken()
  if (!accessToken) {
    throw new Error("Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
  }

  const response = await fetch(CHAT_STREAM_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ message }),
    signal,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(
      getErrorMessage(payload, `Không thể kết nối AI (${response.status}).`)
    )
  }

  if (!response.body) {
    throw new Error("Phản hồi AI không có nội dung.")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  const processBuffer = (flush = false) => {
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = flush ? "" : (blocks.pop() ?? "")
    const readyBlocks = flush ? blocks.filter(Boolean) : blocks

    for (const block of readyBlocks) {
      const chunk = readEventData(block)
      if (chunk) onChunk(chunk)
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    processBuffer()
  }

  buffer += decoder.decode()
  processBuffer(true)
}
