import type { FormEvent } from "react"
import { useEffect, useState } from "react"

import { AppDialog } from "@/components/common/app-dialog"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import type { Category, CategoryFormData } from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

export function CategoryFormDialog({
  open,
  onOpenChange,
  category,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  category: Category | null
  onSave: (data: CategoryFormData) => void
}) {
  const [name, setName] = useState("")

  useEffect(() => {
    if (open) setName(category?.name ?? "")
  }, [category, open])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!name.trim()) {
      toastError("Vui lòng nhập tên danh mục")
      return
    }

    onSave({ name: name.trim() })
  }

  return (
    <AppDialog
      open={open}
      onOpenChange={onOpenChange}
      title={category ? "Chỉnh sửa danh mục" : "Thêm danh mục mới"}
      description={
        category
          ? "Cập nhật tên danh mục đang được sử dụng."
          : "Tạo danh mục để phân loại sản phẩm trong hệ thống."
      }
      className="sm:max-w-md"
      footer={
        <>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Huỷ
          </Button>
          <Button type="submit" form="category-form-dialog">
            {category ? "Lưu thay đổi" : "Thêm danh mục"}
          </Button>
        </>
      }
    >
      <form
        id="category-form-dialog"
        onSubmit={handleSubmit}
        className="flex flex-col gap-5"
      >
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="category-name">Tên danh mục</FieldLabel>
            <Input
              id="category-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Ví dụ: Điện thoại"
              required
            />
          </Field>
        </FieldGroup>
      </form>
    </AppDialog>
  )
}
