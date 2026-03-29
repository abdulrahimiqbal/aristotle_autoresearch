#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RO_BIN="${RO_BIN:-$ROOT_DIR/.venv_erdos/bin/research-orchestrator}"
DB_PATH="${DB_PATH:-$ROOT_DIR/outputs/erdos_mock/state.sqlite}"
WORKSPACE_PATH="${WORKSPACE_PATH:-$ROOT_DIR/outputs/erdos_mock/work}"
REPORT_PATH="${REPORT_PATH:-$ROOT_DIR/outputs/erdos_mock/report.md}"
CHARTER_PATH="$ROOT_DIR/examples/erdos_combinatorics_charter.json"
OUTPUT_DIR="$(dirname "$DB_PATH")"

rm -f "$DB_PATH" "$REPORT_PATH"
rm -rf "$WORKSPACE_PATH"
mkdir -p "$OUTPUT_DIR" "$WORKSPACE_PATH"

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

"$RO_BIN" run-cycle \
  --db "$DB_PATH" \
  --project "erdos-combo-001" \
  --provider mock \
  --workspace "$WORKSPACE_PATH" \
  --max-cycles 5

"$RO_BIN" report \
  --db "$DB_PATH" \
  --project "erdos-combo-001" \
  --output "$REPORT_PATH"

echo
echo "Mock report written to: $REPORT_PATH"
echo
cat "$REPORT_PATH"

# To switch to the live Aristotle CLI provider later, first export your API key
# and make sure the `aristotle` executable is on PATH, then replace the mock run
# with something like:
#
# export ARISTOTLE_API_KEY="your-api-key-here"
# "$RO_BIN" run-cycle \
#   --db "$DB_PATH" \
#   --project "erdos-combo-001" \
#   --provider aristotle-cli \
#   --workspace "$WORKSPACE_PATH" \
#   --max-cycles 5
