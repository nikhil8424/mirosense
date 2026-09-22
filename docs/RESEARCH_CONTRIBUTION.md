# MiroSense — Research Contribution & Architecture Separation

This document explicitly defines the research contribution of **MiroSense**, articulating the boundary between foundational upstream open-source infrastructure and the novel computational research layer developed for this project.

---

## 1. Foundational Upstream Infrastructure vs. MiroSense Research Contribution

```
┌────────────────────────────────────────────────────────────────────────┐
│                   UPSTREAM / SUBSTRATE INFRASTRUCTURE                  │
│  - MiroFish Base: Document ingestion, graph parsing, report templates  │
│  - OASIS / CAMEL: Multi-agent social environment execution substrate  │
│  - NetworkX / Ollama: Graph processing and local LLM runtime          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                              Raw Actions
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│                     MIROSENSE RESEARCH CONTRIBUTION                    │
│                                                                        │
│  1. Canonical Event Ledger (Deterministic Schema & Event Adapter)      │
│  2. Interaction Graph Construction & Topological Metrics Engine        │
│  3. Deterministic Community Detection & Faction Analysis (Louvain)     │
│  4. Continuous Opinion Dynamics & Acceptance Cohesion Model            │
│  5. Temporal Stance, Conflict & Diffusion Trajectory Analysis          │
│  6. Decomposed 3-Part Polarization Model (P_total)                     │
│  7. Contestation & Cross-Community Conflict Analysis                   │
│  8. Simulated Network Influence (PageRank, Centrality & Gini Index)   │
│  9. Empirical Information Cascade Propagation Trees                    │
│ 10. Multi-Scenario Decision Evaluation & Effect Size (Cohen's d)       │
│ 11. Statistical Uncertainty Quantification (Student-t 95% CI)          │
│ 12. Controlled Sensitivity Sweeps & Subsystem Ablation Engine          │
│ 13. End-to-End Metric-to-Evidence Provenance & Audit Trail Trace       │
│ 14. SHA-256 Reproducibility Manifest & Artifact Standard               │
│ 15. Research CLI & Live Empirical Dashboard Pages                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Summary of Novel Contributions

### 1. Canonical Simulation Event Ledger (`app/mirosense/schemas/`, `app/mirosense/adapters/`)
- **Problem Solved:** OASIS outputs platform-specific, unstructured `actions.jsonl` files coupled with simulation lifecycle artifacts (`simulation_start`, `round_start`).
- **Research Contribution:** A typed, immutable `SimulationEvent` dataclass with deterministic ID hashing, explicit stance extraction, target agent linking, and platform normalization, decoupling downstream computational analytics from simulation runtime internals.

### 2. Topological Interaction Graph & Network Centrality (`app/mirosense/analytics/interaction_graph.py`)
- **Problem Solved:** Legacy systems treated social posts as isolated text blobs.
- **Research Contribution:** Directed multi-graph construction modeling agent-to-agent interactions (replies, mentions, likes, disagreements, endorsements) and deterministic mathematical computation of density, reciprocity, in/out-degree, betweenness, PageRank, and clustering coefficients.

### 3. Louvain Sub-Community Modularity & Factional Alignment (`app/mirosense/analytics/community_detection.py`)
- **Problem Solved:** Group dynamics were previously unmodeled or relied on arbitrary LLM groupings.
- **Research Contribution:** Deterministic Louvain modularity optimization ($Q$) over interaction networks to uncover emergent stakeholder factions, internal vs. external interaction ratios, and community-level stance distributions.

### 4. Tri-Part Polarization Decomposition (`app/mirosense/analytics/polarization.py`)
- **Problem Solved:** Legacy polarization metrics were often conflated with raw negative sentiment.
- **Research Contribution:** A mathematically transparent 3-part decomposition:
  $$P_{\text{total}} = w_{\text{opinion}} P_{\text{opinion}} + w_{\text{network}} P_{\text{network}} + w_{\text{interaction}} P_{\text{interaction}}$$
  measuring continuous opinion dispersion ($P_o$), network topological clustering ($P_n$), and cross-community contestation ($P_i$).

### 5. Multi-Scenario Evaluation with Statistical Effect Size (`app/mirosense/evaluation/`)
- **Problem Solved:** Previous decision comparisons made ungrounded claims of "optimal" or "winning" policies without rigorous statistical criteria.
- **Research Contribution:** Objective scenario behavioral profiling (`acceptance`, `polarization`, `conflict_rate`, `modularity`, `stability`) paired with Cohen's $d$ and Hedges' $g$ effect size calculations.

### 6. Scientific Uncertainty, Sensitivity & Ablation Frameworks (`app/mirosense/validation/`)
- **Problem Solved:** Arbitrary $\pm 0.1$ heuristic confidence intervals were used previously.
- **Research Contribution:** Exact Student-$t$ distribution confidence intervals over repeated stochastic Monte Carlo runs, one-at-a-time (OAT) parameter sensitivity sweeps, component ablations (No Graph, No Community, No Memory, No Temporal), and Random Interaction baselines.

### 7. Verifiable Metric-to-Evidence Provenance (`app/mirosense/provenance/`)
- **Problem Solved:** Black-box AI summary metrics lacked traceability.
- **Research Contribution:** An audit trail connecting high-level analytical indicators back to specific simulation event IDs, agent IDs, rounds, and ingested document sources.
