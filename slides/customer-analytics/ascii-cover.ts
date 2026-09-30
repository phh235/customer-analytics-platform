import { createAsciiObject } from "../../frontend/src/components/ascii-object"
import logoUrl from "./assets/3cs-logo.png"

const root = document.querySelector<HTMLElement>("[data-cover-ascii]")
const canvas = document.querySelector<HTMLCanvasElement>("[data-cover-ascii-canvas]")

if (root && canvas) {
  const instance = createAsciiObject(
    { canvas },
    {
      src: logoUrl,
      ascii: true,
      autoRotate: false,
      background: "",
      cellSize: 9,
      floatIntensity: 2.8,
      highlight: "#91ae6e",
      orbit: false,
      rotationIntensity: 0.8,
      scale: 4.2,
      xOffset: 0,
      yOffset: -0.2,
      zoom: false,
      onLoad: () => root.classList.add("is-ready"),
    }
  )

  window.addEventListener("beforeunload", () => instance?.destroy(), { once: true })
}
