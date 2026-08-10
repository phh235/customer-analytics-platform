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
  getRowId?: (item: T, index: number) => string | number
  pagination?: CommonTablePagination
}

function getPageCount(total: number, pageSize: number) {
  return Math.max(1, Math.ceil(total / pageSize))
}

export function CommonTable<T>({
  data,
  columns,
  loading = false,
  emptyMessage = "Không có dữ liệu.",
  summary,
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

  return (
    <div aria-busy={loading} className="flex flex-col gap-2 px-3 pb-3">
      <div className="overflow-hidden rounded-xl border border-border">
        <Table className="min-w-full table-auto border-y-0 [&_td]:px-4 [&_th]:px-4">
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
                  <TableRow key={`skeleton-row-${rowIndex}`}>
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
                  <TableRow key={getRowId?.(item, index) ?? index}>
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

      {summary || (pagination && pageCount > 1) ? (
        <div className="flex flex-col gap-4 px-3 sm:flex-row sm:items-center sm:justify-between">
          {summary ? (
            <div className="text-sm text-muted-foreground">{summary}</div>
          ) : (
            <div />
          )}

          {pagination && pageCount > 1 ? (
            <Pagination className="mx-0 w-auto justify-end">
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    text="Trước"
                    aria-label="Trang trước"
                    aria-disabled={!canGoPrevious}
                    className={
                      !canGoPrevious
                        ? "pointer-events-none opacity-50"
                        : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (canGoPrevious) {
                        pagination.onPageChange(
                          pagination.previousPage ?? currentPage - 1
                        )
                      }
                    }}
                  />
                </PaginationItem>
                {Array.from({ length: pageCount }, (_, index) => (
                  <PaginationItem key={index + 1}>
                    <UiPaginationLink
                      href="#"
                      isActive={index + 1 === currentPage}
                      onClick={(event) => {
                        event.preventDefault()
                        pagination.onPageChange(index + 1)
                      }}
                    >
                      {index + 1}
                    </UiPaginationLink>
                  </PaginationItem>
                ))}
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    text="Sau"
                    aria-label="Trang sau"
                    aria-disabled={!canGoNext}
                    className={
                      !canGoNext ? "pointer-events-none opacity-50" : undefined
                    }
                    onClick={(event) => {
                      event.preventDefault()
                      if (canGoNext) {
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
