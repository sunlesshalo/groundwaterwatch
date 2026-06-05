#!/bin/bash
# init.sh - Quick environment startup script
# Based on Anthropic's long-running agent research
set -e

echo "🚀 Initializing environment..."

# --- Python bootstrap (canonical agent_factory block) -----------------------
# Handles: python3 alias, macOS externally-managed-environment, .venv autocreate.
# Idempotent and safe on non-Python projects (short-circuits if no markers).
# Do not edit inline — update library/templates/*/init.sh and re-sync.

_af_bootstrap_python() {
  local has_python_marker=0
  [ -f requirements.txt ] && has_python_marker=1
  [ -f pyproject.toml ] && has_python_marker=1
  [ -f setup.py ] && has_python_marker=1
  [ "$has_python_marker" = "0" ] && return 0

  # Pick interpreter — prefer python3 (macOS only ships python3)
  local PY=""
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    echo "⚠️  Python project detected but no python3 on PATH — skipping bootstrap" >&2
    return 0
  fi

  # Create .venv if missing
  if [ ! -d .venv ]; then
    echo "📦 Creating .venv (first run)…"
    "$PY" -m venv .venv || {
      echo "⚠️  venv creation failed — check that python3-venv is installed" >&2
      return 0
    }
  fi

  # Activate
  # shellcheck disable=SC1091
  . .venv/bin/activate

  # Install deps on first activation only (marker file in .venv)
  if [ ! -f .venv/.deps-installed ]; then
    if [ -f pyproject.toml ]; then
      echo "📦 Installing project (pip install -e .[dev])…"
      pip install -q -e ".[dev]" 2>/dev/null || pip install -q -e . || true
    elif [ -f requirements.txt ]; then
      echo "📦 Installing requirements.txt…"
      pip install -q -r requirements.txt || true
    fi
    touch .venv/.deps-installed
  fi

  echo "🐍 Python: $(python --version 2>&1) — venv active"
}

_af_bootstrap_python
# --- end Python bootstrap ---------------------------------------------------

# --- CUSTOMIZE BELOW ---
# Node: npm install --silent && npm run dev &
# Docker: docker-compose up -d
# --- END CUSTOMIZE ---

echo "✅ Environment ready"
