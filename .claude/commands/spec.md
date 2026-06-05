---
description: Start spec-driven development — write a structured specification before writing code
---

Invoke the agent-skills:spec-driven-development skill.

## Step 0: Check for existing audit findings

If `memory/AUDIT.md` exists and contains findings (from a prior `/review`, `/test`, or `/ship` run), read it first. Hardening specs should cite the audit findings that motivate them — each critical item in AUDIT.md should either appear in this spec's acceptance criteria or be explicitly deferred with a reason.

Skip Step 0 when building a greenfield feature where no audit exists.

## Step 1: Understand what the user wants

Ask clarifying questions about:
1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

## Step 2: Generate the spec

Generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.

If Step 0 found audit findings, add a **Motivating findings** section at the top of the spec that lists the AUDIT.md items this spec addresses, with file:line references.

N. **Decide repo topology.** Ask the user: standalone repo (default) or subtree? Record the decision in SPEC.md under `## Topology`. See skill guidance in spec-driven-development.

Save the spec as SPEC.md in the project root and confirm with the user before proceeding.
