import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"

import { ThemeProvider } from "@/components/common/theme-provider"
import { ThemeToggle } from "@/components/common/theme-toggle"

describe("ThemeToggle", () => {
  it("chuyển giữa giao diện sáng và tối", async () => {
    const user = userEvent.setup()

    render(
      <ThemeProvider
        defaultTheme="light"
        storageKey="theme-toggle-test"
        disableTransitionOnChange={false}
      >
        <ThemeToggle />
      </ThemeProvider>
    )

    const toggle = screen.getByRole("button", { name: "Bật giao diện tối" })

    await waitFor(() => expect(document.documentElement).toHaveClass("light"))
    await user.click(toggle)

    expect(
      screen.getByRole("button", { name: "Bật giao diện sáng" })
    ).toBeInTheDocument()
    await waitFor(() => expect(document.documentElement).toHaveClass("dark"))
    expect(localStorage.getItem("theme-toggle-test")).toBe("dark")

    localStorage.removeItem("theme-toggle-test")
    document.documentElement.classList.remove("light", "dark")
  })
})
