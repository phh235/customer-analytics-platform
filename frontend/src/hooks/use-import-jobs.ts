import { queryOptions, useQuery } from "@tanstack/react-query"

import { getImportJobs } from "@/api/import-data"
import { useQueryErrorToast } from "@/hooks/use-query-error-toast"

export const importJobQueryKeys = {
  all: ["import-jobs"] as const,
  list: (page: number, size: number) => ["import-jobs", page, size] as const,
}

export function useImportJobs(page: number, size: number) {
  const query = useQuery(
    queryOptions({
      queryKey: importJobQueryKeys.list(page, size),
      queryFn: () => getImportJobs(page, size),
    })
  )
  useQueryErrorToast(query.error, "Không thể tải lịch sử nhập dữ liệu.")
  return query
}
