import { useEffect, useState } from "react"
import { ChartNoAxesCombinedIcon } from "lucide-react"

import { getApiErrorMessage } from "@/api/errors"
import { getSegments, type SegmentRecord } from "@/api/analytics"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import {
  formatDate,
  formatEnumLabel,
  SEGMENT_LABELS,
} from "@/lib/admin-management"

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
  const [segments, setSegments] = useState<SegmentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getSegments()
      .then((response) => {
        if (cancelled) return
        setSegments(response)
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

  const columns: CommonTableColumn<SegmentRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      cell: (segment) => <span>{segment.name}</span>,
    },
    {
      id: "segment_type",
      header: "Phân khúc",
      cell: (segment) => (
        <Badge variant="secondary">
          {formatEnumLabel(segment.segment_type, SEGMENT_LABELS)}
        </Badge>
      ),
    },
    {
      id: "reason",
      header: "Lý do",
      cell: (segment) => (
        <span
          title={segment.reason}
          className="block max-w-xl truncate text-muted-foreground"
        >
          {segment.reason}
        </span>
      ),
    },
    {
      id: "calculated_at",
      header: "Tính lúc",
      cell: (segment) => formatDate(segment.calculated_at),
    },
  ]

  return (
    <div className="mx-auto flex w-full min-w-0 flex-col gap-4">
      <header className="px-3 pt-3">
        <div className="flex items-center gap-2">
          <ChartNoAxesCombinedIcon className="size-5 text-muted-foreground" />
          <h1 className="text-2xl font-semibold">Phân khúc khách hàng</h1>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Kết quả phân khúc được tính từ dữ liệu giao dịch 365 ngày gần nhất.
        </p>
      </header>

      <section aria-label="Danh sách khách hàng">
        {error ? (
          <p className="py-8 text-center text-sm text-destructive">{error}</p>
        ) : (
          <CommonTable
            data={segments}
            columns={columns}
            loading={loading}
            getRowId={(segment) => segment.customer_id}
            itemLabel="khách hàng"
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
