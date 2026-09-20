import {
  debounce,
  defaultRateLimit,
  parseAsInteger,
  parseAsString,
  useQueryStates,
} from "nuqs"

import type { SegmentRecord } from "@/api/analytics"
import { SegmentBadge } from "@/components/admin/management/analytics-status-badge"
import { PotentialScoreValue } from "@/components/admin/management/potential-score-value"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { TableSearch } from "@/components/common/table-search"
import { useDebounce } from "@/hooks/use-debounce"
import { UserAvatar } from "@/components/common/user-avatar"
import { useSegments } from "@/hooks/use-analytics"
import { formatDate } from "@/lib/date"

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
  const segmentsQuery = useSegments({
    page,
    size: PAGE_SIZE,
    search: debouncedSearch || undefined,
  })
  const segments = segmentsQuery.data?.records ?? []
  const total = segmentsQuery.data?.total ?? 0
  const pages = segmentsQuery.data?.pages ?? 1

  const columns: CommonTableColumn<SegmentRecord>[] = [
    {
      id: "name",
      header: "Khách hàng",
      className: "min-w-52",
      cell: (segment) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={segment.name} />
          <div className="min-w-0">
            <p className="truncate font-medium">{segment.name}</p>
            <p className="text-xs text-muted-foreground">
              {segment.customer_code || "-"}
            </p>
          </div>
        </div>
      ),
    },
    {
      id: "segment_type",
      header: "Phân khúc",
      cell: (segment) => <SegmentBadge segment={segment.segment_type} />,
    },
    {
      id: "potential_score",
      header: "Điểm tiềm năng",
      className: "min-w-36",
      cell: (segment) => (
        <PotentialScoreValue value={Number(segment.potential_score)} />
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
        <h1 className="text-2xl font-semibold">Phân khúc khách hàng</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Kết quả phân khúc được tính từ dữ liệu giao dịch 365 ngày gần nhất.
        </p>
      </header>

      <TableSearch
        value={search}
        onChange={(value) => {
          void setQuery(
            { search: value, page: 1 },
            { limitUrlUpdates: value ? debounce(300) : defaultRateLimit }
          )
        }}
        placeholder="Tìm khách hàng, phân khúc, lý do..."
        ariaLabel="Tìm kiếm kết quả phân khúc"
      />

      <section aria-label="Danh sách khách hàng">
        <CommonTable
          data={segments}
          columns={columns}
          loading={segmentsQuery.isPending}
          getRowId={(segment) => segment.customer_id}
          itemLabel="khách hàng"
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
