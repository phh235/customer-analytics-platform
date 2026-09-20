import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  useQueryStates,
} from "nuqs"

import type { PurchasePredictionRecord } from "@/api/analytics"
import { ProbabilityValue } from "@/components/admin/management/probability-value"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { TableSearch } from "@/components/common/table-search"
import { UserAvatar } from "@/components/common/user-avatar"
import { useDebounce } from "@/hooks/use-debounce"
import { formatDate } from "@/lib/date"
import { usePurchasePredictions } from "@/hooks/use-analytics"

const PAGE_SIZE = 10

export const Component = () => {
  const [{ page, search }, setQuery] = useQueryStates(
    {
      page: parseAsInteger.withDefault(1),
      search: parseAsString.withDefault(""),
    },
    { urlKeys: { search: "q" } }
  )
  const debouncedSearch = useDebounce(search, 300)
  const predictionsQuery = usePurchasePredictions({
    page,
    size: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const predictions = predictionsQuery.data?.records ?? []
  const total = predictionsQuery.data?.total ?? 0
  const pages = predictionsQuery.data?.pages ?? 1

  const columns: CommonTableColumn<PurchasePredictionRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      className: "min-w-52",
      cell: (prediction) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={prediction.name} />
          <div className="min-w-0">
            <p className="truncate font-medium">{prediction.name}</p>
            <p className="text-xs text-muted-foreground">
              {prediction.customer_code}
            </p>
          </div>
        </div>
      ),
    },
    {
      id: "purchase_probability",
      header: "Xác suất mua lại",
      cell: (prediction) => (
        <ProbabilityValue value={prediction.purchase_probability} />
      ),
    },
    {
      id: "prediction_horizon_days",
      header: "Khoảng dự báo",
      cell: (prediction) => `${prediction.prediction_horizon_days} ngày`,
    },
    {
      id: "prediction_date",
      header: "Ngày dự báo",
      cell: (prediction) => formatDate(prediction.prediction_date),
    },
    {
      id: "model_version",
      header: "Mô hình",
      cell: (prediction) => prediction.model_version,
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Dự đoán mua lại</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Dự đoán xác suất khách hàng mua lại trong 90 ngày tiếp theo.
        </p>
      </header>

      <TableSearch
        value={search}
        onChange={(value) => {
          void setQuery(
            { search: value, page: 1 },
            { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
          )
        }}
        placeholder="Tìm khách hàng, xác suất, mô hình..."
        ariaLabel="Tìm kiếm dự đoán mua lại"
      />

      <section aria-label="Danh sách khách hàng">
        <CommonTable
          data={predictions}
          columns={columns}
          loading={predictionsQuery.isPending}
          getRowId={(prediction) => prediction.customer_id}
          itemLabel="khách hàng"
          pagination={{
            page,
            pageSize: PAGE_SIZE,
            total,
            totalPages: pages,
            onPageChange: (nextPage) => void setQuery({ page: nextPage }),
          }}
        />
      </section>
    </div>
  )
}

export default Component
