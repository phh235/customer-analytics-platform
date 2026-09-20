import { useEffect, useMemo } from "react"
import { ImageIcon, Trash2Icon, UploadCloudIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Field, FieldLabel } from "@/components/ui/field"
import {
  FileUpload,
  FileUploadDropzone,
  FileUploadTrigger,
} from "@/components/ui/file-upload"
import { cn } from "@/lib/utils"
import { toastError } from "@/utils/toast"

const MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
const ACCEPTED_IMAGE_TYPES = "image/jpeg,image/png,image/webp"

export function ImageFileField({
  id,
  label,
  previewUrl,
  previewAlt,
  previewClassName,
  selectedFile,
  onFileChange,
  onRemoveExisting,
  hideExistingPreview = false,
  disabled = false,
}: {
  id: string
  label: string
  previewUrl?: string
  previewAlt: string
  previewClassName?: string
  selectedFile: File | null
  onFileChange: (file: File | null) => void
  onRemoveExisting?: () => void
  hideExistingPreview?: boolean
  disabled?: boolean
}) {
  const selectedPreviewUrl = useMemo(
    () => (selectedFile ? URL.createObjectURL(selectedFile) : null),
    [selectedFile]
  )

  useEffect(() => {
    return () => {
      if (selectedPreviewUrl) URL.revokeObjectURL(selectedPreviewUrl)
    }
  }, [selectedPreviewUrl])

  const displayedImage =
    selectedPreviewUrl ?? (!hideExistingPreview ? previewUrl : undefined)

  const removeImage = () => {
    if (selectedFile) {
      onFileChange(null)
      return
    }
    onRemoveExisting?.()
  }

  return (
    <Field>
      <FieldLabel>{label}</FieldLabel>
      <FileUpload
        value={selectedFile ? [selectedFile] : []}
        onValueChange={(files) => onFileChange(files[0] ?? null)}
        onFileReject={(file) =>
          toastError(
            file.size > MAX_IMAGE_SIZE_BYTES
              ? "Ảnh không được vượt quá 10 MB"
              : "Chỉ chấp nhận ảnh JPG, PNG hoặc WEBP"
          )
        }
        accept={ACCEPTED_IMAGE_TYPES}
        maxFiles={1}
        maxSize={MAX_IMAGE_SIZE_BYTES}
        label={label}
        name={id}
        disabled={disabled}
      >
        {displayedImage ? (
          <div
            className={cn(
              "relative aspect-square w-full overflow-hidden rounded-xl border bg-muted",
              previewClassName
            )}
          >
            <img
              src={displayedImage}
              alt={previewAlt}
              className="size-full object-cover"
            />
            <div className="absolute right-2 bottom-2 flex items-center gap-1 rounded-lg bg-background/90 p-1 shadow-sm backdrop-blur-sm">
              <FileUploadTrigger
                render={
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Upload lại ảnh"
                    title="Upload lại ảnh"
                  />
                }
              >
                <UploadCloudIcon />
              </FileUploadTrigger>
              {(selectedFile || onRemoveExisting) && (
                <Button
                  type="button"
                  variant="destructive"
                  size="icon-sm"
                  aria-label="Xóa ảnh"
                  title="Xóa ảnh"
                  onClick={removeImage}
                >
                  <Trash2Icon />
                </Button>
              )}
            </div>
          </div>
        ) : (
          <FileUploadDropzone className="aspect-square min-h-0 gap-1.5 p-3 text-center">
            <ImageIcon className="size-6 text-muted-foreground" />
            <p className="text-xs text-muted-foreground">
              JPG, PNG, WEBP · tối đa 10 MB
            </p>
            <FileUploadTrigger
              render={<Button type="button" variant="outline" size="sm" />}
            >
              <UploadCloudIcon data-icon="inline-start" />
              Chọn ảnh
            </FileUploadTrigger>
          </FileUploadDropzone>
        )}
      </FileUpload>
    </Field>
  )
}
