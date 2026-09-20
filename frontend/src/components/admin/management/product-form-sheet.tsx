import { useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm, useWatch } from "react-hook-form"
import { z } from "zod"

import { ImageFileField } from "@/components/admin/management/image-file-field"
import { AppSelect } from "@/components/common/app-select"
import { Button } from "@/components/ui/button"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Spinner } from "@/components/ui/spinner"
import type { Product, ProductFormData } from "@/lib/admin-management"

const NON_DIGIT_PATTERN = /\D/g
const DIGIT_GROUP_PATTERN = /\B(?=(\d{3})+(?!\d))/g

const formatPriceInput = (value: string | number) => {
  const digits = String(value).replace(NON_DIGIT_PATTERN, "")
  return digits ? digits.replace(DIGIT_GROUP_PATTERN, ",") : ""
}

const productFormSchema = z.object({
  name: z.string().trim().min(1, "Vui lòng nhập tên sản phẩm"),
  sku: z.string().trim().min(1, "Vui lòng nhập mã SKU"),
  category: z.string().min(1, "Vui lòng chọn danh mục"),
  price: z
    .string()
    .min(1, "Vui lòng nhập giá bán")
    .refine(
      (value) => Number.isFinite(Number(value.replace(/,/g, ""))),
      "Giá bán không hợp lệ"
    ),
  status: z.enum(["active", "inactive"]),
  image: z.instanceof(File).nullable(),
  remove_image: z.boolean(),
})

type ProductFormValues = z.infer<typeof productFormSchema>

const getDefaultValues = (
  product: Product | null,
  categories: string[]
): ProductFormValues => ({
  name: product?.name ?? "",
  sku: product?.sku ?? "",
  category: product?.category ?? categories[0] ?? "",
  price: product ? formatPriceInput(product.price) : "",
  status: product?.status ?? "active",
  image: null,
  remove_image: false,
})

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
  onSave: (data: ProductFormData) => void | Promise<unknown>
}) {
  const form = useForm<ProductFormValues>({
    defaultValues: getDefaultValues(product, categories),
    resolver: zodResolver(productFormSchema),
  })
  const removeImage = useWatch({
    control: form.control,
    name: "remove_image",
  })

  useEffect(() => {
    if (open) form.reset(getDefaultValues(product, categories))
  }, [categories, form, open, product])

  const handleSubmit = async (values: ProductFormValues) => {
    await onSave({
      name: values.name.trim(),
      sku: values.sku.trim(),
      category: values.category,
      price: Number(values.price.replace(/,/g, "")),
      status: values.status,
      image: values.image,
      removeImage: values.remove_image,
    })
    onOpenChange(false)
  }

  const isSubmitting = form.formState.isSubmitting

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
          onSubmit={form.handleSubmit(handleSubmit)}
          className="flex min-h-0 flex-1 flex-col gap-5 overflow-y-auto px-4 py-4"
        >
          <FieldGroup>
            <Controller
              control={form.control}
              name="name"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="product-name">Tên sản phẩm</FieldLabel>
                  <Input
                    id="product-name"
                    placeholder="Ví dụ: Tai nghe chống ồn AirFlow"
                    aria-invalid={fieldState.invalid}
                    disabled={isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <Controller
              control={form.control}
              name="sku"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="product-sku">Mã SKU</FieldLabel>
                  <Input
                    id="product-sku"
                    placeholder="Ví dụ: AF-1001"
                    aria-invalid={fieldState.invalid}
                    disabled={isSubmitting}
                    {...field}
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
            <FieldGroup className="grid gap-4 sm:grid-cols-2">
              <Controller
                control={form.control}
                name="category"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="product-category">Danh mục</FieldLabel>
                    <AppSelect
                      id="product-category"
                      value={field.value}
                      onChange={field.onChange}
                      disabled={isSubmitting}
                      className="w-full"
                      aria-label="Chọn danh mục sản phẩm"
                      placeholder="Chọn danh mục"
                      options={categories.map((category) => ({
                        value: category,
                        label: category,
                      }))}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
              <Controller
                control={form.control}
                name="status"
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="product-status">Trạng thái</FieldLabel>
                    <AppSelect
                      id="product-status"
                      value={field.value}
                      onChange={field.onChange}
                      disabled={isSubmitting}
                      className="w-full"
                      aria-label="Chọn trạng thái sản phẩm"
                      options={[
                        { value: "active", label: "Đang bán" },
                        { value: "inactive", label: "Tạm ẩn" },
                      ]}
                    />
                    <FieldError errors={[fieldState.error]} />
                  </Field>
                )}
              />
            </FieldGroup>
            <Controller
              control={form.control}
              name="image"
              render={({ field }) => (
                <ImageFileField
                  id="product-image"
                  label="Ảnh sản phẩm"
                  previewUrl={product?.imageUrl ?? undefined}
                  previewAlt={product?.name ?? "Sản phẩm"}
                  previewClassName="w-full rounded-lg"
                  selectedFile={field.value}
                  onFileChange={(file) => {
                    field.onChange(file)
                    if (file) form.setValue("remove_image", false)
                  }}
                  onRemoveExisting={() => {
                    field.onChange(null)
                    form.setValue("remove_image", true)
                  }}
                  hideExistingPreview={removeImage}
                  disabled={isSubmitting}
                />
              )}
            />
            <Controller
              control={form.control}
              name="price"
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="product-price">Giá bán (VNĐ)</FieldLabel>
                  <Input
                    id="product-price"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9,]*"
                    placeholder="0"
                    aria-invalid={fieldState.invalid}
                    disabled={isSubmitting}
                    {...field}
                    onChange={(event) =>
                      field.onChange(formatPriceInput(event.target.value))
                    }
                  />
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />
          </FieldGroup>
        </form>
        <SheetFooter className="border-t bg-muted/50 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            Huỷ
          </Button>
          <Button
            type="submit"
            form="product-form-sheet"
            disabled={isSubmitting}
          >
            {isSubmitting && <Spinner data-icon="inline-start" />}
            {product ? "Lưu thay đổi" : "Thêm sản phẩm"}
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
