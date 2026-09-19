import { useEffect, useState, type FormEvent } from "react"
import { FileUpIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import {
  getImportJobs,
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
import {
  formatDate,
  formatEnumLabel,
  IMPORT_STATUS_LABELS,
  IMPORT_TYPE_LABELS,
} from "@/lib/admin-management"

const PAGE_SIZE = 20

export const Component = () => {
  const [error, setError] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [jobs, setJobs] = useState<ImportJobRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [refreshToken, setRefreshToken] = useState(0)

  useEffect(() => {
    let cancelled = false
    void getImportJobs(page, PAGE_SIZE)
      .then((response) => {
        if (cancelled) return
        setJobs(response.records)
        setPages(response.pages)
        setTotal(response.total)
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
  }, [page, refreshToken])

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!file) {
      setError("Hãy chọn workbook Excel (.xlsx).")
      return
    }
    setUploading(true)
    setError(null)
    try {
      const job = await uploadImportFile(file)
      await processImportJob(job.id)
      setFile(null)
      setPage(1)
      setRefreshToken((value) => value + 1)
    } catch (requestError: unknown) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setUploading(false)
    }
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
        <div className="flex items-center gap-2">
          <FileUpIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Nhập dữ liệu</h1>
        </div>
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
            <Button className="self-end" disabled={uploading} type="submit">
              {uploading ? "Đang xử lý..." : "Tải và xử lý"}
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
          loading={loading}
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
