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
          <div
            className="pointer-events-none absolute inset-0 -top-px -left-px z-0"
            style={{
              backgroundImage: `
              linear-gradient(to right, color-mix(in srgb, var(--card-foreground) 8%, transparent) 1px, transparent 1px),
              linear-gradient(to bottom, color-mix(in srgb, var(--card-foreground) 8%, transparent) 1px, transparent 1px)
      `,
              backgroundSize: "20px 20px",
              backgroundPosition: "0 0, 0 0",
              maskImage: `
              repeating-linear-gradient(
              to right,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            repeating-linear-gradient(
              to bottom,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            radial-gradient(ellipse 70% 50% at 50% 0%, #000 60%, transparent 100%)
      `,
              WebkitMaskImage: `
              repeating-linear-gradient(
              to right,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            repeating-linear-gradient(
              to bottom,
              black 0px,
              black 3px,
              transparent 3px,
              transparent 8px
            ),
            radial-gradient(ellipse 70% 50% at 50% 0%, #000 60%, transparent 100%)
      `,
              maskComposite: "intersect",
              WebkitMaskComposite: "source-in",
            }}
          />
          <Outlet />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
