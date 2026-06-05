Session startup with token-saving ritual.

Based on Anthropic's research: execute steps sequentially to minimize redundant discovery work.

## Token-Saving Startup Ritual

Execute these steps IN ORDER (do not parallelize):

### Step 1: Confirm Environment
```bash
pwd
```
Verify you're in the correct project directory.

### Step 2: Check for Uncommitted Work
```bash
git status --short
```
If uncommitted changes exist, note them - previous session may have been interrupted.

### Step 3: Read Progress State
```bash
cat memory/STATE.json
```
Identify: current_focus and highest-priority failing feature.

### Step 4: Read Recent Git History
```bash
git log --oneline -5
```
Understand what was committed recently (context without reading full files).

### Step 5: Quick Context Scan
```bash
tail -30 memory/CONTEXT.md
```
Read only RECENT context (not entire history - saves tokens).

### Step 6: Run Environment Init (if exists)
```bash
[ -f init.sh ] && ./init.sh
```
Start dev server or other environment setup.

## Output Format

After completing the ritual, summarize:

**Environment:** [project directory confirmed]

**Uncommitted Work:** [none / list files]

**Current Focus:** [from STATE.json]

**Next Feature:** [highest priority failing feature]

**Recent Commits:** [1-line summary of last 3]

**Ready to Work:** [yes/no - if no, explain blockers]

---

Then ask: "Ready to continue with [next feature]?"

Do NOT start implementation until user confirms.
