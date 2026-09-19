import { describe, expect, it } from "vitest"

import {
  canRoleAccessPath,
  getHomePathForRole,
  getPostLoginPath,
} from "@/lib/auth-routing"
import type { UserRole } from "@/types/user"

describe("auth routing", () => {
  it.each([
    ["ADMIN", "/dashboard"],
    ["ANALYST", "/dashboard"],
    ["MANAGER", "/dashboard"],
    ["SALES", "/dashboard"],
    ["CSKH", "/dashboard"],
    ["USER", "/"],
    ["CLIENT", "/"],
  ])("đưa %s vào đúng khu vực sau đăng nhập", (role, path) => {
    expect(getHomePathForRole(role as UserRole)).toBe(path)
    expect(canRoleAccessPath(role as UserRole, path)).toBe(true)
  })

  it("không đưa người dùng khách hàng vào dashboard qua đường dẫn đã lưu", () => {
    expect(
      getPostLoginPath("USER" as UserRole, { from: { pathname: "/dashboard" } })
    ).toBe("/")
  })

  it("khôi phục trang được phép cùng bộ lọc", () => {
    expect(
      getPostLoginPath("MANAGER" as UserRole, {
        from: {
          pathname: "/dashboard/customers",
          search: "?q=An",
          hash: "#results",
        },
      })
    ).toBe("/dashboard/customers?q=An#results")
    expect(canRoleAccessPath("SALES" as UserRole, "/dashboard/users")).toBe(
      false
    )
  })
})
