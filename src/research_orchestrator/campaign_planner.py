from __future__ import annotations

import re
from hashlib import sha1
from typing import List

from research_orchestrator.types import (
    CampaignBudgetPolicy,
    CampaignSpec,
    Conjecture,
    DiscoveryQuestion,
    ProjectCharter,
    RuntimePolicy,
)


DEFAULT_ALLOWED_MOVES = [
    "underspecify",
    "perturb_assumption",
    "reformulate",
    "promote_lemma",
    "promote_subgoal",
    "promote_trace",
    "boundary_map_from_witness",
    "boundary_map_from_missing_assumption",
    "counterexample_mode",
]


def _canonicalize_prompt(prompt: str) -> str:
    normalized = prompt.strip()
    lowered = normalized.lower()
    erdos_match = re.fullmatch(r"erdos problem (\d+)", lowered)
    if erdos_match:
        number = erdos_match.group(1)
        return (
            f"Erdos problem {number}. Build an autonomous verification-driven research campaign for this Erdos problem, "
            f"treating theorem proving as discovery of recurring lemmas, boundary cases, obstructions, and reusable formal subgoals."
        )
    return normalized


def _slugify(text: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return lowered or "campaign"


def _sentences(prompt: str) -> List[str]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", prompt.strip()) if part.strip()]
    return parts or [prompt.strip()]


def _title_from_prompt(prompt: str) -> str:
    head = _sentences(prompt)[0]
    return head[:100].rstrip(".")


def _domain_scope(prompt: str) -> List[str]:
    lowered = prompt.lower()
    matches = []
    if "erdos" in lowered:
        matches.extend(["combinatorics", "number theory"])
    for term in (
        "combinatorics",
        "number theory",
        "graph theory",
        "algebra",
        "topology",
        "analysis",
        "probability",
        "logic",
        "geometry",
        "order theory",
    ):
        if term in lowered:
            matches.append(term)
    return matches or ["mathematics", "formal verification"]


def _assumptions_from_prompt(prompt: str) -> List[str]:
    assumptions = []
    for token in re.findall(r"\b(?:assume|assuming|under|with)\s+([a-zA-Z0-9_-]+)", prompt):
        normalized = re.sub(r"[^a-zA-Z0-9_-]+", "_", token).strip("_").lower()
        if normalized and normalized not in assumptions:
            assumptions.append(normalized)
    return assumptions[:5]


def _equivalent_forms(prompt: str) -> List[str]:
    forms = []
    lowered = prompt.lower()
    if "reformulate" in lowered or "equivalent" in lowered:
        forms.append("equivalent reformulation")
    if "extremal" in lowered:
        forms.append("extremal reformulation")
    if "probabilistic" in lowered:
        forms.append("probabilistic reformulation")
    return forms or ["equivalent reformulation", "boundary-case reformulation"]


def synthesize_campaign(prompt: str) -> tuple[CampaignSpec, ProjectCharter, list[Conjecture], list[DiscoveryQuestion]]:
    normalized_prompt = _canonicalize_prompt(prompt)
    if len(normalized_prompt) < 20:
        raise ValueError("Campaign prompt is too short to synthesize a stable research campaign.")

    title = _title_from_prompt(normalized_prompt)
    digest = sha1(normalized_prompt.encode("utf-8")).hexdigest()[:8]
    project_id = f"campaign-{_slugify(title)[:24]}-{digest}"
    mission = (
        "Grow a verified discovery graph around the starting problem by surfacing reusable lemmas, "
        "recurring subgoals, fragile assumptions, and boundary conditions."
    )
    theorem_family = _sentences(normalized_prompt)[:3]
    domain_scope = _domain_scope(normalized_prompt)

    budget_policy = CampaignBudgetPolicy()
    runtime_policy = RuntimePolicy()
    spec = CampaignSpec(
        project_id=project_id,
        version="v1",
        title=title,
        raw_prompt=normalized_prompt,
        mission=mission,
        theorem_family=theorem_family,
        success_criteria=[
            "Grow the verified discovery graph with reusable mathematical structure.",
            "Map assumption sensitivity and boundary conditions.",
            "Promote recurring verified subgoals into theorem candidates.",
            "Separate search failure from structural obstruction and falsehood.",
        ],
        non_goals=[
            "Do not optimize only for proving the initial statement.",
            "Do not treat one failed proof attempt as evidence of falsity.",
            "Do not let text-only summaries outrun Lean or reproducible artifacts.",
        ],
        allowed_moves=DEFAULT_ALLOWED_MOVES[:],
        phase_order=[],
        domain_scope=domain_scope,
        budget_policy=budget_policy,
        runtime_policy=runtime_policy,
        planner_notes=[
            "Synthesized from a single natural-language prompt.",
            "Verification-backed discovery takes precedence over theorem-only progress.",
        ],
    )

    charter = ProjectCharter(
        project_id=project_id,
        title=title,
        overarching_problem=normalized_prompt,
        success_criteria=spec.success_criteria[:],
        non_goals=spec.non_goals[:],
        allowed_moves=spec.allowed_moves[:],
        phase_order=[],
        domain_scope=domain_scope,
        evaluator_weights={
            "information_gain": 1.3,
            "novelty": 1.0,
            "reusability": 1.35,
            "boundary_sharpness": 1.15,
            "cost_penalty": 0.6,
        },
        human_preferences={
            "prefer_information_gain_over_proof_probability": True,
            "verification_as_discovery": True,
            "require_artifact_backed_conclusions": True,
        },
    )

    conjecture = Conjecture(
        conjecture_id=f"{project_id}-main",
        project_id=project_id,
        name=f"{title} main campaign conjecture",
        domain=domain_scope[0],
        natural_language=normalized_prompt,
        lean_statement="theorem campaign_target : True := by\n  sorry\n",
        assumptions=_assumptions_from_prompt(normalized_prompt),
        critical_assumptions=_assumptions_from_prompt(normalized_prompt)[:2],
        hidden_dependencies=[
            "core_bridge_lemma",
            "boundary_case_reduction",
            "verification_friendly_reformulation",
        ],
        equivalent_forms=_equivalent_forms(normalized_prompt),
        candidate_transfer_domains=domain_scope[1:3],
    )

    questions = [
        DiscoveryQuestion(
            question_id=f"{project_id}-dq-1",
            project_id=project_id,
            conjecture_id=conjecture.conjecture_id,
            category="dependency_mapping",
            question="Which hidden lemmas or missing assumptions does minimal formal context force us to rediscover?",
            rationale="Start by using verification pressure to expose hidden structure instead of aiming only for a full proof.",
            priority=100,
        ),
        DiscoveryQuestion(
            question_id=f"{project_id}-dq-2",
            project_id=project_id,
            conjecture_id=conjecture.conjecture_id,
            category="assumption_boundary",
            question="Which assumptions appear structurally necessary once they are perturbed under formal verification?",
            rationale="Assumption sensitivity is one of the highest-value discovery modes for the campaign.",
            priority=90,
        ),
        DiscoveryQuestion(
            question_id=f"{project_id}-dq-3",
            project_id=project_id,
            conjecture_id=conjecture.conjecture_id,
            category="reformulation",
            question="Which reformulation sharpens the proof boundary or exposes recurring unresolved subgoals?",
            rationale="Alternative formulations often turn proof failures into reusable mathematical structure.",
            priority=80,
        ),
    ]
    return spec, charter, [conjecture], questions
