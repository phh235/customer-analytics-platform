import { BRAND_NAME } from "@/lib/brand"

export const Footer = () => {
  return (
    <footer className="w-full border-y border-border bg-background px-2 md:px-0">
      <div className="mx-auto max-w-5xl border-x p-4">
        <p className="text-center text-sm text-muted-foreground">
          Bản quyền © {new Date().getFullYear()} {BRAND_NAME}.{" "}
          <br className="md:hidden" />
          Mọi quyền được bảo lưu.
        </p>
      </div>
    </footer>
  )
}
