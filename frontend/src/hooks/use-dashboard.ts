import { useQuery } from "@tanstack/react-query"
import { parseAsString, parseAsStringLiteral, useQueryStates } from "nuqs"
import { getDashboardOptions, getDashboardOverview } from "@/api/dashboard"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"
import { DEFAULT_DASHBOARD_FILTERS } from "@/lib/dashboard"
import type { DashboardFilters } from "@/types/dashboard"

const parsers = {
  period: parseAsStringLiteral([
    "30d",
    "90d",
    "6m",
    "12m",
    "custom",
  ] as const).withDefault("90d"),
  from: parseAsString.withDefault(DEFAULT_DASHBOARD_FILTERS.from),
  to: parseAsString.withDefault(DEFAULT_DASHBOARD_FILTERS.to),
  segment: parseAsString.withDefault("all"),
  potential: parseAsString.withDefault("all"),
  category: parseAsString.withDefault("all"),
  employee: parseAsString.withDefault("all"),
}

export function useDashboard() {
  const [rawFilters, setFilters] = useQueryStates(parsers)
  const filters = rawFilters as DashboardFilters
  const optionsQuery = useQuery({
    queryKey: ["dashboard", "options"],
    queryFn: ({ signal }) => getDashboardOptions(signal),
    staleTime: 5 * 60_000,
    retry: false,
  })
  const query = useQuery({
    queryKey: ["dashboard", "overview", filters],
    queryFn: ({ signal }) => getDashboardOverview(filters, signal),
    staleTime: 60_000,
    retry: false,
  })
  useQueryErrorToast(
    optionsQuery.error,
    "Không thể tải các lựa chọn bộ lọc tổng quan."
  )
  return { filters, setFilters, query, optionsQuery }
}
