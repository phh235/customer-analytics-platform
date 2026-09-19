import { useEffect, useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp"
import { PasswordInput } from "@/components/ui/password-input"
import { Spinner } from "@/components/ui/spinner"
import {
  requestForgotPassword,
  resetForgottenPassword,
  verifyForgotPassword,
} from "@/api/auth"
import { getApiErrorMessage } from "@/api/errors"
import { toastError, toastSuccess } from "@/utils/toast"

const emailSchema = z.object({
  email: z.string().trim().email("Địa chỉ email không hợp lệ"),
})

const otpSchema = z.object({
  otp: z.string().regex(/^\d{6}$/, "Vui lòng nhập đủ mã OTP gồm 6 số"),
})

const passwordSchema = z
  .object({
    password: z.string().min(8, "Mật khẩu phải dài ít nhất 8 ký tự"),
    confirmPassword: z.string().min(1, "Vui lòng xác nhận mật khẩu mới"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Mật khẩu xác nhận không khớp",
    path: ["confirmPassword"],
  })

type RecoveryStep = "email" | "otp" | "password"

const STEP_CONTENT: Record<
  RecoveryStep,
  { title: string; description: string; number: number }
> = {
  email: {
    title: "Quên mật khẩu",
    description: "Nhập email của tài khoản để nhận mã xác thực.",
    number: 1,
  },
  otp: {
    title: "Nhập mã xác thực",
    description: "Nhập mã OTP gồm 6 số đã được gửi đến email của bạn.",
    number: 2,
  },
  password: {
    title: "Tạo mật khẩu mới",
    description: "Mật khẩu mới phải có ít nhất 8 ký tự.",
    number: 3,
  },
}

export function PasswordRecoveryPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState<RecoveryStep>("email")
  const [email, setEmail] = useState("")
  const [resetToken, setResetToken] = useState("")
  const [retryAfter, setRetryAfter] = useState(0)
  const content = STEP_CONTENT[step]
  const emailForm = useForm<z.infer<typeof emailSchema>>({
    defaultValues: { email: "" },
    resolver: zodResolver(emailSchema),
  })
  const otpForm = useForm<z.infer<typeof otpSchema>>({
    defaultValues: { otp: "" },
    resolver: zodResolver(otpSchema),
  })
  const passwordForm = useForm<z.infer<typeof passwordSchema>>({
    defaultValues: { password: "", confirmPassword: "" },
    resolver: zodResolver(passwordSchema),
  })

  useEffect(() => {
    if (retryAfter <= 0) return
    const interval = window.setInterval(
      () => setRetryAfter((seconds) => Math.max(0, seconds - 1)),
      1000
    )
    return () => window.clearInterval(interval)
  }, [retryAfter])

  const handleEmailSubmit = async ({
    email: value,
  }: z.infer<typeof emailSchema>) => {
    const normalizedEmail = value.trim().toLowerCase()
    try {
      const response = await requestForgotPassword(normalizedEmail)
      setEmail(normalizedEmail)
      setRetryAfter(response.retry_after)
      toastSuccess(response.message)
      setStep("otp")
    } catch (error) {
      toastError(getApiErrorMessage(error, "Không thể gửi mã OTP."))
    }
  }

  const handleOtpSubmit = async ({ otp }: z.infer<typeof otpSchema>) => {
    try {
      const response = await verifyForgotPassword(email, otp)
      setResetToken(response.reset_token)
      setStep("password")
    } catch (error) {
      toastError(
        getApiErrorMessage(error, "Mã OTP không hợp lệ hoặc đã hết hạn.")
      )
    }
  }

  const handlePasswordSubmit = async ({
    password,
  }: z.infer<typeof passwordSchema>) => {
    if (!resetToken) {
      setStep("otp")
      return
    }
    try {
      const response = await resetForgottenPassword(resetToken, password)
      toastSuccess(response.message)
      navigate("/login", { replace: true })
    } catch (error) {
      toastError(getApiErrorMessage(error, "Không thể đặt lại mật khẩu."))
    }
  }

  const handleResendOtp = async () => {
    if (!email || retryAfter > 0) return
    try {
      const response = await requestForgotPassword(email)
      setRetryAfter(response.retry_after)
      otpForm.reset()
      toastSuccess(response.message)
    } catch (error) {
      toastError(getApiErrorMessage(error, "Không thể gửi lại mã OTP."))
    }
  }

  return (
    <>
      <div className="mt-4 flex flex-col gap-1 text-center">
        <p className="text-xs font-medium text-muted-foreground">
          Bước {content.number} / 3
        </p>
        <h1 className="text-xl font-semibold">{content.title}</h1>
        <p className="text-sm text-muted-foreground">{content.description}</p>
      </div>

      {step === "email" ? (
        <form
          className="mt-6 flex flex-col gap-4"
          noValidate
          onSubmit={emailForm.handleSubmit(handleEmailSubmit)}
        >
          <Controller
            control={emailForm.control}
            name="email"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="recovery-email">Email</FieldLabel>
                <Input
                  id="recovery-email"
                  type="email"
                  autoComplete="email"
                  placeholder="name@example.com"
                  aria-invalid={fieldState.invalid}
                  disabled={emailForm.formState.isSubmitting}
                  {...field}
                />
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
          <Button
            type="submit"
            size="lg"
            disabled={emailForm.formState.isSubmitting}
          >
            {emailForm.formState.isSubmitting ? (
              <Spinner data-icon="inline-start" />
            ) : null}
            Tiếp tục
          </Button>
        </form>
      ) : null}

      {step === "otp" ? (
        <form
          className="mt-6 flex flex-col gap-4"
          noValidate
          onSubmit={otpForm.handleSubmit(handleOtpSubmit)}
        >
          <Controller
            control={otpForm.control}
            name="otp"
            render={({ field, fieldState }) => (
              <Field data-invalid={fieldState.invalid}>
                <FieldLabel htmlFor="recovery-otp">Mã OTP</FieldLabel>
                <InputOTP
                  id="recovery-otp"
                  aria-label="Mã OTP"
                  aria-invalid={fieldState.invalid}
                  maxLength={6}
                  inputMode="numeric"
                  pattern="[0-9]*"
                  disabled={otpForm.formState.isSubmitting}
                  containerClassName="justify-center"
                  {...field}
                >
                  <InputOTPGroup>
                    {Array.from({ length: 6 }, (_, index) => (
                      <InputOTPSlot index={index} key={index} />
                    ))}
                  </InputOTPGroup>
                </InputOTP>
                <FieldError errors={[fieldState.error]} />
              </Field>
            )}
          />
          <p className="text-center text-xs text-muted-foreground">
            Mã xác thực được gửi đến {email}
          </p>
          <Button
            type="submit"
            size="lg"
            disabled={otpForm.formState.isSubmitting}
          >
            {otpForm.formState.isSubmitting ? (
              <Spinner data-icon="inline-start" />
            ) : null}
            Xác nhận mã
          </Button>
          <div className="flex justify-between gap-2 text-sm">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={otpForm.formState.isSubmitting}
              onClick={() => setStep("email")}
            >
              Đổi email
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              disabled={retryAfter > 0 || otpForm.formState.isSubmitting}
              onClick={() => void handleResendOtp()}
            >
              {retryAfter > 0 ? `Gửi lại sau ${retryAfter}s` : "Gửi lại mã"}
            </Button>
          </div>
        </form>
      ) : null}

      {step === "password" ? (
        <form
          className="mt-6 flex flex-col gap-4"
          noValidate
          onSubmit={passwordForm.handleSubmit(handlePasswordSubmit)}
        >
          <FieldGroup className="gap-3">
            <Controller
              control={passwordForm.control}
              name="password"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="new-password">Mật khẩu mới</FieldLabel>
                  <PasswordInput
                    id="new-password"
                    autoComplete="new-password"
                    placeholder="Ít nhất 8 ký tự"
                    aria-invalid={fieldState.invalid}
                    disabled={passwordForm.formState.isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <Controller
              control={passwordForm.control}
              name="confirmPassword"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="confirm-new-password">
                    Xác nhận mật khẩu mới
                  </FieldLabel>
                  <PasswordInput
                    id="confirm-new-password"
                    autoComplete="new-password"
                    placeholder="Nhập lại mật khẩu mới"
                    aria-invalid={fieldState.invalid}
                    disabled={passwordForm.formState.isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
          </FieldGroup>
          <Button
            type="submit"
            size="lg"
            disabled={passwordForm.formState.isSubmitting}
          >
            {passwordForm.formState.isSubmitting ? (
              <Spinner data-icon="inline-start" />
            ) : null}
            Đặt lại mật khẩu
          </Button>
        </form>
      ) : null}

      <p className="mt-4 text-center text-sm text-muted-foreground">
        <Link
          className="font-medium text-primary underline-offset-4 hover:underline"
          to="/login"
        >
          Quay lại đăng nhập
        </Link>
      </p>
    </>
  )
}

export default PasswordRecoveryPage
