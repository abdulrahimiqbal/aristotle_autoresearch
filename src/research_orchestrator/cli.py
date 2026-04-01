from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from research_orchestrator.campaign_planner import synthesize_campaign
from research_orchestrator.charter import load_charter, load_conjecture
from research_orchestrator.dashboard_loader import DashboardLoader
from research_orchestrator.db import Database
# State export (local only - no GitHub integration)
from research_orchestrator.llm_manager import build_campaign_brief, render_campaign_brief
from research_orchestrator.orchestrator import (
    backfill_provider_results,
    manager_tick,
    run_one_cycle,
    submit_one_cycle,
    sync_provider_results,
)
from research_orchestrator.replay import manager_llm_report, replay_experiment, replay_manager_run, reconstruct_manifest
from research_orchestrator.reporter import build_report, write_report
from research_orchestrator.manager import choose_next_experiment
from research_orchestrator.live_projections import refresh_live_projections
from research_orchestrator.health_server import start_health_server
from research_orchestrator.manager_config import load_config, ManagerConfig

import time
import signal
import sys


def cmd_solve(args):
    """Autonomous solve mode: start campaign and run until solved or stopped."""
    
    # Handle graceful shutdown
    stop_requested = [False]
    def handle_signal(signum, frame):
        print("\n[STOP] Shutdown requested. Finishing current tick...")
        stop_requested[0] = True
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Initialize database
    db = Database(args.db)
    db.initialize()
    
    # Start or resume campaign
    if args.project:
        # Resume existing campaign
        project_id = args.project
        charter = db.get_charter(project_id)
        if not charter:
            print(f"Error: Project {project_id} not found")
            sys.exit(1)
        print(f"[RESUME] Continuing campaign: {project_id}")
    else:
        # Start new campaign from prompt
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
        project_id = spec.project_id
        print(f"[START] New campaign: {project_id}")
        print(f"        Title: {spec.title}")
    
    # Setup workspace
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report_output) if args.report_output else workspace / "report.md"
    snapshot_path = report_path.with_suffix(".manager_snapshot.json")
    
    print(f"[CONFIG] Provider: {args.provider}")
    print(f"[CONFIG] Max active: {args.max_active}")
    print(f"[CONFIG] Max submit/tick: {args.max_submit_per_tick}")
    print(f"[CONFIG] Tick interval: {args.tick_interval}s")
    print(f"[CONFIG] Convergence threshold: {args.convergence_threshold * 100}%")
    print(f"[CONFIG] Max experiments: {args.max_experiments}")
    print("")
    print("=" * 60)
    print("AUTONOMOUS SOLVE MODE")
    print("Running until problem is solved or stopped (Ctrl+C)")
    print("=" * 60)
    print("")
    
    tick_count = 0
    start_time = time.time()
    
    while not stop_requested[0]:
        tick_count += 1
        tick_start = time.time()
        
        print(f"\n[TICK {tick_count}] {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check completion criteria
        convergence = db.convergence_metrics(project_id)
        conv_score = convergence.get("convergence_score", 0)
        open_obligations = convergence.get("distance_to_proof", {}).get("open_obligations_count", 999)
        trend = convergence.get("trend", "unknown")
        
        # Count experiments
        experiments = db.list_experiments(project_id)
        exp_count = len(experiments)
        
        print(f"  Progress: {conv_score * 100:.1f}% converged, {open_obligations} open obligations")
        print(f"  Trend: {trend} | Experiments: {exp_count}")
        
        # Check if solved
        if conv_score >= args.convergence_threshold and open_obligations == 0:
            print("\n" + "=" * 60)
            print("[SOLVED] Problem appears to be solved!")
            print(f"  Convergence: {conv_score * 100:.1f}%")
            print(f"  No open obligations remaining")
            print(f"  Total experiments: {exp_count}")
            print(f"  Total time: {time.time() - start_time:.0f}s")
            print("=" * 60)
            break
        
        # Check budget
        if exp_count >= args.max_experiments:
            print(f"\n[BUDGET] Reached max experiments ({args.max_experiments}). Stopping.")
            break
        
        # Run sync first
        try:
            print("  -> Syncing results...")
            sync_provider_results(db, project_id, args.provider, limit=args.max_active * 2)
        except Exception as e:
            print(f"  [WARN] Sync failed: {e}")
        
        # Run manager tick
        try:
            print("  -> Running manager tick...")
            result = manager_tick(
                db=db,
                project_id=project_id,
                provider_name=args.provider,
                workspace_root=str(workspace),
                max_active=args.max_active,
                max_submit_per_tick=args.max_submit_per_tick,
                llm_manager_mode=args.llm_manager,
                report_output=report_path,
                snapshot_output=snapshot_path,
            )
            print(f"  -> Synced: {result['jobs_synced']} | Submitted: {result['jobs_submitted']}")
            print(f"  -> Active: {result['active_after']} | Policy: {result['policy_path']}")
        except Exception as e:
            print(f"  [ERROR] Manager tick failed: {e}")
            if args.stop_on_error:
                raise
        
        # Refresh projections
        try:
            refresh_live_projections(db, project_id)
        except Exception as e:
            print(f"  [WARN] Projection refresh failed: {e}")
        
        # Sleep before next tick
        elapsed = time.time() - tick_start
        sleep_time = max(0, args.tick_interval - elapsed)
        if sleep_time > 0 and not stop_requested[0]:
            print(f"  -> Sleeping {sleep_time:.0f}s...")
            time.sleep(sleep_time)
    
    # Final report
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)
    
    final_conv = db.convergence_metrics(project_id)
    print(f"Convergence: {final_conv.get('convergence_score', 0) * 100:.1f}%")
    print(f"Trend: {final_conv.get('trend', 'unknown')}")
    print(f"Open obligations: {final_conv.get('distance_to_proof', {}).get('open_obligations_count', 0)}")
    print(f"Total experiments: {len(db.list_experiments(project_id))}")
    print(f"Report: {report_path}")
    print(f"Database: {args.db}")
    print("=" * 60)


def cmd_solve_env(args):
    """Autonomous solve mode using environment variables (Railway deployment)."""
    # Load configuration from environment
    try:
        config = load_config()
    except ValueError as e:
        print(f"[ERROR] Configuration error: {e}")
        sys.exit(1)

    print(f"[CONFIG] Problem {config.problem_number}: {config.project_id}")
    print(f"[CONFIG] Database: {config.database_path}")
    print(f"[CONFIG] Workspace: {config.workspace_path}")
    print(f"[CONFIG] Provider: {config.provider_name}")
    print(f"[CONFIG] LLM Mode: {config.llm_manager_mode}")
    print(f"[CONFIG] Max active: {config.max_active}")
    print(f"[CONFIG] Tick interval: {config.tick_interval_seconds}s")

    # Initialize database
    db = Database(config.database_path)
    db.initialize()

    # Check if project exists, error if not (Railway mode requires pre-initialized DB)
    charter = db.get_charter(config.project_id)
    if not charter:
        print(f"[ERROR] Project {config.project_id} not found in database.")
        print("[ERROR] Railway mode requires a pre-initialized database.")
        print("[INFO] Initialize locally first:")
        print(f"  research-orchestrator start-campaign --prompt '...' --db {config.database_path}")
        sys.exit(1)

    print(f"[RESUME] Continuing campaign: {config.project_id}")

    # Setup workspace
    from pathlib import Path
    workspace = Path(config.workspace_path)
    workspace.mkdir(parents=True, exist_ok=True)
    report_path, snapshot_path = config.to_report_paths()

    # Start health server
    health = None
    if config.enable_health_server:
        try:
            from research_orchestrator.llm_manager import get_synthesis_client
            llm_client = get_synthesis_client() if config.llm_manager_mode != "none" else None
        except Exception:
            llm_client = None

        health = start_health_server(
            port=config.health_port,
            project_id=config.project_id,
            db=db,
            llm_client=llm_client,
        )
        print(f"[HEALTH] Health server enabled on port {config.health_port}")

    # Handle graceful shutdown
    stop_requested = [False]
    def handle_signal(signum, frame):
        print("\n[STOP] Shutdown requested. Finishing current tick...")
        stop_requested[0] = True
        if health:
            health.set_healthy(False)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print("")
    print("=" * 60)
    print("AUTONOMOUS SOLVE MODE (Railway)")
    print("Running until problem is solved or stopped")
    print("=" * 60)
    print("")

    tick_count = 0
    start_time = time.time()

    while not stop_requested[0]:
        tick_count += 1
        tick_start = time.time()

        # Update health check
        if health:
            health.set_tick_timestamp()

        print(f"\n[TICK {tick_count}] {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Check completion criteria
        convergence = db.convergence_metrics(config.project_id)
        conv_score = convergence.get("convergence_score", 0)
        open_obligations = convergence.get("distance_to_proof", {}).get("open_obligations_count", 999)
        trend = convergence.get("trend", "unknown")

        # Count experiments
        experiments = db.list_experiments(config.project_id)
        exp_count = len(experiments)

        print(f"  Progress: {conv_score * 100:.1f}% converged, {open_obligations} open obligations")
        print(f"  Trend: {trend} | Experiments: {exp_count}")

        # Check if solved
        if conv_score >= config.convergence_threshold and open_obligations == 0:
            print("\n" + "=" * 60)
            print("[SOLVED] Problem appears to be solved!")
            print(f"  Convergence: {conv_score * 100:.1f}%")
            print(f"  No open obligations remaining")
            print(f"  Total experiments: {exp_count}")
            print(f"  Total time: {time.time() - start_time:.0f}s")
            print("=" * 60)
            break

        # Check budget
        if exp_count >= config.max_experiments:
            print(f"\n[BUDGET] Reached max experiments ({config.max_experiments}). Stopping.")
            break

        # Run sync first
        try:
            print("  -> Syncing results...")
            sync_provider_results(db, config.project_id, config.provider_name, limit=config.max_active * 2)
        except Exception as e:
            print(f"  [WARN] Sync failed: {e}")

        # Run manager tick
        try:
            print("  -> Running manager tick...")
            result = manager_tick(
                db=db,
                project_id=config.project_id,
                provider_name=config.provider_name,
                workspace_root=str(workspace),
                max_active=config.max_active,
                max_submit_per_tick=config.max_submit_per_tick,
                llm_manager_mode=config.llm_manager_mode,
                report_output=report_path,
                snapshot_output=snapshot_path,
            )
            print(f"  -> Synced: {result['jobs_synced']} | Submitted: {result['jobs_submitted']}")
            print(f"  -> Active: {result['active_after']} | Policy: {result['policy_path']}")
        except Exception as e:
            print(f"  [ERROR] Manager tick failed: {e}")
            if config.stop_on_error:
                raise

        # Refresh projections
        try:
            refresh_live_projections(db, config.project_id)
        except Exception as e:
            print(f"  [WARN] Projection refresh failed: {e}")

        # Sleep before next tick
        elapsed = time.time() - tick_start
        sleep_time = max(0, config.tick_interval_seconds - elapsed)
        if sleep_time > 0 and not stop_requested[0]:
            print(f"  -> Sleeping {sleep_time:.0f}s...")
            time.sleep(sleep_time)

    # Final report
    print("\n" + "=" * 60)
    print("FINAL STATUS")
    print("=" * 60)

    final_conv = db.convergence_metrics(config.project_id)
    print(f"Convergence: {final_conv.get('convergence_score', 0) * 100:.1f}%")
    print(f"Trend: {final_conv.get('trend', 'unknown')}")
    print(f"Open obligations: {final_conv.get('distance_to_proof', {}).get('open_obligations_count', 0)}")
    print(f"Total experiments: {len(db.list_experiments(config.project_id))}")
    print(f"Report: {report_path}")
    print(f"Database: {config.database_path}")
    print("=" * 60)


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
    project_id = args.project

    # Source materials for legacy fallback
    summary = db.project_summary(project_id)
    spec = db.get_campaign_spec(project_id)

    # 1. Attempt to gather data from projections (Control Plane source of truth)
    health_current = None
    try:
        health_row = db.conn.execute(
            "SELECT payload_json, manager_status, last_event_at, last_projection_at FROM system_health_current WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if health_row:
            health_current = {
                "manager_status": health_row["manager_status"],
                "last_event_at": health_row["last_event_at"],
                "last_projection_at": health_row["last_projection_at"],
                **json.loads(health_row["payload_json"]),
            }
    except Exception:
        pass

    active_current = []
    try:
        active_current = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM active_experiments_current WHERE project_id = ?",
                (project_id,),
            ).fetchall()
        ]
    except Exception:
        pass

    incidents_current = []
    try:
        incidents_current = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM incidents_current WHERE project_id = ? AND status = 'open'",
                (project_id,),
            ).fetchall()
        ]
    except Exception:
        pass

    timeline_check = db.check_event_timeline_integrity()

    payload = {
        "project_id": project_id,
        "title": summary["campaign_title"],
        "campaign_version": summary.get("campaign_version", ""),
        "raw_prompt": spec.raw_prompt if spec is not None else "",
        "summary": summary,
        "control_plane": {
            "manager_status": health_current["manager_status"] if health_current else "unknown",
            "last_event_at": health_current["last_event_at"] if health_current else "n/a",
            "last_projection_at": health_current["last_projection_at"] if health_current else "n/a",
            "timeline_ok": timeline_check.get("ok", False),
            "timeline_gaps": timeline_check.get("gaps", 0),
            "source_mode": "projection" if health_current else "legacy_fallback",
        },
        "open_questions": db.list_discovery_questions(project_id, status="open"),
        "open_incidents": incidents_current if health_current else db.list_incidents(project_id, status="open"),
        "active_experiments": active_current if active_current else db.list_active_experiments(project_id),
        "health": health_current if health_current else db.campaign_health(project_id),
        "version_drift": db.version_drift_summary(project_id),
        "source": "sqlite",
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


def cmd_campaign_brief(args):
    db = Database(args.db)
    db.initialize()
    brief = build_campaign_brief(db, args.project)
    print(json.dumps(render_campaign_brief(brief), indent=2))


def cmd_manager_llm_report(args):
    db = Database(args.db)
    db.initialize()
    payload = manager_llm_report(db, args.project)
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


def cmd_db_check(args):
    db = Database(args.db)
    db.initialize()
    timeline_check = db.check_event_timeline_integrity()
    payload = {
        "quick_check": db.quick_check(),
        "integrity_check": db.integrity_check(),
        "wal_checkpoint": db.checkpoint_wal(),
        "event_timeline_gaps": timeline_check.get("gaps", 0),
        "event_timeline_ok": timeline_check.get("ok", False),
    }
    print(json.dumps(payload, indent=2))


def cmd_db_backup(args):
    db = Database(args.db)
    db.initialize()
    destination = db.backup_to(args.output)
    print(json.dumps({"backup": destination}, indent=2))


def cmd_db_export(args):
    db = Database(args.db)
    db.initialize()
    written = db.export_readable_state(args.project, args.output_dir)
    print(json.dumps({"written": written}, indent=2))


def cmd_db_refresh_projections(args):
    db = Database(args.db)
    db.initialize()
    project_id = args.project
    if not project_id:
        row = db.conn.execute("SELECT project_id FROM projects ORDER BY created_at DESC LIMIT 1").fetchone()
        project_id = row[0] if row else None
    if not project_id:
        raise SystemExit("No project found in database.")
    refresh_live_projections(db, project_id)
    print(f"Refreshed live projections for project {project_id}")


def cmd_publish_state_bundle(args):
    db = Database(args.db)
    db.initialize()
    written = publish_state_bundle(
        db=db,
        project_id=args.project,
        state_dir=args.output_dir,
        report_path=args.report if args.report else None,
        manager_snapshot_path=args.manager_snapshot if args.manager_snapshot else None,
        include_sqlite_snapshot=args.include_sqlite,
    )
    print(json.dumps({"written": written}, indent=2))


def cmd_dashboard(args):
    if not args.db:
        raise SystemExit("dashboard requires --db")
    try:
        state = DashboardLoader(
            db_path=args.db,
            project_id=args.project,
        ).load()
    except Exception as exc:
        raise SystemExit(f"dashboard source initialization failed: {exc}") from exc
    print(f"Launching dashboard | source={state.source_mode} | project={state.project_id} | db={args.db}")
    try:
        from research_orchestrator.dashboard_app import create_dashboard_app
        import uvicorn
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "dashboard dependencies are missing; install project dependencies first "
            "(fastapi, uvicorn, jinja2)."
        ) from exc

    app = create_dashboard_app(db=args.db, project_id=args.project)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)


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

    campaign_brief = sub.add_parser("campaign-brief", help="Render the structured campaign brief used for manager reasoning.")
    campaign_brief.add_argument("--db", required=True)
    campaign_brief.add_argument("--project", required=True)
    campaign_brief.set_defaults(func=cmd_campaign_brief)

    replay_run = sub.add_parser("replay-run", help="Replay a historical experiment scoring decision from stored manifests.")
    replay_run.add_argument("--db", required=True)
    replay_run.add_argument("--experiment-id", required=True)
    replay_run.add_argument("--include-manifest", action="store_true")
    replay_run.set_defaults(func=cmd_replay_run)

    llm_report = sub.add_parser("manager-llm-report", help="Summarize LLM-assisted manager divergence, validity, and downstream signal.")
    llm_report.add_argument("--db", required=True)
    llm_report.add_argument("--project", required=True)
    llm_report.set_defaults(func=cmd_manager_llm_report)

    db_check = sub.add_parser("db-check", help="Run SQLite integrity checks.")
    db_check.add_argument("--db", required=True)
    db_check.set_defaults(func=cmd_db_check)

    db_backup = sub.add_parser("db-backup", help="Create a SQLite backup.")
    db_backup.add_argument("--db", required=True)
    db_backup.add_argument("--output", required=True)
    db_backup.set_defaults(func=cmd_db_backup)

    db_export = sub.add_parser("db-export", help="Export human-readable campaign state files.")
    db_export.add_argument("--db", required=True)
    db_export.add_argument("--project", required=True)
    db_export.add_argument("--output-dir", required=True)
    db_export.set_defaults(func=cmd_db_export)

    publish_bundle = sub.add_parser("publish-state-bundle", help="Publish a readable state bundle with optional SQLite snapshot.")
    publish_bundle.add_argument("--db", required=True)
    publish_bundle.add_argument("--project", required=True)
    publish_bundle.add_argument("--output-dir", required=True)
    publish_bundle.add_argument("--report")
    publish_bundle.add_argument("--manager-snapshot")
    publish_bundle.add_argument("--include-sqlite", action="store_true")
    publish_bundle.set_defaults(func=cmd_publish_state_bundle)

    dashboard = sub.add_parser("dashboard", help="Launch a local, live dashboard from SQLite.")
    dashboard.add_argument("--db", required=True)
    dashboard.add_argument("--project", default="erdos-combo-001")
    dashboard.add_argument("--host", default="127.0.0.1")
    dashboard.add_argument("--port", type=int, default=8000)
    dashboard.add_argument("--reload", action="store_true")
    dashboard.set_defaults(func=cmd_dashboard)

    db_refresh = sub.add_parser("db-refresh-projections", help="Refresh live timeline projections from the manager event log.")
    db_refresh.add_argument("--db", required=True)
    db_refresh.add_argument("--project", default="")
    db_refresh.set_defaults(func=cmd_db_refresh_projections)

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

    # Autonomous solve command - run until problem is solved
    solve = sub.add_parser("solve", help="Start campaign and run autonomously until solved.")
    solve.add_argument("--db", required=True, help="Path to SQLite database")
    solve.add_argument("--prompt", help="Natural language problem description (for new campaigns)")
    solve.add_argument("--project", help="Existing project ID to resume (alternative to --prompt)")
    solve.add_argument("--workspace", required=True, help="Workspace directory for experiments")
    solve.add_argument("--provider", choices=["mock", "aristotle-cli"], default="aristotle-cli", help="Provider to use")
    solve.add_argument("--max-active", type=int, default=3, help="Max concurrent experiments")
    solve.add_argument("--max-submit-per-tick", type=int, default=2, help="Max new experiments per tick")
    solve.add_argument("--tick-interval", type=int, default=30, help="Seconds between ticks")
    solve.add_argument("--convergence-threshold", type=float, default=0.9, help="Convergence score to consider solved (0-1)")
    solve.add_argument("--max-experiments", type=int, default=100, help="Max total experiments before stopping")
    solve.add_argument("--llm-manager", choices=["on", "off", "auto"], default="off", help="LLM manager mode")
    solve.add_argument("--report-output", help="Path for markdown report (default: workspace/report.md)")
    solve.add_argument("--stop-on-error", action="store_true", help="Stop on first error (default: continue)")
    solve.set_defaults(func=cmd_solve)

    # Autonomous solve using environment variables (Railway deployment mode)
    solve_env = sub.add_parser("solve-env", help="Run autonomously using environment variables (Railway mode).")
    solve_env.add_argument("--health-port", type=int, default=8080, help="Port for health check server")
    solve_env.set_defaults(func=cmd_solve_env)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
