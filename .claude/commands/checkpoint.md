Save progress with verification before marking features complete.

Based on Anthropic's research: agents must VERIFY work through testing before marking complete.

## Pre-Checkpoint Verification

Before saving, verify current work:

### Step 1: Test Current Feature
If you worked on a feature this session:
- Check the feature works as expected
- Look for obvious bugs or edge cases
- Confirm no regressions in related features

**CRITICAL:** Only mark a feature as `passing` if verification succeeds.
If tests fail or bugs exist, keep status as `in_progress` and note the issue.

### Step 2: Ensure Clean Handoff
Code must be in a clean state for next session:
- No commented-out debug code
- No incomplete implementations left mid-function
- Code could be merged to main branch right now

If code is messy, clean it up BEFORE checkpoint.

## Checkpoint Steps

### Step 3: Update memory/CONTEXT.md
Add session entry under "# Session Log":
```markdown
## YYYY-MM-DD
- Completed: [what was done]
- Verified: [how it was tested]
- Blockers: [any issues]
- Next: [suggested focus]
```

### Step 4: Update memory/STATE.json
- Update feature status (failing -> in_progress -> passing)
- Set `verified: true` only if testing confirmed it works
- Update `current_focus` to next priority
- **NEVER delete or modify feature descriptions**

### Step 5: Commit Changes
```bash
git status
```

If changes exist, commit with descriptive message:
```bash
git add -A
git commit -m "feat: [feature name] - verified working"
```

## Output Format

**Verification:** [passed/failed - what was tested]

**Features Updated:**
- [feature] -> [new status] (verified: yes/no)

**Session Notes Added:** [summary]

**Commit:** [commit message or "no changes"]

**Next Session Focus:** [recommendation]

---

Checkpoint complete. Safe to end session.
