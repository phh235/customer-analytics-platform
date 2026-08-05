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
    <header className="sticky top-0 z-50 mx-auto w-full max-w-6xl bg-background">
      <nav
        aria-label="Điều hướng chính"
        className="flex h-14 w-full items-center justify-between border-b border-border px-4 pl-1"
      >
        <Link aria-label="Về trang chủ" className="p-2" to="/">
          <MainLogo className="size-9" />
        </Link>

        <div className="hidden items-center gap-2 md:flex">
          <div className="flex items-center gap-1">
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
          <ThemeToggle />
          {/* <Button
            nativeButton={false}
            render={<Link to="/login" />}
            size="sm"
            variant="outline"
          >
            Đăng nhập
          </Button>
          <Button
            nativeButton={false}
            render={<Link to="/products" />}
            size="sm"
          >
            Khám phá
          </Button> */}
        </div>

        <MobileNav />
      </nav>
    </header>
  )
}
