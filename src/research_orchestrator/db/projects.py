"""Project, Charter, Campaign, Conjecture, and Discovery Question operations."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from research_orchestrator.db.utils import utcnow
from research_orchestrator.types import (
    CampaignSpec,
    Conjecture,
    DiscoveryQuestion,
    ProjectCharter,
)


class DatabaseProjectsMixin:
    """Mixin for project, charter, campaign, and conjecture operations."""

    def save_project(self, charter: ProjectCharter) -> None:
        """Save a project with its charter."""
        self.conn.execute(
            """
            INSERT INTO projects(project_id, title, charter_json, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                title = excluded.title,
                charter_json = excluded.charter_json
            """,
            (
                charter.project_id,
                charter.title,
                json.dumps(charter.__dict__),
                utcnow(),
            ),
        )
        self.conn.commit()

    def save_campaign_spec(self, spec: CampaignSpec) -> None:
        """Save a campaign specification."""
        now = utcnow()
        self.conn.execute(
            """
            INSERT OR REPLACE INTO campaign_specs(project_id, version, raw_prompt, spec_json, created_at, updated_at)
            VALUES (
                ?, ?, ?, ?,
                COALESCE((SELECT created_at FROM campaign_specs WHERE project_id = ?), ?),
                ?
            )
            """,
            (
                spec.project_id,
                spec.version,
                spec.raw_prompt,
                json.dumps(
                    {
                        **spec.__dict__,
                        "budget_policy": spec.budget_policy.__dict__,
                        "runtime_policy": spec.runtime_policy.__dict__,
                    }
                ),
                spec.project_id,
                now,
                now,
            ),
        )
        self.conn.commit()

    def get_campaign_spec(self, project_id: str) -> Optional[CampaignSpec]:
        """Retrieve a campaign spec by project ID."""
        row = self.conn.execute(
            "SELECT spec_json FROM campaign_specs WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        data = json.loads(row["spec_json"])
        from research_orchestrator.types import CampaignBudgetPolicy, RuntimePolicy
        data["budget_policy"] = CampaignBudgetPolicy(**data.get("budget_policy", {}))
        data["runtime_policy"] = RuntimePolicy(**data.get("runtime_policy", {}))
        return CampaignSpec(**data)

    def save_conjecture(self, conjecture: Conjecture) -> None:
        """Save a conjecture."""
        metadata = {
            "theorem_family_id": conjecture.theorem_family_id,
            "assumptions": conjecture.assumptions,
            "critical_assumptions": conjecture.critical_assumptions,
            "hidden_dependencies": conjecture.hidden_dependencies,
            "equivalent_forms": conjecture.equivalent_forms,
            "candidate_transfer_domains": conjecture.candidate_transfer_domains,
            "family_metadata": conjecture.family_metadata,
        }
        self.conn.execute(
            """
            INSERT OR REPLACE INTO conjectures(
                conjecture_id, project_id, name, domain, natural_language, lean_statement, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM conjectures WHERE conjecture_id = ?), ?))
            """,
            (
                conjecture.conjecture_id,
                conjecture.project_id,
                conjecture.name,
                conjecture.domain,
                conjecture.natural_language,
                conjecture.lean_statement,
                json.dumps(metadata),
                conjecture.conjecture_id,
                utcnow(),
            ),
        )
        self.conn.commit()

    def get_charter(self, project_id: str) -> ProjectCharter:
        """Retrieve project charter by ID."""
        row = self.conn.execute(
            "SELECT charter_json FROM projects WHERE project_id = ?",
            (project_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown project_id: {project_id}")
        return ProjectCharter(**json.loads(row["charter_json"]))

    def get_conjecture(self, conjecture_id: str) -> Conjecture:
        """Retrieve a conjecture by ID."""
        row = self.conn.execute(
            "SELECT * FROM conjectures WHERE conjecture_id = ?",
            (conjecture_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown conjecture_id: {conjecture_id}")
        metadata = json.loads(row["metadata_json"])
        return Conjecture(
            conjecture_id=row["conjecture_id"],
            project_id=row["project_id"],
            name=row["name"],
            domain=row["domain"],
            natural_language=row["natural_language"],
            lean_statement=row["lean_statement"],
            theorem_family_id=metadata.get("theorem_family_id", ""),
            assumptions=metadata.get("assumptions", []),
            critical_assumptions=metadata.get("critical_assumptions", []),
            hidden_dependencies=metadata.get("hidden_dependencies", []),
            equivalent_forms=metadata.get("equivalent_forms", []),
            candidate_transfer_domains=metadata.get("candidate_transfer_domains", []),
            family_metadata=metadata.get("family_metadata", {}),
        )

    def list_conjectures(self, project_id: str) -> List[Conjecture]:
        """List all conjectures for a project."""
        rows = self.conn.execute(
            "SELECT * FROM conjectures WHERE project_id = ?",
            (project_id,),
        ).fetchall()
        result = []
        for row in rows:
            metadata = json.loads(row["metadata_json"])
            result.append(
                Conjecture(
                    conjecture_id=row["conjecture_id"],
                    project_id=row["project_id"],
                    name=row["name"],
                    domain=row["domain"],
                    natural_language=row["natural_language"],
                    lean_statement=row["lean_statement"],
                    theorem_family_id=metadata.get("theorem_family_id", ""),
                    assumptions=metadata.get("assumptions", []),
                    critical_assumptions=metadata.get("critical_assumptions", []),
                    hidden_dependencies=metadata.get("hidden_dependencies", []),
                    equivalent_forms=metadata.get("equivalent_forms", []),
                    candidate_transfer_domains=metadata.get("candidate_transfer_domains", []),
                    family_metadata=metadata.get("family_metadata", {}),
                )
            )
        return result

    def save_discovery_question(self, question: DiscoveryQuestion) -> None:
        """Save a discovery question."""
        now = utcnow()
        self.conn.execute(
            """
            INSERT INTO discovery_questions(
                question_id, project_id, conjecture_id, category, question, rationale, priority, status, node_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_id) DO UPDATE SET
                category = excluded.category,
                question = excluded.question,
                rationale = excluded.rationale,
                priority = excluded.priority,
                status = excluded.status,
                node_id = excluded.node_id,
                updated_at = excluded.updated_at
            """,
            (
                question.question_id,
                question.project_id,
                question.conjecture_id,
                question.category,
                question.question,
                question.rationale,
                question.priority,
                question.status,
                question.node_id,
                now,
                now,
            ),
        )
        self.conn.commit()

    def list_discovery_questions(self, project_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List discovery questions for a project."""
        params: List[Any] = [project_id]
        query = "SELECT * FROM discovery_questions WHERE project_id = ?"
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY priority DESC, created_at ASC"
        return [dict(row) for row in self.conn.execute(query, params).fetchall()]

    def mark_discovery_question_status(self, question_id: str, status: str, node_id: str = "") -> None:
        """Update the status of a discovery question."""
        self.conn.execute(
            """
            UPDATE discovery_questions
            SET status = ?, node_id = COALESCE(NULLIF(?, ''), node_id), updated_at = ?
            WHERE question_id = ?
            """,
            (status, node_id, utcnow(), question_id),
        )
        self.conn.commit()
