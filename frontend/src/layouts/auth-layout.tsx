import { Outlet } from "react-router"

import { ShaderBackdrop } from "@/components/auth/shader-backdrop"
import { SquircleSurface } from "@/components/ui/squircle-card"
import { BRAND_NAME } from "@/lib/brand"
import { MainLogo } from "@/lib/svg"

export const AuthLayout = () => {
  return (
    <div className="relative flex min-h-svh items-center justify-center overflow-x-hidden overflow-y-auto bg-[#f6f6f6] ps-(--safe-area-left) pe-(--safe-area-right) pt-[calc(1.5rem+var(--safe-area-top))] pb-[calc(1.5rem+var(--safe-area-bottom))] dark:bg-[#191919]">
      <ShaderBackdrop />
      <div className="relative z-10 flex min-h-[calc(100svh-3rem-var(--safe-area-top)-var(--safe-area-bottom))] w-full max-w-sm items-center justify-center">
        <div className="w-full max-w-sm">
          <div className="rounded-[26px] shadow-[0_1px_2px_rgba(0,0,0,0.06),0_24px_60px_rgba(0,0,0,0.10)] sm:rounded-[32px]">
            <SquircleSurface className="flex flex-col rounded-[26px] border border-border/80 bg-[#f6f6f6] p-1 text-card-foreground [--card-clip-handle:2.25px] [--card-clip-radius:14px] sm:rounded-[32px] sm:[--card-clip-handle:2.5px] sm:[--card-clip-radius:16px] dark:border-border/60 dark:bg-[#191919]">
              <div className="flex h-11 items-center gap-2 pr-3 pl-3.5">
                <MainLogo className="size-7" />
                <span className="text-sm font-medium text-foreground/80">
                  {BRAND_NAME}
                </span>
              </div>

              <SquircleSurface className="relative overflow-hidden rounded-[22px] border border-border/60 bg-white p-6 [--card-clip-radius:12px] sm:rounded-[26px] sm:[--card-clip-radius:14px] dark:bg-[#212121]">
                <Outlet />
              </SquircleSurface>
            </SquircleSurface>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
