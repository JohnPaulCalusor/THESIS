// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5179,
    proxy: {
      "/proxy_api": {
        target: "http://localhost:8000/api",
        changeOrigin: true,
        secure: false,
        rewrite: (p) => p.replace(/^\/proxy_api/, ""),
      },
    },
  },
});
