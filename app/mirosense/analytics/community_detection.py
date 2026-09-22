"""Community Detection & Modularity Analytics.

Detects cohesive agent sub-communities from the simulated interaction graph
using deterministic Louvain/modularity optimization algorithms and computes
community-level stance, internal/external density, and cross-group interactions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from ..schemas.events import SimulationEvent


@dataclass
class CommunityResult:
    """Detailed structural and behavioral summary of a single detected community."""
    community_id: str
    member_agent_ids: List[str] = field(default_factory=list)
    size: int = 0
    density: float = 0.0
    internal_edges: int = 0
    external_edges: int = 0
    dominant_roles: List[str] = field(default_factory=list)
    dominant_topics: List[str] = field(default_factory=list)
    mean_stance: float = 0.0
    stance_distribution: Dict[str, float] = field(default_factory=dict)
    top_agents: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommunityPartition:
    """Overall community structure and modularity partition."""
    community_count: int = 0
    modularity: float = 0.0
    cross_community_interaction_ratio: float = 0.0
    algorithm: str = "louvain"
    seed: int = 42
    communities: List[CommunityResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "community_count": self.community_count,
            "modularity": round(float(self.modularity), 4),
            "cross_community_interaction_ratio": round(float(self.cross_community_interaction_ratio), 4),
            "algorithm": self.algorithm,
            "seed": self.seed,
            "communities": [c.to_dict() for c in self.communities],
        }


class CommunityDetector:
    """Detects and characterizes communities in multi-agent interaction graphs."""

    def __init__(self, algorithm: str = "louvain", seed: int = 42):
        self.algorithm = algorithm
        self.seed = seed

    def detect(
        self,
        graph: nx.MultiDiGraph,
        events: Optional[List[SimulationEvent]] = None,
        algorithm: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> CommunityPartition:
        """Run deterministic community detection over the interaction graph."""
        algo = algorithm or self.algorithm
        rnd_seed = seed if seed is not None else self.seed

        # Convert to undirected simple graph for modularity clustering
        undirected = nx.Graph()
        for node, data in graph.nodes(data=True):
            if data.get("node_type", "agent") == "agent":
                undirected.add_node(str(node), **data)

        for u, v, data in graph.edges(data=True):
            u_str, v_str = str(u), str(v)
            if u_str in undirected and v_str in undirected and u_str != v_str:
                if undirected.has_edge(u_str, v_str):
                    undirected[u_str][v_str]["weight"] += data.get("weight", 1.0)
                else:
                    undirected.add_edge(u_str, v_str, weight=data.get("weight", 1.0))

        n_nodes = undirected.number_of_nodes()
        if n_nodes == 0:
            return CommunityPartition(algorithm=algo, seed=rnd_seed)

        # 1. Detect communities
        raw_communities: List[Set[str]] = []
        if undirected.number_of_edges() > 0:
            try:
                if algo == "louvain":
                    raw_communities = nx.community.louvain_communities(
                        undirected, weight="weight", seed=rnd_seed
                    )
                else:
                    raw_communities = list(
                        nx.community.greedy_modularity_communities(undirected, weight="weight")
                    )
            except Exception:
                raw_communities = [set(c) for c in nx.connected_components(undirected)]
        else:
            # All isolated nodes
            raw_communities = [{node} for node in undirected.nodes()]

        # Filter empty sets and sort by size descending
        raw_communities = sorted(
            [c for c in raw_communities if len(c) > 0],
            key=lambda c: len(c),
            reverse=True,
        )

        # 2. Compute Newman-Girvan Modularity Q
        try:
            if undirected.number_of_edges() > 0 and len(raw_communities) > 1:
                modularity_val = float(nx.community.modularity(undirected, raw_communities, weight="weight"))
            else:
                modularity_val = 0.0
        except Exception:
            modularity_val = 0.0

        # Map agent -> community_id
        agent_to_comm: Dict[str, str] = {}
        for idx, comm_set in enumerate(raw_communities):
            comm_id = f"comm_{idx}"
            for agent_id in comm_set:
                agent_to_comm[agent_id] = comm_id

        # 3. Compute cross-community edge ratio
        total_interactions = 0
        cross_interactions = 0
        for u, v, _ in graph.edges(data=True):
            u_str, v_str = str(u), str(v)
            if u_str in agent_to_comm and v_str in agent_to_comm and u_str != v_str:
                total_interactions += 1
                if agent_to_comm[u_str] != agent_to_comm[v_str]:
                    cross_interactions += 1

        cross_ratio = (cross_interactions / total_interactions) if total_interactions > 0 else 0.0

        # 4. Extract per-agent stances and topics from events
        agent_stances: Dict[str, List[float]] = defaultdict(list)
        agent_topics: Dict[str, List[str]] = defaultdict(list)
        if events:
            for evt in events:
                aid = str(evt.agent_id)
                if evt.stance is not None:
                    agent_stances[aid].append(evt.stance)
                if evt.topic:
                    agent_topics[aid].append(evt.topic)

        # 5. Build detailed CommunityResult objects
        community_results: List[CommunityResult] = []
        for idx, comm_set in enumerate(raw_communities):
            comm_id = f"comm_{idx}"
            members = sorted(list(comm_set))
            subgraph = undirected.subgraph(comm_set)
            internal_edges = subgraph.number_of_edges()

            # External edges
            external_edges = 0
            for u in comm_set:
                for v in undirected.neighbors(u):
                    if v not in comm_set:
                        external_edges += 1

            # Density
            k = len(members)
            density = (2.0 * internal_edges / (k * (k - 1))) if k > 1 else 1.0

            # Roles
            roles = [undirected.nodes[m].get("role", "Citizen") for m in members]
            dominant_roles = [r for r, _ in Counter(roles).most_common(3)]

            # Topics
            comm_topics: List[str] = []
            for m in members:
                comm_topics.extend(agent_topics.get(m, []))
            dominant_topics = [t for t, _ in Counter(comm_topics).most_common(3)]

            # Stances
            comm_stances: List[float] = []
            for m in members:
                comm_stances.extend(agent_stances.get(m, []))

            if comm_stances:
                mean_stance = round(sum(comm_stances) / len(comm_stances), 4)
                pos = sum(1 for s in comm_stances if s > 0.1)
                neg = sum(1 for s in comm_stances if s < -0.1)
                neu = len(comm_stances) - pos - neg
                total_s = len(comm_stances)
                stance_dist = {
                    "supportive": round(pos / total_s, 4),
                    "opposed": round(neg / total_s, 4),
                    "neutral": round(neu / total_s, 4),
                }
            else:
                mean_stance = 0.0
                stance_dist = {"supportive": 0.0, "opposed": 0.0, "neutral": 1.0}

            # Top member agents by degree
            top_members = []
            for m in sorted(members, key=lambda x: undirected.degree(x), reverse=True)[:5]:
                top_members.append({
                    "agent_id": m,
                    "name": undirected.nodes[m].get("name", f"Agent_{m}"),
                    "role": undirected.nodes[m].get("role", "Citizen"),
                    "degree": int(undirected.degree(m)),
                })

            community_results.append(CommunityResult(
                community_id=comm_id,
                member_agent_ids=members,
                size=len(members),
                density=round(float(density), 4),
                internal_edges=internal_edges,
                external_edges=external_edges,
                dominant_roles=dominant_roles,
                dominant_topics=dominant_topics,
                mean_stance=mean_stance,
                stance_distribution=stance_dist,
                top_agents=top_members,
            ))

        return CommunityPartition(
            community_count=len(community_results),
            modularity=round(float(modularity_val), 4),
            cross_community_interaction_ratio=round(float(cross_ratio), 4),
            algorithm=algo,
            seed=rnd_seed,
            communities=community_results,
        )

    def export_communities_json(self, partition: CommunityPartition, output_path: str) -> str:
        """Export community partition to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(partition.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
