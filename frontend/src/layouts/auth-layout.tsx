import { Outlet } from "react-router"

import { FullWidthDivider } from "@/components/ui/full-width-divider"
import { BRAND_NAME } from "@/lib/brand"
import { MainLogo } from "@/lib/svg"

export const AuthLayout = () => {
  return (
    <div className="relative flex h-screen items-center justify-center overflow-hidden">
      <div className="flex min-h-screen w-full max-w-sm items-center justify-center border-x-0 sm:border-x">
        <div className="relative w-full">
          <FullWidthDivider position="top" className="hidden sm:block" />
          <div className="relative w-full p-6">
            <div className="flex items-center justify-center gap-2">
              <MainLogo className="size-11" />
              <span className="text-xl font-semibold">{BRAND_NAME}</span>
            </div>
            <Outlet />
          </div>
          <FullWidthDivider position="bottom" className="hidden sm:block" />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
