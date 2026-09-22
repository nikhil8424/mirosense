# MiroSense — Implementation Status & Scientific Audit

This document records the exact implementation status of all architectural and analytical components within MiroSense following the comprehensive scientific audit and upgrade.

---

## 1. System Components & Status Matrix

| Component | Layer | File Location | Status | Notes |
| :--- | :--- | :--- | :---: | :--- |
| **Document Ingestion** | Ingestion | `app/services/document_parser.py` | **Implemented** | Upstream MiroFish substrate; parses PDF/DOCX/TXT/MD. |
| **Knowledge Graph** | Knowledge | `app/services/graph_service.py` | **Implemented** | Neo4j/NetworkX graph extraction for entity grounding. |
| **Stakeholder Profiles** | Simulation | `app/services/profile_generator.py` | **Implemented** | Persona & stance generation from knowledge graph entities. |
| **OASIS Simulation** | Simulation | `app/services/simulation_runner.py` | **Implemented** | Multi-agent social environment runner (Twitter/Reddit). |
| **Action Log Output** | Simulation | `actions.jsonl` | **Implemented** | Raw heterogeneous action logs recorded per round. |
| **Canonical Event Ledger** | Data / Event | `app/mirosense/schemas/events.py`, `app/mirosense/adapters/oasis_adapter.py` | **Implemented** | Strictly verified normalization, deterministic IDs, parent linking. |
| **Interaction Graph** | Research Analytics | `app/mirosense/analytics/interaction_graph.py` | **Implemented** | MultiDiGraph, PageRank, betweenness, degree, reciprocity. |
| **Community Detection** | Research Analytics | `app/mirosense/analytics/community_detection.py` | **Implemented** | Deterministic Louvain modularity $Q$, faction stance analysis. |
| **Opinion Dynamics** | Research Analytics | `app/mirosense/analytics/opinion_dynamics.py` | **Implemented** | Explicit stance in $[-1, 1]$, acceptance, cohesion, distribution. |
| **Temporal Analysis** | Research Analytics | `app/mirosense/analytics/temporal_analysis.py` | **Implemented** | Round-by-round trajectory series across all analytical dimensions. |
| **Polarization Decomposition** | Research Analytics | `app/mirosense/analytics/polarization.py` | **Implemented** | $P_{\text{total}} = w_o P_o + w_n P_n + w_i P_i$ with documented weights. |
| **Conflict Analysis** | Research Analytics | `app/mirosense/analytics/conflict_analysis.py` | **Implemented** | Contestations, dispute rates, cross-community conflict ratios. |
| **Influence Analysis** | Research Analytics | `app/mirosense/analytics/influence_analysis.py` | **Implemented** | Simulated network influence (PageRank, Gini inequality). |
| **Information Diffusion** | Research Analytics | `app/mirosense/analytics/information_diffusion.py` | **Implemented** | Cascade trees, depth, duration, cross-community spread. |
| **Scenario Engine** | Evaluation | `app/mirosense/evaluation/scenario_engine.py` | **Implemented** | Controlled scenario definitions with parameter isolation. |
| **Scenario Comparison** | Evaluation | `app/mirosense/evaluation/scenario_comparison.py` | **Implemented** | Effect size (Cohen's $d$, Hedges' $g$), behavioral profiles. |
| **Monte Carlo Engine** | Validation | `app/mirosense/validation/monte_carlo.py` | **Implemented** | Seeded stochastic repetitions with empirical aggregation. |
| **Uncertainty Quantification** | Validation | `app/mirosense/validation/uncertainty.py` | **Implemented** | Student-$t$ distribution & empirical bootstrap confidence intervals. |
| **Sensitivity Analysis** | Validation | `app/mirosense/validation/sensitivity.py` | **Implemented** | One-at-a-time (OAT) parameter sweeps with response metrics. |
| **Ablation Framework** | Validation | `app/mirosense/validation/ablation.py` | **Implemented** | Component isolation (Graph, Community, Memory, Temporal). |
| **Baseline Benchmarking** | Validation | `app/mirosense/validation/baselines.py` | **Implemented** | Benchmarks against Random Baseline, Direct LLM, Raw OASIS. |
| **Metric Provenance** | Provenance | `app/mirosense/provenance/metric_provenance.py` | **Implemented** | End-to-end evidence $\to$ entity $\to$ agent $\to$ event $\to$ metric trace. |
| **Experiment Manifest** | Provenance | `app/mirosense/schemas/manifest.py` | **Implemented** | SHA-256 config hashing, environment, and seed tracking. |
| **Research CLI** | Interface | `app/cli.py` | **Implemented** | Subcommands for analytics, comparison, validation, report. |
| **Research Dashboard** | Interface | `app/streamlit_app.py` | **Implemented** | Real artifact-driven UI pages with interactive charts. |
| **Research Reporting** | Reporting | `app/mirosense/reporting/` | **Implemented** | Markdown and JSON comprehensive research reports. |

---

## 2. Deprecated Legacy Heuristics

The following legacy components in `app/research/` have been audited and explicitly marked as **DEPRECATED**:

1. **Fixed-Weight "Social Viability Score":**
   - *Flaw:* Arbitrary linear sum ($0.3 \times \text{acceptance} + 0.25 \times \text{cohesion} + \dots$) asserting normative policy optimality without an empirical objective function.
   - *Status:* Deprecated. Replaced by `app.mirosense.evaluation.scenario_comparison.ScenarioProfile`.
2. **Fabricated Confidence Intervals ($\pm 0.1$):**
   - *Flaw:* Mock heuristic adding $\pm 0.1$ to point estimates instead of calculating variance over repeated stochastic runs.
   - *Status:* Deprecated. Replaced by `app.mirosense.validation.uncertainty.compute_confidence_interval` (exact Student-$t$ 95% CI).
3. **Keyword-Only Polarization:**
   - *Flaw:* Used simple keyword frequency without graph or opinion variance decomposition.
   - *Status:* Deprecated. Replaced by `app.mirosense.analytics.polarization.PolarizationAnalyzer`.
4. **Action-Count Influence:**
   - *Flaw:* Assumed raw post count equals social influence.
   - *Status:* Deprecated. Replaced by `app.mirosense.analytics.influence_analysis.InfluenceAnalyzer` (PageRank, betweenness, in-degree).
