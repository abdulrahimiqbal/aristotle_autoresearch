from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence
from uuid import uuid4

from research_orchestrator.move_registry import DEFAULT_MOVE_REGISTRY, MoveCandidate, MoveGenerationContext
from research_orchestrator.theorem_families import resolve_theorem_family_adapter
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter

DEFAULT_LEAN_TOOLCHAIN = "leanprover/lean4:v4.28.0"


def _strip_imports(lean_source: str) -> str:
    return "\n".join(line for line in lean_source.splitlines() if not line.startswith("import ")) + "\n"


def _lakefile_contents(conjecture: Conjecture) -> str:
    lines = [
        "[package]",
        'name = "AristotleWorkspace"',
        'version = "0.1.0"',
        f'lean = "{DEFAULT_LEAN_TOOLCHAIN}"',
        "",
    ]
    if "import Mathlib" in conjecture.lean_statement:
        lines.extend(
            [
                "[[require]]",
                'name = "mathlib"',
                'scope = "leanprover-community"',
                'version = "main"',
                "",
            ]
        )
    lines.extend(
        [
            "[[lean_lib]]",
            'name = "AristotleWorkspace"',
            "",
        ]
    )
    return "\n".join(lines)




def _seed_discovery_questions(conjecture: Conjecture) -> List[dict]:
    raw = conjecture.family_metadata.get("seed_discovery_questions", [])
    questions = [item for item in raw if isinstance(item, dict) and item.get("question")]
    return sorted(
        questions,
        key=lambda item: (-int(item.get("priority", 0)), str(item.get("question_id", "")), str(item.get("question", ""))),
    )


def _normalize_signal(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


def _recent_signal_counter(experiments: Sequence[dict], conjecture_id: str, limit: int = 6) -> dict[str, int]:
    recent = [
        item
        for item in sorted(
            [item for item in experiments if item["conjecture_id"] == conjecture_id],
            key=lambda item: (
                item.get("completed_at") or "",
                item.get("created_at") or "",
                item.get("experiment_id") or "",
            ),
        )[-limit:]
    ]
    counts: dict[str, int] = {}
    for item in recent:
        ingestion = item.get("ingestion") or {}
        for key in (
            "proof_trace_fragments",
            "counterexample_witnesses",
            "unresolved_goals",
            "blocked_on",
            "missing_assumptions",
        ):
            for raw in ingestion.get(key, []):
                normalized = _normalize_signal(raw)
                if normalized:
                    counts[normalized] = counts.get(normalized, 0) + 1
    return counts


def _candidate_support(candidate: MoveCandidate, key: str) -> float:
    value = candidate.generation_metadata.get(key, 0.0)
    return float(value) if isinstance(value, (int, float)) else 0.0


def _motif_signature(candidate: MoveCandidate) -> str:
    signature = candidate.generation_metadata.get("motif_signature")
    if isinstance(signature, str) and signature:
        return signature
    if candidate.move_family in {"legacy.promote_lemma", "decompose_subclaim"}:
        statement = candidate.parameters.get("lemma_statement") or candidate.parameters.get("subclaim") or ""
        if statement:
            return f"lemma:{_normalize_signal(statement)}"
    if candidate.move_family == "promote_subgoal":
        return f"subgoal:{_normalize_signal(candidate.parameters.get('subgoal_statement', ''))}"
    if candidate.move_family == "promote_trace":
        return f"trace:{_normalize_signal(candidate.parameters.get('trace_fragment', ''))}"
    return f"{candidate.move_family}:{json.dumps(candidate.parameters, sort_keys=True)}"


def _motif_cluster_scores(candidates: Sequence[MoveCandidate]) -> dict[str, dict[str, float]]:
    clusters: dict[str, dict[str, float]] = {}
    for candidate in candidates:
        motif_id = _motif_signature(candidate)
        bucket = clusters.setdefault(
            motif_id,
            {
                "motif_id": motif_id,
                "candidate_count": 0.0,
                "motif_reuse_count": 0.0,
                "signal_support": 0.0,
                "blocker_support": 0.0,
                "witness_support": 0.0,
                "assumption_boundary_support": 0.0,
                "recent_signal_velocity": 0.0,
            },
        )
        bucket["candidate_count"] += 1
        bucket["motif_reuse_count"] += max(candidate.reuse_potential, 0.0)
        bucket["signal_support"] += _candidate_support(candidate, "signal_support")
        bucket["blocker_support"] += _candidate_support(candidate, "blocker_support")
        bucket["witness_support"] += _candidate_support(candidate, "witness_support")
        bucket["assumption_boundary_support"] += _candidate_support(candidate, "assumption_boundary_support")
        bucket["recent_signal_velocity"] = max(bucket["recent_signal_velocity"], _candidate_support(candidate, "recent_signal_velocity"))
    return clusters


def build_boundary_followups(
    *,
    charter: ProjectCharter,
    conjecture: Conjecture,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
    recurring_proof_traces: List[dict] | None = None,
    no_signal_branches: List[dict] | None = None,
    discovery_questions: List[dict] | None = None,
    all_conjectures: List[Conjecture] | None = None,
) -> List[MoveCandidate]:
    context = build_move_generation_context(
        charter=charter,
        conjecture=conjecture,
        experiments=experiments,
        recurring_lemmas=recurring_lemmas,
        recurring_subgoals=recurring_subgoals,
        recurring_proof_traces=recurring_proof_traces,
        no_signal_branches=no_signal_branches,
        discovery_questions=discovery_questions,
        all_conjectures=all_conjectures,
    )
    allowed = {"boundary_map_from_witness", "boundary_map_from_missing_assumption"}
    return [
        candidate
        for candidate in DEFAULT_MOVE_REGISTRY.generate_candidates(context, allowed_moves=allowed)
        if candidate.legacy_move in allowed or candidate.move_family in allowed
    ]


def select_discovery_question(
    *,
    conjecture: Conjecture,
    discovery_questions: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
    recurring_proof_traces: List[dict] | None = None,
    recent_signal_counter: dict[str, int] | None = None,
    blocker_signals: List[str] | None = None,
) -> dict[str, Any] | None:
    questions = discovery_questions or _seed_discovery_questions(conjecture)
    if not questions:
        return None
    recurring_subgoals = recurring_subgoals or []
    recurring_proof_traces = recurring_proof_traces or []
    recent_signal_counter = recent_signal_counter or {}
    blocker_signals = blocker_signals or []
    def _tokens(text: str) -> set[str]:
        return {token for token in _normalize_signal(text).split() if len(token) >= 4}

    lemma_text = " ".join(item.get("representative_statement", "") for item in recurring_lemmas[:4]).lower()
    subgoal_text = " ".join(item.get("statement", "") for item in recurring_subgoals[:4]).lower()
    trace_text = " ".join(item.get("fragment", "") for item in recurring_proof_traces[:4]).lower()
    signal_text = " ".join(recent_signal_counter.keys()).lower()
    blocker_text = " ".join(str(item) for item in blocker_signals).lower()

    scored: list[tuple[tuple[float, ...], str, str, dict[str, Any]]] = []
    for item in questions:
        question = str(item.get("question", ""))
        lowered = question.lower()
        priority = float(item.get("priority", 0)) / 25.0
        unresolvedness = 1.0 if item.get("status", "open") == "open" else 0.0
        recency = 1.0 / (1.0 + len(str(item.get("updated_at", ""))))
        question_tokens = _tokens(question)
        alignment = 0.0
        alignment += 0.8 * sum(1 for token in question_tokens if token in lemma_text)
        alignment += 1.6 * sum(1 for token in question_tokens if token in subgoal_text)
        alignment += 1.2 * sum(1 for token in question_tokens if token in trace_text)
        alignment += 1.4 * sum(1 for token in question_tokens if token in signal_text)
        alignment += 0.8 * sum(1 for token in question_tokens if token in blocker_text)
        if recurring_subgoals and "subgoal" in lowered:
            alignment += 1.0
        if recurring_proof_traces and "trace" in lowered:
            alignment += 1.0
        signal_alignment = sum(count for token, count in recent_signal_counter.items() if any(part in question_tokens for part in _tokens(token)))
        blocker_concentration = sum(1 for token in blocker_signals if any(part in question_tokens for part in _tokens(token)))
        numeric_key = (
            alignment,
            signal_alignment,
            blocker_concentration,
            priority,
            unresolvedness,
            recency,
            -float(len(question)),
        )
        scored.append((numeric_key, str(item.get("question_id", "")), question, item))
    return sorted(
        scored,
        key=lambda pair: (
            tuple(-value for value in pair[0]),
            pair[1],
            pair[2],
        ),
    )[0][3]


def build_move_generation_context(
    *,
    charter: ProjectCharter,
    conjecture: Conjecture,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
    recurring_proof_traces: List[dict] | None = None,
    no_signal_branches: List[dict] | None = None,
    discovery_questions: List[dict] | None = None,
    all_conjectures: List[Conjecture] | None = None,
) -> MoveGenerationContext:
    return MoveGenerationContext(
        charter=charter,
        conjecture=conjecture,
        experiments=experiments,
        recurring_lemmas=recurring_lemmas,
        recurring_subgoals=recurring_subgoals or [],
        recurring_proof_traces=recurring_proof_traces or [],
        no_signal_branches=no_signal_branches or [],
        open_questions=discovery_questions or [],
        all_conjectures=all_conjectures or [],
    )


def generate_move_candidates(
    *,
    charter: ProjectCharter,
    conjecture: Conjecture,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
    recurring_proof_traces: List[dict] | None = None,
    no_signal_branches: List[dict] | None = None,
    discovery_questions: List[dict] | None = None,
    all_conjectures: List[Conjecture] | None = None,
) -> List[MoveCandidate]:
    context = build_move_generation_context(
        charter=charter,
        conjecture=conjecture,
        experiments=experiments,
        recurring_lemmas=recurring_lemmas,
        recurring_subgoals=recurring_subgoals,
        recurring_proof_traces=recurring_proof_traces,
        no_signal_branches=no_signal_branches,
        discovery_questions=discovery_questions,
        all_conjectures=all_conjectures,
    )
    candidates = DEFAULT_MOVE_REGISTRY.generate_candidates(context)
    recent_signal_counter = _recent_signal_counter(experiments, conjecture.conjecture_id)
    recent_signal_velocity = context.recent_signal_velocity()
    motif_cluster_signals = _motif_cluster_scores(candidates)
    seen_signatures = {
        json.dumps(
            {
                "legacy_move": item["move"],
                "parameters": item["modification"],
            },
            sort_keys=True,
        )
        for item in context.effective_conjecture_experiments
    }
    filtered: List[MoveCandidate] = []
    for candidate in candidates:
        motif_id = _motif_signature(candidate)
        cluster = motif_cluster_signals.get(motif_id, {})
        metadata = dict(candidate.generation_metadata)
        metadata.update(
            {
                "motif_signature": motif_id,
                "motif_id": metadata.get("motif_id", motif_id),
                "motif_reuse_count": round(cluster.get("motif_reuse_count", candidate.reuse_potential), 3),
                "signal_support": round(cluster.get("signal_support", 0.0), 3),
                "blocker_support": round(cluster.get("blocker_support", 0.0), 3),
                "witness_support": round(cluster.get("witness_support", 0.0), 3),
                "assumption_boundary_support": round(cluster.get("assumption_boundary_support", 0.0), 3),
                "recent_signal_velocity": recent_signal_velocity,
            }
        )
        candidate = MoveCandidate(
            move_family=candidate.move_family,
            legacy_move=candidate.legacy_move,
            parameters=dict(candidate.parameters),
            objective=candidate.objective,
            expected_signal=candidate.expected_signal,
            rationale=candidate.rationale,
            novelty_score=candidate.novelty_score,
            reuse_potential=candidate.reuse_potential,
            obstruction_targeting=candidate.obstruction_targeting,
            diversity_group=candidate.diversity_group,
            duplicate_penalty=candidate.duplicate_penalty,
            no_signal_penalty=candidate.no_signal_penalty,
            transfer_score=candidate.transfer_score,
            generation_metadata=metadata,
        )
        signature = json.dumps(
            {
                "legacy_move": candidate.legacy_move,
                "parameters": candidate.parameters,
            },
            sort_keys=True,
        )
        if signature in seen_signatures and context.active_no_signal_count < 5:
            continue
        filtered.append(candidate)
    if not filtered and candidates:
        filtered = candidates[:1]
    return filtered


def rank_move_candidates(
    candidates: Sequence[MoveCandidate],
    *,
    existing_experiments: int,
    active_count: int,
    no_signal_penalty: int = 0,
) -> List[MoveCandidate]:
    motif_scores = _motif_cluster_scores(candidates)
    return sorted(
        candidates,
        key=lambda candidate: (
            active_count,
            existing_experiments,
            candidate.no_signal_penalty + no_signal_penalty + candidate.duplicate_penalty,
            -motif_scores.get(_motif_signature(candidate), {}).get("recent_signal_velocity", 0.0),
            -motif_scores.get(_motif_signature(candidate), {}).get("motif_reuse_count", 0.0),
            -(candidate.transfer_score + candidate.reuse_potential + candidate.obstruction_targeting + candidate.novelty_score),
            candidate.move_family,
            candidate.signature,
        ),
    )


def choose_move(
    charter: ProjectCharter,
    conjecture: Conjecture,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
) -> tuple[str, Dict[str, object], str, str]:
    recurring_subgoals = recurring_subgoals or []
    conjecture_experiments = [item for item in experiments if item["conjecture_id"] == conjecture.conjecture_id]
    effective_experiments = [
        item
        for item in conjecture_experiments
        if item.get("proof_outcome") not in {"unknown", "auth_failure", "infra_failure", "malformed"}
        or (item.get("new_signal_count") or 0) > 0
    ]
    seen_moves = [item["move"] for item in effective_experiments]
    tested_assumptions = {
        item["modification"].get("assumption")
        for item in effective_experiments
        if item["move"] == "perturb_assumption" and item["modification"].get("assumption")
    }
    structural_count = sum(
        1
        for item in effective_experiments
        if item["status"] in {"failed", "stalled"} and item.get("blocker_type") == "structural"
    )
    recurring_for_conjecture = [
        item for item in recurring_lemmas if conjecture.conjecture_id in item.get("conjecture_ids", [conjecture.conjecture_id])
    ]
    repeated_unknown = sum(
        1
        for item in effective_experiments
        if item["status"] == "stalled"
        and item.get("proof_outcome") == "unknown"
        and not (item.get("new_signal_count") or 0)
    )
    counter_count = sum(1 for item in conjecture_experiments if item["move"] == "counterexample_mode")
    counter_target = ["most_fragile_variant", "boundary_variant", "minimal_variant", "negated_weakening", "parameter_extreme"][
        counter_count % 5
    ]
    counter_modification = {"target": counter_target, "attempt": counter_count + 1}
    counter_objective = (
        f"Fill in all sorries. Search for a counterexample or independence witness for the "
        f"{counter_target.replace('_', ' ')}."
    )

    if "underspecify" not in seen_moves:
        return (
            "underspecify",
            {"mode": "minimal_context"},
            "Fill in all sorries. Strip imports to expose hidden dependencies. Report any intermediate lemmas or unresolved goals.",
            "Surface hidden assumptions and early lemma needs.",
        )

    for assumption in conjecture.assumptions:
        if assumption not in tested_assumptions:
            return (
                "perturb_assumption",
                {"assumption": assumption, "operation": "remove"},
                f"Fill in all sorries. The assumption '{assumption}' has been removed. Determine whether the proof still closes and report the blocker if not.",
                "Measure assumption sensitivity and classify the blocker.",
            )

    if any(item["reuse_count"] >= charter.promotion_threshold for item in recurring_for_conjecture or recurring_lemmas) and "promote_lemma" not in seen_moves:
        lemma = sorted(recurring_for_conjecture or recurring_lemmas, key=lambda x: (-x["reuse_count"], x["representative_statement"]))[0]
        return (
            "promote_lemma",
            {"lemma_statement": lemma["representative_statement"]},
            "Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem.",
            "Determine whether the recurring helper captures real mathematical structure.",
        )

    if recurring_subgoals and "promote_lemma" not in seen_moves:
        promoted = recurring_subgoals[0]["statement"]
        return (
            "promote_lemma",
            {"lemma_statement": promoted},
            "Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem.",
            "Compress repeated proof search failure into a reusable theorem objective.",
        )

    if "reformulate" not in seen_moves:
        form = conjecture.equivalent_forms[0] if conjecture.equivalent_forms else "equivalent reformulation"
        return (
            "reformulate",
            {"form": form},
            f"Fill in all sorries. This is a reformulation as {form}. Determine whether this form is easier or harder to prove and report intermediate progress.",
            "Separate structural difficulty from representation-specific difficulty.",
        )

    if structural_count >= 2 or repeated_unknown >= 2:
        return (
            "counterexample_mode",
            counter_modification,
            counter_objective,
            "Disambiguate falsehood from search failure after repeated structural blockers or no-signal runs.",
        )

    return (
        "counterexample_mode",
        counter_modification,
        counter_objective,
        "Disambiguate falsehood from search failure.",
    )


def _materialized_body(conjecture: Conjecture, candidate: MoveCandidate, header: List[str]) -> str:
    adapter = resolve_theorem_family_adapter(conjecture)
    if candidate.legacy_move == "underspecify":
        body = _strip_imports(conjecture.lean_statement)
        return "\n".join(header + [body])
    if candidate.legacy_move == "promote_lemma" and candidate.move_family in {"legacy.promote_lemma", "decompose_subclaim"}:
        statement = candidate.parameters.get("lemma_statement") or candidate.parameters.get("subclaim") or "True"
        return "\n".join(
            header
            + [
                f"-- promoted target: {statement}",
                "theorem promoted_lemma : True := by",
                "  sorry",
                "",
            ]
        )
    return adapter.materialize_source(conjecture, candidate.move_family, candidate.parameters, header)


def build_cumulative_workspace(
    base_body: str,
    conjecture_id: str,
    db: Any = None,
    proved_lemmas: List[Dict[str, Any]] | None = None,
) -> str:
    """Build a cumulative workspace including all previously proved lemmas.

    This function prepends proved lemmas from the proof ledger to the base
    workspace body, creating a cumulative context where each new experiment
    builds on all previously verified results.

    Args:
        base_body: The base Lean code for the current experiment
        conjecture_id: The conjecture ID to filter lemmas by
        db: Optional database instance to fetch lemmas from proof_ledger
        proved_lemmas: Optional list of proved lemmas (if db not provided)

    Returns:
        The cumulative workspace body with proved lemmas prepended
    """
    lemmas_to_include: List[Dict[str, Any]] = []

    # Fetch from database if available
    if db is not None:
        try:
            lemmas_to_include = db.get_proved_lemmas_for_conjecture(conjecture_id)
        except Exception:
            # Database might not have the method or connection issue
            pass

    # Use provided lemmas if no db results
    if not lemmas_to_include and proved_lemmas is not None:
        lemmas_to_include = proved_lemmas

    if not lemmas_to_include:
        return base_body

    # Build cumulative header with proved lemmas
    cumulative_parts = ["/-", "Cumulative Workspace: Previously Proved Lemmas", "-/", ""]

    for i, lemma in enumerate(lemmas_to_include):
        statement = lemma.get("lemma_statement", "")
        lean_code = lemma.get("proof_lean_code", "")
        lemma_id = lemma.get("entry_id", f"lemma_{i}")

        if not statement:
            continue

        cumulative_parts.append(f"-- From proof ledger: {lemma_id}")
        cumulative_parts.append(f"lemma cumulative_lemma_{i} : {statement} := by")

        if lean_code:
            # Indent the proof code
            indented_proof = "\n".join("  " + line for line in lean_code.strip().split("\n"))
            cumulative_parts.append(indented_proof)
        else:
            cumulative_parts.append("  sorry")

        cumulative_parts.append("")

    cumulative_parts.append("/-")
    cumulative_parts.append("Current Experiment")
    cumulative_parts.append("-/")
    cumulative_parts.append("")

    return "\n".join(cumulative_parts) + "\n" + base_body


def materialize_candidate(
    *,
    charter: ProjectCharter,
    conjecture: Conjecture,
    workspace_root: str,
    experiments: List[dict],
    candidate: MoveCandidate,
    discovery_questions: List[dict] | None = None,
) -> ExperimentBrief:
    phase = "discovery"
    discovery_questions = discovery_questions or []
    recurring_signal_counter = _recent_signal_counter(experiments, conjecture.conjecture_id)
    chosen_question = select_discovery_question(
        conjecture=conjecture,
        discovery_questions=discovery_questions,
        recurring_lemmas=[],
        recurring_subgoals=[{"statement": candidate.parameters.get("subgoal_statement", "")}] if candidate.move_family == "promote_subgoal" else None,
        recurring_proof_traces=[{"fragment": candidate.parameters.get("trace_fragment", "")}] if candidate.move_family == "promote_trace" else None,
        recent_signal_counter=recurring_signal_counter,
        blocker_signals=list((candidate.generation_metadata.get("blocked_on") or []) if isinstance(candidate.generation_metadata.get("blocked_on"), list) else []),
    )
    experiment_id = str(uuid4())
    workspace_dir = Path(workspace_root) / experiment_id
    workspace_dir.mkdir(parents=True, exist_ok=True)
    lean_file = workspace_dir / "Main.lean"
    toolchain_file = workspace_dir / "lean-toolchain"
    lakefile = workspace_dir / "lakefile.toml"

    theorem_family_id = resolve_theorem_family_adapter(conjecture).family_id
    header = [
        "/-",
        f"Experiment ID: {experiment_id}",
        f"Move: {candidate.legacy_move}",
        f"Move family: {candidate.move_family}",
        f"Theorem family: {theorem_family_id}",
        f"Modification: {json.dumps(candidate.parameters, sort_keys=True)}",
        "-/",
        "",
    ]
    body = _materialized_body(conjecture, candidate, header)

    # Build cumulative workspace with previously proved lemmas
    cumulative_body = build_cumulative_workspace(
        base_body=body,
        conjecture_id=conjecture.conjecture_id,
        db=None,  # Will be injected by caller if available
    )

    with open(lean_file, "w", encoding="utf-8") as handle:
        handle.write(cumulative_body if cumulative_body.endswith("\n") else cumulative_body + "\n")
    toolchain_file.write_text(DEFAULT_LEAN_TOOLCHAIN + "\n", encoding="utf-8")
    lakefile.write_text(_lakefile_contents(conjecture), encoding="utf-8")

    metadata = dict(candidate.generation_metadata)
    metadata.update(
        {
            "move": candidate.legacy_move,
            "move_family": candidate.move_family,
            "novelty_score": candidate.novelty_score,
            "reuse_potential": candidate.reuse_potential,
            "obstruction_targeting": candidate.obstruction_targeting,
            "diversity_group": candidate.diversity_group,
            "duplicate_penalty": candidate.duplicate_penalty,
            "no_signal_penalty": candidate.no_signal_penalty,
            "transfer_score": candidate.transfer_score,
            "motif_id": metadata.get("motif_id", _motif_signature(candidate)),
            "motif_signature": metadata.get("motif_signature", _motif_signature(candidate)),
            "signal_support": metadata.get("signal_support", 0),
            "blocker_support": metadata.get("blocker_support", 0),
            "witness_support": metadata.get("witness_support", 0),
            "assumption_boundary_support": metadata.get("assumption_boundary_support", 0),
            "recent_signal_velocity": metadata.get("recent_signal_velocity", 0),
        }
    )
    return ExperimentBrief(
        experiment_id=experiment_id,
        project_id=charter.project_id,
        conjecture_id=conjecture.conjecture_id,
        phase=phase,
        move=candidate.legacy_move,
        objective=(
            f"{candidate.objective} Discovery question: {chosen_question['question']}"
            if chosen_question
            else candidate.objective
        ),
        expected_signal=(
            f"{candidate.expected_signal} This run should help answer: {chosen_question['question']}"
            if chosen_question
            else candidate.expected_signal
        ),
        modification=candidate.parameters,
        workspace_dir=str(workspace_dir),
        lean_file=str(lean_file),
        move_family=candidate.move_family,
        theorem_family_id=theorem_family_id,
        move_title=candidate.move_family.replace("_", " "),
        rationale=candidate.rationale,
        candidate_metadata=metadata,
        discovery_question_id=chosen_question["question_id"] if chosen_question else "",
        discovery_question=chosen_question["question"] if chosen_question else "",
    )


def materialize_experiment(
    charter: ProjectCharter,
    conjecture: Conjecture,
    workspace_root: str,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
    discovery_questions: List[dict] | None = None,
) -> ExperimentBrief:
    candidates = generate_move_candidates(
        charter=charter,
        conjecture=conjecture,
        experiments=experiments,
        recurring_lemmas=recurring_lemmas,
        recurring_subgoals=recurring_subgoals,
        discovery_questions=discovery_questions,
    )
    ranked = rank_move_candidates(
        candidates,
        existing_experiments=len([item for item in experiments if item["conjecture_id"] == conjecture.conjecture_id]),
        active_count=0,
    )
    return materialize_candidate(
        charter=charter,
        conjecture=conjecture,
        workspace_root=workspace_root,
        experiments=experiments,
        candidate=ranked[0],
        discovery_questions=discovery_questions,
    )
