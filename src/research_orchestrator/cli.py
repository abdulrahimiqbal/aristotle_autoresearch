from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.db import Database
from research_orchestrator.orchestrator import manager_tick, run_one_cycle, submit_one_cycle, sync_provider_results
from research_orchestrator.reporter import build_report, write_report
from research_orchestrator.manager import choose_next_experiment


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
        "objective": brief.objective,
        "expected_signal": brief.expected_signal,
        "modification": brief.modification,
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


def build_parser():
    parser = argparse.ArgumentParser(prog="research-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

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
