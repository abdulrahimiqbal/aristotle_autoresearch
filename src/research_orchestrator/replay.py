from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from research_orchestrator.db import Database, current_version_bundle
from research_orchestrator.evaluator import score_result
from research_orchestrator.manager_policy import build_candidate_audits
from research_orchestrator.semantic_memory import hydrate_semantic_summary
from research_orchestrator.types import (
    ArtifactProvenance,
    ProviderMetadata,
    ProviderResult,
    SemanticArtifact,
    VerificationObservation,
    VerificationRecord,
    VerificationRunMetadata,
    VerificationValidationIssue,
)


def _artifact_provenance_from_dict(payload: Dict[str, Any]) -> ArtifactProvenance:
    return ArtifactProvenance(**payload)


def _verification_observation_from_dict(payload: Dict[str, Any]) -> VerificationObservation:
    return VerificationObservation(
        text=payload.get("text", ""),
        artifact_kind=payload.get("artifact_kind", ""),
        normalized_text=payload.get("normalized_text", ""),
        canonical_id=payload.get("canonical_id", ""),
        cluster_id=payload.get("cluster_id", ""),
        detail=payload.get("detail", ""),
        confidence=payload.get("confidence", 0.5),
        provenance=[_artifact_provenance_from_dict(item) for item in payload.get("provenance", [])],
        metadata=payload.get("metadata", {}),
    )


def _verification_record_from_dict(payload: Optional[Dict[str, Any]]) -> Optional[VerificationRecord]:
    if not payload:
        return None
    return VerificationRecord(
        schema_version=payload.get("schema_version", ""),
        provider=ProviderMetadata(**payload.get("provider", {"provider_name": "unknown"})),
        run=VerificationRunMetadata(**payload.get("run", {})),
        verification_status=payload.get("verification_status", "unknown"),
        theorem_status=payload.get("theorem_status", "unresolved"),
        unsolved_goals=[_verification_observation_from_dict(item) for item in payload.get("unsolved_goals", [])],
        generated_lemmas=[_verification_observation_from_dict(item) for item in payload.get("generated_lemmas", [])],
        proved_lemmas=[_verification_observation_from_dict(item) for item in payload.get("proved_lemmas", [])],
        missing_assumptions=[_verification_observation_from_dict(item) for item in payload.get("missing_assumptions", [])],
        counterexamples=[_verification_observation_from_dict(item) for item in payload.get("counterexamples", [])],
        blocker_observations=[_verification_observation_from_dict(item) for item in payload.get("blocker_observations", [])],
        proof_traces=[_verification_observation_from_dict(item) for item in payload.get("proof_traces", [])],
        artifact_provenance=[_artifact_provenance_from_dict(item) for item in payload.get("artifact_provenance", [])],
        raw_text_fallback=payload.get("raw_text_fallback", {}),
        raw_payload=payload.get("raw_payload", {}),
        validation_issues=[VerificationValidationIssue(**item) for item in payload.get("validation_issues", [])],
    )


def _semantic_summary_from_dict(payload: Optional[Dict[str, Any]]):
    if not payload:
        return None
    artifacts = [
        SemanticArtifact(
            kind=item.get("kind", ""),
            raw_text=item.get("raw_text", ""),
            canonical_text=item.get("canonical_text", ""),
            exact_id=item.get("exact_id", ""),
            canonical_id=item.get("canonical_id", ""),
            cluster_id=item.get("cluster_id", ""),
            theorem_family=item.get("theorem_family", ""),
            metadata=item.get("metadata", {}),
        )
        for item in payload.get("artifacts", [])
    ]
    return hydrate_semantic_summary(
        artifacts,
        new_exact_count=payload.get("new_exact_count", 0),
        normalized_equivalent_count=payload.get("normalized_equivalent_count", 0),
        exact_reuse_count=payload.get("exact_reuse_count", 0),
        canonical_reuse_count=payload.get("canonical_reuse_count", 0),
        blocker_reuse_count=payload.get("blocker_reuse_count", 0),
        parser_ambiguity_count=payload.get("parser_ambiguity_count", 0),
    )


def provider_result_from_payload(payload: Dict[str, Any]) -> ProviderResult:
    return ProviderResult(
        status=payload.get("status", "unknown"),
        blocker_type=payload.get("blocker_type", "unknown"),
        proof_outcome=payload.get("proof_outcome", "unknown"),
        signal_summary=payload.get("signal_summary", ""),
        generated_lemmas=payload.get("generated_lemmas", []),
        proved_lemmas=payload.get("proved_lemmas", []),
        candidate_lemmas=payload.get("candidate_lemmas", []),
        unresolved_goals=payload.get("unresolved_goals", []),
        blocked_on=payload.get("blocked_on", []),
        missing_assumptions=payload.get("missing_assumptions", []),
        artifact_inventory=payload.get("artifact_inventory", []),
        proof_trace_fragments=payload.get("proof_trace_fragments", []),
        counterexample_witnesses=payload.get("counterexample_witnesses", []),
        normalized_candidate_lemmas=payload.get("normalized_candidate_lemmas", []),
        normalized_unresolved_goals=payload.get("normalized_unresolved_goals", []),
        new_signal_count=payload.get("new_signal_count", 0),
        reused_signal_count=payload.get("reused_signal_count", 0),
        suspected_missing_assumptions=payload.get("suspected_missing_assumptions", []),
        notes=payload.get("notes", ""),
        confidence=payload.get("confidence", 0.5),
        raw_stdout=payload.get("raw_stdout", ""),
        raw_stderr=payload.get("raw_stderr", ""),
        artifacts=payload.get("artifacts", []),
        external_id=payload.get("external_id", ""),
        external_status=payload.get("external_status", ""),
        metadata=payload.get("metadata", {}),
        verification_record=_verification_record_from_dict(payload.get("verification_record")),
        semantic_summary=_semantic_summary_from_dict(payload.get("semantic_summary")),
    )


def reconstruct_manifest(db: Database, experiment_id: str) -> Dict[str, Any]:
    manifest_row = db.latest_experiment_manifest(experiment_id)
    if manifest_row is not None:
        return manifest_row["manifest"]
    experiment = db.get_experiment(experiment_id)
    if experiment is None:
        raise KeyError(f"Unknown experiment_id: {experiment_id}")
    return db.build_experiment_manifest(
        experiment,
        snapshot_kind="reconstructed",
        provider_name=experiment.get("provider", ""),
    )


def replay_experiment(db: Database, experiment_id: str) -> Dict[str, Any]:
    experiment = db.get_experiment(experiment_id)
    if experiment is None:
        raise KeyError(f"Unknown experiment_id: {experiment_id}")
    manifest = reconstruct_manifest(db, experiment_id)
    provider_payload = (experiment.get("outcome") or {}).get("provider_result", {})
    provider_result = provider_result_from_payload(provider_payload)
    stored_evaluation = (experiment.get("outcome") or {}).get("evaluation")
    current_evaluation = score_result(
        db.get_charter(experiment["project_id"]),
        provider_result,
        verification_record=provider_result.verification_record,
        semantic_summary=provider_result.semantic_summary,
    )
    current_versions = current_version_bundle()
    stored_versions = manifest.get("versions", {})
    drift = {
        key: {
            "stored": stored_versions.get(key, ""),
            "current": current_value,
        }
        for key, current_value in current_versions.items()
        if stored_versions.get(key) and stored_versions.get(key) != current_value
    }
    stored_total = stored_evaluation.get("total") if stored_evaluation else None
    current_total = current_evaluation.total
    delta = round(current_total - stored_total, 4) if stored_total is not None else None
    return {
        "experiment_id": experiment_id,
        "status": experiment["status"],
        "snapshot_kind": manifest.get("snapshot_kind", "reconstructed"),
        "stored_versions": stored_versions,
        "current_versions": current_versions,
        "version_drift": drift,
        "stored_evaluation": stored_evaluation,
        "current_evaluation": asdict(current_evaluation),
        "delta_total": delta,
        "material_change": abs(delta) >= 0.5 if delta is not None else False,
    }


def replay_manager_run(db: Database, run_id: str) -> Dict[str, Any]:
    row = db.conn.execute("SELECT * FROM manager_runs WHERE run_id = ?", (run_id,)).fetchone()
    if row is None:
        raise KeyError(f"Unknown run_id: {run_id}")
    manager_run = dict(row)
    audits = db.list_manager_candidate_audits(run_id)
    frontier = [item["candidate"] for item in audits]
    selected_count = sum(1 for item in audits if item["selected"])
    current_audits = build_candidate_audits(frontier, [], [])
    current_selected = [item["experiment_id"] for item in current_audits[:selected_count]]
    historical_selected = [item["experiment_id"] for item in audits if item["selected"]]
    return {
        "run_id": run_id,
        "policy_path": manager_run["policy_path"],
        "historical_selected": historical_selected,
        "current_selected": current_selected,
        "selection_changed": historical_selected != current_selected,
        "historical_candidate_count": len(audits),
        "current_candidate_ranking": current_audits,
    }


def manager_llm_report(db: Database, project_id: str) -> Dict[str, Any]:
    runs = db.list_manager_runs(project_id, limit=200)
    interpretations = db.list_campaign_interpretations(project_id, limit=200)
    bridges = db.list_bridge_hypotheses(project_id, limit=500)
    audits: List[Dict[str, Any]] = []
    for run in runs:
        audits.extend(db.list_manager_candidate_audits(run["run_id"]))
    llm_audits = [item for item in audits if item.get("score_breakdown", {}).get("llm_adjustments", {}).get("total", 0) != 0]
    accepted_synthesis = sum(
        1
        for item in audits
        if item.get("candidate", {}).get("candidate_metadata", {}).get("llm_parameter_synthesis")
    )
    signal_by_policy: Dict[str, List[float]] = {}
    for run in runs:
        summary = run.get("summary", {})
        submitted = summary.get("submitted_experiments", []) if isinstance(summary, dict) else []
        for item in submitted:
            experiment = db.get_experiment(item.get("experiment_id", ""))
            if experiment is None:
                continue
            signal_by_policy.setdefault(run["policy_path"], []).append(float(experiment.get("new_signal_count") or 0))
    return {
        "project_id": project_id,
        "manager_runs": len(runs),
        "divergence_frequency": round(sum(1 for run in runs if run["policy_path"] == "llm_assisted") / max(1, len(runs)), 3),
        "average_accepted_llm_delta": round(
            sum(item["score_breakdown"]["llm_adjustments"]["llm_delta"] for item in llm_audits)
            / max(1, len(llm_audits)),
            4,
        ),
        "interpretation_validity_rate": round(
            sum(1 for item in interpretations if item.get("validation_status") == "valid") / max(1, len(interpretations)),
            3,
        ),
        "parameter_synthesis_acceptance_rate": round(accepted_synthesis / max(1, len(audits)), 3),
        "bridge_hypothesis_count": len(bridges),
        "downstream_signal_comparison": {
            policy: round(sum(values) / max(1, len(values)), 3)
            for policy, values in signal_by_policy.items()
        },
    }
