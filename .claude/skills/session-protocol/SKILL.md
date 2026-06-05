---
name: Session Protocol
description: Manages session lifecycle for long-running agent work. Use when starting a new session, ending a session, or when context about the current project state is needed. Handles STATE.json feature tracking, CONTEXT.md logging, frozen memory injection, and clean handoffs between sessions.
---

# Session Protocol Skill

This skill enforces the session protocol for long-running agent work based on Anthropic's research.

## When This Skill Applies

- Starting a new coding session
- Ending a session or checkpointing progress
- Tracking feature status (failing → in_progress → passing)
- Logging discoveries, errors, or decisions
- Searching past context to avoid repeating mistakes

## Core Files

| File | Purpose | Read | Write |
|------|---------|------|-------|
| `memory/STATE.json` | Feature tracking (status, verified) | Once at /start | Anytime (takes effect next session) |
| `memory/CONTEXT.md` | Session log and notes | Last 30 lines at /start | Append anytime |
| `init.sh` | Environment startup script | At /start | Rarely |

## Frozen Memory Pattern

Memory is read **once at session start** and treated as a frozen snapshot for the rest of the session. This is intentional — it preserves the prefix cache and prevents stale re-reads from wasting tokens.

**Rules:**
1. **Read once** — STATE.json and CONTEXT.md are read during `/start`. Do not re-read them mid-session unless the user explicitly asks.
2. **Write immediately** — When updating STATE.json or appending to CONTEXT.md, write to disk immediately. The writes take effect for the current session's working state, but the "frozen snapshot" in the system prompt is not updated.
3. **No mid-session refresh** — If you need to check current state mid-session, rely on your in-context knowledge from the `/start` read plus any writes you've made. Do not re-read the files from disk.

**Why this matters:**
- Re-reading large state files mid-session wastes tokens on information you already have
- The frozen snapshot ensures consistent state throughout the session
- Writes are durable (survive crashes) without needing mid-session reads

## Session Start Protocol

1. Confirm environment (pwd)
2. Check uncommitted work (git status)
3. **FREEZE:** Read STATE.json for current focus and failing features
4. Read recent git history (last 5 commits)
5. **FREEZE:** Scan last 30 lines of CONTEXT.md
6. Run init.sh if it exists

Steps 3 and 5 create the frozen snapshot. All subsequent work references this snapshot.

## Feature Lifecycle

```
failing → in_progress → (verify) → passing
```

**Rules:**
- All features start as `failing`
- Only modify `status` and `verified` fields
- Never delete or edit feature descriptions
- Set `verified: true` only after testing confirms it works

## Session End Protocol

Before ending any session:
1. **Verify** - Run tests or manually verify features work
2. **Clean handoff** - Remove debug code, ensure code is merge-ready
3. **Update state** - Set passing features, update current_focus
4. **Shadow checkpoint** - Run `scripts/shadow-checkpoint.sh save "session-end"` before committing
5. **Commit** - Descriptive commit message

## Logging

Append to CONTEXT.md with tags:
- `[error]` Problem → solution
- `[discovery]` What was learned
- `[decision]` What was decided and why

## Anti-Circle Rule

Before debugging any issue, search CONTEXT.md for existing solutions.
If already solved → use existing solution.
If new → solve it, then log the solution.
