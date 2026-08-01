import { defineConfig } from "astro/config";

// og:image and canonical URLs must be absolute, so `site` has to match wherever
// this is actually served. SITE_URL wins; CF_PAGES_URL is set automatically by
// Cloudflare Pages; the domain is the fallback for production.
const site = process.env.SITE_URL || process.env.CF_PAGES_URL || "https://groundwaterwatch.eu";

export default defineConfig({
  site,
  output: "static",
  build: {
    format: "directory",
  },
});
