from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectCharter:
    project_id: str
    title: str
    overarching_problem: str
    success_criteria: List[str]
    non_goals: List[str]
    allowed_moves: List[str]
    phase_order: List[str]
    promotion_threshold: int = 3
    domain_scope: List[str] = field(default_factory=list)
    evaluator_weights: Dict[str, float] = field(default_factory=dict)
    human_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conjecture:
    conjecture_id: str
    project_id: str
    name: str
    domain: str
    natural_language: str
    lean_statement: str
    assumptions: List[str] = field(default_factory=list)
    critical_assumptions: List[str] = field(default_factory=list)
    hidden_dependencies: List[str] = field(default_factory=list)
    equivalent_forms: List[str] = field(default_factory=list)
    candidate_transfer_domains: List[str] = field(default_factory=list)


@dataclass
class ExperimentBrief:
    experiment_id: str
    project_id: str
    conjecture_id: str
    phase: str
    move: str
    objective: str
    expected_signal: str
    modification: Dict[str, Any]
    workspace_dir: str
    lean_file: str


@dataclass
class ProviderResult:
    status: str
    blocker_type: str
    proof_outcome: str = "unknown"
    signal_summary: str = ""
    generated_lemmas: List[str] = field(default_factory=list)
    proved_lemmas: List[str] = field(default_factory=list)
    candidate_lemmas: List[str] = field(default_factory=list)
    unresolved_goals: List[str] = field(default_factory=list)
    blocked_on: List[str] = field(default_factory=list)
    missing_assumptions: List[str] = field(default_factory=list)
    artifact_inventory: List[Dict[str, Any]] = field(default_factory=list)
    suspected_missing_assumptions: List[str] = field(default_factory=list)
    notes: str = ""
    confidence: float = 0.5
    raw_stdout: str = ""
    raw_stderr: str = ""
    artifacts: List[str] = field(default_factory=list)
    external_id: str = ""
    external_status: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationScore:
    information_gain: float
    novelty: float
    reusability: float
    boundary_sharpness: float
    cost_penalty: float
    total: float
    notes: List[str] = field(default_factory=list)
