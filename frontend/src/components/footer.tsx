export const Footer = () => {
  return (
    <footer className="w-full border-y border-border bg-background">
      <div className="mx-auto max-w-5xl border-x p-4">
        <p className="text-center text-sm text-muted-foreground">
          Bản quyền © {new Date().getFullYear()} Customer Analytics Platform.
          Mọi quyền được bảo lưu.
        </p>
      </div>
    </footer>
  )
}
