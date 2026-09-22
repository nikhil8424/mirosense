"""Research Report Generator.

Compiles comprehensive, academically rigorous research reports from
persisted MiroSense analytics, evaluation, and provenance artifacts.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class ResearchReportGenerator:
    """Generates structured Markdown and JSON research reports."""

    def generate_report(
        self,
        run_id: str,
        manifest: Dict[str, Any],
        opinion_metrics: Optional[Dict[str, Any]] = None,
        polarization: Optional[Dict[str, Any]] = None,
        communities: Optional[Dict[str, Any]] = None,
        network_metrics: Optional[Dict[str, Any]] = None,
        conflict_metrics: Optional[Dict[str, Any]] = None,
        influence_metrics: Optional[Dict[str, Any]] = None,
        diffusion_metrics: Optional[Dict[str, Any]] = None,
        temporal_metrics: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a complete Markdown research report from analytics artifacts."""
        lines: List[str] = []

        lines.append(f"# MiroSense Research Report: {manifest.get('project_name', 'Simulation Study')}")
        lines.append("")
        lines.append(f"**Run ID:** `{run_id}`  ")
        lines.append(f"**Created At:** {manifest.get('created_at', 'N/A')}  ")
        lines.append(f"**Requirement / Policy Query:** {manifest.get('requirement', 'N/A')}  ")
        lines.append("")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary")
        acc = opinion_metrics.get("acceptance", "N/A") if opinion_metrics else "N/A"
        pol = polarization.get("p_total", "N/A") if polarization else "N/A"
        mod = communities.get("modularity", "N/A") if communities else "N/A"
        conf = conflict_metrics.get("conflict_rate", "N/A") if conflict_metrics else "N/A"
        
        lines.append(f"- **Simulated Policy Acceptance:** `{acc}`")
        lines.append(f"- **Composite Polarization ($P_{{total}}$):** `{pol}`")
        lines.append(f"- **Network Modularity ($Q$):** `{mod}`")
        lines.append(f"- **Contestation / Conflict Rate:** `{conf}`")
        lines.append("")

        # 2. Experimental Configuration & Grounding
        lines.append("## 2. Experimental Configuration & Evidence Grounding")
        lines.append(f"- **Source Evidence Files:** {len(manifest.get('source_files', []))} files ingested")
        for src in manifest.get("source_files", []):
            lines.append(f"  - `{os.path.basename(src)}`")
        lines.append(f"- **Total Simulation Rounds:** {manifest.get('rounds', 'N/A')}")
        lines.append(f"- **Simulated Agents:** {opinion_metrics.get('unique_agents', 'N/A') if opinion_metrics else 'N/A'}")
        lines.append("")

        # 3. Opinion Dynamics & Stance Dispersion
        lines.append("## 3. Opinion & Stance Dynamics")
        if opinion_metrics:
            lines.append(f"- **Mean Stance:** `{opinion_metrics.get('mean_stance', 0.0):+.4f}` (Range $[-1.0, 1.0]$)")
            lines.append(f"- **Stance Standard Deviation:** `{opinion_metrics.get('stance_std', 0.0):.4f}`")
            lines.append(f"- **Support Ratio (> 0.1):** `{opinion_metrics.get('support_ratio', 0.0):.2%}`")
            lines.append(f"- **Opposition Ratio (< -0.1):** `{opinion_metrics.get('opposition_ratio', 0.0):.2%}`")
            lines.append(f"- **Neutral / Undecided Ratio:** `{opinion_metrics.get('neutral_ratio', 0.0):.2%}`")
        else:
            lines.append("*Opinion dynamics data not available.*")
        lines.append("")

        # 4. Community Structure & Modularity
        lines.append("## 4. Community Structure & Modularity")
        if communities:
            lines.append(f"- **Detected Sub-Communities:** `{communities.get('community_count', 0)}`")
            lines.append(f"- **Newman-Girvan Modularity ($Q$):** `{communities.get('modularity', 0.0):.4f}`")
            lines.append(f"- **Cross-Community Interaction Ratio:** `{communities.get('cross_community_interaction_ratio', 0.0):.2%}`")
            lines.append("")
            lines.append("| Community ID | Size | Mean Stance | Internal Edges | External Edges |")
            lines.append("| :--- | :---: | :---: | :---: | :---: |")
            for comm in communities.get("communities", []):
                lines.append(
                    f"| `{comm.get('community_id')}` | {comm.get('size')} | "
                    f"`{comm.get('mean_stance', 0.0):+.2f}` | {comm.get('internal_edges')} | {comm.get('external_edges')} |"
                )
        else:
            lines.append("*Community detection data not available.*")
        lines.append("")

        # 5. Polarization Decomposition
        lines.append("## 5. Polarization Decomposition")
        if polarization:
            lines.append("Polarization is decomposed into three orthogonal structural and behavioral components:")
            lines.append("$$P_{\\text{total}} = w_{\\text{opinion}} P_{\\text{opinion}} + w_{\\text{network}} P_{\\text{network}} + w_{\\text{interaction}} P_{\\text{interaction}}$$")
            lines.append("")
            lines.append(f"- **$P_{{\\text{{total}}}}$ Composite:** `{polarization.get('p_total', 0.0):.4f}` ({polarization.get('interpretation', 'N/A')})")
            lines.append(f"- **$P_{{\\text{{opinion}}}}$ (Stance Dispersion):** `{polarization.get('p_opinion', 0.0):.4f}`")
            lines.append(f"- **$P_{{\\text{{network}}}}$ (Graph Modularity):** `{polarization.get('p_network', 0.0):.4f}`")
            lines.append(f"- **$P_{{\\text{{interaction}}}}$ (Cross-Group Contestation):** `{polarization.get('p_interaction', 0.0):.4f}`")
        lines.append("")

        # 6. Simulated Network Influence
        lines.append("## 6. Simulated Network Influence (Top Agents)")
        if influence_metrics:
            lines.append(f"- **Gini Inequality Index:** `{influence_metrics.get('gini_index', 0.0):.4f}`")
            lines.append("")
            lines.append("| Agent ID | Role / Name | PageRank | In-Degree | Betweenness | Influence Rank |")
            lines.append("| :--- | :--- | :---: | :---: | :---: | :---: |")
            for agent in influence_metrics.get("ranked_agents", [])[:8]:
                lines.append(
                    f"| `{agent.get('agent_id')}` | {agent.get('agent_name', 'Agent ' + str(agent.get('agent_id')))} | "
                    f"`{agent.get('pagerank', 0.0):.4f}` | {agent.get('in_degree', 0)} | `{agent.get('betweenness', 0.0):.4f}` | #{agent.get('rank', 0)} |"
                )
        lines.append("")

        # 7. Scientific Limitations
        lines.append("## 7. Research Methodology & Scientific Limitations")
        lines.append("- **Simulation Environment:** Agent interactions reflect OASIS simulated discourse conditioned on ingested documentation.")
        lines.append("- **No Normative Optimality Claim:** Behavioral comparisons reflect simulated social responses, not absolute real-world truth.")
        lines.append("- **Reproducibility:** All metrics are derived deterministically from canonical simulation events.")
        lines.append("")

        return "\n".join(lines)
