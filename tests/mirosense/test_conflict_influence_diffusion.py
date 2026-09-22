"""Unit tests for conflict, influence, and diffusion analytics."""

from app.mirosense.schemas.events import SimulationEvent, ActionType
from app.mirosense.analytics.interaction_graph import InteractionGraphBuilder
from app.mirosense.analytics.community_detection import CommunityDetector, CommunityPartition, CommunityResult
from app.mirosense.analytics.conflict_analysis import ConflictAnalyzer
from app.mirosense.analytics.influence_analysis import InfluenceAnalyzer
from app.mirosense.analytics.information_diffusion import DiffusionAnalyzer


def test_conflict_analysis():
    events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, agent_id="1", action_type="CREATE_POST", stance=0.8),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, agent_id="2", target_agent_id="1", action_type="DISAGREE", stance=-0.9),
        SimulationEvent(event_id="e3", simulation_id="s1", round_id=1, agent_id="3", target_agent_id="1", action_type="REPLY", stance=-0.5),
    ]
    partition = CommunityPartition(
        communities=[
            CommunityResult(community_id="comm_0", member_agent_ids=["1"]),
            CommunityResult(community_id="comm_1", member_agent_ids=["2", "3"]),
        ]
    )

    analyzer = ConflictAnalyzer()
    metrics = analyzer.analyze(events, partition)

    assert metrics.total_conflicts == 2
    assert metrics.cross_community_conflicts == 2
    assert metrics.cross_community_conflict_ratio == 1.0


def test_influence_and_gini_ranking():
    events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, agent_id="Leader", action_type="CREATE_POST"),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, agent_id="Follower1", target_agent_id="Leader", action_type="REPLY"),
        SimulationEvent(event_id="e3", simulation_id="s1", round_id=0, agent_id="Follower2", target_agent_id="Leader", action_type="LIKE"),
        SimulationEvent(event_id="e4", simulation_id="s1", round_id=1, agent_id="Follower3", target_agent_id="Leader", action_type="REPOST"),
    ]

    builder = InteractionGraphBuilder()
    graph = builder.build_graph(events)

    inf_analyzer = InfluenceAnalyzer()
    ranking = inf_analyzer.analyze(graph, events)

    assert ranking.total_evaluated_agents == 4
    assert len(ranking.top_influential_agents) > 0
    assert ranking.top_influential_agents[0]["agent_id"] == "Leader"
    assert ranking.influence_concentration_gini > 0.0


def test_information_diffusion_cascade():
    events = [
        SimulationEvent(event_id="e_root", simulation_id="s1", round_id=0, agent_id="Author", action_type="CREATE_POST", content="Root Announcement"),
        SimulationEvent(event_id="e_child1", simulation_id="s1", round_id=1, agent_id="Reposter", parent_event_id="e_root", action_type="REPOST"),
        SimulationEvent(event_id="e_grandchild", simulation_id="s1", round_id=2, agent_id="Commenter", parent_event_id="e_child1", action_type="REPLY"),
    ]

    analyzer = DiffusionAnalyzer()
    diff = analyzer.analyze(events)

    assert diff.total_cascades == 1
    assert diff.max_cascade_depth == 2
    assert diff.total_downstream_actions == 2
    assert diff.repost_ratio > 0.0
