"""Unit tests for OASIS action log adapter."""

import json
import os
from pathlib import Path
from app.mirosense.adapters.oasis_adapter import OasisEventAdapter, compute_lexical_stance
from app.mirosense.schemas.events import ActionType, SimulationEvent
from app.run_artifacts import RunStore
from app.cli import _collect_run_outputs


def test_lexical_stance_computation():
    pos_text = "I strongly support this helpful policy, it provides a great benefit!"
    neg_text = "We strongly oppose this deficit shortfall, tax hike is a terrible burden!"
    neutral_text = "The committee meeting is scheduled for 3 PM on Tuesday."

    assert compute_lexical_stance(pos_text) > 0.0
    assert compute_lexical_stance(neg_text) < 0.0
    assert compute_lexical_stance(neutral_text) == 0.0
    assert compute_lexical_stance(None) is None


def test_normalize_raw_oasis_action():
    adapter = OasisEventAdapter(simulation_id="sim_101", default_platform="reddit")

    raw = {
        "round": 0,
        "timestamp": "2026-09-03T15:13:31.135832",
        "agent_id": 0,
        "agent_name": "City Council",
        "action_type": "CREATE_POST",
        "action_args": {
            "content": "Mayor Sarah Jenkins announced that all city buses will be completely free of charge on weekends."
        },
        "result": None,
        "success": True,
    }

    evt = adapter.normalize_action(raw, index=0)
    assert evt is not None
    assert evt.simulation_id == "sim_101"
    assert evt.round_id == 0
    assert evt.agent_id == "0"
    assert evt.agent_name == "City Council"
    assert evt.action_type == ActionType.CREATE_POST.value
    assert "city buses" in evt.content
    assert evt.platform == "reddit"
    assert evt.event_id.startswith("evt_sim_101_reddit_r0_0")


def test_adapter_skips_lifecycle_events():
    adapter = OasisEventAdapter(simulation_id="sim_101")
    start_event = {"timestamp": "2026-09-03T15:13:31", "event_type": "simulation_start", "total_rounds": 10}
    round_event = {"round": 0, "event_type": "round_start"}

    assert adapter.normalize_action(start_event) is None
    assert adapter.normalize_action(round_event) is None


def test_target_linking_and_canonical_export(tmp_path: Path):
    adapter = OasisEventAdapter(simulation_id="sim_test")

    raw_actions = [
        {
            "round": 0,
            "timestamp": "2026-09-03T15:00:00",
            "agent_id": 1,
            "agent_name": "Alice",
            "action_type": "CREATE_POST",
            "action_args": {"post_id": "post_100", "content": "I support free weekend buses!"},
        },
        {
            "round": 1,
            "timestamp": "2026-09-03T15:05:00",
            "agent_id": 2,
            "agent_name": "Bob",
            "action_type": "REPLY",
            "action_args": {"target_id": "post_100", "content": "I disagree, who pays for this deficit?"},
        },
    ]

    events = adapter.normalize_actions(raw_actions)
    assert len(events) == 2

    evt0 = events[0]
    evt1 = events[1]

    assert evt0.action_type == "CREATE_POST"
    assert evt0.stance > 0.0

    assert evt1.action_type == "REPLY"
    assert evt1.target_post_id == "post_100"
    assert evt1.target_agent_id == "1"
    assert evt1.parent_event_id == evt0.event_id
    assert evt1.stance < 0.0

    # Test JSONL export and re-read
    out_file = tmp_path / "canonical_events.jsonl"
    adapter.export_canonical_jsonl(events, str(out_file))

    assert out_file.exists()
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_adapter_determinism_and_event_id_stability():
    """Verify that running the adapter twice on identical inputs yields bit-for-bit identical outputs."""
    raw_actions = [
        {
            "round": 0,
            "timestamp": "2026-09-03T15:00:00",
            "agent_id": 1,
            "agent_name": "Alice",
            "action_type": "CREATE_POST",
            "action_args": {"post_id": "p_1", "content": "Great initiative!"},
        },
        {
            "round": 0,
            "timestamp": "2026-09-03T15:01:00",
            "agent_id": 2,
            "agent_name": "Bob",
            "action_type": "LIKE_POST",
            "action_args": {"target_id": "p_1"},
        },
    ]

    adapter1 = OasisEventAdapter(simulation_id="sim_det")
    adapter2 = OasisEventAdapter(simulation_id="sim_det")

    events1 = adapter1.normalize_actions(raw_actions)
    events2 = adapter2.normalize_actions(raw_actions)

    assert len(events1) == len(events2) == 2
    for e1, e2 in zip(events1, events2):
        assert e1.event_id == e2.event_id
        assert e1.to_dict() == e2.to_dict()


def test_adapter_error_handling_and_malformed_records(tmp_path: Path):
    """Verify safe degradation with empty files, malformed lines, and unknown action types."""
    adapter = OasisEventAdapter(simulation_id="sim_err")

    # 1. Empty file
    empty_file = tmp_path / "empty_actions.jsonl"
    empty_file.write_text("", encoding="utf-8")
    assert adapter.parse_actions_file(str(empty_file)) == []

    # 2. Non-existent file
    assert adapter.parse_actions_file(str(tmp_path / "missing.jsonl")) == []

    # 3. Malformed lines
    malformed_file = tmp_path / "malformed.jsonl"
    malformed_file.write_text(
        '{"round": 0, "agent_id": 1, "action_type": "CREATE_POST", "action_args": {"content": "Hello"}}\n'
        'NOT VALID JSON {{{{ \n'
        '{"round": 1, "agent_id": 2, "action_type": "CUSTOM_UNKNOWN_ACTION", "action_args": {"content": "World"}}\n',
        encoding="utf-8",
    )

    evts = adapter.parse_actions_file(str(malformed_file))
    assert len(evts) == 2
    assert evts[0].action_type == "CREATE_POST"
    assert evts[1].action_type == "UNKNOWN"  # safely classified as UNKNOWN rather than crashing


def test_adapter_on_real_repo_oasis_action_log():
    """Verify parsing against real OASIS actions.jsonl files in the repository."""
    adapter = OasisEventAdapter(simulation_id="run_5fd6fb990dd6")
    real_path = "uploads/runs/run_5fd6fb990dd6/simulation/actions.jsonl"

    if os.path.exists(real_path):
        events = adapter.parse_actions_file(real_path)
        assert len(events) == 4
        assert events[0].agent_name == "David Chen"
        assert events[0].action_type == "CREATE_POST"
        assert events[0].simulation_id == "run_5fd6fb990dd6"


def test_collect_run_outputs_persists_canonical_events(tmp_path: Path):
    """Verify that _collect_run_outputs creates canonical_events.jsonl and updates manifest."""
    store = RunStore(root_dir=str(tmp_path / "runs"))
    manifest = store.create(requirement="Transit Test", source_files=[], project_name="Test Run")
    run_id = manifest["run_id"]

    actions = [
        {
            "round": 0,
            "timestamp": "2026-09-03T16:00:00",
            "agent_id": 1,
            "agent_name": "David",
            "action_type": "CREATE_POST",
            "action_args": {"content": "I support free weekend buses!"},
        }
    ]

    updated_manifest = _collect_run_outputs(
        store=store,
        manifest=manifest,
        graph_data={"nodes": [], "edges": []},
        graph_stats={"node_count": 0, "edge_count": 0},
        timeline=[{"round": 0, "total_actions": 1}],
        agent_stats=[],
        actions=actions,
        report_payload=None,
        report_markdown="",
    )

    assert "canonical_events" in updated_manifest["artifacts"]
    canonical_rel_path = updated_manifest["artifacts"]["canonical_events"]
    canonical_abs_path = os.path.join(store.run_dir(run_id), canonical_rel_path)
    assert os.path.exists(canonical_abs_path)

    adapter = OasisEventAdapter(simulation_id=run_id)
    canonical_evts = adapter.parse_actions_file(canonical_abs_path)
    assert len(canonical_evts) == 1
    assert canonical_evts[0].agent_name == "David"
    assert canonical_evts[0].action_type == "CREATE_POST"
