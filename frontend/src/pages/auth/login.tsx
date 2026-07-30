import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Field, FieldError, FieldLabel } from "@/components/ui/field"
import { InputGroup, InputGroupInput } from "@/components/ui/input-group"
import { PasswordInput } from "@/components/ui/password-input"
import { useNavigate } from "react-router"
import { MainLogo } from "@/lib/svg"

const formSchema = z.object({
  email: z.string().email("Địa chỉ email không hợp lệ"),
  password: z.string().min(8, "Mật khẩu phải dài ít nhất 8 ký tự"),
})

export const Component = () => {
  const navigate = useNavigate()
  const form = useForm<z.infer<typeof formSchema>>({
    defaultValues: {
      email: "",
      password: "",
    },
    resolver: zodResolver(formSchema),
  })

  const onSubmit = (data: z.infer<typeof formSchema>) => {
    console.log(data)
    localStorage.setItem("access_token", "demo-token")
    navigate("/dashboard", { replace: true })
  }

  return (
    <>
      <div className="flex justify-center">
        <MainLogo />
      </div>
      <div className="mt-4 space-y-1">
        <p className="text-center text-xl font-semibold">
          Hệ thống phân tích khách hàng
        </p>
        <p className="text-center text-sm text-muted-foreground">
          Vui lòng nhập thông tin tài khoản để tiếp tục
        </p>
      </div>
      <form
        className="mt-6 w-full space-y-3"
        onSubmit={form.handleSubmit(onSubmit)}
      >
        <Controller
          control={form.control}
          name="email"
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel>Email</FieldLabel>
              <InputGroup className="h-9 w-full">
                <InputGroupInput
                  aria-invalid={fieldState.invalid}
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
            <Field data-invalid={fieldState.invalid}>
              <FieldLabel>Mật khẩu</FieldLabel>
              <PasswordInput
                aria-invalid={fieldState.invalid}
                autoComplete="current-password"
                className="h-9 w-full"
                placeholder="Mật khẩu"
                {...field}
              />
              <FieldError errors={[fieldState.error]} />
            </Field>
          )}
        />
        <Button className="w-full" type="submit" size="lg">
          Đăng nhập
        </Button>
      </form>
    </>
  )
}
