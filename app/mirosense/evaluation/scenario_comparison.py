"""Scenario Comparison & Comparative Behavioral Profiling.

Performs quantitative side-by-side comparative benchmarking across multiple candidate
policy / decision scenarios without making uncalibrated normative claims.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional

from .effect_size import compute_cohens_d


@dataclass
class ScenarioProfile:
    """Multi-dimensional simulated behavioral profile of a single scenario."""
    scenario_id: str
    scenario_name: str
    acceptance: float = 0.0
    agreement: float = 0.0
    polarization: float = 0.0
    conflict_rate: float = 0.0
    modularity: float = 0.0
    diffusion_rate: float = 0.0
    stability: float = 0.0
    gini_influence: float = 0.0
    active_communities: int = 0
    total_actions: int = 0
    sample_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "acceptance": round(float(self.acceptance), 4),
            "agreement": round(float(self.agreement), 4),
            "polarization": round(float(self.polarization), 4),
            "conflict_rate": round(float(self.conflict_rate), 4),
            "modularity": round(float(self.modularity), 4),
            "diffusion_rate": round(float(self.diffusion_rate), 4),
            "stability": round(float(self.stability), 4),
            "gini_influence": round(float(self.gini_influence), 4),
            "active_communities": self.active_communities,
            "total_actions": self.total_actions,
            "sample_size": self.sample_size,
        }


@dataclass
class ScenarioComparisonReport:
    """Comprehensive comparative analysis report across scenarios."""
    scenarios: List[ScenarioProfile] = field(default_factory=list)
    baseline_scenario_id: Optional[str] = None
    comparison_table: Dict[str, Dict[str, float]] = field(default_factory=dict)
    pairwise_differences: Dict[str, Dict[str, float]] = field(default_factory=dict)
    effect_sizes: Dict[str, Dict[str, float]] = field(default_factory=dict)
    summary_findings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenarios": [s.to_dict() for s in self.scenarios],
            "baseline_scenario_id": self.baseline_scenario_id,
            "comparison_table": self.comparison_table,
            "pairwise_differences": self.pairwise_differences,
            "effect_sizes": self.effect_sizes,
            "summary_findings": self.summary_findings,
        }


class ScenarioComparator:
    """Compares candidate decision scenarios across multiple behavioral dimensions."""

    def compare(
        self,
        profiles: List[ScenarioProfile],
        baseline_id: Optional[str] = None,
        raw_distributions: Optional[Dict[str, Dict[str, List[float]]]] = None,
    ) -> ScenarioComparisonReport:
        """Generate side-by-side comparison report."""
        if not profiles:
            return ScenarioComparisonReport()

        base_id = baseline_id or profiles[0].scenario_id
        base_profile = next((p for p in profiles if p.scenario_id == base_id), profiles[0])

        dimensions = [
            "acceptance", "agreement", "polarization", "conflict_rate",
            "modularity", "diffusion_rate", "stability", "gini_influence"
        ]

        # 1. Comparison table
        comp_table: Dict[str, Dict[str, float]] = {}
        for p in profiles:
            comp_table[p.scenario_id] = {
                "name": p.scenario_name,
                "acceptance": p.acceptance,
                "agreement": p.agreement,
                "polarization": p.polarization,
                "conflict_rate": p.conflict_rate,
                "modularity": p.modularity,
                "diffusion_rate": p.diffusion_rate,
                "stability": p.stability,
                "gini_influence": p.gini_influence,
            }

        # 2. Pairwise differences relative to baseline
        differences: Dict[str, Dict[str, float]] = {}
        for p in profiles:
            if p.scenario_id != base_id:
                diff_map: Dict[str, float] = {}
                for dim in dimensions:
                    val_p = getattr(p, dim, 0.0)
                    val_b = getattr(base_profile, dim, 0.0)
                    diff_map[dim] = round(val_p - val_b, 4)
                differences[p.scenario_id] = diff_map

        # 3. Effect sizes if raw metric sample distributions are provided
        effect_sizes: Dict[str, Dict[str, float]] = {}
        if raw_distributions:
            base_dists = raw_distributions.get(base_id, {})
            for p in profiles:
                if p.scenario_id != base_id and p.scenario_id in raw_distributions:
                    p_dists = raw_distributions[p.scenario_id]
                    cohen_map: Dict[str, float] = {}
                    for dim in dimensions:
                        if dim in p_dists and dim in base_dists:
                            cd = compute_cohens_d(p_dists[dim], base_dists[dim])
                            if cd is not None:
                                cohen_map[dim] = cd
                    if cohen_map:
                        effect_sizes[p.scenario_id] = cohen_map

        # 4. Objective, evidence-supported summary findings
        findings: List[str] = []
        for p in profiles:
            if p.scenario_id != base_id:
                diff = differences.get(p.scenario_id, {})
                acc_diff = diff.get("acceptance", 0.0)
                pol_diff = diff.get("polarization", 0.0)
                conf_diff = diff.get("conflict_rate", 0.0)

                findings.append(
                    f"Scenario '{p.scenario_name}' shows an acceptance change of {acc_diff:+.2f}, "
                    f"polarization change of {pol_diff:+.2f}, and conflict rate change of {conf_diff:+.2f} "
                    f"relative to baseline '{base_profile.scenario_name}'."
                )

        return ScenarioComparisonReport(
            scenarios=profiles,
            baseline_scenario_id=base_id,
            comparison_table=comp_table,
            pairwise_differences=differences,
            effect_sizes=effect_sizes,
            summary_findings=findings,
        )

    def export_comparison_json(self, report: ScenarioComparisonReport, output_path: str) -> str:
        """Export scenario comparison report to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
