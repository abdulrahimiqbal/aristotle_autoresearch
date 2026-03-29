from __future__ import annotations

import json
from pathlib import Path

from research_orchestrator.types import Conjecture, ProjectCharter


def _read_json(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_charter(path: str | Path) -> ProjectCharter:
    data = _read_json(path)
    return ProjectCharter(**data)


def load_conjecture(path: str | Path) -> Conjecture:
    data = _read_json(path)
    return Conjecture(**data)
