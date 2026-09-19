import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { InputGroup, InputGroupInput } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import { Spinner } from "@/components/ui/spinner"
import { registerAccount } from "@/api/auth"
import { getApiErrorMessage } from "@/api/errors"
import { toastError, toastSuccess } from "@/utils/toast"

const formSchema = z
  .object({
    name: z.string().trim().min(2, "Họ và tên phải có ít nhất 2 ký tự"),
    email: z.string().email("Địa chỉ email không hợp lệ"),
    password: z.string().min(8, "Mật khẩu phải dài ít nhất 8 ký tự"),
    confirmPassword: z.string().min(1, "Vui lòng xác nhận mật khẩu"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["confirmPassword"],
  })

export const Component = () => {
  const navigate = useNavigate()
  const form = useForm<z.infer<typeof formSchema>>({
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
    resolver: zodResolver(formSchema),
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      const response = await registerAccount({
        email: values.email.trim().toLowerCase(),
        password: values.password,
        full_name: values.name.trim(),
      })
      toastSuccess(response.message)
      navigate("/login", { replace: true })
    } catch (error) {
      toastError(
        getApiErrorMessage(
          error,
          "Không thể đăng ký tài khoản. Vui lòng thử lại."
        )
      )
    }
  }

  const isSubmitting = form.formState.isSubmitting

  return (
    <>
      <div className="mt-4 flex flex-col gap-1">
        <p className="text-center text-xl font-semibold">Tạo tài khoản</p>
        <p className="text-center text-sm text-muted-foreground">
          Đăng ký để bắt đầu khám phá sản phẩm
        </p>
      </div>
      <form
        className="mt-6 flex w-full flex-col gap-3"
        noValidate
        onSubmit={form.handleSubmit(onSubmit)}
      >
        <Controller
          control={form.control}
          name="name"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="register-name">Họ và tên</FieldLabel>
              <InputGroup className="h-9 w-full">
                <InputGroupInput
                  id="register-name"
                  aria-invalid={fieldState.invalid}
                  autoComplete="name"
                  placeholder="Họ và tên"
                  disabled={isSubmitting}
                  {...field}
                />
              </InputGroup>
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="register-email">Email</FieldLabel>
              <InputGroup className="h-9 w-full">
                <InputGroupInput
                  id="register-email"
                  aria-invalid={fieldState.invalid}
                  autoComplete="email"
                  placeholder="Email"
                  type="email"
                  disabled={isSubmitting}
                  {...field}
                />
              </InputGroup>
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="password"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="register-password">Mật khẩu</FieldLabel>
              <PasswordInput
                id="register-password"
                aria-invalid={fieldState.invalid}
                autoComplete="new-password"
                className="h-9 w-full"
                placeholder="Mật khẩu"
                disabled={isSubmitting}
                {...field}
              />
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Controller
          control={form.control}
          name="confirmPassword"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel htmlFor="register-confirm-password">
                Xác nhận mật khẩu
              </FieldLabel>
              <PasswordInput
                id="register-confirm-password"
                aria-invalid={fieldState.invalid}
                autoComplete="new-password"
                className="h-9 w-full"
                placeholder="Nhập lại mật khẩu"
                disabled={isSubmitting}
                {...field}
              />
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Button
          className="w-full"
          type="submit"
          size="lg"
          disabled={isSubmitting}
        >
          {isSubmitting ? <Spinner data-icon="inline-start" /> : null}
          Đăng ký
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Đã có tài khoản?{" "}
        <Link
          className="font-medium text-primary underline-offset-4 hover:underline"
          to="/login"
        >
          Đăng nhập
        </Link>
      </p>
    </>
  )
}
