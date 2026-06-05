#!/bin/bash
# Safety hook - blocks dangerous commands
# Used with dangerously-skip-permissions for autonomous but safe operation

COMMAND="$1"

# High-severity: File system destruction
if echo "$COMMAND" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+.*(/|~|\*|\.git)|.*\s+/)'; then
  echo "BLOCKED: Destructive rm command" >&2
  exit 2
fi

# High-severity: Git history destruction
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*--force|git\s+push\s+-f'; then
  echo "BLOCKED: Force push (use --force-with-lease if needed)" >&2
  exit 2
fi

if echo "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: git reset --hard (loses uncommitted work)" >&2
  exit 2
fi

# High-severity: Privilege escalation
if echo "$COMMAND" | grep -qE '^sudo\s+'; then
  echo "BLOCKED: sudo commands require manual approval" >&2
  exit 2
fi

# High-severity: Remote code execution
if echo "$COMMAND" | grep -qE 'curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh'; then
  echo "BLOCKED: Piping remote content to shell" >&2
  exit 2
fi

# Medium-severity: Database destruction
if echo "$COMMAND" | grep -qiE 'DROP\s+(DATABASE|TABLE)|TRUNCATE\s+|DELETE\s+FROM\s+\S+\s*;?\s*$'; then
  echo "BLOCKED: Destructive database command" >&2
  exit 2
fi

# Medium-severity: System paths
if echo "$COMMAND" | grep -qE '>\s*/etc/|>\s*/usr/'; then
  echo "BLOCKED: Writing to system paths" >&2
  exit 2
fi

# Medium-severity: Secrets in git
if echo "$COMMAND" | grep -qE 'git\s+add\s+.*\.env'; then
  echo "BLOCKED: Adding .env to git" >&2
  exit 2
fi

exit 0
