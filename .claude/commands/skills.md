List available skills using progressive disclosure (Tier 0 → Tier 1).

## Step 1: Scan All Skills (Tier 0)

```bash
echo "=== Available Skills ==="
for dir in .claude/skills/*/; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  desc=$(sed -n '/^---$/,/^---$/p' "$dir/SKILL.md" 2>/dev/null | grep "^description:" | sed 's/description: //')
  files=$(find "$dir" -type f | wc -l | tr -d ' ')
  echo "- **$name** ($files files): $desc"
done
```

## Step 2: Present Summary

Show the skills list to the user. For each skill, show:
- Name
- Description (from frontmatter)
- File count

## Step 3: Offer Drill-Down

Ask: "Want details on any skill? I'll load its full content (Tier 2)."

If user picks a skill, read its full SKILL.md. If they ask about references/scripts, load those too (Tier 3).

Do NOT load any full skill content unless the user requests it.
