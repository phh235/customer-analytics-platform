import { useId, useState, type PropsWithChildren } from "react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Label,
  Pie,
  PieChart,
  ReferenceLine,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  SquircleCard as Card,
  SquircleCardBody,
} from "@/components/ui/squircle-card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty"
import {
  formatCompactMoney,
  formatDashboardDate,
  formatDashboardMoney,
  formatDashboardNumber,
  formatShortDate,
  getDashboardSegmentLabel,
} from "@/lib/dashboard"
import type {
  DashboardOpportunityCustomer,
  DashboardOverview,
} from "@/types/dashboard"

const seriesConfig = {
  current: { label: "Kỳ này", color: "var(--chart-1)" },
  previous: { label: "Kỳ trước", color: "var(--muted-foreground)" },
} satisfies ChartConfig
const customerConfig = {
  count: { label: "Khách hàng", color: "var(--chart-1)" },
} satisfies ChartConfig
const opportunityConfig = {
  probability: { label: "Xác suất mua", color: "var(--chart-2)" },
  potential_score: { label: "Điểm tiềm năng", color: "var(--chart-1)" },
  revenue: { label: "Doanh thu", color: "var(--chart-3)" },
} satisfies ChartConfig
const segmentColors = [
  "var(--chart-1)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-2)",
  "var(--chart-5)",
  "var(--muted-foreground)",
  "var(--border)",
]
const categoryColors = [
  "#689d4b",
  "#576a8f",
  "#d9a45b",
  "#d96868",
  "#a6b1e1",
  "#7c6aa6",
  "#4f9d8f",
  "#c47f62",
]

function NoChartData({
  description = "Chưa có giao dịch hợp lệ trong khoảng thời gian đã chọn.",
}: {
  description?: string
}) {
  return (
    <Empty className="h-64">
      <EmptyHeader>
        <EmptyTitle>Chưa đủ dữ liệu</EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  )
}

export function RevenueChart({ data }: { data: DashboardOverview }) {
  const [metric, setMetric] = useState("revenue")
  const gradientId = useId().replaceAll(":", "")
  const isRevenue = metric === "revenue"
  const points = data.trend.map((point) => ({
    ...point,
    current: isRevenue ? point.revenue : point.orders,
    previous: isRevenue ? point.previous_revenue : point.previous_orders,
  }))
  return (
    <Card className="min-w-0 xl:col-span-2">
      <CardHeader>
        <CardTitle>Xu hướng kinh doanh</CardTitle>
        <CardDescription>So sánh với kỳ trước có cùng số ngày</CardDescription>
        <CardAction>
          <Tabs
            value={metric}
            onValueChange={(value) => setMetric(String(value))}
          >
            <TabsList aria-label="Chỉ số xu hướng">
              <TabsTrigger value="revenue">Doanh thu</TabsTrigger>
              <TabsTrigger value="orders">Đơn hàng</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardAction>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="flex flex-col gap-3">
          <ChartContainer
            config={seriesConfig}
            className="aspect-auto h-72 w-full"
            aria-label={`Biểu đồ ${isRevenue ? "doanh thu" : "đơn hàng"} theo ngày`}
          >
            <AreaChart
              accessibilityLayer
              data={points}
              margin={{ left: 0, right: 8, top: 12, bottom: 0 }}
            >
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="0%"
                    stopColor="var(--color-current)"
                    stopOpacity={0.25}
                  />
                  <stop
                    offset="100%"
                    stopColor="var(--color-current)"
                    stopOpacity={0.02}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis
                tick={{ fill: "var(--muted-foreground)" }}
                dataKey="date"
                tickLine={false}
                axisLine={false}
                minTickGap={32}
                tickMargin={10}
                tickFormatter={formatShortDate}
              />
              <YAxis
                tick={{ fill: "var(--muted-foreground)" }}
                tickLine={false}
                axisLine={false}
                width={48}
                allowDecimals={false}
                tickFormatter={(value: number) =>
                  isRevenue
                    ? formatCompactMoney(value)
                    : formatDashboardNumber(value)
                }
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    labelFormatter={(_, payload) => {
                      const point = payload[0]?.payload
                      return point
                        ? `${formatShortDate(point.date)} · đối chiếu ${formatShortDate(point.previous_date)}`
                        : ""
                    }}
                    formatter={(value, name) => (
                      <div className="flex w-full items-center justify-between gap-6">
                        <span className="text-muted-foreground">
                          {name === "current" ? "Kỳ này" : "Kỳ trước"}
                        </span>
                        <span className="font-medium tabular-nums">
                          {isRevenue
                            ? formatDashboardMoney(Number(value))
                            : `${formatDashboardNumber(Number(value))} đơn`}
                        </span>
                      </div>
                    )}
                  />
                }
              />
              <Area
                type="monotone"
                dataKey="previous"
                stroke="var(--color-previous)"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                fill="transparent"
                isAnimationActive={false}
              />
              <Area
                type="monotone"
                dataKey="current"
                stroke="var(--color-current)"
                strokeWidth={2}
                fill={`url(#${gradientId})`}
                isAnimationActive={false}
              />
            </AreaChart>
          </ChartContainer>
          <ChartMeta>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="size-2 rounded-full bg-chart-1" />
                Kỳ này
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 border-t border-dashed border-muted-foreground" />
                Kỳ trước
              </span>
            </div>
            <span>
              {formatDashboardDate(data.period.from)} –{" "}
              {formatDashboardDate(data.period.to)}
            </span>
          </ChartMeta>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

export function SegmentChart({ data }: { data: DashboardOverview }) {
  const segments = data.segments.map((item) => ({
    ...item,
    label: getDashboardSegmentLabel(item.key, item.label),
  }))
  const config = Object.fromEntries(
    segments.map((item, index) => [
      item.key,
      { label: item.label, color: segmentColors[index] },
    ])
  ) satisfies ChartConfig
  const total = data.metrics.customers.current
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Phân bố khách hàng</CardTitle>
        <CardDescription>
          Mỗi khách hàng thuộc một phân khúc chính
        </CardDescription>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="grid flex-1 grid-cols-2 items-center gap-4">
          <ChartContainer
            config={config}
            className="aspect-auto h-64 w-full min-w-0"
            aria-label="Biểu đồ tỷ trọng phân khúc khách hàng"
          >
            <PieChart accessibilityLayer>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent nameKey="key" hideLabel />}
              />
              <Pie
                data={segments.filter((item) => item.count > 0)}
                dataKey="count"
                nameKey="key"
                innerRadius="65%"
                outerRadius="94%"
                paddingAngle={2}
                strokeWidth={2}
                isAnimationActive={false}
              >
                {segments
                  .filter((item) => item.count > 0)
                  .map((item) => (
                    <Cell key={item.key} fill={`var(--color-${item.key})`} />
                  ))}
                <Label
                  content={({ viewBox }) =>
                    viewBox && "cx" in viewBox && "cy" in viewBox ? (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          dy="-4"
                          className="fill-foreground text-3xl font-semibold"
                        >
                          {formatDashboardNumber(total)}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          dy="22"
                          className="fill-muted-foreground text-xs"
                        >
                          khách hàng
                        </tspan>
                      </text>
                    ) : null
                  }
                />
              </Pie>
            </PieChart>
          </ChartContainer>
          <ul className="grid min-w-0 gap-3">
            {segments.map((item, index) => (
              <li
                key={item.key}
                className="flex items-center justify-between gap-2 text-xs"
              >
                <span className="flex min-w-0 items-center gap-2">
                  <span
                    className="size-2 shrink-0 rounded-full"
                    style={{ backgroundColor: segmentColors[index] }}
                  />
                  {item.label}
                </span>
                <span className="shrink-0 whitespace-nowrap tabular-nums">
                  {item.count}
                  <span className="ml-2 text-muted-foreground">
                    {total ? Math.round((item.count / total) * 100) : 0}%
                  </span>
                </span>
              </li>
            ))}
          </ul>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

export function PotentialChart({ data }: { data: DashboardOverview }) {
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Điểm tiềm năng</CardTitle>
        <CardDescription>Điểm theo quy tắc, thang 0–100</CardDescription>
        <CardAction>
          <Badge variant="success">
            {data.potential.high_count} tiềm năng cao
          </Badge>
        </CardAction>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="flex flex-1 flex-col gap-3">
          {data.potential.eligible_count === 0 ? (
            <NoChartData description="Khách hàng chưa có dữ liệu cần thiết để chấm điểm." />
          ) : (
            <ChartContainer
              config={customerConfig}
              className="aspect-auto h-56 w-full"
              aria-label="Biểu đồ phân bố điểm tiềm năng"
            >
              <BarChart
                accessibilityLayer
                data={data.potential.distribution}
                margin={{ top: 12, right: 4, left: -20, bottom: 0 }}
              >
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis
                  tick={{ fill: "var(--muted-foreground)" }}
                  dataKey="label"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis
                  allowDecimals={false}
                  axisLine={false}
                  tickLine={false}
                />
                <ChartTooltip
                  cursor={false}
                  content={<ChartTooltipContent />}
                />
                <Bar
                  dataKey="count"
                  radius={[5, 5, 0, 0]}
                  maxBarSize={48}
                  isAnimationActive={false}
                >
                  {data.potential.distribution.map((item) => (
                    <Cell
                      key={item.min}
                      fill={
                        item.min >= 80
                          ? "var(--chart-3)"
                          : item.min >= 60
                            ? "var(--chart-1)"
                            : "var(--chart-2)"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ChartContainer>
          )}
          <ChartMeta>
            <span>
              Cao ≥ {data.potential.thresholds.high} · Tiềm năng ≥{" "}
              {data.potential.thresholds.potential}
            </span>
            <span>
              {data.potential.insufficient_count} khách hàng chưa đủ dữ liệu
            </span>
          </ChartMeta>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

export function CategoryChart({ data }: { data: DashboardOverview }) {
  const config = {
    revenue: { label: "Doanh thu", color: "var(--chart-1)" },
  } satisfies ChartConfig
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Nhóm sản phẩm nổi bật</CardTitle>
        <CardDescription>
          Xếp hạng theo doanh thu giao dịch hợp lệ
        </CardDescription>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="flex flex-1 flex-col gap-3">
          {data.categories.length === 0 ? (
            <NoChartData />
          ) : (
            <ChartContainer
              config={config}
              className="aspect-auto h-56 w-full"
              aria-label="Biểu đồ doanh thu theo nhóm sản phẩm"
            >
              <BarChart
                accessibilityLayer
                data={data.categories}
                layout="vertical"
                margin={{ right: 12, top: 0, bottom: 0, left: 0 }}
              >
                <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                <XAxis
                  tick={{ fill: "var(--muted-foreground)" }}
                  type="number"
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={formatCompactMoney}
                />
                <YAxis
                  tick={{ fill: "var(--muted-foreground)" }}
                  dataKey="name"
                  type="category"
                  axisLine={false}
                  tickLine={false}
                  width={108}
                  tickMargin={8}
                />
                <ChartTooltip
                  cursor={false}
                  content={
                    <ChartTooltipContent
                      formatter={(value) => (
                        <span className="font-medium">
                          {formatDashboardMoney(Number(value))}
                        </span>
                      )}
                    />
                  }
                />
                <Bar
                  dataKey="revenue"
                  fill="var(--color-revenue)"
                  radius={[0, 5, 5, 0]}
                  maxBarSize={24}
                  isAnimationActive={false}
                >
                  {data.categories.map((category, index) => (
                    <Cell
                      key={category.id}
                      fill={categoryColors[index % categoryColors.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ChartContainer>
          )}
          <ChartMeta>
            <span>Đơn vị: VNĐ</span>
            <span>Theo nhóm sản phẩm trong bộ lọc</span>
          </ChartMeta>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

export function PredictionChart({ data }: { data: DashboardOverview }) {
  const prediction = data.predictions
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Xác suất mua hàng</CardTitle>
        <CardDescription>
          Kết quả ML riêng
          {prediction.horizon_days
            ? ` · ${prediction.horizon_days} ngày tiếp theo`
            : ""}
        </CardDescription>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="flex flex-1 flex-col gap-3">
          {prediction.status !== "available" ? (
            <NoChartData
              description={
                prediction.status === "not_deployed"
                  ? "Chưa có mô hình được triển khai để dự đoán."
                  : "Chưa có khách hàng đủ dữ liệu để chạy dự đoán."
              }
            />
          ) : (
            <ChartContainer
              config={customerConfig}
              className="aspect-auto h-56 w-full"
              aria-label="Biểu đồ phân bố xác suất mua hàng từ ML"
            >
              <BarChart
                accessibilityLayer
                data={prediction.distribution}
                margin={{ top: 12, right: 4, left: -20, bottom: 0 }}
              >
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis
                  tick={{ fill: "var(--muted-foreground)" }}
                  dataKey="label"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis
                  allowDecimals={false}
                  axisLine={false}
                  tickLine={false}
                />
                <ChartTooltip
                  cursor={false}
                  content={<ChartTooltipContent />}
                />
                <Bar
                  dataKey="count"
                  fill="var(--chart-2)"
                  radius={[5, 5, 0, 0]}
                  maxBarSize={48}
                  isAnimationActive={false}
                />
              </BarChart>
            </ChartContainer>
          )}
          <ChartMeta>
            <span>
              {prediction.evaluated_customers} khách hàng có dự đoán ·{" "}
              {prediction.insufficient_count} chưa đủ dữ liệu
            </span>
            <span>
              {prediction.model_version ?? "Chưa có mô hình"}
              {prediction.prediction_date
                ? ` · ${formatDashboardDate(prediction.prediction_date)}`
                : ""}
            </span>
          </ChartMeta>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

export function OpportunityMatrixChart({ data }: { data: DashboardOverview }) {
  const points = data.opportunity_customers.map((customer) => ({
    ...customer,
    probability: Math.round(customer.purchase_probability * 100),
  }))

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Ma trận cơ hội khách hàng</CardTitle>
        <CardDescription>
          Kết hợp điểm tiềm năng, xác suất mua và doanh thu trong kỳ
        </CardDescription>
      </CardHeader>
      <SquircleCardBody>
        <CardContent className="flex flex-col gap-3">
          {points.length === 0 ? (
            <NoChartData description="Chưa có khách hàng đồng thời đủ dữ liệu chấm điểm và dự đoán." />
          ) : (
            <ChartContainer
              config={opportunityConfig}
              className="aspect-auto h-80 w-full"
              aria-label="Ma trận điểm tiềm năng và xác suất mua của khách hàng"
            >
              <ScatterChart
                accessibilityLayer
                margin={{ top: 12, right: 16, bottom: 8, left: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  dataKey="probability"
                  name="Xác suất mua"
                  unit="%"
                  domain={[0, 100]}
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis
                  type="number"
                  dataKey="potential_score"
                  name="Điểm tiềm năng"
                  domain={[0, 100]}
                  width={36}
                  tickLine={false}
                  axisLine={false}
                />
                <ZAxis
                  type="number"
                  dataKey="revenue"
                  name="Doanh thu"
                  range={[64, 420]}
                />
                <ReferenceLine
                  y={data.potential.thresholds.high}
                  stroke="var(--chart-3)"
                  strokeDasharray="4 4"
                />
                <ReferenceLine
                  y={data.potential.thresholds.potential}
                  stroke="var(--chart-1)"
                  strokeDasharray="4 4"
                />
                <ChartTooltip
                  cursor={{ strokeDasharray: "3 3" }}
                  content={({ active, payload }) => {
                    const point = payload?.[0]?.payload as
                      | (DashboardOpportunityCustomer & {
                          probability: number
                        })
                      | undefined

                    if (!active || !point) return null

                    return (
                      <div className="grid min-w-52 gap-1.5 rounded-lg border border-border/50 bg-background px-2.5 py-2 text-xs shadow-xl">
                        <div className="font-medium">{point.name}</div>
                        <div className="flex justify-between gap-6 text-muted-foreground">
                          <span>Điểm tiềm năng</span>
                          <span className="font-medium text-foreground tabular-nums">
                            {point.potential_score} / 100
                          </span>
                        </div>
                        <div className="flex justify-between gap-6 text-muted-foreground">
                          <span>Xác suất mua</span>
                          <span className="font-medium text-foreground tabular-nums">
                            {point.probability}%
                          </span>
                        </div>
                        <div className="flex justify-between gap-6 text-muted-foreground">
                          <span>Doanh thu trong kỳ</span>
                          <span className="font-medium text-foreground tabular-nums">
                            {formatDashboardMoney(point.revenue)}
                          </span>
                        </div>
                      </div>
                    )
                  }}
                />
                <Scatter
                  data={points}
                  name="Khách hàng"
                  isAnimationActive={false}
                >
                  {points.map((point) => {
                    const segmentIndex = data.segments.findIndex(
                      (segment) => segment.key === point.segment
                    )
                    return (
                      <Cell
                        key={point.id}
                        fill={segmentColors[Math.max(segmentIndex, 0)]}
                        fillOpacity={0.78}
                        stroke="var(--background)"
                        strokeWidth={1}
                      />
                    )
                  })}
                </Scatter>
              </ScatterChart>
            </ChartContainer>
          )}
          <ChartMeta>
            <span>Trục ngang: xác suất mua · Trục dọc: điểm tiềm năng</span>
            <span>
              Kích thước: doanh thu · {points.length} khách hàng đủ dữ liệu
            </span>
          </ChartMeta>
        </CardContent>
      </SquircleCardBody>
    </Card>
  )
}

function ChartMeta({ children }: PropsWithChildren) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-xs text-muted-foreground">
      {children}
    </div>
  )
}
