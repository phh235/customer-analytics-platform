import { Fragment, useState } from "react"
import { useNavigate } from "react-router"

import { Button } from "@/components/ui/button"
import { navMain } from "@/config/navigation"
import { Kbd } from "@/components/ui/kbd"
import { useEventListener } from "@/hooks/use-event-listener"
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command"
import { SquircleSurface } from "@/components/ui/squircle-card"

export function CommandPalette() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const isMac =
    typeof navigator !== "undefined" &&
    /Mac|iPhone|iPad/.test(navigator.userAgent)

  useEventListener("keydown", (event) => {
    if (event.key.toLowerCase() === "k" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault()
      setOpen((currentOpen) => !currentOpen)
    }
  })

  const handleSelect = (url: string) => {
    setOpen(false)
    navigate(url)
  }

  return (
    <div className="flex flex-col gap-4">
      <Button
        onClick={() => setOpen(true)}
        variant="outline"
        className="w-fit pr-1 text-muted-foreground"
      >
        Tìm kiếm
        <Kbd className="ml-2">{isMac ? "⌘ K" : "Ctrl K"}</Kbd>
      </Button>
      <CommandDialog open={open} onOpenChange={setOpen}>
        <Command className="h-auto! rounded-none! bg-transparent p-0">
          <SquircleSurface className="rounded-[22px] border border-border/80 bg-muted/95 p-1 shadow-xl [--card-clip-radius:12px] dark:bg-[#191919]">
            <CommandInput
              placeholder="Tìm kiếm trang..."
              wrapperClassName="p-1.5"
            />
            <SquircleSurface className="overflow-hidden rounded-[18px] border border-border/60 bg-popover [--card-clip-radius:10px]">
              <CommandList>
                <CommandEmpty className="text-muted-foreground">
                  Không tìm thấy kết quả.
                </CommandEmpty>
                <CommandGroup heading="Điều hướng">
                  {navMain
                    .filter((item) => !item.items)
                    .map((item) => (
                      <CommandItem
                        key={item.url}
                        value={item.title}
                        onSelect={() => handleSelect(item.url)}
                      >
                        {item.icon}
                        <span>{item.title}</span>
                      </CommandItem>
                    ))}
                </CommandGroup>
                {navMain
                  .filter((item) => item.items)
                  .map((item) => (
                    <Fragment key={item.url}>
                      <CommandSeparator />
                      <CommandGroup heading={item.title}>
                        {item.items?.map((subItem) => (
                          <CommandItem
                            key={subItem.url}
                            value={`${item.title} ${subItem.title}`}
                            onSelect={() => handleSelect(subItem.url)}
                          >
                            {item.icon}
                            <span>{subItem.title}</span>
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </Fragment>
                  ))}
              </CommandList>
            </SquircleSurface>
          </SquircleSurface>
        </Command>
      </CommandDialog>
    </div>
  )
}
