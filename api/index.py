import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from research_orchestrator.dashboard_app import create_dashboard_app  # noqa: E402


def _first_existing(paths: list[str]) -> str:
    for item in paths:
        if item and Path(item).exists():
            return item
    return ""


state_dir = os.getenv("STATE_DIR", "")
db_path = os.getenv("DB_PATH", "")
project_id = os.getenv("PROJECT_ID", "")

if not db_path:
    db_path = _first_existing(
        [
            "live_state.sqlite",
            "live_state_final.sqlite",
            "live_state_after_fix3.sqlite",
        ]
    )

if not state_dir:
    state_dir = _first_existing(
        [
            "outputs/dashboard_bundle_live",
            "outputs/dashboard_bundle_test2",
            "outputs/erdos_live_async",
        ]
    )

app = create_dashboard_app(
    state_dir=state_dir or None,
    db=db_path or None,
    project_id=project_id or None,
)
