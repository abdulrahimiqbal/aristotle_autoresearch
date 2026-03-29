from __future__ import annotations

from abc import ABC, abstractmethod

from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter, ProviderResult


class Provider(ABC):
    name = "base"

    @abstractmethod
    def run(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        raise NotImplementedError
