import { useMemo } from "react"
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

  const items: AppDropdownItem[] = useMemo(
    () => [
      {
        key: "light",
        label: "Sáng",
        icon: <SunIcon className="size-4" />,
        endIcon:
          theme === "light" ? (
            <CheckIcon className="size-3.5 text-primary" />
          ) : null,
        onClick: () => setTheme("light"),
      },
      {
        key: "dark",
        label: "Tối",
        icon: <MoonIcon className="size-4" />,
        endIcon:
          theme === "dark" ? (
            <CheckIcon className="size-3.5 text-primary" />
          ) : null,
        onClick: () => setTheme("dark"),
      },
      {
        key: "system",
        label: "Hệ thống",
        icon: <MonitorIcon className="size-4" />,
        endIcon:
          theme === "system" ? (
            <CheckIcon className="size-3.5 text-primary" />
          ) : null,
        onClick: () => setTheme("system"),
      },
    ],
    [setTheme, theme]
  )

  return (
    <AppDropdown
      items={items}
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
