import * as React from "react"
import { MenuIcon, XIcon } from "lucide-react"
import { Link } from "react-router"

import { ThemeToggle } from "@/components/common/theme-toggle"
import { UserAvatar } from "@/components/common/user-avatar"
import { Button, buttonVariants } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import { useLogout } from "@/hooks/use-logout"
import { Portal, PortalBackdrop } from "@/components/portal"
import { cn } from "@/lib/utils"
import { navLinks } from "@/components/header"
import { useAuthStore } from "@/stores/use-auth-store"

export function MobileNav() {
  const [open, setOpen] = React.useState(false)
  const user = useAuthStore((state) => state.user)
  const authStatus = useAuthStore((state) => state.status)
  const { handleLogout, isLoggingOut } = useLogout()

  const closeMenu = () => setOpen(false)

  return (
    <div className="flex items-center gap-2 md:hidden">
      <ThemeToggle />
      <Button
        aria-controls="mobile-menu"
        aria-expanded={open}
        aria-label={open ? "Đóng menu" : "Mở menu"}
        onClick={() => setOpen((isOpen) => !isOpen)}
        size="icon"
        variant="outline"
      >
        {open ? <XIcon aria-hidden="true" /> : <MenuIcon aria-hidden="true" />}
      </Button>

      {open ? (
        <Portal className="top-16" id="mobile-menu">
          <PortalBackdrop />
          <div
            className={cn("size-full p-4", "data-[slot=open]:animate-in")}
            data-slot="open"
          >
            <div className="grid gap-2">
              {navLinks.map((link) => (
                <Link
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "justify-start"
                  )}
                  key={link.href}
                  onClick={closeMenu}
                  to={link.href}
                >
                  {link.label}
                </Link>
              ))}
            </div>
            <div className="mt-12 flex flex-col gap-2">
              {user ? (
                <>
                  <div className="flex min-w-0 items-center gap-3 px-3 py-2">
                    <UserAvatar email={user.email} />
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {user.full_name}
                      </p>
                      <p className="truncate text-xs text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  </div>
                  <Button
                    className="w-full"
                    disabled={isLoggingOut}
                    onClick={() => {
                      closeMenu()
                      void handleLogout()
                    }}
                    variant="outline"
                  >
                    {isLoggingOut ? <Spinner data-icon="inline-start" /> : null}
                    Đăng xuất
                  </Button>
                </>
              ) : authStatus === "unauthenticated" ? (
                <Link
                  className={cn(
                    buttonVariants({ variant: "outline" }),
                    "w-full"
                  )}
                  onClick={closeMenu}
                  to="/login"
                >
                  Đăng nhập
                </Link>
              ) : null}
            </div>
          </div>
        </Portal>
      ) : null}
    </div>
  )
}
