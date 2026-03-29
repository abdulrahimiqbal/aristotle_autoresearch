from __future__ import annotations

import hashlib

from research_orchestrator.providers.base import Provider
from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter, ProviderResult


class MockProvider(Provider):
    name = "mock"

    def _seed(self, text: str) -> int:
        return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % 1000

    def run(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        hidden = list(conjecture.hidden_dependencies)
        critical = set(conjecture.critical_assumptions)
        assumption = brief.modification.get("assumption")
        seed = self._seed(brief.experiment_id + brief.move)

        if brief.move == "underspecify":
            generated = hidden[:2] or ["minimal_context_bridge_lemma"]
            return ProviderResult(
                status="stalled",
                blocker_type="formalization",
                generated_lemmas=generated,
                proved_lemmas=[],
                unresolved_goals=["Need a chain-decomposition bridge lemma."],
                suspected_missing_assumptions=conjecture.assumptions[:1],
                notes="Minimal context forced the proof attempt to reconstruct missing dependencies.",
                confidence=0.72,
            )

        if brief.move == "perturb_assumption":
            if assumption in critical:
                return ProviderResult(
                    status="stalled",
                    blocker_type="structural",
                    generated_lemmas=hidden[:1],
                    proved_lemmas=[],
                    unresolved_goals=[f"The bound no longer closes cleanly without {assumption}."],
                    suspected_missing_assumptions=[assumption],
                    notes=f"Removing {assumption} created a sharp boundary change.",
                    confidence=0.84,
                )
            return ProviderResult(
                status="stalled",
                blocker_type="search",
                generated_lemmas=hidden[:2],
                proved_lemmas=[],
                unresolved_goals=[f"Search did not settle the role of {assumption}."],
                suspected_missing_assumptions=[],
                notes=f"Removing {assumption} did not immediately reveal structural failure.",
                confidence=0.61,
            )

        if brief.move == "promote_lemma":
            lemma = brief.modification["lemma_statement"]
            return ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                generated_lemmas=[],
                proved_lemmas=[lemma],
                unresolved_goals=[],
                suspected_missing_assumptions=[],
                notes="The recurring helper lemma can stand as its own theorem candidate.",
                confidence=0.88,
            )

        if brief.move == "reformulate":
            form = brief.modification.get("form", "equivalent reformulation")
            proved = hidden[:1] or ["reformulation_bridge_lemma"]
            generated = hidden[1:3] if len(hidden) > 1 else ["packing_to_chain_equivalence"]
            return ProviderResult(
                status="succeeded",
                blocker_type="unknown",
                generated_lemmas=generated,
                proved_lemmas=proved,
                unresolved_goals=[],
                suspected_missing_assumptions=[],
                notes=f"The {form} made one dependency easier to prove directly.",
                confidence=0.79,
            )

        if brief.move == "counterexample_mode":
            outcome = "failed" if seed % 2 == 0 else "stalled"
            return ProviderResult(
                status=outcome,
                blocker_type="unknown" if outcome == "stalled" else "malformed",
                generated_lemmas=[],
                proved_lemmas=[],
                unresolved_goals=["Need a concrete witness or model."] if outcome == "stalled" else [],
                suspected_missing_assumptions=[],
                notes="Counterexample mode could not yet separate falsehood from under-specification."
                if outcome == "stalled"
                else "The variant appears malformed under the current assumptions.",
                confidence=0.55,
            )

        return ProviderResult(
            status="failed",
            blocker_type="unknown",
            notes="Unknown move.",
            confidence=0.1,
        )
