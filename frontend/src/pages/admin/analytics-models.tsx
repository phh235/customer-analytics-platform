import { useEffect, useState, type FormEvent } from "react"
import { BrainCircuitIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import {
  deployModel,
  getModels,
  trainModel,
  type ModelLifecycleRecord,
} from "@/api/analytics"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatEnumLabel,
  MODEL_STATUS_LABELS,
  MODEL_TYPE_LABELS,
} from "@/lib/admin-management"

const today = new Date().toISOString().slice(0, 10)

export const Component = () => {
  const [models, setModels] = useState<ModelLifecycleRecord[]>([])
  const [version, setVersion] = useState(`purchase-repeat-${today}`)
  const [modelType, setModelType] = useState<
    "LOGISTIC_REGRESSION" | "RANDOM_FOREST"
  >("LOGISTIC_REGRESSION")
  const [featureWindowDays, setFeatureWindowDays] = useState(365)
  const [predictionHorizonDays, setPredictionHorizonDays] = useState(90)
  const [analysisDate, setAnalysisDate] = useState(today)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshModels = () => {
    void getModels()
      .then((response) => setModels(response))
      .catch((requestError: unknown) =>
        setError(getApiErrorMessage(requestError))
      )
  }

  useEffect(() => {
    let cancelled = false
    void getModels()
      .then((response) => {
        if (!cancelled) setModels(response)
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

  const handleTrain = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await trainModel({
        version,
        model_type: modelType,
        feature_window_days: featureWindowDays,
        prediction_horizon_days: predictionHorizonDays,
        analysis_date: analysisDate || undefined,
      })
      refreshModels()
    } catch (requestError: unknown) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeploy = async (modelVersion: string) => {
    setError(null)
    try {
      await deployModel(modelVersion)
      refreshModels()
    } catch (requestError: unknown) {
      setError(getApiErrorMessage(requestError))
    }
  }

  const columns: CommonTableColumn<ModelLifecycleRecord>[] = [
    {
      id: "version",
      header: "Phiên bản",
      cell: (model) => <span className="font-medium">{model.version}</span>,
    },
    {
      id: "model_type",
      header: "Loại mô hình",
      cell: (model) =>
        formatEnumLabel(model.model_type, MODEL_TYPE_LABELS),
    },
    {
      id: "status",
      header: "Trạng thái",
      cell: (model) => (
        <Badge variant="outline">
          {formatEnumLabel(model.status, MODEL_STATUS_LABELS)}
        </Badge>
      ),
    },
    {
      id: "metrics",
      header: "PR-AUC / Lift@10",
      cell: (model) => `${model.pr_auc ?? "—"} / ${model.lift_top10 ?? "—"}`,
    },
    {
      id: "action",
      header: "Thao tác",
      cell: (model) => (
        <Button
          disabled={model.status !== "APPROVED"}
          onClick={() => void handleDeploy(model.version)}
          size="sm"
          type="button"
        >
          {model.status === "APPROVED" ? "Đưa vào sử dụng" : "Không khả dụng"}
        </Button>
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4">
      <header>
        <div className="flex items-center gap-2">
          <BrainCircuitIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Quản lý mô hình</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Chỉ deploy model APPROVED; model phải vượt các gate PR-AUC, Lift@10 và
          Precision@10.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Train model</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-5"
            onSubmit={handleTrain}
          >
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Version</span>
              <input
                className="h-9 rounded-md border bg-background px-3"
                required
                value={version}
                onChange={(event) => setVersion(event.target.value)}
              />
            </label>
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Model</span>
              <select
                className="h-9 rounded-md border bg-background px-3"
                value={modelType}
                onChange={(event) =>
                  setModelType(
                    event.target.value as
                      "LOGISTIC_REGRESSION" | "RANDOM_FOREST"
                  )
                }
              >
                <option value="LOGISTIC_REGRESSION">Logistic Regression</option>
                <option value="RANDOM_FOREST">Random Forest</option>
              </select>
            </label>
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Feature window</span>
              <input
                className="h-9 rounded-md border bg-background px-3"
                min={30}
                max={3650}
                type="number"
                value={featureWindowDays}
                onChange={(event) =>
                  setFeatureWindowDays(Number(event.target.value))
                }
              />
            </label>
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Prediction horizon</span>
              <input
                className="h-9 rounded-md border bg-background px-3"
                min={1}
                max={365}
                type="number"
                value={predictionHorizonDays}
                onChange={(event) =>
                  setPredictionHorizonDays(Number(event.target.value))
                }
              />
            </label>
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Analysis date</span>
              <input
                className="h-9 rounded-md border bg-background px-3"
                type="date"
                value={analysisDate}
                onChange={(event) => setAnalysisDate(event.target.value)}
              />
            </label>
            <Button
              className="lg:col-span-5"
              disabled={submitting}
              type="submit"
            >
              {submitting ? "Đang train..." : "Train và evaluate"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Model registry</CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <p className="py-8 text-center text-sm text-destructive">{error}</p>
          ) : (
            <CommonTable
              data={models}
              columns={columns}
              loading={loading}
              getRowId={(model) => model.version}
              emptyMessage="Chưa có model nào được đăng ký."
              summary={`${models.length} model version`}
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Component
