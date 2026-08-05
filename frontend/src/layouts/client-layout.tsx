import { Outlet, ScrollRestoration } from "react-router"

import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ScrollToTop } from "@/components/scroll-to-top"

export const ClientLayout = () => {
  return (
    <div className="relative isolate mx-auto min-h-screen">
      <Header />
      <Outlet />
      <Footer />
      <ScrollRestoration />
      <ScrollToTop />
    </div>
  )
}

export default ClientLayout
