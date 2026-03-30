from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Sequence

from research_orchestrator.theorem_families import infer_theorem_family_id, resolve_theorem_family_adapter
from research_orchestrator.types import Conjecture, ProjectCharter


NON_SIGNAL_PROOF_OUTCOMES = {"unknown", "auth_failure", "infra_failure", "malformed"}
COUNTEREXAMPLE_TARGETS = [
    "most_fragile_variant",
    "boundary_variant",
    "minimal_variant",
    "negated_weakening",
    "parameter_extreme",
]


def _stable_signature(values: Dict[str, Any]) -> str:
    return json.dumps(values, sort_keys=True, separators=(",", ":"))


def _effective_experiments(experiments: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        item
        for item in experiments
        if item.get("proof_outcome") not in NON_SIGNAL_PROOF_OUTCOMES or (item.get("new_signal_count") or 0) > 0
    ]


def _semantic_kinds(experiments: Sequence[Dict[str, Any]], kind: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for item in experiments:
        ingestion = item.get("ingestion") or {}
        semantic_summary = ingestion.get("semantic_summary") or {}
        for artifact in semantic_summary.get("artifacts", []):
            if artifact.get("kind") == kind:
                counts[artifact.get("canonical_text") or artifact.get("raw_text") or ""] += 1
        record = ingestion.get("verification_record") or {}
        field_name = {
            "lemma": "generated_lemmas",
            "goal": "unsolved_goals",
            "blocker": "blocker_observations",
            "counterexample": "counterexamples",
            "proof_trace": "proof_traces",
            "assumption": "missing_assumptions",
        }.get(kind, "")
        for artifact in record.get(field_name, []):
            counts[artifact.get("text", "")] += 1
        provider_result = (item.get("outcome") or {}).get("provider_result") or {}
        fallback_groups = {
            "lemma": provider_result.get("proved_lemmas", []) + provider_result.get("generated_lemmas", []),
            "goal": provider_result.get("unresolved_goals", []),
            "blocker": provider_result.get("blocked_on", []) or ([item.get("blocker_type", "")] if item.get("blocker_type") else []),
            "counterexample": provider_result.get("counterexample_witnesses", []),
            "proof_trace": provider_result.get("proof_trace_fragments", []),
            "assumption": provider_result.get("missing_assumptions", []) + provider_result.get("suspected_missing_assumptions", []),
        }
        for artifact in fallback_groups.get(kind, []):
            if artifact:
                counts[str(artifact)] += 1
    return counts


@dataclass
class MoveCandidate:
    move_family: str
    legacy_move: str
    parameters: Dict[str, Any]
    objective: str
    expected_signal: str
    rationale: str
    novelty_score: float = 0.0
    reuse_potential: float = 0.0
    obstruction_targeting: float = 0.0
    diversity_group: str = ""
    duplicate_penalty: float = 0.0
    no_signal_penalty: float = 0.0
    transfer_score: float = 0.0
    generation_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def signature(self) -> str:
        return _stable_signature(
            {
                "move_family": self.move_family,
                "legacy_move": self.legacy_move,
                "parameters": self.parameters,
            }
        )


@dataclass
class MoveGenerationContext:
    charter: ProjectCharter
    conjecture: Conjecture
    experiments: List[Dict[str, Any]]
    recurring_lemmas: List[Dict[str, Any]]
    recurring_subgoals: List[Dict[str, Any]]
    recurring_proof_traces: List[Dict[str, Any]]
    no_signal_branches: List[Dict[str, Any]]
    open_questions: List[Dict[str, Any]]
    all_conjectures: List[Conjecture] = field(default_factory=list)

    @property
    def conjecture_experiments(self) -> List[Dict[str, Any]]:
        return [item for item in self.experiments if item["conjecture_id"] == self.conjecture.conjecture_id]

    @property
    def effective_conjecture_experiments(self) -> List[Dict[str, Any]]:
        return _effective_experiments(self.conjecture_experiments)

    @property
    def active_no_signal_count(self) -> int:
        return sum(
            item["observations"]
            for item in self.no_signal_branches
            if item["conjecture_id"] == self.conjecture.conjecture_id
        )

    @property
    def theorem_family_id(self) -> str:
        return infer_theorem_family_id(self.conjecture)

    def prior_family_count(self, move_family: str) -> int:
        return sum(1 for item in self.conjecture_experiments if item.get("move_family", item["move"]) == move_family)

    def legacy_move_count(self, legacy_move: str) -> int:
        return sum(1 for item in self.conjecture_experiments if item["move"] == legacy_move)

    def tested_assumptions(self) -> set[str]:
        return {
            item["modification"].get("assumption")
            for item in self.effective_conjecture_experiments
            if item["move"] == "perturb_assumption" and item["modification"].get("assumption")
        }

    def recurring_lemmas_for_conjecture(self) -> List[Dict[str, Any]]:
        return [
            item
            for item in self.recurring_lemmas
            if self.conjecture.conjecture_id in item.get("conjecture_ids", [self.conjecture.conjecture_id])
        ]

    def semantic_counter(self, kind: str) -> Counter[str]:
        return _semantic_kinds(self.conjecture_experiments, kind)

    def transfer_hints(self) -> List[Dict[str, Any]]:
        transfer_domains = set(self.conjecture.candidate_transfer_domains)
        if not transfer_domains:
            return []
        hints: List[Dict[str, Any]] = []
        for other in self.all_conjectures:
            if other.conjecture_id == self.conjecture.conjecture_id:
                continue
            if other.domain not in transfer_domains and infer_theorem_family_id(other) not in transfer_domains:
                continue
            other_experiments = [item for item in self.experiments if item["conjecture_id"] == other.conjecture_id]
            proved_counts = _semantic_kinds(other_experiments, "lemma")
            if not proved_counts:
                continue
            statement, reuse = sorted(proved_counts.items(), key=lambda pair: (-pair[1], pair[0]))[0]
            hints.append(
                {
                    "source_conjecture_id": other.conjecture_id,
                    "source_domain": other.domain,
                    "artifact": statement,
                    "reuse_count": reuse,
                }
            )
        return sorted(hints, key=lambda item: (-item["reuse_count"], item["source_conjecture_id"]))

    def recent_evaluation_average(self) -> float:
        totals: List[float] = []
        for item in self.conjecture_experiments:
            outcome = item.get("outcome") or {}
            evaluation = outcome.get("evaluation") or {}
            total = evaluation.get("total")
            if isinstance(total, (float, int)):
                totals.append(float(total))
        if not totals:
            return 0.0
        return sum(totals) / len(totals)


Generator = Callable[[MoveGenerationContext], List[MoveCandidate]]


@dataclass(frozen=True)
class MoveFamilySpec:
    move_family: str
    legacy_move: str
    description: str
    parameter_keys: Sequence[str]
    generator: Generator
    interpretation_metadata: Dict[str, Any] = field(default_factory=dict)


class MoveRegistry:
    def __init__(self) -> None:
        self._families: Dict[str, MoveFamilySpec] = {}

    def register(self, spec: MoveFamilySpec) -> None:
        self._families[spec.move_family] = spec

    def get(self, move_family: str) -> MoveFamilySpec:
        return self._families[move_family]

    def all_specs(self) -> List[MoveFamilySpec]:
        return [self._families[key] for key in sorted(self._families)]

    def generate_candidates(self, context: MoveGenerationContext, allowed_moves: Iterable[str] | None = None) -> List[MoveCandidate]:
        allowed = set(allowed_moves or context.charter.allowed_moves or [])
        raw: List[MoveCandidate] = []
        for spec in self.all_specs():
            if allowed and spec.legacy_move not in allowed and spec.move_family not in allowed:
                continue
            for candidate in spec.generator(context):
                raw.append(candidate)
        return _dedupe_candidates(raw)


def _dedupe_candidates(candidates: Sequence[MoveCandidate]) -> List[MoveCandidate]:
    deduped: Dict[str, MoveCandidate] = {}
    for candidate in candidates:
        existing = deduped.get(candidate.signature)
        if existing is None:
            deduped[candidate.signature] = candidate
            continue
        current_score = candidate.novelty_score + candidate.reuse_potential + candidate.transfer_score - candidate.duplicate_penalty
        existing_score = existing.novelty_score + existing.reuse_potential + existing.transfer_score - existing.duplicate_penalty
        if current_score > existing_score:
            deduped[candidate.signature] = candidate
    return sorted(
        deduped.values(),
        key=lambda item: (
            -(item.novelty_score + item.reuse_potential + item.obstruction_targeting + item.transfer_score),
            item.no_signal_penalty,
            item.move_family,
            item.signature,
        ),
    )


def _legacy_underspecify(context: MoveGenerationContext) -> List[MoveCandidate]:
    if context.prior_family_count("legacy.underspecify") > 0 and context.active_no_signal_count < 5:
        return []
    return [
        MoveCandidate(
            move_family="legacy.underspecify",
            legacy_move="underspecify",
            parameters={"mode": "minimal_context"},
            objective="Fill in all sorries. Strip imports to expose hidden dependencies. Report intermediate lemmas or unresolved goals.",
            expected_signal="Surface hidden assumptions and early lemma needs.",
            rationale="Minimal context is the safest first pass for exposing missing structure.",
            novelty_score=1.1,
            reuse_potential=0.8,
            diversity_group="mapping",
            generation_metadata={"legacy_move": True},
        )
    ]


def _assumption_perturbations(context: MoveGenerationContext) -> List[MoveCandidate]:
    candidates: List[MoveCandidate] = []
    for assumption in context.conjecture.assumptions:
        if assumption in context.tested_assumptions():
            continue
        candidates.append(
            MoveCandidate(
                move_family="legacy.perturb_assumption",
                legacy_move="perturb_assumption",
                parameters={"assumption": assumption, "operation": "remove"},
                objective=f"Fill in all sorries. The assumption '{assumption}' has been removed. Determine whether the proof still closes and report the blocker if not.",
                expected_signal="Measure assumption sensitivity and classify the blocker.",
                rationale=f"Assumption '{assumption}' has not yet been stress-tested under verification pressure.",
                novelty_score=0.9,
                reuse_potential=0.8,
                obstruction_targeting=1.2 if assumption in context.conjecture.critical_assumptions else 0.7,
                diversity_group="assumption_boundary",
            )
        )
    return candidates


def _promote_lemma(context: MoveGenerationContext) -> List[MoveCandidate]:
    recurring = context.recurring_lemmas_for_conjecture() or context.recurring_lemmas
    if not recurring:
        return []
    lemma = sorted(recurring, key=lambda item: (-item["reuse_count"], item["representative_statement"]))[0]
    if lemma["reuse_count"] < context.charter.promotion_threshold and not context.recurring_subgoals:
        return []
    statement = lemma["representative_statement"]
    return [
        MoveCandidate(
            move_family="legacy.promote_lemma",
            legacy_move="promote_lemma",
            parameters={"lemma_statement": statement},
            objective="Fill in all sorries. This lemma was promoted from a recurring intermediate result. Prove it as a standalone theorem.",
            expected_signal="Determine whether the recurring helper captures real mathematical structure.",
            rationale=f"Recurring lemma '{statement}' crossed the promotion threshold.",
            novelty_score=0.8,
            reuse_potential=1.5,
            obstruction_targeting=0.8,
            diversity_group="reuse",
            generation_metadata={"reuse_count": lemma["reuse_count"]},
        )
    ]


def _reformulations(context: MoveGenerationContext) -> List[MoveCandidate]:
    forms = context.conjecture.equivalent_forms or ["equivalent reformulation"]
    candidates: List[MoveCandidate] = []
    for form in forms[:2]:
        candidates.append(
            MoveCandidate(
                move_family="legacy.reformulate" if "equivalent" in form else "equivalent_view",
                legacy_move="reformulate",
                parameters={"form": form},
                objective=f"Fill in all sorries. This is a reformulation as {form}. Determine whether this form is easier or harder to prove and report intermediate progress.",
                expected_signal="Separate structural difficulty from representation-specific difficulty.",
                rationale=f"Equivalent form '{form}' may expose different proof obligations.",
                novelty_score=0.8,
                reuse_potential=0.9,
                diversity_group="reformulation",
            )
        )
    return candidates


def _counterexample_search(context: MoveGenerationContext) -> List[MoveCandidate]:
    counter_count = context.legacy_move_count("counterexample_mode")
    target = COUNTEREXAMPLE_TARGETS[counter_count % len(COUNTEREXAMPLE_TARGETS)]
    repeated_unknown = sum(
        1
        for item in context.effective_conjecture_experiments
        if item["status"] == "stalled" and item.get("proof_outcome") == "unknown" and not (item.get("new_signal_count") or 0)
    )
    structural_count = sum(
        1
        for item in context.effective_conjecture_experiments
        if item["status"] in {"failed", "stalled"} and item.get("blocker_type") == "structural"
    )
    low_eval = context.recent_evaluation_average()
    boost = 0.5 if structural_count >= 2 or repeated_unknown >= 2 or (low_eval and low_eval < 1.5) else 0.0
    return [
        MoveCandidate(
            move_family="legacy.counterexample_mode",
            legacy_move="counterexample_mode",
            parameters={"target": target, "attempt": counter_count + 1},
            objective=f"Fill in all sorries. Search for a counterexample or independence witness for the {target.replace('_', ' ')}.",
            expected_signal="Disambiguate falsehood from search failure.",
            rationale="A targeted counterexample pass helps separate true obstruction from solver drift.",
            novelty_score=0.6 + boost,
            reuse_potential=0.4,
            obstruction_targeting=1.3 + boost,
            diversity_group="boundary",
            generation_metadata={"evaluation_average": low_eval},
        )
    ]


def _invariant_mining(context: MoveGenerationContext) -> List[MoveCandidate]:
    blockers = context.semantic_counter("blocker")
    traces = context.semantic_counter("proof_trace")
    if not blockers and not traces:
        return []
    signal = sorted((blockers + traces).items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
    evaluation_average = context.recent_evaluation_average()
    return [
        MoveCandidate(
            move_family="invariant_mining",
            legacy_move="promote_lemma",
            parameters={"invariant_hint": signal},
            objective=f"Fill in all sorries. Mine a reusable invariant or monotonicity principle that explains the recurring signal '{signal}'.",
            expected_signal="Extract a reusable invariant from repeated blockers or proof motifs.",
            rationale=f"Recurring semantic signal '{signal}' suggests a hidden invariant worth isolating.",
            novelty_score=1.2 + (0.2 if evaluation_average >= 2.5 else 0.0),
            reuse_potential=1.4,
            obstruction_targeting=0.9,
            diversity_group="reuse",
            generation_metadata={"evaluation_average": evaluation_average},
        )
    ]


def _extremal_case(context: MoveGenerationContext) -> List[MoveCandidate]:
    goals = context.semantic_counter("goal")
    if not goals and not context.conjecture.equivalent_forms:
        return []
    target = sorted(goals.items(), key=lambda pair: (-pair[1], pair[0]))[0][0] if goals else "extremal parameter boundary"
    return [
        MoveCandidate(
            move_family="extremal_case",
            legacy_move="reformulate",
            parameters={"extremal_target": target},
            objective=f"Fill in all sorries. Reformulate the conjecture around the extremal or boundary case suggested by '{target}'.",
            expected_signal="Expose whether the hard regime is genuinely extremal or an artifact of presentation.",
            rationale="Recurring unresolved goals often hide the true extremal regime.",
            novelty_score=1.0,
            reuse_potential=0.7,
            obstruction_targeting=1.1,
            diversity_group="boundary",
        )
    ]


def _decompose_subclaim(context: MoveGenerationContext) -> List[MoveCandidate]:
    if not context.recurring_subgoals:
        return []
    statement = context.recurring_subgoals[0]["statement"]
    return [
        MoveCandidate(
            move_family="decompose_subclaim",
            legacy_move="promote_lemma",
            parameters={"subclaim": statement},
            objective="Fill in all sorries. Split the current theorem into a bridge lemma and a remaining reduction built around the recurring subgoal.",
            expected_signal="Convert repeated subgoal pressure into a reusable bridge lemma candidate.",
            rationale=f"Recurring subgoal '{statement}' is ready to be isolated as its own bridge claim.",
            novelty_score=0.9,
            reuse_potential=1.4,
            obstruction_targeting=1.0,
            diversity_group="reuse",
        )
    ]


def _adversarial_counterexample(context: MoveGenerationContext) -> List[MoveCandidate]:
    witnesses = context.semantic_counter("counterexample")
    blockers = context.semantic_counter("blocker")
    target = ""
    if witnesses:
        target = sorted(witnesses.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
    elif blockers:
        target = sorted(blockers.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
    if not target:
        return []
    return [
        MoveCandidate(
            move_family="adversarial_counterexample",
            legacy_move="counterexample_mode",
            parameters={"target": target, "mode": "adversarial"},
            objective=f"Fill in all sorries. Construct an adversarial witness that sharpens or refutes the blocker pattern '{target}'.",
            expected_signal="Stress-test the current obstruction with a deliberately adversarial witness search.",
            rationale=f"Observed witness/blocker '{target}' can be sharpened with a targeted adversarial run.",
            novelty_score=0.9,
            reuse_potential=0.5,
            obstruction_targeting=1.5,
            diversity_group="boundary",
        )
    ]


def _witness_minimization(context: MoveGenerationContext) -> List[MoveCandidate]:
    witnesses = context.semantic_counter("counterexample")
    if not witnesses:
        return []
    witness = sorted(witnesses.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
    return [
        MoveCandidate(
            move_family="witness_minimization",
            legacy_move="counterexample_mode",
            parameters={"witness_target": witness, "mode": "minimize"},
            objective=f"Fill in all sorries. Minimize the witness or blocker around '{witness}' to identify the sharp boundary case.",
            expected_signal="Turn a coarse witness into a sharp obstruction description.",
            rationale=f"Witness '{witness}' should be minimized before treating it as a decisive obstruction.",
            novelty_score=0.8,
            reuse_potential=0.6,
            obstruction_targeting=1.3,
            diversity_group="boundary",
        )
    ]


def _transfer_reformulation(context: MoveGenerationContext) -> List[MoveCandidate]:
    hints = context.transfer_hints()
    if not hints:
        return []
    hint = hints[0]
    return [
        MoveCandidate(
            move_family="transfer_reformulation",
            legacy_move="reformulate",
            parameters={
                "source_conjecture_id": hint["source_conjecture_id"],
                "source_domain": hint["source_domain"],
                "artifact": hint["artifact"],
            },
            objective=f"Fill in all sorries. Reformulate the current conjecture using the transferable artifact '{hint['artifact']}' from {hint['source_domain']}.",
            expected_signal="Test whether reusable structure transfers across theorem families or adjacent domains.",
            rationale=f"Reusable signal from {hint['source_conjecture_id']} suggests a cross-family transfer opportunity.",
            novelty_score=1.0,
            reuse_potential=1.1,
            obstruction_targeting=0.7,
            transfer_score=1.5,
            diversity_group="transfer",
            generation_metadata={"transfer_hint": hint},
        )
    ]


def default_move_registry() -> MoveRegistry:
    registry = MoveRegistry()
    registry.register(MoveFamilySpec("legacy.counterexample_mode", "counterexample_mode", "Legacy counterexample search", ["target", "attempt"], _counterexample_search))
    registry.register(MoveFamilySpec("legacy.promote_lemma", "promote_lemma", "Legacy lemma promotion", ["lemma_statement"], _promote_lemma))
    registry.register(MoveFamilySpec("legacy.perturb_assumption", "perturb_assumption", "Legacy perturb assumption", ["assumption", "operation"], _assumption_perturbations))
    registry.register(MoveFamilySpec("legacy.reformulate", "reformulate", "Legacy equivalent reformulation", ["form"], _reformulations))
    registry.register(MoveFamilySpec("legacy.underspecify", "underspecify", "Legacy minimal-context probe", ["mode"], _legacy_underspecify))
    registry.register(MoveFamilySpec("adversarial_counterexample", "counterexample_mode", "Adversarial witness search", ["target", "mode"], _adversarial_counterexample))
    registry.register(MoveFamilySpec("decompose_subclaim", "promote_lemma", "Split theorem into bridge subclaims", ["subclaim"], _decompose_subclaim))
    registry.register(MoveFamilySpec("equivalent_view", "reformulate", "Alternative equivalent view generation", ["form"], _reformulations))
    registry.register(MoveFamilySpec("extremal_case", "reformulate", "Extremal-case exploration", ["extremal_target"], _extremal_case))
    registry.register(MoveFamilySpec("invariant_mining", "promote_lemma", "Mine reusable invariants", ["invariant_hint"], _invariant_mining))
    registry.register(MoveFamilySpec("transfer_reformulation", "reformulate", "Cross-family transfer-aware reformulation", ["source_conjecture_id", "source_domain", "artifact"], _transfer_reformulation))
    registry.register(MoveFamilySpec("witness_minimization", "counterexample_mode", "Minimize boundary witnesses", ["witness_target", "mode"], _witness_minimization))
    return registry


DEFAULT_MOVE_REGISTRY = default_move_registry()
