const slides = [...document.querySelectorAll(".slide-shell")]
const deck = document.querySelector(".deck")
const currentLabel = document.querySelector("[data-current-slide]")
const videoDialog = document.querySelector("[data-video-dialog]")
const demoVideo = document.querySelector("[data-demo-video]")
const requestedSlide = Number.parseInt(
  new URLSearchParams(window.location.search).get("slide") ?? "1",
  10
)
let activeIndex = Number.isFinite(requestedSlide)
  ? Math.max(0, Math.min(requestedSlide - 1, slides.length - 1))
  : 0
let scrollFrame = null

function updateCounter() {
  if (currentLabel) currentLabel.textContent = `${activeIndex + 1} / ${slides.length}`
}

function updateSlideParam() {
  const url = new URL(window.location.href)
  url.searchParams.set("slide", String(activeIndex + 1))
  window.history.replaceState({}, "", url)
}

function goTo(index) {
  activeIndex = Math.max(0, Math.min(index, slides.length - 1))
  const target = slides[activeIndex]
  deck?.scrollTo({ left: target.offsetLeft, top: 0, behavior: "auto" })
  updateCounter()
  updateSlideParam()
}

document.querySelector("[data-prev]")?.addEventListener("click", () => {
  goTo(activeIndex - 1)
})

document.querySelector("[data-next]")?.addEventListener("click", () => {
  goTo(activeIndex + 1)
})

document.querySelector("[data-fullscreen]")?.addEventListener("click", async () => {
  if (document.fullscreenElement) await document.exitFullscreen()
  else await document.documentElement.requestFullscreen()
})

document.querySelector("[data-print]")?.addEventListener("click", () => window.print())

document.querySelector("[data-video-open]")?.addEventListener("click", async () => {
  if (!(videoDialog instanceof HTMLDialogElement)) return

  videoDialog.showModal()
  if (demoVideo instanceof HTMLVideoElement) {
    demoVideo.currentTime = 0
    await demoVideo.play().catch(() => undefined)
  }
})

document.querySelector("[data-video-close]")?.addEventListener("click", () => {
  if (videoDialog instanceof HTMLDialogElement) videoDialog.close()
})

videoDialog?.addEventListener("close", () => {
  if (demoVideo instanceof HTMLVideoElement) demoVideo.pause()
})

document.addEventListener("keydown", (event) => {
  if (videoDialog instanceof HTMLDialogElement && videoDialog.open) return

  if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {
    event.preventDefault()
    goTo(activeIndex + 1)
  }
  if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
    event.preventDefault()
    goTo(activeIndex - 1)
  }
  if (event.key.toLowerCase() === "f") {
    document.querySelector("[data-fullscreen]")?.click()
  }
})

deck?.addEventListener(
  "scroll",
  () => {
    if (scrollFrame !== null) cancelAnimationFrame(scrollFrame)
    scrollFrame = requestAnimationFrame(() => {
      activeIndex = Math.max(
        0,
        Math.min(Math.round(deck.scrollLeft / deck.clientWidth), slides.length - 1)
      )
      updateCounter()
      updateSlideParam()
      scrollFrame = null
    })
  },
  { passive: true }
)

updateCounter()
updateSlideParam()
requestAnimationFrame(() => {
  const target = slides[activeIndex]
  deck?.scrollTo({ left: target.offsetLeft, top: 0, behavior: "auto" })
})
