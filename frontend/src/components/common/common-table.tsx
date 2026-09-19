import type { ReactNode } from "react"

import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink as UiPaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export interface CommonTableColumn<T> {
  id: string
  header: ReactNode
  cell: (item: T) => ReactNode
  className?: string
  skeletonClassName?: string
}

export interface CommonTablePagination {
  page: number
  pageSize: number
  total?: number
  totalPages?: number
  hasNext?: boolean
  hasPrevious?: boolean
  nextPage?: number | null
  previousPage?: number | null
  onPageChange: (page: number) => void
}

interface CommonTableProps<T> {
  data: T[]
  columns: CommonTableColumn<T>[]
  loading?: boolean
  emptyMessage?: ReactNode
  summary?: ReactNode
  itemLabel?: string
  getRowId?: (item: T, index: number) => string | number
  pagination?: CommonTablePagination
}

function getPageCount(total: number, pageSize: number) {
  return Math.max(1, Math.ceil(total / pageSize))
}
function getVisiblePages(currentPage: number, pageCount: number) {
  if (pageCount <= 3) {
    return Array.from({ length: pageCount }, (_, index) => index + 1)
  }

  const firstPage = Math.min(Math.max(currentPage - 1, 1), pageCount - 2)
  return [firstPage, firstPage + 1, firstPage + 2]
}

export function CommonTable<T>({
  data,
  columns,
  loading = false,
  emptyMessage = "Không có dữ liệu.",
  summary,
  itemLabel,
  getRowId,
  pagination,
}: CommonTableProps<T>) {
  const total = pagination?.total ?? data.length
  const pageCount = pagination
    ? Math.max(
        1,
        pagination.totalPages ?? getPageCount(total, pagination.pageSize)
      )
    : 1
  const currentPage = pagination
    ? Math.min(Math.max(pagination.page, 1), pageCount)
    : 1
  const canGoPrevious =
    pagination?.hasPrevious ??
    (pagination?.previousPage !== undefined
      ? pagination.previousPage !== null
      : currentPage > 1)
  const visiblePages = pagination ? getVisiblePages(currentPage, pageCount) : []

  const canGoNext =
    pagination?.hasNext ??
    (pagination?.nextPage !== undefined
      ? pagination.nextPage !== null
      : currentPage < pageCount)
  const pageData =
    pagination?.total === undefined
      ? data.slice(
          (currentPage - 1) * (pagination?.pageSize ?? data.length),
          currentPage * (pagination?.pageSize ?? data.length)
        )
      : data

  const skeletonRows = Math.min(pagination?.pageSize ?? 6, 6)
  const firstItem =
    pageData.length > 0
      ? (currentPage - 1) * (pagination?.pageSize ?? data.length) + 1
      : 0
  const lastItem = Math.min(firstItem + pageData.length - 1, total)
  const tableSummary =
    summary ??
    (itemLabel
      ? loading
        ? `Đang tải ${itemLabel}...`
        : `Hiển thị ${firstItem === 0 ? "0" : `${firstItem}–${lastItem}`} / ${total} ${itemLabel}`
      : undefined)

  return (
    <div aria-busy={loading} className="flex min-w-0 flex-col gap-2 px-3 pb-3">
      <div className="overflow-hidden rounded-xl border border-border bg-background">
        <Table
          aria-label={itemLabel ? `Danh sách ${itemLabel}` : undefined}
          className="min-w-full table-auto border-y-0 [&_td]:px-4 [&_th]:px-4"
        >
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead key={column.id} className={column.className}>
                  {loading ? <Skeleton className="h-4 w-3/5" /> : column.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading
              ? Array.from({ length: skeletonRows }, (_, rowIndex) => (
                  <TableRow className="h-12" key={`skeleton-row-${rowIndex}`}>
                    {columns.map((column) => (
                      <TableCell key={column.id} className={column.className}>
                        <Skeleton
                          className={column.skeletonClassName ?? "h-6 w-4/5"}
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              : pageData.map((item, index) => (
                  <TableRow
                    className="h-12"
                    key={getRowId?.(item, index) ?? index}
                  >
                    {columns.map((column) => (
                      <TableCell key={column.id} className={column.className}>
                        {column.cell(item)}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
            {!loading && pageData.length === 0 ? (
              <TableRow>
                <TableCell
                  className="py-8 text-center text-muted-foreground"
                  colSpan={columns.length}
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : null}
          </TableBody>
        </Table>
      </div>

      {tableSummary || (pagination && pageCount > 1) ? (
        <div className="flex min-h-8 flex-col gap-2 px-3 sm:flex-row sm:items-center sm:justify-between">
          {tableSummary ? (
            <div role="status" className="text-sm text-muted-foreground">
              {tableSummary}
            </div>
          ) : (
            <div />
          )}

          {pagination && pageCount > 1 ? (
            <Pagination
              aria-label={itemLabel ? `Phân trang ${itemLabel}` : "Phân trang"}
              className="mx-0 w-auto justify-end self-end sm:self-auto"
            >
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    text="Trước"
                    aria-label="Trang trước"
                    aria-disabled={loading || !canGoPrevious}
                    tabIndex={loading || !canGoPrevious ? -1 : undefined}
                    className={
                      loading || !canGoPrevious
                        ? "pointer-events-none opacity-50"
                        : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (!loading && canGoPrevious) {
                        pagination.onPageChange(
                          pagination.previousPage ?? currentPage - 1
                        )
                      }
                    }}
                  />
                </PaginationItem>
                {visiblePages.map((pageNumber) => (
                  <PaginationItem key={pageNumber}>
                    <UiPaginationLink
                      href="#"
                      isActive={pageNumber === currentPage}
                      aria-label={`Trang ${pageNumber}`}
                      aria-disabled={loading}
                      tabIndex={loading ? -1 : undefined}
                      onClick={(event) => {
                        event.preventDefault()
                        if (!loading) pagination.onPageChange(pageNumber)
                      }}
                    >
                      {pageNumber}
                    </UiPaginationLink>
                  </PaginationItem>
                ))}
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    text="Sau"
                    aria-label="Trang sau"
                    aria-disabled={loading || !canGoNext}
                    tabIndex={loading || !canGoNext ? -1 : undefined}
                    className={
                      loading || !canGoNext
                        ? "pointer-events-none opacity-50"
                        : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (!loading && canGoNext) {
                        pagination.onPageChange(
                          pagination.nextPage ?? currentPage + 1
                        )
                      }
                    }}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
