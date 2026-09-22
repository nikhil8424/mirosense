"""Conflict & Disagreement Analytics.

Quantifies contestation, dispute frequency, and cross-community ideological friction
from canonical simulation events.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional

from ..schemas.events import SimulationEvent, ActionType
from .community_detection import CommunityPartition


@dataclass
class ConflictMetrics:
    """Quantitative conflict, contestation, and disagreement summary."""
    total_conflicts: int = 0
    total_actions: int = 0
    conflict_rate: float = 0.0
    cross_community_conflicts: int = 0
    internal_community_conflicts: int = 0
    cross_community_conflict_ratio: float = 0.0
    conflict_by_round: Dict[int, int] = field(default_factory=dict)
    conflict_by_agent: Dict[str, int] = field(default_factory=dict)
    conflict_by_topic: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_conflicts": self.total_conflicts,
            "total_actions": self.total_actions,
            "conflict_rate": round(float(self.conflict_rate), 4),
            "cross_community_conflicts": self.cross_community_conflicts,
            "internal_community_conflicts": self.internal_community_conflicts,
            "cross_community_conflict_ratio": round(float(self.cross_community_conflict_ratio), 4),
            "conflict_by_round": {str(k): v for k, v in self.conflict_by_round.items()},
            "conflict_by_agent": self.conflict_by_agent,
            "conflict_by_topic": self.conflict_by_topic,
        }


class ConflictAnalyzer:
    """Analyzes disagreement actions, dispute intensity, and inter-group friction."""

    def analyze(
        self,
        events: List[SimulationEvent],
        partition: Optional[CommunityPartition] = None,
    ) -> ConflictMetrics:
        """Compute conflict metrics from simulation events and community partition."""
        # Build agent to community map if partition available
        agent_to_comm: Dict[str, str] = {}
        if partition:
            for comm in partition.communities:
                for agent_id in comm.member_agent_ids:
                    agent_to_comm[str(agent_id)] = comm.community_id

        total_actions = len(events)
        if total_actions == 0:
            return ConflictMetrics()

        conflict_events: List[SimulationEvent] = []
        by_round: Dict[int, int] = defaultdict(int)
        by_agent: Dict[str, int] = defaultdict(int)
        by_topic: Dict[str, int] = defaultdict(int)

        cross_conflicts = 0
        internal_conflicts = 0

        for evt in events:
            # Check for conflict action types or strongly oppositional stance / negative interaction
            is_conflict = (
                evt.action_type == ActionType.DISAGREE.value
                or (evt.stance is not None and evt.stance < -0.3)
                or (evt.action_type == ActionType.REPLY.value and evt.stance is not None and evt.stance < -0.1)
            )

            if is_conflict:
                conflict_events.append(evt)
                r = evt.round_id if evt.round_id is not None else 0
                by_round[r] += 1
                if evt.agent_id:
                    by_agent[str(evt.agent_id)] += 1
                if evt.topic:
                    by_topic[evt.topic] += 1

                # Check cross-community vs internal conflict
                if evt.target_agent_id and evt.agent_id:
                    src_comm = agent_to_comm.get(str(evt.agent_id))
                    tgt_comm = agent_to_comm.get(str(evt.target_agent_id))
                    if src_comm and tgt_comm:
                        if src_comm != tgt_comm:
                            cross_conflicts += 1
                        else:
                            internal_conflicts += 1

        n_conflicts = len(conflict_events)
        conflict_rate = n_conflicts / total_actions if total_actions > 0 else 0.0
        total_attributed = cross_conflicts + internal_conflicts
        cross_ratio = (cross_conflicts / total_attributed) if total_attributed > 0 else 0.0

        return ConflictMetrics(
            total_conflicts=n_conflicts,
            total_actions=total_actions,
            conflict_rate=conflict_rate,
            cross_community_conflicts=cross_conflicts,
            internal_community_conflicts=internal_conflicts,
            cross_community_conflict_ratio=cross_ratio,
            conflict_by_round=dict(by_round),
            conflict_by_agent=dict(sorted(by_agent.items(), key=lambda x: x[1], reverse=True)[:10]),
            conflict_by_topic=dict(sorted(by_topic.items(), key=lambda x: x[1], reverse=True)[:5]),
        )

    def export_conflict_json(self, metrics: ConflictMetrics, output_path: str) -> str:
        """Export conflict metrics to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
