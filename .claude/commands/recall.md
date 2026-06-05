Search memory for past context before debugging or deciding.

## When to Use
- Before debugging an error (was it solved before?)
- When something seems familiar
- When you need to remember why a decision was made
- Before making a decision that might conflict with a past one

## Steps

1. Search `memory/CONTEXT.md` for relevant keywords:
```bash
grep -i "keyword" memory/CONTEXT.md
```

2. Look for matching tags:
   - `[error]` - Past errors and solutions
   - `[discovery]` - Past learnings
   - `[decision]` - Past decisions and rationale

3. If found:
   - Apply the past solution
   - Reference it: "Previously solved on [date]: [solution]"

4. If not found:
   - Proceed with solving/investigating
   - Log the result afterward using `/log`

## Search Tips
- Search for error codes, API names, specific terms
- Check recent session entries first
- Use `git log -S "keyword" -- memory/` for archived content
