import { mkdir, rm } from "node:fs/promises"
import path from "node:path"
import { pathToFileURL } from "node:url"
import { chromium } from "playwright-core"

const output = path.resolve("../html-slides-qa")
await rm(output, { recursive: true, force: true })
await mkdir(output, { recursive: true })

const browser = await chromium.launch({
  executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
  headless: true,
})

try {
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } })
  const errors = []
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text())
  })
  const slideUrl = pathToFileURL(
    path.resolve("../../slides/customer-analytics/index.html")
  ).href
  await page.goto(slideUrl, { waitUntil: "networkidle" })
  await page.evaluate(() => document.fonts.ready)
  const navigation = []
  for (let index = 0; index < 4; index += 1) {
    await page.locator(".controls").hover()
    await page.locator("[data-next]").click()
    await page.waitForTimeout(900)
    navigation.push({
      counter: await page.locator("[data-current-slide]").innerText(),
      scrollX: await page.evaluate(() => document.querySelector(".deck")?.scrollLeft),
    })
  }
  if (navigation.at(-1)?.counter !== "5 / 10") {
    throw new Error(`Điều hướng ngang không đúng: ${JSON.stringify(navigation)}`)
  }
  if (!page.url().endsWith("?slide=5")) {
    throw new Error(`URL slide 5 không đúng: ${page.url()}`)
  }
  for (let index = 0; index < 4; index += 1) {
    await page.locator(".controls").hover()
    await page.locator("[data-next]").click()
    await page.waitForTimeout(900)
  }
  await page.locator("[data-video-open]").click()
  await page.waitForTimeout(1200)
  const videoState = await page.evaluate(() => {
    const dialog = document.querySelector("[data-video-dialog]")
    const video = document.querySelector("[data-demo-video]")
    return {
      dialogOpen: dialog instanceof HTMLDialogElement && dialog.open,
      paused: video instanceof HTMLVideoElement ? video.paused : true,
      source: video instanceof HTMLVideoElement ? video.currentSrc : "",
    }
  })
  if (!videoState.dialogOpen || videoState.paused || !videoState.source.includes("demo.mp4")) {
    throw new Error(`Trình phát video không đúng: ${JSON.stringify(videoState)}`)
  }
  await page.locator("[data-video-close]").click()
  await page.waitForTimeout(200)
  const videoClosed = await page.evaluate(() => {
    const dialog = document.querySelector("[data-video-dialog]")
    const video = document.querySelector("[data-demo-video]")
    return {
      dialogOpen: dialog instanceof HTMLDialogElement && dialog.open,
      paused: video instanceof HTMLVideoElement ? video.paused : false,
    }
  })
  if (videoClosed.dialogOpen || !videoClosed.paused) {
    throw new Error(`Không đóng được video: ${JSON.stringify(videoClosed)}`)
  }
  if (!page.url().endsWith("?slide=9")) {
    throw new Error(`URL slide 9 không đúng: ${page.url()}`)
  }
  await page.reload({ waitUntil: "networkidle" })
  await page.waitForTimeout(300)
  const restoredCounter = await page.locator("[data-current-slide]").innerText()
  if (restoredCounter !== "9 / 10") {
    throw new Error(`Không khôi phục đúng slide sau khi tải lại: ${restoredCounter}`)
  }
  await page.evaluate(() =>
    document.querySelector(".deck")?.scrollTo({ left: 0, top: 0, behavior: "instant" })
  )
  await page.waitForTimeout(300)
  const slides = page.locator(".slide-shell")
  const count = await slides.count()
  if (count !== 10) throw new Error(`Số slide không đúng: ${count}`)
  for (let index = 0; index < count; index += 1) {
    await slides.nth(index).screenshot({
      path: path.join(output, `slide-${String(index + 1).padStart(2, "0")}.png`),
    })
  }
  await page.pdf({
    path: path.join(output, "customer-analytics-html-slides.pdf"),
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  })
  console.log(
    JSON.stringify({
      success: true,
      count,
      errors,
      navigation,
      videoState,
      videoClosed,
      restoredCounter,
    })
  )
} finally {
  await browser.close()
}
