import { Outlet } from "react-router"
import { ThemeToggle } from "@/components/common/theme-toggle"

export const AuthLayout = () => {
  return (
    <div className="relative flex h-screen items-center justify-center">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className="flex min-h-screen items-center justify-center">
        <div className="relative w-full max-w-sm overflow-hidden rounded-xl border bg-linear-to-b from-muted/50 to-card px-8 py-8 shadow-lg/5 dark:from-transparent dark:shadow-xl">
          <div className="pointer-events-none absolute inset-0 -top-px -left-px z-0 auth-grid-mask" />
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
