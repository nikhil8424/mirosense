"""Monte Carlo Simulation Engine & Distribution Aggregation.

Executes repeated stochastic simulation runs across multiple random seeds and builds
statistical aggregation matrices with empirical confidence intervals.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Callable, Dict, List, Optional

from ..schemas.scenarios import Scenario
from ..evaluation.scenario_comparison import ScenarioProfile
from .uncertainty import compute_confidence_interval, ConfidenceInterval


@dataclass
class MonteCarloResult:
    """Aggregated experimental result across multiple seeds."""
    scenario_id: str
    scenario_name: str
    runs_count: int
    base_seed: int
    seeds_evaluated: List[int] = field(default_factory=list)
    metric_matrices: Dict[str, List[float]] = field(default_factory=dict)
    statistical_summary: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    status: str = "COMPLETED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "runs_count": self.runs_count,
            "base_seed": self.base_seed,
            "seeds_evaluated": self.seeds_evaluated,
            "metric_matrices": {k: [round(x, 4) for x in v] for k, v in self.metric_matrices.items()},
            "statistical_summary": self.statistical_summary,
            "status": self.status,
        }


class MonteCarloEngine:
    """Orchestrates multi-seed simulation experiments and statistical synthesis."""

    def aggregate_profiles(
        self,
        scenario_id: str,
        scenario_name: str,
        profiles: List[ScenarioProfile],
        base_seed: int = 42,
        seeds: Optional[List[int]] = None,
    ) -> MonteCarloResult:
        """Aggregate a collection of ScenarioProfiles from repeated runs into a MonteCarloResult."""
        n_runs = len(profiles)
        if n_runs == 0:
            return MonteCarloResult(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                runs_count=0,
                base_seed=base_seed,
                status="NO_RUNS",
            )

        evaluated_seeds = seeds or [base_seed + i for i in range(n_runs)]

        dimensions = [
            "acceptance", "agreement", "polarization", "conflict_rate",
            "modularity", "diffusion_rate", "stability", "gini_influence"
        ]

        matrices: Dict[str, List[float]] = {dim: [] for dim in dimensions}
        for p in profiles:
            for dim in dimensions:
                matrices[dim].append(getattr(p, dim, 0.0))

        summary: Dict[str, Dict[str, Any]] = {}
        for dim, samples in matrices.items():
            ci = compute_confidence_interval(samples, metric_name=dim, confidence_level=0.95)
            summary[dim] = ci.to_dict()

        return MonteCarloResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            runs_count=n_runs,
            base_seed=base_seed,
            seeds_evaluated=evaluated_seeds,
            metric_matrices=matrices,
            statistical_summary=summary,
            status="COMPLETED",
        )

    def export_monte_carlo_json(self, result: MonteCarloResult, output_path: str) -> str:
        """Export Monte Carlo experiment results to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
