#!/bin/bash
set -euo pipefail

# Only run in remote Claude Code on the web environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Installing compintel dependencies..."
pip install -r "$CLAUDE_PROJECT_DIR/requirements.txt"

# Make scrapers and analysis importable from project root
echo "export PYTHONPATH=\"$CLAUDE_PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"

echo "compintel setup complete."
