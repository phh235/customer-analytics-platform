import { Link } from "react-router"

import { ThemeToggle } from "@/components/common/theme-toggle"
import { MobileNav } from "@/components/mobile-nav"
import { Button } from "@/components/ui/button"
import { MainLogo } from "@/lib/svg"

export const navLinks = [
  { label: "Trang chủ", href: "/" },
  { label: "Sản phẩm", href: "/products" },
]

export function Header() {
  return (
    <header className="sticky top-0 z-50 mx-auto w-full border-b border-border bg-background px-2 md:p-0">
      <nav
        aria-label="Điều hướng chính"
        className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between border-x px-4 pl-1"
      >
        <div className="flex items-center gap-6">
          <Link aria-label="Về trang chủ" className="p-2" to="/">
            <MainLogo className="size-8" />
          </Link>
          <div className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => (
              <Button
                key={link.href}
                nativeButton={false}
                render={<Link to={link.href} />}
                variant="ghost"
              >
                {link.label}
              </Button>
            ))}
          </div>
        </div>

        <div className="hidden items-center gap-2 md:flex">
          <Button
            nativeButton={false}
            render={<Link to="/login" />}
            variant="outline"
          >
            Đăng nhập
          </Button>
          <Button nativeButton={false} render={<Link to="/register" />}>
            Đăng ký
          </Button>
          <ThemeToggle />
        </div>

        <MobileNav />
      </nav>
    </header>
  )
}
