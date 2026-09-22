"""Decomposed Polarization Analytics.

Implements a transparent, modular 3-part polarization model:
    P_total = w_opinion * P_opinion + w_network * P_network + w_interaction * P_interaction

Where:
- P_opinion: Statistical dispersion / bimodality of agent policy stances
- P_network: Topological modularity Q of detected community clusters
- P_interaction: Ratio of intra-group vs cross-group interaction contestation
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
import json
import math
import os
import statistics
from typing import Any, Dict, List, Optional

from ..schemas.events import SimulationEvent
from .community_detection import CommunityPartition


@dataclass
class PolarizationDecomposition:
    """Decomposed polarization components and composite score."""
    p_total: float = 0.0
    p_opinion: float = 0.0
    p_network: float = 0.0
    p_interaction: float = 0.0

    weights: Dict[str, float] = field(default_factory=lambda: {
        "w_opinion": 0.40,
        "w_network": 0.30,
        "w_interaction": 0.30,
    })

    opinion_std: float = 0.0
    modularity: float = 0.0
    cross_group_ratio: float = 0.0
    interpretation: str = "Low Polarization"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "p_total": round(float(self.p_total), 4),
            "p_opinion": round(float(self.p_opinion), 4),
            "p_network": round(float(self.p_network), 4),
            "p_interaction": round(float(self.p_interaction), 4),
            "weights": self.weights,
            "opinion_std": round(float(self.opinion_std), 4),
            "modularity": round(float(self.modularity), 4),
            "cross_group_ratio": round(float(self.cross_group_ratio), 4),
            "interpretation": self.interpretation,
        }


class PolarizationAnalyzer:
    """Calculates multi-dimensional polarization across opinion, network, and interaction axes."""

    def __init__(
        self,
        w_opinion: float = 0.40,
        w_network: float = 0.30,
        w_interaction: float = 0.30,
    ):
        total_w = w_opinion + w_network + w_interaction
        if total_w > 0:
            self.w_opinion = w_opinion / total_w
            self.w_network = w_network / total_w
            self.w_interaction = w_interaction / total_w
        else:
            self.w_opinion, self.w_network, self.w_interaction = 0.4, 0.3, 0.3

    def analyze(
        self,
        events: List[SimulationEvent],
        partition: Optional[CommunityPartition] = None,
    ) -> PolarizationDecomposition:
        """Compute decomposed polarization index."""
        # 1. Opinion Polarization (P_opinion)
        stances = [evt.stance for evt in events if evt.stance is not None]
        if len(stances) > 1:
            std_s = statistics.stdev(stances)
            # Normalize std (max theoretical std on [-1, 1] is 1.0 for equal -1 and +1)
            p_opinion = min(1.0, std_s)
        else:
            std_s = 0.0
            p_opinion = 0.0

        # 2. Network Polarization (P_network)
        if partition is not None:
            # Modularity is typically in [-0.5, 1.0]. Normalize non-negative modularity to [0, 1]
            modularity_val = max(0.0, float(partition.modularity))
            p_network = min(1.0, modularity_val)
            cross_ratio = partition.cross_community_interaction_ratio
        else:
            modularity_val = 0.0
            p_network = 0.0
            cross_ratio = 1.0

        # 3. Interaction Polarization (P_interaction)
        # When cross-group interactions are low, interaction polarization is high (echo chamber effect)
        p_interaction = max(0.0, min(1.0, 1.0 - cross_ratio))

        # Composite total polarization
        p_total = (
            self.w_opinion * p_opinion
            + self.w_network * p_network
            + self.w_interaction * p_interaction
        )
        p_total = min(max(p_total, 0.0), 1.0)

        # Interpretive category
        if p_total > 0.70:
            interp = "High Polarization (Severely Divided Communities & Opposing Stances)"
        elif p_total > 0.40:
            interp = "Moderate Polarization (Noticeable Factional Divergence)"
        else:
            interp = "Low Polarization (Cohesive Population Alignment)"

        return PolarizationDecomposition(
            p_total=p_total,
            p_opinion=p_opinion,
            p_network=p_network,
            p_interaction=p_interaction,
            weights={
                "w_opinion": round(self.w_opinion, 3),
                "w_network": round(self.w_network, 3),
                "w_interaction": round(self.w_interaction, 3),
            },
            opinion_std=std_s,
            modularity=modularity_val,
            cross_group_ratio=cross_ratio,
            interpretation=interp,
        )

    def export_polarization_json(self, decomp: PolarizationDecomposition, output_path: str) -> str:
        """Export polarization decomposition to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(decomp.to_dict(), f, ensure_ascii=False, indent=2)
        return output_path
