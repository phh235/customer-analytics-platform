import { useEffect, useRef, useState } from "react"
import { flushSync } from "react-dom"
import { CheckIcon, MonitorIcon, MoonIcon, SunIcon } from "lucide-react"

import {
  AppDropdown,
  type AppDropdownItem,
} from "@/components/common/app-dropdown"
import { useTheme, type Theme } from "@/components/common/theme-provider"
import { Button } from "@/components/ui/button"

const renderThemeIcon = (currentTheme: Theme) => {
  if (currentTheme === "dark") {
    return <MoonIcon className="size-4" />
  }
  if (currentTheme === "light") {
    return <SunIcon className="size-4" />
  }
  return <MonitorIcon className="size-4" />
}

export const ThemeToggle = () => {
  const { theme, setTheme } = useTheme()
  const [open, setOpen] = useState(false)
  const pendingTheme = useRef<Theme | null>(null)
  const transitionFrame = useRef<number | null>(null)

  useEffect(
    () => () => {
      if (transitionFrame.current !== null) {
        cancelAnimationFrame(transitionFrame.current)
      }
    },
    []
  )

  const applySelectedTheme = (nextTheme: Theme) => {
    if (theme === nextTheme) return

    const resolvedTheme =
      nextTheme === "system"
        ? window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light"
        : nextTheme

    if (
      !document.startViewTransition ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
      document.documentElement.classList.contains(resolvedTheme)
    ) {
      setTheme(nextTheme)
      return
    }

    const transition = document.startViewTransition(() => {
      flushSync(() => setTheme(nextTheme))
    })
    void transition.finished.catch(() => undefined)
  }

  const handleSelectTheme = (nextTheme: Theme) => {
    pendingTheme.current = nextTheme
    setOpen(false)
  }

  const handleOpenChangeComplete = (isOpen: boolean) => {
    if (isOpen || pendingTheme.current === null) return

    const nextTheme = pendingTheme.current
    pendingTheme.current = null
    transitionFrame.current = requestAnimationFrame(() => {
      transitionFrame.current = null
      applySelectedTheme(nextTheme)
    })
  }

  const items: AppDropdownItem[] = [
    {
      key: "light",
      label: "Sáng",
      icon: <SunIcon className="size-4" />,
      endIcon:
        theme === "light" ? (
          <CheckIcon className="size-3.5 text-primary" />
        ) : null,
      onClick: () => handleSelectTheme("light"),
    },
    {
      key: "dark",
      label: "Tối",
      icon: <MoonIcon className="size-4" />,
      endIcon:
        theme === "dark" ? (
          <CheckIcon className="size-3.5 text-primary" />
        ) : null,
      onClick: () => handleSelectTheme("dark"),
    },
    {
      key: "system",
      label: "Hệ thống",
      icon: <MonitorIcon className="size-4" />,
      endIcon:
        theme === "system" ? (
          <CheckIcon className="size-3.5 text-primary" />
        ) : null,
      onClick: () => handleSelectTheme("system"),
    },
  ]

  return (
    <AppDropdown
      items={items}
      open={open}
      onOpenChange={setOpen}
      onOpenChangeComplete={handleOpenChangeComplete}
      align="end"
      aria-label="Chọn giao diện"
      contentClassName="w-fit"
      trigger={
        <Button
          type="button"
          variant="outline"
          size="icon"
          aria-label="Chọn giao diện"
        >
          {renderThemeIcon(theme)}
          <span className="sr-only">Chọn giao diện</span>
        </Button>
      }
    />
  )
}
