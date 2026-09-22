"""Experiment Manifest Schema.

Defines the metadata record ensuring full reproducibility across code version,
random seeds, LLM provider, scenario configurations, and generated artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib
import json
from typing import Any, Dict, List, Optional


@dataclass
class ExperimentManifest:
    """Immutable manifest for an entire experimental execution."""
    experiment_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    scenario_id: str = "baseline"
    random_seed: int = 42
    agent_count: int = 20
    rounds: int = 5
    platform: str = "parallel"
    llm_provider: str = "ollama"
    llm_model: str = "qwen3:8b"
    code_version: str = "1.0.0"
    config_hash: str = ""
    metrics_version: str = "1.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)

    def compute_config_hash(self) -> str:
        """Compute SHA256 hash of experimental parameters and seeds."""
        payload = {
            "scenario_id": self.scenario_id,
            "random_seed": self.random_seed,
            "agent_count": self.agent_count,
            "rounds": self.rounds,
            "platform": self.platform,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "parameters": self.parameters,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not data["config_hash"]:
            data["config_hash"] = self.compute_config_hash()
        return data
