const currencyFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
})

const numberFormatter = new Intl.NumberFormat("vi-VN")

export function formatCurrency(value: number) {
  return currencyFormatter.format(value)
}

export function formatNumber(value: number) {
  return numberFormatter.format(value)
}

export function normalizeText(value: string) {
  return value.toLocaleLowerCase("vi-VN")
}

export function formatEnumLabel(
  value: string | null | undefined,
  labels: Record<string, string>
) {
  if (!value) return "—"
  const normalized = value.trim().toUpperCase()
  return (
    labels[normalized] ??
    value.trim().replaceAll("_", " ").toLocaleLowerCase("vi-VN")
  )
}
