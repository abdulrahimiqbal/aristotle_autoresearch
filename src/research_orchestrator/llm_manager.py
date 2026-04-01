from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict
from typing import Any, Dict, List, Sequence

from research_orchestrator.db import Database, utcnow
from research_orchestrator.schema_versions import PROMPT_TEMPLATE_VERSION
from research_orchestrator.types import (
    CampaignBrief,
    CampaignBriefSection,
    Conjecture,
    EvidenceRef,
)


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def feature_flags() -> Dict[str, bool]:
    return {
        "brief_generation": _env_flag("RESEARCH_ORCHESTRATOR_LLM_BRIEF_GENERATION", True),
    }


def llm_command() -> List[str]:
    raw = os.environ.get("RESEARCH_ORCHESTRATOR_LLM_MANAGER_COMMAND", "").strip()
    return raw.split() if raw else []


def llm_model_version() -> str:
    return os.environ.get("RESEARCH_ORCHESTRATOR_LLM_MANAGER_MODEL", "").strip() or "external-command"


def llm_prompt_version() -> str:
    return f"{PROMPT_TEMPLATE_VERSION}.manager-llm"


def run_llm_json(prompt: str) -> tuple[str, bool]:
    command = llm_command()
    if not command:
        return "", False
    completed = subprocess.run(
        command,
        input=prompt,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        output = completed.stdout + ("\n" + completed.stderr if completed.stderr else "")
        return output.strip(), False
    return completed.stdout.strip(), True


def _ref(ref_type: str, ref_id: str, label: str = "", *, conjecture_id: str = "", experiment_id: str = "", metadata: Dict[str, Any] | None = None) -> EvidenceRef:
    return EvidenceRef(
        ref_type=ref_type,
        ref_id=ref_id,
        label=label,
        conjecture_id=conjecture_id,
        experiment_id=experiment_id,
        metadata=metadata or {},
    )


def _top_refs(rows: Sequence[Dict[str, Any]], ref_type: str, label_key: str, count_key: str, *, conjecture_id: str = "", limit: int = 5) -> List[EvidenceRef]:
    refs: List[EvidenceRef] = []
    for item in rows[:limit]:
        refs.append(
            _ref(
                ref_type,
                str(item.get(label_key, "")),
                label=str(item.get(label_key, "")),
                conjecture_id=conjecture_id,
                metadata={"observations": item.get(count_key, 0)},
            )
        )
    return refs


def build_campaign_brief(
    db: Database,
    project_id: str,
    frontier: Sequence[Dict[str, Any]] | None = None,
) -> CampaignBrief:
    """Build a structured campaign brief from database state."""
    frontier = list(frontier or [])
    summary = db.project_summary(project_id)
    conjectures = db.list_conjectures(project_id)
    completed = db.list_completed_experiments(project_id, limit=12)
    recent_completed = sorted(
        completed,
        key=lambda item: (
            item.get("completed_at") or "",
            item.get("created_at") or "",
            item.get("experiment_id") or "",
        ),
        reverse=True,
    )[:8]
    recurring_lemmas = db.recurring_lemmas()[:8]
    recurring_subgoals = db.recurring_subgoals(project_id)[:8]
    recurring_traces = db.recurring_proof_traces(project_id)[:8]
    stale_branches = db.no_signal_branches(project_id)[:8]
    counterexamples = db.counterexample_summary(project_id)[:8]
    sensitivity = db.assumption_sensitivity(project_id)[:8]
    open_questions = db.list_discovery_questions(project_id, status="open")[:10]

    frontier_by_conjecture: Dict[str, int] = {}
    frontier_by_move_family: Dict[str, int] = {}
    for item in frontier:
        frontier_by_conjecture[item["conjecture_id"]] = frontier_by_conjecture.get(item["conjecture_id"], 0) + 1
        family = item.get("move_family", item.get("move", ""))
        frontier_by_move_family[family] = frontier_by_move_family.get(family, 0) + 1

    transfer_opportunities: List[Dict[str, Any]] = []
    for item in frontier:
        if float(item.get("transfer_opportunity", 0.0)) <= 0:
            continue
        transfer_opportunities.append(
            {
                "experiment_id": item["experiment_id"],
                "conjecture_id": item["conjecture_id"],
                "move_family": item.get("move_family", item["move"]),
                "transfer_opportunity": float(item.get("transfer_opportunity", 0.0)),
                "rationale": item.get("rationale", ""),
            }
        )
    transfer_opportunities.sort(
        key=lambda item: (-item["transfer_opportunity"], item["conjecture_id"], item["experiment_id"])
    )

    signal_velocity = round(
        sum((item.get("new_signal_count") or 0) + 0.35 * (item.get("reused_signal_count") or 0) for item in recent_completed)
        / max(1, len(recent_completed)),
        3,
    )

    evidence_pack = {
        "project_summary": summary,
        "frontier_summary": {
            "candidate_count": len(frontier),
            "by_conjecture": frontier_by_conjecture,
            "by_move_family": frontier_by_move_family,
        },
        "recurring_structures": {
            "lemmas": recurring_lemmas,
            "subgoals": recurring_subgoals,
            "proof_traces": recurring_traces,
        },
        "stale_branches": stale_branches,
        "boundary_map": {
            "counterexamples": counterexamples,
            "assumption_sensitivity": sensitivity,
        },
        "cross_conjecture_transfer": transfer_opportunities[:6],
        "recent_outcomes": [
            {
                "experiment_id": item["experiment_id"],
                "conjecture_id": item["conjecture_id"],
                "move": item["move"],
                "move_family": item.get("move_family", item["move"]),
                "proof_outcome": item.get("proof_outcome", ""),
                "new_signal_count": item.get("new_signal_count", 0),
                "reused_signal_count": item.get("reused_signal_count", 0),
                "signal_summary": item.get("signal_summary", ""),
            }
            for item in recent_completed
        ],
        "missing_experiments": open_questions,
    }

    sections = [
        CampaignBriefSection(
            title="frontier summary",
            summary=f"Frontier has {len(frontier)} candidates across {len(frontier_by_conjecture)} conjectures and {len(frontier_by_move_family)} move families.",
            refs=[_ref("candidate", item["experiment_id"], conjecture_id=item["conjecture_id"], experiment_id=item["experiment_id"]) for item in frontier[:6]],
            metadata=evidence_pack["frontier_summary"],
        ),
        CampaignBriefSection(
            title="dominant recurring motifs / structures",
            summary=(
                f"Recurring lemmas={len(recurring_lemmas)}, subgoals={len(recurring_subgoals)}, proof traces={len(recurring_traces)}."
            ),
            refs=_top_refs(recurring_lemmas, "lemma", "representative_statement", "reuse_count")
            + _top_refs(recurring_subgoals, "subgoal", "statement", "observations")
            + _top_refs(recurring_traces, "proof_trace", "fragment", "observations"),
        ),
        CampaignBriefSection(
            title="stale branches",
            summary=f"{len(stale_branches)} branches have repeated no-signal outcomes above threshold.",
            refs=[
                _ref(
                    "branch",
                    f"{item['conjecture_id']}::{item['move']}",
                    label=f"{item['conjecture_id']}::{item['move']}",
                    conjecture_id=item["conjecture_id"],
                    metadata={"observations": item["observations"]},
                )
                for item in stale_branches[:6]
            ],
        ),
        CampaignBriefSection(
            title="missing experiments / gaps",
            summary=f"{len(open_questions)} open discovery questions remain; {sum(1 for item in conjectures if frontier_by_conjecture.get(item.conjecture_id, 0) == 0)} conjectures currently have no frontier coverage.",
            refs=[
                _ref("discovery_question", item["question_id"], label=item["question"], conjecture_id=item["conjecture_id"])
                for item in open_questions[:6]
            ],
        ),
        CampaignBriefSection(
            title="boundary map / witness signals",
            summary=f"Counterexample witnesses={len(counterexamples)}; sensitive assumptions={len(sensitivity)}.",
            refs=_top_refs(counterexamples, "counterexample", "witness", "observations")
            + _top_refs(sensitivity, "assumption", "assumption_name", "observations"),
        ),
        CampaignBriefSection(
            title="cross-conjecture transfer opportunities",
            summary=f"{len(transfer_opportunities)} frontier candidates already expose transfer-style opportunities.",
            refs=[
                _ref("candidate", item["experiment_id"], label=item["move_family"], conjecture_id=item["conjecture_id"], experiment_id=item["experiment_id"])
                for item in transfer_opportunities[:6]
            ],
        ),
        CampaignBriefSection(
            title="recent experiment outcomes and signal velocity",
            summary=f"Recent signal velocity={signal_velocity}; recent completed runs={len(recent_completed)}.",
            refs=[
                _ref("experiment", item["experiment_id"], label=item.get("signal_summary", ""), conjecture_id=item["conjecture_id"], experiment_id=item["experiment_id"])
                for item in recent_completed[:6]
            ],
            metadata={"recent_signal_velocity": signal_velocity},
        ),
    ]
    return CampaignBrief(
        project_id=project_id,
        generated_at=utcnow(),
        phase_estimate="discovery",
        evidence_pack=evidence_pack,
        narrative_summary=sections,
    )


def render_campaign_brief(brief: CampaignBrief) -> Dict[str, Any]:
    return {
        "project_id": brief.project_id,
        "generated_at": brief.generated_at,
        "phase_estimate": brief.phase_estimate,
        "evidence_pack": brief.evidence_pack,
        "narrative_summary": [
            {
                "title": section.title,
                "summary": section.summary,
                "refs": [asdict(ref) for ref in section.refs],
                "metadata": section.metadata,
            }
            for section in brief.narrative_summary
        ],
    }
