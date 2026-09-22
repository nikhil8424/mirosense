"""Scenario Specifications Schema.

Defines formal candidate policy / decision scenarios for controlled in-silico simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
from typing import Any, Dict, List, Optional


@dataclass
class Scenario:
    """A parameterized candidate policy or decision scenario."""
    scenario_id: str
    name: str
    description: str
    intervention_text: str

    policy_parameters: Dict[str, Any] = field(default_factory=dict)
    agent_parameters: Dict[str, Any] = field(default_factory=dict)
    simulation_parameters: Dict[str, Any] = field(default_factory=lambda: {
        "platform": "parallel",
        "max_rounds": 5,
        "agent_count": 20,
    })
    random_seed: int = 42
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Scenario:
        return cls(
            scenario_id=str(data.get("scenario_id", "")),
            name=str(data.get("name", "")),
            description=str(data.get("description", "")),
            intervention_text=str(data.get("intervention_text", "")),
            policy_parameters=dict(data.get("policy_parameters", {})),
            agent_parameters=dict(data.get("agent_parameters", {})),
            simulation_parameters=dict(data.get("simulation_parameters", {})),
            random_seed=int(data.get("random_seed", 42)),
            metadata=dict(data.get("metadata", {})),
        )
