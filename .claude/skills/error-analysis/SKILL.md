---
name: Error Analysis
description: Structured failure analysis for learning from mistakes. Use when a command fails, code doesn't work as expected, or debugging takes multiple attempts. Focuses on root cause analysis and prevention strategies.
---

# Error Analysis Skill

Transforms failures into learnable patterns.

## When This Skill Applies

- A bash command fails
- Code doesn't compile or tests fail
- Debugging takes more than 2 attempts
- Same error occurs twice

## Analysis Framework

For every failure, identify:

1. **Trigger**: Exact prompt or action that caused the failure
2. **Category**:
   - `hallucination` - Made up API/function/syntax
   - `ignored_instruction` - Didn't follow explicit request
   - `wrong_approach` - Correct execution of wrong strategy
   - `context_loss` - Forgot earlier information
   - `environment` - System/config issue
3. **Root Cause**: Why it happened (focus on inputs, not the model)
4. **Prevention**: Specific change to prevent recurrence

## Logging Format

Append to `memory/CONTEXT.md` under Error Patterns:

```markdown
### [YYYY-MM-DD] Category: <category>
**Trigger:** "<exact prompt or action>"
**Failure:** <what went wrong>
**Root Cause:** <why — focus on your input/context>
**Prevention:** <concrete change>
```

## Philosophy

"Focus on variables, not constants" — the model performs consistently; user inputs determine outcomes. Every failure reveals a learnable pattern.

## Recurring Patterns

If a pattern appears 2+ times:
1. Add a rule to CLAUDE.md
2. Or create a hook to prevent it automatically
