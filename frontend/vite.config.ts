import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { loadEnv } from "vite"
import { defineConfig } from "vitest/config"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, "VITE_")
  const apiTarget = /^https?:\/\//.test(env.VITE_API_URL ?? "")
    ? new URL(env.VITE_API_URL).origin
    : "http://127.0.0.1:8000"

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      open: true,
      port: 4000,
      proxy: {
        "/api": {
          target: apiTarget,
          changeOrigin: true,
          cookieDomainRewrite: "",
        },
      },
      host: true,
      allowedHosts: true,
    },
    test: {
      environment: "jsdom",
      setupFiles: ["./src/test/setup.ts"],
      clearMocks: true,
      restoreMocks: true,
    },
  }
})
