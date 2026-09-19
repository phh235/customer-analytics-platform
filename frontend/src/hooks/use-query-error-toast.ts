import { useEffect } from "react"

import { getApiErrorMessage } from "@/api/errors"
import { toastError } from "@/utils/toast"

export function useQueryErrorToast(error: unknown, fallback?: string) {
  useEffect(() => {
    if (error) toastError(getApiErrorMessage(error, fallback))
  }, [error, fallback])
}
