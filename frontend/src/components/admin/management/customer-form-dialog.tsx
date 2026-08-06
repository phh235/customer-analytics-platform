import type { FormEvent } from "react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <DialogHeader>
            <DialogTitle>
              {customer ? "Chỉnh sửa khách hàng" : "Thêm khách hàng mới"}
            </DialogTitle>
            <DialogDescription>
              {customer
                ? "Cập nhật thông tin liên hệ và trạng thái tài khoản."
                : "Nhập thông tin cơ bản để tạo hồ sơ khách hàng mẫu."}
            </DialogDescription>
          </DialogHeader>

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
                <Select
                  value={form.status}
                  onValueChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      status: (value ?? "active") as CustomerStatus,
                    }))
                  }
                >
                  <SelectTrigger id="customer-status" className="w-full">
                    <SelectValue>
                      {form.status === "active"
                        ? "Đang hoạt động"
                        : "Không hoạt động"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="active">Đang hoạt động</SelectItem>
                      <SelectItem value="inactive">Không hoạt động</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>
            </FieldGroup>
          </FieldGroup>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Huỷ
            </Button>
            <Button type="submit">
              {customer ? "Lưu thay đổi" : "Thêm khách hàng"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
