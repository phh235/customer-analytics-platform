import { ImageIcon, UploadCloudIcon, XIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Field, FieldLabel } from "@/components/ui/field"
import {
  FileUpload,
  FileUploadDropzone,
  FileUploadItem,
  FileUploadItemDelete,
  FileUploadItemMetadata,
  FileUploadItemPreview,
  FileUploadList,
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
  disabled = false,
}: {
  id: string
  label: string
  previewUrl?: string
  previewAlt: string
  previewClassName?: string
  selectedFile: File | null
  onFileChange: (file: File | null) => void
  disabled?: boolean
}) {
  return (
    <Field>
      <FieldLabel>{label}</FieldLabel>
      {previewUrl && !selectedFile ? (
        <img
          src={previewUrl}
          alt={previewAlt}
          className={cn("h-32 border object-cover", previewClassName)}
        />
      ) : null}

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
        <FileUploadDropzone className="min-h-28 gap-1.5 p-3 text-center">
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

        <FileUploadList>
          {selectedFile ? (
            <FileUploadItem value={selectedFile}>
              <FileUploadItemPreview className="size-16 rounded-lg [&>img]:object-cover [&>svg]:size-6" />
              <FileUploadItemMetadata />
              <FileUploadItemDelete
                render={
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon-sm"
                    aria-label="Xóa ảnh đã chọn"
                  />
                }
              >
                <XIcon />
              </FileUploadItemDelete>
            </FileUploadItem>
          ) : null}
        </FileUploadList>
      </FileUpload>
    </Field>
  )
}
