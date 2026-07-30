import { FullWidthDivider } from "@/components/ui/full-width-divider"
import { Outlet } from "react-router"

export const AuthLayout = () => {
  return (
    <div className="relative flex h-screen items-center justify-center overflow-hidden">
      <div className="flex min-h-screen items-center justify-center border-x">
        <div className="relative">
          <FullWidthDivider position="top" />
          <div className="relative w-full p-6">
            <Outlet />
          </div>
          <FullWidthDivider position="bottom" />
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
