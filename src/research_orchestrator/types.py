from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class VerificationSchemaVersion(str, Enum):
    V1 = "1.0"


class VerificationStatus(str, Enum):
    PROVED = "proved"
    PARTIAL = "partial"
    DISPROVED = "disproved"
    STALLED = "stalled"
    UNKNOWN = "unknown"
    AUTH_FAILURE = "auth_failure"
    INFRA_FAILURE = "infra_failure"
    MALFORMED = "malformed"


class TheoremStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    REFUTED = "refuted"
    UNRESOLVED = "unresolved"
    INVALID = "invalid"


class VerificationArtifactKind(str, Enum):
    LEMMA = "lemma"
    GOAL = "goal"
    BLOCKER = "blocker"
    COUNTEREXAMPLE = "counterexample"
    PROOF_TRACE = "proof_trace"
    ASSUMPTION = "assumption"


class ValidationSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


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
    theorem_family_id: str = ""
    assumptions: List[str] = field(default_factory=list)
    critical_assumptions: List[str] = field(default_factory=list)
    hidden_dependencies: List[str] = field(default_factory=list)
    equivalent_forms: List[str] = field(default_factory=list)
    candidate_transfer_domains: List[str] = field(default_factory=list)
    family_metadata: Dict[str, Any] = field(default_factory=dict)


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
    move_family: str = ""
    move_family_version: str = "v1"
    theorem_family_id: str = ""
    move_title: str = ""
    rationale: str = ""
    candidate_metadata: Dict[str, Any] = field(default_factory=dict)
    discovery_question_id: str = ""
    discovery_question: str = ""


@dataclass
class ArtifactProvenance:
    kind: str
    path: str
    source: str
    confidence: float = 1.0


@dataclass
class ProviderMetadata:
    provider_name: str
    adapter_name: str = "legacy-text-adapter"
    adapter_version: str = ""
    provider_status: str = ""
    provider_blocker_type: str = ""
    external_id: str = ""
    external_status: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationRunMetadata:
    parser_version: str = ""
    evaluator_version: str = ""
    semantic_memory_version: str = ""
    schema_version: str = VerificationSchemaVersion.V1.value
    run_id: str = ""
    workspace_dir: str = ""
    lean_file: str = ""
    artifact_paths: List[str] = field(default_factory=list)
    raw_stdout_excerpt: str = ""
    raw_stderr_excerpt: str = ""
    notes: str = ""
    timestamps: Dict[str, str] = field(default_factory=dict)


@dataclass
class VerificationObservation:
    text: str
    artifact_kind: str
    normalized_text: str = ""
    canonical_id: str = ""
    cluster_id: str = ""
    detail: str = ""
    confidence: float = 0.5
    provenance: List[ArtifactProvenance] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationValidationIssue:
    issue_type: str
    detail: str
    severity: str = ValidationSeverity.ERROR.value
    path: str = ""


@dataclass
class VerificationRecord:
    schema_version: str = VerificationSchemaVersion.V1.value
    provider: ProviderMetadata = field(default_factory=lambda: ProviderMetadata(provider_name="unknown"))
    run: VerificationRunMetadata = field(default_factory=VerificationRunMetadata)
    verification_status: str = VerificationStatus.UNKNOWN.value
    theorem_status: str = TheoremStatus.UNRESOLVED.value
    unsolved_goals: List[VerificationObservation] = field(default_factory=list)
    generated_lemmas: List[VerificationObservation] = field(default_factory=list)
    proved_lemmas: List[VerificationObservation] = field(default_factory=list)
    missing_assumptions: List[VerificationObservation] = field(default_factory=list)
    counterexamples: List[VerificationObservation] = field(default_factory=list)
    blocker_observations: List[VerificationObservation] = field(default_factory=list)
    proof_traces: List[VerificationObservation] = field(default_factory=list)
    artifact_provenance: List[ArtifactProvenance] = field(default_factory=list)
    raw_text_fallback: Dict[str, str] = field(default_factory=dict)
    raw_payload: Dict[str, Any] = field(default_factory=dict)
    validation_issues: List[VerificationValidationIssue] = field(default_factory=list)


@dataclass
class SemanticArtifact:
    kind: str
    raw_text: str
    canonical_text: str
    exact_id: str
    canonical_id: str
    cluster_id: str
    theorem_family: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticMemorySummary:
    artifacts: List[SemanticArtifact] = field(default_factory=list)
    new_exact_count: int = 0
    normalized_equivalent_count: int = 0
    exact_reuse_count: int = 0
    canonical_reuse_count: int = 0
    blocker_reuse_count: int = 0
    duplicate_artifact_count: int = 0
    parser_ambiguity_count: int = 0
    reusable_artifact_count: int = 0
    obstruction_artifact_count: int = 0
    boundary_artifact_count: int = 0
    proof_motif_count: int = 0
    by_kind: Dict[str, Dict[str, int]] = field(default_factory=dict)


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
    verification_record: Optional[VerificationRecord] = None
    semantic_summary: Optional[SemanticMemorySummary] = None


@dataclass
class PreparedIngestion:
    provider_result: ProviderResult
    verification_record: VerificationRecord
    semantic_summary: SemanticMemorySummary
    validation_issues: List[VerificationValidationIssue] = field(default_factory=list)


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
    obstruction_discovery: float = 0.0
    transfer_potential: float = 0.0
    duplication_penalty: float = 0.0
    ambiguity_penalty: float = 0.0
    notes: List[str] = field(default_factory=list)
