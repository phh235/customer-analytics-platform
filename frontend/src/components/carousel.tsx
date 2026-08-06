import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel"
import type { CarouselApi } from "@/components/ui/carousel"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

const AUTOPLAY_INTERVAL = 4000

const images = [
  "https://www.fffuel.co/images/dddepth-preview/dddepth-248.jpg",
  "https://www.fffuel.co/images/dddepth-preview/dddepth-051.jpg",
  "https://www.fffuel.co/images/dddepth-preview/dddepth-029.jpg",
  "https://www.fffuel.co/images/dddepth-preview/dddepth-038.jpg",
  "https://www.fffuel.co/images/dddepth-preview/dddepth-012.jpg",
]

const CarouselClient = () => {
  const [api, setApi] = useState<CarouselApi>()
  const [current, setCurrent] = useState(0)
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!api) {
      return
    }

    setCount(api.scrollSnapList().length)
    setCurrent(api.selectedScrollSnap())

    const handleSelect = () => {
      setCurrent(api.selectedScrollSnap())
    }

    api.on("select", handleSelect)

    return () => {
      api.off("select", handleSelect)
    }
  }, [api])

  useEffect(() => {
    if (!api) {
      return
    }

    const intervalId = window.setInterval(() => {
      api.scrollNext()
    }, AUTOPLAY_INTERVAL)

    return () => {
      window.clearInterval(intervalId)
    }
  }, [api, current])

  return (
    <Carousel className="relative w-full" setApi={setApi} opts={{ loop: true }}>
      <CarouselContent className="ml-0">
        {images.map((image) => (
          <CarouselItem key={image}>
            <div className="h-58 w-full md:h-75">
              <img
                alt="dddepth"
                className="block h-full w-full object-cover"
                draggable={false}
                src={image}
              />
            </div>
          </CarouselItem>
        ))}
      </CarouselContent>
      <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 gap-2">
        {Array.from({ length: count }).map((_, index) => (
          <button
            key={index}
            onClick={() => api?.scrollTo(index)}
            className={cn(
              "h-2 w-2 cursor-pointer rounded-full transition-all",
              current === index ? "bg-white" : "bg-white/50 hover:bg-white/85"
            )}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </Carousel>
  )
}

export default CarouselClient
