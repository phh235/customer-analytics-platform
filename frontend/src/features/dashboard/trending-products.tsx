import { useState } from "react"
import {
  ArrowDownRightIcon,
  ArrowUpRightIcon,
  SparklesIcon,
} from "lucide-react"

import type { TrendingProduct } from "@/api/product-analytics"
import {
  CommonTable,
  type CommonTableColumn,
} from "@/components/common/common-table"
import { Badge } from "@/components/ui/badge"
import {
  CardAction,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { SquircleCard, SquircleCardBody } from "@/components/ui/squircle-card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useTrendingProducts } from "@/hooks/use-product-analytics"

const columns: CommonTableColumn<TrendingProduct>[] = [
  {
    id: "product",
    header: "Sản phẩm",
    className: "min-w-56",
    cell: (product) => (
      <div>
        <p className="font-medium">{product.productName}</p>
        <p className="text-xs text-muted-foreground">{product.productCode}</p>
      </div>
    ),
  },
  {
    id: "currentViews",
    header: "Lượt xem kỳ này",
    cell: (product) => (
      <span className="font-medium tabular-nums">{product.currentViews}</span>
    ),
  },
  {
    id: "previousViews",
    header: "Kỳ trước",
    cell: (product) => (
      <span className="text-muted-foreground tabular-nums">
        {product.previousViews}
      </span>
    ),
  },
  {
    id: "growth",
    header: "Tăng trưởng",
    cell: (product) => {
      if (product.trendStatus === "NEW_TREND") {
        return (
          <Badge variant="info">
            <SparklesIcon />
            Xu hướng mới
          </Badge>
        )
      }
      const growth = product.growthPercent ?? 0
      return (
        <Badge
          variant={
            growth > 0 ? "success" : growth < 0 ? "destructive" : "secondary"
          }
        >
          {growth >= 0 ? <ArrowUpRightIcon /> : <ArrowDownRightIcon />}
          {growth > 0 ? "+" : ""}
          {growth.toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%
        </Badge>
      )
    },
  },
]

export function TrendingProducts() {
  const [period, setPeriod] = useState<"7D" | "30D">("7D")
  const query = useTrendingProducts(period)

  return (
    <SquircleCard>
      <CardHeader>
        <CardTitle>Sản phẩm xu hướng</CardTitle>
        <CardDescription>
          So sánh lượt xem {period === "7D" ? "7 ngày" : "30 ngày"} gần nhất với
          kỳ liền trước
        </CardDescription>
        <CardAction>
          <Tabs
            value={period}
            onValueChange={(value) => setPeriod(value as "7D" | "30D")}
          >
            <TabsList aria-label="Khoảng thời gian xu hướng">
              <TabsTrigger value="7D">7 ngày</TabsTrigger>
              <TabsTrigger value="30D">30 ngày</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardAction>
      </CardHeader>
      <SquircleCardBody className="py-0">
        <CommonTable
          variant="embedded"
          data={query.data?.items ?? []}
          columns={columns}
          loading={query.isPending}
          getRowId={(product) => product.productId}
          emptyMessage="Chưa có sản phẩm xu hướng trong kỳ này."
          itemLabel="sản phẩm xu hướng"
        />
      </SquircleCardBody>
    </SquircleCard>
  )
}
