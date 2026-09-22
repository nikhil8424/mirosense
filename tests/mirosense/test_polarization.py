"""Unit tests for decomposed polarization model."""

from app.mirosense.schemas.events import SimulationEvent
from app.mirosense.analytics.polarization import PolarizationAnalyzer
from app.mirosense.analytics.community_detection import CommunityPartition, CommunityResult


def test_polarization_decomposition_cohesive_vs_divided():
    analyzer = PolarizationAnalyzer(w_opinion=0.4, w_network=0.3, w_interaction=0.3)

    # Cohesive population
    cohesive_events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="1", stance=0.8),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T2", agent_id="2", stance=0.9),
    ]
    cohesive_partition = CommunityPartition(community_count=1, modularity=0.0, cross_community_interaction_ratio=1.0)
    res_cohesive = analyzer.analyze(cohesive_events, cohesive_partition)

    assert res_cohesive.p_total < 0.2
    assert "Low Polarization" in res_cohesive.interpretation

    # Divided polarized factions
    divided_events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="1", stance=1.0),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T2", agent_id="2", stance=-1.0),
    ]
    divided_partition = CommunityPartition(community_count=2, modularity=0.8, cross_community_interaction_ratio=0.05)
    res_divided = analyzer.analyze(divided_events, divided_partition)

    assert res_divided.p_total > 0.7
    assert res_divided.p_opinion > 0.9
    assert res_divided.p_network > 0.7
    assert res_divided.p_interaction > 0.9
    assert "High Polarization" in res_divided.interpretation
