import { useEffect, useRef, useState } from "react"
import {
  Maximize2Icon,
  Minimize2Icon,
  RotateCcwIcon,
  XIcon,
} from "lucide-react"

import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation"
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message"
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  type PromptInputMessage,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input"
import { Button } from "@/components/ui/button"
import { CardHeader, CardTitle } from "@/components/ui/card"
import { UserAvatar } from "@/components/common/user-avatar"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { MainLogo } from "@/lib/svg"
import { cn } from "@/lib/utils"
import { streamChatMessage } from "@/api/chat"
import { useAuthStore } from "@/stores/use-auth-store"

type ChatMessage = {
  id: number
  role: "assistant" | "user"
  content: string
  streaming?: boolean
}

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 0,
    role: "assistant",
    content:
      "Xin chào! Tôi là trợ lý AI của 3CS Store. Bạn muốn tìm hiểu về khách hàng, sản phẩm hay giao dịch?",
  },
]

export default function AiChatPanel({
  closing,
  onClose,
}: {
  closing: boolean
  onClose: () => void
}) {
  const currentUser = useAuthStore((state) => state.user)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES)
  const [isStreaming, setIsStreaming] = useState(false)
  const [maximized, setMaximized] = useState(false)
  const messageId = useRef(1)
  const streamController = useRef<AbortController | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(
    () => () => {
      streamController.current?.abort()
    },
    []
  )

  const resetConversation = () => {
    streamController.current?.abort()
    streamController.current = null
    setIsStreaming(false)
    setMessages(INITIAL_MESSAGES)
    setInput("")
    messageId.current = 1
  }

  const handleSubmit = async ({ text }: PromptInputMessage) => {
    const content = text.trim()
    if (!content || isStreaming) return

    const assistantId = messageId.current + 1
    const userMessage: ChatMessage = {
      id: messageId.current++,
      role: "user",
      content,
    }
    const assistantMessage: ChatMessage = {
      id: messageId.current++,
      role: "assistant",
      content: "",
      streaming: true,
    }

    setMessages((current) => [...current, userMessage, assistantMessage])
    setInput("")
    setIsStreaming(true)

    const controller = new AbortController()
    streamController.current = controller

    try {
      await streamChatMessage(content, {
        signal: controller.signal,
        onChunk: (chunk) => {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? { ...message, content: message.content + chunk }
                : message
            )
          )
        },
      })
    } catch (error) {
      const aborted =
        controller.signal.aborted ||
        (error instanceof DOMException && error.name === "AbortError")
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? {
                ...message,
                content:
                  message.content ||
                  (aborted
                    ? "Đã dừng phản hồi."
                    : error instanceof Error
                      ? error.message
                      : "Không thể kết nối với AI."),
              }
            : message
        )
      )
    } finally {
      setMessages((current) =>
        current.map((message) =>
          message.id === assistantId
            ? { ...message, streaming: false }
            : message
        )
      )
      if (streamController.current === controller) {
        streamController.current = null
        setIsStreaming(false)
      }
    }
  }

  const closeChat = () => {
    streamController.current?.abort()
    onClose()
  }

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 size-full shadow-[0_18px_60px_rgba(0,0,0,0.18)] duration-200",
        closing
          ? "pointer-events-none animate-out zoom-out-95 fade-out slide-out-to-bottom-4"
          : "animate-in zoom-in-95 fade-in slide-in-from-bottom-4",
        maximized
          ? "sm:inset-4 sm:size-auto sm:rounded-2xl"
          : "sm:top-auto sm:right-[calc(0.75rem+var(--safe-area-right))] sm:bottom-[calc(1rem+var(--safe-area-bottom))] sm:left-auto sm:h-[min(36rem,calc(100svh-2rem-var(--safe-area-bottom)))] sm:w-96 sm:rounded-2xl"
      )}
    >
      <SquircleCard
        role="dialog"
        aria-label="Trợ lý AI 3CS Store"
        className="h-full rounded-none! border-0! p-0! [--card-clip-handle:0px]! [--card-clip-radius:0px]! sm:rounded-[28px]! sm:border! sm:p-1! sm:[--card-clip-handle:2.5px]! sm:[--card-clip-radius:15px]!"
      >
        <CardHeader className="block px-3 py-2!">
          <div className="grid min-w-0 grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2">
            <MainLogo className="size-7" />
            <div className="min-w-0">
              <CardTitle className="truncate text-sm leading-tight">
                3CS AI
              </CardTitle>
            </div>
            <div className="flex shrink-0 items-center gap-1">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="hidden sm:inline-flex"
                aria-label={
                  maximized ? "Thu nhỏ trợ lý AI" : "Phóng to trợ lý AI"
                }
                aria-pressed={maximized}
                onClick={() => setMaximized((current) => !current)}
              >
                {maximized ? <Minimize2Icon /> : <Maximize2Icon />}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Bắt đầu cuộc trò chuyện mới"
                onClick={resetConversation}
              >
                <RotateCcwIcon />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Đóng trợ lý AI"
                onClick={closeChat}
              >
                <XIcon />
              </Button>
            </div>
          </div>
        </CardHeader>

        <SquircleCardBody className="gap-0 py-0">
          <Conversation className="min-h-0">
            <ConversationContent className="gap-5 p-4">
              {messages.map((message) => (
                <Message from={message.role} key={message.id}>
                  <span
                    aria-label={
                      message.role === "assistant"
                        ? "Tin nhắn từ 3CS AI"
                        : `Tin nhắn của ${currentUser?.full_name ?? "bạn"}`
                    }
                    className={
                      message.role === "assistant"
                        ? "flex size-8 items-center justify-center rounded-full border bg-primary/10"
                        : "ml-auto flex size-8 items-center justify-center"
                    }
                  >
                    {message.role === "assistant" ? (
                      <MainLogo className="size-6" />
                    ) : (
                      <UserAvatar
                        email={currentUser?.email}
                        name={currentUser?.full_name}
                      />
                    )}
                  </span>
                  <MessageContent
                    className={
                      message.role === "assistant"
                        ? "rounded-2xl rounded-bl-md bg-muted px-3 py-2.5"
                        : "rounded-2xl rounded-br-md"
                    }
                  >
                    {message.streaming && !message.content ? (
                      <span className="shimmer text-sm text-muted-foreground">
                        AI đang trả lời…
                      </span>
                    ) : (
                      <MessageResponse>{message.content}</MessageResponse>
                    )}
                  </MessageContent>
                </Message>
              ))}
            </ConversationContent>
            <ConversationScrollButton className="bottom-2" />
          </Conversation>

          <div className="shrink-0 border-t bg-card p-2">
            <PromptInput
              aria-label="Khung nhập câu hỏi cho trợ lý AI"
              onSubmit={handleSubmit}
              onClick={(event) => {
                if ((event.target as HTMLElement).closest("button")) return
                textareaRef.current?.focus()
              }}
              className="**:data-[slot=input-group]:rounded-[16px] **:data-[slot=input-group]:border-0! **:data-[slot=input-group]:bg-transparent! **:data-[slot=input-group]:shadow-none! **:data-[slot=input-group]:ring-0!"
            >
              <PromptInputBody>
                <PromptInputTextarea
                  autoFocus
                  ref={textareaRef}
                  value={input}
                  disabled={isStreaming}
                  onChange={(event) => setInput(event.currentTarget.value)}
                  placeholder="Nhập câu hỏi cho trợ lý AI..."
                  className="max-h-20 min-h-10"
                />
              </PromptInputBody>
              <PromptInputFooter className="justify-end px-1.5 pb-1.5">
                <PromptInputSubmit
                  status={isStreaming ? "streaming" : "ready"}
                  onStop={() => streamController.current?.abort()}
                  disabled={!isStreaming && !input.trim()}
                  aria-label="Gửi tin nhắn"
                />
              </PromptInputFooter>
            </PromptInput>
            <p className="px-2 pt-1 text-center text-[10px] leading-4 text-muted-foreground">
              3CS AI có thể mắc lỗi. Hãy kiểm tra lại thông tin quan trọng.
            </p>
          </div>
        </SquircleCardBody>
      </SquircleCard>
    </div>
  )
}
