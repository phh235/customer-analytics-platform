import { createRoot } from "react-dom/client"
import { RouterProvider } from "react-router/dom"

import "./index.css"
import { AppProviders } from "@/app/app-providers"
import { router } from "@/router"

createRoot(document.getElementById("root")!).render(
  <AppProviders>
    <RouterProvider router={router} />
  </AppProviders>
)
