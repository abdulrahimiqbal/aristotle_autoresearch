# Aristotle Research Orchestrator

A research orchestration prototype for running **structured theorem-discovery workflows around Aristotle**.

It does **not** try to replace Aristotle. Instead, it adds the missing layers you asked for:

- persistent **project charter**
- explicit **research phases**
- controlled **experiment generation**
- cross-run **lemma memory**
- **assumption sensitivity** tracking
- research-grade **prompt contracts**
- a deterministic **mock provider** so you can test the full system locally
- a shell-based **Aristotle CLI adapter** you can swap in once you have API access

## What this repo gives you

- A working manager/worker architecture
- SQLite-backed research memory
- Prompt generation + prompt linting
- A sample project around a weighted monotone subsequence theorem family
- A demo command that runs a full mini research cycle
- Unit tests for the orchestration core

## What is mocked vs live

### Working now
The full orchestration loop works end-to-end with the `mock` provider:
- creates experiments
- generates prompts
- simulates Aristotle-style outcomes
- stores lemmas and experiment outcomes
- produces a research memo

### Live Aristotle integration
The `aristotle-cli` provider is a **real shell adapter boundary**:
- it calls the public Aristotle CLI with a project directory and objective prompt
- it captures stdout/stderr and stores artifacts
- it is intentionally conservative about parsing outputs

You will likely want to customize its result ingestion for your own Aristotle workflow.

## Quick start

### 1) Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install the package
```bash
pip install -e .
```

### 3) Run the full local demo
```bash
research-orchestrator demo --workspace ./demo_run
```

This will:
- create a SQLite database
- register the sample project
- import the sample conjecture
- run several research cycles with the mock provider
- write a markdown report into `./demo_run/report.md`

### 4) Inspect the report
Open:
```bash
./demo_run/report.md
```

## Single-prompt campaign workflow

The repo now supports a production-foundation workflow where you start from one natural-language prompt and let the manager build a verification-driven campaign around it.

### 1) Start a campaign from one prompt
```bash
research-orchestrator start-campaign \
  --db ./state.sqlite \
  --prompt "Study the hidden structure behind weighted monotone subsequence thresholds and discover which assumptions are truly necessary through formal verification."
```

This will:
- synthesize a campaign spec
- create an initial conjecture
- seed discovery questions
- persist campaign state for autonomous runs

### 2) Inspect campaign status
```bash
research-orchestrator campaign-status \
  --db ./state.sqlite \
  --project <project-id>
```

Machine-readable health is also available:
```bash
research-orchestrator campaign-health \
  --db ./state.sqlite \
  --project <project-id> \
  --format json
```

### 3) Run autonomous cycles
```bash
research-orchestrator run-cycle \
  --db ./state.sqlite \
  --project <project-id> \
  --provider mock \
  --workspace ./work \
  --max-cycles 4
```

### 4) Generate the discovery-centric report
```bash
research-orchestrator report \
  --db ./state.sqlite \
  --project <project-id> \
  --output ./report.md
```

The report now includes:
- the campaign contract
- discovery questions
- discovery graph nodes and edges
- incidents and audit trail
- experiment-level discovery context
- campaign health and version drift
- latest manager candidate audit summary

Replay historical experiment and manager decisions:
```bash
research-orchestrator replay-run \
  --db ./state.sqlite \
  --experiment-id <experiment-id> \
  --include-manifest

research-orchestrator audit-run \
  --db ./state.sqlite \
  --run-id <manager-run-id>
```

## Readable state bundles and motif-centric search

The manager is now more motif-centric than linear. Strong recurring lemmas, unresolved subgoals, proof-trace fragments, witnesses, and missing assumptions can all spawn multiple related candidates in the same tick. In particular:
- `promote_subgoal` promotes a recurring unresolved goal into its own target
- `promote_trace` isolates a recurring proof fragment or tactic bottleneck
- `boundary_map_from_witness` treats a falsifying witness as a local map of the false region
- `boundary_map_from_missing_assumption` turns a fragile falsification into a minimal assumption-repair experiment

The campaign also publishes a readable state bundle so humans do not need SQLite tooling just to inspect progress. The bundle is designed to be the primary inspection surface and can include:
- `report.md`
- `report.manager_snapshot.json`
- `campaign_summary.json`
- `conjecture_scoreboard.json`
- `recurring_structures.json`
- `active_queue.json`
- `experiments.csv`
- `incidents.json`
- `integrity.json`
- optional `state.snapshot.sqlite`

### Export and inspect readable state
```bash
research-orchestrator db-export \
  --db ./state.sqlite \
  --project <project-id> \
  --output-dir ./state_bundle
```

```bash
research-orchestrator publish-state-bundle \
  --db ./state.sqlite \
  --project <project-id> \
  --output-dir ./state_bundle \
  --report ./report.md \
  --manager-snapshot ./report.manager_snapshot.json \
  --include-sqlite
```

If the SQLite file is unavailable, `campaign-status` can read the exported bundle:
```bash
research-orchestrator campaign-status \
  --db ./missing-or-corrupt.sqlite \
  --project <project-id> \
  --state-dir ./state_bundle
```

### Integrity checks and backups
```bash
research-orchestrator db-check --db ./state.sqlite
research-orchestrator db-backup --db ./state.sqlite --output ./backups/state.sqlite
```

`sync-github-state` now prefers the readable bundle and only pulls a SQLite snapshot when explicitly asked:
```bash
research-orchestrator sync-github-state \
  --repo <repo> \
  --ref <branch> \
  --state-dir ./synced_state \
  --include-sqlite
```

## Core commands

### Initialize a project
```bash
research-orchestrator init-project   --db ./state.sqlite   --charter ./examples/project_charter.json   --conjecture ./examples/conjectures/weighted_monotone.json
```

### Run one automatic research cycle
```bash
research-orchestrator run-cycle   --db ./state.sqlite   --project mono-001   --provider mock   --workspace ./work
```

### Run multiple cycles
```bash
research-orchestrator run-cycle   --db ./state.sqlite   --project mono-001   --provider mock   --workspace ./work   --max-cycles 5
```

### Preview prompts for the next planned experiment
```bash
research-orchestrator preview-next   --db ./state.sqlite   --project mono-001
```

### Generate a research report
```bash
research-orchestrator report   --db ./state.sqlite   --project mono-001   --output ./report.md
```

### Lint prompt contracts
```bash
research-orchestrator lint-prompts   --db ./state.sqlite   --project mono-001
```

## Testing the full ability of the system

This repo is set up so you can test three things separately.

### A. Orchestration quality
Run:
```bash
research-orchestrator demo --workspace ./demo_run
```
Then inspect:
- `report.md`
- the SQLite database
- the generated workspace directories

You should see:
- recurring lemmas
- assumption sensitivity changes
- manager-selected next experiments
- clearly classified blockers

### B. Prompt discipline
Run:
```bash
research-orchestrator lint-prompts   --db ./demo_run/state.sqlite   --project mono-001
```

This verifies the generated manager and worker prompts contain hard constraints such as:
- do not conclude falsity from one failed proof attempt
- stay within the theorem family
- return structured outputs
- distinguish structural from search/formalization blockers

### C. Code-level tests
Run:
```bash
python -m unittest discover -s tests -v
```

This checks:
- prompt contracts
- lemma normalization
- manager behavior
- demo orchestration flow

## Using the live Aristotle CLI

The public `aristotlelib` package documents installation and commands such as:
- `uv pip install aristotlelib`
- `aristotle submit "Fill in all sorries" --project-dir ./my-lean-project --wait`
- `aristotle formalize paper.tex --wait --destination output.tar.gz` citeturn430475search0

### 1) Install the Aristotle CLI
```bash
uv pip install aristotlelib
```

### 2) Set your API key
```bash
export ARISTOTLE_API_KEY="your-api-key-here"
```

The PyPI package says the key can also be passed directly with `--api-key`, and that Python 3.10+ is required. citeturn430475search0

### 3) Run with the CLI provider
```bash
research-orchestrator run-cycle   --db ./state.sqlite   --project mono-001   --provider aristotle-cli   --workspace ./work
```

### Notes on live use
- The adapter currently shells out to `aristotle submit ... --project-dir ... --wait`.
- It stores stdout/stderr as artifacts and classifies the run conservatively.
- You should customize the parser if your Aristotle workflow returns structured result archives or generated Lean outputs.

## GitHub Actions deployment

The repo includes a scheduled/manual GitHub Actions workflow at `.github/workflows/erdos-manager.yml` for the Erdős campaign manager.

### Required repository secret
Set this secret in GitHub:
```bash
ARISTOTLE_API_KEY
```

### What the workflow does
- restores prior campaign state from the `campaign-state` branch
- creates a fresh virtualenv
- installs this repo and `aristotlelib`
- runs `./run_erdos_live_research.sh`, which executes one `manager-tick`
- commits the updated SQLite/report/snapshot artifacts back to `campaign-state`
- uploads the latest report, snapshot, and database as workflow artifacts

### Trigger modes
- scheduled every 5 minutes
- within each GitHub Actions run, the manager performs 4 one-minute-spaced `manager-tick` iterations and persists `campaign-state` after each tick
- manual `workflow_dispatch` with optional overrides for:
  - `max_active`
  - `max_submit_per_tick`
  - `llm_manager`

### Deployment model
This is the intended production shape for the stateless manager:
- a GitHub-hosted runner executes one tick
- SQLite/report state lives on the `campaign-state` branch
- no laptop or always-on local daemon is required

### Canonical live-state workflow
For live Aristotle campaigns, treat GitHub as the source of truth:
- GitHub Actions owns submission and polling
- the `campaign-state` branch is the canonical live state
- local inspection should begin by syncing those artifacts down before reading reports or the DB

### Monitoring the live campaign
Sync the canonical state locally with:
```bash
research-orchestrator sync-github-state \
  --repo <your-github-username>/aristotle_autoresearch \
  --ref campaign-state \
  --state-dir outputs/erdos_live_async
```

That downloads only the canonical live-state artifacts:
- `outputs/erdos_live_async/state.sqlite`
- `outputs/erdos_live_async/report.md`
- `outputs/erdos_live_async/report.manager_snapshot.json`

Recommended practice:
- do not run local `manager-tick` against a live campaign unless you intentionally want a separate campaign
- run `sync-github-state` before inspecting live status locally
- use the local DB for mock runs or for read-only inspection of the GitHub-managed live campaign

Read the latest report:
```bash
cat outputs/erdos_live_async/report.md
```

Inspect the latest experiment activity:
```bash
sqlite3 outputs/erdos_live_async/state.sqlite "SELECT experiment_id, conjecture_id, move, status, proof_outcome, new_signal_count FROM experiments ORDER BY created_at DESC LIMIT 20"
```

Check discovery graph growth:
```bash
sqlite3 outputs/erdos_live_async/state.sqlite "SELECT node_type, COUNT(*) FROM discovery_graph_nodes GROUP BY node_type"
```

Check for incidents:
```bash
sqlite3 outputs/erdos_live_async/state.sqlite "SELECT * FROM incidents WHERE status='open'"
```

## Suggested development path

### Week 1
- Run the demo
- Read the database tables
- Adjust the project charter and sample conjecture metadata

### Week 2
- Add a second theorem family
- Improve lemma normalization
- Add a second provider or more experiment moves

### Week 3
- Customize the Aristotle CLI parser
- Connect actual Lean project outputs
- Add counterexample mode

### Week 4
- Build an eval set of theorem families
- Track prompt versions and compare decision quality

## File overview

- `src/research_orchestrator/charter.py` — project charter loading and validation
- `src/research_orchestrator/db.py` — SQLite schema and persistence
- `src/research_orchestrator/manager.py` — research manager policy
- `src/research_orchestrator/experiment_generator.py` — allowed research moves
- `src/research_orchestrator/prompts.py` — project/manager/worker prompt construction
- `src/research_orchestrator/prompt_linter.py` — prompt contract checks
- `src/research_orchestrator/providers/mock.py` — deterministic local provider
- `src/research_orchestrator/providers/aristotle_cli.py` — shell adapter to the Aristotle CLI
- `src/research_orchestrator/reporter.py` — markdown research memos

## Research-grade prompt design principles in this repo

Prompts are not treated as magic. The system uses:
- project charters as a constitution
- explicit allowed moves
- structured run briefs
- output schemas
- prompt linting
- deterministic tests

That is how you keep “research quality” behavior from drifting.

## Limitations

- The mock provider is only a simulation of proof-search outcomes.
- The live Aristotle adapter is real but conservative; it is not a complete parser for every possible Aristotle output layout.
- Lean statement transformation in this prototype is intentionally lightweight and metadata-driven rather than a full theorem parser.

## Recommended next upgrades

- Add canonicalization with a Lean-aware normalizer
- Add a richer evaluator using proof cost and recurrence gain
- Add a proper result ingester for `aristotle result`
- Add a dashboard over the SQLite database
