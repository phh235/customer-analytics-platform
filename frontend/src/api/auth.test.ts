import { describe, expect, it, vi } from "vitest"
import apiClient from "@/api/client"
import { getCurrentUser } from "@/api/auth"

vi.mock("@/api/client", () => ({ default: { get: vi.fn() } }))

describe("current user response", () => {
  it.each(["ADMIN", "MANAGER", "ANALYST", "SALES", "CSKH", "USER", "CLIENT"])(
    "chấp nhận vai trò %s",
    async (role_code) => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: { role_code } })
      expect((await getCurrentUser()).role_code).toBe(role_code)
    }
  )

  it.each([{ role_code: "UNKNOWN" }, {}, null])(
    "từ chối phản hồi không có vai trò được hỗ trợ",
    async (data) => {
      vi.mocked(apiClient.get).mockResolvedValue({ data })
      await expect(getCurrentUser()).rejects.toThrow(
        "Vai trò của tài khoản chưa được hỗ trợ"
      )
    }
  )
})
