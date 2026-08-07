import axios from "axios"

interface ApiErrorDetail {
  field?: string
  issue?: string
  type?: string
  [key: string]: string | number | null | undefined
}

interface ApiErrorResponse {
  code?: number
  message?: string
  error?: string
  path?: string
  timestamp?: number
  details?: ApiErrorDetail[]
  detail?: string | ApiErrorDetail[]
}

const GENERIC_ERROR_MESSAGE = "Đã xảy ra lỗi. Vui lòng thử lại sau."
const SERVER_ERROR_MESSAGE =
  "Hệ thống đang gặp sự cố. Vui lòng thử lại sau ít phút."

function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  return typeof value === "object" && value !== null
}

function getValidationMessage(detail: string | ApiErrorDetail[]) {
  if (typeof detail === "string") return detail

  const messages = detail
    .map((item) => item.issue)
    .filter((message): message is string => Boolean(message))

  return messages.length > 0 ? messages.join(" ") : null
}

export function getApiErrorMessage(
  error: unknown,
  fallbackMessage = GENERIC_ERROR_MESSAGE
) {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error && error.message
      ? error.message
      : fallbackMessage
  }

  const status = error.response?.status
  if (status && status >= 500) return SERVER_ERROR_MESSAGE

  const data = error.response?.data
  if (!isApiErrorResponse(data)) return fallbackMessage

  if (data.message) return data.message

  if (data.detail) {
    return getValidationMessage(data.detail) ?? fallbackMessage
  }

  if (data.details) {
    return getValidationMessage(data.details) ?? fallbackMessage
  }

  return fallbackMessage
}
