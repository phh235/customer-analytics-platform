import { useState, type FormEvent } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { getApiErrorMessage } from "@/api/errors"
import {
  processImportJob,
  uploadImportFile,
  type ImportJobRecord,
} from "@/api/import-data"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { importJobQueryKeys, useImportJobs } from "@/hooks/use-import-jobs"
import {
  IMPORT_STATUS_LABELS,
  IMPORT_TYPE_LABELS,
} from "@/lib/admin-management"
import { formatDate } from "@/lib/date"
import { formatEnumLabel } from "@/lib/format"

const PAGE_SIZE = 10

export const Component = () => {
  const [error, setError] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [page, setPage] = useState(1)
  const queryClient = useQueryClient()
  const jobsQuery = useImportJobs(page, PAGE_SIZE)
  const jobs = jobsQuery.data?.records ?? []
  const pages = jobsQuery.data?.pages ?? 1
  const total = jobsQuery.data?.total ?? 0
  const uploadMutation = useMutation({
    mutationFn: async (selectedFile: File) => {
      const job = await uploadImportFile(selectedFile)
      return processImportJob(job.id)
    },
    onSuccess: async () => {
      setFile(null)
      setPage(1)
      await queryClient.invalidateQueries({ queryKey: importJobQueryKeys.all })
    },
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  })

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setError("Hãy chọn workbook Excel (.xlsx).")
      return
    }
    setError(null)
    uploadMutation.mutate(file)
  }

  const columns: CommonTableColumn<ImportJobRecord>[] = [
    {
      id: "filename",
      header: "Tệp",
      cell: (job) => <span>{job.filename}</span>,
    },
    {
      id: "import_type",
      header: "Loại",
      cell: (job) => formatEnumLabel(job.import_type, IMPORT_TYPE_LABELS),
    },
    {
      id: "status",
      header: "Trạng thái",
      cell: (job) => (
        <Badge
          variant={
            job.status === "COMPLETED"
              ? "success"
              : job.status === "FAILED"
                ? "destructive"
                : "secondary"
          }
        >
          {formatEnumLabel(job.status, IMPORT_STATUS_LABELS)}
        </Badge>
      ),
    },
    {
      id: "progress",
      header: "Tiến độ",
      cell: (job) => `${job.success_rows}/${job.total_rows}`,
    },
    {
      id: "created_at",
      header: "Thời gian",
      cell: (job) => formatDate(job.created_at),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <h1 className="text-2xl font-semibold">Nhập dữ liệu</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Tải lên tệp Excel theo mẫu dữ liệu gồm 14 trang tính.
        </p>
      </header>

      <Card className="mx-3">
        <CardHeader>
          <CardTitle>Tải dữ liệu</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4 md:flex-row md:items-end"
            onSubmit={handleUpload}
          >
            <FieldGroup className="min-w-0 flex-1">
              <Field>
                <FieldLabel htmlFor="import-file">Tệp Excel</FieldLabel>
                <Input
                  id="import-file"
                  type="file"
                  accept=".xlsx"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                />
              </Field>
            </FieldGroup>
            <Button
              className="self-end"
              disabled={uploadMutation.isPending}
              type="submit"
            >
              {uploadMutation.isPending ? "Đang xử lý..." : "Tải và xử lý"}
            </Button>
          </form>
          {error ? (
            <p className="mt-4 text-sm text-destructive">{error}</p>
          ) : null}
        </CardContent>
      </Card>

      <section aria-label="Danh sách phiên nhập dữ liệu">
        <CommonTable
          data={jobs}
          columns={columns}
          loading={jobsQuery.isPending}
          getRowId={(job) => job.id}
          emptyMessage="Chưa có phiên import nào."
          itemLabel="phiên nhập dữ liệu"
          pagination={{
            page,
            pageSize: PAGE_SIZE,
            total,
            totalPages: pages,
            onPageChange: setPage,
          }}
        />
      </section>
    </div>
  )
}

export default Component
