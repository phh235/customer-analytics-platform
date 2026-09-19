import type { FormEvent } from "react"
import { useState } from "react"

import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import type {
  Product,
  ProductFormData,
  ProductStatus,
} from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

const NON_DIGIT_PATTERN = /\D/g
const DIGIT_GROUP_PATTERN = /\B(?=(\d{3})+(?!\d))/g

const formatPriceInput = (value: string | number) => {
  const digits = String(value).replace(NON_DIGIT_PATTERN, "")

  return digits ? digits.replace(DIGIT_GROUP_PATTERN, ",") : ""
}

export function ProductFormSheet({
  open,
  onOpenChange,
  product,
  categories,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  product: Product | null
  categories: string[]
  onSave: (data: ProductFormData) => void | Promise<void>
}) {
  const [form, setForm] = useState(() =>
    product
      ? {
          name: product.name,
          sku: product.sku,
          category: product.category,
          price: formatPriceInput(product.price),
          status: product.status,
          image: null as File | null,
        }
      : {
          name: "",
          sku: "",
          category: categories[0] ?? "",
          price: "",
          status: "active" as ProductStatus,
          image: null as File | null,
        }
  )
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const rawPrice = form.price.replace(/,/g, "")
    const price = Number(rawPrice)

    if (
      !form.name.trim() ||
      !form.sku.trim() ||
      !form.category ||
      !rawPrice ||
      !Number.isFinite(price) ||
      price < 0
    ) {
      toastError("Vui lòng nhập đầy đủ thông tin sản phẩm")
      return
    }

    setSaving(true)
    try {
      await onSave({
        name: form.name.trim(),
        sku: form.sku.trim(),
        category: form.category,
        price,
        status: form.status,
        image: form.image,
      })
      onOpenChange(false)
    } catch {
      // The parent displays the API error; keep the sheet open for correction.
    } finally {
      setSaving(false)
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="gap-0 sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>
            {product ? "Chỉnh sửa sản phẩm" : "Thêm sản phẩm mới"}
          </SheetTitle>
          <SheetDescription>
            {product
              ? "Cập nhật thông tin sản phẩm và danh mục đang hiển thị."
              : "Nhập thông tin để thêm sản phẩm vào danh sách quản lý."}
          </SheetDescription>
        </SheetHeader>
        <form
          id="product-form-sheet"
          onSubmit={handleSubmit}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="product-name">Tên sản phẩm</FieldLabel>
              <Input
                id="product-name"
                value={form.name}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    name: event.target.value,
                  }))
                }
                placeholder="Ví dụ: Tai nghe chống ồn AirFlow"
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="product-sku">Mã SKU</FieldLabel>
              <Input
                id="product-sku"
                value={form.sku}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    sku: event.target.value,
                  }))
                }
                placeholder="Ví dụ: AF-1001"
                required
              />
            </Field>
            <FieldGroup className="grid gap-4 sm:grid-cols-2">
              <Field>
                <FieldLabel htmlFor="product-category">Danh mục</FieldLabel>
                <AppSelect
                  options={categories.map((category) => ({
                    value: category,
                    label: category,
                  }))}
                  value={form.category}
                  onChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      category: value,
                    }))
                  }
                  id="product-category"
                  className="w-full"
                  aria-label="Chọn danh mục sản phẩm"
                  placeholder="Chọn danh mục"
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="product-status">Trạng thái</FieldLabel>
                <AppSelect
                  options={[
                    { value: "active", label: "Đang bán" },
                    { value: "inactive", label: "Tạm ẩn" },
                  ]}
                  value={form.status}
                  onChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      status: value as ProductStatus,
                    }))
                  }
                  id="product-status"
                  className="w-full"
                  aria-label="Chọn trạng thái sản phẩm"
                />
              </Field>
            </FieldGroup>
            <Field>
              <FieldLabel htmlFor="product-image">Ảnh sản phẩm</FieldLabel>
              {product?.imageUrl ? (
                <img
                  src={product.imageUrl}
                  alt={product.name}
                  className="h-32 w-full rounded-lg border object-cover"
                />
              ) : null}
              <Input
                id="product-image"
                type="file"
                accept="image/*"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null
                  if (file && !file.type.startsWith("image/")) {
                    toastError("Vui lòng chọn một tệp ảnh")
                    event.currentTarget.value = ""
                    return
                  }
                  if (file && file.size > 10 * 1024 * 1024) {
                    toastError("Ảnh không được vượt quá 10 MB")
                    event.currentTarget.value = ""
                    return
                  }
                  setForm((current) => ({ ...current, image: file }))
                }}
              />
              <p className="text-xs text-muted-foreground">
                JPG, PNG, WEBP; tối đa 10 MB.
                {form.image ? ` Đã chọn: ${form.image.name}` : ""}
              </p>
            </Field>
            <Field>
              <FieldLabel htmlFor="product-price">Giá bán (VNĐ)</FieldLabel>
              <Input
                id="product-price"
                type="text"
                inputMode="numeric"
                pattern="[0-9,]*"
                value={form.price}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    price: formatPriceInput(event.target.value),
                  }))
                }
                placeholder="0"
                required
              />
            </Field>
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={saving}
          >
            Huỷ
          </Button>
          <Button type="submit" form="product-form-sheet" disabled={saving}>
            {saving
              ? "Đang lưu..."
              : product
                ? "Lưu thay đổi"
                : "Thêm sản phẩm"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
