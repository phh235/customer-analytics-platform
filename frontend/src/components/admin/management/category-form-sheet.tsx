import type { FormEvent } from "react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import type { Category, CategoryFormData } from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

export function CategoryFormSheet({
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
  const [form, setForm] = useState({ name: "", code: "" })

  useEffect(() => {
    if (!open) return

    setForm({
      name: category?.name ?? "",
      code: category?.code ?? "",
    })
  }, [category, open])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!form.name.trim() || !form.code.trim()) {
      toastError("Vui lòng nhập tên và mã danh mục")
      return
    }

    onSave({ name: form.name.trim(), code: form.code.trim() })
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="gap-0 sm:max-w-md">
        <SheetHeader>
          <SheetTitle>
            {category ? "Chỉnh sửa danh mục" : "Thêm danh mục mới"}
          </SheetTitle>
          <SheetDescription>
            {category
              ? "Cập nhật tên và mã danh mục đang được sử dụng."
              : "Tạo danh mục để phân loại sản phẩm trong hệ thống."}
          </SheetDescription>
        </SheetHeader>
        <form
          id="category-form-sheet"
          onSubmit={handleSubmit}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="category-name">Tên danh mục</FieldLabel>
              <Input
                id="category-name"
                value={form.name}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Ví dụ: Điện thoại"
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="category-code">Mã danh mục</FieldLabel>
              <Input
                id="category-code"
                value={form.code}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    code: event.target.value,
                  }))
                }
                placeholder="Ví dụ: PHONE"
                required
              />
            </Field>
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Huỷ
          </Button>
          <Button type="submit" form="category-form-sheet">
            {category ? "Lưu thay đổi" : "Thêm danh mục"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
