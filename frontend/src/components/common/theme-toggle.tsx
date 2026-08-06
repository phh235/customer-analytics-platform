import { Button } from "@/components/ui/button"
import { useTheme } from "@/components/common/theme-provider"
import { Brightness } from "@/lib/svg"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      aria-label={theme === "dark" ? "Bật giao diện sáng" : "Bật giao diện tối"}
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Brightness />
    </Button>
  )
}
