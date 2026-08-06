import { useEffect, useState } from "react"
import { EyeIcon, EyeOffIcon } from "lucide-react"

import { AppDialog } from "@/components/common/app-dialog"
import { Button } from "@/components/ui/button"
import type { ProductStatus } from "@/lib/admin-management"

export interface ProductStatusTarget {
  id: string
  name: string
  nextStatus: ProductStatus
}

export function ConfirmProductStatusDialog({
  target,
  onOpenChange,
  onConfirm,
}: {
  target: ProductStatusTarget | null
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
}) {
  const [lastTarget, setLastTarget] = useState<ProductStatusTarget | null>(
    target
  )

  useEffect(() => {
    if (target) setLastTarget(target)
  }, [target])

  const displayTarget = target ?? lastTarget
  const willShow = displayTarget?.nextStatus === "active"
  const actionLabel = willShow ? "hiển thị" : "ẩn"

  return (
    <AppDialog
      open={Boolean(target)}
      onOpenChange={onOpenChange}
      title={`${willShow ? "Hiển thị" : "Ẩn"} sản phẩm`}
      description={
        <>
          Bạn có chắc muốn {actionLabel} <strong>{displayTarget?.name}</strong>?
          Sản phẩm sẽ {willShow ? "được hiển thị" : "không còn hiển thị"} trong
          danh sách bán hàng.
        </>
      }
      className="sm:max-w-md"
      footer={
        <>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Huỷ
          </Button>
          <Button
            variant={willShow ? "default" : "destructive"}
            onClick={onConfirm}
          >
            {willShow ? (
              <EyeIcon data-icon="inline-start" />
            ) : (
              <EyeOffIcon data-icon="inline-start" />
            )}
            {willShow ? "Hiển thị sản phẩm" : "Ẩn sản phẩm"}
          </Button>
        </>
      }
    />
  )
}
