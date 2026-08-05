import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { InputGroup, InputGroupInput } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import { MainLogo } from "@/lib/svg"

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

  const onSubmit = () => {
    navigate("/login", { replace: true })
  }

  return (
    <>
      <div className="flex justify-center">
        <MainLogo />
      </div>
      <div className="mt-4 space-y-1">
        <p className="text-center text-xl font-semibold">Tạo tài khoản</p>
        <p className="text-center text-sm text-muted-foreground">
          Đăng ký để bắt đầu phân tích khách hàng
        </p>
      </div>
      <form
        className="mt-6 w-full space-y-3"
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
                {...field}
              />
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Button className="w-full" type="submit" size="lg">
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
