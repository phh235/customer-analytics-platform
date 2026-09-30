import path from "node:path"
import { fileURLToPath } from "node:url"

const directory = path.dirname(fileURLToPath(import.meta.url))

export default {
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
  publicDir: false,
  build: {
    assetsInlineLimit: Number.POSITIVE_INFINITY,
    emptyOutDir: false,
    lib: {
      entry: path.resolve(directory, "ascii-cover.ts"),
      fileName: "ascii-cover",
      formats: ["iife"],
      name: "AsciiCover",
    },
    outDir: path.resolve(directory, "assets/ascii"),
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
}
