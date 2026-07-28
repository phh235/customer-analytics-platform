import { Link } from "react-router"
import { CompassIcon, HomeIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyTitle,
} from "@/components/ui/empty"

export function Component() {
  return (
    <main className="relative isolate flex min-h-svh w-full items-center justify-center overflow-hidden bg-[radial-gradient(circle_at_center,rgba(99,102,241,0.16),transparent_70%)] text-foreground">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <div className="absolute top-1/2 left-[40%] size-90 -translate-1/2 rounded-full bg-linear-to-tr from-purple-500/30 to-blue-500/30 blur-3xl" />
        <div className="absolute top-1/2 left-[60%] size-100 -translate-1/2 rounded-full bg-linear-to-br from-indigo-400/20 to-pink-400/20 blur-3xl" />
      </div>

      <Empty className="relative z-10">
        <EmptyHeader>
          <EmptyTitle className="text-8xl font-extrabold text-primary">
            404
          </EmptyTitle>
          <EmptyDescription className="max-w-md text-base sm:text-lg">
            Rất tiếc, trang bạn đang tìm kiếm không tồn tại hoặc đã được chuyển
            sang địa chỉ khác.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button size="lg" render={<Link to="/dashboard" />}>
              <HomeIcon data-icon="inline-start" />
              Về tổng quan
            </Button>
            <Button variant="secondary" size="lg" render={<Link to="/login" />}>
              <CompassIcon data-icon="inline-start" />
              Đăng nhập
            </Button>
          </div>
        </EmptyContent>
      </Empty>
    </main>
  )
}
