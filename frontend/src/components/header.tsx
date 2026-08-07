import { Link } from "react-router"
import { LogOutIcon } from "lucide-react"

import { ThemeToggle } from "@/components/common/theme-toggle"
import { UserAvatar } from "@/components/common/user-avatar"
import { MobileNav } from "@/components/mobile-nav"
import { buttonVariants } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Spinner } from "@/components/ui/spinner"
import { useLogout } from "@/hooks/use-logout"
import { BRAND_NAME } from "@/lib/brand"
import { MainLogo } from "@/lib/svg"
import { useAuthStore } from "@/stores/use-auth-store"

export const navLinks = [
  { label: "Trang chủ", href: "/" },
  { label: "Sản phẩm", href: "/products" },
]

export function Header() {
  const user = useAuthStore((state) => state.user)
  const authStatus = useAuthStore((state) => state.status)
  const { handleLogout, isLoggingOut } = useLogout()

  return (
    <header className="sticky top-0 z-50 mx-auto w-full border-b border-border bg-background px-2 md:p-0">
      <nav
        aria-label="Điều hướng chính"
        className="mx-auto flex h-14 w-full max-w-5xl items-center justify-between border-x px-4 pl-1"
      >
        <div className="flex items-center gap-6">
          <Link
            aria-label={`Về trang chủ ${BRAND_NAME}`}
            className="flex items-center gap-2 p-2"
            to="/"
          >
            <MainLogo className="size-8" />
            <span className="text-lg font-semibold tracking-tight">
              {BRAND_NAME}
            </span>
          </Link>
          <div className="hidden items-center gap-1 md:flex">
            {navLinks.map((link) => (
              <Link
                className={buttonVariants({ variant: "ghost" })}
                key={link.href}
                to={link.href}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>

        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger>
                <UserAvatar email={user.email} />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-50" sideOffset={8}>
                <DropdownMenuGroup>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col">
                      <span className="truncate text-sm font-medium text-foreground">
                        {user.full_name}
                      </span>
                      <span className="truncate text-xs text-muted-foreground">
                        {user.email}
                      </span>
                    </div>
                  </DropdownMenuLabel>
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                  <DropdownMenuItem
                    disabled={isLoggingOut}
                    onClick={() => void handleLogout()}
                    variant="destructive"
                  >
                    {isLoggingOut ? <Spinner /> : <LogOutIcon />}
                    Đăng xuất
                  </DropdownMenuItem>
                </DropdownMenuGroup>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : authStatus === "unauthenticated" ? (
            <>
              <Link
                className={buttonVariants({ variant: "outline" })}
                to="/login"
              >
                Đăng nhập
              </Link>
              <Link className={buttonVariants()} to="/register">
                Đăng ký
              </Link>
            </>
          ) : null}
          <ThemeToggle />
        </div>

        <MobileNav />
      </nav>
    </header>
  )
}
