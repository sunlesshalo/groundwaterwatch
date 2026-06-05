---
description: Run the pre-launch checklist and prepare for production deployment
---

Invoke the agent-skills:shipping-and-launch skill.

## Step 0: Stack detection (before running any check)

Inspect the project to decide which checklist items actually apply. A generic checklist produces false failures on stacks that don't match.

| Signal | Checks to enable |
|---|---|
| `package.json` | `npm audit`, lint, type-check, bundle size, `npm test` |
| `pyproject.toml` / `requirements.txt` | `pip-audit`, `ruff`/`mypy`, `pytest` |
| `Cargo.toml` | `cargo audit`, `cargo clippy`, `cargo test` |
| `go.mod` | `govulncheck`, `go vet`, `go test` |
| Database migrations dir | Migration readiness + rollback plan |
| Backend / API endpoints | Health check endpoint, rate limiting, auth |
| Static site (HTML/CSS/JS only, no build) | CSP meta, SRI hashes, security headers in host config (vercel.json/netlify.toml/nginx) |
| Client-side auth (OAuth in browser) | API key referrer restrictions, token storage review |
| PWA (manifest + service worker) | SW cache bump on deploy, offline behavior verified |
| Frontend UI | a11y (ARIA, keyboard, contrast), Core Web Vitals |
| CI config (`.github/workflows`, `.gitlab-ci.yml`) | Pipeline green |

Items for stacks not present in the project get marked **N/A** in the report, not **FAIL**. Be explicit about why each N/A applies — future readers need to know whether it was skipped correctly or missed.

## Step 1: Run the applicable checklist

Only run items enabled by Step 0. For each item: **PASS**, **FAIL**, **N/A** (with reason), or **UNVERIFIED** (needs external access like GCP console, production dashboard, etc.).

Generic categories (prune to what applies):

1. **Code Quality** — Tests pass, build clean, lint clean, no TODOs, no `console.log` / debug prints
2. **Security** — No secrets in code, dep audit clean, input validation, auth checks, security headers (CSP/HSTS/X-Frame/Referrer-Policy/Permissions-Policy), SRI on CDN scripts
3. **Performance** — Core Web Vitals, bundle size, no N+1, caching configured
4. **Accessibility** — Keyboard nav, screen reader, WCAG 2.1 AA contrast, focus management
5. **Infrastructure** — Env vars set, migrations ready, monitoring, error reporting, health check
6. **Documentation** — README current, changelog updated, ADRs for arch decisions

## Step 2: Report + rollback plan

Append findings to `memory/AUDIT.md` under a `## Ship Audit` section. Structure:

```
## Ship Audit — YYYY-MM-DD

### Stack detected
[list of signals from Step 0]

### Results
| Category | Status | Blockers |
|---|---|---|
...

### Blockers (must fix before launch)
...

### Rollback plan
...
```

Define the rollback plan before proceeding. A ship without a documented rollback is not a ship — it's a gamble.
