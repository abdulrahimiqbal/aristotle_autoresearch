from __future__ import annotations

from dataclasses import dataclass
from typing import List


REQUIRED_MANAGER_SNIPPETS = [
    "Do not treat one failed proof attempt as evidence of falsity",
    "Choose exactly one next experiment",
    "information gain",
    "recurring lemma discovery",
]

REQUIRED_WORKER_SNIPPETS = [
    "Do not conclude falsity from failure",
    "Distinguish structural blockers from search blockers and formalization blockers",
    "Return structured outputs",
    "blocker classification",
]


@dataclass
class PromptLintResult:
    ok: bool
    missing: List[str]


def lint_manager_prompt(text: str) -> PromptLintResult:
    missing = [snippet for snippet in REQUIRED_MANAGER_SNIPPETS if snippet not in text]
    return PromptLintResult(ok=not missing, missing=missing)


def lint_worker_prompt(text: str) -> PromptLintResult:
    missing = [snippet for snippet in REQUIRED_WORKER_SNIPPETS if snippet not in text]
    return PromptLintResult(ok=not missing, missing=missing)
