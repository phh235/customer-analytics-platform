import { Trash2Icon } from "lucide-react"

import { AppDialog } from "@/components/common/app-dialog"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import type { DeleteTarget } from "@/components/admin/management/types"

export function ConfirmDeleteDialog({
  target,
  onOpenChange,
  onConfirm,
  isLoading = false,
}: {
  target: DeleteTarget | null
  onOpenChange: (open: boolean) => void
  onConfirm: () => void | Promise<void>
  isLoading?: boolean
}) {
  if (!target) return null

  const dialogTarget = target
  const entityLabel =
    dialogTarget?.type === "product"
      ? "sản phẩm"
      : dialogTarget?.type === "customer"
        ? "khách hàng"
        : dialogTarget?.type === "user"
          ? "tài khoản"
          : "đối tượng"

  return (
    <AppDialog
      open={Boolean(target)}
      onOpenChange={onOpenChange}
      title={
        dialogTarget?.type === "user"
          ? "Xác nhận vô hiệu hóa tài khoản"
          : `Xác nhận xoá ${entityLabel}`
      }
      description={
        <>
          {dialogTarget?.type === "user"
            ? `Bạn có chắc muốn vô hiệu hóa tài khoản ${dialogTarget.name}? Người dùng sẽ không thể đăng nhập, nhưng dữ liệu vẫn được giữ lại.`
            : `Bạn có chắc muốn xoá ${dialogTarget?.name}?`}
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
            variant="destructive"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? (
              <Spinner data-icon="inline-start" />
            ) : (
              <Trash2Icon data-icon="inline-start" />
            )}
            {dialogTarget?.type === "user" ? "Vô hiệu hóa" : "Xác nhận xoá"}
          </Button>
        </>
      }
    />
  )
}
