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
      cell: (job) => <span className="font-medium">{job.filename}</span>,
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
        <Badge variant="outline">
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
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 p-4">
      <header>
        <div className="flex items-center gap-2">
          <FileUpIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Nhập dữ liệu</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Import workbook Excel 14 sheet theo đúng contract dữ liệu.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Tải dữ liệu</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4 md:grid-cols-[1fr_auto]"
            onSubmit={handleUpload}
          >
            <label className="grid gap-1 text-sm">
              <span className="font-medium">Workbook Excel</span>
              <input
                className="h-9 rounded-md border px-3 py-1 text-sm"
                type="file"
                accept=".xlsx"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <Button className="self-end" disabled={uploading} type="submit">
              {uploading ? "Đang xử lý..." : "Tải và xử lý"}
            </Button>
          </form>
          {error ? (
            <p className="mt-4 text-sm text-destructive">{error}</p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Lịch sử import</CardTitle>
        </CardHeader>
        <CardContent>
          <CommonTable
            data={jobs}
            columns={columns}
            loading={loading}
            getRowId={(job) => job.id}
            emptyMessage="Chưa có phiên import nào."
            summary={`${jobs.length} phiên import trên ${total} phiên`}
            pagination={{
              page,
              pageSize: PAGE_SIZE,
              total,
              totalPages: pages,
              onPageChange: setPage,
            }}
          />
        </CardContent>
      </Card>
    </div>
  )
}

export default Component
