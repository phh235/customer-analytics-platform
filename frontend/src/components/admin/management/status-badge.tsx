import { Badge } from "@/components/ui/badge"
import type {
  CustomerStatus,
  ProductStatus,
} from "@/lib/admin-management"

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
