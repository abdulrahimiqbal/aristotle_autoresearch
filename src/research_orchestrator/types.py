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
class CampaignBudgetPolicy:
    max_active_jobs: int = 5
    max_total_experiments: int = 25
    max_retries_per_error: int = 3
    max_consecutive_failures: int = 5
    hard_cost_limit_usd: float = 25.0
    cooldown_seconds: int = 300


@dataclass
class RuntimePolicy:
    runtime: str = "cloud-worker"
    autonomy_mode: str = "full_auto"
    verification_mode: str = "lean_artifact_first"
    pause_on_incident: bool = False
    artifact_retention_days: int = 30


@dataclass
class CampaignSpec:
    project_id: str
    version: str
    title: str
    raw_prompt: str
    mission: str
    theorem_family: List[str]
    success_criteria: List[str]
    non_goals: List[str]
    allowed_moves: List[str]
    phase_order: List[str]
    domain_scope: List[str] = field(default_factory=list)
    budget_policy: CampaignBudgetPolicy = field(default_factory=CampaignBudgetPolicy)
    runtime_policy: RuntimePolicy = field(default_factory=RuntimePolicy)
    planner_notes: List[str] = field(default_factory=list)


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
    discovery_question_id: str = ""
    discovery_question: str = ""


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
    proof_trace_fragments: List[str] = field(default_factory=list)
    counterexample_witnesses: List[str] = field(default_factory=list)
    normalized_candidate_lemmas: List[str] = field(default_factory=list)
    normalized_unresolved_goals: List[str] = field(default_factory=list)
    new_signal_count: int = 0
    reused_signal_count: int = 0
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
class DiscoveryQuestion:
    question_id: str
    project_id: str
    conjecture_id: str
    category: str
    question: str
    rationale: str
    priority: int = 50
    status: str = "open"
    node_id: str = ""


@dataclass
class ArtifactProvenance:
    kind: str
    path: str
    source: str
    confidence: float = 1.0


@dataclass
class VerificationSignal:
    signal_id: str
    project_id: str
    conjecture_id: str
    experiment_id: str
    signal_type: str
    label: str
    detail: str = ""
    confidence: float = 0.5
    provenance: List[ArtifactProvenance] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IncidentRecord:
    incident_id: str
    project_id: str
    experiment_id: str = ""
    incident_type: str = "unknown"
    severity: str = "warning"
    detail: str = ""
    status: str = "open"


@dataclass
class EvaluationScore:
    information_gain: float
    novelty: float
    reusability: float
    boundary_sharpness: float
    cost_penalty: float
    total: float
    notes: List[str] = field(default_factory=list)
