"""Scenario Engine.

Manages the authoring, parameter isolation, and execution staging of candidate
decision scenarios for controlled in-silico experiments.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional

from ..schemas.scenarios import Scenario


class ScenarioEngine:
    """Manages scenario specifications and validates experimental parameter isolation."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = storage_dir or "uploads/scenarios"
        self._scenarios: Dict[str, Scenario] = {}
        os.makedirs(self.storage_dir, exist_ok=True)

    def create_scenario(
        self,
        name: str,
        description: str,
        intervention_text: str,
        policy_parameters: Optional[Dict[str, Any]] = None,
        agent_parameters: Optional[Dict[str, Any]] = None,
        simulation_parameters: Optional[Dict[str, Any]] = None,
        random_seed: int = 42,
        scenario_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Scenario:
        """Create and store a parameterized decision scenario."""
        sid = scenario_id or f"scen_{uuid.uuid4().hex[:8]}"
        scen = Scenario(
            scenario_id=sid,
            name=name,
            description=description,
            intervention_text=intervention_text,
            policy_parameters=policy_parameters or {},
            agent_parameters=agent_parameters or {},
            simulation_parameters=simulation_parameters or {
                "platform": "parallel",
                "max_rounds": 5,
                "agent_count": 20,
            },
            random_seed=random_seed,
            metadata=metadata or {},
        )
        self._scenarios[sid] = scen
        self.save_scenario(scen)
        return scen

    def save_scenario(self, scenario: Scenario) -> str:
        """Persist scenario JSON to storage directory."""
        path = os.path.join(self.storage_dir, f"{scenario.scenario_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scenario.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    def load_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Load scenario from memory or disk."""
        if scenario_id in self._scenarios:
            return self._scenarios[scenario_id]
        path = os.path.join(self.storage_dir, f"{scenario_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                scen = Scenario.from_dict(json.load(f))
                self._scenarios[scenario_id] = scen
                return scen
        return None

    def list_scenarios(self) -> List[Scenario]:
        """List all persisted scenarios."""
        results: List[Scenario] = list(self._scenarios.values())
        if os.path.exists(self.storage_dir):
            for fname in os.listdir(self.storage_dir):
                if fname.endswith(".json"):
                    sid = fname[:-5]
                    if sid not in self._scenarios:
                        scen = self.load_scenario(sid)
                        if scen:
                            results.append(scen)
        return results

    def validate_controlled_comparison(self, scenarios: List[Scenario]) -> List[str]:
        """Verify that non-intervention parameters (agent_count, platform) remain constant across comparisons."""
        warnings: List[str] = []
        if len(scenarios) < 2:
            return warnings

        base = scenarios[0]
        base_agents = base.simulation_parameters.get("agent_count")
        base_platform = base.simulation_parameters.get("platform")

        for s in scenarios[1:]:
            s_agents = s.simulation_parameters.get("agent_count")
            s_platform = s.simulation_parameters.get("platform")
            if s_agents != base_agents:
                warnings.append(
                    f"Confounding variable: Scenario '{s.name}' agent count ({s_agents}) differs from baseline ({base_agents})."
                )
            if s_platform != base_platform:
                warnings.append(
                    f"Confounding variable: Scenario '{s.name}' platform ({s_platform}) differs from baseline ({base_platform})."
                )
        return warnings
