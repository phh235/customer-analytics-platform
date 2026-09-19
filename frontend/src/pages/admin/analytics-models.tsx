import { useEffect, useState, type FormEvent } from "react"
import { BrainCircuitIcon, RocketIcon } from "lucide-react"

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
import { AppSelect } from "@/components/common/app-select"
import { TableActions } from "@/components/common/table-actions"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  formatEnumLabel,
  MODEL_STATUS_LABELS,
  MODEL_TYPE_LABELS,
} from "@/lib/admin-management"

const today = new Date().toISOString().slice(0, 10)

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
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
      cell: (model) => <span>{model.version}</span>,
    },
    {
      id: "model_type",
      header: "Loại mô hình",
      cell: (model) => formatEnumLabel(model.model_type, MODEL_TYPE_LABELS),
    },
    {
      id: "status",
      header: "Trạng thái",
      cell: (model) => (
        <Badge
          variant={
            ["APPROVED", "DEPLOYED"].includes(model.status)
              ? "success"
              : model.status === "FAILED"
                ? "destructive"
                : "secondary"
          }
        >
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
      className: "w-24 text-right",
      cell: (model) => (
        <TableActions
          actions={[
            {
              key: "deploy",
              label: "Đưa vào sử dụng",
              icon: <RocketIcon />,
              disabled: model.status !== "APPROVED",
              onClick: () => void handleDeploy(model.version),
            },
          ]}
        />
      ),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <div className="flex items-center gap-2">
          <BrainCircuitIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Quản lý mô hình</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Huấn luyện, đánh giá và đưa các mô hình đã được duyệt vào sử dụng.
        </p>
      </header>

      <Card className="mx-3">
        <CardHeader>
          <CardTitle>Huấn luyện mô hình</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleTrain}>
            <FieldGroup className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <Field>
                <FieldLabel htmlFor="model-version">Phiên bản</FieldLabel>
                <Input
                  id="model-version"
                  required
                  value={version}
                  onChange={(event) => setVersion(event.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="model-type">Loại mô hình</FieldLabel>
                <AppSelect
                  id="model-type"
                  className="w-full"
                  value={modelType}
                  onChange={setModelType}
                  options={[
                    { value: "LOGISTIC_REGRESSION", label: "Hồi quy logistic" },
                    { value: "RANDOM_FOREST", label: "Rừng ngẫu nhiên" },
                  ]}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="feature-window">
                  Kỳ quan sát (ngày)
                </FieldLabel>
                <Input
                  id="feature-window"
                  type="number"
                  min={30}
                  max={3650}
                  value={featureWindowDays}
                  onChange={(event) =>
                    setFeatureWindowDays(Number(event.target.value))
                  }
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="prediction-horizon">
                  Kỳ dự đoán (ngày)
                </FieldLabel>
                <Input
                  id="prediction-horizon"
                  type="number"
                  min={1}
                  max={365}
                  value={predictionHorizonDays}
                  onChange={(event) =>
                    setPredictionHorizonDays(Number(event.target.value))
                  }
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="analysis-date">Ngày phân tích</FieldLabel>
                <Input
                  id="analysis-date"
                  className="scheme-light dark:scheme-dark"
                  type="date"
                  value={analysisDate}
                  onChange={(event) => setAnalysisDate(event.target.value)}
                />
              </Field>
            </FieldGroup>
            <Button className="self-end" disabled={submitting} type="submit">
              {submitting ? "Đang huấn luyện..." : "Huấn luyện và đánh giá"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <section aria-label="Danh sách mô hình">
        {error ? (
          <p className="py-8 text-center text-sm text-destructive">{error}</p>
        ) : (
          <CommonTable
            data={models}
            columns={columns}
            loading={loading}
            getRowId={(model) => model.version}
            emptyMessage="Chưa có mô hình nào được đăng ký."
            itemLabel="mô hình"
            pagination={{
              page,
              pageSize: PAGE_SIZE,
              onPageChange: setPage,
            }}
          />
        )}
      </section>
    </div>
  )
}

export default Component
