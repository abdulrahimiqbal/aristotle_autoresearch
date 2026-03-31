#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RO_BIN="${RO_BIN:-$ROOT_DIR/.venv_erdos/bin/research-orchestrator}"
DB_PATH="${DB_PATH:-$ROOT_DIR/outputs/erdos_live_async/state.sqlite}"
WORKSPACE_PATH="${WORKSPACE_PATH:-$ROOT_DIR/outputs/erdos_live_async/work}"
REPORT_PATH="${REPORT_PATH:-$ROOT_DIR/outputs/erdos_live_async/report.md}"
CHARTER_PATH="$ROOT_DIR/examples/erdos_combinatorics_charter.json"
MAX_ACTIVE="${MAX_ACTIVE:-5}"
MAX_SUBMIT_PER_TICK="${MAX_SUBMIT_PER_TICK:-5}"
BACKFILL_LIMIT="${BACKFILL_LIMIT:-6}"
LLM_MANAGER="${LLM_MANAGER:-auto}"

if [[ -n "${ARISTOTLE_BIN_DIR:-}" ]]; then
  RESOLVED_ARISTOTLE_BIN_DIR="$ARISTOTLE_BIN_DIR"
elif [[ -x "$ROOT_DIR/.venv_erdos/bin/aristotle" ]]; then
  RESOLVED_ARISTOTLE_BIN_DIR="$ROOT_DIR/.venv_erdos/bin"
elif [[ -x "$ROOT_DIR/.venv/bin/aristotle" ]]; then
  RESOLVED_ARISTOTLE_BIN_DIR="$ROOT_DIR/.venv/bin"
else
  RESOLVED_ARISTOTLE_BIN_DIR="$ROOT_DIR/.venv_erdos/bin"
fi

if [[ -z "${ARISTOTLE_API_KEY:-}" ]]; then
  echo "ARISTOTLE_API_KEY is not set." >&2
  exit 1
fi

export PATH="$RESOLVED_ARISTOTLE_BIN_DIR:$PATH"

mkdir -p "$(dirname "$DB_PATH")" "$WORKSPACE_PATH"

"$RO_BIN" init-project \
  --db "$DB_PATH" \
  --charter "$CHARTER_PATH" \
  --conjecture "$ROOT_DIR/examples/conjectures/erdos/erdos_181_hypercube_ramsey.json"

"$RO_BIN" init-project \
  --db "$DB_PATH" \
  --charter "$CHARTER_PATH" \
  --conjecture "$ROOT_DIR/examples/conjectures/erdos/erdos_44_sidon_extension.json"

"$RO_BIN" init-project \
  --db "$DB_PATH" \
  --charter "$CHARTER_PATH" \
  --conjecture "$ROOT_DIR/examples/conjectures/erdos/erdos_123_d_complete_sequences.json"

"$RO_BIN" backfill-results \
  --db "$DB_PATH" \
  --project "erdos-combo-001" \
  --provider aristotle-cli \
  --limit "$BACKFILL_LIMIT"

"$RO_BIN" manager-tick \
  --db "$DB_PATH" \
  --project "erdos-combo-001" \
  --provider aristotle-cli \
  --workspace "$WORKSPACE_PATH" \
  --max-active "$MAX_ACTIVE" \
  --max-submit-per-tick "$MAX_SUBMIT_PER_TICK" \
  --report-output "$REPORT_PATH" \
  --llm-manager "$LLM_MANAGER"

# Ensure live projections are fresh before state is committed
"$RO_BIN" db-refresh-projections \
  --db "$DB_PATH" \
  --project "erdos-combo-001"

echo
echo "Manager-tick report written to: $REPORT_PATH"
echo
sed -n '1,240p' "$REPORT_PATH"
