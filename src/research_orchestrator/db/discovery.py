"""Discovery graph operations including nodes, edges, and result ingestion."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional

from research_orchestrator.db.utils import utcnow
from research_orchestrator.lemma_utils import goal_fingerprint
from research_orchestrator.semantic_memory import canonicalize_text, hydrate_semantic_summary
from research_orchestrator.types import (
    SemanticMemorySummary,
    VerificationRecord,
    VerificationSignal,
)
from research_orchestrator.schema_versions import (
    VERIFICATION_SCHEMA_VERSION,
    SEMANTIC_MEMORY_VERSION,
)


class DatabaseDiscoveryMixin:
    """Mixin for discovery graph and result ingestion operations."""

    def upsert_discovery_node(
        self,
        *,
        project_id: str,
        node_type: str,
        label: str,
        conjecture_id: str = "",
        experiment_id: str = "",
        confidence: float = 0.5,
        provenance_kind: str = "inferred",
        provenance_ref: str = "",
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create or update a discovery graph node."""
        import uuid

        metadata_json = json.dumps(metadata or {})
        row = self.conn.execute(
            """
            SELECT node_id FROM discovery_graph_nodes
            WHERE project_id = ? AND node_type = ? AND label = ?
            """,
            (project_id, node_type, label),
        ).fetchone()
        now = utcnow()
        if row is not None:
            node_id = row["node_id"]
            self.conn.execute(
                """
                UPDATE discovery_graph_nodes
                SET confidence = MAX(confidence, ?),
                    status = ?,
                    conjecture_id = COALESCE(NULLIF(?, ''), conjecture_id),
                    experiment_id = COALESCE(NULLIF(?, ''), experiment_id),
                    provenance_kind = ?,
                    provenance_ref = ?,
                    metadata_json = ?,
                    updated_at = ?
                WHERE node_id = ?
                """,
                (
                    confidence,
                    status,
                    conjecture_id,
                    experiment_id,
                    provenance_kind,
                    provenance_ref,
                    metadata_json,
                    now,
                    node_id,
                ),
            )
        else:
            node_id = str(uuid.uuid4())
            self.conn.execute(
                """
                INSERT INTO discovery_graph_nodes(
                    node_id, project_id, conjecture_id, experiment_id, node_type, label, status,
                    confidence, provenance_kind, provenance_ref, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    node_id,
                    project_id,
                    conjecture_id or None,
                    experiment_id or None,
                    node_type,
                    label,
                    status,
                    confidence,
                    provenance_kind,
                    provenance_ref,
                    metadata_json,
                    now,
                    now,
                ),
            )
        self.conn.commit()
        return node_id

    def create_discovery_edge(
        self,
        *,
        project_id: str,
        source_node_id: str,
        target_node_id: str,
        relation: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a discovery graph edge if it doesn't already exist."""
        import uuid

        existing = self.conn.execute(
            """
            SELECT edge_id FROM discovery_graph_edges
            WHERE project_id = ? AND source_node_id = ? AND target_node_id = ? AND relation = ?
            """,
            (project_id, source_node_id, target_node_id, relation),
        ).fetchone()
        if existing is not None:
            return
        self.conn.execute(
            """
            INSERT INTO discovery_graph_edges(edge_id, project_id, source_node_id, target_node_id, relation, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                source_node_id,
                target_node_id,
                relation,
                json.dumps(metadata or {}),
                utcnow(),
            ),
        )
        self.conn.commit()

    def list_discovery_nodes(
        self, project_id: str, node_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List discovery nodes for a project."""
        params: List[Any] = [project_id]
        query = "SELECT * FROM discovery_graph_nodes WHERE project_id = ?"
        if node_type is not None:
            query += " AND node_type = ?"
            params.append(node_type)
        query += " ORDER BY confidence DESC, created_at ASC"
        rows = self.conn.execute(query, params).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata_json"])
            items.append(item)
        return items

    def list_discovery_edges(self, project_id: str) -> List[Dict[str, Any]]:
        """List discovery edges for a project."""
        rows = self.conn.execute(
            "SELECT * FROM discovery_graph_edges WHERE project_id = ? ORDER BY created_at ASC",
            (project_id,),
        ).fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item["metadata"] = json.loads(item["metadata_json"])
            items.append(item)
        return items

    def record_result_ingestion(
        self,
        project_id: str,
        conjecture_id: str,
        experiment_id: str,
        proof_outcome: str,
        blocker_type: str,
        unresolved_goals: Iterable[str],
        artifact_inventory: Iterable[Dict[str, Any]],
        signal_summary: str,
        proof_trace_fragments: Iterable[str] = (),
        counterexample_witnesses: Iterable[str] = (),
        discovery_question_id: str = "",
        verification_signals: Iterable[VerificationSignal] = (),
        verification_record: Optional[VerificationRecord] = None,
        semantic_summary: Optional[SemanticMemorySummary] = None,
        theorem_family: str = "",
    ) -> SemanticMemorySummary:
        """Record result ingestion, creating semantic objects and discovery nodes."""
        import uuid

        verification_signals = list(verification_signals)
        semantic_summary = semantic_summary or SemanticMemorySummary()
        if not semantic_summary.artifacts:
            semantic_summary.artifacts = [
                canonicalize_text("goal", goal, theorem_family) for goal in unresolved_goals
            ] + [
                canonicalize_text("proof_trace", fragment, theorem_family) for fragment in proof_trace_fragments
            ] + [
                canonicalize_text("counterexample", witness, theorem_family) for witness in counterexample_witnesses
            ] + (
                [canonicalize_text("blocker", blocker_type, theorem_family)]
                if blocker_type and blocker_type != "unknown"
                else []
            )

        # Clear existing records for this experiment
        self.conn.execute("DELETE FROM extracted_subgoals WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM artifact_metadata WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM blocker_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM proof_trace_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM counterexample_observations WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM semantic_occurrences WHERE experiment_id = ?", (experiment_id,))
        self.conn.execute("DELETE FROM verification_records WHERE experiment_id = ?", (experiment_id,))

        # Insert extracted subgoals
        for goal in unresolved_goals:
            normalized_goal, _ = goal_fingerprint(goal)
            self.conn.execute(
                """
                INSERT INTO extracted_subgoals(subgoal_id, project_id, conjecture_id, experiment_id, statement, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    normalized_goal or goal,
                    "result_ingestion",
                    utcnow(),
                ),
            )

        # Insert artifact metadata
        for artifact in artifact_inventory:
            self.conn.execute(
                """
                INSERT INTO artifact_metadata(artifact_id, experiment_id, path, kind, size_bytes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    experiment_id,
                    artifact.get("path", ""),
                    artifact.get("kind", "file"),
                    int(artifact.get("size_bytes", 0) or 0),
                    utcnow(),
                ),
            )

        # Insert blocker observation
        self.conn.execute(
            """
            INSERT INTO blocker_observations(blocker_observation_id, project_id, conjecture_id, experiment_id, blocker_type, proof_outcome, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                project_id,
                conjecture_id,
                experiment_id,
                blocker_type,
                proof_outcome,
                signal_summary,
                utcnow(),
            ),
        )

        # Insert proof trace observations
        for fragment in proof_trace_fragments:
            normalized_fragment, _ = goal_fingerprint(fragment)
            self.conn.execute(
                """
                INSERT INTO proof_trace_observations(trace_id, project_id, conjecture_id, experiment_id, fragment, normalized_fragment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    fragment,
                    normalized_fragment or fragment,
                    utcnow(),
                ),
            )

        # Insert counterexample observations
        for witness in counterexample_witnesses:
            normalized_witness, _ = goal_fingerprint(witness)
            self.conn.execute(
                """
                INSERT INTO counterexample_observations(witness_id, project_id, conjecture_id, experiment_id, witness_text, normalized_witness, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    project_id,
                    conjecture_id,
                    experiment_id,
                    witness,
                    normalized_witness or witness,
                    utcnow(),
                ),
            )

        # Insert verification record if present
        if verification_record is not None:
            self.conn.execute(
                """
                INSERT INTO verification_records(
                    record_id, experiment_id, schema_version, provider_name, verification_status,
                    theorem_status, validation_ok, record_json, raw_payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    experiment_id,
                    verification_record.schema_version,
                    verification_record.provider.provider_name,
                    verification_record.verification_status,
                    verification_record.theorem_status,
                    0 if verification_record.validation_issues else 1,
                    json.dumps(asdict(verification_record)),
                    json.dumps(verification_record.raw_payload),
                    utcnow(),
                ),
            )

        # Process semantic artifacts
        exact_reuse = 0
        canonical_reuse = 0
        new_exact = 0
        blocker_reuse = 0
        for artifact in semantic_summary.artifacts:
            object_row = self.conn.execute(
                """
                SELECT object_id, occurrence_count
                FROM semantic_objects
                WHERE project_id = ? AND kind = ? AND canonical_hash = ?
                """,
                (project_id, artifact.kind, artifact.canonical_id),
            ).fetchone()
            if object_row is None:
                object_id = str(uuid.uuid4())
                self.conn.execute(
                    """
                    INSERT INTO semantic_objects(
                        object_id, project_id, kind, canonical_hash, canonical_text,
                        representative_text, theorem_family, normalization_version,
                        occurrence_count, first_seen_at, last_seen_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        object_id,
                        project_id,
                        artifact.kind,
                        artifact.canonical_id,
                        artifact.canonical_text,
                        artifact.raw_text,
                        theorem_family,
                        SEMANTIC_MEMORY_VERSION,
                        1,
                        utcnow(),
                        utcnow(),
                        json.dumps(artifact.metadata),
                    ),
                )
                match_type = "new_exact"
                new_exact += 1
            else:
                object_id = object_row["object_id"]
                exact_row = self.conn.execute(
                    """
                    SELECT 1
                    FROM semantic_occurrences
                    WHERE object_id = ? AND exact_hash = ?
                    LIMIT 1
                    """,
                    (object_id, artifact.exact_id),
                ).fetchone()
                match_type = "exact_reuse" if exact_row is not None else "normalized_equivalent_reuse"
                if exact_row is not None:
                    exact_reuse += 1
                else:
                    canonical_reuse += 1
                if artifact.kind == "blocker":
                    blocker_reuse += 1
                self.conn.execute(
                    """
                    UPDATE semantic_objects
                    SET occurrence_count = occurrence_count + 1, last_seen_at = ?
                    WHERE object_id = ?
                    """,
                    (utcnow(), object_id),
                )
            self.conn.execute(
                """
                INSERT INTO semantic_occurrences(
                    occurrence_id, object_id, project_id, conjecture_id, experiment_id,
                    exact_hash, exact_text, match_type, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    object_id,
                    project_id,
                    conjecture_id,
                    experiment_id,
                    artifact.exact_id,
                    artifact.raw_text,
                    match_type,
                    json.dumps(artifact.metadata),
                    utcnow(),
                ),
            )

        semantic_summary.new_exact_count = new_exact
        semantic_summary.exact_reuse_count = exact_reuse
        semantic_summary.canonical_reuse_count = canonical_reuse
        semantic_summary.blocker_reuse_count = blocker_reuse

        # Link discovery question to results
        question_node_id = ""
        if discovery_question_id:
            question_rows = self.conn.execute(
                "SELECT * FROM discovery_questions WHERE question_id = ?",
                (discovery_question_id,),
            ).fetchone()
            if question_rows is not None:
                question = dict(question_rows)
                question_node_id = self.upsert_discovery_node(
                    project_id=project_id,
                    node_type="discovery_question",
                    label=question["question"],
                    conjecture_id=conjecture_id,
                    experiment_id=experiment_id,
                    confidence=1.0,
                    provenance_kind="manager",
                    provenance_ref=discovery_question_id,
                    metadata={
                        "category": question["category"],
                        "priority": question["priority"],
                        "rationale": question["rationale"],
                    },
                )
                self.mark_discovery_question_status(discovery_question_id, "answered", node_id=question_node_id)

        # Create discovery nodes for verification signals
        for signal in verification_signals:
            node_id = self.upsert_discovery_node(
                project_id=signal.project_id,
                node_type=signal.signal_type,
                label=signal.label,
                conjecture_id=signal.conjecture_id,
                experiment_id=signal.experiment_id,
                confidence=signal.confidence,
                provenance_kind=signal.provenance[0].kind if signal.provenance else "artifact",
                provenance_ref=signal.provenance[0].path if signal.provenance else "",
                metadata={
                    "detail": signal.detail,
                    "metadata": signal.metadata,
                    "provenance": [item.__dict__ for item in signal.provenance],
                },
            )
            if question_node_id:
                self.create_discovery_edge(
                    project_id=project_id,
                    source_node_id=question_node_id,
                    target_node_id=node_id,
                    relation="answered_by",
                    metadata={"experiment_id": experiment_id},
                )
            # Create experiment node
            experiment_node_id = self.upsert_discovery_node(
                project_id=project_id,
                node_type="experiment",
                label=experiment_id,
                conjecture_id=conjecture_id,
                experiment_id=experiment_id,
                confidence=1.0,
                provenance_kind="execution",
                provenance_ref=experiment_id,
                metadata={"proof_outcome": proof_outcome, "blocker_type": blocker_type},
            )
            self.create_discovery_edge(
                project_id=project_id,
                source_node_id=experiment_node_id,
                target_node_id=node_id,
                relation="produced_signal",
                metadata={"proof_outcome": proof_outcome},
            )

        # Add audit event
        self.add_audit_event(
            project_id=project_id,
            experiment_id=experiment_id,
            event_type="result_ingested",
            detail={
                "proof_outcome": proof_outcome,
                "blocker_type": blocker_type,
                "signal_summary": signal_summary,
                "verification_signal_count": len(verification_signals),
                "verification_schema_version": verification_record.schema_version if verification_record else VERIFICATION_SCHEMA_VERSION,
                "semantic_objects": len(semantic_summary.artifacts),
            },
        )
        self.conn.commit()
        return semantic_summary
