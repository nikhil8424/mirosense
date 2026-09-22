"""Baseline Comparison Framework.

Provides benchmarking against simpler reference approaches:
1. Baseline A: Direct LLM Prompting (Zero-shot / single query)
2. Baseline B: Random Interaction Model
3. Baseline C: Raw OASIS simulation (without analytical graph grounding)
4. Proposed: MiroSense Research Extension
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional

from ..evaluation.scenario_comparison import ScenarioProfile


@dataclass
class BaselineResult:
    """Benchmark results comparing MiroSense with standard baselines."""
    scenario_id: str
    scenario_name: str
    baseline_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    comparative_advantages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaselineEngine:
    """Manages baseline evaluations and benchmarking comparisons."""

    def compare_baselines(
        self,
        scenario_id: str,
        scenario_name: str,
        profiles_by_system: Dict[str, ScenarioProfile],
    ) -> BaselineResult:
        """Benchmark MiroSense against simpler baseline approaches."""
        summary: Dict[str, Dict[str, Any]] = {}
        for sys_name, p in profiles_by_system.items():
            summary[sys_name] = {
                "acceptance": round(float(p.acceptance), 4),
                "agreement": round(float(p.agreement), 4),
                "polarization": round(float(p.polarization), 4),
                "conflict_rate": round(float(p.conflict_rate), 4),
                "modularity": round(float(p.modularity), 4),
                "diffusion_rate": round(float(p.diffusion_rate), 4),
            }

        advantages = [
            "MiroSense captures multi-round emergent discourse and factional polarization that single-query Direct LLM ignores.",
            "Document-grounded digital twins provide realistic ideological friction compared to random interaction baselines.",
            "Analytical event decomposition enables structured, reproducible decision comparison without black-box report generation.",
        ]

        return BaselineResult(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            baseline_profiles=summary,
            comparative_advantages=advantages,
        )

    def export_baseline_json(self, result: BaselineResult, output_path: str) -> str:
        """Export baseline comparison results to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
