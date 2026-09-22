"""Metric Provenance & Evidence Traceability Analytics.

Provides end-to-end provenance tracing connecting high-level analytical metrics
back to supporting simulation event IDs, agent IDs, rounds, and original source documents.
Trace: Evidence -> Graph Entity -> Stakeholder -> Event -> Metric
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
import os
from typing import Any, Dict, List, Optional

from ..schemas.events import SimulationEvent
from ..analytics.community_detection import CommunityPartition
from ..analytics.opinion_dynamics import OpinionMetrics
from ..analytics.polarization import PolarizationDecomposition
from ..analytics.conflict_analysis import ConflictMetrics


@dataclass
class MetricProvenanceRecord:
    """Detailed audit trace for a specific analytical metric."""
    metric_id: str
    metric_name: str
    metric_value: Any
    simulation_id: str
    run_id: str
    scenario_id: Optional[str] = None
    round_ids: List[int] = field(default_factory=list)
    constituent_event_ids: List[str] = field(default_factory=list)
    constituent_agent_ids: List[str] = field(default_factory=list)
    community_ids: List[str] = field(default_factory=list)
    source_evidence_files: List[str] = field(default_factory=list)
    source_entities: List[str] = field(default_factory=list)
    method_or_formula: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MetricProvenanceTracker:
    """Builds and serializes verifiable provenance indexes for analytical metrics."""

    def build_provenance_index(
        self,
        simulation_id: str,
        run_id: str,
        events: List[SimulationEvent],
        opinion_metrics: OpinionMetrics,
        polarization: PolarizationDecomposition,
        conflict_metrics: ConflictMetrics,
        partition: Optional[CommunityPartition] = None,
        scenario_id: Optional[str] = None,
        source_files: Optional[List[str]] = None,
        source_entities: Optional[List[str]] = None,
    ) -> Dict[str, MetricProvenanceRecord]:
        """Construct the complete provenance index for all computed research metrics."""
        records: Dict[str, MetricProvenanceRecord] = {}

        all_event_ids = [evt.event_id for evt in events if evt.event_id]
        all_agent_ids = list({str(evt.agent_id) for evt in events if evt.agent_id})
        all_rounds = sorted(list({evt.round_id for evt in events if evt.round_id is not None}))
        comm_ids = [c.community_id for c in partition.communities] if partition else []
        src_files = source_files or []
        src_ents = source_entities or []

        # 1. Acceptance Provenance
        pos_events = [evt.event_id for evt in events if evt.stance is not None and evt.stance > 0.1]
        records["acceptance"] = MetricProvenanceRecord(
            metric_id=f"prov_{simulation_id}_acceptance",
            metric_name="acceptance",
            metric_value=opinion_metrics.acceptance,
            simulation_id=simulation_id,
            run_id=run_id,
            scenario_id=scenario_id,
            round_ids=all_rounds,
            constituent_event_ids=pos_events[:20],
            constituent_agent_ids=all_agent_ids[:15],
            community_ids=comm_ids,
            source_evidence_files=src_files,
            source_entities=src_ents,
            method_or_formula="0.6 * normalized_mean_stance + 0.4 * support_ratio",
        )

        # 2. Polarization Provenance
        records["polarization"] = MetricProvenanceRecord(
            metric_id=f"prov_{simulation_id}_polarization",
            metric_name="polarization",
            metric_value=polarization.p_total,
            simulation_id=simulation_id,
            run_id=run_id,
            scenario_id=scenario_id,
            round_ids=all_rounds,
            constituent_event_ids=all_event_ids[:20],
            constituent_agent_ids=all_agent_ids[:15],
            community_ids=comm_ids,
            source_evidence_files=src_files,
            source_entities=src_ents,
            method_or_formula="w_opinion * P_opinion + w_network * P_network + w_interaction * P_interaction",
        )

        # 3. Conflict Rate Provenance
        conflict_events = [
            evt.event_id for evt in events
            if evt.action_type == "DISAGREE" or (evt.stance is not None and evt.stance < -0.3)
        ]
        records["conflict_rate"] = MetricProvenanceRecord(
            metric_id=f"prov_{simulation_id}_conflict_rate",
            metric_name="conflict_rate",
            metric_value=conflict_metrics.conflict_rate,
            simulation_id=simulation_id,
            run_id=run_id,
            scenario_id=scenario_id,
            round_ids=all_rounds,
            constituent_event_ids=conflict_events[:20],
            constituent_agent_ids=list(conflict_metrics.conflict_by_agent.keys())[:10],
            community_ids=comm_ids,
            source_evidence_files=src_files,
            source_entities=src_ents,
            method_or_formula="total_conflict_actions / total_simulation_actions",
        )

        # 4. Modularity Provenance
        records["modularity"] = MetricProvenanceRecord(
            metric_id=f"prov_{simulation_id}_modularity",
            metric_name="modularity",
            metric_value=partition.modularity if partition else 0.0,
            simulation_id=simulation_id,
            run_id=run_id,
            scenario_id=scenario_id,
            round_ids=all_rounds,
            constituent_event_ids=all_event_ids[:20],
            constituent_agent_ids=all_agent_ids[:15],
            community_ids=comm_ids,
            source_evidence_files=src_files,
            source_entities=src_ents,
            method_or_formula="Newman-Girvan Modularity Q over interaction multi-graph",
        )

        return records

    def export_provenance_json(
        self,
        provenance_index: Dict[str, MetricProvenanceRecord],
        output_path: str,
    ) -> str:
        """Export provenance records to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        payload = {k: v.to_dict() for k, v in provenance_index.items()}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return output_path
