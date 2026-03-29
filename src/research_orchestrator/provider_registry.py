from __future__ import annotations

from research_orchestrator.providers.aristotle_cli import AristotleCLIProvider
from research_orchestrator.providers.base import Provider
from research_orchestrator.providers.mock import MockProvider


def get_provider(name: str) -> Provider:
    if name == "mock":
        return MockProvider()
    if name == "aristotle-cli":
        return AristotleCLIProvider()
    raise KeyError(f"Unknown provider: {name}")
