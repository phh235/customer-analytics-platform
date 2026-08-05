import * as React from "react"
import { MenuIcon, XIcon } from "lucide-react"
import { Link } from "react-router"

import { ThemeToggle } from "@/components/common/theme-toggle"
import { Button } from "@/components/ui/button"
import { Portal, PortalBackdrop } from "@/components/portal"
import { cn } from "@/lib/utils"
import { navLinks } from "@/components/header"

export function MobileNav() {
  const [open, setOpen] = React.useState(false)

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

      {open && (
        <Portal className="top-16" id="mobile-menu">
          <PortalBackdrop />
          <div
            className={cn("size-full p-4", "data-[slot=open]:animate-in")}
            data-slot="open"
          >
            <div className="grid gap-2">
              {navLinks.map((link) => (
                <Button
                  className="justify-start"
                  key={link.href}
                  nativeButton={false}
                  onClick={closeMenu}
                  render={<Link to={link.href} />}
                  variant="ghost"
                >
                  {link.label}
                </Button>
              ))}
            </div>
            <div className="mt-12 flex flex-col gap-2">
              <Button
                className="w-full"
                nativeButton={false}
                onClick={closeMenu}
                render={<Link to="/login" />}
                variant="outline"
              >
                Đăng nhập
              </Button>
              <Button
                className="w-full"
                nativeButton={false}
                onClick={closeMenu}
                render={<Link to="/products" />}
              >
                Khám phá sản phẩm
              </Button>
            </div>
          </div>
        </Portal>
      )}
    </div>
  )
}
