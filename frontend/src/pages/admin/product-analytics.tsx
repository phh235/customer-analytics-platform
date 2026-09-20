import {
  ArrowLeftIcon,
  EyeIcon,
  Repeat2Icon,
  UsersIcon,
  type LucideIcon,
} from "lucide-react"
import { Link, Navigate, useParams } from "react-router"
import { parseAsString, parseAsStringLiteral, useQueryStates } from "nuqs"
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"

import type { InterestedCustomer } from "@/api/product-analytics"
import { AppSelect } from "@/components/common/app-select"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { UserAvatar } from "@/components/common/user-avatar"
import { Button } from "@/components/ui/button"
import {
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { useProductAnalytics } from "@/hooks/use-product-analytics"
import { useProduct } from "@/hooks/use-products"
import { formatDateTime } from "@/lib/date"

const PAGE_SIZE = 10
const today = new Date().toISOString().slice(0, 10)
const fromDate = new Date(`${today}T00:00:00Z`)
fromDate.setUTCDate(fromDate.getUTCDate() - 29)
const defaultFrom = fromDate.toISOString().slice(0, 10)

const chartConfig = {
  views: { label: "Lượt xem", color: "var(--chart-1)" },
} satisfies ChartConfig

export const Component = () => {
  const { productId } = useParams()
  const [{ from, to, groupBy }, setQuery] = useQueryStates({
    from: parseAsString.withDefault(defaultFrom),
    to: parseAsString.withDefault(today),
    groupBy: parseAsStringLiteral([
      "DAY",
      "WEEK",
      "MONTH",
    ] as const).withDefault("DAY"),
  })
  const productQuery = useProduct(productId)
  const {
    interestQuery,
    viewsQuery,
    uniqueViewersQuery,
    viewersQuery,
    trendQuery,
    customersQuery,
  } = useProductAnalytics(productId, {
    from,
    to,
    groupBy,
    size: PAGE_SIZE,
  })
  const overview = interestQuery.data
  const totalViews = viewsQuery.data?.totalViews ?? overview?.totalViews
  const uniqueViewers =
    uniqueViewersQuery.data?.uniqueViewers ?? overview?.uniqueViewers
  const repeatViewers = viewersQuery.data?.items.filter(
    (viewer) => viewer.viewCount > 1
  ).length
  const averageViews =
    typeof totalViews === "number" && uniqueViewers
      ? totalViews / uniqueViewers
      : 0
  const loading =
    productQuery.isPending ||
    interestQuery.isPending ||
    viewsQuery.isPending ||
    uniqueViewersQuery.isPending ||
    viewersQuery.isPending ||
    trendQuery.isPending ||
    customersQuery.isPending
  const metrics: {
    label: string
    value: number | undefined
    icon: LucideIcon
  }[] = [
    { label: "Tổng lượt xem", value: totalViews, icon: EyeIcon },
    {
      label: "Khách duy nhất",
      value: uniqueViewers,
      icon: UsersIcon,
    },
    {
      label: "Khách xem lại",
      value: repeatViewers,
      icon: Repeat2Icon,
    },
    {
      label: "Lượt xem trung bình",
      value: averageViews,
      icon: EyeIcon,
    },
  ]

  const columns: CommonTableColumn<InterestedCustomer>[] = [
    {
      id: "customer",
      header: "Khách hàng",
      className: "min-w-56",
      cell: (customer) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={customer.customerName} />
          <div className="min-w-0">
            <p className="truncate font-medium">{customer.customerName}</p>
            <p className="text-xs text-muted-foreground">
              {customer.customerCode}
            </p>
          </div>
        </div>
      ),
    },
    {
      id: "views",
      header: "Lượt xem",
      cell: (customer) => (
        <span className="font-medium tabular-nums">{customer.viewCount}</span>
      ),
    },
    {
      id: "lastViewedAt",
      header: "Xem gần nhất",
      cell: (customer) => formatDateTime(customer.lastViewedAt),
    },
  ]

  if (!productId) return <Navigate replace to="/dashboard/products" />

  return (
    <div className="flex w-full min-w-0 flex-col gap-4 p-3">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Button
            nativeButton={false}
            render={<Link to="/dashboard/products" />}
            variant="ghost"
            className="-ml-2"
          >
            <ArrowLeftIcon data-icon="inline-start" />
            Quản lý sản phẩm
          </Button>
          <h1 className="mt-1 text-2xl font-semibold">
            Phân tích mức độ quan tâm
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {productQuery.data?.name ?? "Đang tải sản phẩm…"}
            {productQuery.data?.product_code
              ? ` · ${productQuery.data.product_code}`
              : ""}
          </p>
        </div>
        <FieldGroup className="grid grid-cols-2 gap-2 sm:grid-cols-3">
          <Field className="gap-1">
            <FieldLabel htmlFor="analytics-from">Từ ngày</FieldLabel>
            <Input
              id="analytics-from"
              type="date"
              value={from}
              max={to}
              onChange={(event) => void setQuery({ from: event.target.value })}
            />
          </Field>
          <Field className="gap-1">
            <FieldLabel htmlFor="analytics-to">Đến ngày</FieldLabel>
            <Input
              id="analytics-to"
              type="date"
              value={to}
              min={from}
              onChange={(event) => void setQuery({ to: event.target.value })}
            />
          </Field>
          <Field className="col-span-2 gap-1 sm:col-span-1">
            <FieldLabel htmlFor="analytics-group">Nhóm theo</FieldLabel>
            <AppSelect
              id="analytics-group"
              value={groupBy}
              onChange={(value) => void setQuery({ groupBy: value })}
              className="w-full"
              options={[
                { value: "DAY", label: "Ngày" },
                { value: "WEEK", label: "Tuần" },
                { value: "MONTH", label: "Tháng" },
              ]}
            />
          </Field>
        </FieldGroup>
      </header>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ label, value, icon: Icon }) => (
          <SquircleCard key={label} size="sm">
            <CardHeader className="grid grid-cols-[1fr_auto] items-center">
              <CardTitle>{label}</CardTitle>
              <Icon className="size-4 text-muted-foreground" />
            </CardHeader>
            <SquircleCardBody>
              <CardContent>
                {loading ? (
                  <Skeleton className="h-8 w-24" />
                ) : (
                  <p className="text-2xl font-semibold tabular-nums">
                    {typeof value === "number"
                      ? value.toLocaleString("vi-VN", {
                          maximumFractionDigits: 2,
                        })
                      : "0"}
                  </p>
                )}
              </CardContent>
            </SquircleCardBody>
          </SquircleCard>
        ))}
      </div>

      <SquircleCard>
        <CardHeader>
          <CardTitle>Xu hướng lượt xem</CardTitle>
          <CardDescription>Lượt xem sản phẩm theo thời gian</CardDescription>
        </CardHeader>
        <SquircleCardBody>
          <CardContent>
            {loading ? (
              <Skeleton className="h-72 w-full" />
            ) : (
              <ChartContainer config={chartConfig} className="h-72 w-full">
                <LineChart data={trendQuery.data?.items ?? []}>
                  <CartesianGrid vertical={false} strokeDasharray="3 3" />
                  <XAxis dataKey="period" tickLine={false} axisLine={false} />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                  />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    dataKey="views"
                    stroke="var(--color-views)"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ChartContainer>
            )}
          </CardContent>
        </SquircleCardBody>
      </SquircleCard>

      <SquircleCard>
        <CardHeader>
          <CardTitle>Khách hàng quan tâm nhiều nhất</CardTitle>
          <CardDescription>
            Xếp hạng theo số lần xem và lần xem gần nhất
          </CardDescription>
        </CardHeader>
        <SquircleCardBody className="py-0">
          <CommonTable
            variant="embedded"
            data={customersQuery.data?.items ?? []}
            columns={columns}
            loading={loading}
            getRowId={(customer) => customer.customerId}
            itemLabel="khách hàng"
            emptyMessage="Chưa có lượt xem sản phẩm trong khoảng thời gian này."
          />
        </SquircleCardBody>
      </SquircleCard>
    </div>
  )
}

export default Component
