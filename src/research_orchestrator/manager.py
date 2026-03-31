from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from typing import Any, Dict, List

from research_orchestrator.db import Database
from research_orchestrator.experiment_generator import generate_move_candidates, materialize_candidate
from research_orchestrator.llm_manager import (
    annotate_frontier,
    build_bridge_candidate,
    build_campaign_brief,
    feature_flags,
    interpret_campaign,
    null_interpretation,
    render_campaign_brief,
    synthesize_parameters,
    validate_bridge_hypotheses,
)
from research_orchestrator.move_registry import MoveCandidate
from research_orchestrator.prompts import build_manager_prompt


MOVE_PRIORITY = {
    "underspecify": 0,
    "perturb_assumption": 1,
    "promote_lemma": 2,
    "promote_subgoal": 3,
    "promote_trace": 4,
    "reformulate": 5,
    "boundary_map_from_witness": 6,
    "boundary_map_from_missing_assumption": 7,
    "counterexample_mode": 8,
}


def _counts_by_conjecture(conjectures, experiments):
    counts = {conjecture.conjecture_id: 0 for conjecture in conjectures}
    for experiment in experiments:
        conjecture_id = experiment["conjecture_id"]
        if conjecture_id in counts:
            counts[conjecture_id] += 1
    return counts


def _has_seeded_structure(conjecture) -> bool:
    return any(
        conjecture.family_metadata.get(key)
        for key in (
            "seed_invariants",
            "seed_subclaims",
            "seed_extremal_targets",
            "seed_adversarial_targets",
            "seed_witness_targets",
            "seed_transfer_hints",
            "seed_discovery_questions",
        )
    )


def _manager_candidate_slice(conjecture, experiments, move_candidates):
    conjecture_experiments = [item for item in experiments if item["conjecture_id"] == conjecture.conjecture_id]
    effective_moves = {
        item["move"]
        for item in conjecture_experiments
        if item.get("proof_outcome") not in {"unknown", "auth_failure", "infra_failure", "malformed"}
        or (item.get("new_signal_count") or 0) > 0
    }
    tested_assumptions = {
        item["modification"].get("assumption")
        for item in conjecture_experiments
        if item["move"] == "perturb_assumption" and item.get("modification", {}).get("assumption")
    }
    if not conjecture_experiments and not _has_seeded_structure(conjecture):
        initial = [candidate for candidate in move_candidates if candidate.legacy_move == "underspecify"]
        return initial[:1] if initial else move_candidates
    if "underspecify" in effective_moves and not tested_assumptions:
        high_value_nonperturb = [
            candidate
            for candidate in move_candidates
            if candidate.legacy_move != "perturb_assumption" and candidate.transfer_score > 0
        ]
        if high_value_nonperturb:
            return move_candidates
        perturb = [candidate for candidate in move_candidates if candidate.legacy_move == "perturb_assumption"]
        if perturb:
            return perturb
    return move_candidates


def _candidate_payload(candidate, conjecture_id, project_id, existing_experiments, discovery_priority):
    metadata = candidate.candidate_metadata
    return {
        "experiment_id": candidate.experiment_id,
        "project_id": project_id,
        "conjecture_id": conjecture_id,
        "existing_experiments": existing_experiments,
        "phase": candidate.phase,
        "move": candidate.move,
        "move_family": candidate.move_family or candidate.move,
        "theorem_family_id": candidate.theorem_family_id,
        "move_title": candidate.move_title or candidate.move_family or candidate.move,
        "objective": candidate.objective,
        "expected_signal": candidate.expected_signal,
        "modification": candidate.modification,
        "workspace_dir": candidate.workspace_dir,
        "lean_file": candidate.lean_file,
        "rationale": candidate.rationale,
        "candidate_metadata": metadata,
        "discovery_question_id": candidate.discovery_question_id,
        "discovery_question": candidate.discovery_question,
        "discovery_priority": discovery_priority,
        "motif_id": metadata.get("motif_id", ""),
        "motif_signature": metadata.get("motif_signature", ""),
        "motif_reuse_count": metadata.get("motif_reuse_count", 0),
        "signal_support": metadata.get("signal_support", 0),
        "blocker_support": metadata.get("blocker_support", 0),
        "witness_support": metadata.get("witness_support", 0),
        "assumption_boundary_support": metadata.get("assumption_boundary_support", 0),
        "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
    }


def _frontier_sort_key(item: Dict[str, object]):
    metadata = item.get("candidate_metadata", {})
    return (
        item.get("existing_experiments", 0),
        -item.get("discovery_priority", 0),
        -item.get("recent_signal_velocity", 0),
        -item.get("motif_reuse_count", 0),
        MOVE_PRIORITY.get(item.get("move", ""), 99),
        -metadata.get("campaign_priority", 0),
        -metadata.get("transfer_score", 0),
        -metadata.get("reuse_potential", 0),
        -metadata.get("obstruction_targeting", 0),
        -metadata.get("novelty_score", 0),
        -item.get("signal_support", 0),
        item.get("conjecture_id", ""),
        item.get("move_family", ""),
    )


def _runtime_context(db: Database, project_id: str) -> Dict[str, Any]:
    conjectures = db.list_conjectures(project_id)
    experiments = db.list_experiments(project_id)
    open_questions = db.list_discovery_questions(project_id, status="open")
    questions_by_conjecture: Dict[str, List[Dict[str, Any]]] = {}
    for question in open_questions:
        questions_by_conjecture.setdefault(question["conjecture_id"], []).append(question)
    return {
        "charter": db.get_charter(project_id),
        "conjectures": conjectures,
        "experiments": experiments,
        "counts": _counts_by_conjecture(conjectures, experiments),
        "recurring": db.recurring_lemmas(),
        "recurring_subgoals": db.recurring_subgoals(project_id),
        "recurring_proof_traces": db.recurring_proof_traces(project_id),
        "questions_by_conjecture": questions_by_conjecture,
    }


def _materialize_payload(
    project_id: str,
    workspace_root: str,
    conjecture,
    move_candidate: MoveCandidate,
    runtime: Dict[str, Any],
) -> Dict[str, Any]:
    brief = materialize_candidate(
        charter=runtime["charter"],
        conjecture=conjecture,
        workspace_root=workspace_root,
        experiments=runtime["experiments"],
        candidate=move_candidate,
        discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
    )
    payload = _candidate_payload(
        brief,
        conjecture.conjecture_id,
        project_id,
        runtime["counts"].get(conjecture.conjecture_id, 0),
        0,
    )
    payload["_frontier_candidate"] = {
        "conjecture_id": conjecture.conjecture_id,
        "move_candidate": move_candidate,
        "brief": brief,
    }
    return payload


def _strip_frontier_internal_fields(frontier: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for item in frontier:
        payload = dict(item)
        payload.pop("_frontier_candidate", None)
        cleaned.append(payload)
    return cleaned


def _annotate_runtime_fields(frontier: List[Dict[str, Any]], active: List[Dict[str, Any]], no_signal: Dict[tuple[str, str], int], active_counts: Dict[str, int]) -> None:
    active_signatures = {
        (
            item["conjecture_id"],
            item["move"],
            json.dumps(item["modification"], sort_keys=True),
        )
        for item in active
    }
    for payload in frontier:
        metadata = payload["candidate_metadata"]
        signature = (
            payload["conjecture_id"],
            payload["move"],
            json.dumps(payload["modification"], sort_keys=True),
        )
        payload.update(
            {
                "active_count_for_conjecture": active_counts.get(payload["conjecture_id"], 0),
                "duplicate_active_signature": signature in active_signatures,
                "targets_recurring_structure": payload["move_family"] in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"},
                "signal_priority": 2 if payload["move_family"] in {"legacy.promote_lemma", "decompose_subclaim", "invariant_mining"} else 1 if payload["move"] == "reformulate" else 0,
                "no_signal_penalty": no_signal.get((payload["conjecture_id"], payload["move"]), 0) + metadata.get("no_signal_penalty", 0),
                "semantic_novelty": metadata.get("novelty_score", 0),
                "reuse_potential": metadata.get("reuse_potential", 0),
                "obstruction_targeting": metadata.get("obstruction_targeting", 0),
                "transfer_opportunity": metadata.get("transfer_score", 0),
                "campaign_priority": metadata.get("campaign_priority", 0),
                "motif_id": metadata.get("motif_id", ""),
                "motif_reuse_count": metadata.get("motif_reuse_count", 0),
                "signal_support": metadata.get("signal_support", 0),
                "blocker_support": metadata.get("blocker_support", 0),
                "witness_support": metadata.get("witness_support", 0),
                "assumption_boundary_support": metadata.get("assumption_boundary_support", 0),
                "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
            }
        )


def _rebuild_payload(payload: Dict[str, Any], synthesis, project_id: str, workspace_root: str, runtime: Dict[str, Any]) -> Dict[str, Any]:
    conjecture = next(item for item in runtime["conjectures"] if item.conjecture_id == payload["_frontier_candidate"]["conjecture_id"])
    original_candidate = payload["_frontier_candidate"]["move_candidate"]
    rebuilt_candidate = MoveCandidate(
        move_family=original_candidate.move_family,
        legacy_move=original_candidate.legacy_move,
        parameters=dict(synthesis.parameters),
        objective=original_candidate.objective,
        expected_signal=original_candidate.expected_signal,
        rationale=original_candidate.rationale,
        novelty_score=original_candidate.novelty_score,
        reuse_potential=original_candidate.reuse_potential,
        obstruction_targeting=original_candidate.obstruction_targeting,
        diversity_group=original_candidate.diversity_group,
        duplicate_penalty=original_candidate.duplicate_penalty,
        no_signal_penalty=original_candidate.no_signal_penalty,
        transfer_score=original_candidate.transfer_score,
        generation_metadata={
            **original_candidate.generation_metadata,
            "llm_parameter_synthesis": asdict(synthesis),
        },
    )
    shutil.rmtree(payload["_frontier_candidate"]["brief"].workspace_dir, ignore_errors=True)
    rebuilt = _materialize_payload(project_id, workspace_root, conjecture, rebuilt_candidate, runtime)
    rebuilt["candidate_metadata"]["llm_parameter_synthesis"] = asdict(synthesis)
    rebuilt["candidate_metadata"]["original_experiment_id"] = payload["experiment_id"]
    return rebuilt


def _apply_llm_enrichment(db: Database, project_id: str, workspace_root: str, frontier: List[Dict[str, Any]], runtime: Dict[str, Any]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    flags = feature_flags()
    artifacts: Dict[str, Any] = {"brief": None, "interpretation": None, "bridge_hypotheses": []}
    if not frontier or not flags["brief_generation"]:
        return frontier, artifacts

    clean_frontier = _strip_frontier_internal_fields(frontier)
    brief = build_campaign_brief(db, project_id, frontier=clean_frontier)
    artifacts["brief"] = render_campaign_brief(brief)
    interpretation = null_interpretation()

    if flags["interpretation"]:
        interpretation, record = interpret_campaign(db, project_id, brief)
        interpretation_id = db.save_campaign_interpretation(
            project_id=project_id,
            prompt_version=record["prompt_version"],
            model_version=record["model_version"],
            raw_response=record["raw_response"],
            parsed=record["parsed"],
            validation_status=record["validation_status"],
        )
        artifacts["interpretation"] = {"interpretation_id": interpretation_id, **asdict(interpretation)}

    if flags["annotation"]:
        annotations, _ = annotate_frontier(runtime["charter"], brief, interpretation, clean_frontier)
        for payload in frontier:
            annotation = annotations.get(payload["experiment_id"])
            if annotation is None:
                continue
            payload["llm_annotation"] = asdict(annotation)
            payload["candidate_metadata"]["llm_annotation"] = asdict(annotation)

    if flags["parameter_synthesis"]:
        syntheses, _ = synthesize_parameters(runtime["charter"], brief, interpretation, clean_frontier)
        if syntheses:
            frontier = [
                _rebuild_payload(payload, syntheses[payload["experiment_id"]], project_id, workspace_root, runtime)
                if payload["experiment_id"] in syntheses
                else payload
                for payload in frontier
            ]
            clean_frontier = _strip_frontier_internal_fields(frontier)

    if flags["bridge_hypotheses"] and interpretation.cross_conjecture_bridges:
        bridges = validate_bridge_hypotheses(interpretation.cross_conjecture_bridges, runtime["conjectures"])
        if bridges:
            db.save_bridge_hypotheses(project_id, [asdict(item) for item in bridges])
            artifacts["bridge_hypotheses"] = [asdict(item) for item in bridges]
            existing_signatures = {
                (
                    item["conjecture_id"],
                    item.get("move_family", item["move"]),
                    json.dumps(item["modification"], sort_keys=True),
                )
                for item in clean_frontier
            }
            for bridge in bridges:
                conjecture = next((item for item in runtime["conjectures"] if item.conjecture_id == bridge.target_conjecture_id), None)
                if conjecture is None:
                    continue
                candidate = build_bridge_candidate(bridge)
                signature = (
                    conjecture.conjecture_id,
                    candidate.move_family,
                    json.dumps(candidate.parameters, sort_keys=True),
                )
                if signature in existing_signatures:
                    continue
                payload = _materialize_payload(project_id, workspace_root, conjecture, candidate, runtime)
                payload["candidate_metadata"]["bridge_hypothesis"] = asdict(bridge)
                frontier.append(payload)

    return frontier, artifacts


def choose_next_experiment(db: Database, project_id: str, workspace_root: str):
    runtime = _runtime_context(db, project_id)
    frontier: List[Dict[str, Any]] = []
    generated_candidates: Dict[str, List[MoveCandidate]] = {}
    for conjecture in runtime["conjectures"]:
        move_candidates = generate_move_candidates(
            charter=runtime["charter"],
            conjecture=conjecture,
            experiments=runtime["experiments"],
            recurring_lemmas=runtime["recurring"],
            recurring_subgoals=runtime["recurring_subgoals"],
            recurring_proof_traces=runtime["recurring_proof_traces"],
            no_signal_branches=db.no_signal_branches(project_id),
            discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
            all_conjectures=runtime["conjectures"],
        )
        move_candidates = _manager_candidate_slice(conjecture, runtime["experiments"], move_candidates)
        generated_candidates[conjecture.conjecture_id] = move_candidates
        for move_candidate in move_candidates:
            frontier.append(_materialize_payload(project_id, workspace_root, conjecture, move_candidate, runtime))

    frontier, llm_artifacts = _apply_llm_enrichment(db, project_id, workspace_root, frontier, runtime)
    cleaned_frontier = _strip_frontier_internal_fields(frontier)
    for item in cleaned_frontier:
        shutil.rmtree(item["workspace_dir"], ignore_errors=True)

    manager_prompt = build_manager_prompt(
        charter=runtime["charter"],
        state_summary=db.project_summary(project_id),
        frontier=cleaned_frontier,
    )
    if llm_artifacts["brief"] is not None:
        manager_prompt = manager_prompt + "\n\nCampaign brief:\n" + json.dumps(llm_artifacts["brief"], indent=2)
    chosen_payload = min(cleaned_frontier, key=_frontier_sort_key)
    chosen_conjecture = next(item for item in runtime["conjectures"] if item.conjecture_id == chosen_payload["conjecture_id"])
    chosen_move_candidate = next(item["_frontier_candidate"]["move_candidate"] for item in frontier if item["experiment_id"] == chosen_payload["experiment_id"])
    chosen = materialize_candidate(
        charter=runtime["charter"],
        conjecture=chosen_conjecture,
        workspace_root=workspace_root,
        experiments=runtime["experiments"],
        candidate=chosen_move_candidate,
        discovery_questions=runtime["questions_by_conjecture"].get(chosen_conjecture.conjecture_id, []),
    )
    return chosen, manager_prompt, cleaned_frontier


def generate_frontier(db: Database, project_id: str, workspace_root: str) -> List[Dict[str, object]]:
    runtime = _runtime_context(db, project_id)
    frontier: List[Dict[str, Any]] = []
    for conjecture in runtime["conjectures"]:
        move_candidates = generate_move_candidates(
            charter=runtime["charter"],
            conjecture=conjecture,
            experiments=runtime["experiments"],
            recurring_lemmas=runtime["recurring"],
            recurring_subgoals=runtime["recurring_subgoals"],
            recurring_proof_traces=runtime["recurring_proof_traces"],
            no_signal_branches=db.no_signal_branches(project_id),
            discovery_questions=runtime["questions_by_conjecture"].get(conjecture.conjecture_id, []),
            all_conjectures=runtime["conjectures"],
        )
        move_candidates = _manager_candidate_slice(conjecture, runtime["experiments"], move_candidates)
        for move_candidate in move_candidates:
            frontier.append(_materialize_payload(project_id, workspace_root, conjecture, move_candidate, runtime))

    frontier, _ = _apply_llm_enrichment(db, project_id, workspace_root, frontier, runtime)
    active = db.list_active_experiments(project_id)
    active_counts = _counts_by_conjecture(runtime["conjectures"], active)
    no_signal = {(item["conjecture_id"], item["move"]): item["observations"] for item in db.no_signal_branches(project_id)}
    _annotate_runtime_fields(frontier, active, no_signal, active_counts)
    return sorted(_strip_frontier_internal_fields(frontier), key=_frontier_sort_key)
