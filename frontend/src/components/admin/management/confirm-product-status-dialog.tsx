import { EyeIcon, EyeOffIcon } from "lucide-react"

import { AppDialog } from "@/components/common/app-dialog"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
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
  isLoading = false,
}: {
  target: ProductStatusTarget | null
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  isLoading?: boolean
}) {
  if (!target) return null

  const displayTarget = target
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
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            Huỷ
          </Button>
          <Button
            variant={willShow ? "default" : "destructive"}
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? (
              <Spinner data-icon="inline-start" />
            ) : willShow ? (
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
