from __future__ import annotations

from pathlib import Path

from research_orchestrator.db import Database


def build_report(db: Database, project_id: str) -> str:
    charter = db.get_charter(project_id)
    summary = db.project_summary(project_id)
    experiments = db.list_experiments(project_id)
    active = db.list_active_experiments(project_id)
    recent_completed = db.list_completed_experiments(project_id, limit=5)
    recurring = db.recurring_lemmas()
    recurring_subgoals = db.recurring_subgoals(project_id)
    blocker_summary = db.blocker_summary(project_id)
    sensitivity = db.assumption_sensitivity(project_id)
    latest_manager_run = db.latest_manager_run(project_id)

    lines = []
    lines.append(f"# Research Report: {charter.title}")
    lines.append("")
    lines.append(f"**Project ID:** `{charter.project_id}`")
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
    lines.append("## Active jobs")
    lines.append("")
    if active:
        for item in summary.get("active_by_external_status", []):
            lines.append(f"- `{item['external_status']}`: {item['count']}")
    else:
        lines.append("- None active.")
    lines.append("")
    lines.append("## Recently completed")
    lines.append("")
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
        lines.append(f"- phase: `{experiment['phase']}`")
        lines.append(f"- status: `{experiment['status']}`")
        if experiment.get("proof_outcome"):
            lines.append(f"- proof outcome: `{experiment['proof_outcome']}`")
        lines.append(f"- blocker: `{experiment['blocker_type']}`")
        if experiment.get("external_id"):
            lines.append(f"- external job id: `{experiment['external_id']}`")
        if experiment.get("external_status"):
            lines.append(f"- external status: `{experiment['external_status']}`")
        lines.append(f"- objective: {experiment['objective']}")
        if experiment.get("outcome"):
            provider_result = experiment["outcome"]["provider_result"]
            evaluation = experiment["outcome"].get("evaluation")
            ingestion = experiment.get("ingestion") or {}
            if ingestion.get("signal_summary"):
                lines.append(f"- learned summary: {ingestion['signal_summary']}")
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
    lines.append("## Latest manager decision")
    lines.append("")
    if latest_manager_run is not None:
        lines.append(f"- policy path: `{latest_manager_run['policy_path']}`")
        lines.append(f"- jobs synced: {latest_manager_run['jobs_synced']}")
        lines.append(f"- jobs submitted: {latest_manager_run['jobs_submitted']}")
        lines.append(f"- active before: {latest_manager_run['active_before']}")
        lines.append(f"- active after: {latest_manager_run['active_after']}")
        if latest_manager_run.get("report_path"):
            lines.append(f"- report path: `{latest_manager_run['report_path']}`")
        if latest_manager_run.get("snapshot_path"):
            lines.append(f"- snapshot path: `{latest_manager_run['snapshot_path']}`")
        for item in latest_manager_run["summary"].get("submitted_experiments", []):
            lines.append(
                f"- queued `{item['experiment_id']}` for `{item['conjecture_id']}` via `{item['move']}` ({item['reason']})"
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
