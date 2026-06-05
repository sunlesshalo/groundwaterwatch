---
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
---

Invoke the agent-skills:planning-and-task-breakdown skill.

Read the existing spec (SPEC.md or equivalent) and the relevant codebase sections. If `memory/AUDIT.md` exists, also read it — critical audit findings should be ordered first in the plan, before any nice-to-have work. Then:

1. Enter plan mode — read only, no code changes
2. Identify the dependency graph between components
3. Slice work vertically (one complete path per task, not horizontal layers)
4. **Order by severity when audit findings drive the work:** Critical → Important → Suggestion. A plan that puts a Suggestion before a Critical is a failed plan.
5. Write tasks with acceptance criteria and verification steps
6. Add checkpoints between phases
7. Present the plan for human review

Save the plan to `tasks/plan.md`. The plan file is durable (committed to git); it's the shape-of-the-work artifact. **Do not write `tasks/todo.md`** — live task state is held by TodoWrite, seeded by `/build` from this plan. See CLAUDE.md Key Rule #12.
