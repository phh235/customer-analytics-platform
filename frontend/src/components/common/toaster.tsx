import { Toaster as SonnerToaster, type ToasterProps } from "sonner"
import { useTheme } from "@/components/common/theme-provider"

export function Toaster() {
  const { theme } = useTheme()

  return (
    <SonnerToaster
      richColors
      position="top-center"
      theme={theme as ToasterProps["theme"]}
      // expand={true}
    />
  )
}
