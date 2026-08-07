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
import { getPostLoginPath } from "@/lib/auth-routing"
import { useAuthStore } from "@/stores/use-auth-store"
import { toastError, toastSuccess } from "@/utils/toast"
import { Link, useLocation, useNavigate } from "react-router"

const formSchema = z.object({
  email: z.string().email("Địa chỉ email không hợp lệ"),
  password: z.string().min(8, "Mật khẩu phải dài ít nhất 8 ký tự"),
})

export const Component = () => {
  const location = useLocation()
  const navigate = useNavigate()
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
      const user = await login(data)
      toastSuccess("Đăng nhập thành công")
      navigate(getPostLoginPath(user.role_code, location.state), {
        replace: true,
      })
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
    <>
      <div className="mt-4 flex flex-col gap-1">
        <p className="text-center text-xl font-semibold">Chào mừng trở lại</p>
        <p className="text-center text-sm text-muted-foreground">
          Đăng nhập để tiếp tục khám phá sản phẩm
        </p>
      </div>
      <form
        aria-busy={isFormDisabled}
        className="mt-6 flex w-full flex-col gap-3"
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
                <FieldLabel htmlFor="login-password">Mật khẩu</FieldLabel>
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
        <Button
          className="w-full"
          type="submit"
          size="lg"
          disabled={isFormDisabled}
        >
          {form.formState.isSubmitting ? (
            <Spinner data-icon="inline-start" />
          ) : null}
          Đăng nhập
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Chưa có tài khoản?{" "}
        <Link
          className="font-medium text-primary underline-offset-4 hover:underline"
          to="/register"
        >
          Đăng ký
        </Link>
        <span className="mx-1">hoặc</span>
        <Link
          className="font-medium text-primary underline-offset-4 hover:underline"
          to="/"
        >
          tìm hiểu thêm
        </Link>
      </p>
    </>
  )
}
