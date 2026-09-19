import js from "@eslint/js"
import globals from "globals"
import reactHooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"
import tseslint from "typescript-eslint"
import { defineConfig, globalIgnores } from "eslint/config"

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
    },
  },
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: [
      "src/components/ui/**",
      "src/components/common/common-table.tsx",
      "src/components/common/app-select.tsx",
      "**/*.test.tsx",
    ],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          paths: [
            {
              name: "@/components/ui/table",
              message:
                "Use CommonTable for the shared table layout and pagination.",
            },
            {
              name: "@/components/ui/select",
              message: "Use AppSelect for consistent selection controls.",
            },
            {
              name: "@base-ui/react/select",
              message: "Use AppSelect for consistent selection controls.",
            },
          ],
        },
      ],
      "no-restricted-syntax": [
        "error",
        {
          selector: 'JSXOpeningElement[name.name="select"]',
          message: "Use AppSelect instead of a native select.",
        },
        {
          selector: 'JSXOpeningElement[name.name="table"]',
          message: "Use CommonTable instead of a custom table.",
        },
      ],
    },
  },
])
