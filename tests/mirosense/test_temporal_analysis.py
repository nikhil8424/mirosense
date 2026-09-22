"""Unit tests for temporal dynamics time-series analyzer."""

from app.mirosense.schemas.events import SimulationEvent, ActionType
from app.mirosense.analytics.temporal_analysis import TemporalAnalyzer


def test_temporal_trajectory_calculation():
    events = [
        # Round 0: High initial excitement
        SimulationEvent(event_id="e1", simulation_id="s1", round_id=0, timestamp="T0", agent_id="1", action_type="CREATE_POST", stance=0.9),
        SimulationEvent(event_id="e2", simulation_id="s1", round_id=0, timestamp="T0", agent_id="2", action_type="SUPPORT", stance=0.8),
        # Round 1: Opposition emerges
        SimulationEvent(event_id="e3", simulation_id="s1", round_id=1, timestamp="T1", agent_id="3", action_type="DISAGREE", stance=-0.8),
        SimulationEvent(event_id="e4", simulation_id="s1", round_id=1, timestamp="T1", agent_id="4", action_type="REPOST", stance=0.0),
    ]

    analyzer = TemporalAnalyzer()
    series = analyzer.analyze(events)

    assert series.total_rounds == 2
    assert series.total_actions == 4
    assert len(series.snapshots) == 2

    snap0 = series.snapshots[0]
    snap1 = series.snapshots[1]

    assert snap0.round_id == 0
    assert snap0.mean_stance > 0.8
    assert snap0.conflict_count == 0

    assert snap1.round_id == 1
    assert snap1.mean_stance < 0.0
    assert snap1.conflict_count == 1
    assert snap1.share_count == 1
    assert snap1.diffusion_rate == 0.5
