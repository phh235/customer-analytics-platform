import type { FormEvent } from "react"
import { useEffect, useState } from "react"

import { AppDialog } from "@/components/common/app-dialog"
import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import type {
  Customer,
  CustomerFormData,
  CustomerStatus,
} from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

export function CustomerFormDialog({
  open,
  onOpenChange,
  customer,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customer: Customer | null
  onSave: (data: CustomerFormData) => void
}) {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    status: "active" as CustomerStatus,
  })

  useEffect(() => {
    if (!open) return

    setForm(
      customer
        ? {
            name: customer.name,
            email: customer.email,
            phone: customer.phone,
            status: customer.status,
          }
        : {
            name: "",
            email: "",
            phone: "",
            status: "active",
          }
    )
  }, [customer, open])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!form.name.trim() || !form.email.trim() || !form.phone.trim()) {
      toastError("Vui lòng nhập đầy đủ thông tin khách hàng")
      return
    }

    onSave({
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      status: form.status,
    })
  }

  return (
    <AppDialog
      open={open}
      onOpenChange={onOpenChange}
      title={customer ? "Chỉnh sửa khách hàng" : "Thêm khách hàng mới"}
      description={
        customer
          ? "Cập nhật thông tin liên hệ và trạng thái tài khoản."
          : "Nhập thông tin cơ bản để tạo hồ sơ khách hàng mẫu."
      }
      className="sm:max-w-lg"
      footer={
        <>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
          >
            Huỷ
          </Button>
          <Button type="submit" form="customer-form-dialog">
            {customer ? "Lưu thay đổi" : "Thêm khách hàng"}
          </Button>
        </>
      }
    >
      <form
        id="customer-form-dialog"
        onSubmit={handleSubmit}
        className="flex flex-col gap-5"
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
    </AppDialog>
  )
}
