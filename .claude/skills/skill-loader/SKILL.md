---
name: Skill Loader
description: Progressive skill discovery and loading. Use when you need to find relevant skills, check available capabilities, or load skill content on demand. Implements 3-tier loading to minimize token usage.
---

# Skill Loader — Progressive Discovery

Load skills efficiently using 3 tiers of progressive disclosure. Never dump all skill content into context at once.

## 3-Tier Loading Protocol

### Tier 0: Categories (cheapest)
List skill categories with counts. Use when orienting or when user asks "what can you do?"

```bash
# List all skill categories
for dir in .claude/skills/*/; do
  name=$(basename "$dir")
  files=$(find "$dir" -type f | wc -l)
  desc=$(head -5 "$dir/SKILL.md" 2>/dev/null | grep "^description:" | sed 's/description: //')
  echo "- $name ($files files): $desc"
done
```

### Tier 1: Metadata Only
Read only the YAML frontmatter (name + description). Use when deciding which skill to activate.

```bash
# Read skill metadata without loading full content
head -10 .claude/skills/SKILL_NAME/SKILL.md
```

Parse the `---` delimited frontmatter. Do NOT read past the closing `---`.

### Tier 2: Full Content
Load complete SKILL.md when skill is needed for the current task. Only load ONE skill at a time unless tasks genuinely require multiple.

```bash
# Load full skill content
cat .claude/skills/SKILL_NAME/SKILL.md
```

### Tier 3: References & Scripts
Load bundled resources only when the skill instructions reference them.

```bash
# List available resources
ls .claude/skills/SKILL_NAME/references/ .claude/skills/SKILL_NAME/scripts/ 2>/dev/null

# Load specific resource
cat .claude/skills/SKILL_NAME/references/FILENAME
```

## Decision Rules

| Situation | Tier |
|-----------|------|
| "What skills do I have?" | 0 |
| "Is there a skill for X?" | 1 (scan descriptions) |
| "Help me with X" (matches a skill) | 2 (load the matching skill) |
| Skill says "see REFERENCE.md" | 3 (load that reference) |

## Token Budget

- Tier 0: ~50 tokens per skill (name + count)
- Tier 1: ~100 tokens per skill (frontmatter)
- Tier 2: ~500-2000 tokens (full SKILL.md)
- Tier 3: Variable (only load what's referenced)

## Anti-Patterns

- Loading all skills at session start
- Reading full SKILL.md to check if it's relevant (use description field)
- Loading references "just in case"
- Loading multiple skills when only one is needed
