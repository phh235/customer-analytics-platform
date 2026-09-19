import type { ComponentProps } from "react"

import { Badge } from "@/components/ui/badge"
import {
  ORDER_STATUS_LABELS,
  type CustomerStatus,
  type ProductStatus,
} from "@/lib/admin-management"
import { formatEnumLabel } from "@/lib/format"

type BadgeVariant = NonNullable<ComponentProps<typeof Badge>["variant"]>

const ORDER_STATUS_VARIANTS: Record<string, BadgeVariant> = {
  PAID: "info",
  PROCESSING: "warning",
  COMPLETED: "success",
  DELIVERED: "success",
  CANCELED: "destructive",
  CANCELLED: "destructive",
  FAILED: "destructive",
  RETURNED: "destructive",
  REFUNDED: "secondary",
  PARTIAL_REFUNDED: "secondary",
}

export function StatusBadge({
  status,
  entity,
}: {
  status: ProductStatus | CustomerStatus
  entity: "product" | "customer"
}) {
  const isActive = status === "active"

  return (
    <Badge variant={isActive ? "success" : "secondary"}>
      {isActive
        ? entity === "product"
          ? "Đang bán"
          : "Đang hoạt động"
        : entity === "product"
          ? "Tạm ẩn"
          : "Không hoạt động"}
    </Badge>
  )
}

export function OrderStatusBadge({ status }: { status: string }) {
  const normalizedStatus = status.trim().toUpperCase()

  return (
    <Badge variant={ORDER_STATUS_VARIANTS[normalizedStatus] ?? "outline"}>
      {formatEnumLabel(normalizedStatus, ORDER_STATUS_LABELS)}
    </Badge>
  )
}
