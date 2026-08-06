import type { ReactNode } from "react"

interface ClientPageLayoutProps {
  children: ReactNode
}

export const ClientPageLayout = ({ children }: ClientPageLayoutProps) => {
  return (
    <main className="max-w-screen overflow-x-clip px-2 md:px-0">
      <div className="[--separator-height:--spacing(8)]">
        <div className="mx-auto max-w-5xl">{children}</div>
      </div>
    </main>
  )
}
