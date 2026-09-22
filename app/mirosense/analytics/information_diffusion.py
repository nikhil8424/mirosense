"""Information Diffusion & Cascade Analytics.

Measures information propagation, cascade sizes, tree depths, and cross-community
reach from canonical simulation events.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional, Set

from ..schemas.events import SimulationEvent, ActionType
from .community_detection import CommunityPartition


@dataclass
class CascadeTree:
    """A single information cascade initiated by an original post."""
    cascade_id: str
    root_event_id: str
    root_agent_id: str
    root_agent_name: Optional[str] = None
    root_content: Optional[str] = None
    root_round: int = 0
    cascade_size: int = 1         # Total participants (root + downstream)
    cascade_depth: int = 0        # Max tree depth
    cascade_duration_rounds: int = 0
    repost_count: int = 0
    reply_count: int = 0
    like_count: int = 0
    participating_agents: List[str] = field(default_factory=list)
    cross_community_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiffusionMetrics:
    """Population-level information diffusion and propagation summary."""
    total_cascades: int = 0
    total_downstream_actions: int = 0
    mean_cascade_size: float = 0.0
    max_cascade_depth: int = 0
    overall_diffusion_rate: float = 0.0
    repost_ratio: float = 0.0
    top_cascades: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_cascades": self.total_cascades,
            "total_downstream_actions": self.total_downstream_actions,
            "mean_cascade_size": round(float(self.mean_cascade_size), 4),
            "max_cascade_depth": self.max_cascade_depth,
            "overall_diffusion_rate": round(float(self.overall_diffusion_rate), 4),
            "repost_ratio": round(float(self.repost_ratio), 4),
            "top_cascades": self.top_cascades,
        }


class DiffusionAnalyzer:
    """Analyzes information cascades, propagation depth, and diffusion velocity."""

    def analyze(
        self,
        events: List[SimulationEvent],
        partition: Optional[CommunityPartition] = None,
    ) -> DiffusionMetrics:
        """Construct cascade trees and compute diffusion metrics."""
        agent_to_comm: Dict[str, str] = {}
        if partition:
            for comm in partition.communities:
                for aid in comm.member_agent_ids:
                    agent_to_comm[str(aid)] = comm.community_id

        # 1. Identify root posts
        event_by_id: Dict[str, SimulationEvent] = {evt.event_id: evt for evt in events if evt.event_id}
        root_posts: List[SimulationEvent] = [
            evt for evt in events if evt.action_type == ActionType.CREATE_POST.value
        ]

        if not root_posts:
            # If no explicit CREATE_POST, treat earliest round actions as origins
            return DiffusionMetrics()

        # 2. Build child map: parent_event_id -> list of downstream child events
        children_map: Dict[str, List[SimulationEvent]] = defaultdict(list)
        for evt in events:
            if evt.parent_event_id and evt.parent_event_id in event_by_id:
                children_map[evt.parent_event_id].append(evt)

        cascades: List[CascadeTree] = []
        total_downstream = 0
        total_shares = 0

        for idx, root in enumerate(root_posts):
            cid = f"cascade_{idx}_{root.event_id}"
            root_agent = str(root.agent_id)
            root_comm = agent_to_comm.get(root_agent)
            root_round = root.round_id if root.round_id is not None else 0

            # BFS/DFS traversal to calculate cascade size, depth, and reach
            visited_events: Set[str] = {root.event_id}
            participating_agents: Set[str] = {root_agent}
            max_depth = 0
            max_round = root_round
            reposts = 0
            replies = 0
            likes = 0
            cross_comm = 0

            queue: List[Tuple[SimulationEvent, int]] = [(root, 0)]
            while queue:
                curr_evt, curr_depth = queue.pop(0)
                if curr_depth > max_depth:
                    max_depth = curr_depth

                if curr_evt.round_id is not None and curr_evt.round_id > max_round:
                    max_round = curr_evt.round_id

                for child in children_map.get(curr_evt.event_id, []):
                    if child.event_id not in visited_events:
                        visited_events.add(child.event_id)
                        child_agent = str(child.agent_id)
                        participating_agents.add(child_agent)

                        if child.action_type in (ActionType.REPOST.value, ActionType.SHARE.value):
                            reposts += 1
                            total_shares += 1
                        elif child.action_type == ActionType.REPLY.value:
                            replies += 1
                        elif child.action_type == ActionType.LIKE.value:
                            likes += 1

                        if root_comm and child_agent in agent_to_comm:
                            if agent_to_comm[child_agent] != root_comm:
                                cross_comm += 1

                        queue.append((child, curr_depth + 1))

            cascade_size = len(visited_events)
            downstream_count = cascade_size - 1
            total_downstream += downstream_count
            duration = max(0, max_round - root_round)

            cascades.append(CascadeTree(
                cascade_id=cid,
                root_event_id=root.event_id,
                root_agent_id=root_agent,
                root_agent_name=root.agent_name,
                root_content=root.content,
                root_round=root_round,
                cascade_size=cascade_size,
                cascade_depth=max_depth,
                cascade_duration_rounds=duration,
                repost_count=reposts,
                reply_count=replies,
                like_count=likes,
                participating_agents=list(participating_agents),
                cross_community_count=cross_comm,
            ))

        n_cascades = len(cascades)
        mean_size = sum(c.cascade_size for c in cascades) / n_cascades if n_cascades > 0 else 0.0
        max_d = max((c.cascade_depth for c in cascades), default=0)
        total_events = len(events)
        diffusion_rate = total_downstream / total_events if total_events > 0 else 0.0
        repost_ratio = total_shares / total_events if total_events > 0 else 0.0

        # Sort top cascades by size descending
        sorted_cascades = sorted(cascades, key=lambda c: c.cascade_size, reverse=True)[:5]

        return DiffusionMetrics(
            total_cascades=n_cascades,
            total_downstream_actions=total_downstream,
            mean_cascade_size=mean_size,
            max_cascade_depth=max_d,
            overall_diffusion_rate=diffusion_rate,
            repost_ratio=repost_ratio,
            top_cascades=[c.to_dict() for c in sorted_cascades],
        )

    def export_diffusion_json(self, metrics: DiffusionMetrics, output_path: str) -> str:
        """Export diffusion metrics to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
