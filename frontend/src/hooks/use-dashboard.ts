import { useQuery } from "@tanstack/react-query"
import { parseAsString, parseAsStringLiteral, useQueryStates } from "nuqs"
import { getDashboardOverview } from "@/api/dashboard"
import { DEFAULT_DASHBOARD_FILTERS } from "@/lib/dashboard"

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
  segment: parseAsStringLiteral([
    "all",
    "HIGH_VALUE",
    "LOYAL",
    "AT_RISK",
    "POTENTIAL",
    "NEW_CUSTOMER",
    "NORMAL",
    "INSUFFICIENT_DATA",
  ] as const).withDefault("all"),
  potential: parseAsStringLiteral([
    "all",
    "HIGH",
    "POTENTIAL",
    "NORMAL",
    "INSUFFICIENT_DATA",
  ] as const).withDefault("all"),
  category: parseAsStringLiteral([
    "all",
    "phone",
    "laptop",
    "accessories",
    "home",
    "audio",
  ] as const).withDefault("all"),
  employee: parseAsStringLiteral([
    "all",
    "nv-01",
    "nv-02",
    "nv-03",
    "nv-04",
  ] as const).withDefault("all"),
}

export function useDashboard() {
  const [filters, setFilters] = useQueryStates(parsers)
  const query = useQuery({
    queryKey: ["dashboard", "demo", filters],
    queryFn: ({ signal }) => getDashboardOverview(filters, signal),
    staleTime: 60_000,
    retry: false,
  })
  return { filters, setFilters, query }
}
