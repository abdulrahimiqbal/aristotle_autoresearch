"""Manager configuration from environment variables for Railway deployment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ManagerConfig:
    """Configuration for a research manager instance.

    Loaded from environment variables for Railway deployment.
    Each problem runs in isolation with its own config.
    """

    # Required identity
    problem_number: str  # e.g., "273"
    project_id: str  # e.g., "campaign-erdos-problem-273-d686516d"

    # Paths (can be overridden)
    database_path: str = "/data/erdos.sqlite"
    workspace_path: str = "/data/workspace"

    # Operational parameters
    max_active: int = 3
    max_submit_per_tick: int = 2
    tick_interval_seconds: int = 60
    convergence_threshold: float = 0.95
    max_experiments: int = 10000

    # Provider settings
    provider_name: str = "aristotle-cli"

    # LLM settings
    llm_manager_mode: str = "gatekeeper"  # or "synthesis", "none"
    moonshot_api_key: Optional[str] = None
    moonshot_base_url: str = "https://api.moonshot.cn/v1"
    moonshot_model: str = "kimi-k2-5"

    # Aristotle provider settings
    aristotle_api_key: Optional[str] = None
    aristotle_base_url: str = "https://api.aristotle.io"

    # Feature flags
    enable_cross_pollination: bool = False
    enable_auto_retry: bool = True
    stop_on_error: bool = False

    # Health server
    health_port: int = 8080
    enable_health_server: bool = True

    # Reporting
    report_output_path: Optional[str] = None
    snapshot_output_path: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ManagerConfig":
        """Load configuration from environment variables.

        Required env vars:
            PROBLEM_NUMBER - Problem identifier (e.g., "273")
            PROJECT_ID - Full project ID

        Optional env vars:
            DATABASE_PATH - SQLite database path (default: /data/erdos.sqlite)
            WORKSPACE_PATH - Workspace directory (default: /data/workspace)
            MAX_ACTIVE - Max concurrent experiments (default: 3)
            TICK_INTERVAL - Seconds between ticks (default: 60)
            CONVERGENCE_THRESHOLD - Target convergence (default: 0.95)
            PROVIDER_NAME - Provider to use (default: aristotle-cli)
            LLM_MANAGER_MODE - LLM mode (default: gatekeeper)
            MOONSHOT_API_KEY - API key for Moonshot AI
            ARISTOTLE_API_KEY - API key for Aristotle
            HEALTH_PORT - Port for health checks (default: 8080)
            ENABLE_HEALTH_SERVER - Run health server (default: true)
        """
        problem_number = os.getenv("PROBLEM_NUMBER")
        project_id = os.getenv("PROJECT_ID")

        if not problem_number:
            raise ValueError("PROBLEM_NUMBER environment variable is required")
        if not project_id:
            raise ValueError("PROJECT_ID environment variable is required")

        # Derive default paths from problem number if not set
        default_db = f"/data/erdos{problem_number}.sqlite"
        default_workspace = f"/data/workspace{problem_number}"

        def _bool(val: Optional[str]) -> bool:
            if val is None:
                return False
            return val.lower() in ("1", "true", "yes", "on")

        return cls(
            problem_number=problem_number,
            project_id=project_id,
            database_path=os.getenv("DATABASE_PATH", default_db),
            workspace_path=os.getenv("WORKSPACE_PATH", default_workspace),
            max_active=int(os.getenv("MAX_ACTIVE", "3")),
            max_submit_per_tick=int(os.getenv("MAX_SUBMIT_PER_TICK", "2")),
            tick_interval_seconds=int(os.getenv("TICK_INTERVAL", "60")),
            convergence_threshold=float(os.getenv("CONVERGENCE_THRESHOLD", "0.95")),
            max_experiments=int(os.getenv("MAX_EXPERIMENTS", "10000")),
            provider_name=os.getenv("PROVIDER_NAME", "aristotle-cli"),
            llm_manager_mode=os.getenv("LLM_MANAGER_MODE", "gatekeeper"),
            moonshot_api_key=os.getenv("MOONSHOT_API_KEY"),
            moonshot_base_url=os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
            moonshot_model=os.getenv("MOONSHOT_MODEL", "kimi-k2-5"),
            aristotle_api_key=os.getenv("ARISTOTLE_API_KEY"),
            aristotle_base_url=os.getenv("ARISTOTLE_BASE_URL", "https://api.aristotle.io"),
            enable_cross_pollination=_bool(os.getenv("ENABLE_CROSS_POLLINATION")),
            enable_auto_retry=_bool(os.getenv("ENABLE_AUTO_RETRY", "true")),
            stop_on_error=_bool(os.getenv("STOP_ON_ERROR")),
            health_port=int(os.getenv("HEALTH_PORT", "8080")),
            enable_health_server=_bool(os.getenv("ENABLE_HEALTH_SERVER", "true")),
            report_output_path=os.getenv("REPORT_OUTPUT_PATH"),
            snapshot_output_path=os.getenv("SNAPSHOT_OUTPUT_PATH"),
        )

    def to_report_paths(self) -> tuple[Optional[str], Optional[str]]:
        """Return report and snapshot output paths.

        If not explicitly set, derives them from workspace path.
        """
        if self.report_output_path:
            report = self.report_output_path
        else:
            report = f"{self.workspace_path}/report.md"

        if self.snapshot_output_path:
            snapshot = self.snapshot_output_path
        else:
            snapshot = f"{self.workspace_path}/manager_snapshot.json"

        return report, snapshot

    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues: List[str] = []

        # Check API keys are present if needed
        if self.llm_manager_mode != "none" and not self.moonshot_api_key:
            issues.append("MOONSHOT_API_KEY required when LLM_MANAGER_MODE is not 'none'")

        if self.provider_name == "aristotle-cli" and not self.aristotle_api_key:
            issues.append("ARISTOTLE_API_KEY required for aristotle-cli provider")

        # Check paths are absolute (required for Docker)
        if not self.database_path.startswith("/"):
            issues.append(f"DATABASE_PATH must be absolute: {self.database_path}")
        if not self.workspace_path.startswith("/"):
            issues.append(f"WORKSPACE_PATH must be absolute: {self.workspace_path}")

        return issues


def load_config() -> ManagerConfig:
    """Load and validate configuration from environment.

    Raises:
        ValueError: If required env vars missing or validation fails.
    """
    config = ManagerConfig.from_env()
    issues = config.validate()
    if issues:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {i}" for i in issues))
    return config
