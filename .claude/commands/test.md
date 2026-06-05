---
description: Run TDD workflow, verify a bug fix with Prove-It, or audit the test posture of an existing codebase.
---

Invoke the agent-skills:test-driven-development skill.

Three modes — pick the one that matches the task:

## Mode 1: New feature (TDD)
1. Write tests that describe the expected behavior (they should FAIL)
2. Implement the code to make them pass
3. Refactor while keeping tests green

## Mode 2: Bug fix (Prove-It pattern)
1. Write a test that reproduces the bug (must FAIL)
2. Confirm the test fails
3. Implement the fix
4. Confirm the test passes
5. Run the full test suite for regressions

## Mode 3: Audit existing codebase
Use when instantiating on a legacy project with unknown test posture. Goal is to assess, not to author.

1. **Inventory the test runner** — check for `package.json` scripts, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, CI config. If none, there is no test infrastructure.
2. **Count existing tests** — grep for `*.test.*`, `*.spec.*`, `*_test.go`, `test_*.py`. Report count by directory.
3. **Run the suite** — execute the test command and capture pass/fail/skip counts. If tests don't run, that's finding #1.
4. **Coverage signal** — if a coverage tool exists, run it. Otherwise identify untested modules by inspection.
5. **Round-trip / schema tests** — for projects with serialization (DB, API, file formats), check whether round-trip tests exist. Their absence is a silent-data-loss risk vector (e.g. a reader range that doesn't match a writer schema).
6. **Recommend a minimal pyramid** — not a full test suite; the smallest set that would catch the most likely regressions. Usually 3-6 unit tests + 1 end-to-end smoke.
7. **Append findings to memory/AUDIT.md** under a `## Test Audit` section.

Audit mode never writes new tests unless the user explicitly asks. It reports.

---

For browser-related issues in any mode, also invoke agent-skills:browser-testing-with-devtools to verify with Chrome DevTools MCP.

---

## UI-feature verification gate

Before flipping any feature to `verified: true` in STATE.json, check whether it's a UI feature. A feature is UI if its `feature` field contains any of: **popup**, **extension**, **page**, **button**, **dropdown**, **form**, **dashboard**, **modal**, **toast**, **HUD**, **overlay**, **UI**, **frontend**, **browser tab**.

If it matches, endpoint / unit tests are **not sufficient evidence**. One of these must be true before `verified: true`:

1. **User has confirmed in chat** that they clicked it and it worked
2. **Browser-automation screenshot** exists in the repo and is referenced from CONTEXT.md
3. **Explicit skip** recorded in CONTEXT.md with a justification (e.g. "UI verified in previous session", "feature is behind flag X")

If none of those are true, **do not silently set `verified: true`**. Instead, ask the user:

> "Server-side tests pass for [feature]. This is a UI feature — can you click through it and confirm it works as expected? Then I'll mark it verified."

Wait for the user's reply before updating STATE.json. The user may override ("mark it, I'll verify later") — that's fine, but the default path must go through human eyes.

See agent-skills:test-driven-development → "UI-Layer Features — Human Verification Gate" for the full rule and rationale.
