"""Simulated Network Influence Analytics.

Computes multi-dimensional simulated network influence based on graph centrality
(PageRank, in-degree, betweenness) and Gini inequality distribution.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, asdict
import json
import math
import os
from typing import Any, Dict, List, Optional

import networkx as nx

from ..schemas.events import SimulationEvent
from .interaction_graph import InteractionGraphBuilder
from .community_detection import CommunityPartition


def compute_gini_coefficient(values: List[float]) -> float:
    """Calculate the Gini coefficient of a distribution in [0, 1]."""
    if not values or len(values) < 2:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0

    cumulative_sum = 0.0
    for i, val in enumerate(sorted_vals):
        cumulative_sum += (i + 1) * val

    gini = (2.0 * cumulative_sum) / (n * total) - (n + 1.0) / n
    return min(max(gini, 0.0), 1.0)


@dataclass
class InfluenceRanking:
    """Simulated network influence rankings and concentration indices."""
    top_influential_agents: List[Dict[str, Any]] = field(default_factory=list)
    influence_concentration_gini: float = 0.0
    influence_by_community: Dict[str, float] = field(default_factory=dict)
    total_evaluated_agents: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "top_influential_agents": self.top_influential_agents,
            "influence_concentration_gini": round(float(self.influence_concentration_gini), 4),
            "influence_by_community": {k: round(v, 4) for k, v in self.influence_by_community.items()},
            "total_evaluated_agents": self.total_evaluated_agents,
        }


class InfluenceAnalyzer:
    """Calculates network influence rankings from structural topology."""

    def analyze(
        self,
        graph: nx.MultiDiGraph,
        events: Optional[List[SimulationEvent]] = None,
        partition: Optional[CommunityPartition] = None,
    ) -> InfluenceRanking:
        """Compute composite simulated network influence."""
        builder = InteractionGraphBuilder()
        simple_graph = builder.to_simple_digraph(graph)

        n_nodes = simple_graph.number_of_nodes()
        if n_nodes == 0:
            return InfluenceRanking()

        # Compute standard centralities
        try:
            pr_scores = nx.pagerank(simple_graph, weight="weight", alpha=0.85, max_iter=100)
        except Exception:
            pr_scores = {node: 1.0 / n_nodes for node in simple_graph.nodes()}

        try:
            bw_scores = nx.betweenness_centrality(simple_graph, weight="weight", normalized=True)
        except Exception:
            bw_scores = {node: 0.0 for node in simple_graph.nodes()}

        in_deg = dict(simple_graph.in_degree())
        max_in_deg = max(in_deg.values()) if in_deg and max(in_deg.values()) > 0 else 1

        # Count broadcast posts
        broadcast_posts: Dict[str, int] = defaultdict(int)
        if events:
            for evt in events:
                if evt.action_type == "CREATE_POST" and evt.agent_id:
                    broadcast_posts[str(evt.agent_id)] += 1

        # Composite influence score: 0.45 * PageRank + 0.30 * Normalized InDegree + 0.25 * Betweenness
        influence_scores: Dict[str, float] = {}
        for node in simple_graph.nodes():
            pr = pr_scores.get(node, 0.0)
            in_d_norm = in_deg.get(node, 0) / max_in_deg
            bw = bw_scores.get(node, 0.0)

            score = 0.45 * (pr * n_nodes) + 0.30 * in_d_norm + 0.25 * bw
            influence_scores[str(node)] = float(score)

        # Normalize composite scores so they sum to 1.0
        total_inf = sum(influence_scores.values())
        if total_inf > 0:
            normalized_inf = {k: v / total_inf for k, v in influence_scores.items()}
        else:
            normalized_inf = {k: 1.0 / n_nodes for k in influence_scores}

        # Gini concentration
        gini = compute_gini_coefficient(list(normalized_inf.values()))

        # Community influence breakdown
        comm_influence: Dict[str, float] = defaultdict(float)
        if partition:
            for comm in partition.communities:
                for aid in comm.member_agent_ids:
                    comm_influence[comm.community_id] += normalized_inf.get(str(aid), 0.0)

        # Top influencers list
        sorted_nodes = sorted(normalized_inf.items(), key=lambda x: x[1], reverse=True)[:10]
        top_list = []
        for rank, (node, inf_score) in enumerate(sorted_nodes, start=1):
            data = simple_graph.nodes.get(node, {})
            top_list.append({
                "rank": rank,
                "agent_id": str(node),
                "name": data.get("name", f"Agent_{node}"),
                "role": data.get("role", "Citizen"),
                "simulated_influence_score": round(float(inf_score), 4),
                "pagerank": round(float(pr_scores.get(node, 0.0)), 4),
                "in_degree": int(in_deg.get(node, 0)),
                "betweenness": round(float(bw_scores.get(node, 0.0)), 4),
                "posts_authored": int(broadcast_posts.get(str(node), 0)),
            })

        return InfluenceRanking(
            top_influential_agents=top_list,
            influence_concentration_gini=round(float(gini), 4),
            influence_by_community=dict(comm_influence),
            total_evaluated_agents=n_nodes,
        )

    def export_influence_json(self, ranking: InfluenceRanking, output_path: str) -> str:
        """Export influence rankings to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ranking.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
