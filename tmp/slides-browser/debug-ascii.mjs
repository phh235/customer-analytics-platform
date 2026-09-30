import { chromium } from "playwright-core"

const browser = await chromium.launch({
  executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  headless: true,
})
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } })
const messages = []
page.on("console", (message) => messages.push(`${message.type()}: ${message.text()}`))
page.on("pageerror", (error) => messages.push(`pageerror: ${error.message}`))
await page.goto(process.argv[2] ?? "http://127.0.0.1:4173/?slide=1", {
  waitUntil: "networkidle",
})
await page.waitForTimeout(5000)
const state = await page.evaluate(() => {
  const root = document.querySelector("[data-cover-ascii]")
  const canvas = document.querySelector("[data-cover-ascii-canvas]")
  return {
    className: root?.className,
    canvasHeight: canvas instanceof HTMLCanvasElement ? canvas.height : null,
    canvasWidth: canvas instanceof HTMLCanvasElement ? canvas.width : null,
    opacity: canvas ? getComputedStyle(canvas).opacity : null,
  }
})
console.log(JSON.stringify({ state, messages }))
await page.screenshot({ path: "../html-slides-qa/ascii-debug.png" })
await browser.close()
