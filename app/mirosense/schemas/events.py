"""Canonical Simulation Event Schema.

Defines the normalized event data structure produced by social simulation runtimes
and consumed by all MiroSense analytical and validation layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional
import json


class ActionType(str, Enum):
    """Normalized action types across simulation platforms."""
    CREATE_POST = "CREATE_POST"
    REPLY = "REPLY"
    LIKE = "LIKE"
    REPOST = "REPOST"
    SHARE = "SHARE"
    FOLLOW = "FOLLOW"
    DISAGREE = "DISAGREE"
    SUPPORT = "SUPPORT"
    ADOPT = "ADOPT"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_str(cls, value: Optional[str]) -> ActionType:
        if not value:
            return cls.UNKNOWN
        clean = value.strip().upper().replace(" ", "_").replace("-", "_")
        if clean in ("LIKE_POST", "UPVOTE", "FAVORITE"):
            return cls.LIKE
        if clean in ("RETWEET", "QUOTE_TWEET", "CROSSPOST"):
            return cls.REPOST
        if clean in ("COMMENT", "REPLY_POST", "REPLY_COMMENT"):
            return cls.REPLY
        if clean in ("POST", "CREATE_TWEET", "SUBMIT_POST"):
            return cls.CREATE_POST
        try:
            return cls(clean)
        except ValueError:
            return cls.UNKNOWN


@dataclass
class SimulationEvent:
    """Canonical simulation event representing a single action or utterance."""
    event_id: str
    simulation_id: str = "sim_default"
    round_id: Optional[int] = None
    timestamp: Optional[str] = None

    agent_id: str = "0"
    agent_name: Optional[str] = None
    agent_role: Optional[str] = None

    action_type: str = ActionType.UNKNOWN.value

    target_agent_id: Optional[str] = None
    target_post_id: Optional[str] = None

    content: Optional[str] = None

    sentiment: Optional[float] = None  # Polarity in [-1.0, 1.0]
    stance: Optional[float] = None     # Policy alignment in [-1.0, 1.0]

    topic: Optional[str] = None
    community_id: Optional[str] = None

    parent_event_id: Optional[str] = None

    platform: Optional[str] = None     # "twitter", "reddit", etc.

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to a JSON-compatible dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize event to a single-line JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SimulationEvent:
        """Construct SimulationEvent from a dictionary."""
        return cls(
            event_id=str(data.get("event_id", "")),
            simulation_id=str(data.get("simulation_id", "")),
            round_id=data.get("round_id") if data.get("round_id") is not None else None,
            timestamp=data.get("timestamp"),
            agent_id=str(data.get("agent_id", "")),
            agent_name=data.get("agent_name"),
            agent_role=data.get("agent_role"),
            action_type=str(data.get("action_type", ActionType.UNKNOWN.value)),
            target_agent_id=str(data["target_agent_id"]) if data.get("target_agent_id") is not None else None,
            target_post_id=str(data["target_post_id"]) if data.get("target_post_id") is not None else None,
            content=data.get("content"),
            sentiment=float(data["sentiment"]) if data.get("sentiment") is not None else None,
            stance=float(data["stance"]) if data.get("stance") is not None else None,
            topic=data.get("topic"),
            community_id=data.get("community_id"),
            parent_event_id=str(data["parent_event_id"]) if data.get("parent_event_id") is not None else None,
            platform=data.get("platform"),
            metadata=dict(data.get("metadata", {})),
        )

    @classmethod
    def from_json(cls, json_str: str) -> SimulationEvent:
        """Construct SimulationEvent from a JSON string."""
        return cls.from_dict(json.loads(json_str))
