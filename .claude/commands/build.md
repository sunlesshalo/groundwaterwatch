---
description: Implement the next task incrementally — build, test, verify, commit
---

Invoke the agent-skills:incremental-implementation skill alongside agent-skills:test-driven-development.

1. **Seed TodoWrite from `tasks/plan.md`.** Read the plan once. Convert each task into a TodoWrite entry with status `pending`. TodoWrite is the live task state for the rest of the session — do not re-read `tasks/plan.md` unless the plan itself changes. Mark items `in_progress` / `completed` as you work.

Pick the next pending task from the plan. For each task:

1. Read the task's acceptance criteria
2. Load relevant context (existing code, patterns, types)
3. Write a failing test for the expected behavior (RED)
4. Implement the minimum code to pass the test (GREEN)
5. Run the full test suite to check for regressions
6. Run the build to verify compilation
7. Commit with a descriptive message
8. Mark the task complete and move to the next one

If any step fails, follow the agent-skills:debugging-and-error-recovery skill.
