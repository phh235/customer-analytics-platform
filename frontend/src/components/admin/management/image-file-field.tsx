import { Field, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { toastError } from "@/utils/toast"

const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

export function ImageFileField({
  id,
  label,
  previewUrl,
  previewAlt,
  previewClassName,
  selectedFile,
  onFileChange,
}: {
  id: string
  label: string
  previewUrl?: string
  previewAlt: string
  previewClassName?: string
  selectedFile: File | null
  onFileChange: (file: File | null) => void
}) {
  return (
    <Field>
      <FieldLabel htmlFor={id}>{label}</FieldLabel>
      {previewUrl ? (
        <img
          src={previewUrl}
          alt={previewAlt}
          className={cn("h-32 border object-cover", previewClassName)}
        />
      ) : null}
      <Input
        id={id}
        type="file"
        accept="image/*"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null

          if (file && !file.type.startsWith("image/")) {
            toastError("Vui lòng chọn một tệp ảnh")
            event.currentTarget.value = ""
            return
          }

          if (file && file.size > MAX_IMAGE_SIZE_BYTES) {
            toastError("Ảnh không được vượt quá 10 MB")
            event.currentTarget.value = ""
            return
          }

          onFileChange(file)
        }}
      />
      <p className="text-xs text-muted-foreground">
        JPG, PNG, WEBP; tối đa 10 MB.
        {selectedFile ? ` Đã chọn: ${selectedFile.name}` : ""}
      </p>
    </Field>
  )
}
