"""Sensitivity Analysis Engine.

Performs controlled one-at-a-time (OAT) parameter sweeps to quantify how simulated
outcomes (acceptance, polarization, conflict) vary with agent population, rounds,
or environmental parameters.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional

from ..evaluation.scenario_comparison import ScenarioProfile


@dataclass
class SensitivityDataPoint:
    """A single evaluation point in a parameter sweep."""
    parameter_name: str
    parameter_value: Any
    acceptance: float
    polarization: float
    conflict_rate: float
    modularity: float
    stability: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "parameter_value": self.parameter_value,
            "acceptance": round(float(self.acceptance), 4),
            "polarization": round(float(self.polarization), 4),
            "conflict_rate": round(float(self.conflict_rate), 4),
            "modularity": round(float(self.modularity), 4),
            "stability": round(float(self.stability), 4),
        }


@dataclass
class SensitivityExperimentResult:
    """Complete sensitivity experiment results for a parameter sweep."""
    parameter_name: str
    parameter_values: List[Any]
    points: List[SensitivityDataPoint] = field(default_factory=list)
    sensitivity_indices: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "parameter_values": self.parameter_values,
            "points": [p.to_dict() for p in self.points],
            "sensitivity_indices": {k: round(v, 4) for k, v in self.sensitivity_indices.items()},
        }


class SensitivityEngine:
    """Orchestrates parameter sweep experiments and sensitivity evaluations."""

    def analyze_sweep(
        self,
        parameter_name: str,
        value_to_profile: Dict[Any, ScenarioProfile],
    ) -> SensitivityExperimentResult:
        """Compute sensitivity response across evaluated parameter values."""
        points: List[SensitivityDataPoint] = []
        param_values = list(value_to_profile.keys())

        for val, p in value_to_profile.items():
            points.append(SensitivityDataPoint(
                parameter_name=parameter_name,
                parameter_value=val,
                acceptance=p.acceptance,
                polarization=p.polarization,
                conflict_rate=p.conflict_rate,
                modularity=p.modularity,
                stability=p.stability,
            ))

        # Calculate sensitivity index as normalized max delta
        sens_indices: Dict[str, float] = {}
        if len(points) >= 2:
            accs = [p.acceptance for p in points]
            pols = [p.polarization for p in points]
            confs = [p.conflict_rate for p in points]

            sens_indices["acceptance_range"] = max(accs) - min(accs)
            sens_indices["polarization_range"] = max(pols) - min(pols)
            sens_indices["conflict_range"] = max(confs) - min(confs)

        return SensitivityExperimentResult(
            parameter_name=parameter_name,
            parameter_values=param_values,
            points=points,
            sensitivity_indices=sens_indices,
        )

    def export_sensitivity_json(self, result: SensitivityExperimentResult, output_path: str) -> str:
        """Export sensitivity results to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
