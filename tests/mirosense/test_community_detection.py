"""Unit tests for deterministic community detection and modularity."""

from pathlib import Path
from app.mirosense.schemas.events import SimulationEvent
from app.mirosense.analytics.interaction_graph import InteractionGraphBuilder
from app.mirosense.analytics.community_detection import CommunityDetector


def test_community_detection_bipartite_factions(tmp_path: Path):
    # Create two tightly-knit factions: {A1, A2} and {B1, B2} with 1 bridge interaction
    events = [
        # Faction A internal
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="A1", action_type="REPLY", target_agent_id="A2", stance=0.8),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T2", agent_id="A2", action_type="REPLY", target_agent_id="A1", stance=0.9),
        # Faction B internal
        SimulationEvent(event_id="e3", simulation_id="s1", round_id=0, timestamp="T3", agent_id="B1", action_type="REPLY", target_agent_id="B2", stance=-0.8),
        SimulationEvent(event_id="e4", simulation_id="s1", round_id=0, timestamp="T4", agent_id="B2", action_type="REPLY", target_agent_id="B1", stance=-0.7),
        # Cross bridge
        SimulationEvent(event_id="e5", simulation_id="s1", round_id=1, timestamp="T5", agent_id="A1", action_type="DISAGREE", target_agent_id="B1", stance=-0.5),
    ]

    builder = InteractionGraphBuilder()
    graph = builder.build_graph(events)

    detector = CommunityDetector(seed=42)
    partition = detector.detect(graph, events)

    assert partition.community_count >= 2
    assert partition.modularity > 0.0
    assert partition.cross_community_interaction_ratio > 0.0

    out_file = tmp_path / "communities.json"
    detector.export_communities_json(partition, str(out_file))
    assert out_file.exists()


def test_community_detection_single_node():
    events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="Solo", action_type="CREATE_POST", stance=0.0),
    ]
    builder = InteractionGraphBuilder()
    graph = builder.build_graph(events)

    detector = CommunityDetector()
    partition = detector.detect(graph, events)

    assert partition.community_count == 1
    assert partition.communities[0].size == 1
