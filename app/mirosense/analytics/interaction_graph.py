"""Interaction Graph Builder & Network Centrality Analytics.

Constructs directed, weighted interaction networks from canonical simulation events
and computes deterministic topological and centrality metrics.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, asdict
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from ..schemas.events import SimulationEvent, ActionType


@dataclass
class NetworkMetrics:
    """Graph-level topological and centrality summary."""
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0
    reciprocity: float = 0.0
    weakly_connected_components: int = 0
    strongly_connected_components: int = 0
    average_clustering: float = 0.0
    is_directed: bool = True
    top_pagerank_agents: List[Dict[str, Any]] = field(default_factory=list)
    top_betweenness_agents: List[Dict[str, Any]] = field(default_factory=list)
    top_degree_agents: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class InteractionGraphBuilder:
    """Builds and analyzes multi-agent interaction networks from simulation events."""

    def __init__(self, include_posts: bool = False):
        self.include_posts = include_posts

    def build_graph(self, events: List[SimulationEvent]) -> nx.MultiDiGraph:
        """Construct a NetworkX MultiDiGraph from canonical simulation events.
        
        Edges represent directed interactions from source agent to target agent.
        """
        graph = nx.MultiDiGraph()
        agent_names: Dict[str, str] = {}
        agent_roles: Dict[str, str] = {}
        agent_actions_count: Dict[str, int] = defaultdict(int)

        # 1. Discover all agents and their metadata
        for evt in events:
            if not evt.agent_id:
                continue
            agent_id = str(evt.agent_id)
            agent_actions_count[agent_id] += 1
            if evt.agent_name and agent_id not in agent_names:
                agent_names[agent_id] = evt.agent_name
            if evt.agent_role and agent_id not in agent_roles:
                agent_roles[agent_id] = evt.agent_role

        # Add agent nodes
        for agent_id, act_count in agent_actions_count.items():
            graph.add_node(
                agent_id,
                node_type="agent",
                name=agent_names.get(agent_id, f"Agent_{agent_id}"),
                role=agent_roles.get(agent_id, "Citizen"),
                total_actions=act_count,
            )

        # 2. Add edges for directed interactions
        for evt in events:
            source = str(evt.agent_id)
            target = str(evt.target_agent_id) if evt.target_agent_id is not None else None

            # Add post node if configured
            if self.include_posts and evt.action_type == ActionType.CREATE_POST.value:
                post_id = f"post_{evt.event_id}"
                graph.add_node(post_id, node_type="post", content=evt.content or "")
                graph.add_edge(source, post_id, relation="AUTHORED", round=evt.round_id, weight=1.0)

            # Direct agent-to-agent interactions
            if target and target != source and target in graph:
                relation = "INTERACTED_WITH"
                if evt.action_type == ActionType.REPLY.value:
                    relation = "REPLIED_TO"
                elif evt.action_type == ActionType.LIKE.value:
                    relation = "LIKED"
                elif evt.action_type in (ActionType.REPOST.value, ActionType.SHARE.value):
                    relation = "REPOSTED"
                elif evt.action_type == ActionType.FOLLOW.value:
                    relation = "FOLLOWED"
                elif evt.action_type == ActionType.DISAGREE.value:
                    relation = "DISAGREED_WITH"
                elif evt.action_type == ActionType.SUPPORT.value:
                    relation = "SUPPORTED"

                graph.add_edge(
                    source,
                    target,
                    key=evt.event_id,
                    relation=relation,
                    action_type=evt.action_type,
                    round=evt.round_id,
                    timestamp=evt.timestamp,
                    stance=evt.stance,
                    weight=1.0,
                )

        return graph

    def to_simple_digraph(self, multi_graph: nx.MultiDiGraph) -> nx.DiGraph:
        """Collapse a MultiDiGraph into a weighted simple DiGraph for centrality calculations."""
        simple = nx.DiGraph()
        for node, data in multi_graph.nodes(data=True):
            if data.get("node_type") == "agent":
                simple.add_node(node, **data)

        edge_weights: Dict[Tuple[str, str], float] = defaultdict(float)
        for u, v, data in multi_graph.edges(data=True):
            if u in simple and v in simple and u != v:
                edge_weights[(u, v)] += data.get("weight", 1.0)

        for (u, v), weight in edge_weights.items():
            simple.add_edge(u, v, weight=weight)

        return simple

    def compute_metrics(self, graph: nx.MultiDiGraph) -> NetworkMetrics:
        """Calculate graph topological and centrality metrics."""
        simple_graph = self.to_simple_digraph(graph)
        n_nodes = simple_graph.number_of_nodes()
        n_edges = simple_graph.number_of_edges()

        if n_nodes == 0:
            return NetworkMetrics()

        density = float(nx.density(simple_graph)) if n_nodes > 1 else 0.0

        try:
            reciprocity = float(nx.reciprocity(simple_graph))
        except Exception:
            reciprocity = 0.0

        try:
            wcc = nx.number_weakly_connected_components(simple_graph)
            scc = nx.number_strongly_connected_components(simple_graph)
        except Exception:
            wcc, scc = 1, 1

        try:
            avg_clustering = float(nx.average_clustering(simple_graph.to_undirected()))
        except Exception:
            avg_clustering = 0.0

        # Centralities
        try:
            pagerank_scores = nx.pagerank(simple_graph, weight="weight", alpha=0.85, max_iter=100)
        except Exception:
            # Fallback for disconnected / singular graphs
            pagerank_scores = {node: 1.0 / n_nodes for node in simple_graph.nodes()}

        try:
            betweenness_scores = nx.betweenness_centrality(simple_graph, weight="weight", normalized=True)
        except Exception:
            betweenness_scores = {node: 0.0 for node in simple_graph.nodes()}

        in_degrees = dict(simple_graph.in_degree())
        out_degrees = dict(simple_graph.out_degree())
        weighted_degrees = {node: sum(data.get("weight", 1.0) for _, _, data in simple_graph.edges(node, data=True)) for node in simple_graph.nodes()}

        # Format top rankings
        def format_top(scores: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
            sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
            result = []
            for node, score in sorted_items:
                node_data = simple_graph.nodes.get(node, {})
                result.append({
                    "agent_id": node,
                    "name": node_data.get("name", f"Agent_{node}"),
                    "role": node_data.get("role", "Citizen"),
                    "score": round(float(score), 4),
                })
            return result

        top_pr = format_top(pagerank_scores)
        top_bw = format_top(betweenness_scores)
        top_deg = format_top(weighted_degrees)

        return NetworkMetrics(
            node_count=n_nodes,
            edge_count=n_edges,
            density=round(density, 4),
            reciprocity=round(reciprocity, 4),
            weakly_connected_components=wcc,
            strongly_connected_components=scc,
            average_clustering=round(avg_clustering, 4),
            is_directed=True,
            top_pagerank_agents=top_pr,
            top_betweenness_agents=top_bw,
            top_degree_agents=top_deg,
        )

    def export_graph_json(self, graph: nx.MultiDiGraph, metrics: NetworkMetrics, output_path: str) -> str:
        """Export interaction graph structure and metrics to JSON."""
        nodes_list = []
        simple = self.to_simple_digraph(graph)

        try:
            pr_map = nx.pagerank(simple, weight="weight", alpha=0.85, max_iter=100) if simple.number_of_nodes() > 0 else {}
        except Exception:
            pr_map = {}

        try:
            bw_map = nx.betweenness_centrality(simple, weight="weight") if simple.number_of_nodes() > 0 else {}
        except Exception:
            bw_map = {}

        for node, data in graph.nodes(data=True):
            nodes_list.append({
                "id": str(node),
                "name": data.get("name", str(node)),
                "role": data.get("role", "Citizen"),
                "node_type": data.get("node_type", "agent"),
                "in_degree": int(simple.in_degree(node)) if node in simple else 0,
                "out_degree": int(simple.out_degree(node)) if node in simple else 0,
                "pagerank": round(float(pr_map.get(node, 0.0)), 4),
                "betweenness": round(float(bw_map.get(node, 0.0)), 4),
            })

        edges_list = []
        for u, v, k, data in graph.edges(keys=True, data=True):
            edges_list.append({
                "source": str(u),
                "target": str(v),
                "key": str(k),
                "relation": data.get("relation", "INTERACTED_WITH"),
                "action_type": data.get("action_type", "UNKNOWN"),
                "round": data.get("round"),
                "weight": float(data.get("weight", 1.0)),
                "stance": data.get("stance"),
            })

        payload = {
            "metrics": metrics.to_dict(),
            "nodes": nodes_list,
            "edges": edges_list,
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return output_path
