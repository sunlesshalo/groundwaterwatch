#!/bin/bash
# Wrapper for PreToolUse hook
# Reads JSON from stdin, extracts command, runs safety check

COMMAND=$(jq -r '.tool_input.command // empty')

if [ -n "$COMMAND" ]; then
  scripts/safety-check.sh "$COMMAND"
  exit $?
fi

exit 0
