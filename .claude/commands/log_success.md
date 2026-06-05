Log a success to capture reproducible patterns.

## Required Fields

1. **Task**: What was accomplished
2. **Approach**: Key prompt/context that worked
3. **Why It Worked**: What made this effective
4. **Reuse**: How to replicate this success

## Steps

1. Append to `memory/CONTEXT.md` under **Success Patterns** section:

```markdown
### [YYYY-MM-DD] Success: <task>
**Approach:** <what you did>
**Why It Worked:** <key factors>
**Reuse:** <template or pattern for future>
```

## Examples

```markdown
### 2026-01-17 Success: Complex refactor across 12 files
**Approach:** Used subagent per file with validation gate
**Why It Worked:** Parallelization + isolated context per task
**Reuse:** For multi-file changes, spawn one agent per file
```

## Philosophy

Successes are as learnable as failures. Capture what works.
