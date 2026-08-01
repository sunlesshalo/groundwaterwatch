import { defineConfig } from "astro/config";

// og:image and canonical URLs must be absolute, so `site` has to match wherever
// this is actually served. SITE_URL wins; CF_PAGES_URL is set automatically by
// Cloudflare Pages; the domain is the fallback for production.
const site = process.env.SITE_URL || process.env.CF_PAGES_URL || "https://groundwaterwatch.eu";

// A GitHub Pages *project* site is served from /<repo>/, not the domain root.
// Set BASE_PATH=/groundwaterwatch there; leave it unset for root-served hosts
// (Cloudflare Pages, or GitHub Pages behind a custom domain).
const base = process.env.BASE_PATH || "/";

export default defineConfig({
  site,
  base,
  output: "static",
  build: {
    format: "directory",
  },
});
