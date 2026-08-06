import type { FormEvent } from "react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type {
  Product,
  ProductFormData,
  ProductStatus,
} from "@/lib/admin-management"
import { toastError } from "@/utils/toast"

export function ProductFormDialog({
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
  onSave: (data: ProductFormData) => void
}) {
  const [form, setForm] = useState({
    name: "",
    sku: "",
    category: categories[0] ?? "",
    price: "",
    status: "active" as ProductStatus,
  })

  useEffect(() => {
    if (!open) return

    setForm(
      product
        ? {
            name: product.name,
            sku: product.sku,
            category: product.category,
            price: String(product.price),
            status: product.status,
          }
        : {
            name: "",
            sku: "",
            category: categories[0] ?? "",
            price: "",
            status: "active",
          }
    )
  }, [categories, open, product])

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const price = Number(form.price)

    if (!form.name.trim() || !form.sku.trim() || !form.category || price < 0) {
      toastError("Vui lòng nhập đầy đủ thông tin sản phẩm")
      return
    }

    onSave({
      name: form.name.trim(),
      sku: form.sku.trim(),
      category: form.category,
      price,
      status: form.status,
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <DialogHeader>
            <DialogTitle>
              {product ? "Chỉnh sửa sản phẩm" : "Thêm sản phẩm mới"}
            </DialogTitle>
            <DialogDescription>
              {product
                ? "Cập nhật thông tin sản phẩm và danh mục đang hiển thị."
                : "Nhập thông tin để thêm sản phẩm vào danh sách quản lý."}
            </DialogDescription>
          </DialogHeader>

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
                <Select
                  value={form.category}
                  onValueChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      category: value ?? "",
                    }))
                  }
                >
                  <SelectTrigger id="product-category" className="w-full">
                    <SelectValue>
                      {form.category || "Chọn danh mục"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="product-status">Trạng thái</FieldLabel>
                <Select
                  value={form.status}
                  onValueChange={(value) =>
                    setForm((current) => ({
                      ...current,
                      status: (value ?? "active") as ProductStatus,
                    }))
                  }
                >
                  <SelectTrigger id="product-status" className="w-full">
                    <SelectValue>
                      {form.status === "active" ? "Đang bán" : "Tạm ẩn"}
                    </SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="active">Đang bán</SelectItem>
                      <SelectItem value="inactive">Tạm ẩn</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </Field>
            </FieldGroup>
            <Field>
              <FieldLabel htmlFor="product-price">Giá bán (VNĐ)</FieldLabel>
              <Input
                id="product-price"
                type="number"
                min="0"
                step="1000"
                value={form.price}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    price: event.target.value,
                  }))
                }
                placeholder="0"
                required
              />
            </Field>
          </FieldGroup>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Huỷ
            </Button>
            <Button type="submit">
              {product ? "Lưu thay đổi" : "Thêm sản phẩm"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
