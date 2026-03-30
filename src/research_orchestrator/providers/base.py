from __future__ import annotations

from abc import ABC, abstractmethod

from research_orchestrator.types import Conjecture, ExperimentBrief, ProjectCharter, ProviderResult


class Provider(ABC):
    name = "base"
    supports_async = False

    @abstractmethod
    def run(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        raise NotImplementedError

    def submit(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
    ) -> ProviderResult:
        return self.run(charter, conjecture, brief, worker_prompt)

    def poll(
        self,
        charter: ProjectCharter,
        conjecture: Conjecture,
        brief: ExperimentBrief,
        worker_prompt: str,
        external_id: str,
        submitted_at: str = "",
    ) -> ProviderResult:
        raise NotImplementedError(f"{self.name} does not support polling.")
