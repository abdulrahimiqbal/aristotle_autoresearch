from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from research_orchestrator.campaign_planner import synthesize_campaign
from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.github_state import sync_github_state
from research_orchestrator.orchestrator import (
    backfill_provider_results,
    manager_tick,
    run_one_cycle,
    submit_one_cycle,
    sync_provider_results,
)
from research_orchestrator.replay import replay_experiment, replay_manager_run, reconstruct_manifest
from research_orchestrator.reporter import build_report, write_report
from research_orchestrator.manager import choose_next_experiment


def cmd_start_campaign(args):
    db = Database(args.db)
    db.initialize()
    spec, charter, conjectures, questions = synthesize_campaign(args.prompt)
    db.save_project(charter)
    db.save_campaign_spec(spec)
    for conjecture in conjectures:
        db.save_conjecture(conjecture)
    for question in questions:
        db.save_discovery_question(question)
    db.add_audit_event(
        project_id=spec.project_id,
        event_type="campaign_started",
        detail={
            "version": spec.version,
            "title": spec.title,
            "conjectures": [item.conjecture_id for item in conjectures],
            "discovery_questions": [item.question_id for item in questions],
        },
    )
    print(f"Started campaign {spec.project_id}")
    print(json.dumps(
        {
            "project_id": spec.project_id,
            "title": spec.title,
            "conjectures": [item.conjecture_id for item in conjectures],
            "open_discovery_questions": [item.question for item in questions],
        },
        indent=2,
    ))


def cmd_campaign_status(args):
    db = Database(args.db)
    db.initialize()
    summary = db.project_summary(args.project)
    spec = db.get_campaign_spec(args.project)
    payload = {
        "project_id": args.project,
        "title": summary["campaign_title"],
        "campaign_version": summary.get("campaign_version", ""),
        "raw_prompt": spec.raw_prompt if spec is not None else "",
        "summary": summary,
        "open_questions": db.list_discovery_questions(args.project, status="open"),
        "discovery_nodes": db.list_discovery_nodes(args.project)[:20],
        "recent_audit_events": db.list_audit_events(args.project, limit=10),
        "open_incidents": db.list_incidents(args.project, status="open"),
        "health": db.campaign_health(args.project),
        "version_drift": db.version_drift_summary(args.project),
    }
    print(json.dumps(payload, indent=2))


def cmd_campaign_health(args):
    db = Database(args.db)
    db.initialize()
    health = db.campaign_health(args.project)
    if args.format == "json":
        print(json.dumps(health, indent=2))
        return
    counts = health["counts"]
    signals = health["signals"]
    print(
        "Campaign health"
        f" | active={counts['active']}"
        f" | pending={counts['pending']}"
        f" | running={counts['running']}"
        f" | completed={counts['completed']}"
        f" | failed={counts['failed']}"
    )
    print(
        "Signals"
        f" | ingestion_success={signals['structured_ingestion_success_rate']}"
        f" | semantic_reuse={signals['semantic_reuse_rate']}"
        f" | transfer_usage={signals['transfer_usage_rate']}"
        f" | reusable_structure={signals.get('reusable_structure_rate', 0.0)}"
        f" | obstruction_discovery={signals.get('obstruction_discovery_rate', 0.0)}"
        f" | high_priority_frontier={signals.get('high_priority_frontier_share', 0.0)}"
        f" | no_signal_streak={signals['repeated_no_signal_streak']}"
        f" | duplicate_pressure={signals['duplicate_frontier_pressure']}"
    )
    print(json.dumps(health["incidents"], indent=2))


def cmd_audit_run(args):
    db = Database(args.db)
    db.initialize()
    payload = replay_manager_run(db, args.run_id)
    print(json.dumps(payload, indent=2))


def cmd_replay_run(args):
    db = Database(args.db)
    db.initialize()
    payload = replay_experiment(db, args.experiment_id)
    if args.include_manifest:
        payload["manifest"] = reconstruct_manifest(db, args.experiment_id)
    print(json.dumps(payload, indent=2))


def cmd_init_project(args):
    db = Database(args.db)
    db.initialize()
    charter = load_charter(args.charter)
    conjecture = load_conjecture(args.conjecture)
    db.save_project(charter)
    db.save_conjecture(conjecture)
    print(f"Initialized project {charter.project_id} in {args.db}")


def cmd_run_cycle(args):
    db = Database(args.db)
    db.initialize()
    for _ in range(args.max_cycles):
        result = run_one_cycle(db, args.project, args.provider, args.workspace)
        brief = result["brief"]
        print(
            f"Completed {brief.experiment_id} | move={brief.move} | phase={brief.phase} | status={result['result'].status} | blocker={result['result'].blocker_type}"
        )


def cmd_submit_cycle(args):
    db = Database(args.db)
    db.initialize()
    for _ in range(args.max_cycles):
        result = submit_one_cycle(db, args.project, args.provider, args.workspace)
        brief = result["brief"]
        external = f" | external_id={result['result'].external_id}" if result["result"].external_id else ""
        print(
            f"Submitted {brief.experiment_id} | move={brief.move} | phase={brief.phase} | status={result['result'].status}{external}"
        )


def cmd_sync_results(args):
    db = Database(args.db)
    db.initialize()
    results = sync_provider_results(db, args.project, args.provider, args.limit)
    if not results:
        print("No asynchronous results to sync.")
        return
    for item in results:
        brief = item["brief"]
        result = item["result"]
        external = f" | external_id={result.external_id}" if result.external_id else ""
        print(
            f"Synced {brief.experiment_id} | status={result.status} | blocker={result.blocker_type}{external}"
        )


def cmd_backfill_results(args):
    db = Database(args.db)
    db.initialize()
    results = backfill_provider_results(db, args.project, args.provider, args.limit)
    if not results:
        print("No completed low-signal results eligible for backfill.")
        return
    for item in results:
        brief = item["brief"]
        result = item["result"]
        external = f" | external_id={result.external_id}" if result.external_id else ""
        print(
            f"Backfilled {brief.experiment_id} | status={result.status} | blocker={result.blocker_type}{external}"
        )


def cmd_report(args):
    db = Database(args.db)
    db.initialize()
    write_report(db, args.project, args.output)
    print(f"Wrote report to {args.output}")


def cmd_manager_tick(args):
    db = Database(args.db)
    db.initialize()
    report_output = Path(args.report_output)
    snapshot_output = report_output.with_suffix(".manager_snapshot.json")
    result = manager_tick(
        db=db,
        project_id=args.project,
        provider_name=args.provider,
        workspace_root=args.workspace,
        max_active=args.max_active,
        max_submit_per_tick=args.max_submit_per_tick,
        llm_manager_mode=args.llm_manager,
        report_output=report_output,
        snapshot_output=snapshot_output,
    )
    print(
        f"Manager tick {result['run_id']} | policy={result['policy_path']} | "
        f"synced={result['jobs_synced']} | submitted={result['jobs_submitted']} | "
        f"active_before={result['active_before']} | active_after={result['active_after']}"
    )
    print(f"Report: {result['report_output']}")
    print(f"Snapshot: {result['snapshot_output']}")


def cmd_preview_next(args):
    db = Database(args.db)
    db.initialize()
    brief, manager_prompt, frontier = choose_next_experiment(db, args.project, args.workspace)
    shutil.rmtree(brief.workspace_dir, ignore_errors=True)
    print("=== NEXT EXPERIMENT ===")
    print(json.dumps({
        "experiment_id": brief.experiment_id,
        "phase": brief.phase,
        "move": brief.move,
        "move_family": brief.move_family or brief.move,
        "theorem_family_id": brief.theorem_family_id,
        "objective": brief.objective,
        "expected_signal": brief.expected_signal,
        "modification": brief.modification,
        "rationale": brief.rationale,
    }, indent=2))
    print("\n=== MANAGER PROMPT ===")
    print(manager_prompt)


def cmd_lint_prompts(args):
    db = Database(args.db)
    db.initialize()
    preview = run_one_cycle(db, args.project, "mock", args.workspace)
    # Delete the side effects of this preview cycle if the user requested a clean lint only.
    if args.clean_preview:
        db.conn.execute("DELETE FROM experiments WHERE experiment_id = ?", (preview["brief"].experiment_id,))
        db.conn.execute("DELETE FROM research_notes WHERE experiment_id = ?", (preview["brief"].experiment_id,))
        db.conn.execute("DELETE FROM lemma_occurrences WHERE experiment_id = ?", (preview["brief"].experiment_id,))
        db.conn.commit()
        shutil.rmtree(preview["brief"].workspace_dir, ignore_errors=True)
    print("manager_prompt_ok=", preview["manager_prompt_lint"].ok)
    print("worker_prompt_ok=", preview["worker_prompt_lint"].ok)
    if not preview["manager_prompt_lint"].ok:
        print("missing manager snippets:", preview["manager_prompt_lint"].missing)
    if not preview["worker_prompt_lint"].ok:
        print("missing worker snippets:", preview["worker_prompt_lint"].missing)


def cmd_demo(args):
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    db_path = workspace / "state.sqlite"
    report_path = workspace / "report.md"

    db = Database(db_path)
    db.initialize()

    root = Path(__file__).resolve().parents[2]
    charter_path = root / "examples" / "project_charter.json"
    conjecture_path = root / "examples" / "conjectures" / "weighted_monotone.json"

    charter = load_charter(charter_path)
    conjecture = load_conjecture(conjecture_path)
    db.save_project(charter)
    db.save_conjecture(conjecture)

    work_dir = workspace / "work"
    for _ in range(args.max_cycles):
        result = run_one_cycle(db, charter.project_id, "mock", work_dir)
        brief = result["brief"]
        print(f"[demo] {brief.experiment_id} {brief.move} -> {result['result'].status}/{result['result'].blocker_type}")

    write_report(db, charter.project_id, report_path)
    print(f"Demo complete. Report: {report_path}")


def cmd_sync_github_state(args):
    written = sync_github_state(
        repo=args.repo,
        ref=args.ref,
        state_dir=args.state_dir,
    )
    print(f"Synced {len(written)} canonical state files from {args.repo}@{args.ref}")
    for path in written:
        print(path)


def build_parser():
    parser = argparse.ArgumentParser(prog="research-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    start_campaign = sub.add_parser("start-campaign", help="Create a research campaign from one natural-language prompt.")
    start_campaign.add_argument("--db", required=True)
    start_campaign.add_argument("--prompt", required=True)
    start_campaign.set_defaults(func=cmd_start_campaign)

    campaign_status = sub.add_parser("campaign-status", help="Inspect campaign state, discovery graph, and incidents.")
    campaign_status.add_argument("--db", required=True)
    campaign_status.add_argument("--project", required=True)
    campaign_status.set_defaults(func=cmd_campaign_status)

    campaign_health = sub.add_parser("campaign-health", help="Inspect machine-readable campaign health and runtime signals.")
    campaign_health.add_argument("--db", required=True)
    campaign_health.add_argument("--project", required=True)
    campaign_health.add_argument("--format", choices=["text", "json"], default="text")
    campaign_health.set_defaults(func=cmd_campaign_health)

    init_project = sub.add_parser("init-project", help="Initialize a project from charter and conjecture files.")
    init_project.add_argument("--db", required=True)
    init_project.add_argument("--charter", required=True)
    init_project.add_argument("--conjecture", required=True)
    init_project.set_defaults(func=cmd_init_project)

    run_cycle = sub.add_parser("run-cycle", help="Run one or more research cycles.")
    run_cycle.add_argument("--db", required=True)
    run_cycle.add_argument("--project", required=True)
    run_cycle.add_argument("--provider", choices=["mock", "aristotle-cli"], default="mock")
    run_cycle.add_argument("--workspace", required=True)
    run_cycle.add_argument("--max-cycles", type=int, default=1)
    run_cycle.set_defaults(func=cmd_run_cycle)

    submit_cycle = sub.add_parser("submit-cycle", help="Submit one or more research cycles without waiting for asynchronous providers.")
    submit_cycle.add_argument("--db", required=True)
    submit_cycle.add_argument("--project", required=True)
    submit_cycle.add_argument("--provider", choices=["mock", "aristotle-cli"], default="aristotle-cli")
    submit_cycle.add_argument("--workspace", required=True)
    submit_cycle.add_argument("--max-cycles", type=int, default=1)
    submit_cycle.set_defaults(func=cmd_submit_cycle)

    sync_results = sub.add_parser("sync-results", help="Poll asynchronous provider jobs and ingest finished results.")
    sync_results.add_argument("--db", required=True)
    sync_results.add_argument("--project", required=True)
    sync_results.add_argument("--provider", choices=["mock", "aristotle-cli"], default="aristotle-cli")
    sync_results.add_argument("--limit", type=int, default=None)
    sync_results.set_defaults(func=cmd_sync_results)

    backfill_results = sub.add_parser(
        "backfill-results",
        help="Retry result retrieval for completed low-signal asynchronous provider jobs.",
    )
    backfill_results.add_argument("--db", required=True)
    backfill_results.add_argument("--project", required=True)
    backfill_results.add_argument("--provider", choices=["mock", "aristotle-cli"], default="aristotle-cli")
    backfill_results.add_argument("--limit", type=int, default=None)
    backfill_results.set_defaults(func=cmd_backfill_results)

    preview_next = sub.add_parser("preview-next", help="Preview the next automatically chosen experiment.")
    preview_next.add_argument("--db", required=True)
    preview_next.add_argument("--project", required=True)
    preview_next.add_argument("--workspace", default="./preview_work")
    preview_next.set_defaults(func=cmd_preview_next)

    report = sub.add_parser("report", help="Generate a markdown research report.")
    report.add_argument("--db", required=True)
    report.add_argument("--project", required=True)
    report.add_argument("--output", required=True)
    report.set_defaults(func=cmd_report)

    manager_tick_parser = sub.add_parser("manager-tick", help="Run one stateless campaign-control iteration: sync, rank, submit, and report.")
    manager_tick_parser.add_argument("--db", required=True)
    manager_tick_parser.add_argument("--project", required=True)
    manager_tick_parser.add_argument("--workspace", required=True)
    manager_tick_parser.add_argument("--provider", choices=["mock", "aristotle-cli"], default="aristotle-cli")
    manager_tick_parser.add_argument("--max-active", type=int, default=5)
    manager_tick_parser.add_argument("--max-submit-per-tick", type=int, default=5)
    manager_tick_parser.add_argument("--report-output", required=True)
    manager_tick_parser.add_argument("--llm-manager", choices=["on", "off", "auto"], default="auto")
    manager_tick_parser.set_defaults(func=cmd_manager_tick)

    audit_run = sub.add_parser("audit-run", help="Replay a historical manager decision from stored candidate audits.")
    audit_run.add_argument("--db", required=True)
    audit_run.add_argument("--run-id", required=True)
    audit_run.set_defaults(func=cmd_audit_run)

    replay_run = sub.add_parser("replay-run", help="Replay a historical experiment scoring decision from stored manifests.")
    replay_run.add_argument("--db", required=True)
    replay_run.add_argument("--experiment-id", required=True)
    replay_run.add_argument("--include-manifest", action="store_true")
    replay_run.set_defaults(func=cmd_replay_run)

    sync_github = sub.add_parser(
        "sync-github-state",
        help="Download the canonical live campaign state from GitHub into the local state directory.",
    )
    sync_github.add_argument("--repo", default="abdulrahimiqbal/aristotle_autoresearch")
    sync_github.add_argument("--ref", default="campaign-state")
    sync_github.add_argument("--state-dir", default="outputs/erdos_live_async")
    sync_github.set_defaults(func=cmd_sync_github_state)

    lint = sub.add_parser("lint-prompts", help="Generate prompts for the next cycle and lint them.")
    lint.add_argument("--db", required=True)
    lint.add_argument("--project", required=True)
    lint.add_argument("--workspace", default="./lint_work")
    lint.add_argument("--clean-preview", action="store_true")
    lint.set_defaults(func=cmd_lint_prompts)

    demo = sub.add_parser("demo", help="Run a complete local demo with the mock provider.")
    demo.add_argument("--workspace", required=True)
    demo.add_argument("--max-cycles", type=int, default=5)
    demo.set_defaults(func=cmd_demo)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
