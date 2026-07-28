import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router/dom"

import "./index.css"
import { router } from "@/router"
import { ThemeProvider } from "@/components/common/theme-provider"
import { Toaster } from "@/components/common/toaster"

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <RouterProvider router={router} />
    <Toaster />
  </ThemeProvider>
)
