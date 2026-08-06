import dayjs, { type ConfigType } from "dayjs"
import relativeTime from "dayjs/plugin/relativeTime"
import "dayjs/locale/vi"

dayjs.extend(relativeTime)
dayjs.locale("vi")

export const DATE_FORMATS = {
  date: "DD/MM/YYYY",
  dateTime: "DD/MM/YYYY HH:mm",
  apiDate: "YYYY-MM-DD",
  time: "HH:mm",
} as const

type DateInput = ConfigType | null | undefined

function toValidDate(value: DateInput) {
  if (value == null || value === "") return null

  const date = dayjs(value)
  return date.isValid() ? date : null
}

export function isValidDate(value: DateInput) {
  return toValidDate(value) !== null
}

export function formatDate(
  value: DateInput,
  format: string = DATE_FORMATS.date,
  fallback = "—"
) {
  return toValidDate(value)?.format(format) ?? fallback
}

export function formatDateTime(value: DateInput, fallback = "—") {
  return formatDate(value, DATE_FORMATS.dateTime, fallback)
}

export function formatTime(value: DateInput, fallback = "—") {
  return formatDate(value, DATE_FORMATS.time, fallback)
}

export function formatApiDate(value: DateInput, fallback = "") {
  return formatDate(value, DATE_FORMATS.apiDate, fallback)
}

export function formatRelativeTime(value: DateInput, fallback = "—") {
  return toValidDate(value)?.fromNow() ?? fallback
}

export function formatDateRange(
  start: DateInput,
  end: DateInput,
  format: string = DATE_FORMATS.date,
  separator = " – ",
  fallback = "—"
) {
  const startDate = toValidDate(start)
  const endDate = toValidDate(end)

  if (!startDate || !endDate) return fallback
  if (startDate.isSame(endDate, "day")) return startDate.format(format)

  return `${startDate.format(format)}${separator}${endDate.format(format)}`
}
