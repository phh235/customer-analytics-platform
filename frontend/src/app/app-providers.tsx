import type { PropsWithChildren } from "react"
import { QueryClientProvider } from "@tanstack/react-query"
import { Analytics } from "@vercel/analytics/react"
import { NuqsAdapter } from "nuqs/adapters/react-router/v8"

import { ThemeProvider } from "@/components/common/theme-provider"
import { Toaster } from "@/components/common/toaster"
import { queryClient } from "@/app/query-client"

export function AppProviders({ children }: PropsWithChildren) {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <NuqsAdapter>{children}</NuqsAdapter>
        <Toaster />
        <Analytics />
      </QueryClientProvider>
    </ThemeProvider>
  )
}
