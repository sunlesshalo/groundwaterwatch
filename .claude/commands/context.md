Show context status and suggest hygiene actions.

## Steps

### 1. Measure Context Files

```bash
wc -c memory/CONTEXT.md memory/STATE.json memory/errors.json 2>/dev/null
```

Report sizes in bytes. Estimate tokens (~4 chars = 1 token).

### 2. Check Session Age

```bash
git log -1 --format="%ar" -- memory/CONTEXT.md
```

How long since last context commit?

### 3. Count Error Patterns

```bash
grep -c '"category"' memory/errors.json 2>/dev/null || echo "0"
```

If 10+ errors logged, suggest pattern analysis.

### 4. Assess Context Health

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| CONTEXT.md | <5KB | 5-15KB | >15KB |
| errors.json entries | <10 | 10-25 | >25 |
| Session age | <1 day | 1-3 days | >3 days |

### 5. Output Status Report

```
## Context Status

**CONTEXT.md:** X bytes (~Y tokens) [GREEN/YELLOW/RED]
**errors.json:** N entries [GREEN/YELLOW/RED]
**Last commit:** Z ago [GREEN/YELLOW/RED]

### Loaded This Session
- Skills: [list if known]
- Files read: [estimate]

### Recommendations
- [If CONTEXT.md large] → Run /archive to move old sessions to git
- [If many errors] → Review patterns, extract rules to CLAUDE.md
- [If session old] → Run /checkpoint to commit state
```

### 6. Suggest Compaction (if needed)

If RED status on any metric:
> "Consider running `/archive` to move completed session notes to git history, keeping active context lean."

## Philosophy

Context hygiene is proactive, not reactive. Regular checks prevent token waste and context loss.
