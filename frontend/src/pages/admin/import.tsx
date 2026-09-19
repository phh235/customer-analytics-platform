import { useState, type FormEvent } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FileSpreadsheetIcon, UploadCloudIcon, XIcon } from "lucide-react"
import { parseAsInteger, useQueryState } from "nuqs"

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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  FileUpload,
  FileUploadDropzone,
  FileUploadItem,
  FileUploadItemDelete,
  FileUploadItemMetadata,
  FileUploadItemPreview,
  FileUploadList,
  FileUploadTrigger,
} from "@/components/ui/file-upload"
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
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1))
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
      void setPage(1)
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

      <div className="grid min-w-0 items-start gap-4 px-3 xl:grid-cols-[minmax(18rem,1fr)_minmax(0,2.2fr)]">
        <Card className="min-w-0 xl:sticky xl:top-4">
          <CardHeader>
            <CardTitle>Tải dữ liệu</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-4" onSubmit={handleUpload}>
              <FileUpload
                value={file ? [file] : []}
                onValueChange={(files) => {
                  setFile(files[0] ?? null)
                  setError(null)
                }}
                onFileReject={(_, message) => setError(message)}
                accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                maxFiles={1}
                label="Tệp Excel cần nhập"
                disabled={uploadMutation.isPending}
              >
                <FileUploadDropzone className="min-h-40 p-4 text-center">
                  <FileSpreadsheetIcon className="size-8 text-primary" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">
                      Kéo thả tệp Excel vào đây
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Chỉ chấp nhận workbook định dạng .xlsx
                    </p>
                  </div>
                  <FileUploadTrigger
                    render={
                      <Button type="button" variant="outline" size="sm" />
                    }
                  >
                    <UploadCloudIcon data-icon="inline-start" />
                    Chọn tệp
                  </FileUploadTrigger>
                </FileUploadDropzone>

                <FileUploadList>
                  {file ? (
                    <FileUploadItem value={file}>
                      <FileUploadItemPreview className="[&>svg]:size-5" />
                      <FileUploadItemMetadata />
                      <FileUploadItemDelete
                        render={
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            aria-label="Xóa tệp đã chọn"
                          />
                        }
                      >
                        <XIcon />
                      </FileUploadItemDelete>
                    </FileUploadItem>
                  ) : null}
                </FileUploadList>
              </FileUpload>

              {error ? (
                <p className="text-sm text-destructive">{error}</p>
              ) : null}

              <Button
                className="w-full"
                disabled={!file || uploadMutation.isPending}
                type="submit"
              >
                {uploadMutation.isPending ? "Đang xử lý..." : "Tải và xử lý"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <section
          aria-label="Danh sách phiên nhập dữ liệu"
          className="min-w-0 [&>[aria-busy]]:px-0"
        >
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
              onPageChange: (nextPage) => void setPage(nextPage),
            }}
          />
        </section>
      </div>
    </div>
  )
}

export default Component
