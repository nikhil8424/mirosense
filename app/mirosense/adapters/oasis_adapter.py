"""OASIS Simulation Action Log Adapter.

Parses and normalizes raw OASIS/MiroFish `actions.jsonl` files and action objects
into canonical `SimulationEvent` streams.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..schemas.events import ActionType, SimulationEvent


# Basic lexicon for deterministic stance proxy extraction when LLM labels are absent
POSITIVE_STANCE_TERMS = {
    "support", "agree", "favor", "welcome", "praise", "endorse", "benefit",
    "positive", "great", "excellent", "good", "helpful", "sustainable", "encourage"
}
NEGATIVE_STANCE_TERMS = {
    "oppose", "disagree", "reject", "criticize", "alarm", "concern", "shortfall",
    "deficit", "tax hike", "costly", "negative", "bad", "terrible", "burden", "protest"
}


def compute_lexical_stance(text: Optional[str]) -> Optional[float]:
    """Compute a deterministic stance proxy in [-1.0, 1.0] from message text.
    
    Returns None if text is empty or neutral without salient indicators.
    """
    if not text:
        return None
    lower = text.lower()
    pos_count = sum(1 for term in POSITIVE_STANCE_TERMS if term in lower)
    neg_count = sum(1 for term in NEGATIVE_STANCE_TERMS if term in lower)

    total = pos_count + neg_count
    if total == 0:
        return 0.0  # Neutral
    # Bounded score in [-1.0, 1.0]
    raw = (pos_count - neg_count) / total
    return round(float(raw), 4)


class OasisEventAdapter:
    """Normalizes OASIS action dictionaries and log files into canonical SimulationEvent objects."""

    def __init__(self, simulation_id: str = "sim_default", default_platform: Optional[str] = None):
        self.simulation_id = simulation_id
        self.default_platform = default_platform
        self._post_to_event_id: Dict[str, str] = {}
        self._post_to_agent_id: Dict[str, str] = {}

    def normalize_action(
        self,
        raw_action: Dict[str, Any],
        index: int = 0,
        simulation_id: Optional[str] = None,
        platform_hint: Optional[str] = None,
    ) -> Optional[SimulationEvent]:
        """Normalize a single OASIS action dictionary into a SimulationEvent.
        
        Returns None if the entry is a lifecycle meta-event (e.g. round_start).
        """
        # Skip simulation lifecycle logs
        if "event_type" in raw_action and raw_action["event_type"] in (
            "simulation_start", "simulation_end", "round_start", "round_end"
        ):
            return None

        sim_id = simulation_id or raw_action.get("simulation_id") or self.simulation_id
        round_id = raw_action.get("round", raw_action.get("round_num"))
        if round_id is not None:
            try:
                round_id = int(round_id)
            except (ValueError, TypeError):
                round_id = None

        timestamp = raw_action.get("timestamp")
        raw_agent_id = raw_action.get("agent_id", raw_action.get("user_id", "0"))
        agent_id = str(raw_agent_id)
        agent_name = raw_action.get("agent_name", raw_action.get("user_name"))

        raw_action_type = raw_action.get("action_type", "")
        action_type = ActionType.from_str(raw_action_type).value

        action_args = raw_action.get("action_args") or {}
        if isinstance(action_args, str):
            try:
                action_args = json.loads(action_args)
            except Exception:
                action_args = {"raw_content": action_args}

        # Extract content text
        content = (
            action_args.get("content")
            or action_args.get("text")
            or action_args.get("message")
            or action_args.get("comment")
            or raw_action.get("content")
        )

        # Platform detection
        platform = (
            raw_action.get("platform")
            or platform_hint
            or self.default_platform
            or ("reddit" if "reddit" in str(raw_action).lower() else "twitter")
        )

        # Target post and parent identification
        target_post_id = (
            action_args.get("post_id")
            or action_args.get("target_post_id")
            or action_args.get("target_id")
            or action_args.get("parent_id")
            or action_args.get("comment_id")
        )
        if target_post_id is not None:
            target_post_id = str(target_post_id)

        # Target agent identification
        target_agent_id = action_args.get("target_user_id") or action_args.get("target_agent_id")
        if target_agent_id is None and target_post_id and target_post_id in self._post_to_agent_id:
            target_agent_id = self._post_to_agent_id[target_post_id]
        if target_agent_id is not None:
            target_agent_id = str(target_agent_id)

        # Parent event link
        parent_event_id = None
        if target_post_id and target_post_id in self._post_to_event_id:
            parent_event_id = self._post_to_event_id[target_post_id]

        # Generate deterministic event_id
        safe_plat = platform or "oasis"
        safe_round = round_id if round_id is not None else "0"
        event_id = f"evt_{sim_id}_{safe_plat}_r{safe_round}_{index}"

        # Record post author mapping if this is a post creation
        if action_type == ActionType.CREATE_POST.value:
            post_id_val = action_args.get("post_id") or f"p_{safe_round}_{agent_id}_{index}"
            self._post_to_event_id[str(post_id_val)] = event_id
            self._post_to_agent_id[str(post_id_val)] = agent_id

        # Compute stance / sentiment
        stance = compute_lexical_stance(content)
        sentiment = stance  # Stance proxy aligns with sentiment for plain text unless overridden

        # Extract role if available in args or raw
        agent_role = action_args.get("agent_role") or raw_action.get("agent_role")

        return SimulationEvent(
            event_id=event_id,
            simulation_id=sim_id,
            round_id=round_id,
            timestamp=timestamp,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_role=agent_role,
            action_type=action_type,
            target_agent_id=target_agent_id,
            target_post_id=target_post_id,
            content=content,
            sentiment=sentiment,
            stance=stance,
            topic=action_args.get("topic"),
            community_id=action_args.get("community_id"),
            parent_event_id=parent_event_id,
            platform=platform,
            metadata={
                "success": raw_action.get("success", True),
                "result": raw_action.get("result"),
                "raw_action_type": raw_action_type,
                "action_args": action_args,
            },
        )

    def normalize_actions(
        self,
        actions: Iterable[Dict[str, Any]],
        simulation_id: Optional[str] = None,
        platform_hint: Optional[str] = None,
    ) -> List[SimulationEvent]:
        """Normalize a collection of raw actions into a list of SimulationEvents."""
        events: List[SimulationEvent] = []
        for idx, item in enumerate(actions):
            if isinstance(item, dict):
                evt = self.normalize_action(
                    item, index=idx, simulation_id=simulation_id, platform_hint=platform_hint
                )
                if evt is not None:
                    events.append(evt)
        return events

    def parse_actions_file(
        self,
        file_path: str,
        simulation_id: Optional[str] = None,
        platform_hint: Optional[str] = None,
    ) -> List[SimulationEvent]:
        """Read a raw `actions.jsonl` file and return a normalized list of SimulationEvents."""
        if not os.path.exists(file_path):
            return []

        raw_items: List[Dict[str, Any]] = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    try:
                        raw_items.append(json.loads(line_str))
                    except json.JSONDecodeError:
                        continue

        return self.normalize_actions(
            raw_items, simulation_id=simulation_id, platform_hint=platform_hint
        )

    def export_canonical_jsonl(self, events: List[SimulationEvent], output_path: str) -> str:
        """Write canonical events to a JSON Lines file deterministically."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for evt in events:
                f.write(evt.to_json() + "\n")
        return output_path
