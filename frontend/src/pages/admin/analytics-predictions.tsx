import { useEffect, useState } from "react"
import { BrainCircuitIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import {
  getPurchasePredictions,
  type PurchasePredictionRecord,
} from "@/api/analytics"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatDate } from "@/lib/admin-management"

export const Component = () => {
  const [predictions, setPredictions] = useState<PurchasePredictionRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getPurchasePredictions()
      .then((response) => {
        if (cancelled) return
        setPredictions(response)
        setError(null)
      })
      .catch((requestError: unknown) => {
        if (!cancelled) setError(getApiErrorMessage(requestError))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const columns: CommonTableColumn<PurchasePredictionRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      cell: (prediction) => (
        <span className="font-medium">{prediction.name}</span>
      ),
    },
    {
      id: "purchase_probability",
      header: "Xác suất mua lại",
      cell: (prediction) =>
        `${(prediction.purchase_probability * 100).toFixed(1)}%`,
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
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4">
      <header>
        <div className="flex items-center gap-2">
          <BrainCircuitIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Dự đoán mua lại</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Dự đoán xác suất khách hàng mua lại trong 90 ngày tiếp theo.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Kết quả dự đoán</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <p className="py-8 text-center text-sm text-destructive">{error}</p>
          ) : (
            <CommonTable
              data={predictions}
              columns={columns}
              loading={loading}
              getRowId={(prediction) => prediction.customer_id}
              summary={`${predictions.length} khách hàng có dự báo`}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Component
