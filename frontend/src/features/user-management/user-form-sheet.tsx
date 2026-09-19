import { useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"

import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { PasswordInput } from "@/components/ui/password-input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Spinner } from "@/components/ui/spinner"
import {
  MANAGEABLE_USER_ROLES,
  USER_ROLES,
  USER_ROLE_LABELS,
  USER_STATUSES,
  type User,
} from "@/types/user"
import type { UserFormData } from "@/types/user-management"

const formSchema = z.object({
  email: z.string().trim().email("Địa chỉ email không hợp lệ"),
  full_name: z
    .string()
    .trim()
    .min(1, "Vui lòng nhập họ và tên")
    .max(100, "Họ và tên không được vượt quá 100 ký tự"),
  password: z.string().optional(),
  role_code: z.enum(USER_ROLES),
  status: z.enum(USER_STATUSES),
})

type UserFormValues = z.infer<typeof formSchema>

interface UserFormSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user: User | null
  onSave: (data: UserFormData) => Promise<void>
}

export function UserFormSheet({
  open,
  onOpenChange,
  user,
  onSave,
}: UserFormSheetProps) {
  const form = useForm<UserFormValues>({
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      role_code: "USER",
      status: "ACTIVE",
    },
    resolver: zodResolver(formSchema),
  })

  useEffect(() => {
    if (!open) return

    form.reset({
      email: user?.email ?? "",
      full_name: user?.full_name ?? "",
      password: "",
      role_code:
        user?.role_code === "CLIENT" ? "USER" : (user?.role_code ?? "USER"),
      status: user?.status ?? "ACTIVE",
    })
  }, [form, open, user])

  const handleSubmit = async (values: UserFormValues) => {
    if (!user && (!values.password || values.password.length < 8)) {
      form.setError("password", {
        type: "manual",
        message: "Mật khẩu phải dài ít nhất 8 ký tự",
      })
      return
    }

    await onSave({
      email: values.email.trim().toLowerCase(),
      full_name: values.full_name.trim(),
      password: values.password || undefined,
      role_code: values.role_code,
      status: values.status,
    })
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="gap-0 sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>
            {user ? "Chỉnh sửa tài khoản" : "Thêm tài khoản mới"}
          </SheetTitle>
          <SheetDescription>
            {user
              ? "Cập nhật thông tin và quyền truy cập của tài khoản."
              : "Tạo tài khoản người dùng, phân tích hoặc quản trị hệ thống."}
          </SheetDescription>
        </SheetHeader>
        <form
          id="user-form-sheet"
          onSubmit={form.handleSubmit(handleSubmit)}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Controller
              control={form.control}
              name="full_name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="user-full-name">Họ và tên</FieldLabel>
                  <Input
                    id="user-full-name"
                    autoComplete="name"
                    placeholder="Ví dụ: Nguyễn Văn An"
                    aria-invalid={fieldState.invalid}
                    disabled={form.formState.isSubmitting}
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
                  <FieldLabel htmlFor="user-email">Email</FieldLabel>
                  <Input
                    id="user-email"
                    type="email"
                    autoComplete="email"
                    placeholder="user@example.com"
                    disabled={Boolean(user) || form.formState.isSubmitting}
                    aria-invalid={fieldState.invalid}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            {!user && (
              <Controller
                control={form.control}
                name="password"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="user-password">
                      Mật khẩu tạm thời
                    </FieldLabel>
                    <PasswordInput
                      id="user-password"
                      autoComplete="new-password"
                      placeholder="Ít nhất 8 ký tự"
                      aria-invalid={fieldState.invalid}
                      disabled={form.formState.isSubmitting}
                      {...field}
                    />
                    <FieldDescription>
                      Người dùng có thể đổi mật khẩu sau khi đăng nhập.
                    </FieldDescription>
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
            )}
            <Controller
              control={form.control}
              name="role_code"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="user-role">Vai trò</FieldLabel>
                  <AppSelect
                    id="user-role"
                    value={field.value}
                    onChange={(value) => field.onChange(value)}
                    disabled={form.formState.isSubmitting}
                    aria-label="Chọn vai trò tài khoản"
                    className="w-full"
                    options={MANAGEABLE_USER_ROLES.map((role) => ({
                      value: role,
                      label: USER_ROLE_LABELS[role],
                    }))}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            {user && (
              <Controller
                control={form.control}
                name="status"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="user-status">Trạng thái</FieldLabel>
                    <AppSelect
                      id="user-status"
                      value={field.value}
                      onChange={(value) => field.onChange(value)}
                      disabled={form.formState.isSubmitting}
                      aria-label="Chọn trạng thái tài khoản"
                      className="w-full"
                      options={USER_STATUSES.map((status) => ({
                        value: status,
                        label:
                          status === "ACTIVE"
                            ? "Đang hoạt động"
                            : status === "DISABLED"
                              ? "Đã vô hiệu hóa"
                              : "Đang bị khóa",
                      }))}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
            )}
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={form.formState.isSubmitting}
          >
            Huỷ
          </Button>
          <Button
            type="submit"
            form="user-form-sheet"
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting && (
              <Spinner data-icon="inline-start" />
            )}
            {user ? "Lưu thay đổi" : "Tạo tài khoản"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
