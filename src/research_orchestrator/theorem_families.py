from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Protocol

from research_orchestrator.types import Conjecture


class TheoremFamilyAdapter(Protocol):
    family_id: str
    display_name: str

    def supports(self, conjecture: Conjecture) -> bool: ...

    def canonical_family_name(self, conjecture: Conjecture) -> str: ...

    def family_metadata(self, conjecture: Conjecture) -> Dict[str, object]: ...

    def materialize_source(self, conjecture: Conjecture, move_family: str, modification: Dict[str, object], header: List[str]) -> str: ...

    def transfer_targets(self, conjecture: Conjecture) -> List[str]: ...


@dataclass(frozen=True)
class BaseFamilyAdapter:
    family_id: str
    display_name: str

    def supports(self, conjecture: Conjecture) -> bool:
        return self.family_id == infer_theorem_family_id(conjecture)

    def canonical_family_name(self, conjecture: Conjecture) -> str:
        return conjecture.theorem_family_id or self.family_id

    def family_metadata(self, conjecture: Conjecture) -> Dict[str, object]:
        return {
            "family_id": self.family_id,
            "display_name": self.display_name,
            "domain": conjecture.domain,
            "transfer_targets": self.transfer_targets(conjecture),
        }

    def materialize_source(
        self,
        conjecture: Conjecture,
        move_family: str,
        modification: Dict[str, object],
        header: List[str],
    ) -> str:
        body = conjecture.lean_statement
        return "\n".join(header + [body])

    def transfer_targets(self, conjecture: Conjecture) -> List[str]:
        return list(conjecture.candidate_transfer_domains)


@dataclass(frozen=True)
class WeightedMonotoneFamilyAdapter(BaseFamilyAdapter):
    family_id: str = "weighted_monotone"
    display_name: str = "Weighted Monotone Thresholds"

    def materialize_source(
        self,
        conjecture: Conjecture,
        move_family: str,
        modification: Dict[str, object],
        header: List[str],
    ) -> str:
        body = conjecture.lean_statement
        prefix = [
            "-- weighted-monotone family workspace",
            "-- focus: chain decompositions, threshold structure, and order-sensitive witnesses",
        ]
        if move_family == "invariant_mining":
            prefix.append(f"-- mine invariant: {modification.get('invariant_hint', 'chain monotonicity')}")
        elif move_family == "decompose_subclaim":
            prefix.append(f"-- bridge lemma target: {modification.get('subclaim', 'chain decomposition bridge')}")
        elif move_family == "witness_minimization":
            prefix.append(f"-- minimize witness around blocker: {modification.get('witness_target', 'threshold obstruction')}")
        return "\n".join(header + prefix + [body])


@dataclass(frozen=True)
class ErdosFamilyAdapter(BaseFamilyAdapter):
    family_id: str = "erdos_problem"
    display_name: str = "Erdos Problem Family"

    def materialize_source(
        self,
        conjecture: Conjecture,
        move_family: str,
        modification: Dict[str, object],
        header: List[str],
    ) -> str:
        body = conjecture.lean_statement
        prefix = [
            "-- erdos family workspace",
            "-- focus: extremal constructions, additive structure, and parameter boundary behavior",
        ]
        if conjecture.conjecture_id == "erdos-123":
            prefix.append("-- erdos-123 focus: d-completeness, divisibility antichains, and reusable covering lemmas")
        if move_family == "extremal_case":
            prefix.append(f"-- extremal sweep: {modification.get('extremal_target', 'maximal density boundary')}")
        elif move_family == "invariant_mining":
            prefix.append(f"-- invariant target: {modification.get('invariant_hint', 'covering-to-antichain upgrade')}")
        elif move_family == "decompose_subclaim":
            prefix.append(f"-- bridge lemma target: {modification.get('subclaim', 'covering or antichain extraction lemma')}")
        elif move_family == "equivalent_view":
            prefix.append(f"-- equivalent view: {modification.get('form', 'antichain-friendly reformulation')}")
        elif move_family == "adversarial_counterexample":
            prefix.append(f"-- adversarial target: {modification.get('target', 'small counterexample')}")
        elif move_family == "witness_minimization":
            prefix.append(f"-- witness minimization target: {modification.get('witness_target', 'sharp boundary witness')}")
        elif move_family == "transfer_reformulation":
            prefix.append(f"-- transfer source: {modification.get('source_domain', 'related Erdos motif')}")
        return "\n".join(header + prefix + [body])


def infer_theorem_family_id(conjecture: Conjecture) -> str:
    if conjecture.theorem_family_id:
        return conjecture.theorem_family_id
    lowered_name = f"{conjecture.conjecture_id} {conjecture.name} {conjecture.domain}".lower()
    if "erdos" in lowered_name or "ramsey" in lowered_name or "sidon" in lowered_name:
        return "erdos_problem"
    if "weighted monotone" in lowered_name or "preorder" in conjecture.lean_statement.lower():
        return "weighted_monotone"
    return "generic_theorem_family"


class GenericFamilyAdapter(BaseFamilyAdapter):
    family_id = "generic_theorem_family"
    display_name = "Generic Theorem Family"


_FAMILIES: List[TheoremFamilyAdapter] = [
    WeightedMonotoneFamilyAdapter(),
    ErdosFamilyAdapter(),
    GenericFamilyAdapter("generic_theorem_family", "Generic Theorem Family"),
]


def registered_family_adapters() -> List[TheoremFamilyAdapter]:
    return list(_FAMILIES)


def resolve_theorem_family_adapter(conjecture: Conjecture) -> TheoremFamilyAdapter:
    for adapter in _FAMILIES:
        if adapter.supports(conjecture):
            return adapter
    return _FAMILIES[-1]


def encode_family_metadata(conjecture: Conjecture) -> Dict[str, object]:
    adapter = resolve_theorem_family_adapter(conjecture)
    return adapter.family_metadata(conjecture)
