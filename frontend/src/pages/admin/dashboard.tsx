import { useCallback, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { getHello } from "@/api"
import { toastSuccess, toastError } from "@/utils"
import { Badge } from "@/components/ui/badge"

export const Component = () => {
  const [message, setMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleFetchHello = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await getHello()
      setMessage(data.message)
      toastSuccess("Kết nối đến máy chủ thành công!")
    } catch {
      toastError("Không thể kết nối đến máy chủ")
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    let ignore = false
    Promise.resolve().then(() => {
      if (!ignore) {
        handleFetchHello()
      }
    })
    return () => {
      ignore = true
    }
  }, [handleFetchHello])

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div className="flex items-center justify-between rounded-md border border-border bg-card p-5 shadow-xs">
        <div>
          <h1 className="flex items-center gap-2 text-xl font-semibold text-foreground">
            Tổng quan phân tích khách hàng
            {isLoading ? (
              <Badge variant="warning">Đang kết nối</Badge>
            ) : message ? (
              <Badge variant="success" className="gap-1.5 rounded-full">
                Đã kết nối
              </Badge>
            ) : (
              <Badge variant="destructive">Mất kết nối</Badge>
            )}
          </h1>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Trạng thái kết nối máy chủ:{" "}
            <span className="font-medium text-foreground">
              {isLoading ? "Đang tải..." : message || "Mất kết nối"}
            </span>
          </p>
        </div>
        <Button
          variant="outline"
          onClick={handleFetchHello}
          disabled={isLoading}
        >
          Kiểm tra kết nối
        </Button>
      </div>
    </div>
  )
}
