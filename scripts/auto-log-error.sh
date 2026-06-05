#!/bin/bash
# Auto-log failed commands to CONTEXT.md
# Called by PostToolUse hook when bash commands fail

# Read tool result from stdin
RESULT=$(cat)

# Extract command and exit code
COMMAND=$(echo "$RESULT" | jq -r '.tool_input.command // "unknown"' 2>/dev/null)
EXIT_CODE=$(echo "$RESULT" | jq -r '.tool_result.exit_code // 0' 2>/dev/null)

# Only log if command failed (non-zero exit)
if [ "$EXIT_CODE" != "0" ] && [ "$EXIT_CODE" != "null" ]; then
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

  # Truncate command if too long
  if [ ${#COMMAND} -gt 100 ]; then
    COMMAND="${COMMAND:0:100}..."
  fi

  # Append to CONTEXT.md
  echo "- [$TIMESTAMP] [auto-error] Command failed (exit $EXIT_CODE): \`$COMMAND\`" >> memory/CONTEXT.md
fi

exit 0
