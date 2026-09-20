import type {
  DashboardFilters,
  DashboardSegment,
  PotentialLevel,
} from "@/types/dashboard"

export const DEMO_ANALYSIS_DATE = "2026-09-19"
export const DEFAULT_DASHBOARD_FILTERS: DashboardFilters = {
  period: "90d",
  from: "2026-06-22",
  to: DEMO_ANALYSIS_DATE,
  segment: "all",
  potential: "all",
  category: "all",
  employee: "all",
}

export const DASHBOARD_SEGMENTS: Record<DashboardSegment, string> = {
  HIGH_VALUE: "Giá trị cao",
  LOYAL: "Trung thành",
  AT_RISK: "Nguy cơ rời bỏ",
  POTENTIAL: "Tiềm năng",
  NEW_CUSTOMER: "Khách hàng mới",
  NORMAL: "Thông thường",
  INSUFFICIENT_DATA: "Chưa đủ dữ liệu",
}
export const DASHBOARD_POTENTIAL_LEVELS: Record<PotentialLevel, string> = {
  HIGH: "Tiềm năng cao",
  POTENTIAL: "Tiềm năng",
  NORMAL: "Thông thường",
  INSUFFICIENT_DATA: "Chưa đủ dữ liệu",
}

export const getDashboardSegmentLabel = (value: string, fallback = value) =>
  DASHBOARD_SEGMENTS[value as DashboardSegment] ?? fallback

export const getDashboardPotentialLabel = (value: string, fallback = value) =>
  DASHBOARD_POTENTIAL_LEVELS[value as PotentialLevel] ?? fallback

export const DASHBOARD_CATEGORIES = [
  { value: "phone", label: "Điện thoại" },
  { value: "laptop", label: "Laptop" },
  { value: "accessories", label: "Phụ kiện" },
  { value: "home", label: "Gia dụng" },
  { value: "audio", label: "Thiết bị âm thanh" },
]
export const DASHBOARD_EMPLOYEES = [
  { value: "nv-01", label: "Nguyễn Ngọc Mai" },
  { value: "nv-02", label: "Trần Minh Đức" },
  { value: "nv-03", label: "Lê Thu Trang" },
  { value: "nv-04", label: "Phạm Quốc Huy" },
]

export const formatDashboardNumber = (value: number) =>
  new Intl.NumberFormat("vi-VN").format(value)
export const formatDashboardMoney = (value: number) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(value)
export const formatCompactMoney = (value: number) =>
  new Intl.NumberFormat("vi-VN", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value)
export const formatDashboardDate = (value: string) =>
  new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(value))
export const formatShortDate = (value: string) =>
  new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    timeZone: "UTC",
  }).format(new Date(value))

export function shiftDate(date: string, days: number) {
  const value = new Date(`${date}T00:00:00Z`)
  value.setUTCDate(value.getUTCDate() + days)
  return value.toISOString().slice(0, 10)
}

export function getDashboardRange(filters: DashboardFilters) {
  if (filters.period === "custom") {
    const validDate = (value: string) =>
      /^\d{4}-\d{2}-\d{2}$/.test(value) &&
      !Number.isNaN(Date.parse(value)) &&
      new Date(value).toISOString().slice(0, 10) === value
    if (
      !validDate(filters.from) ||
      !validDate(filters.to) ||
      filters.from > filters.to ||
      filters.to > DEMO_ANALYSIS_DATE
    ) {
      throw new Error(
        "Chọn khoảng ngày hợp lệ, không vượt quá ngày chốt dữ liệu 19/09/2026."
      )
    }
    if ((Date.parse(filters.to) - Date.parse(filters.from)) / 86400000 >= 366) {
      throw new Error("Khoảng thời gian tối đa 366 ngày.")
    }
    return { from: filters.from, to: filters.to }
  }
  const to = DEMO_ANALYSIS_DATE
  if (filters.period === "30d" || filters.period === "90d") {
    return { from: shiftDate(to, filters.period === "30d" ? -29 : -89), to }
  }
  const start = new Date(`${to}T00:00:00Z`)
  start.setUTCMonth(start.getUTCMonth() - (filters.period === "6m" ? 6 : 12))
  return { from: shiftDate(start.toISOString().slice(0, 10), 1), to }
}
