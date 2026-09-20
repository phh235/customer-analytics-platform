import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { ThemeProvider } from "@/components/common/theme-provider"
import { ThemeToggle } from "@/components/common/theme-toggle"

describe("ThemeToggle", () => {
  afterEach(() => {
    Object.defineProperty(document, "startViewTransition", {
      configurable: true,
      value: undefined,
    })
  })

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
    await waitFor(() =>
      expect(localStorage.getItem("theme-toggle-test")).toBe("system")
    )

    fireEvent.click(trigger)
    const lightOption = await screen.findByRole("menuitem", { name: /Sáng/i })
    fireEvent.click(lightOption)
    await waitFor(() => {
      expect(document.documentElement).toHaveClass("light")
      expect(localStorage.getItem("theme-toggle-test")).toBe("light")
    })

    localStorage.removeItem("theme-toggle-test")
    document.documentElement.classList.remove("light", "dark")
  })

  it("đổi theme trong view transition sau khi dropdown đã đóng", async () => {
    const snapshots: string[] = []
    const startViewTransition = vi.fn((update: () => void) => {
      expect(document.querySelector('[role="menu"]')).toBeNull()
      snapshots.push(document.documentElement.className)
      update()
      snapshots.push(document.documentElement.className)
      return { finished: Promise.resolve() }
    })
    Object.defineProperty(document, "startViewTransition", {
      configurable: true,
      value: startViewTransition,
    })

    render(
      <ThemeProvider
        defaultTheme="light"
        storageKey="theme-transition-test"
        disableTransitionOnChange={false}
      >
        <ThemeToggle />
      </ThemeProvider>
    )
    await waitFor(() => expect(document.documentElement).toHaveClass("light"))

    fireEvent.click(screen.getByRole("button", { name: "Chọn giao diện" }))
    fireEvent.click(await screen.findByRole("menuitem", { name: /Tối/i }))

    await waitFor(() => expect(startViewTransition).toHaveBeenCalledOnce())
    expect(snapshots).toEqual(["light", "dark"])
    expect(localStorage.getItem("theme-transition-test")).toBe("dark")

    localStorage.removeItem("theme-transition-test")
    document.documentElement.classList.remove("light", "dark")
  })
})
