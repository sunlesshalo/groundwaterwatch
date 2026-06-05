---
name: Subagent Orchestration
description: Guides spawning and managing subagents for complex tasks. Use when considering whether to spawn subagents, when working on multi-file changes, or when parallelizing independent tasks. Ensures proper validation gates and prevents hallucination chains.
---

# Subagent Orchestration Skill

Optimize subagent usage for complex, multi-step tasks.

## When This Skill Applies

- Considering whether to spawn a subagent
- Multi-file refactors or implementations
- Parallelizable independent tasks
- Research followed by implementation
- Long-running background tasks

## Default Behavior

- **Model:** Use Opus for subagents unless task is trivial (then Haiku)
- **Parallelization:** Spawn multiple agents for independent tasks in a single message
- **Scope:** One focused task per agent (not multiple tasks)

## Core Principle

**More agents with less scope > fewer agents with more scope**

## Patterns

### Multi-File Refactor
```
One agent per file → validate each → merge results
```

### Research → Implement Pipeline
```
Research agent (explore) → Implementation agent (with findings)
```

### Parallel Independent Tasks
```
Single message with multiple Task tool calls → all run concurrently
```

## Validation Gates

**Critical:** After any subagent completes, verify output before using:

1. Does the code compile/lint?
2. Does it match the requested change?
3. Any hallucinated imports or APIs?
4. Any invented function names or parameters?

This prevents **hallucination chains** where one bad output feeds the next.

## When to Use Subagents

| Scenario | Approach |
|----------|----------|
| Search across codebase | Single explore agent |
| Implement feature in multiple files | One agent per file |
| Research + implement | Research agent first, then implement agent |
| Long-running task | Background agent with periodic checks |
| Independent parallel tasks | Multiple agents in single message |

## When NOT to Use Subagents

- Single file edits (do it directly)
- Quick lookups (use Grep/Glob directly)
- Tasks requiring conversation context (context doesn't transfer)
- Simple sequential operations

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Mega-agent | One agent doing 10 things | Use 10 focused agents |
| Context overload | Passing entire codebase | Pass only relevant files |
| Blind trust | Using output without validation | Always verify first |
| Serial when parallel | Running independent tasks sequentially | Parallelize in single message |

## Subagent Types Reference

| Type | Use For |
|------|---------|
| `Explore` | Codebase search, finding files, understanding structure |
| `Bash` | Git operations, command execution |
| `Plan` | Architecture decisions, implementation planning |
| `general-purpose` | Complex multi-step research tasks |
