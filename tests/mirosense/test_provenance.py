"""Tests for metric provenance and audit trail."""

import pytest
from app.mirosense.schemas.events import SimulationEvent, ActionType
from app.mirosense.analytics.opinion_dynamics import OpinionMetrics
from app.mirosense.analytics.polarization import PolarizationDecomposition
from app.mirosense.analytics.conflict_analysis import ConflictMetrics
from app.mirosense.analytics.community_detection import CommunityPartition, CommunityResult
from app.mirosense.provenance.metric_provenance import MetricProvenanceTracker


def test_metric_provenance_tracker():
    tracker = MetricProvenanceTracker()

    events = [
        SimulationEvent(
            event_id="e1",
            simulation_id="run_1",
            agent_id="agent_1",
            action_type=ActionType.CREATE_POST.value,
            content="I strongly support transit line A.",
            stance=0.85,
            round_id=0,
        ),
        SimulationEvent(
            event_id="e2",
            simulation_id="run_1",
            agent_id="agent_2",
            action_type=ActionType.REPLY.value,
            content="I completely oppose this transit spending.",
            stance=-0.9,
            parent_event_id="e1",
            target_agent_id="agent_1",
            round_id=0,
        ),
    ]

    opinion_metrics = OpinionMetrics(
        sample_size=2,
        unique_agents=2,
        mean_stance=-0.025,
        stance_variance=0.7656,
        stance_std=0.875,
        acceptance=0.5,
        agreement=0.5,
        support_ratio=0.5,
        opposition_ratio=0.5,
        neutral_ratio=0.0,
    )

    polarization = PolarizationDecomposition(
        p_total=0.875,
        p_opinion=0.875,
        p_network=0.0,
        p_interaction=0.5,
    )

    conflict = ConflictMetrics(
        total_conflicts=1,
        total_actions=1,
        conflict_rate=1.0,
        cross_community_conflicts=0,
        internal_community_conflicts=1,
        cross_community_conflict_ratio=0.0,
    )

    partition = CommunityPartition(
        community_count=1,
        modularity=0.0,
        communities=[
            CommunityResult(
                community_id="c_0",
                member_agent_ids=["agent_1", "agent_2"],
                size=2,
                mean_stance=-0.025,
                internal_edges=1,
                external_edges=0,
            )
        ],
    )

    records = tracker.build_provenance_index(
        simulation_id="sim_1",
        run_id="run_1",
        events=events,
        opinion_metrics=opinion_metrics,
        polarization=polarization,
        conflict_metrics=conflict,
        partition=partition,
        scenario_id="scenario_transit",
        source_files=["transit_policy.md"],
        source_entities=["Line A", "Budget"],
    )

    assert "acceptance" in records
    assert "polarization" in records
    assert "conflict_rate" in records
    assert "modularity" in records

    acc_rec = records["acceptance"]
    assert acc_rec.metric_value == 0.5
    assert "e1" in acc_rec.constituent_event_ids
    assert "agent_1" in acc_rec.constituent_agent_ids
    assert "transit_policy.md" in acc_rec.source_evidence_files
