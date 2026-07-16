import { defineConfig } from "vitest/config";
import { loadEnv, type Plugin } from "vite";
import { readFileSync } from "node:fs";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";
import { parse as parseYaml } from "yaml";
import path from "node:path";

const pkg = JSON.parse(readFileSync(new URL("./package.json", import.meta.url), "utf8"));

// Import *.yaml as a parsed JS object at build time. This is what lets the console read the
// evaluator's rubric.yaml as the single source of truth (INV-1) without a committed copy. We
// carry a tiny plugin instead of a third-party one to keep the dependency (js-yaml) with its
// known merge-key advisories out of the tree — the maintained `yaml` parser has none.
function yamlPlugin(): Plugin {
  return {
    name: "governance-console:yaml",
    transform(code, id) {
      if (!/\.ya?ml$/.test(id)) return null;
      return { code: `export default ${JSON.stringify(parseYaml(code))};`, map: null };
    },
  };
}

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, path.resolve(__dirname), "");
  const basePath = env.VITE_BASE || env.VITE_BASE_PATH || "/";

  return {
    base: basePath,
    resolve: { alias: { "@": path.resolve(__dirname, "src") } },
    plugins: [
      yamlPlugin(),
      react(),
      tailwindcss(),
      VitePWA({
        registerType: "autoUpdate",
        injectRegister: "auto",
        devOptions: { enabled: false },
        workbox: {
          clientsClaim: true,
          // false: an in-progress assessment should not be forced to reload mid-session.
          skipWaiting: false,
          cleanupOutdatedCaches: true,
          navigateFallback: "index.html",
          globPatterns: ["**/*.{js,css,html,woff2,ico,svg,png}"],
          maximumFileSizeToCacheInBytes: 3 * 1024 * 1024,
        },
        manifest: {
          name: "AI Governance Console",
          short_name: "Governance Console",
          description:
            "Local, offline-capable governance console — interactive risk assessment over the toolkit's scoring rubric.",
          display: "standalone",
          theme_color: "#0b0b0b",
          background_color: "#0b0b0b",
          start_url: basePath,
          scope: basePath,
          // A single, versionable SVG icon — no binary blobs enter the repo (BIBLE ethos).
          icons: [{ src: "icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any maskable" }],
        },
      }),
    ],
    build: {
      sourcemap: "hidden",
      assetsInlineLimit: (filePath) => (/\.(woff2?|ttf|otf|eot)$/i.test(filePath) ? false : undefined),
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes("node_modules")) return undefined;
            if (/\/node_modules\/(react|react-dom|scheduler)\//.test(id)) return "react-vendor";
            if (/\/node_modules\/(i18next|react-i18next)\//.test(id)) return "i18n";
            return undefined;
          },
        },
      },
    },
    // The rubric.yaml lives in the sibling evaluator/ tree, outside app/. Allow the dev server to
    // read it (build/vitest resolve it directly and are unaffected by this).
    server: { port: 5273, fs: { allow: [path.resolve(__dirname, "..")] } },
    define: {
      __DEV__: JSON.stringify(command !== "build"),
      __APP_VERSION__: JSON.stringify(pkg.version),
    },
    test: { environment: "node" },
  };
});
