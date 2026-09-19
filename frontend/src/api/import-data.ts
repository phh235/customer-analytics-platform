import apiClient from "@/api/client"

export interface ImportJobRecord {
  id: string
  filename: string
  import_type: string
  status: string
  total_rows: number
  processed_rows: number
  success_rows: number
  error_rows: number
  created_at: string
  completed_at: string | null
}

export interface PaginatedImportJobsResponse {
  current: number
  size: number
  total: number
  pages: number
  records: ImportJobRecord[]
}

export async function getImportJobs(page = 1, size = 20) {
  const { data } = await apiClient.get<PaginatedImportJobsResponse>(
    "/import/jobs",
    { params: { page, size } }
  )
  return data
}

export async function uploadImportFile(file: File) {
  const formData = new FormData()
  formData.append("file", file)
  const { data } = await apiClient.post<ImportJobRecord>(
    "/import/upload",
    formData,
    {
      params: { import_type: "DATASET" },
      headers: { "Content-Type": "multipart/form-data" },
    }
  )
  return data
}

export async function processImportJob(jobId: string) {
  const { data } = await apiClient.post<ImportJobRecord>("/import/process", {
    job_id: jobId,
    column_mapping: { __workbook__: "DATASET" },
  })
  return data
}
