"""Opinion Dynamics Analytics.

Computes population-level stance, dispersion, acceptance, and agreement metrics
from canonical simulation events.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, asdict
import json
import math
import os
import statistics
from typing import Any, Dict, List, Optional

from ..schemas.events import SimulationEvent, ActionType


@dataclass
class OpinionMetrics:
    """Quantitative stance and agreement metrics across the agent population."""
    sample_size: int = 0
    unique_agents: int = 0
    mean_stance: float = 0.0
    stance_variance: float = 0.0
    stance_std: float = 0.0
    acceptance: float = 0.0       # Proportion of positive stance actions in [0, 1]
    agreement: float = 0.0        # Inverse of stance dispersion (cohesion) in [0, 1]
    support_ratio: float = 0.0    # Proportion with stance > 0.1
    opposition_ratio: float = 0.0 # Proportion with stance < -0.1
    neutral_ratio: float = 0.0    # Proportion with |stance| <= 0.1
    stance_histogram: Dict[str, int] = field(default_factory=dict)
    agent_stance_map: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_size": self.sample_size,
            "unique_agents": self.unique_agents,
            "mean_stance": round(float(self.mean_stance), 4),
            "stance_variance": round(float(self.stance_variance), 4),
            "stance_std": round(float(self.stance_std), 4),
            "acceptance": round(float(self.acceptance), 4),
            "agreement": round(float(self.agreement), 4),
            "support_ratio": round(float(self.support_ratio), 4),
            "opposition_ratio": round(float(self.opposition_ratio), 4),
            "neutral_ratio": round(float(self.neutral_ratio), 4),
            "stance_histogram": self.stance_histogram,
            "agent_stance_map": {k: round(v, 4) for k, v in self.agent_stance_map.items()},
        }


class OpinionDynamicsAnalyzer:
    """Analyzes stance distributions, acceptance, and opinion consensus."""

    def analyze(self, events: List[SimulationEvent]) -> OpinionMetrics:
        """Analyze opinion dynamics across all events."""
        agent_stances: Dict[str, List[float]] = defaultdict(list)
        all_stances: List[float] = []

        for evt in events:
            if evt.stance is not None:
                all_stances.append(evt.stance)
                if evt.agent_id:
                    agent_stances[str(evt.agent_id)].append(evt.stance)

        n = len(all_stances)
        if n == 0:
            return OpinionMetrics()

        mean_s = statistics.mean(all_stances)
        variance_s = statistics.pvariance(all_stances) if n > 1 else 0.0
        std_s = math.sqrt(variance_s)

        # Acceptance: normalized scale where -1 -> 0, +1 -> 1
        pos_count = sum(1 for s in all_stances if s > 0.1)
        neg_count = sum(1 for s in all_stances if s < -0.1)
        neu_count = n - pos_count - neg_count

        support_ratio = pos_count / n
        opposition_ratio = neg_count / n
        neutral_ratio = neu_count / n

        # Acceptance blends positive support ratio with normalized mean stance
        normalized_mean = (mean_s + 1.0) / 2.0
        acceptance = 0.6 * normalized_mean + 0.4 * support_ratio
        acceptance = min(max(acceptance, 0.0), 1.0)

        # Agreement: maximum when standard deviation is 0; approaches 0 when std approaches 1.0
        agreement = max(0.0, 1.0 - std_s)

        # Histogram bins
        histogram = {
            "strongly_opposed_[-1.0,-0.5)": sum(1 for s in all_stances if s < -0.5),
            "moderately_opposed_[-0.5,-0.1)": sum(1 for s in all_stances if -0.5 <= s < -0.1),
            "neutral_[-0.1,0.1]": sum(1 for s in all_stances if -0.1 <= s <= 0.1),
            "moderately_supportive_(0.1,0.5]": sum(1 for s in all_stances if 0.1 < s <= 0.5),
            "strongly_supportive_(0.5,1.0]": sum(1 for s in all_stances if s > 0.5),
        }

        # Agent average stance map
        agent_map = {aid: float(statistics.mean(stances)) for aid, stances in agent_stances.items()}

        return OpinionMetrics(
            sample_size=n,
            unique_agents=len(agent_map),
            mean_stance=mean_s,
            stance_variance=variance_s,
            stance_std=std_s,
            acceptance=acceptance,
            agreement=agreement,
            support_ratio=support_ratio,
            opposition_ratio=opposition_ratio,
            neutral_ratio=neutral_ratio,
            stance_histogram=histogram,
            agent_stance_map=agent_map,
        )

    def export_opinion_json(self, metrics: OpinionMetrics, output_path: str) -> str:
        """Export opinion dynamics metrics to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
