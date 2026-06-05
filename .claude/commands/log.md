Log important context to memory for future sessions.

## When to Use
- After solving an error or bug
- When discovering something about the data, API, or system
- When making a decision that affects future work

## Categories

| Tag | Use For | Example |
|-----|---------|---------|
| `[error]` | Problem -> solution | `[error] API 429 on bulk requests -> add 100ms delay` |
| `[discovery]` | Something learned | `[discovery] TEST_ prefix = sandbox accounts` |
| `[decision]` | Choice + reasoning | `[decision] Using pagination=50, API times out at 100+` |

## Steps

1. Identify the category (error/discovery/decision)

2. Append to `memory/CONTEXT.md` under **Notes** section:
```markdown
- [category] Description -> outcome/solution
```

3. Confirm what was logged

## Examples

```markdown
- [error] Docker build fails on M1 -> use --platform linux/amd64
- [discovery] /api/v2 endpoints require different auth header
- [decision] Chose SQLite over Postgres for MVP - simpler deployment
```
