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

## LLM Synthesis & Gatekeeper (Deep Reasoning)

The system can leverage Kimi K2.5 as both a **gatekeeper** and a **creative research partner**. When enabled, **no experiment is submitted to Aristotle unless the LLM has deeply reasoned through it first**.

### Two Modes of LLM Assistance

| Mode | Badge | Purpose |
|------|-------|---------|
| **Gatekeeper Review** | 🧠 LLM Deeply Reasoned | Every candidate is reviewed before submission |
| **Synthesis** | ✨ LLM Synthesized | New conjectures created from verified patterns |

### The Gatekeeper Mechanism

When `RESEARCH_ORCHESTRATOR_LLM_SYNTHESIS=true`:

1. **Generate Frontier** → Heuristic candidates created by the system
2. **LLM Review** → Top 15 candidates presented to LLM with full context:
   - Verified discoveries (100% mathematically true)
   - Charter objectives
   - Expected signals and risks
3. **Deep Reasoning** → LLM provides for each candidate:
   - `epistemic_score`: 0.0-1.0 (confidence in value)
   - `strategic_priority`: high/medium/low
   - `llm_reasoning`: Detailed strategic assessment
   - `risk_assessment`: What could go wrong
   - `connection_to_verified`: How it builds on known truths
4. **Gatekeeper Decision** → `llm_reasoned: true/false`
5. **Only Approved Submitted** → Rejected candidates are **dropped**, never sent to Aristotle

### The Synthesis Mechanism

The LLM also acts as a creative partner:

1. **Gather Verified Discoveries** → Recurring lemmas, subgoals, proof traces, no-signal patterns
2. **Synthesize Patterns** → LLM identifies gaps and connections
3. **Propose New Conjectures** → 2-3 novel experiment directions with:
   - `synthesis_observation`: Pattern noticed across verified results
   - `novelty`: What's new vs existing approaches
   - `expected_verification`: Clear criteria for confirmation
4. **Pre-approved** → Synthesized candidates automatically pass gatekeeper review

### Enable LLM Synthesis

```bash
# Option 1: Environment variable
export RESEARCH_ORCHESTRATOR_LLM_SYNTHESIS=true

# Option 2: Copy the example env file and edit
cp .env.example .env
# Edit .env and set RESEARCH_ORCHESTRATOR_LLM_SYNTHESIS=true
```

### Dashboard Indicators

When LLM synthesis is enabled, the dashboard shows:

- **Green Badge (🧠 LLM Deeply Reasoned)**: Candidate passed gatekeeper review
  - Epistemic score (0.0-1.0)
  - Strategic reasoning text
  - Priority level (high/medium/low)

- **Purple Badge (✨ LLM Synthesized)**: Candidate created by LLM synthesis
  - Synthesis observation
  - Novelty claim

### The Epistemic Separation

| Component | Role | Confidence |
|-----------|------|------------|
| **Aristotle** | Mathematical verification | 100% (ground truth) |
| **LLM Gatekeeper** | Strategic reasoning, risk assessment | Heuristic (filters candidates) |
| **LLM Synthesis** | Creative hypothesis generation | Heuristic (proposes new directions) |

This maintains the ethos: mathematical truth comes from Aristotle verification, but LLM-driven reasoning ensures only high-quality candidates are submitted, and LLM creativity accelerates discovery by proposing novel directions grounded in verified patterns.

### Events Emitted

When gatekeeper is active:
- `llm.gatekeeper.reviewed` — Stats on reviewed candidates, epistemic scores, approval counts
- `llm.synthesis.generated` — New conjectures proposed by LLM synthesis

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

## Starting a New Experiment

There are three ways to start experiments, depending on your workflow needs:

### Method A: Single-Prompt Campaign (Recommended for New Research)

Best when you have a research idea but no formal conjecture yet. The system will:
- Generate a campaign spec from your prompt
- Create an initial conjecture
- Seed discovery questions
- Start autonomous experimentation

```bash
# Step 1: Start from a natural language prompt
research-orchestrator start-campaign \
  --db ./state.sqlite \
  --prompt "Study the hidden structure behind weighted monotone subsequence thresholds and discover which assumptions are truly necessary through formal verification."

# This outputs a project ID (e.g., campaign-map-hidden-lemmas-xxx)

# Step 2: Run autonomous cycles
research-orchestrator run-cycle \
  --db ./state.sqlite \
  --project <project-id> \
  --provider mock \
  --workspace ./work \
  --max-cycles 4

# Step 3: View the dashboard
research-orchestrator dashboard \
  --db ./state.sqlite \
  --project <project-id> \
  --port 8000
```

### Method B: Manual Project Initialization (For Structured Conjectures)

Best when you have a formal conjecture defined in a JSON file.

```bash
# Step 1: Create project charter and conjecture JSON files
# See examples/ for templates

# Step 2: Initialize the project
research-orchestrator init-project \
  --db ./state.sqlite \
  --charter ./examples/project_charter.json \
  --conjecture ./examples/conjectures/weighted_monotone.json

# Step 3: Run cycles
research-orchestrator run-cycle \
  --db ./state.sqlite \
  --project mono-001 \
  --provider mock \
  --workspace ./work \
  --max-cycles 5
```

### Method C: Direct Experiment Submission (For Specific Moves)

Best when you want to test a specific move on a specific conjecture.

```bash
# After initializing a project, use the manager-tick for direct control
research-orchestrator manager-tick \
  --db ./state.sqlite \
  --project <project-id> \
  --provider mock \
  --workspace ./work \
  --max-active 3 \
  --max-submit 2
```

### Workflow Comparison

| Workflow | Best For | Setup | Flexibility |
|----------|----------|-------|-------------|
| **Single-Prompt** | New research, exploration | One command | High - system generates everything |
| **Manual Init** | Known conjectures, structured campaigns | JSON files | Medium - you define structure |
| **Direct Tick** | Testing, debugging, specific moves | Existing project | Low - precise control |

### With LLM Synthesis Enabled

When `RESEARCH_ORCHESTRATOR_LLM_SYNTHESIS=true`, the workflow is the same, but:

1. **Candidates are reviewed by LLM before submission**
   - Each candidate gets an epistemic score
   - Only approved candidates go to Aristotle
   - Dashboard shows 🧠 LLM Deeply Reasoned badge

2. **LLM may propose new conjectures**
   - Synthesized from verified discoveries
   - Dashboard shows ✨ LLM Synthesized badge

3. **Manager events include gatekeeper stats**
   ```bash
   # Check LLM gatekeeper activity
   sqlite3 ./state.sqlite "SELECT event_type, payload_json FROM manager_events WHERE event_type LIKE 'llm.%' ORDER BY sequence_no DESC LIMIT 10"
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

### Live dashboard (bundle, db, or mixed)
The dashboard is a lightweight FastAPI + Jinja app that reads real campaign state. It prefers bundle files for overview sections and uses SQLite for supplemental detail when both are provided.

```bash
research-orchestrator dashboard \
  --state-dir ./state_bundle \
  --db ./state.sqlite \
  --host 127.0.0.1 \
  --port 8000 \
  --reload
```

Use one source or both:
- bundle-only: `--state-dir ./state_bundle`
- db-only: `--db ./state.sqlite`
- mixed: pass both flags

If SQLite is corrupt but the bundle is readable, the dashboard still starts and shows a warning banner.

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

### Render the structured campaign brief
```bash
research-orchestrator campaign-brief   --db ./state.sqlite   --project mono-001
```

### Summarize LLM-assisted manager behavior
```bash
research-orchestrator manager-llm-report   --db ./state.sqlite   --project mono-001
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

## LLM-assisted manager layer

The research manager now supports a feature-flagged LLM assistance layer that sits between frontier generation and deterministic candidate selection.

Deterministic guardrails still remain the final authority:
- budget and capacity caps run first
- duplicate active signatures are rejected first
- repeated no-signal branches are still pruned deterministically
- move families must already exist in the registry
- synthesized parameters must match the registered parameter schema
- execution, Lean interaction, and result ingestion still use the existing deterministic pipeline

### Progressive feature flags

All new LLM-assisted behavior is off by default except local brief generation.

```bash
export RESEARCH_ORCHESTRATOR_LLM_BRIEF_GENERATION=1
export RESEARCH_ORCHESTRATOR_LLM_INTERPRETATION=0
export RESEARCH_ORCHESTRATOR_LLM_CANDIDATE_ANNOTATION=0
export RESEARCH_ORCHESTRATOR_LLM_PARAMETER_SYNTHESIS=0
export RESEARCH_ORCHESTRATOR_LLM_BRIDGE_HYPOTHESES=0
export RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND="python path/to/manager_llm.py"
export RESEARCH_ORCHESTRATOR_LLM_MANAGER_MODEL="your-model-name"
```

Recommended rollout:
- start with `RESEARCH_ORCHESTRATOR_LLM_BRIEF_GENERATION=1`
- then enable `RESEARCH_ORCHESTRATOR_LLM_INTERPRETATION=1`
- then enable `RESEARCH_ORCHESTRATOR_LLM_CANDIDATE_ANNOTATION=1`
- only after that turn on parameter synthesis and bridge hypotheses

### Stored manager artifacts

LLM-assisted manager artifacts are persisted in SQLite so they can be audited and replayed:
- `campaign_interpretations`
- `bridge_hypotheses`
- `manager_candidate_audits` now include baseline score, LLM adjustments, and final score breakdowns

Accepted parameter syntheses and candidate annotations are also embedded into candidate metadata and audit records so historical rankings can be compared without a separate execution path.

### Replay and evaluation

Use these commands to inspect and compare decisions:

```bash
research-orchestrator audit-run   --db ./state.sqlite   --run-id <manager-run-id>
research-orchestrator replay-run   --db ./state.sqlite   --experiment-id <experiment-id>   --include-manifest
research-orchestrator manager-llm-report   --db ./state.sqlite   --project mono-001
```

The aggregated LLM report summarizes:
- divergence frequency between baseline and LLM-assisted ordering
- average accepted LLM delta
- interpretation validity rate
- parameter synthesis acceptance rate
- downstream signal by policy path when measurable

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

## Project Dashboard

A FastAPI-based dashboard provides a clean, experiment-focused view of your research campaigns.

### Features
- **Problem filtering**: Switch between conjectures (e.g., erdos-123, erdos-181, erdos-44)
- **Status filtering**: Filter by Proved/Stalled/Failed/All
- **Experiment cards**: Each shows:
  - LLM reasoning (why the manager sent this experiment)
  - Raw results (duration, proof outcome, blockers)
  - LLM summary of findings
  - Knowledge graph contributions (+Node / +Edge format)
- **Search**: Filter experiments by move type, status, or content
- **Collapsible cards**: Most recent expanded by default
- **Dark theme**: GitHub-style monospace typography

### Run locally from SQLite
```bash
research-orchestrator dashboard \
  --db ./outputs/erdos_live_async/state.sqlite \
  --project erdos-combo-001 \
  --port 8000
```

Then open: http://127.0.0.1:8000/project

### Deploy to Vercel
The dashboard can be deployed to Vercel for public access:

```bash
# 1. Export state bundle from SQLite
research-orchestrator publish-state-bundle \
  --db ./outputs/erdos_live_async/state.sqlite \
  --project erdos-combo-001 \
  --output-dir ./outputs/dashboard_bundle_live

# 2. Deploy to Vercel
vercel --prod
```

The Vercel deployment reads from `outputs/dashboard_bundle_live/` which contains:
- `experiments.csv` - all experiment data
- `campaign_summary.json` - project metadata
- `manager_events.json` - timeline events

### Files
- `api/index.py` - Vercel serverless function (FastAPI)
- `src/research_orchestrator/dashboard_project.py` - Local dashboard router
- `vercel.json` - Vercel deployment config

## Recommended next upgrades

- Add canonicalization with a Lean-aware normalizer
- Add a richer evaluator using proof cost and recurrence gain
- Add a proper result ingester for `aristotle result`
- Add candidate audit trail extraction from manager_events for real selection rationale
