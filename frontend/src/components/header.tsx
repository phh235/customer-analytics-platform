import { Link } from "react-router"

import { ThemeToggle } from "@/components/common/theme-toggle"
import { MobileNav } from "@/components/mobile-nav"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useScroll } from "@/hooks/use-scroll"
import { MainLogo } from "@/lib/svg"

export const navLinks = [
  { label: "Trang chủ", href: "/" },
  { label: "Sản phẩm", href: "/products" },
]

export function Header() {
  const scrolled = useScroll(10)

  return (
    <header
      className={cn(
        "sticky top-0 z-50 mx-auto w-full max-w-6xl border-b border-transparent md:rounded-md md:border md:transition-all md:ease-out",
        scrolled &&
          "border-border bg-background/95 backdrop-blur-sm supports-backdrop-filter:bg-background/50 md:top-2 md:max-w-5xl md:shadow"
      )}
    >
      <nav
        aria-label="Điều hướng chính"
        className={cn(
          "flex h-16 w-full items-center justify-between px-4 md:h-14 md:px-6 md:transition-all md:ease-out",
          scrolled && "md:px-3"
        )}
      >
        <Link aria-label="Về trang chủ" className="rounded-md p-2" to="/">
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
