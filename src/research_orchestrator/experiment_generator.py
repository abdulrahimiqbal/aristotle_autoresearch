from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter

DEFAULT_LEAN_TOOLCHAIN = "leanprover/lean4:v4.28.0"


def _next_phase(charter: ProjectCharter, num_experiments: int) -> str:
    if num_experiments == 0:
        return "mapping"
    if num_experiments < 3:
        return "excavation"
    if num_experiments < 5:
        return "stress_testing"
    return "consolidation"


def choose_move(
    charter: ProjectCharter,
    conjecture: Conjecture,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
) -> tuple[str, Dict[str, str], str, str]:
    conjecture_experiments = [item for item in experiments if item["conjecture_id"] == conjecture.conjecture_id]
    seen_moves = [item["move"] for item in conjecture_experiments]
    tested_assumptions = {
        item["modification"].get("assumption")
        for item in experiments
        if item["move"] == "perturb_assumption" and item["modification"].get("assumption")
    }
    structural_count = sum(
        1
        for item in conjecture_experiments
        if item["status"] in {"failed", "stalled"} and item.get("blocker_type") == "structural"
    )
    recurring_for_conjecture = [
        item for item in recurring_lemmas if conjecture.conjecture_id in item.get("conjecture_ids", [conjecture.conjecture_id])
    ]
    recurring_subgoals = recurring_subgoals or []
    repeated_unknown = sum(
        1
        for item in conjecture_experiments
        if item["status"] == "stalled"
        and item.get("proof_outcome") == "unknown"
        and not (item.get("new_signal_count") or 0)
    )

    if "underspecify" not in seen_moves:
        return (
            "underspecify",
            {"mode": "minimal_context"},
            "Force the prover to reconstruct dependencies from minimal formal context.",
            "Surface hidden assumptions and early lemma needs.",
        )

    for assumption in conjecture.assumptions:
        if assumption not in tested_assumptions:
            return (
                "perturb_assumption",
                {"assumption": assumption, "operation": "remove"},
                f"Remove assumption `{assumption}` and test whether the theorem landscape changes sharply.",
                "Measure assumption sensitivity and classify the blocker.",
            )

    if any(item["reuse_count"] >= charter.promotion_threshold for item in recurring_for_conjecture or recurring_lemmas) and "promote_lemma" not in seen_moves:
        lemma = sorted(recurring_for_conjecture or recurring_lemmas, key=lambda x: (-x["reuse_count"], x["representative_statement"]))[0]
        return (
            "promote_lemma",
            {"lemma_statement": lemma["representative_statement"]},
            "Promote the most recurring helper lemma into a standalone theorem target.",
            "Determine whether the recurring helper captures real mathematical structure.",
        )

    if recurring_subgoals and "promote_lemma" not in seen_moves:
        promoted = recurring_subgoals[0]["statement"]
        return (
            "promote_lemma",
            {"lemma_statement": promoted},
            "Promote the most recurring unresolved subgoal into a standalone theorem target.",
            "Compress repeated proof search failure into a reusable theorem objective.",
        )

    if "reformulate" not in seen_moves:
        form = conjecture.equivalent_forms[0] if conjecture.equivalent_forms else "equivalent reformulation"
        return (
            "reformulate",
            {"form": form},
            f"Re-express the conjecture as a {form}.",
            "Separate structural difficulty from representation-specific difficulty.",
        )

    if structural_count >= 2 or repeated_unknown >= 2:
        return (
            "counterexample_mode",
            {"target": "most_fragile_variant"},
            "Seek a falsifying or independence-style witness for the most fragile observed variant.",
            "Disambiguate falsehood from search failure after repeated structural blockers or no-signal runs.",
        )

    return (
        "counterexample_mode",
        {"target": "most_fragile_variant"},
        "Seek a falsifying or independence-style witness for the most fragile observed variant.",
        "Disambiguate falsehood from search failure.",
    )


def materialize_experiment(
    charter: ProjectCharter,
    conjecture: Conjecture,
    workspace_root: str,
    experiments: List[dict],
    recurring_lemmas: List[dict],
    recurring_subgoals: List[dict] | None = None,
) -> ExperimentBrief:
    phase = _next_phase(charter, len(experiments))
    move, modification, objective, expected_signal = choose_move(
        charter, conjecture, experiments, recurring_lemmas, recurring_subgoals
    )
    experiment_id = str(uuid4())
    workspace_dir = Path(workspace_root) / experiment_id
    workspace_dir.mkdir(parents=True, exist_ok=True)
    lean_file = workspace_dir / "Main.lean"
    toolchain_file = workspace_dir / "lean-toolchain"
    lakefile = workspace_dir / "lakefile.toml"

    header = [
        "/-",
        f"Experiment ID: {experiment_id}",
        f"Move: {move}",
        f"Phase: {phase}",
        f"Modification: {json.dumps(modification)}",
        "-/",
        "",
    ]
    body = conjecture.lean_statement
    if move == "underspecify":
        body = body.replace("import Mathlib\n", "")
    elif move == "reformulate":
        body = "\n".join(header) + "\n-- reformulation: " + modification["form"] + "\n" + body
    elif move == "perturb_assumption":
        body = "\n".join(header) + "\n-- assumption removed: " + modification["assumption"] + "\n" + body
    elif move == "promote_lemma":
        body = "\n".join(header) + "\n" + f"theorem promoted_lemma : True := by\n  sorry\n"
    elif move == "counterexample_mode":
        body = "\n".join(header) + "\n-- counterexample mode target\n" + body
    else:
        body = "\n".join(header) + "\n" + body

    with open(lean_file, "w", encoding="utf-8") as handle:
        handle.write("\n".join(header) + body if not body.startswith("/-") else body)
    toolchain_file.write_text(DEFAULT_LEAN_TOOLCHAIN + "\n", encoding="utf-8")
    lakefile.write_text(
        "\n".join(
            [
                'name = "AristotleWorkspace"',
                'version = "0.1.0"',
                'defaultTargets = ["AristotleWorkspace"]',
                "",
                "[[lean_lib]]",
                'name = "AristotleWorkspace"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    return ExperimentBrief(
        experiment_id=experiment_id,
        project_id=charter.project_id,
        conjecture_id=conjecture.conjecture_id,
        phase=phase,
        move=move,
        objective=objective,
        expected_signal=expected_signal,
        modification=modification,
        workspace_dir=str(workspace_dir),
        lean_file=str(lean_file),
    )
