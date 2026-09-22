"""Ablation Study Framework.

Evaluates the contribution of individual architectural components (Knowledge Graph,
Memory, Community Analytics, Temporal Modeling) by running controlled ablated variants.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional

from ..evaluation.scenario_comparison import ScenarioProfile


@dataclass
class AblationConfig:
    """Feature flags defining which components are enabled in an experimental run."""
    name: str = "FULL"
    graph_grounding: bool = True
    memory: bool = True
    community_analytics: bool = True
    temporal_analysis: bool = True
    scenario_conditioning: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AblationExperimentResult:
    """Comparison results across full and ablated configurations."""
    baseline_config: str = "FULL"
    configurations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metric_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    component_impacts: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_config": self.baseline_config,
            "configurations": self.configurations,
            "metric_comparison": self.metric_comparison,
            "component_impacts": self.component_impacts,
        }


class AblationEngine:
    """Manages ablation studies across architectural configurations."""

    @staticmethod
    def get_standard_ablation_configs() -> Dict[str, AblationConfig]:
        """Return the standard set of ablation configurations."""
        return {
            "FULL": AblationConfig(name="FULL"),
            "NO_GRAPH": AblationConfig(name="NO_GRAPH", graph_grounding=False),
            "NO_COMMUNITY": AblationConfig(name="NO_COMMUNITY", community_analytics=False),
            "NO_MEMORY": AblationConfig(name="NO_MEMORY", memory=False),
            "NO_TEMPORAL": AblationConfig(name="NO_TEMPORAL", temporal_analysis=False),
        }

    def evaluate_ablations(
        self,
        config_to_profile: Dict[str, ScenarioProfile],
        baseline_name: str = "FULL",
    ) -> AblationExperimentResult:
        """Evaluate the effect of each ablated subsystem relative to the full baseline."""
        full_p = config_to_profile.get(baseline_name)
        if not full_p:
            if config_to_profile:
                baseline_name = list(config_to_profile.keys())[0]
                full_p = config_to_profile[baseline_name]
            else:
                return AblationExperimentResult()

        configs_summary: Dict[str, Dict[str, Any]] = {}
        comparison: Dict[str, Dict[str, float]] = {}
        impacts: Dict[str, Dict[str, float]] = {}

        dimensions = ["acceptance", "agreement", "polarization", "conflict_rate", "stability"]

        for name, p in config_to_profile.items():
            configs_summary[name] = {
                "scenario_name": p.scenario_name,
                "acceptance": p.acceptance,
                "polarization": p.polarization,
                "conflict_rate": p.conflict_rate,
                "stability": p.stability,
            }
            comparison[name] = {dim: getattr(p, dim, 0.0) for dim in dimensions}

            if name != baseline_name:
                impacts[name] = {
                    dim: round(getattr(p, dim, 0.0) - getattr(full_p, dim, 0.0), 4)
                    for dim in dimensions
                }

        return AblationExperimentResult(
            baseline_config=baseline_name,
            configurations=configs_summary,
            metric_comparison=comparison,
            component_impacts=impacts,
        )

    def export_ablation_json(self, result: AblationExperimentResult, output_path: str) -> str:
        """Export ablation experiment results to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
