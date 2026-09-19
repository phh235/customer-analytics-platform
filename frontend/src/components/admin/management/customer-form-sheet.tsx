import type { FormEvent } from "react"
import { useState } from "react"

import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import type {
  Customer,
  CustomerFormData,
  CustomerStatus,
} from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

export function CustomerFormSheet({
  open,
  onOpenChange,
  customer,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customer: Customer | null
  onSave: (data: CustomerFormData) => void | Promise<void>
}) {
  const [form, setForm] = useState(() =>
    customer
      ? {
          name: customer.name,
          email: customer.email,
          phone: customer.phone,
          status: customer.status,
          image: null as File | null,
        }
      : {
          name: "",
          email: "",
          phone: "",
          status: "active" as CustomerStatus,
          image: null as File | null,
        }
  )
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!form.name.trim() || !form.email.trim() || !form.phone.trim()) {
      toastError("Vui lòng nhập đầy đủ thông tin khách hàng")
      return
    }

    setSaving(true)
    try {
      await onSave({
        name: form.name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim(),
        status: form.status,
        image: form.image,
      })
      onOpenChange(false)
    } catch {
      // The parent displays the API error; keep the sheet open for correction.
    } finally {
      setSaving(false)
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="gap-0 sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>
            {customer ? "Chỉnh sửa khách hàng" : "Thêm khách hàng mới"}
          </SheetTitle>
          <SheetDescription>
            {customer
              ? "Cập nhật thông tin liên hệ và trạng thái tài khoản."
              : "Nhập thông tin cơ bản để tạo hồ sơ khách hàng mẫu."}
          </SheetDescription>
        </SheetHeader>
        <form
          id="customer-form-sheet"
          onSubmit={handleSubmit}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="customer-name">Họ và tên</FieldLabel>
              <Input
                id="customer-name"
                value={form.name}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Ví dụ: Nguyễn Minh Anh"
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="customer-email">Email</FieldLabel>
              <Input
                id="customer-email"
                type="email"
                value={form.email}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    email: event.target.value,
                  }))
                }
                placeholder="khachhang@example.com"
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="customer-image">Ảnh khách hàng</FieldLabel>
              {customer?.imageUrl ? (
                <img
                  src={customer.imageUrl}
                  alt={customer.name}
                  className="h-32 w-32 rounded-full border object-cover"
                />
              ) : null}
              <Input
                id="customer-image"
                type="file"
                accept="image/*"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null
                  if (file && !file.type.startsWith("image/")) {
                    toastError("Vui lòng chọn một tệp ảnh")
                    event.currentTarget.value = ""
                    return
                  }
                  if (file && file.size > 10 * 1024 * 1024) {
                    toastError("Ảnh không được vượt quá 10 MB")
                    event.currentTarget.value = ""
                    return
                  }
                  setForm((current) => ({ ...current, image: file }))
                }}
              />
              <p className="text-xs text-muted-foreground">
                JPG, PNG, WEBP; tối đa 10 MB.
                {form.image ? ` Đã chọn: ${form.image.name}` : ""}
              </p>
            </Field>
            <FieldGroup className="grid gap-4 sm:grid-cols-2">
              <Field>
                <FieldLabel htmlFor="customer-phone">Số điện thoại</FieldLabel>
                <Input
                  id="customer-phone"
                  type="tel"
                  value={form.phone}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      phone: event.target.value,
                    }))
                  }
                  placeholder="0901 234 567"
                  required
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="customer-status">Trạng thái</FieldLabel>
                <AppSelect
                  options={[
                    { value: "active", label: "Đang hoạt động" },
                    { value: "inactive", label: "Không hoạt động" },
                  ]}
                  value={form.status}
                  onChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      status: value as CustomerStatus,
                    }))
                  }
                  id="customer-status"
                  className="w-full"
                  aria-label="Chọn trạng thái khách hàng"
                />
              </Field>
            </FieldGroup>
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={saving}
          >
            Huỷ
          </Button>
          <Button type="submit" form="customer-form-sheet" disabled={saving}>
            {saving
              ? "Đang lưu..."
              : customer
                ? "Lưu thay đổi"
                : "Thêm khách hàng"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
