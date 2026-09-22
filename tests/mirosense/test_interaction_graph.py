"""Unit tests for interaction graph builder and network metrics."""

import networkx as nx
from pathlib import Path
from app.mirosense.schemas.events import SimulationEvent, ActionType
from app.mirosense.analytics.interaction_graph import InteractionGraphBuilder, NetworkMetrics


def test_interaction_graph_construction_and_centrality():
    events = [
        SimulationEvent(
            event_id="e1", simulation_id="s1", round_id=0, timestamp="T1",
            agent_id="agent_1", agent_name="Mayor", action_type="CREATE_POST",
        ),
        SimulationEvent(
            event_id="e2", simulation_id="s1", round_id=1, timestamp="T2",
            agent_id="agent_2", agent_name="Citizen A", action_type="REPLY",
            target_agent_id="agent_1",
        ),
        SimulationEvent(
            event_id="e3", simulation_id="s1", round_id=1, timestamp="T3",
            agent_id="agent_3", agent_name="Citizen B", action_type="REPLY",
            target_agent_id="agent_1",
        ),
        SimulationEvent(
            event_id="e4", simulation_id="s1", round_id=2, timestamp="T4",
            agent_id="agent_3", agent_name="Citizen B", action_type="LIKE",
            target_agent_id="agent_2",
        ),
    ]

    builder = InteractionGraphBuilder()
    graph = builder.build_graph(events)

    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3

    metrics = builder.compute_metrics(graph)
    assert metrics.node_count == 3
    assert metrics.edge_count == 3
    assert len(metrics.top_pagerank_agents) > 0
    # Agent 1 was replied to by both Agent 2 and 3, so Agent 1 has highest in-degree / PageRank
    assert metrics.top_pagerank_agents[0]["agent_id"] == "agent_1"


def test_interaction_graph_empty_and_isolated_edges(tmp_path: Path):
    builder = InteractionGraphBuilder()
    empty_graph = builder.build_graph([])
    metrics = builder.compute_metrics(empty_graph)

    assert metrics.node_count == 0
    assert metrics.edge_count == 0
    assert metrics.density == 0.0

    out_file = tmp_path / "graph.json"
    builder.export_graph_json(empty_graph, metrics, str(out_file))
    assert out_file.exists()
