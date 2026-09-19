import apiClient from "@/api/client"
import type {
  DashboardFilters,
  DashboardOptions,
  DashboardOverview,
} from "@/types/dashboard"

const getDashboardParams = (filters: DashboardFilters) => ({
  period: filters.period,
  from: filters.period === "custom" ? filters.from : undefined,
  to: filters.period === "custom" ? filters.to : undefined,
  segment: filters.segment,
  potential: filters.potential,
  category: filters.category,
  employee: filters.employee,
})

export async function getDashboardOverview(
  filters: DashboardFilters,
  signal?: AbortSignal
) {
  const { data } = await apiClient.get<DashboardOverview>(
    "/analytics/dashboard/overview",
    { params: getDashboardParams(filters), signal }
  )
  return data
}

export async function getDashboardOptions(signal?: AbortSignal) {
  const { data } = await apiClient.get<DashboardOptions>(
    "/analytics/dashboard/options",
    { signal }
  )
  return data
}

export async function exportDashboardCsv(filters: DashboardFilters) {
  const { data } = await apiClient.get<Blob>(
    "/analytics/dashboard/export.csv",
    {
      params: getDashboardParams(filters),
      responseType: "blob",
    }
  )
  return data
}
