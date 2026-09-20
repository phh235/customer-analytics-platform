import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { NuqsTestingAdapter } from "nuqs/adapters/testing"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { DashboardPage } from "@/features/dashboard/dashboard-page"
import {
  exportDashboardCsv,
  getDashboardOptions,
  getDashboardOverview,
} from "@/api/dashboard"
import { useAuthStore } from "@/stores/use-auth-store"
import {
  DEFAULT_DASHBOARD_FILTERS,
  DASHBOARD_EMPLOYEES,
  formatDashboardMoney,
} from "@/lib/dashboard"
import { buildDemoDashboard } from "@/mocks/dashboard"

vi.mock("@/features/dashboard/dashboard-charts", () => ({
  RevenueChart: () => <div>Biểu đồ xu hướng</div>,
  SegmentChart: () => <div>Biểu đồ phân khúc</div>,
  PotentialChart: () => <div>Biểu đồ điểm tiềm năng</div>,
  CategoryChart: () => <div>Biểu đồ sản phẩm</div>,
  PredictionChart: () => <div>Biểu đồ xác suất ML</div>,
  OpportunityMatrixChart: () => <div>Ma trận cơ hội khách hàng</div>,
}))
vi.mock("@/features/dashboard/trending-products", () => ({
  TrendingProducts: () => <div>Sản phẩm xu hướng</div>,
}))
vi.mock("@/api/dashboard", () => ({
  getDashboardOverview: vi.fn(),
  getDashboardOptions: vi.fn(),
  exportDashboardCsv: vi.fn(),
}))

function renderDashboard(searchParams = "") {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  const onUrlUpdate = vi.fn()
  render(
    <QueryClientProvider client={client}>
      <NuqsTestingAdapter
        hasMemory
        searchParams={searchParams}
        onUrlUpdate={onUrlUpdate}
      >
        <DashboardPage />
      </NuqsTestingAdapter>
    </QueryClientProvider>
  )
  return onUrlUpdate
}

describe("Dashboard demo", () => {
  beforeEach(() => {
    vi.mocked(getDashboardOverview).mockImplementation(async (filters) =>
      buildDemoDashboard(filters)
    )
    const dashboard = buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS)
    vi.mocked(getDashboardOptions).mockResolvedValue({
      segments: dashboard.segments.map((segment) => ({
        id: segment.key,
        name: segment.label,
      })),
      potential_levels: [
        { id: "HIGH", name: "Tiềm năng cao (≥ 80)" },
        { id: "POTENTIAL", name: "Tiềm năng (60–79)" },
        { id: "NORMAL", name: "Thông thường (< 60)" },
        { id: "INSUFFICIENT_DATA", name: "Chưa đủ dữ liệu" },
      ],
      categories: dashboard.categories.map((category) => ({
        id: category.id,
        name: category.name,
      })),
      employees: DASHBOARD_EMPLOYEES.map((employee) => ({
        id: employee.value,
        name: employee.label,
      })),
      thresholds: dashboard.potential.thresholds,
      weights: dashboard.potential.weights,
      analysis_date: dashboard.meta.analysis_date,
      max_custom_range_days: 366,
      currency: "VND",
      timezone: "Asia/Ho_Chi_Minh",
    })
    vi.mocked(exportDashboardCsv).mockResolvedValue(new Blob(["date,revenue"]))
    useAuthStore.setState({
      user: {
        id: "demo-admin",
        role_code: "ADMIN",
        permissions: [],
        email: "admin@example.com",
        full_name: "Admin",
        status: "ACTIVE",
        created_at: "2026-09-19",
        last_login_at: null,
      },
    })
  })
  afterEach(() => useAuthStore.setState({ user: null }))

  it("đổi bộ lọc và đặt lại sẽ cập nhật KPI, bảng và URL", async () => {
    const user = userEvent.setup()
    const onUrlUpdate = renderDashboard()
    const total = formatDashboardMoney(
      buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS).metrics.revenue.current
    ).replace(/\s/g, " ")
    expect(await screen.findByText(total)).toBeInTheDocument()
    await user.click(screen.getByRole("combobox", { name: "Mức tiềm năng" }))
    await user.click(screen.getByRole("option", { name: "Chưa đủ dữ liệu" }))
    expect(
      await screen.findByText("Chưa có khách hàng đạt ngưỡng tiềm năng cao.")
    ).toBeInTheDocument()
    await waitFor(() => expect(onUrlUpdate).toHaveBeenCalled())
    expect(screen.queryByText(total)).not.toBeInTheDocument()
    await user.click(screen.getByRole("button", { name: "Xoá bộ lọc" }))
    expect(await screen.findByText(total)).toBeInTheDocument()
  })

  it("hiển thị trạng thái rỗng khi bộ lọc không có khách hàng", async () => {
    renderDashboard("?potential=HIGH&segment=INSUFFICIENT_DATA")
    expect(
      await screen.findByText("Không có dữ liệu phù hợp")
    ).toBeInTheDocument()
    expect(
      screen.getByRole("button", { name: "Xóa bộ lọc" })
    ).toBeInTheDocument()
  })

  it("báo khoảng ngày không hợp lệ và giữ các trường để sửa", async () => {
    renderDashboard("?period=custom&from=2026-09-20&to=2026-09-19")
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Chọn khoảng ngày hợp lệ"
    )
    expect(screen.getByLabelText("Từ ngày")).toHaveValue("2026-09-20")
  })

  it("không hiển thị xuất báo cáo khi không có quyền", async () => {
    useAuthStore.setState({
      user: {
        ...useAuthStore.getState().user!,
        role_code: "SALES",
        permissions: [],
      },
    })
    renderDashboard()
    await screen.findByText("Biểu đồ xu hướng")
    expect(
      screen.queryByRole("button", { name: "Xuất CSV" })
    ).not.toBeInTheDocument()
  })
})
