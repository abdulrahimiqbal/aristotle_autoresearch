from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Sequence

from research_orchestrator.db import Database, utcnow
from research_orchestrator.move_registry import DEFAULT_MOVE_REGISTRY, MoveCandidate
from research_orchestrator.prompts import build_project_constitution
from research_orchestrator.schema_versions import PROMPT_TEMPLATE_VERSION
from research_orchestrator.types import (
    BranchAssessment,
    BridgeHypothesis,
    CampaignBrief,
    CampaignBriefSection,
    CampaignInterpretation,
    CandidateAnnotation,
    Conjecture,
    EvidenceRef,
    GapDescription,
    MotifAssessment,
    SynthesizedMoveParameters,
)


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def feature_flags() -> Dict[str, bool]:
    return {
        "brief_generation": _env_flag("RESEARCH_ORCHESTRATOR_LLM_BRIEF_GENERATION", True),
        "interpretation": _env_flag("RESEARCH_ORCHESTRATOR_LLM_INTERPRETATION", False),
        "annotation": _env_flag("RESEARCH_ORCHESTRATOR_LLM_CANDIDATE_ANNOTATION", False),
        "parameter_synthesis": _env_flag("RESEARCH_ORCHESTRATOR_LLM_PARAMETER_SYNTHESIS", False),
        "bridge_hypotheses": _env_flag("RESEARCH_ORCHESTRATOR_LLM_BRIDGE_HYPOTHESES", False),
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


def _safe_json_loads(raw_response: str) -> Any:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return None


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


def _phase_estimate(num_experiments: int) -> str:
    if num_experiments == 0:
        return "mapping"
    if num_experiments < 3:
        return "excavation"
    if num_experiments < 5:
        return "stress_testing"
    return "consolidation"


def build_campaign_brief(
    db: Database,
    project_id: str,
    frontier: Sequence[Dict[str, Any]] | None = None,
) -> CampaignBrief:
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
            title="current phase / phase estimate",
            summary=f"Estimated phase: {_phase_estimate(summary.get('num_experiments', 0))}; experiments={summary.get('num_experiments', 0)}; pending={summary.get('pending', 0)}.",
            refs=[_ref("project", project_id, label=summary.get("campaign_title", ""))],
            metadata={"phase_estimate": _phase_estimate(summary.get("num_experiments", 0))},
        ),
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
        phase_estimate=_phase_estimate(summary.get("num_experiments", 0)),
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


def null_interpretation() -> CampaignInterpretation:
    return CampaignInterpretation(phase_assessment="heuristic_only", confidence=0.0)


def _llm_prompt(header: str, charter, brief_payload: Dict[str, Any], extra: str) -> str:
    return (
        f"{build_project_constitution(charter)}\n\n"
        f"{header}\n"
        f"Prompt template version: {llm_prompt_version()}\n\n"
        f"Campaign brief:\n{json.dumps(brief_payload, indent=2)}\n\n"
        f"{extra}\n"
    ).strip()


def _parse_ref_list(payload: Any) -> List[EvidenceRef]:
    refs: List[EvidenceRef] = []
    if not isinstance(payload, list):
        return refs
    for item in payload:
        if not isinstance(item, dict):
            continue
        ref_type = str(item.get("ref_type", "")).strip()
        ref_id = str(item.get("ref_id", "")).strip()
        if not ref_type or not ref_id:
            continue
        refs.append(
            EvidenceRef(
                ref_type=ref_type,
                ref_id=ref_id,
                label=str(item.get("label", "")),
                conjecture_id=str(item.get("conjecture_id", "")),
                experiment_id=str(item.get("experiment_id", "")),
                metadata=dict(item.get("metadata", {})) if isinstance(item.get("metadata"), dict) else {},
            )
        )
    return refs


def _bounded_float(value: Any, minimum: float, maximum: float) -> float:
    if not isinstance(value, (int, float)):
        return minimum
    return round(max(minimum, min(maximum, float(value))), 3)


def interpret_campaign(
    db: Database,
    project_id: str,
    brief: CampaignBrief,
) -> tuple[CampaignInterpretation, Dict[str, Any]]:
    charter = db.get_charter(project_id)
    prompt = _llm_prompt(
        "Produce a structured campaign interpretation. Use only the supplied evidence. Do not suggest executing anything.",
        charter,
        render_campaign_brief(brief),
        (
            "Return valid JSON with keys: phase_assessment, confidence, observed_vs_inferred, evidence_refs, "
            "dominant_motifs, cross_conjecture_bridges, stale_branches, missing_experiments. "
            "You may also include manager_reasoning as a concise explicit reasoning trace grounded in the supplied evidence.\n"
            "Each dominant_motifs item needs motif_id, summary, confidence, observed_vs_inferred, evidence_refs.\n"
            "Each cross_conjecture_bridges item needs source_conjecture_id, target_conjecture_id, shared_structure, "
            "transfer_rationale, suggested_move_family, confidence, source_evidence, evidence_refs.\n"
            "Each stale_branches item needs conjecture_id, move_family, summary, status, confidence, observed_vs_inferred, evidence_refs.\n"
            "Each missing_experiments item needs conjecture_id, category, description, confidence, observed_vs_inferred, evidence_refs."
        ),
    )
    raw_response, success = run_llm_json(prompt)
    parsed = _safe_json_loads(raw_response) if success else None
    if not isinstance(parsed, dict):
        interpretation = null_interpretation()
        return interpretation, {
            "prompt_version": llm_prompt_version(),
            "model_version": llm_model_version(),
            "raw_response": raw_response,
            "parsed": {},
            "validation_status": "invalid_json",
        }

    interpretation = CampaignInterpretation(
        phase_assessment=str(parsed.get("phase_assessment", "heuristic_only")),
        confidence=_bounded_float(parsed.get("confidence", 0.0), 0.0, 1.0),
        observed_vs_inferred=str(parsed.get("observed_vs_inferred", "observed")),
        evidence_refs=_parse_ref_list(parsed.get("evidence_refs")),
        dominant_motifs=[
            MotifAssessment(
                motif_id=str(item.get("motif_id", "")),
                summary=str(item.get("summary", "")),
                confidence=_bounded_float(item.get("confidence", 0.0), 0.0, 1.0),
                observed_vs_inferred=str(item.get("observed_vs_inferred", "observed")),
                evidence_refs=_parse_ref_list(item.get("evidence_refs")),
            )
            for item in parsed.get("dominant_motifs", [])
            if isinstance(item, dict) and item.get("motif_id") and item.get("summary")
        ],
        cross_conjecture_bridges=[
            BridgeHypothesis(
                source_conjecture_id=str(item.get("source_conjecture_id", "")),
                target_conjecture_id=str(item.get("target_conjecture_id", "")),
                shared_structure=str(item.get("shared_structure", "")),
                transfer_rationale=str(item.get("transfer_rationale", "")),
                suggested_move_family=str(item.get("suggested_move_family", "transfer_reformulation")),
                confidence=_bounded_float(item.get("confidence", 0.0), 0.0, 1.0),
                source_evidence=_parse_ref_list(item.get("source_evidence")),
                evidence_refs=_parse_ref_list(item.get("evidence_refs")),
            )
            for item in parsed.get("cross_conjecture_bridges", [])
            if isinstance(item, dict)
            and item.get("source_conjecture_id")
            and item.get("target_conjecture_id")
            and item.get("shared_structure")
        ],
        stale_branches=[
            BranchAssessment(
                conjecture_id=str(item.get("conjecture_id", "")),
                move_family=str(item.get("move_family", "")),
                summary=str(item.get("summary", "")),
                status=str(item.get("status", "active")),
                confidence=_bounded_float(item.get("confidence", 0.0), 0.0, 1.0),
                observed_vs_inferred=str(item.get("observed_vs_inferred", "observed")),
                evidence_refs=_parse_ref_list(item.get("evidence_refs")),
            )
            for item in parsed.get("stale_branches", [])
            if isinstance(item, dict) and item.get("conjecture_id") and item.get("move_family")
        ],
        missing_experiments=[
            GapDescription(
                conjecture_id=str(item.get("conjecture_id", "")),
                category=str(item.get("category", "")),
                description=str(item.get("description", "")),
                confidence=_bounded_float(item.get("confidence", 0.0), 0.0, 1.0),
                observed_vs_inferred=str(item.get("observed_vs_inferred", "observed")),
                evidence_refs=_parse_ref_list(item.get("evidence_refs")),
            )
            for item in parsed.get("missing_experiments", [])
            if isinstance(item, dict) and item.get("conjecture_id") and item.get("description")
        ],
    )
    if not interpretation.phase_assessment:
        interpretation = null_interpretation()
        validation_status = "missing_phase"
    else:
        validation_status = "valid"
    return interpretation, {
        "prompt_version": llm_prompt_version(),
        "model_version": llm_model_version(),
        "raw_response": raw_response,
        "parsed": parsed,
        "validation_status": validation_status,
    }


def annotate_frontier(
    charter,
    brief: CampaignBrief,
    interpretation: CampaignInterpretation,
    frontier: Sequence[Dict[str, Any]],
) -> tuple[Dict[str, CandidateAnnotation], Dict[str, Any]]:
    prompt = _llm_prompt(
        "Annotate frontier candidates for bounded ranking assistance. Do not remove candidates and do not override hard constraints.",
        charter,
        {
            "brief": render_campaign_brief(brief),
            "interpretation": asdict(interpretation),
            "frontier": list(frontier),
        },
        (
            "Return valid JSON with key annotations. annotations must be a list of objects with keys: "
            "experiment_id, mathematical_rationale, connects_to_motif, expected_discovery, expected_failure_signal, "
            "phase_alignment, failure_value, llm_delta, confidence, evidence_refs. "
            "phase_alignment and failure_value must be in [0,1]. llm_delta must be in [-2,2]. "
            "You may also include manager_reasoning as a concise explicit reasoning trace."
        ),
    )
    raw_response, success = run_llm_json(prompt)
    parsed = _safe_json_loads(raw_response) if success else None
    if not isinstance(parsed, dict):
        return {}, {
            "prompt_version": llm_prompt_version(),
            "model_version": llm_model_version(),
            "raw_response": raw_response,
            "parsed": {},
            "validation_status": "invalid_json",
        }

    known_ids = {item["experiment_id"] for item in frontier}
    annotations: Dict[str, CandidateAnnotation] = {}
    for item in parsed.get("annotations", []):
        if not isinstance(item, dict):
            continue
        experiment_id = str(item.get("experiment_id", ""))
        if experiment_id not in known_ids:
            continue
        annotations[experiment_id] = CandidateAnnotation(
            experiment_id=experiment_id,
            mathematical_rationale=str(item.get("mathematical_rationale", "")),
            connects_to_motif=str(item.get("connects_to_motif", "")),
            expected_discovery=str(item.get("expected_discovery", "")),
            expected_failure_signal=str(item.get("expected_failure_signal", "")),
            phase_alignment=_bounded_float(item.get("phase_alignment", 0.0), 0.0, 1.0),
            failure_value=_bounded_float(item.get("failure_value", 0.0), 0.0, 1.0),
            llm_delta=_bounded_float(item.get("llm_delta", 0.0), -2.0, 2.0),
            confidence=_bounded_float(item.get("confidence", 0.0), 0.0, 1.0),
            evidence_refs=_parse_ref_list(item.get("evidence_refs")),
        )
    return annotations, {
        "prompt_version": llm_prompt_version(),
        "model_version": llm_model_version(),
        "raw_response": raw_response,
        "parsed": parsed,
        "validation_status": "valid" if annotations else "empty",
    }


def _validate_parameter_types(reference: Dict[str, Any], proposed: Dict[str, Any]) -> bool:
    if set(reference) != set(proposed):
        return False
    for key, value in proposed.items():
        ref_value = reference.get(key)
        if ref_value is None:
            continue
        if isinstance(ref_value, bool):
            if not isinstance(value, bool):
                return False
            continue
        if isinstance(ref_value, int) and not isinstance(ref_value, bool):
            if not isinstance(value, int) or isinstance(value, bool):
                return False
            continue
        if isinstance(ref_value, float):
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
            continue
        if type(value) is not type(ref_value):
            return False
    return True


def synthesize_parameters(
    charter,
    brief: CampaignBrief,
    interpretation: CampaignInterpretation,
    frontier: Sequence[Dict[str, Any]],
) -> tuple[Dict[str, SynthesizedMoveParameters], Dict[str, Any]]:
    prompt = _llm_prompt(
        "Propose improved parameters only for existing move families already present in the frontier.",
        charter,
        {
            "brief": render_campaign_brief(brief),
            "interpretation": asdict(interpretation),
            "frontier": list(frontier),
        },
        (
            "Return valid JSON with key syntheses. syntheses must be a list of objects with keys: "
            "experiment_id, move_family, parameters, rationale, source_evidence. "
            "Do not invent new move families. Use the exact parameter keys already required by the move family. "
            "You may also include manager_reasoning as a concise explicit reasoning trace."
        ),
    )
    raw_response, success = run_llm_json(prompt)
    parsed = _safe_json_loads(raw_response) if success else None
    if not isinstance(parsed, dict):
        return {}, {
            "prompt_version": llm_prompt_version(),
            "model_version": llm_model_version(),
            "raw_response": raw_response,
            "parsed": {},
            "validation_status": "invalid_json",
        }
    candidate_by_id = {item["experiment_id"]: item for item in frontier}
    accepted: Dict[str, SynthesizedMoveParameters] = {}
    for item in parsed.get("syntheses", []):
        if not isinstance(item, dict):
            continue
        experiment_id = str(item.get("experiment_id", ""))
        candidate = candidate_by_id.get(experiment_id)
        if candidate is None:
            continue
        move_family = str(item.get("move_family", ""))
        parameters = item.get("parameters")
        if move_family != candidate.get("move_family", candidate.get("move", "")):
            continue
        if not isinstance(parameters, dict):
            continue
        spec = DEFAULT_MOVE_REGISTRY.get(move_family)
        if set(parameters) != set(spec.parameter_keys):
            continue
        if not _validate_parameter_types(candidate.get("modification", {}), parameters):
            continue
        evidence = _parse_ref_list(item.get("source_evidence"))
        if parameters != candidate.get("modification", {}) and not evidence:
            continue
        accepted[experiment_id] = SynthesizedMoveParameters(
            move_family=move_family,
            parameters=parameters,
            rationale=str(item.get("rationale", "")),
            source_evidence=evidence,
        )
    return accepted, {
        "prompt_version": llm_prompt_version(),
        "model_version": llm_model_version(),
        "raw_response": raw_response,
        "parsed": parsed,
        "validation_status": "valid" if accepted else "empty",
    }


def validate_bridge_hypotheses(hypotheses: Iterable[BridgeHypothesis], conjectures: Sequence[Conjecture]) -> List[BridgeHypothesis]:
    known = {item.conjecture_id for item in conjectures}
    valid: List[BridgeHypothesis] = []
    for item in hypotheses:
        if item.source_conjecture_id not in known or item.target_conjecture_id not in known:
            continue
        if item.source_conjecture_id == item.target_conjecture_id:
            continue
        if item.suggested_move_family != "transfer_reformulation":
            continue
        if not item.shared_structure or not item.source_evidence:
            continue
        valid.append(item)
    return valid


def build_bridge_candidate(hypothesis: BridgeHypothesis) -> MoveCandidate:
    artifact = ""
    for ref in hypothesis.source_evidence:
        if ref.label:
            artifact = ref.label
            break
    if not artifact:
        artifact = hypothesis.shared_structure
    return MoveCandidate(
        move_family="transfer_reformulation",
        legacy_move="reformulate",
        parameters={
            "source_conjecture_id": hypothesis.source_conjecture_id,
            "source_domain": hypothesis.source_evidence[0].metadata.get("source_domain", hypothesis.source_conjecture_id),
            "artifact": artifact,
        },
        objective=f"Fill in all sorries. Test whether the shared structure '{hypothesis.shared_structure}' transfers from {hypothesis.source_conjecture_id}.",
        expected_signal="Probe whether a bridgeable structural analogy can be turned into reusable transfer signal.",
        rationale=hypothesis.transfer_rationale,
        novelty_score=1.0,
        reuse_potential=1.0,
        transfer_score=max(1.2, round(hypothesis.confidence * 2.0, 3)),
        diversity_group="transfer",
        generation_metadata={
            "bridge_hypothesis": asdict(hypothesis),
            "campaign_priority": round(hypothesis.confidence, 3),
        },
    )
