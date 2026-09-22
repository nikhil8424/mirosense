"""Unit tests for MiroSense canonical SimulationEvent schema."""

import json
from app.mirosense.schemas.events import SimulationEvent, ActionType


def test_simulation_event_creation_and_serialization():
    evt = SimulationEvent(
        event_id="evt_sim_001_twitter_r0_1",
        simulation_id="sim_001",
        round_id=0,
        timestamp="2026-09-21T12:00:00",
        agent_id="agent_42",
        agent_name="Mayor Jenkins",
        agent_role="Executive",
        action_type=ActionType.CREATE_POST.value,
        target_agent_id=None,
        target_post_id=None,
        content="Free transit for all citizens starting next month!",
        sentiment=0.85,
        stance=1.0,
        topic="Transit Policy",
        community_id="comm_0",
        parent_event_id=None,
        platform="twitter",
        metadata={"success": True},
    )

    data = evt.to_dict()
    assert data["event_id"] == "evt_sim_001_twitter_r0_1"
    assert data["stance"] == 1.0
    assert data["action_type"] == "CREATE_POST"

    json_str = evt.to_json()
    assert "Mayor Jenkins" in json_str

    deserialized = SimulationEvent.from_json(json_str)
    assert deserialized.event_id == evt.event_id
    assert deserialized.agent_id == "agent_42"
    assert deserialized.sentiment == 0.85
    assert deserialized.stance == 1.0


def test_simulation_event_nullable_fields():
    evt = SimulationEvent(
        event_id="evt_empty",
        simulation_id="sim_test",
        round_id=None,
        timestamp=None,
        agent_id="0",
    )

    assert evt.target_agent_id is None
    assert evt.target_post_id is None
    assert evt.content is None
    assert evt.sentiment is None
    assert evt.stance is None
    assert evt.action_type == ActionType.UNKNOWN.value

    d = evt.to_dict()
    reconstructed = SimulationEvent.from_dict(d)
    assert reconstructed.event_id == "evt_empty"
    assert reconstructed.agent_id == "0"
    assert reconstructed.round_id is None


def test_action_type_normalization():
    assert ActionType.from_str("create_post") == ActionType.CREATE_POST
    assert ActionType.from_str("LIKE_POST") == ActionType.LIKE
    assert ActionType.from_str("upvote") == ActionType.LIKE
    assert ActionType.from_str("RETWEET") == ActionType.REPOST
    assert ActionType.from_str("comment") == ActionType.REPLY
    assert ActionType.from_str("unknown_action_xyz") == ActionType.UNKNOWN
    assert ActionType.from_str(None) == ActionType.UNKNOWN
