from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from uuid import uuid4

from research_orchestrator.schema_versions import EVALUATOR_VERSION, SEMANTIC_MEMORY_VERSION, VERIFICATION_PARSER_VERSION, VERIFICATION_SCHEMA_VERSION
from research_orchestrator.semantic_memory import canonicalize_text
from research_orchestrator.types import (
    ArtifactProvenance,
    PreparedIngestion,
    ProviderMetadata,
    ProviderResult,
    SemanticMemorySummary,
    TheoremStatus,
    ValidationSeverity,
    VerificationArtifactKind,
    VerificationObservation,
    VerificationRecord,
    VerificationSchemaVersion,
    VerificationSignal,
    VerificationStatus,
    VerificationValidationIssue,
    VerificationRunMetadata,
)


THEOREM_PATTERN = re.compile(r"^\s*(?:theorem|lemma)\s+(.*)$", re.MULTILINE)
INTERMEDIATE_PATTERN = re.compile(r"^\s*(?:have|suffices)\s+([A-Za-z0-9_'.]+)?\s*:?\s*(.*)$", re.MULTILINE)
GOAL_PATTERN = re.compile(r"(?im)^(?:unsolved\s+goal|goal|required goal|need|show|prove)\s*:?\s*(.+)$")
BLOCKED_ON_PATTERN = re.compile(r"(?im)^(?:blocked on|requires|need|stuck on|waiting on)\s*:?\s*(.+)$")
MISSING_ASSUMPTION_PATTERN = re.compile(r"(?im)^(?:missing assumption|assumption needed|requires assumption)\s*:?\s*(.+)$")
COUNTEREXAMPLE_PATTERN = re.compile(r"(?im)^(?:counterexample|witness|minimal witness|smallest witness)\s*:?\s*(.+)$")
TRACE_PATTERN = re.compile(r"(?im)^(?:have|suffices|try|tactic|reduce to|it suffices to show)\s*:?\s*(.+)$")
GENERATED_LEMMA_PATTERN = re.compile(r"(?im)^(?:generated lemma|lemma candidate|candidate lemma)\s*:?\s*(.+)$")

PROVED_HINTS = ("proof complete", "all goals solved", "qed", "no goals remaining", "proved theorem")
DISPROVED_HINTS = ("counterexample", "falsified", "contradiction found", "disproved")
PARTIAL_HINTS = ("partial proof", "generated lemma", "reduced to lemma", "it suffices to show", "enough to prove")
AUTH_HINTS = ("invalid api key", "check your api key", "get a valid api key")
INFRA_HINTS = ("could not resolve host", "nodename nor servname provided", "connection refused", "network is unreachable")
PATH_HINTS = ("cli executable was not found on path", "permission denied", "not found on path")
TOOLCHAIN_HINTS = ("lean-toolchain", "no lean files", "toolchain")
TRACEBACK_HINTS = ("traceback", "exception:")
TIMEOUT_HINTS = ("timeout", "time budget", "resource exhausted", "search budget", "maximum recursion", "too many heartbeats")
MALFORMED_HINTS = ("cli executable was not found on path",)


class VerificationParser:
    """Parser for verification output that extracts structured information."""

    def __init__(self, raw_output: str):
        self.raw_output = raw_output
        self.lines = raw_output.splitlines()
        self.artifacts: List[VerificationObservation] = []
        self.proved_lemmas: List[VerificationObservation] = []
        self.generated_lemmas: List[VerificationObservation] = []
        self.unsolved_goals: List[VerificationObservation] = []
        self.blocker_observations: List[VerificationObservation] = []
        self.counterexamples: List[VerificationObservation] = []
        self.proof_traces: List[VerificationObservation] = []
        self.missing_assumptions: List[VerificationObservation] = []

    def parse(self) -> VerificationRecord:
        """Parse the raw output and return a structured verification record."""
        self._extract_theorems_and_lemmas()
        self._extract_goals()
        self._extract_blockers()
        self._extract_missing_assumptions()
        self._extract_counterexamples()
        self._extract_proof_traces()
        self._classify_artifacts()

        return VerificationRecord(
            schema_version=VerificationSchemaVersion.V1.value,
            verification_status=self._determine_verification_status().value,
            theorem_status=self._determine_theorem_status().value,
            raw_text_fallback={"output": self.raw_output},
            proved_lemmas=self.proved_lemmas,
            generated_lemmas=self.generated_lemmas,
            unsolved_goals=self.unsolved_goals,
            blocker_observations=self.blocker_observations,
            counterexamples=self.counterexamples,
            proof_traces=self.proof_traces,
            missing_assumptions=self.missing_assumptions,
            artifact_provenance=[
                ArtifactProvenance(
                    kind="raw_output",
                    path="",
                    source="verification_parser",
                    confidence=0.7,
                )
            ],
        )

    def _extract_theorems_and_lemmas(self) -> None:
        """Extract theorem and lemma statements from the output."""
        for match in THEOREM_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement:
                self.artifacts.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.LEMMA.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.LEMMA.value, statement).canonical_id,
                    )
                )

        for match in GENERATED_LEMMA_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement:
                self.generated_lemmas.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.LEMMA.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.LEMMA.value, statement).canonical_id,
                    )
                )

    def _extract_goals(self) -> None:
        """Extract unsolved goals from the output."""
        for match in GOAL_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement and len(statement) > 10:
                self.unsolved_goals.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.GOAL.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.GOAL.value, statement).canonical_id,
                    )
                )

    def _extract_blockers(self) -> None:
        """Extract blocker observations from the output."""
        for match in BLOCKED_ON_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement:
                self.blocker_observations.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.BLOCKER.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.BLOCKER.value, statement).canonical_id,
                    )
                )

    def _extract_missing_assumptions(self) -> None:
        """Extract missing assumption observations from the output."""
        for match in MISSING_ASSUMPTION_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement:
                self.missing_assumptions.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.ASSUMPTION.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.ASSUMPTION.value, statement).canonical_id,
                    )
                )

    def _extract_counterexamples(self) -> None:
        """Extract counterexample observations from the output."""
        for match in COUNTEREXAMPLE_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement:
                self.counterexamples.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.COUNTEREXAMPLE.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.COUNTEREXAMPLE.value, statement).canonical_id,
                    )
                )

    def _extract_proof_traces(self) -> None:
        """Extract proof trace fragments from the output."""
        for match in TRACE_PATTERN.finditer(self.raw_output):
            statement = match.group(1).strip()
            if statement and len(statement) > 5:
                self.proof_traces.append(
                    VerificationObservation(
                        artifact_kind=VerificationArtifactKind.PROOF_TRACE.value,
                        text=statement,
                        canonical_id=canonicalize_text(VerificationArtifactKind.PROOF_TRACE.value, statement).canonical_id,
                    )
                )

    def _classify_artifacts(self) -> None:
        """Classify artifacts based on proof hints in the output."""
        raw_lower = self.raw_output.lower()

        if any(hint in raw_lower for hint in PROVED_HINTS):
            for artifact in self.artifacts:
                if artifact.artifact_kind == VerificationArtifactKind.LEMMA.value:
                    self.proved_lemmas.append(artifact)
        elif any(hint in raw_lower for hint in DISPROVED_HINTS):
            pass

    def _determine_verification_status(self) -> VerificationStatus:
        """Determine the overall verification status from the output."""
        raw_lower = self.raw_output.lower()

        if any(hint in raw_lower for hint in AUTH_HINTS):
            return VerificationStatus.AUTH_FAILURE
        if any(hint in raw_lower for hint in INFRA_HINTS):
            return VerificationStatus.INFRA_FAILURE
        if any(hint in raw_lower for hint in PATH_HINTS):
            return VerificationStatus.INFRA_FAILURE
        if any(hint in raw_lower for hint in TOOLCHAIN_HINTS):
            return VerificationStatus.INFRA_FAILURE
        if any(hint in raw_lower for hint in TRACEBACK_HINTS):
            return VerificationStatus.INFRA_FAILURE
        if any(hint in raw_lower for hint in TIMEOUT_HINTS):
            return VerificationStatus.INFRA_FAILURE

        if any(hint in raw_lower for hint in PROVED_HINTS):
            return VerificationStatus.PROVED
        if any(hint in raw_lower for hint in DISPROVED_HINTS):
            return VerificationStatus.DISPROVED
        if any(hint in raw_lower for hint in PARTIAL_HINTS):
            return VerificationStatus.PARTIAL
        if self.blocker_observations:
            return VerificationStatus.STALLED

        return VerificationStatus.UNKNOWN

    def _determine_theorem_status(self) -> TheoremStatus:
        """Determine the theorem status based on verification status."""
        verification = self._determine_verification_status()
        mapping = {
            VerificationStatus.PROVED: TheoremStatus.VERIFIED,
            VerificationStatus.PARTIAL: TheoremStatus.PARTIALLY_VERIFIED,
            VerificationStatus.DISPROVED: TheoremStatus.REFUTED,
            VerificationStatus.STALLED: TheoremStatus.UNRESOLVED,
            VerificationStatus.UNKNOWN: TheoremStatus.UNRESOLVED,
            VerificationStatus.AUTH_FAILURE: TheoremStatus.INVALID,
            VerificationStatus.INFRA_FAILURE: TheoremStatus.INVALID,
            VerificationStatus.MALFORMED: TheoremStatus.INVALID,
        }
        return mapping.get(verification, TheoremStatus.UNRESOLVED)


def parse_verification_output(raw_output: str) -> VerificationRecord:
    """Parse raw verification output into a structured record."""
    parser = VerificationParser(raw_output)
    return parser.parse()


def validate_verification_record(record: VerificationRecord) -> List[VerificationValidationIssue]:
    """Validate a verification record and return any issues found."""
    issues: List[VerificationValidationIssue] = []

    if not record:
        issues.append(
            VerificationValidationIssue(
                issue_type="missing_record",
                severity=ValidationSeverity.ERROR.value,
                detail="Verification record is empty",
                path="record",
            )
        )
        return issues

    # Check if record has content (either raw_payload or structured data)
    has_content = (
        record.raw_payload
        or record.proved_lemmas
        or record.generated_lemmas
        or record.unsolved_goals
        or record.raw_text_fallback
    )
    if not has_content:
        issues.append(
            VerificationValidationIssue(
                issue_type="missing_payload",
                severity=ValidationSeverity.ERROR.value,
                detail="Verification record is empty or missing payload",
                path="raw_payload",
            )
        )

    if record.verification_status == VerificationStatus.UNKNOWN.value:
        issues.append(
            VerificationValidationIssue(
                issue_type="unknown_status",
                severity=ValidationSeverity.WARNING.value,
                detail="Verification status is unknown - could not determine outcome",
                path="verification_status",
            )
        )

    # Check for invalid status values
    valid_statuses = {status.value for status in VerificationStatus}
    if record.verification_status not in valid_statuses:
        issues.append(
            VerificationValidationIssue(
                issue_type="invalid_status",
                severity=ValidationSeverity.ERROR.value,
                detail=f"Invalid verification status: {record.verification_status}",
                path="verification_status",
            )
        )

    return issues


def prepare_ingested_result(result: ProviderResult) -> PreparedIngestion:
    """Prepare a provider result for ingestion into the system."""
    if result.verification_record is None:
        # Combine stdout and stderr for parsing (either may contain relevant signals)
        combined_output = ""
        if result.raw_stdout:
            combined_output += result.raw_stdout
        if result.raw_stderr:
            combined_output += "\n" + result.raw_stderr if combined_output else result.raw_stderr
        if combined_output:
            result.verification_record = parse_verification_output(combined_output)

    record = result.verification_record
    if record is None:
        record = VerificationRecord(
            schema_version=VerificationSchemaVersion.V1.value,
            verification_status=VerificationStatus.MALFORMED.value,
            theorem_status=TheoremStatus.INVALID.value,
            raw_text_fallback={"output": result.raw_stdout or ""},
        )

    issues = validate_verification_record(record)

    semantic_summary = SemanticMemorySummary(
        exact_reuse_count=0,
        canonical_reuse_count=0,
        normalized_equivalent_count=0,
        new_exact_count=len(record.proved_lemmas) + len(record.generated_lemmas),
        artifacts=[
            {
                "kind": obs.artifact_kind,
                "text": obs.text,
                "canonical_id": obs.canonical_id,
            }
            for obs in (
                record.proved_lemmas
                + record.generated_lemmas
                + record.unsolved_goals
                + record.blocker_observations
            )
        ],
    )

    enriched = result
    enriched.verification_record = record
    enriched.proof_outcome = record.verification_status
    enriched.blocker_type = (
        record.blocker_observations[0].text[:50]
        if record.blocker_observations
        else "unknown"
    )
    enriched.unresolved_goals = [goal.text for goal in record.unsolved_goals]
    enriched.proved_lemmas = [lemma.text for lemma in record.proved_lemmas]
    enriched.generated_lemmas = [lemma.text for lemma in record.generated_lemmas]
    enriched.proof_trace_fragments = [trace.text for trace in record.proof_traces]
    enriched.counterexample_witnesses = [cx.text for cx in record.counterexamples]
    enriched.artifact_inventory = {
        "proved_lemmas": len(record.proved_lemmas),
        "generated_lemmas": len(record.generated_lemmas),
        "unsolved_goals": len(record.unsolved_goals),
        "blockers": len(record.blocker_observations),
        "counterexamples": len(record.counterexamples),
        "proof_traces": len(record.proof_traces),
    }
    enriched.new_signal_count = sum(1 for item in semantic_summary.artifacts if item["canonical_id"])
    enriched.reused_signal_count = semantic_summary.normalized_equivalent_count + semantic_summary.exact_reuse_count
    enriched.signal_summary = _summary_for(enriched, record, semantic_summary)
    if not enriched.notes:
        enriched.notes = enriched.signal_summary
    return PreparedIngestion(
        provider_result=enriched,
        verification_record=record,
        semantic_summary=semantic_summary,
        validation_issues=issues,
    )


def ingest_provider_result(result: ProviderResult) -> ProviderResult:
    return prepare_ingested_result(result).provider_result


def build_verification_signals(
    *,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> list[VerificationSignal]:
    record = result.verification_record
    if record is None:
        record = prepare_ingested_result(result).verification_record
    provenance = record.artifact_provenance or [ArtifactProvenance(kind="stdout", path="", source="provider_result", confidence=0.55)]
    signals: list[VerificationSignal] = []

    for lemma in record.proved_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="verified_lemma",
                label=lemma.text,
                detail="Structured verification record marked this lemma as proved.",
                confidence=0.95,
                provenance=lemma.provenance or provenance,
                metadata={"canonical_id": lemma.canonical_id},
            )
        )
    for lemma in record.generated_lemmas:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="reproducible_candidate_lemma",
                label=lemma.text,
                detail="Structured verification record surfaced a reusable generated lemma.",
                confidence=0.75,
                provenance=lemma.provenance or provenance,
                metadata={"canonical_id": lemma.canonical_id},
            )
        )
    for goal in record.unsolved_goals:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="recurring_subgoal",
                label=goal.text,
                detail="Structured verification retained this unsolved goal as a discovery object.",
                confidence=0.8,
                provenance=goal.provenance or provenance,
                metadata={"canonical_id": goal.canonical_id},
            )
        )
    for assumption in record.missing_assumptions:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="assumption_boundary",
                label=assumption.text,
                detail=f"Potentially necessary assumption under outcome={record.verification_status}.",
                confidence=0.78,
                provenance=assumption.provenance or provenance,
                metadata={"canonical_id": assumption.canonical_id},
            )
        )
    for witness in record.counterexamples:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="counterexample_witness",
                label=witness.text,
                detail="Structured verification captured a falsifying or fragility witness.",
                confidence=0.85,
                provenance=witness.provenance or provenance,
                metadata={"canonical_id": witness.canonical_id},
            )
        )
    for trace in record.proof_traces:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="proof_trace_fragment",
                label=trace.text[:100],
                detail="Proof trace fragment captured from structured output.",
                confidence=0.8,
                provenance=trace.provenance or provenance,
                metadata={"canonical_id": trace.canonical_id},
            )
        )
    for blocker in record.blocker_observations:
        signals.append(
            VerificationSignal(
                signal_id=str(uuid4()),
                project_id=project_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                signal_type="formalization_blocker" if "failure" not in record.verification_status else "infra_incident",
                label=blocker.text,
                detail=result.signal_summary or result.notes,
                confidence=0.9,
                provenance=blocker.provenance or provenance,
                metadata={"canonical_id": blocker.canonical_id, "proof_outcome": result.proof_outcome},
            )
        )
    return signals


def save_proved_lemmas_to_ledger(
    db,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> None:
    """Save proved lemmas from a provider result to the proof ledger.

    This extracts proved lemmas from the verification record and adds them
    to the cumulative proof ledger for reuse across experiments.
    """
    record = result.verification_record
    if record is None:
        return

    for lemma in record.proved_lemmas:
        if not lemma.text or not lemma.canonical_id:
            continue

        # Check if already proved to avoid duplicates
        if db.lemma_is_proved(lemma.canonical_id):
            continue

        db.add_proof_ledger_entry(
            entry_id=str(uuid4()),
            project_id=project_id,
            conjecture_id=conjecture_id,
            experiment_id=experiment_id,
            lemma_statement=lemma.text,
            lemma_hash=lemma.canonical_id,
            proof_status="proved",
            proof_lean_code=lemma.raw_lean_code if hasattr(lemma, "raw_lean_code") else None,
            dependencies=[],  # TODO: extract dependencies from proof
        )


def extract_obligations_from_result(
    db,
    project_id: str,
    conjecture_id: str,
    experiment_id: str,
    result: ProviderResult,
) -> List[str]:
    """Extract proof obligations from a provider result and add to DAG.

    This creates obligation nodes from unsolved goals, blockers, and other
    incomplete proof states, linking them into the obligation DAG.

    Returns:
        List of created obligation IDs
    """
    record = result.verification_record
    if record is None:
        return []

    created_obligations: List[str] = []

    # Create obligations from unsolved goals (subgoals to prove)
    for goal in record.unsolved_goals:
        if not goal.text:
            continue

        # Generate a hash for deduplication
        goal_hash = goal.canonical_id or hashlib.sha256(goal.text.encode()).hexdigest()[:16]

        # Check if this obligation already exists
        existing = db.conn.execute(
            "SELECT 1 FROM proof_obligations WHERE statement_hash = ? AND conjecture_id = ? AND status = 'open'",
            (goal_hash, conjecture_id)
        ).fetchone()

        if existing:
            continue

        obligation_id = str(uuid4())
        db.add_obligation(
            obligation_id=obligation_id,
            project_id=project_id,
            conjecture_id=conjecture_id,
            statement=goal.text,
            statement_hash=goal_hash,
            source_experiment_id=experiment_id,
            priority=1,  # Base priority for subgoals
        )
        created_obligations.append(obligation_id)

    # Create obligations from blocker observations
    for blocker in record.blocker_observations:
        if not blocker.text:
            continue

        blocker_hash = blocker.canonical_id or hashlib.sha256(blocker.text.encode()).hexdigest()[:16]

        existing = db.conn.execute(
            "SELECT 1 FROM proof_obligations WHERE statement_hash = ? AND conjecture_id = ? AND status = 'open'",
            (blocker_hash, conjecture_id)
        ).fetchone()

        if existing:
            continue

        obligation_id = str(uuid4())
        db.add_obligation(
            obligation_id=obligation_id,
            project_id=project_id,
            conjecture_id=conjecture_id,
            statement=f"Resolve blocker: {blocker.text}",
            statement_hash=blocker_hash,
            source_experiment_id=experiment_id,
            priority=2,  # Higher priority for blockers
        )
        created_obligations.append(obligation_id)

    return created_obligations


def _summary_for(result: ProviderResult, record: VerificationRecord, semantic: SemanticMemorySummary) -> str:
    parts: List[str] = []
    parts.append(f"Outcome: {result.proof_outcome}")
    parts.append(f"Artifacts: {len(semantic.artifacts)} total")
    if record.proved_lemmas:
        parts.append(f"Proved: {len(record.proved_lemmas)}")
    if record.generated_lemmas:
        parts.append(f"Generated: {len(record.generated_lemmas)}")
    if record.unsolved_goals:
        parts.append(f"Goals: {len(record.unsolved_goals)}")
    if record.blocker_observations:
        parts.append(f"Blockers: {len(record.blocker_observations)}")
    return "; ".join(parts)
