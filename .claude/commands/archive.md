Archive old sessions to git history. Keeps active memory lean.

Based on Anthropic's research: git history IS the archive.

## When to Use
- Weekly maintenance
- When CONTEXT.md exceeds ~300 lines
- When STATE.json has many passing features
- Before starting a major new phase

## Steps

### 1. Check Current State
```bash
wc -l memory/CONTEXT.md
jq '[.features[] | select(.status=="passing")] | length' memory/STATE.json
```

### 2. Create Archive Commit
```bash
git add -A
git commit -m "Archive: [date range] sessions

Sessions archived:
- [date]: [summary]

Completed features archived:
- [feature 1]
- [feature 2]

Active work: [current focus]"
```

### 3. Clean STATE.json
Remove features with `status: "passing"` and `verified: true`.
Keep only: `failing` and `in_progress` features.

### 4. Trim CONTEXT.md
- Keep last 5-7 sessions
- Keep Notes section
- Remove older session entries

### 5. Commit Cleanup
```bash
git add -A
git commit -m "Memory cleanup: kept last N sessions

Archived content searchable via:
git log --grep='Archive:' --oneline
git log -S 'keyword' -- memory/"
```

### 6. Report
- Sessions archived: N
- Features removed: M
- Active features remaining: X
- Next archive due: [date + 1 week]

## Finding Archived Content
```bash
git log --grep="Archive:" --oneline
git log -p -S "keyword" -- memory/
git show <commit>:memory/CONTEXT.md
```
