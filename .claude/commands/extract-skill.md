Extract a reusable skill from work completed in this session.

After completing a complex task, use this command to capture the procedure as a reusable skill.

## Step 1: Identify the Procedure

Review what was done in this session. Look for:
- Multi-step workflows that could recur
- Domain-specific patterns that aren't obvious
- Debugging sequences that solved tricky problems
- Integration patterns with external services

Ask the user: "What should this skill be called? (e.g., `api-migration`, `docker-debug`)"

## Step 2: Gather Artifacts

Check for reusable artifacts created during the session:
```bash
git diff --name-only HEAD~1..HEAD 2>/dev/null || git diff --name-only --cached
```

Identify:
- **Scripts** that were written and could be reused
- **Config patterns** that required research to get right
- **Reference docs** that were consulted

## Step 3: Generate SKILL.md

Create the skill directory and SKILL.md:

```
.claude/skills/SKILL_NAME/
├── SKILL.md          # Instructions + frontmatter
├── scripts/          # Reusable scripts (if any)
└── references/       # Reference docs (if any)
```

The SKILL.md MUST include:
```yaml
---
name: skill-name
description: Clear trigger condition. When to use this skill.
trust: agent-created
created: YYYY-MM-DD
source_session: (brief description of originating task)
---
```

Body should contain:
1. **When This Skill Applies** — trigger conditions
2. **Procedure** — step-by-step instructions
3. **Common Pitfalls** — mistakes to avoid (from session errors)
4. **Verification** — how to confirm it worked

## Step 4: Security Scan

Before saving, check the skill content for:
- Hardcoded secrets, tokens, API keys
- Destructive commands without safeguards (rm -rf, DROP TABLE)
- External URLs that could be injection vectors
- Overly broad permissions (sudo, chmod 777)

If any found, warn the user and sanitize.

## Step 5: Save and Register

Write the skill files. Then confirm:

**Skill Created:** `SKILL_NAME`
**Location:** `.claude/skills/SKILL_NAME/`
**Files:** [list files created]
**Trust Level:** agent-created
**Trigger:** [description field]

The skill will auto-load in future sessions when Claude determines it's relevant.

## Trust Levels

| Level | Source | Auto-apply |
|-------|--------|-----------|
| `builtin` | Shipped with template | Yes |
| `trusted` | Installed from verified source | Yes |
| `community` | Installed from skills hub | Review first |
| `agent-created` | Extracted by this command | Yes (flagged in frontmatter) |
