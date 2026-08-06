import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router/dom"
import { Analytics } from "@vercel/analytics/react"
import { NuqsAdapter } from "nuqs/adapters/react-router/v8"

import "./index.css"
import { router } from "@/router"
import { ThemeProvider } from "@/components/common/theme-provider"
import { Toaster } from "@/components/common/toaster"

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <NuqsAdapter>
      <RouterProvider router={router} />
    </NuqsAdapter>
    <Toaster />
    <Analytics />
  </ThemeProvider>
)
