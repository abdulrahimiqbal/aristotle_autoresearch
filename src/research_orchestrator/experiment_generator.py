from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
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


def _next_phase(charter: ProjectCharter, num_experiments: int) -> str:
    if num_experiments == 0:
        return "mapping"
    if num_experiments < 3:
        return "excavation"
    if num_experiments < 5:
        return "stress_testing"
    return "consolidation"


def _seed_discovery_questions(conjecture: Conjecture) -> List[dict]:
    raw = conjecture.family_metadata.get("seed_discovery_questions", [])
    questions = [item for item in raw if isinstance(item, dict) and item.get("question")]
    return sorted(
        questions,
        key=lambda item: (-int(item.get("priority", 0)), str(item.get("question_id", "")), str(item.get("question", ""))),
    )


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
    return sorted(
        candidates,
        key=lambda candidate: (
            active_count,
            existing_experiments,
            candidate.no_signal_penalty + no_signal_penalty + candidate.duplicate_penalty,
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


def materialize_candidate(
    *,
    charter: ProjectCharter,
    conjecture: Conjecture,
    workspace_root: str,
    experiments: List[dict],
    candidate: MoveCandidate,
    discovery_questions: List[dict] | None = None,
) -> ExperimentBrief:
    phase = _next_phase(charter, len(experiments))
    discovery_questions = discovery_questions or []
    chosen_question = (
        sorted(discovery_questions, key=lambda item: (-item.get("priority", 0), item.get("question_id", "")))[0]
        if discovery_questions
        else (_seed_discovery_questions(conjecture)[0] if _seed_discovery_questions(conjecture) else None)
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
        f"Phase: {phase}",
        f"Modification: {json.dumps(candidate.parameters, sort_keys=True)}",
        "-/",
        "",
    ]
    body = _materialized_body(conjecture, candidate, header)

    with open(lean_file, "w", encoding="utf-8") as handle:
        handle.write(body if body.endswith("\n") else body + "\n")
    toolchain_file.write_text(DEFAULT_LEAN_TOOLCHAIN + "\n", encoding="utf-8")
    lakefile.write_text(_lakefile_contents(conjecture), encoding="utf-8")

    metadata = dict(candidate.generation_metadata)
    metadata.update(
        {
            "novelty_score": candidate.novelty_score,
            "reuse_potential": candidate.reuse_potential,
            "obstruction_targeting": candidate.obstruction_targeting,
            "diversity_group": candidate.diversity_group,
            "duplicate_penalty": candidate.duplicate_penalty,
            "no_signal_penalty": candidate.no_signal_penalty,
            "transfer_score": candidate.transfer_score,
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
