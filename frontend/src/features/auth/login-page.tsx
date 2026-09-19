import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { InputGroup, InputGroupInput } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import { Spinner } from "@/components/ui/spinner"
import { getApiErrorMessage } from "@/api/errors"
import { useAuthStore } from "@/stores/use-auth-store"
import { cn } from "@/lib/utils"
import { toastError, toastSuccess } from "@/utils/toast"
import { Link } from "react-router"

const formSchema = z.object({
  email: z.string().email("Địa chỉ email không hợp lệ"),
  password: z.string().min(8, "Mật khẩu phải dài ít nhất 8 ký tự"),
})

export const Component = () => {
  const login = useAuthStore((state) => state.login)
  const authStatus = useAuthStore((state) => state.status)
  const form = useForm<z.infer<typeof formSchema>>({
    defaultValues: {
      email: "",
      password: "",
    },
    resolver: zodResolver(formSchema),
  })
  const isSessionPending = authStatus === "unknown" || authStatus === "loading"
  const isFormDisabled = isSessionPending || form.formState.isSubmitting

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    try {
      await login(data)
      toastSuccess("Đăng nhập thành công")
    } catch (error) {
      toastError(
        getApiErrorMessage(
          error,
          "Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin."
        )
      )
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-base font-medium">Chào mừng trở lại!</h1>
        <p className="text-sm leading-6 text-muted-foreground">
          Vui lòng nhập thông tin tài khoản để tiếp tục
        </p>
      </div>
      <form
        aria-busy={isFormDisabled}
        className="flex w-full flex-col gap-4"
        noValidate
        onSubmit={form.handleSubmit(onSubmit)}
      >
        <FieldGroup className="gap-3">
          <Controller
            control={form.control}
            name="email"
            render={({ field, fieldState }) => (
              <Field
                data-disabled={isFormDisabled}
                data-invalid={fieldState.invalid}
              >
                <FieldLabel htmlFor="login-email">Email</FieldLabel>
                <InputGroup className="h-9 w-full">
                  <InputGroupInput
                    id="login-email"
                    aria-invalid={fieldState.invalid}
                    disabled={isFormDisabled}
                    autoComplete="username"
                    placeholder="Email"
                    type="email"
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
              <Field
                data-disabled={isFormDisabled}
                data-invalid={fieldState.invalid}
              >
                <div className="flex items-center justify-between gap-3">
                  <FieldLabel htmlFor="login-password">Mật khẩu</FieldLabel>
                  <Link
                    aria-disabled={isFormDisabled}
                    tabIndex={isFormDisabled ? -1 : undefined}
                    onClick={(event) => {
                      if (isFormDisabled) event.preventDefault()
                    }}
                    className={cn(
                      "text-sm font-medium text-primary underline-offset-4 hover:underline",
                      isFormDisabled && "pointer-events-none opacity-50"
                    )}
                    to="/forgot-password"
                  >
                    Quên mật khẩu?
                  </Link>
                </div>
                <PasswordInput
                  id="login-password"
                  aria-invalid={fieldState.invalid}
                  disabled={isFormDisabled}
                  autoComplete="current-password"
                  className="h-9 w-full"
                  placeholder="Mật khẩu"
                  {...field}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
        </FieldGroup>
        <Button className="h-9 w-full" type="submit" disabled={isFormDisabled}>
          {form.formState.isSubmitting ? (
            <Spinner data-icon="inline-start" />
          ) : null}
          Đăng nhập
        </Button>
      </form>
      <p className="text-center text-sm text-muted-foreground">
        Chưa có tài khoản?{" "}
        <Link
          aria-disabled={isFormDisabled}
          tabIndex={isFormDisabled ? -1 : undefined}
          onClick={(event) => {
            if (isFormDisabled) event.preventDefault()
          }}
          className={cn(
            "font-medium text-primary underline-offset-4 hover:underline",
            isFormDisabled && "pointer-events-none opacity-50"
          )}
          to="/register"
        >
          Đăng ký
        </Link>
        <span className="mx-1">hoặc</span>
        <Link
          aria-disabled={isFormDisabled}
          tabIndex={isFormDisabled ? -1 : undefined}
          onClick={(event) => {
            if (isFormDisabled) event.preventDefault()
          }}
          className={cn(
            "font-medium text-primary underline-offset-4 hover:underline",
            isFormDisabled && "pointer-events-none opacity-50"
          )}
          to="/"
        >
          tìm hiểu thêm
        </Link>
      </p>
    </div>
  )
}
