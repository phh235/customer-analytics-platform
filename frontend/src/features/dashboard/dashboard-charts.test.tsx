import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import {
  OpportunityMatrixChart,
  PredictionChart,
  PotentialChart,
} from "@/features/dashboard/dashboard-charts"
import { buildDemoDashboard } from "@/mocks/dashboard"
import { DEFAULT_DASHBOARD_FILTERS } from "@/lib/dashboard"

describe("Analytics data states", () => {
  it("phân biệt chưa triển khai ML với xác suất bằng 0", () => {
    const data = buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS)
    data.predictions = {
      ...data.predictions,
      status: "not_deployed",
      model_version: null,
      prediction_date: null,
      evaluated_customers: 0,
      distribution: [],
      insufficient_count: data.metrics.customers.current,
    }
    render(<PredictionChart data={data} />)
    expect(
      screen.getByText("Chưa có mô hình được triển khai để dự đoán.")
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText("Biểu đồ phân bố xác suất mua hàng từ ML")
    ).not.toBeInTheDocument()
  })

  it("không vẽ cột điểm 0 cho khách hàng thiếu dữ liệu", () => {
    const data = buildDemoDashboard({
      ...DEFAULT_DASHBOARD_FILTERS,
      potential: "INSUFFICIENT_DATA",
    })
    render(<PotentialChart data={data} />)
    expect(
      screen.getByText("Khách hàng chưa có dữ liệu cần thiết để chấm điểm.")
    ).toBeInTheDocument()
  })

  it("kết hợp điểm tiềm năng và xác suất mua trong ma trận cơ hội", () => {
    const data = buildDemoDashboard(DEFAULT_DASHBOARD_FILTERS)
    render(<OpportunityMatrixChart data={data} />)
    expect(
      screen.getByLabelText(
        "Ma trận điểm tiềm năng và xác suất mua của khách hàng"
      )
    ).toBeInTheDocument()
    expect(screen.getByText(/Kích thước: doanh thu/)).toBeInTheDocument()
  })
})
