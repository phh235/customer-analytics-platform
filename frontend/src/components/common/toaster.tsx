import { Toaster as SonnerToaster, type ToasterProps } from "sonner"
import { useTheme } from "@/components/common/theme-provider"
import { useIsMobile } from "@/hooks/use-mobile"

export function Toaster() {
  const { theme } = useTheme()
  const isMobile = useIsMobile()

  return (
    <SonnerToaster
      richColors
      position={isMobile ? "top-center" : "bottom-right"}
      theme={theme as ToasterProps["theme"]}
      // expand={true}
    />
  )
}
