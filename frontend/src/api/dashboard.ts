import { buildDemoDashboard } from "@/mocks/dashboard"
import type { DashboardFilters, DashboardOverview } from "@/types/dashboard"

// Explicit demo adapter. Replace only this function with the agreed BE endpoint.
// Do not silently fall back to mock data when a real API request fails.
export async function getDashboardOverview(
  filters: DashboardFilters,
  signal?: AbortSignal
): Promise<DashboardOverview> {
  signal?.throwIfAborted()
  return buildDemoDashboard(filters)
}
