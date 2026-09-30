const fs = require("node:fs")
const path = require("node:path")
const sharp = require("C:/Users/Phan Huy Hoang/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp")

const root = path.resolve(__dirname, "../..")
const source = path.join(root, "slides/customer-analytics/assets/tech")
const output = path.join(__dirname, "tech-icons")
fs.mkdirSync(output, { recursive: true })

const icons = [
  "react",
  "typescript",
  "vite",
  "fastapi",
  "python",
  "postgresql",
  "cloudinary",
  "groq",
]

Promise.all(
  icons.map((name) =>
    sharp(path.join(source, `${name}.svg`), { density: 300 })
      .resize({ height: name === "cloudinary" || name === "groq" ? 96 : 128 })
      .png()
      .toFile(path.join(output, `${name}.png`))
  )
).catch((error) => {
  console.error(error)
  process.exit(1)
})
