import fs from "node:fs/promises"
import path from "node:path"
import { pathToFileURL } from "node:url"
import { Presentation, PresentationFile } from "@oai/artifact-tool"

const SKILL_DIR =
  "C:/Users/Phan Huy Hoang/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.61513/skills/presentations"
const WORKSPACE = "D:/Monorepo/customer-analytics-platform"
const TMP_DIR = path.join(WORKSPACE, "tmp/slides-build")
const OUTPUT_DIR = path.join(WORKSPACE, "output/presentations")
const FINAL_PPTX = path.join(
  OUTPUT_DIR,
  "customer-analytics-platform-10-slides.pptx"
)

const { finalizePresentation } = await import(
  pathToFileURL(
    path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")
  ).href
)

await fs.mkdir(TMP_DIR, { recursive: true })
await fs.mkdir(OUTPUT_DIR, { recursive: true })

const W = 1280
const H = 720
const FONT = "Arial"
const MONO = "Arial"
const C = {
  bg: "#FAFAFA",
  paper: "#FFFFFF",
  ink: "#111111",
  muted: "#666666",
  faint: "#A3A3A3",
  border: "#E6E6E6",
  borderStrong: "#C8C8C8",
  accent: "#91AE6E",
  accentDark: "#668546",
  accentPale: "#EEF4E7",
  black: "#050505",
}

const presentation = Presentation.create({ slideSize: { width: W, height: H } })

const logoPath = path.join(
  WORKSPACE,
  "frontend/src/assets/3cs-logo-primary.png"
)
const screenshotDir = path.join(WORKSPACE, "tmp/slide-screens")
const logo = new Uint8Array(await fs.readFile(logoPath))
const images = {
  login: new Uint8Array(await fs.readFile(path.join(screenshotDir, "01-login.png"))),
  home: new Uint8Array(
    await fs.readFile(path.join(screenshotDir, "02-client-home.png"))
  ),
  dashboard: new Uint8Array(
    await fs.readFile(path.join(screenshotDir, "04-admin-dashboard.png"))
  ),
  segments: new Uint8Array(
    await fs.readFile(path.join(screenshotDir, "05-segments.png"))
  ),
  priority: new Uint8Array(
    await fs.readFile(path.join(screenshotDir, "06-priority.png"))
  ),
}

function addShape(slide, {
  x,
  y,
  w,
  h,
  fill = "none",
  line = "none",
  radius = 0,
  geometry = "rect",
}) {
  return slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line:
      line === "none"
        ? { fill: "none", width: 0 }
        : { style: "solid", fill: line, width: 1 },
    ...(radius ? { borderRadius: radius } : {}),
  })
}

function addText(slide, text, x, y, w, h, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { fill: "none", width: 0 },
  })
  shape.text = text
  shape.text.style = {
    typeface: options.font ?? FONT,
    fontSize: options.size ?? 20,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.align ?? "left",
    verticalAlignment: options.valign ?? "top",
    autoFit: options.autoFit ?? "shrinkText",
    wrap: "square",
    insets: options.insets ?? { top: 0, right: 0, bottom: 0, left: 0 },
    lineSpacing: options.lineSpacing ?? 1.08,
  }
  return shape
}

function addRule(slide, x, y, w, color = C.border, weight = 1) {
  return slide.shapes.add({
    geometry: "line",
    position: { left: x, top: y, width: w, height: 0 },
    fill: "none",
    line: { style: "solid", fill: color, width: weight },
  })
}

function addLogo(slide, x, y, size = 34) {
  return slide.images.add({
    blob: logo,
    contentType: "image/png",
    alt: "3CS Store",
    fit: "contain",
    position: { left: x, top: y, width: size, height: size },
  })
}

function addHeader(slide, section, page) {
  addLogo(slide, 62, 30, 28)
  addText(slide, "3CS STORE", 98, 35, 150, 22, {
    size: 13,
    bold: true,
    color: C.ink,
  })
  addText(slide, section, 840, 36, 360, 20, {
    size: 12,
    color: C.muted,
    align: "right",
  })
  addRule(slide, 62, 72, 1156, C.border)
  addText(slide, `0${page} / 10`, 1140, 678, 78, 18, {
    size: 11,
    color: C.faint,
    align: "right",
  })
}

function addTitle(slide, title, subtitle) {
  addText(slide, title, 62, 96, 1040, 62, {
    size: 34,
    bold: true,
    color: C.ink,
  })
  if (subtitle) {
    addText(slide, subtitle, 62, 157, 1040, 34, {
      size: 17,
      color: C.muted,
    })
  }
}

function addScreenshot(slide, blob, alt, x, y, w, h) {
  addShape(slide, {
    x: x - 5,
    y: y - 5,
    w: w + 10,
    h: h + 10,
    fill: C.paper,
    line: C.borderStrong,
    radius: 12,
  })
  return slide.images.add({
    blob,
    contentType: "image/png",
    alt,
    fit: "cover",
    position: { left: x, top: y, width: w, height: h },
    geometry: "roundRect",
    borderRadius: 8,
  })
}

function addMetric(slide, label, value, detail, x, y, w) {
  addText(slide, label, x, y, w, 24, {
    size: 13,
    color: C.muted,
  })
  addText(slide, value, x, y + 28, w, 54, {
    size: 34,
    bold: true,
    color: C.ink,
  })
  addText(slide, detail, x, y + 83, w, 42, {
    size: 14,
    color: C.muted,
  })
}

function setNotes(slide, text) {
  slide.speakerNotes.textFrame.setText(text)
}

// Slide 1: Cover
{
  const slide = presentation.slides.add()
  slide.background.fill = C.black
  addLogo(slide, 66, 54, 44)
  addText(slide, "3CS STORE", 124, 64, 180, 26, {
    size: 15,
    bold: true,
    color: "#FFFFFF",
  })
  addText(
    slide,
    "Hệ thống phân khúc khách hàng\nvà dự đoán giá trị mua",
    66,
    184,
    930,
    160,
    { size: 48, bold: true, color: "#FFFFFF", lineSpacing: 0.98 }
  )
  addText(
    slide,
    "Customer Analytics Platform",
    68,
    367,
    620,
    38,
    { size: 22, color: C.accent }
  )
  addRule(slide, 68, 458, 1148, "#2C2C2C")
  addText(slide, "Phan Huy Hoàng · 25410219", 68, 486, 430, 28, {
    size: 16,
    color: "#D4D4D4",
  })
  addText(slide, "TP. Hồ Chí Minh · 09/2026", 68, 522, 430, 28, {
    size: 14,
    color: "#8F8F8F",
  })
  addText(slide, "01 / 10", 1134, 672, 82, 18, {
    size: 11,
    color: "#707070",
    align: "right",
  })
  setNotes(
    slide,
    "Nguồn nội dung: README dự án. Bố cục tham khảo dart-ai-slides.pdf và nguyên tắc Vercel Design Guidelines."
  )
}

// Slide 2: Problem
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "01 · Tổng quan", 2)
  addTitle(slide, "Bài toán đặt ra")
  addText(
    slide,
    "Dữ liệu khách hàng, giao dịch và tương tác thường nằm ở nhiều nơi. Doanh nghiệp khó nhận biết ai có giá trị cao, ai có khả năng mua lại và sản phẩm nào đang được quan tâm.",
    62,
    186,
    760,
    118,
    { size: 24, color: C.ink, lineSpacing: 1.16 }
  )
  const items = [
    ["Dữ liệu phân tán", "Hồ sơ, đơn hàng và hành vi khó đối chiếu trong một góc nhìn."],
    ["Ưu tiên chưa rõ", "Đội ngũ thiếu cơ sở để chọn khách hàng cần chăm sóc trước."],
    ["Phản ứng chậm", "Xu hướng sản phẩm và thay đổi hành vi chỉ được phát hiện sau khi đã xảy ra."],
  ]
  items.forEach(([label, body], index) => {
    const x = 62 + index * 386
    addRule(slide, x, 365, 330, index === 0 ? C.accentDark : C.borderStrong, 3)
    addText(slide, label, x, 390, 330, 34, { size: 20, bold: true })
    addText(slide, body, x, 438, 330, 84, { size: 16, color: C.muted })
  })
  setNotes(slide, "Tóm lược bài toán từ mục tiêu và phạm vi của repository.")
}

// Slide 3: Objectives and scope
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "01 · Tổng quan", 3)
  addTitle(slide, "Mục tiêu và phạm vi")
  const rows = [
    ["Quản lý", "Hồ sơ khách hàng, sản phẩm, giao dịch và tài khoản theo quyền."],
    ["Phân tích", "Phân khúc hành vi, điểm tiềm năng và xu hướng kinh doanh."],
    ["Dự đoán", "Ước lượng khả năng mua lại và tạo danh sách khách hàng ưu tiên."],
    ["Tương tác", "Theo dõi lượt xem sản phẩm và hỗ trợ truy vấn bằng 3CS AI."],
  ]
  rows.forEach(([label, body], index) => {
    const y = 204 + index * 92
    addText(slide, `0${index + 1}`, 62, y, 56, 34, {
      size: 17,
      bold: true,
      color: index === 0 ? C.accentDark : C.faint,
      font: MONO,
    })
    addText(slide, label, 145, y, 205, 34, { size: 20, bold: true })
    addText(slide, body, 385, y, 780, 52, { size: 17, color: C.muted })
    addRule(slide, 145, y + 67, 1020, C.border)
  })
  addText(
    slide,
    "Hai không gian sử dụng",
    62,
    594,
    260,
    24,
    { size: 13, color: C.muted }
  )
  addText(slide, "Khách hàng", 324, 586, 190, 34, { size: 20, bold: true })
  addText(slide, "Quản trị viên", 612, 586, 210, 34, { size: 20, bold: true })
  addText(slide, "Xem sản phẩm và tạo tín hiệu quan tâm", 324, 623, 240, 40, {
    size: 14,
    color: C.muted,
  })
  addText(slide, "Theo dõi dữ liệu và ra quyết định", 612, 623, 250, 40, {
    size: 14,
    color: C.muted,
  })
  setNotes(slide, "Nguồn: README, frontend README và backend API documentation.")
}

// Slide 4: Architecture
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "02 · Phân tích và thiết kế", 4)
  addTitle(slide, "Kiến trúc tổng thể", "Các thành phần chính và luồng trao đổi dữ liệu")
  const browser = addShape(slide, {
    x: 62,
    y: 258,
    w: 238,
    h: 136,
    fill: C.paper,
    line: C.borderStrong,
    radius: 10,
  })
  addText(slide, "Giao diện", 84, 278, 190, 32, { size: 21, bold: true })
  addText(slide, "React · TypeScript · Vite", 84, 320, 190, 26, {
    size: 15,
    color: C.accentDark,
  })
  addText(slide, "Client và trang quản trị", 84, 356, 190, 24, {
    size: 14,
    color: C.muted,
  })

  const api = addShape(slide, {
    x: 400,
    y: 232,
    w: 260,
    h: 188,
    fill: C.black,
    line: C.black,
    radius: 10,
  })
  addText(slide, "API và nghiệp vụ", 424, 258, 214, 36, {
    size: 22,
    bold: true,
    color: "#FFFFFF",
  })
  addText(slide, "FastAPI · Python", 424, 307, 214, 26, {
    size: 15,
    color: C.accent,
  })
  addText(slide, "Xác thực, quyền, kiểm tra dữ liệu\nvà điều phối phân tích", 424, 348, 214, 52, {
    size: 14,
    color: "#CFCFCF",
  })

  const data = addShape(slide, {
    x: 770,
    y: 162,
    w: 424,
    h: 86,
    fill: C.paper,
    line: C.borderStrong,
    radius: 8,
  })
  addText(slide, "PostgreSQL", 792, 182, 150, 28, { size: 19, bold: true })
  addText(slide, "Khách hàng · giao dịch · phân tích", 952, 184, 220, 24, {
    size: 14,
    color: C.muted,
  })
  const ml = addShape(slide, {
    x: 770,
    y: 284,
    w: 424,
    h: 86,
    fill: C.paper,
    line: C.borderStrong,
    radius: 8,
  })
  addText(slide, "Mô hình ML", 792, 304, 150, 28, { size: 19, bold: true })
  addText(slide, "Phân khúc và dự đoán mua lại", 952, 306, 220, 24, {
    size: 14,
    color: C.muted,
  })
  const cloud = addShape(slide, {
    x: 770,
    y: 406,
    w: 424,
    h: 86,
    fill: C.paper,
    line: C.borderStrong,
    radius: 8,
  })
  addText(slide, "Dịch vụ ngoài", 792, 426, 150, 28, { size: 19, bold: true })
  addText(slide, "Cloudinary · Groq Cloud", 952, 428, 220, 24, {
    size: 14,
    color: C.muted,
  })
  slide.shapes.connect(browser, api, {
    kind: "straight",
    fromSide: "right",
    toSide: "left",
    line: { style: "solid", fill: C.borderStrong, width: 2 },
    head: { type: "triangle", width: "sm", length: "sm" },
  })
  ;[data, ml, cloud].forEach((target) => {
    slide.shapes.connect(api, target, {
      kind: "straight",
      fromSide: "right",
      toSide: "left",
      line: { style: "solid", fill: C.borderStrong, width: 1.5 },
      head: { type: "triangle", width: "sm", length: "sm" },
    })
  })
  addText(slide, "HTTPS · JSON · SSE", 400, 458, 260, 24, {
    size: 13,
    color: C.muted,
    align: "center",
    font: MONO,
  })
  setNotes(slide, "Nguồn: AGENTS.md, README và backend API documentation.")
}

// Slide 5: Scoring logic
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "03 · Phân tích dữ liệu", 5)
  addTitle(slide, "Điểm tiềm năng khách hàng", "Kết hợp giá trị giao dịch và tín hiệu tương tác")
  addShape(slide, {
    x: 62,
    y: 215,
    w: 1156,
    h: 112,
    fill: C.black,
    line: C.black,
    radius: 10,
  })
  addText(
    slide,
    "Potential Score = (R × 0,35 + F × 0,30 + M × 0,20 + Interaction × 0,15) × 20",
    90,
    248,
    1100,
    42,
    { size: 24, bold: true, color: "#FFFFFF", align: "center", font: MONO }
  )
  const components = [
    ["R", "35%", "Mức độ gần đây"],
    ["F", "30%", "Tần suất mua"],
    ["M", "20%", "Giá trị chi tiêu"],
    ["I", "15%", "Tương tác sản phẩm"],
  ]
  components.forEach(([symbol, weight, label], index) => {
    const x = 62 + index * 289
    addText(slide, symbol, x, 376, 70, 54, {
      size: 36,
      bold: true,
      color: index === 0 ? C.accentDark : C.ink,
      font: MONO,
    })
    addText(slide, weight, x + 74, 384, 76, 32, { size: 20, bold: true })
    addText(slide, label, x, 440, 235, 32, { size: 15, color: C.muted })
  })
  addRule(slide, 62, 515, 1156, C.border)
  addMetric(slide, "Tiềm năng cao", "≥ 80", "Ưu tiên chăm sóc", 62, 548, 250)
  addMetric(slide, "Tiềm năng", "60–79", "Theo dõi và nuôi dưỡng", 367, 548, 260)
  addMetric(slide, "Thông thường", "< 60", "Duy trì tương tác", 690, 548, 230)
  addMetric(slide, "Chưa đủ dữ liệu", "—", "Không thay null bằng 0", 972, 548, 246)
  setNotes(slide, "Nguồn: backend/docs/API.md. Trọng số theo SCRIPT_DUAN_V4_EXCEL_PARITY.")
}

// Slide 6: Workflow
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "03 · Phân tích dữ liệu", 6)
  addTitle(slide, "Luồng nghiệp vụ phân tích")
  const steps = [
    ["01", "Khách hàng", "Xem sản phẩm\nvà phát sinh giao dịch"],
    ["02", "Thu thập", "Hồ sơ, đơn hàng\nvà lượt tương tác"],
    ["03", "Phân tích", "RFM, phân khúc\nvà điểm tiềm năng"],
    ["04", "Dự đoán", "Khả năng mua lại\nvà sản phẩm quan tâm"],
    ["05", "Hành động", "Danh sách ưu tiên\nvà chăm sóc phù hợp"],
  ]
  const boxes = steps.map(([number, title, body], index) => {
    const x = 62 + index * 230
    const box = addShape(slide, {
      x,
      y: 246,
      w: 196,
      h: 190,
      fill: index === 2 ? C.black : C.paper,
      line: index === 2 ? C.black : C.borderStrong,
      radius: 10,
    })
    addText(slide, number, x + 20, 267, 60, 24, {
      size: 14,
      bold: true,
      color: index === 2 ? C.accent : C.accentDark,
      font: MONO,
    })
    addText(slide, title, x + 20, 315, 156, 34, {
      size: 21,
      bold: true,
      color: index === 2 ? "#FFFFFF" : C.ink,
    })
    addText(slide, body, x + 20, 365, 156, 50, {
      size: 14,
      color: index === 2 ? "#CCCCCC" : C.muted,
    })
    return box
  })
  for (let index = 0; index < boxes.length - 1; index += 1) {
    slide.shapes.connect(boxes[index], boxes[index + 1], {
      kind: "straight",
      fromSide: "right",
      toSide: "left",
      line: { style: "solid", fill: C.borderStrong, width: 1.5 },
      head: { type: "triangle", width: "sm", length: "sm" },
    })
  }
  addText(
    slide,
    "Dữ liệu từ trải nghiệm mua sắm quay lại phục vụ quyết định quản trị",
    190,
    510,
    900,
    44,
    { size: 20, bold: true, align: "center" }
  )
  setNotes(slide, "Luồng tổng hợp từ các chức năng client, product analytics và dashboard.")
}

// Slide 7: Login and roles
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "04 · Giao diện và phân quyền", 7)
  addTitle(slide, "Đăng nhập và phân quyền")
  addScreenshot(slide, images.login, "Màn hình đăng nhập 3CS Store", 62, 190, 678, 424)
  addText(slide, "Hai không gian sau xác thực", 800, 206, 368, 32, {
    size: 20,
    bold: true,
  })
  addRule(slide, 800, 258, 368, C.borderStrong)
  addText(slide, "Khách hàng", 800, 290, 180, 30, { size: 20, bold: true })
  addText(
    slide,
    "Xem danh mục và chi tiết sản phẩm. Mỗi lượt quan tâm tạo thêm dữ liệu hành vi.",
    800,
    330,
    350,
    76,
    { size: 16, color: C.muted }
  )
  addText(slide, "Quản trị viên", 800, 445, 180, 30, { size: 20, bold: true })
  addText(
    slide,
    "Quản lý dữ liệu, tài khoản, mô hình và toàn bộ báo cáo phân tích.",
    800,
    485,
    350,
    66,
    { size: 16, color: C.muted }
  )
  addText(slide, "JWT · refresh session · permission checks", 800, 590, 350, 24, {
    size: 13,
    color: C.accentDark,
    font: MONO,
  })
  setNotes(slide, "Ảnh chụp trực tiếp từ hệ thống demo. Quyền tham khảo backend/docs/API.md.")
}

// Slide 8: Client experience
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "04 · Giao diện và phân quyền", 8)
  addTitle(slide, "Trải nghiệm phía khách hàng")
  addText(slide, "Tìm sản phẩm", 62, 204, 220, 30, { size: 20, bold: true })
  addText(
    slide,
    "Danh sách có tìm kiếm, lọc danh mục và phân trang để người dùng tiếp cận sản phẩm nhanh hơn.",
    62,
    245,
    360,
    88,
    { size: 16, color: C.muted }
  )
  addText(slide, "Tạo tín hiệu quan tâm", 62, 378, 250, 30, {
    size: 20,
    bold: true,
  })
  addText(
    slide,
    "Lượt xem sản phẩm được ghi nhận và liên kết với hồ sơ khách hàng để phục vụ phân tích.",
    62,
    419,
    360,
    88,
    { size: 16, color: C.muted }
  )
  addText(slide, "Giao diện thích ứng", 62, 552, 220, 30, {
    size: 20,
    bold: true,
  })
  addText(slide, "Hỗ trợ chế độ sáng, tối và nhiều kích thước màn hình.", 62, 593, 350, 56, {
    size: 16,
    color: C.muted,
  })
  addScreenshot(slide, images.home, "Trang chủ và sản phẩm nổi bật", 468, 188, 750, 469)
  setNotes(slide, "Ảnh chụp trực tiếp từ giao diện client của hệ thống demo.")
}

// Slide 9: Admin analytics
{
  const slide = presentation.slides.add()
  slide.background.fill = C.bg
  addHeader(slide, "04 · Giao diện và phân quyền", 9)
  addTitle(slide, "Quản trị và phân tích")
  addScreenshot(slide, images.dashboard, "Dashboard quản trị", 62, 186, 744, 465)
  addScreenshot(slide, images.segments, "Bảng phân khúc khách hàng", 842, 186, 376, 235)
  addScreenshot(slide, images.priority, "Danh sách khách hàng ưu tiên", 842, 447, 376, 204)
  addText(slide, "Một màn hình tổng quan", 842, 658, 190, 20, {
    size: 12,
    bold: true,
    color: C.accentDark,
  })
  setNotes(
    slide,
    "Ảnh chụp trực tiếp từ Dashboard, Phân khúc và Danh sách ưu tiên của hệ thống demo."
  )
}

// Slide 10: Conclusion
{
  const slide = presentation.slides.add()
  slide.background.fill = C.black
  addLogo(slide, 66, 44, 38)
  addText(slide, "Kết quả triển khai", 66, 126, 520, 58, {
    size: 38,
    bold: true,
    color: "#FFFFFF",
  })
  addText(
    slide,
    "Hệ thống đã kết nối trải nghiệm khách hàng với phân tích quản trị trong một luồng dữ liệu thống nhất.",
    66,
    198,
    720,
    72,
    { size: 22, color: "#D5D5D5" }
  )
  const done = [
    "Quản lý khách hàng, sản phẩm, giao dịch và tài khoản",
    "Phân khúc, điểm tiềm năng và dự đoán mua lại",
    "Theo dõi mức độ quan tâm sản phẩm và danh sách ưu tiên",
    "113 kiểm thử frontend đạt trong lần kiểm tra gần nhất",
  ]
  done.forEach((text, index) => {
    const y = 326 + index * 54
    addShape(slide, {
      x: 68,
      y: y + 4,
      w: 10,
      h: 10,
      fill: C.accent,
      line: C.accent,
      radius: 5,
    })
    addText(slide, text, 96, y, 620, 32, { size: 17, color: "#FFFFFF" })
  })
  addRule(slide, 804, 126, 1, "#363636")
  addText(slide, "Hướng phát triển", 850, 126, 350, 44, {
    size: 24,
    bold: true,
    color: "#FFFFFF",
  })
  addText(
    slide,
    "Mở rộng dữ liệu thực tế\n\nĐánh giá mô hình trên tập độc lập\n\nTheo dõi chất lượng dự đoán theo thời gian\n\nHoàn thiện quy trình chăm sóc theo từng phân khúc",
    850,
    208,
    350,
    260,
    { size: 17, color: "#BDBDBD", lineSpacing: 1.2 }
  )
  addText(slide, "Cảm ơn thầy", 850, 554, 350, 54, {
    size: 34,
    bold: true,
    color: C.accent,
  })
  addText(slide, "Nhóm xin lắng nghe câu hỏi và góp ý", 850, 616, 350, 30, {
    size: 15,
    color: "#8F8F8F",
  })
  addText(slide, "10 / 10", 1134, 672, 82, 18, {
    size: 11,
    color: "#707070",
    align: "right",
  })
  setNotes(
    slide,
    "Kết quả kiểm thử frontend được xác nhận bằng Vitest: 32 file, 113 test đạt. Hạn chế và hướng phát triển tổng hợp từ trạng thái dự án hiện tại."
  )
}

const candidatePath = path.join(TMP_DIR, "candidate.pptx")
await (await PresentationFile.exportPptx(presentation)).save(candidatePath)

for (let index = 0; index < presentation.slides.items.length; index += 1) {
  const slide = presentation.slides.items[index]
  const preview = await presentation.export({ slide, format: "png", scale: 1 })
  await fs.writeFile(
    path.join(TMP_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`),
    new Uint8Array(await preview.arrayBuffer())
  )
}

const requirements = {
  explicitTotalSlideCount: 10,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
}
const stagingDir = path.join(TMP_DIR, ".codex-finalizer")
await fs.mkdir(stagingDir, { recursive: true })
const result = await finalizePresentation({
  ...requirements,
  workspaceDir: WORKSPACE,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable:
    "C:/Users/Phan Huy Hoang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
  integrityValidatorPath: path.join(
    SKILL_DIR,
    "container_tools/inspect_presentation_package_integrity.py"
  ),
  layoutValidatorPath: path.join(
    SKILL_DIR,
    "container_tools/inspect_presentation_layout_geometry.py"
  ),
  layoutArgs: [
    "--expected-slide-size-emu",
    "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  requiredNativeTableOwnerSlides: [],
  fontPolicy: { basis: "design", families: [FONT] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "deck.validation.json"),
})

console.log(JSON.stringify({ success: true, output: FINAL_PPTX, result }))
