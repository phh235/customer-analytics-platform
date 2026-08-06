import { Trash2Icon } from "lucide-react"

import { AppDialog } from "@/components/common/app-dialog"
import { Button } from "@/components/ui/button"
import type { DeleteTarget } from "@/components/admin/management/types"

export function ConfirmDeleteDialog({
  target,
  onOpenChange,
  onConfirm,
}: {
  target: DeleteTarget | null
  onOpenChange: (open: boolean) => void
  onConfirm: () => void
}) {
  const entityLabel =
    target?.type === "product"
      ? "sản phẩm"
      : target?.type === "customer"
        ? "khách hàng"
        : "danh mục"

  return (
    <AppDialog
      open={Boolean(target)}
      onOpenChange={onOpenChange}
      title={`Xác nhận xoá ${entityLabel}`}
      description={
        <>
          Bạn có chắc muốn xoá <strong>{target?.name}</strong>? Hành động này
          chỉ xoá dữ liệu mẫu khỏi bảng hiện tại.
        </>
      }
      className="sm:max-w-md"
      footer={
        <>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Huỷ
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            <Trash2Icon data-icon="inline-start" />
            Xác nhận xoá
          </Button>
        </>
      }
    />
  )
}
