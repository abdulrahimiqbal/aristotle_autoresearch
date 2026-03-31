from __future__ import annotations

import json
from pathlib import Path

from research_orchestrator.db import Database


def build_report(db: Database, project_id: str) -> str:
    charter = db.get_charter(project_id)
    spec = db.get_campaign_spec(project_id)
    summary = db.project_summary(project_id)
    experiments = db.list_experiments(project_id)
    active = db.list_active_experiments(project_id)
    recent_completed = db.list_completed_experiments(project_id, limit=5)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    recurring_traces = db.recurring_proof_traces(project_id)
    blocker_summary = db.blocker_summary(project_id)
    blockers_by_move = summary.get("blockers_by_move", [])
    counterexample_summary = summary.get("counterexample_summary", [])
    no_signal_branches = summary.get("no_signal_branches", [])
    sensitivity = db.assumption_sensitivity(project_id)
    latest_manager_run = db.latest_manager_run(project_id)
    latest_health = db.latest_campaign_health_snapshot(project_id)
    version_drift = db.version_drift_summary(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    discovery_nodes = db.list_discovery_nodes(project_id)
    discovery_edges = db.list_discovery_edges(project_id)
    incidents = db.list_incidents(project_id, status="open")
    audit_events = db.list_audit_events(project_id, limit=10)

    lines = []
    lines.append(f"# Research Report: {charter.title}")
    lines.append("")
    lines.append(f"**Project ID:** `{charter.project_id}`")
    lines.append("")
    if spec is not None:
        lines.append("## Campaign Contract")
        lines.append("")
        lines.append(f"- version: `{spec.version}`")
        lines.append(f"- runtime: `{spec.runtime_policy.runtime}`")
        lines.append(f"- autonomy: `{spec.runtime_policy.autonomy_mode}`")
        lines.append(f"- verification mode: `{spec.runtime_policy.verification_mode}`")
        lines.append(f"- mission: {spec.mission}")
        lines.append("- verification-as-discovery: experiments are judged by the verified discovery graph, not only theorem proofs")
        lines.append("")
    lines.append("## Overarching problem")
    lines.append("")
    lines.append(charter.overarching_problem)
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Experiments: {summary['num_experiments']}")
    lines.append(f"- Succeeded: {summary['solved']}")
    lines.append(f"- Stalled: {summary['stalled']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Pending: {summary.get('pending', 0)}")
    lines.append("")
    lines.append("## Campaign Health")
    lines.append("")
    health = latest_health["health"] if latest_health is not None else db.campaign_health(project_id)
    counts = health.get("counts", {})
    signals = health.get("signals", {})
    incidents_summary = health.get("incidents", {})
    runtime_controls = health.get("runtime_controls", {})
    lines.append(f"- active={counts.get('active', 0)} pending={counts.get('pending', 0)} running={counts.get('running', 0)} completed={counts.get('completed', 0)} failed={counts.get('failed', 0)}")
    lines.append(f"- structured ingestion success rate: {signals.get('structured_ingestion_success_rate', 0.0)}")
    lines.append(f"- semantic reuse rate: {signals.get('semantic_reuse_rate', 0.0)}")
    lines.append(f"- transfer usage rate: {signals.get('transfer_usage_rate', 0.0)}")
    lines.append(f"- reusable structure rate: {signals.get('reusable_structure_rate', 0.0)}")
    lines.append(f"- obstruction discovery rate: {signals.get('obstruction_discovery_rate', 0.0)}")
    lines.append(f"- high-priority frontier share: {signals.get('high_priority_frontier_share', 0.0)}")
    lines.append(f"- repeated no-signal streak: {signals.get('repeated_no_signal_streak', 0)}")
    lines.append(f"- duplicate frontier pressure: {signals.get('duplicate_frontier_pressure', 0)}")
    lines.append(f"- move-family diversity: frontier={signals.get('candidate_move_family_diversity', 0)} completed={signals.get('completed_move_family_diversity', 0)}")
    lines.append(f"- open incidents: {incidents_summary.get('open_total', 0)}")
    if runtime_controls.get("stuck_runs"):
        for item in runtime_controls["stuck_runs"][:5]:
            lines.append(
                f"- stuck run `{item['experiment_id']}` status=`{item['status']}` class=`{item['classification']}` sync_age={item['sync_age_seconds']}s"
            )
    if runtime_controls.get("retry_exhausted"):
        lines.append(f"- retry budget exhausted: {', '.join(runtime_controls['retry_exhausted'][:5])}")
    lines.append("")
    lines.append("## Version Drift")
    lines.append("")
    mismatch_summary = version_drift.get("mismatches", {})
    if mismatch_summary:
        for key, values in mismatch_summary.items():
            for version, count in values.items():
                lines.append(f"- `{key}` historical=`{version}` current=`{version_drift['current'][key]}` count={count}")
    else:
        lines.append("- No manifest version drift detected.")
    lines.append("")
    lines.append("## Discovery Graph")
    lines.append("")
    counts = summary.get("discovery_graph_counts", {})
    lines.append(f"- nodes: {counts.get('nodes', 0)}")
    lines.append(f"- edges: {counts.get('edges', 0)}")
    lines.append(f"- verified-like nodes: {counts.get('verified_like_nodes', 0)}")
    if discovery_nodes:
        for item in discovery_nodes[:10]:
            lines.append(
                f"- `{item['node_type']}` `{item['label']}` confidence={item['confidence']} provenance={item['provenance_kind']}"
            )
    else:
        lines.append("- No discovery nodes yet.")
    lines.append("")
    lines.append("## Discovery Questions")
    lines.append("")
    if open_questions:
        for item in open_questions:
            lines.append(f"- [{item['category']}] {item['question']}")
    else:
        lines.append("- No open discovery questions.")
    lines.append("")
    conjectures = db.list_conjectures(project_id)
    tuned = [
        item for item in conjectures
        if item.family_metadata.get("campaign_focus") or item.family_metadata.get("preferred_move_families")
    ]
    lines.append("## Conjecture Tuning")
    lines.append("")
    if tuned:
        for conjecture in tuned:
            lines.append(f"### {conjecture.name}")
            lines.append("")
            focus = conjecture.family_metadata.get("campaign_focus") or []
            preferred = conjecture.family_metadata.get("preferred_move_families") or []
            for question in conjecture.family_metadata.get("seed_discovery_questions", [])[:3]:
                lines.append(f"- seed question [{question.get('category', 'focus')}]: {question.get('question', '')}")
            if focus:
                lines.append(f"- focus areas: {', '.join(focus)}")
            if preferred:
                lines.append(f"- preferred move families: {', '.join(preferred)}")
            lines.append("")
    else:
        lines.append("- No conjecture-specific tuning metadata.")
        lines.append("")
    lines.append("## Active jobs")
    lines.append("")
    # Prefer *_current projection tables for operational data (Control Plane source of truth)
    try:
        active_current = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM active_experiments_current WHERE project_id = ?",
                (project_id,),
            ).fetchall()
        ]
        if active_current:
            by_status: dict[str, int] = {}
            for item in active_current:
                status_key = item.get("external_status") or item.get("status") or "unknown"
                by_status[status_key] = by_status.get(status_key, 0) + 1
            for status_key, count in sorted(by_status.items()):
                lines.append(f"- `{status_key}`: {count}")
        else:
            lines.append("- None active.")
    except Exception:
        # Fallback to legacy path if projections not yet available
        if active:
            for item in summary.get("active_by_external_status", []):
                lines.append(f"- `{item['external_status']}`: {item['count']}")
        else:
            lines.append("- None active.")
    lines.append("")
    lines.append("## Recently completed")
    lines.append("")
    # Prefer *_current projection tables (Control Plane source of truth)
    try:
        recent_current = [
            json.loads(row["payload_json"])
            for row in db.conn.execute(
                "SELECT payload_json FROM recent_results_current WHERE project_id = ? ORDER BY completed_at DESC LIMIT 5",
                (project_id,),
            ).fetchall()
        ]
        if recent_current:
            for experiment in recent_current:
                lines.append(
                    f"- `{experiment['experiment_id']}` on `{experiment['conjecture_id']}` -> `{experiment['status']}`"
                )
        else:
            lines.append("- None yet.")
    except Exception:
        # Fallback to legacy path
        if recent_completed:
            for experiment in recent_completed:
                lines.append(
                    f"- `{experiment['experiment_id']}` on `{experiment['conjecture_id']}` -> `{experiment['status']}`"
                )
        else:
            lines.append("- None yet.")
    lines.append("")
    lines.append("## Recurring lemmas")
    lines.append("")
    if recurring:
        for item in recurring:
            lines.append(f"- `{item['representative_statement']}` — reuse={item['reuse_count']}")
    else:
        lines.append("- None yet.")
    lines.append("")
    lines.append("## Space Search Progress")
    lines.append("")
    if recurring:
        lines.append(f"- recurring lemmas: {len(recurring)} clusters")
    else:
        lines.append("- recurring lemmas: none stabilized yet")
    if recurring_subgoals:
        lines.append(f"- recurring subgoals: {len(recurring_subgoals)} clusters")
    else:
        lines.append("- recurring subgoals: none stabilized yet")
    if recurring_traces:
        lines.append(f"- recurring proof traces: {len(recurring_traces)} motifs")
    else:
        lines.append("- recurring proof traces: none stabilized yet")
    if no_signal_branches:
        for item in no_signal_branches[:5]:
            lines.append(f"- no-signal branch `{item['conjecture_id']}` / `{item['move']}` repeated {item['observations']} times")
    else:
        lines.append("- no-signal branches: none crossed the backoff threshold")
    lines.append("")
    lines.append("## What we learned")
    lines.append("")
    if recurring:
        lines.append("- recurring lemmas are beginning to cluster across runs")
    else:
        lines.append("- no recurring lemmas have stabilized yet")
    if recurring_subgoals:
        for item in recurring_subgoals[:5]:
            lines.append(f"- repeated subgoal `{item['statement']}` across {item['observations']} runs")
    else:
        lines.append("- no repeated subgoals captured yet")
    if blocker_summary:
        for item in blocker_summary[:5]:
            lines.append(
                f"- blocker pattern `{item['blocker_type']}` / `{item['proof_outcome']}` appeared {item['observations']} times"
            )
    else:
        lines.append("- no blocker patterns aggregated yet")
    if blockers_by_move:
        for item in blockers_by_move[:5]:
            lines.append(
                f"- move `{item['move']}` repeatedly yields blocker `{item['blocker_type']}` / `{item['proof_outcome']}` ({item['observations']} runs)"
            )
    if counterexample_summary:
        for item in counterexample_summary[:5]:
            lines.append(f"- counterexample witness motif `{item['witness']}` appeared {item['observations']} times")
    lines.append("")
    lines.append("## Assumption sensitivity")
    lines.append("")
    if sensitivity:
        for item in sensitivity:
            lines.append(
                f"- `{item['assumption_name']}` — avg_sensitivity={item['avg_sensitivity']} across {item['observations']} observations"
            )
    else:
        lines.append("- None yet.")
    lines.append("")
    lines.append("## Experiment log")
    lines.append("")
    for experiment in experiments:
        lines.append(f"### {experiment['experiment_id']}")
        lines.append("")
        lines.append(f"- move: `{experiment['move']}`")
        if experiment.get("move_family"):
            lines.append(f"- move family: `{experiment['move_family']}`")
        if experiment.get("theorem_family_id"):
            lines.append(f"- theorem family: `{experiment['theorem_family_id']}`")
        lines.append(f"- phase: `{experiment['phase']}`")
        lines.append(f"- status: `{experiment['status']}`")
        if experiment.get("proof_outcome"):
            lines.append(f"- proof outcome: `{experiment['proof_outcome']}`")
        lines.append(f"- blocker: `{experiment['blocker_type']}`")
        if experiment.get("discovery_question_id"):
            question = next(
                (item for item in db.list_discovery_questions(project_id) if item["question_id"] == experiment["discovery_question_id"]),
                None,
            )
            if question is not None:
                lines.append(f"- discovery question: {question['question']}")
        if experiment.get("external_id"):
            lines.append(f"- external job id: `{experiment['external_id']}`")
        if experiment.get("external_status"):
            lines.append(f"- external status: `{experiment['external_status']}`")
        lines.append(f"- objective: {experiment['objective']}")
        if experiment.get("rationale"):
            lines.append(f"- rationale: {experiment['rationale']}")
        if experiment.get("candidate_metadata", {}).get("campaign_priority"):
            lines.append(f"- campaign priority: {experiment['candidate_metadata']['campaign_priority']}")
        if experiment.get("candidate_metadata", {}).get("transfer_score"):
            lines.append(f"- transfer score: {experiment['candidate_metadata']['transfer_score']}")
        if experiment.get("outcome"):
            provider_result = experiment["outcome"]["provider_result"]
            evaluation = experiment["outcome"].get("evaluation")
            ingestion = experiment.get("ingestion") or {}
            if ingestion.get("signal_summary"):
                lines.append(f"- learned summary: {ingestion['signal_summary']}")
            if provider_result.get("new_signal_count") is not None:
                lines.append(f"- new signal count: {provider_result.get('new_signal_count', 0)}")
                lines.append(f"- reused signal count: {provider_result.get('reused_signal_count', 0)}")
            if provider_result.get("generated_lemmas"):
                lines.append("- generated lemmas:")
                for lemma in provider_result["generated_lemmas"]:
                    lines.append(f"  - `{lemma}`")
            if provider_result.get("proved_lemmas"):
                lines.append("- proved lemmas:")
                for lemma in provider_result["proved_lemmas"]:
                    lines.append(f"  - `{lemma}`")
            if provider_result.get("candidate_lemmas"):
                lines.append("- candidate lemmas:")
                for lemma in provider_result["candidate_lemmas"]:
                    lines.append(f"  - `{lemma}`")
            if provider_result.get("unresolved_goals"):
                lines.append("- unresolved goals:")
                for goal in provider_result["unresolved_goals"]:
                    lines.append(f"  - `{goal}`")
            if provider_result.get("blocked_on"):
                lines.append("- blocked on:")
                for item in provider_result["blocked_on"]:
                    lines.append(f"  - `{item}`")
            if provider_result.get("proof_trace_fragments"):
                lines.append("- proof traces:")
                for item in provider_result["proof_trace_fragments"][:5]:
                    lines.append(f"  - `{item}`")
            if provider_result.get("counterexample_witnesses"):
                lines.append("- counterexample witnesses:")
                for item in provider_result["counterexample_witnesses"][:5]:
                    lines.append(f"  - `{item}`")
            if provider_result.get("missing_assumptions") or provider_result.get("suspected_missing_assumptions"):
                lines.append("- suspected missing assumptions:")
                for assumption in provider_result.get("missing_assumptions") or provider_result.get("suspected_missing_assumptions") or []:
                    lines.append(f"  - `{assumption}`")
            if ingestion.get("artifact_inventory"):
                lines.append("- artifact inventory:")
                for artifact in ingestion["artifact_inventory"][:10]:
                    lines.append(
                        f"  - `{artifact['kind']}` `{artifact['path']}` ({artifact['size_bytes']} bytes)"
                    )
            if provider_result.get("artifacts"):
                lines.append("- artifacts:")
                for artifact in provider_result["artifacts"]:
                    lines.append(f"  - `{artifact}`")
            if evaluation is not None:
                lines.append(f"- evaluation total: {evaluation['total']}")
            lines.append(f"- notes: {provider_result.get('notes', '')}")
        lines.append("")
    lines.append("## Incidents")
    lines.append("")
    if incidents:
        for incident in incidents[:10]:
            lines.append(
                f"- `{incident['severity']}` `{incident['incident_type']}`: {incident['detail']}"
            )
    else:
        lines.append("- No open incidents.")
    lines.append("")
    lines.append("## Audit Trail")
    lines.append("")
    if audit_events:
        for event in audit_events:
            lines.append(f"- `{event['event_type']}` at `{event['created_at']}`")
    else:
        lines.append("- No audit events.")
    lines.append("")
    lines.append("## Control Plane Status")
    lines.append("")
    try:
        health_row = db.conn.execute(
            "SELECT payload_json, last_event_at, last_projection_at, manager_status FROM system_health_current WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if health_row:
            lines.append(f"- manager status: `{health_row['manager_status']}`")
            lines.append(f"- last event: `{health_row['last_event_at']}`")
            lines.append(f"- last projection: `{health_row['last_projection_at']}`")
        else:
            lines.append("- Control plane projections not yet initialized. Run `db-refresh-projections` to populate.")
        route_rows = db.conn.execute(
            "SELECT route_key, route_status, current_strength, recent_signal_velocity FROM route_strength_current WHERE project_id = ? ORDER BY current_strength DESC LIMIT 5",
            (project_id,),
        ).fetchall()
        if route_rows:
            lines.append("- top routes:")
            for route in route_rows:
                lines.append(
                    f"  - `{route['route_key']}` status=`{route['route_status']}` strength={route['current_strength']} velocity={route['recent_signal_velocity']}"
                )
    except Exception:
        lines.append("- Control plane projections unavailable (migration may not have run yet).")
    lines.append("")
    lines.append("## Latest manager decision")
    lines.append("")
    if latest_manager_run is not None:
        lines.append(f"- policy path: `{latest_manager_run['policy_path']}`")
        lines.append(f"- policy candidate audits: {len(db.list_manager_candidate_audits(latest_manager_run['run_id']))}")
        lines.append(f"- jobs synced: {latest_manager_run['jobs_synced']}")
        lines.append(f"- jobs submitted: {latest_manager_run['jobs_submitted']}")
        lines.append(f"- active before: {latest_manager_run['active_before']}")
        lines.append(f"- active after: {latest_manager_run['active_after']}")
        if latest_manager_run.get("report_path"):
            lines.append(f"- report path: `{latest_manager_run['report_path']}`")
        if latest_manager_run.get("snapshot_path"):
            lines.append(f"- snapshot path: `{latest_manager_run['snapshot_path']}`")
        recurring_structures = latest_manager_run["summary"].get("recurring_structures", {})
        if recurring_structures:
            lines.append(f"- recurring structures considered: lemmas={len(recurring_structures.get('lemmas', []))}, subgoals={len(recurring_structures.get('subgoals', []))}, traces={len(recurring_structures.get('proof_traces', []))}")
        signal_progress = latest_manager_run["summary"].get("signal_progress", {})
        if signal_progress:
            for item in signal_progress.get("latest_completed", []):
                lines.append(
                    f"- synced `{item['experiment_id']}` with proof_outcome=`{item['proof_outcome']}` new_signal={item['new_signal_count']} reused_signal={item['reused_signal_count']}"
                )
        for item in latest_manager_run["summary"].get("submitted_experiments", []):
            lines.append(
                f"- queued `{item['experiment_id']}` for `{item['conjecture_id']}` via `{item['move']}` / `{item.get('move_family', item['move'])}` ({item['reason']})"
            )
        for item in db.list_manager_candidate_audits(latest_manager_run["run_id"])[:5]:
            status = "selected" if item["selected"] else "considered"
            lines.append(
                f"- {status} `{item['experiment_id']}` rank={item['rank_position']} score={item['policy_score']}"
            )
        for item in latest_manager_run["summary"].get("skipped_candidates", []):
            if item.get("experiment_id"):
                lines.append(
                    f"- skipped `{item['experiment_id']}` for `{item['conjecture_id']}` ({item['reason']})"
                )
    else:
        lines.append("- No manager tick recorded yet.")
    lines.append("")
    lines.append("## Suggested next move")
    lines.append("")
    if latest_manager_run is not None and latest_manager_run["summary"].get("submitted_experiments"):
        lines.append("- Let the queued jobs advance, then run another manager tick to sync results and refill capacity.")
    elif recurring and recurring[0]["reuse_count"] >= charter.promotion_threshold:
        lines.append("- Promote the top recurring lemma into a standalone theorem if not already tested.")
    else:
        lines.append("- Continue assumption perturbation and equivalent reformulations to sharpen the boundary map.")
    lines.append("")
    return "\n".join(lines)


def write_report(db: Database, project_id: str, output_path: str | Path) -> None:
    text = build_report(db, project_id)
    Path(output_path).write_text(text, encoding="utf-8")
