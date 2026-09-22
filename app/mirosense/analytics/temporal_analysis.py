"""Temporal Dynamics & Round Trajectory Analytics.

Calculates round-by-round time-series trajectories of stance, consensus,
conflict, modularity, and diffusion.
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
from .community_detection import CommunityPartition


@dataclass
class TemporalSnapshot:
    """Metrics captured at a single simulation round."""
    round_id: int
    action_count: int = 0
    cumulative_actions: int = 0
    active_agents: int = 0
    mean_stance: float = 0.0
    stance_variance: float = 0.0
    acceptance: float = 0.0
    agreement: float = 0.0
    conflict_count: int = 0
    conflict_rate: float = 0.0
    share_count: int = 0
    diffusion_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_id": self.round_id,
            "action_count": self.action_count,
            "cumulative_actions": self.cumulative_actions,
            "active_agents": self.active_agents,
            "mean_stance": round(float(self.mean_stance), 4),
            "stance_variance": round(float(self.stance_variance), 4),
            "acceptance": round(float(self.acceptance), 4),
            "agreement": round(float(self.agreement), 4),
            "conflict_count": self.conflict_count,
            "conflict_rate": round(float(self.conflict_rate), 4),
            "share_count": self.share_count,
            "diffusion_rate": round(float(self.diffusion_rate), 4),
        }


@dataclass
class TemporalMetricsSeries:
    """Multi-round time-series metrics over the entire simulation horizon."""
    total_rounds: int = 0
    total_actions: int = 0
    snapshots: List[TemporalSnapshot] = field(default_factory=list)
    stance_trajectory: List[float] = field(default_factory=list)
    acceptance_trajectory: List[float] = field(default_factory=list)
    conflict_trajectory: List[float] = field(default_factory=list)
    diffusion_trajectory: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_rounds": self.total_rounds,
            "total_actions": self.total_actions,
            "snapshots": [s.to_dict() for s in self.snapshots],
            "stance_trajectory": [round(s, 4) for s in self.stance_trajectory],
            "acceptance_trajectory": [round(a, 4) for a in self.acceptance_trajectory],
            "conflict_trajectory": [round(c, 4) for c in self.conflict_trajectory],
            "diffusion_trajectory": [round(d, 4) for d in self.diffusion_trajectory],
        }


class TemporalAnalyzer:
    """Computes round-by-round time-series trajectories from canonical simulation events."""

    def analyze(self, events: List[SimulationEvent]) -> TemporalMetricsSeries:
        """Group events by round and compute temporal metrics."""
        events_by_round: Dict[int, List[SimulationEvent]] = defaultdict(list)
        for evt in events:
            r = evt.round_id if evt.round_id is not None else 0
            events_by_round[r].append(evt)

        if not events_by_round:
            return TemporalMetricsSeries()

        sorted_rounds = sorted(events_by_round.keys())
        snapshots: List[TemporalSnapshot] = []
        cumulative = 0

        for r in sorted_rounds:
            round_events = events_by_round[r]
            act_count = len(round_events)
            cumulative += act_count

            active_agents = len({evt.agent_id for evt in round_events if evt.agent_id})

            # Stance metrics for this round
            stances = [evt.stance for evt in round_events if evt.stance is not None]
            if stances:
                m_stance = statistics.mean(stances)
                v_stance = statistics.pvariance(stances) if len(stances) > 1 else 0.0
                pos = sum(1 for s in stances if s > 0.1)
                supp_ratio = pos / len(stances)
                norm_m = (m_stance + 1.0) / 2.0
                acc = 0.6 * norm_m + 0.4 * supp_ratio
                agr = max(0.0, 1.0 - math.sqrt(v_stance))
            else:
                m_stance = 0.0
                v_stance = 0.0
                acc = 0.5
                agr = 1.0

            # Conflict & Diffusion
            conflict_actions = sum(1 for evt in round_events if evt.action_type == ActionType.DISAGREE.value or (evt.stance is not None and evt.stance < -0.3))
            share_actions = sum(1 for evt in round_events if evt.action_type in (ActionType.REPOST.value, ActionType.SHARE.value))

            conf_rate = (conflict_actions / act_count) if act_count > 0 else 0.0
            diff_rate = (share_actions / act_count) if act_count > 0 else 0.0

            snapshots.append(TemporalSnapshot(
                round_id=r,
                action_count=act_count,
                cumulative_actions=cumulative,
                active_agents=active_agents,
                mean_stance=m_stance,
                stance_variance=v_stance,
                acceptance=acc,
                agreement=agr,
                conflict_count=conflict_actions,
                conflict_rate=conf_rate,
                share_count=share_actions,
                diffusion_rate=diff_rate,
            ))

        return TemporalMetricsSeries(
            total_rounds=len(snapshots),
            total_actions=cumulative,
            snapshots=snapshots,
            stance_trajectory=[s.mean_stance for s in snapshots],
            acceptance_trajectory=[s.acceptance for s in snapshots],
            conflict_trajectory=[s.conflict_rate for s in snapshots],
            diffusion_trajectory=[s.diffusion_rate for s in snapshots],
        )

    def export_temporal_json(self, series: TemporalMetricsSeries, output_path: str) -> str:
        """Export temporal dynamics metrics to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(series.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
