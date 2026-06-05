Log a failure for pattern learning. Be critical — focus on what YOU did wrong.

## Required Fields

1. **Trigger**: Exact user prompt that caused the failure (verbatim, in quotes)
2. **Category**: hallucination | ignored_instruction | wrong_approach | context_loss | ambiguous_verb | scope_creep | other
3. **What Happened**: The actual failure behavior
4. **Root Cause**: Why it happened (be honest — focus on input/context, not the model)
5. **Prevention**: Specific change to prevent recurrence

## Steps

### 1. Append to structured log (`memory/errors.json`)

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "trigger": "exact user prompt verbatim",
  "category": "category_name",
  "failure": "what went wrong",
  "root_cause": "why — focus on your input",
  "prevention": "concrete change",
  "session_context": "brief note on what was happening"
}
```

Create file if missing. Append to existing array.

### 2. Append human-readable entry to `memory/CONTEXT.md`

Under **## Error Patterns** section (create if missing):

```markdown
### [YYYY-MM-DD] Category: <category>
**Trigger:** "<exact prompt>"
**Failure:** <what went wrong>
**Root Cause:** <why>
**Prevention:** <concrete change>
```

### 3. Pattern check

After logging, scan `memory/errors.json` for:
- Same category appearing 3+ times → suggest CLAUDE.md rule
- Same trigger phrase causing issues → flag ambiguous language

## Categories Explained

| Category | When to use |
|----------|-------------|
| `hallucination` | Made up file/function/fact that doesn't exist |
| `ignored_instruction` | User gave clear instruction, I didn't follow |
| `wrong_approach` | Chose poor strategy for the task |
| `context_loss` | Forgot earlier context, repeated work |
| `ambiguous_verb` | Misinterpreted "deploy", "update", "fix", etc. |
| `scope_creep` | Did more than asked, over-engineered |
| `other` | Doesn't fit above |

## Philosophy

"Focus on variables, not constants" — the model is consistent; your inputs determine outcomes. Every failure is learnable. Patterns emerge from structured logs.
