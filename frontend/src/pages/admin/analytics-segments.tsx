import { useState } from "react"

import type { SegmentRecord } from "@/api/analytics"
import { SegmentBadge } from "@/components/admin/management/analytics-status-badge"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { UserAvatar } from "@/components/common/user-avatar"
import { useSegments } from "@/hooks/use-analytics"
import { formatDate } from "@/lib/date"

const PAGE_SIZE = 10

export const Component = () => {
  const [page, setPage] = useState(1)
  const segmentsQuery = useSegments()
  const segments = segmentsQuery.data ?? []

  const columns: CommonTableColumn<SegmentRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      className: "min-w-52",
      cell: (segment) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={segment.name} />
          <span>{segment.name}</span>
        </div>
      ),
    },
    {
      id: "segment_type",
      header: "Phân khúc",
      cell: (segment) => <SegmentBadge segment={segment.segment_type} />,
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
        <h1 className="text-2xl font-semibold">Phân khúc khách hàng</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Kết quả phân khúc được tính từ dữ liệu giao dịch 365 ngày gần nhất.
        </p>
      </header>

      <section aria-label="Danh sách khách hàng">
        <CommonTable
          data={segments}
          columns={columns}
          loading={segmentsQuery.isPending}
          getRowId={(segment) => segment.customer_id}
          itemLabel="khách hàng"
          pagination={{ page, pageSize: PAGE_SIZE, onPageChange: setPage }}
        />
      </section>
    </div>
  )
}

export default Component
