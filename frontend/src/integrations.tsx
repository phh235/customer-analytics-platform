import { Eye, Gem, Layers3, Palette, ScanSearch, Sparkles } from "lucide-react"

export default function Integrations() {
  return (
    <div className="mx-auto flex flex-col gap-6 p-4">
      <div>
        <h2 className="text-xl font-bold">Khám phá theo phong cách</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Tìm cảm hứng từ những phong cách được tuyển chọn cho bạn.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {styleHighlights.map((highlight) => {
          const Icon = highlight.icon

          return (
            <div
              className="relative flex flex-col items-start overflow-hidden border bg-card"
              key={highlight.title}
            >
              <div className="absolute inset-x-0 top-7 h-9.5 border-y border-dashed bg-muted/30" />
              <div className="absolute inset-y-0 left-7 w-9.5 border-x border-dashed bg-muted/30" />

              <div className="relative isolate flex items-start justify-between gap-5 p-6">
                <div className="relative flex size-11 shrink-0 items-center justify-center border bg-background">
                  <Icon aria-hidden="true" className="size-5" />
                </div>
                <div>
                  <h3 className="py-2 text-xl font-medium">
                    {highlight.title}
                  </h3>
                  <p className="mt-4 mb-2 tracking-normal text-pretty text-muted-foreground">
                    {highlight.description}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const styleHighlights = [
  {
    title: "Minimal",
    description:
      "Phom dáng tinh gọn và bảng màu trung tính cho phong cách hiện đại.",
    icon: Palette,
  },
  {
    title: "Streetwear",
    description:
      "Tinh thần tự do với những thiết kế cá tính và giàu năng lượng.",
    icon: Sparkles,
  },
  {
    title: "Techwear",
    description:
      "Chất liệu chức năng và đường nét tương lai cho nhịp sống đô thị.",
    icon: ScanSearch,
  },
  {
    title: "Tailoring",
    description: "Sự cân bằng giữa cấu trúc sắc nét và tinh thần thanh lịch.",
    icon: Layers3,
  },
  {
    title: "Phụ kiện",
    description:
      "Những điểm nhấn hoàn thiện cá tính riêng trong từng lựa chọn.",
    icon: Gem,
  },
  {
    title: "Được quan tâm nhiều",
    description:
      "Những thiết kế đang thu hút nhiều sự chú ý trong cộng đồng 3CS Store.",
    icon: Eye,
  },
]
