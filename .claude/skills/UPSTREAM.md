# Vendored: addyosmani/agent-skills

**Source:** https://github.com/addyosmani/agent-skills
**Commit SHA:** b3e905987490e948667f04d95ab3169236b9c212
**Vendored on:** 2026-04-10
**License:** MIT

## What was vendored

| Path | From upstream |
|------|---------------|
| `.claude/skills/*` (21 skills listed below) | `skills/` |
| `.claude/commands/{spec,plan,build,test,review,ship,code-simplify}.md` | `.claude/commands/` |
| `.claude/agents/{code-reviewer,test-engineer,security-auditor}.md` | `agents/` |
| `references/{testing,security,performance,accessibility}-*.md` | `references/` |

### Vendored skills (21)

1. api-and-interface-design
2. browser-testing-with-devtools
3. ci-cd-and-automation
4. code-review-and-quality
5. code-simplification
6. context-engineering
7. debugging-and-error-recovery
8. deprecation-and-migration
9. documentation-and-adrs
10. frontend-ui-engineering
11. git-workflow-and-versioning
12. idea-refine
13. incremental-implementation
14. performance-optimization
15. planning-and-task-breakdown
16. security-and-hardening
17. shipping-and-launch
18. source-driven-development
19. spec-driven-development
20. test-driven-development
21. using-agent-skills (meta-skill)

### Base-agent skills (kept alongside, 7)

audit-logging, error-analysis, google-workspace-guide, risk-assessment, session-protocol, skill-loader, subagent-orchestration

## What was NOT vendored

- `hooks/` — upstream session-start hook conflicts with agent_factory's `/start` command. The hooks already wired in `.claude/settings.json` (pre-tool-check, risk-gate, shadow-checkpoint, auto-log-error, audit-log, focus banner) stay authoritative.
- `.claude-plugin/` — marketplace metadata, irrelevant for vendored use.
- Upstream `CLAUDE.md`, `README.md`, `AGENTS.md`, `docs/` — replaced by dev-agent's own docs.

## Re-syncing

```bash
# From repo root
git clone --depth 1 https://github.com/addyosmani/agent-skills.git /tmp/agent-skills-sync
cd /tmp/agent-skills-sync && git rev-parse HEAD  # note new SHA

# Diff vendored skills against upstream
diff -rq library/templates/dev-agent/.claude/skills/ /tmp/agent-skills-sync/skills/ | grep -v 'Only in.*skills/: '
```

Update this file with the new SHA and date after any sync.

## Per-project pruning

The dev-agent template ships *all* skills. When instantiating for a specific project, delete skill directories the project doesn't need — each skill is self-contained under `.claude/skills/<name>/`. Update `.claude/commands/` similarly if lifecycle commands become irrelevant.
