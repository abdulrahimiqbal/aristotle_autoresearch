"""Utility functions for database operations."""

from datetime import datetime, timezone
import subprocess
from typing import Dict

from research_orchestrator.schema_versions import (
    EVALUATOR_VERSION,
    MANAGER_POLICY_VERSION,
    MOVE_REGISTRY_VERSION,
    PROMPT_TEMPLATE_VERSION,
    REPLAY_MANIFEST_VERSION,
    RUNTIME_POLICY_VERSION,
    SEMANTIC_MEMORY_VERSION,
    THEOREM_FAMILY_VERSION,
    VERIFICATION_PARSER_VERSION,
    VERIFICATION_SCHEMA_VERSION,
)


def utcnow() -> str:
    """Return current UTC time as ISO format string."""
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(value: str | None) -> datetime | None:
    """Parse an ISO timestamp string to datetime (UTC)."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def current_version_bundle() -> Dict[str, str]:
    """Return a dictionary of all current schema/component versions."""
    return {
        "manifest_version": REPLAY_MANIFEST_VERSION,
        "prompt_version": PROMPT_TEMPLATE_VERSION,
        "parser_version": VERIFICATION_PARSER_VERSION,
        "evaluator_version": EVALUATOR_VERSION,
        "semantic_memory_version": SEMANTIC_MEMORY_VERSION,
        "verification_schema_version": VERIFICATION_SCHEMA_VERSION,
        "policy_version": MANAGER_POLICY_VERSION,
        "move_registry_version": MOVE_REGISTRY_VERSION,
        "theorem_family_version": THEOREM_FAMILY_VERSION,
        "runtime_policy_version": RUNTIME_POLICY_VERSION,
    }


def best_effort_git_branch(cwd: str) -> str:
    """Attempt to get current git branch name. Returns empty string on failure."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()
