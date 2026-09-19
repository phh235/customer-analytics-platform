import { useState } from "react"

import type { PurchasePredictionRecord } from "@/api/analytics"
import { ProbabilityValue } from "@/components/admin/management/probability-value"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { UserAvatar } from "@/components/common/user-avatar"
import { formatDate } from "@/lib/date"
import { usePurchasePredictions } from "@/hooks/use-analytics"

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
  const predictionsQuery = usePurchasePredictions()
  const predictions = predictionsQuery.data ?? []

  const columns: CommonTableColumn<PurchasePredictionRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      className: "min-w-52",
      cell: (prediction) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={prediction.name} />
          <span>{prediction.name}</span>
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

      <section aria-label="Danh sách khách hàng">
        <CommonTable
          data={predictions}
          columns={columns}
          loading={predictionsQuery.isPending}
          getRowId={(prediction) => prediction.customer_id}
          itemLabel="khách hàng"
          pagination={{ page, pageSize: PAGE_SIZE, onPageChange: setPage }}
        />
      </section>
    </div>
  )
}

export default Component
