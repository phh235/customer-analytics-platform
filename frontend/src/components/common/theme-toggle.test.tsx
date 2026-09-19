import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { ThemeProvider } from "@/components/common/theme-provider"
import { ThemeToggle } from "@/components/common/theme-toggle"

describe("ThemeToggle", () => {
  it("chọn giữa các chế độ sáng, tối và hệ thống qua dropdown", async () => {
    render(
      <ThemeProvider
        defaultTheme="light"
        storageKey="theme-toggle-test"
        disableTransitionOnChange={false}
      >
        <ThemeToggle />
      </ThemeProvider>
    )

    await waitFor(() => expect(document.documentElement).toHaveClass("light"))

    const trigger = screen.getByRole("button", { name: "Chọn giao diện" })
    fireEvent.click(trigger)

    const darkOption = await screen.findByRole("menuitem", { name: /Tối/i })
    expect(screen.getByRole("menuitem", { name: /Sáng/i })).toBeInTheDocument()
    expect(
      screen.getByRole("menuitem", { name: /Hệ thống/i })
    ).toBeInTheDocument()

    fireEvent.click(darkOption)
    await waitFor(() => expect(document.documentElement).toHaveClass("dark"))
    expect(localStorage.getItem("theme-toggle-test")).toBe("dark")

    fireEvent.click(trigger)
    const systemOption = await screen.findByRole("menuitem", {
      name: /Hệ thống/i,
    })
    fireEvent.click(systemOption)
    expect(localStorage.getItem("theme-toggle-test")).toBe("system")

    fireEvent.click(trigger)
    const lightOption = await screen.findByRole("menuitem", { name: /Sáng/i })
    fireEvent.click(lightOption)
    await waitFor(() => expect(document.documentElement).toHaveClass("light"))
    expect(localStorage.getItem("theme-toggle-test")).toBe("light")

    localStorage.removeItem("theme-toggle-test")
    document.documentElement.classList.remove("light", "dark")
  })
})
