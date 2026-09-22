"""Unit tests for opinion dynamics analyzer."""

from app.mirosense.schemas.events import SimulationEvent
from app.mirosense.analytics.opinion_dynamics import OpinionDynamicsAnalyzer


def test_opinion_dynamics_consensus_and_acceptance():
    events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="1", action_type="POST", stance=0.9),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T2", agent_id="2", action_type="REPLY", stance=0.8),
        SimulationEvent(event_id="e3", simulation_id="s1", round_id=1, timestamp="T3", agent_id="3", action_type="REPLY", stance=0.7),
    ]

    analyzer = OpinionDynamicsAnalyzer()
    metrics = analyzer.analyze(events)

    assert metrics.sample_size == 3
    assert metrics.mean_stance == 0.8
    assert metrics.acceptance > 0.8
    assert metrics.support_ratio == 1.0
    assert metrics.opposition_ratio == 0.0
    assert metrics.agreement > 0.9  # High cohesion


def test_opinion_dynamics_divided_population():
    events = [
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T1", agent_id="1", action_type="POST", stance=1.0),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T2", agent_id="2", action_type="POST", stance=-1.0),
    ]

    analyzer = OpinionDynamicsAnalyzer()
    metrics = analyzer.analyze(events)

    assert metrics.sample_size == 2
    assert metrics.mean_stance == 0.0
    assert metrics.stance_std == 1.0
    assert metrics.agreement == 0.0  # Max divergence
