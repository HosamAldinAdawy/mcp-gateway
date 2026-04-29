import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/v1": "http://localhost:8000",
      "/status": "http://localhost:8000",
      "/mcp": "http://localhost:8000",
    },
  },
  build: {
    outDir: "../gateway/static",
    emptyOutDir: true,
  },
});
