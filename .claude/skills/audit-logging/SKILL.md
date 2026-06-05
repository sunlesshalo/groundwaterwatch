---
name: Audit Logging
description: Records all operations for accountability, debugging, and reporting. Use when executing operations that modify target systems, generating reports, or investigating past actions. Maintains memory/AUDIT.md as the source of truth.
---

# Audit Logging

## What to Log

Every action that modifies a target system must be logged:

| Always Log | Never Log |
|-----------|-----------|
| Commands that modify remote systems | Credentials, API keys, passwords |
| Risk assessments and their outcomes | Personal data (names, emails) |
| Approvals and rejections | Read-only queries |
| Rollback operations | Internal tool-use metadata |
| Errors and recovery actions | Conversation content |

## Log File

All entries go to `memory/AUDIT.md`. Create it if it doesn't exist.

## Entry Format

```
[YYYY-MM-DD HH:MM] [ACTION] target=TARGET risk=LEVEL result=RESULT
  Details: what was done
```

**ACTION types:** `ASSESS`, `EXECUTE`, `VERIFY`, `ROLLBACK`, `ERROR`, `APPROVE`, `REJECT`

**Examples:**
```
[2026-03-12 14:30] [ASSESS] target=shop.example.com risk=MEDIUM result=pending
  Details: Plugin update assessment — 3 plugins need updating
[2026-03-12 14:31] [APPROVE] target=shop.example.com risk=MEDIUM result=approved
  Details: User approved plugin update
[2026-03-12 14:35] [EXECUTE] target=shop.example.com risk=MEDIUM result=success
  Details: Updated woocommerce (8.4.0 → 8.5.1), akismet (5.3 → 5.3.1)
[2026-03-12 14:36] [VERIFY] target=shop.example.com risk=LOW result=success
  Details: Homepage loads, checkout flow works, no PHP errors in log
```

## Redaction

Sensitive values appear as `[REDACTED]`:
```
[2026-03-12 15:00] [EXECUTE] target=api.example.com risk=HIGH result=success
  Details: Rotated API key — old=[REDACTED] new=[REDACTED]
```

## Non-Blocking Rule

Audit logging must **never** prevent the actual operation from completing. If writing to AUDIT.md fails (file locked, disk full, permission error), the operation continues. Log the logging failure to CONTEXT.md instead.

## Reporting

The `/report` command uses AUDIT.md as its primary data source. Entries are transformed from technical log format to plain English for client-facing reports.

## Retention

AUDIT.md grows over time. When it exceeds 500 lines, use `/archive` to move older entries to git history. Keep the last 100 entries active.
