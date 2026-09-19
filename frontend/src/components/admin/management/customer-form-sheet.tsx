import { useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"

import { ImageFileField } from "@/components/admin/management/image-file-field"
import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Spinner } from "@/components/ui/spinner"
import type { Customer, CustomerFormData } from "@/lib/admin-management"

const customerFormSchema = z.object({
  name: z.string().trim().min(1, "Vui lòng nhập họ và tên"),
  email: z.string().trim().email("Địa chỉ email không hợp lệ"),
  phone: z.string().trim().min(1, "Vui lòng nhập số điện thoại"),
  status: z.enum(["active", "inactive"]),
  image: z.instanceof(File).nullable(),
})

type CustomerFormValues = z.infer<typeof customerFormSchema>

const getDefaultValues = (customer: Customer | null): CustomerFormValues => ({
  name: customer?.name ?? "",
  email: customer?.email ?? "",
  phone: customer?.phone ?? "",
  status: customer?.status ?? "active",
  image: null,
})

export function CustomerFormSheet({
  open,
  onOpenChange,
  customer,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  customer: Customer | null
  onSave: (data: CustomerFormData) => void | Promise<unknown>
}) {
  const form = useForm<CustomerFormValues>({
    defaultValues: getDefaultValues(customer),
    resolver: zodResolver(customerFormSchema),
  })

  useEffect(() => {
    if (open) form.reset(getDefaultValues(customer))
  }, [customer, form, open])

  const handleSubmit = async (values: CustomerFormValues) => {
    await onSave({
      ...values,
      name: values.name.trim(),
      email: values.email.trim(),
      phone: values.phone.trim(),
    })
    onOpenChange(false)
  }

  const isSubmitting = form.formState.isSubmitting

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
              : "Nhập thông tin cơ bản để tạo hồ sơ khách hàng."}
          </SheetDescription>
        </SheetHeader>
        <form
          id="customer-form-sheet"
          onSubmit={form.handleSubmit(handleSubmit)}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Controller
              control={form.control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="customer-name">Họ và tên</FieldLabel>
                  <Input
                    id="customer-name"
                    autoComplete="name"
                    placeholder="Ví dụ: Nguyễn Minh Anh"
                    aria-invalid={fieldState.invalid}
                    disabled={isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <Controller
              control={form.control}
              name="email"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="customer-email">Email</FieldLabel>
                  <Input
                    id="customer-email"
                    type="email"
                    autoComplete="email"
                    placeholder="khachhang@example.com"
                    aria-invalid={fieldState.invalid}
                    disabled={isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <Controller
              control={form.control}
              name="image"
              render={({ field }) => (
                <ImageFileField
                  id="customer-image"
                  label="Ảnh khách hàng"
                  previewUrl={customer?.imageUrl ?? undefined}
                  previewAlt={customer?.name ?? "Khách hàng"}
                  previewClassName="w-32 rounded-full"
                  selectedFile={field.value}
                  onFileChange={field.onChange}
                  disabled={isSubmitting}
                />
              )}
            />
            <FieldGroup className="grid gap-4 sm:grid-cols-2">
              <Controller
                control={form.control}
                name="phone"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="customer-phone">
                      Số điện thoại
                    </FieldLabel>
                    <Input
                      id="customer-phone"
                      type="tel"
                      autoComplete="tel"
                      placeholder="0901 234 567"
                      aria-invalid={fieldState.invalid}
                      disabled={isSubmitting}
                      {...field}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Controller
                control={form.control}
                name="status"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="customer-status">
                      Trạng thái
                    </FieldLabel>
                    <AppSelect
                      id="customer-status"
                      value={field.value}
                      onChange={field.onChange}
                      disabled={isSubmitting}
                      className="w-full"
                      aria-label="Chọn trạng thái khách hàng"
                      options={[
                        { value: "active", label: "Đang hoạt động" },
                        { value: "inactive", label: "Không hoạt động" },
                      ]}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
            </FieldGroup>
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Huỷ
          </Button>
          <Button
            type="submit"
            form="customer-form-sheet"
            disabled={isSubmitting}
          >
            {isSubmitting && <Spinner data-icon="inline-start" />}
            {customer ? "Lưu thay đổi" : "Thêm khách hàng"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
