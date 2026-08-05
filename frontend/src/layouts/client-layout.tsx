import { Outlet } from "react-router"

import { Header } from "@/components/header"

export const ClientLayout = () => {
  return (
    <div className="mx-auto min-h-screen max-w-4xl bg-background">
      <Header />
      <Outlet />
    </div>
  )
}

export default ClientLayout
