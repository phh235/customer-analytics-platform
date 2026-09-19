import { useState, type FormEvent } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { RocketIcon } from "lucide-react"
import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  useQueryStates,
} from "nuqs"

import { getApiErrorMessage } from "@/api/errors"
import {
  deployModel,
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
import { TableSearch } from "@/components/common/table-search"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { analyticsQueryKeys, useModels } from "@/hooks/use-analytics"
import { useDebounce } from "@/hooks/use-debounce"
import { MODEL_STATUS_LABELS, MODEL_TYPE_LABELS } from "@/lib/admin-management"
import { formatEnumLabel } from "@/lib/format"
import { toastError, toastSuccess } from "@/utils/toast"

const today = new Date().toISOString().slice(0, 10)

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
  const queryClient = useQueryClient()
  const modelsQuery = useModels({
    page,
    size: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const models = modelsQuery.data?.records ?? []
  const total = modelsQuery.data?.total ?? 0
  const pages = modelsQuery.data?.pages ?? 1
  const [version, setVersion] = useState(`purchase-repeat-${today}`)
  const [modelType, setModelType] = useState<
    "LOGISTIC_REGRESSION" | "RANDOM_FOREST"
  >("LOGISTIC_REGRESSION")
  const [featureWindowDays, setFeatureWindowDays] = useState(365)
  const [predictionHorizonDays, setPredictionHorizonDays] = useState(90)
  const [analysisDate, setAnalysisDate] = useState(today)
  const trainMutation = useMutation({
    mutationFn: (payload: Parameters<typeof trainModel>[0]) =>
      trainModel(payload),
    onSuccess: async () => {
      toastSuccess("Đã hoàn tất huấn luyện và đánh giá")
      await queryClient.invalidateQueries({
        queryKey: analyticsQueryKeys.all,
      })
    },
    onError: (error) => toastError(getApiErrorMessage(error)),
  })
  const deployMutation = useMutation({
    mutationFn: (version: string) => deployModel(version),
    onSuccess: async () => {
      toastSuccess("Đã đưa mô hình vào sử dụng")
      await queryClient.invalidateQueries({
        queryKey: analyticsQueryKeys.all,
      })
    },
    onError: (error) => toastError(getApiErrorMessage(error)),
  })

  const handleTrain = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    trainMutation.mutate({
      version,
      model_type: modelType,
      feature_window_days: featureWindowDays,
      prediction_horizon_days: predictionHorizonDays,
      analysis_date: analysisDate || undefined,
    })
  }

  const handleDeploy = async (modelVersion: string) => {
    deployMutation.mutate(modelVersion)
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
              disabled: model.status !== "APPROVED" || deployMutation.isPending,
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
        <h1 className="text-2xl font-semibold">Quản lý mô hình</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Huấn luyện, đánh giá và đưa các mô hình đã được duyệt vào sử dụng.
        </p>
      </header>

      <Card className="mx-3">
        <CardHeader>
          <CardTitle>Huấn luyện mô hình</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleTrain}>
            <FieldGroup className="grid gap-4 md:grid-cols-2 xl:grid-cols-[repeat(5,minmax(0,1fr))_auto]">
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
              <Button
                className="w-full self-end whitespace-nowrap md:w-auto"
                disabled={trainMutation.isPending}
                type="submit"
              >
                {trainMutation.isPending
                  ? "Đang huấn luyện..."
                  : "Huấn luyện và đánh giá"}
              </Button>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>

      <TableSearch
        value={search}
        onChange={(value) => {
          void setQuery(
            { search: value, page: 1 },
            { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
          )
        }}
        placeholder="Tìm phiên bản, loại hoặc trạng thái mô hình..."
        ariaLabel="Tìm kiếm mô hình"
      />

      <section aria-label="Danh sách mô hình">
        <CommonTable
          data={models}
          columns={columns}
          loading={modelsQuery.isPending}
          getRowId={(model) => model.version}
          emptyMessage="Chưa có mô hình nào được đăng ký."
          itemLabel="mô hình"
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
