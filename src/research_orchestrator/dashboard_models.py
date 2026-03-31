from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DataProvenance:
    source: str
    last_updated: str = ""
    integrity_status: str = "unknown"


@dataclass
class HealthStatus:
    source_mode: str
    db_path: str = ""
    state_dir: str = ""
    db_readable: bool = False
    db_corrupt: bool = False
    db_integrity: str = "unknown"
    last_bundle_export: str = ""
    last_db_update: str = ""
    missing_files: list[str] = field(default_factory=list)
    stale_bundle_warning: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class DashboardState:
    project_id: str
    campaign_name: str
    source_mode: str
    campaign_snapshot: dict[str, Any]
    knowledge_structures: list[dict[str, Any]]
    problem_progress: list[dict[str, Any]]
    falsehood_boundaries: list[dict[str, Any]]
    knowledge_pipeline: list[dict[str, Any]]
    recent_results: list[dict[str, Any]]
    manager_actions: list[dict[str, Any]]
    manager_reasoning: list[dict[str, Any]]
    problems: dict[str, dict[str, Any]]
    experiments: dict[str, dict[str, Any]]
    provenance: dict[str, DataProvenance]
    health: HealthStatus
