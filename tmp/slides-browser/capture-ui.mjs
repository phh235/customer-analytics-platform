import { mkdir, rm } from "node:fs/promises"
import path from "node:path"
import { chromium } from "playwright-core"

const chunks = []
for await (const chunk of process.stdin) chunks.push(chunk)
const credentials = JSON.parse(Buffer.concat(chunks).toString("utf8"))
const BASE = "https://lit-merchant-voip-listed.trycloudflare.com"
const OUTPUT = path.resolve("../slide-screens")
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe"

await rm(OUTPUT, { recursive: true, force: true })
await mkdir(OUTPUT, { recursive: true })

async function newBrowser() {
  return chromium.launch({ executablePath: CHROME, headless: true })
}

async function login(page, email, password, expectedUrl) {
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" })
  await page.getByLabel("Email").fill(email)
  await page.locator("#login-password").fill(password)
  await page.getByRole("button", { name: "Đăng nhập" }).click()
  await page.waitForURL(expectedUrl, { timeout: 60_000 })
  await page.waitForTimeout(4000)
}

const browser = await newBrowser()
try {
  const loginPage = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await loginPage.goto(`${BASE}/login`, { waitUntil: "networkidle" })
  await loginPage.screenshot({ path: path.join(OUTPUT, "01-login.png") })
  await loginPage.close()

  const clientContext = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const client = await clientContext.newPage()
  await login(client, credentials.clientEmail, credentials.clientPassword, /\/$/)
  await client
    .getByRole("heading", { name: "Chào mừng bạn đến với 3CS Store" })
    .waitFor({ timeout: 60_000 })
  await client
    .locator('[data-slot="skeleton"]')
    .first()
    .waitFor({ state: "detached", timeout: 60_000 })
    .catch(() => undefined)
  await client.waitForTimeout(1200)
  await client.screenshot({ path: path.join(OUTPUT, "02-client-home.png") })
  const firstProduct = client.locator('a[aria-label^="Xem chi tiết"]').first()
  await firstProduct.scrollIntoViewIfNeeded()
  await firstProduct.click()
  await client.waitForURL(/\/products\/.+/)
  await client.locator("main h1").waitFor({ timeout: 60_000 })
  await client
    .locator('[data-slot="skeleton"]')
    .first()
    .waitFor({ state: "detached", timeout: 60_000 })
    .catch(() => undefined)
  await client.waitForTimeout(1500)
  await client.screenshot({ path: path.join(OUTPUT, "03-product-detail.png") })
  await clientContext.close()

  const adminContext = await browser.newContext({ viewport: { width: 1440, height: 900 } })
  const admin = await adminContext.newPage()
  await login(admin, credentials.adminEmail, credentials.adminPassword, /\/dashboard/)
  await admin.getByRole("heading", { name: "Tổng quan" }).waitFor({ timeout: 60_000 })
  await admin
    .locator('[data-slot="skeleton"]')
    .first()
    .waitFor({ state: "detached", timeout: 60_000 })
    .catch(() => undefined)
  await admin.screenshot({ path: path.join(OUTPUT, "04-admin-dashboard.png") })
  await admin.goto(`${BASE}/dashboard/analytics/segments`, { waitUntil: "networkidle" })
  await admin.getByRole("heading", { name: "Phân khúc khách hàng" }).waitFor()
  await admin.screenshot({ path: path.join(OUTPUT, "05-segments.png") })
  await admin.goto(`${BASE}/dashboard/analytics/priority`, { waitUntil: "networkidle" })
  await admin.getByRole("heading", { name: "Danh sách ưu tiên" }).waitFor()
  await admin.screenshot({ path: path.join(OUTPUT, "06-priority.png") })
  await adminContext.close()
} finally {
  await browser.close()
}

console.log(JSON.stringify({ success: true, output: OUTPUT }))
