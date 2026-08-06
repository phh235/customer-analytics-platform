import { Trash2Icon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
  const entityLabel = target?.type === "product" ? "sản phẩm" : "khách hàng"

  return (
    <Dialog open={Boolean(target)} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Xác nhận xoá {entityLabel}</DialogTitle>
          <DialogDescription>
            Bạn có chắc muốn xoá <strong>{target?.name}</strong>? Hành động này
            chỉ xoá dữ liệu mẫu khỏi bảng hiện tại.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Huỷ
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            <Trash2Icon data-icon="inline-start" />
            Xác nhận xoá
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
