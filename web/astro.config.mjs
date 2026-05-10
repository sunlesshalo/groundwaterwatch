import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://groundwaterwatch.eu",
  output: "static",
  build: {
    format: "directory",
  },
});
