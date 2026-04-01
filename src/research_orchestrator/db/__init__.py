"""Database module for the research orchestrator.

This module provides a unified Database class that combines functionality
from multiple mixins for clean separation of concerns.

Usage:
    from research_orchestrator.db import Database
    
    db = Database("./state.sqlite")
    db.initialize()
    
    # Use any method from any mixin:
    db.save_project(charter)
    db.save_experiment_plan(plan)
    db.list_active_experiments(project_id)
    db.campaign_health(project_id)
"""

from research_orchestrator.db.core import DatabaseCoreMixin
from research_orchestrator.db.projects import DatabaseProjectsMixin
from research_orchestrator.db.experiments import DatabaseExperimentsMixin
from research_orchestrator.db.discovery import DatabaseDiscoveryMixin
from research_orchestrator.db.manager_state import DatabaseManagerStateMixin
from research_orchestrator.db.routes import DatabaseRoutesMixin
from research_orchestrator.db.incidents import DatabaseIncidentsMixin
from research_orchestrator.db.health import DatabaseHealthMixin
from research_orchestrator.db.export import DatabaseExportMixin
from research_orchestrator.db.utils import utcnow, parse_timestamp, current_version_bundle


class Database(
    DatabaseCoreMixin,
    DatabaseProjectsMixin,
    DatabaseExperimentsMixin,
    DatabaseDiscoveryMixin,
    DatabaseManagerStateMixin,
    DatabaseRoutesMixin,
    DatabaseIncidentsMixin,
    DatabaseHealthMixin,
    DatabaseExportMixin,
):
    """Unified database interface combining all database functionality.
    
    This class inherits from multiple mixins to provide a clean, organized
    interface to all database operations. The mixins are organized by domain:
    
    - Core: Connection, transactions, initialization, row decoders
    - Projects: Project, charter, campaign, conjecture operations
    - Experiments: Experiment lifecycle, plans, results, manifests
    - Discovery: Discovery graph, result ingestion, semantic memory
    - ManagerState: Manager runs, audits, interpretations, bridge hypotheses
    - Routes: Theorem routes, evidence, operator commands
    - Incidents: Incident creation, detection, escalation
    - Health: Campaign health, summaries, recurring structure queries
    - Export: Readable state bundle exports
    """
    pass


__all__ = [
    "Database",
    "utcnow",
    "parse_timestamp",
    "current_version_bundle",
]
