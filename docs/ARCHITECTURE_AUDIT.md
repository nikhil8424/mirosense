# MiroSense — Post-Implementation Research Architecture Audit

**Date:** September 21, 2026  
**Auditor:** Automated Senior Research Architecture Review  
**Repository:** `mirofish-cli` (`MiroFish` / `MiroSense`)  
**Scope:** Complete Codebase, Simulation Runtime, Analytics Pipeline, Validation Suite, CLI, Streamlit UI, Documentation

---

## Executive Summary

This document presents a comprehensive, evidence-based audit of the `MiroFish` / `MiroSense` repository following the initial research architecture upgrade.

The core finding of this audit is:
* **The upstream MiroFish + OASIS simulation engine is fully operational:** Document ingestion, knowledge graph generation (Kùzu/JSON), agent profile preparation, OASIS subprocess execution (Twitter/Reddit/Parallel), and single-pass markdown report generation with visual SVGs are working and verified.
* **The research layer (`app/research/`) is disconnected and scientifically incomplete:** Seven standalone module files exist in `app/research/`, but they are **not invoked by the main CLI execution pipeline** (`app/cli.py`) nor wired into the **Streamlit UI** (`app/streamlit_app.py`, where research pages currently render static placeholder `st.info` notices).
* **Key scientific components requested for symposium readiness are absent:** There is no canonical `SimulationEvent` ledger, no post-simulation interaction graph with network centrality, no community detection (Leiden/Louvain), no multi-component polarization model, no temporal trajectory tracking, no Monte Carlo multi-seed engine, no sensitivity analysis, no ablation framework, no baseline comparisons, no metric provenance tracing, and 0 tests covering the research modules.

---

## 1. Repository Snapshot & Architectural Baseline

### 1.1 Directory Tree
```text
mirofish-cli/
├── app/
│   ├── cli.py                  # CLI entrypoint (commands: run, runs list/status/export, doctor)
│   ├── cli_display.py          # Rich terminal display for pipeline
│   ├── config.py               # Env validation (LLM_PROVIDER: ollama, claude-cli, codex-cli)
│   ├── run_artifacts.py        # RunStore: immutable run directories (uploads/runs/<run_id>/)
│   ├── visual_snapshots.py     # Deterministic SVG chart generation (swarm, cluster, timeline)
│   ├── streamlit_app.py        # Streamlit web interface (13 pages, research pages are placeholders)
│   ├── core/                   # WorkbenchSession, TaskManager, ResourceLoader, SessionManager
│   ├── tools/                  # Pipeline tools: generate_ontology, build_graph, prepare_sim, run_sim, generate_report
│   ├── services/               # Core services: simulation_runner (1476 lines), graph_builder, ontology_generator, etc.
│   ├── resources/              # Persistence adapters: projects, documents, graph, simulations, reports
│   ├── models/                 # Data models: project.py, task.py
│   ├── utils/                  # llm_client.py, oasis_llm.py, file_parser.py, logger.py
│   └── research/               # [DISCONNECTED] 7 research modules (community context, twins, scenario, impact, etc.)
├── scripts/                    # OASIS runner scripts: run_parallel_simulation.py, run_twitter_simulation.py, etc.
├── tests/                      # 19 tests across test_cli_artifacts_and_visuals.py & test_ollama_llm_client.py
├── uploads/                    # Runtime data: projects, runs, simulations, reports
├── data/                       # Kùzu / JSON graph database files
├── docs/                       # PRDs, explanations, architecture docs
├── pyproject.toml              # Dependencies (camel-oasis==0.2.5, camel-ai==0.2.78, PyMuPDF, rich, streamlit)
└── README.md                   # 775 lines of research documentation and mathematical formulations
```

### 1.2 Master Implementation Matrix

| Research Component | Requested Previously | Exists? | Actually Connected? | Tested? | Working? | Research-Ready? | Evidence & Call Chain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Evidence Ingestion** | Yes | Yes | **Yes** | Yes | **Yes** | Yes | `FileParser` in `app/utils/file_parser.py` called by `session.generate_ontology` |
| **Knowledge Graph** | Yes | Yes | **Yes** | Yes | **Yes** | Yes | `GraphBuilderService`, `GraphDatabase` in `app/services/` called by `session.start_graph_build` |
| **Agent Profile Gen** | Yes | Yes | **Yes** | Yes | **Yes** | Partial | `OasisProfileGenerator` in `app/services/` called by `session.start_simulation_preparation` |
| **Digital Twin Wrapper** | Yes | Yes | **No (DISCONNECTED)** | No | Partial | No | `StakeholderDigitalTwin` in `app/research/stakeholder_digital_twin.py` (not called in CLI/UI) |
| **OASIS Simulation** | Yes | Yes | **Yes** | Yes | **Yes** | Yes | `SimulationRunner` in `app/services/simulation_runner.py` spawns `scripts/run_parallel_simulation.py` |
| **Canonical Event Ledger** | Yes | **No (MISSING)** | No | No | No | No | No `SimulationEvent` dataclass; uses untyped `AgentAction` in `simulation_runner.py` |
| **Interaction Graph** | Yes | **No (MISSING)** | No | No | No | No | No post-simulation interaction graph constructed; no centrality/PageRank algorithms |
| **Community Detection** | Yes | **No (MISSING)** | No | No | No | No | No Leiden, Louvain, or modularity algorithms exist in repo; no `networkx` dependency |
| **Opinion/Stance Model** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `EmergentBehaviourAnalyzer` in `app/research/` uses keyword matching, not called in pipeline |
| **Polarization Model** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | Simplistic formula `1 - min(pos,neg)/(pos+neg)` in `emergent_behaviour_analyzer.py`; not decomposed |
| **Temporal Dynamics** | Yes | **No (MISSING)** | No | No | No | No | No round-by-round trajectory metric computation or time-series storage |
| **Diffusion Analysis** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `information_spread_rate = shares / actions` in `emergent_behaviour_analyzer.py`; no cascade trees |
| **Conflict Analysis** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | Keyword search in `emergent_behaviour_analyzer.py`; no cross-community conflict |
| **Influence Analysis** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `influence = actions / total_actions` in `emergent_behaviour_analyzer.py`; no network centrality |
| **Scenario Engine** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `ScenarioDesigner` in `app/research/scenario_designer.py` (in-memory dict, not wired to runner) |
| **Scenario Comparison** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `DecisionComparisonEngine` in `app/research/` (sorts hardcoded score, not in pipeline) |
| **Viability Score Refactor** | Yes | Partial | **No (DISCONNECTED)** | No | Weak | No | `SocialImpactModel` in `app/research/` uses hardcoded fixed weights; labeled "Social Viability Score" |
| **Monte Carlo Engine** | Yes | **No (MISSING)** | No | No | No | No | No multi-seed runner, no aggregation matrix, no statistical distributions |
| **Uncertainty Bands** | Yes | Partial | **No (DISCONNECTED)** | No | Broken | No | `_estimate_confidence_intervals` in `decision_intelligence_engine.py` hardcodes `[score - 0.1, score + 0.1]` |
| **Sensitivity Analysis** | Yes | **No (MISSING)** | No | No | No | No | No parameter sweep engine or sensitivity plot generator |
| **Ablation Framework** | Yes | **No (MISSING)** | No | No | No | No | No feature-flagged ablation experiment runner |
| **Baseline Framework** | Yes | **No (MISSING)** | No | No | No | No | No baseline comparator (Direct LLM, standard OASIS vs MiroSense) |
| **Metric Provenance** | Yes | **No (MISSING)** | No | No | No | No | No trace linkage connecting Metric $\to$ Event IDs $\to$ Agents $\to$ Evidence |
| **Reproducibility Manifest** | Yes | Partial | **Yes** | Yes | Partial | Partial | `RunStore` creates `manifest.json` for single runs, but no multi-run/experiment manifest |
| **Research Dashboard UI** | Yes | Partial | **No (PLACEHOLDER)** | No | No | No | `app/streamlit_app.py` renders static `st.info` placeholder text for all research tabs |
| **Research CLI** | Yes | **No (MISSING)** | No | No | No | No | `app/cli.py` only supports `run`, `runs`, `doctor`; no `analyze`, `compare`, `experiment`, etc. |

---

## 2. Detailed Findings by Architectural Layer

### 2.1 Simulation Core (MiroFish + OASIS) — STATUS: VERIFIED & WORKING
* **Subprocess Architecture:** `SimulationRunner` (`app/services/simulation_runner.py`) correctly manages isolated Python subprocesses running `scripts/run_parallel_simulation.py`, `scripts/run_twitter_simulation.py`, or `scripts/run_reddit_simulation.py`.
* **IPC & Action Logging:** `PlatformActionLogger` and `SimulationLogManager` in `scripts/action_logger.py` append json-lines to `actions.jsonl`.
* **Profile Generation:** `OasisProfileGenerator` correctly prompts LLM to generate bounded personas ($\le 150$ words) for Twitter (CSV) and Reddit (JSON).
* **LLM Bridging:** `app/utils/oasis_llm.py` and `app/utils/llm_client.py` provide a robust OpenAI API mock interface enabling CAMEL-AI agents to run against local Ollama, Claude CLI, or Codex CLI.
* **Run Artifacts:** `RunStore` (`app/run_artifacts.py`) creates immutable directory structures (`uploads/runs/<run_id>/`) with frozen source files, configs, logs, report, verdict, and SVG snapshots.

### 2.2 Canonical Event Ledger — STATUS: MISSING
* **Current State:** The simulation emits raw `AgentAction` dictionaries with fields: `round_num`, `timestamp`, `platform`, `agent_id`, `agent_name`, `action_type`, `action_args`, `result`, `success`.
* **Deficiencies:**
  1. No `SimulationEvent` canonical model exists.
  2. Missing fields: `event_id`, `simulation_id`, `round_id`, `agent_role`, `target_agent_id`, `target_post_id`, `content`, `sentiment`, `stance`, `topic`, `community_id`, `parent_event_id`, `metadata`.
  3. No event adapter exists to normalize raw OASIS actions into canonical events.
  4. Actions are saved as raw JSONL but never parsed into an enriched event stream for analytical consumers.

### 2.3 Interaction Graph & Community Detection — STATUS: MISSING
* **Current State:** Knowledge graph extraction from input text exists (`GraphBuilderService` using Kùzu/JSON), but **zero post-simulation interaction graph logic exists**.
* **Deficiencies:**
  1. No agent-agent interaction graph is constructed from replies, likes, reposts, follows, or disagreements.
  2. No centrality metrics (degree, weighted degree, in/out degree, betweenness, PageRank) are calculated.
  3. No community detection algorithm (Leiden or Louvain) is implemented.
  4. Network modularity is completely uncomputed.

### 2.4 Opinion Dynamics & Polarization Model — STATUS: SCIENTIFICALLY WEAK & DISCONNECTED
* **Current State:** Located in `app/research/emergent_behaviour_analyzer.py`, but never called in the execution pipeline.
* **Deficiencies:**
  1. **Sentiment heuristic:** Uses hardcoded keyword lists (`['support', 'agree', 'good', ...]`) and adds $\pm 0.5 \pm 0.1 \times \text{count}$.
  2. **Consensus formula:** Formulated as $C_{ons} = |\bar{S}|$ (absolute value of mean sentiment). If a population is evenly divided (-1 and +1), mean sentiment is 0, giving consensus = 0. However, if all agents are -1 (unanimous opposition), consensus = 1.0, conflating consensus with positive/negative extremism.
  3. **Polarization formula:** $P_{ol} = 1 - \frac{\min(N_{pos}, N_{neg})}{N_{pos} + N_{neg}}$. This is merely the unbalance of binary keyword counts.
  4. **No decomposition:** The requested three-part model ($P_{total} = w_{op} P_{op} + w_{net} P_{net} + w_{int} P_{int}$) does not exist.
  5. **No temporal tracking:** All calculations are lumped across the entire simulation without round-by-round trajectory data.

### 2.5 Decision Intelligence & Social Viability Score — STATUS: SCIENTIFICALLY WEAK & DISCONNECTED
* **Current State:** Located in `app/research/social_impact_model.py`, `decision_comparison_engine.py`, and `decision_intelligence_engine.py`.
* **Deficiencies:**
  1. **Fixed Weights:** Combines 7 sub-metrics with hardcoded static weights (0.20, 0.15, 0.15, 0.15, 0.10, 0.15, 0.10) labeled as an absolute "Overall Social Viability Score".
  2. **Fake Confidence Intervals:** `_estimate_confidence_intervals` in `decision_intelligence_engine.py` (lines 461-478) computes:
     ```python
     'overall_score_range': [max(0.0, result.overall_score - 0.1), min(1.0, result.overall_score + 0.1)]
     ```
     This is an arbitrary $\pm 0.1$ constant, not a statistical confidence interval.
  3. **Fake Confidence Score:** `_estimate_confidence` in `social_impact_model.py` computes:
     ```python
     confidence = (sample_size / 100.0) * ((1 + has_sentiment + has_influence) / 3)
     ```
  4. **Unused in Pipeline:** The CLI calls `_generate_verdict` (LLM-based text extraction from `report.md`) and stores `report/verdict.json`, completely ignoring `SocialImpactModel` and `DecisionIntelligenceEngine`.

### 2.6 Scientific Validation Framework — STATUS: MISSING
* **Monte Carlo Engine:** Completely absent. No multi-seed runner, no statistical aggregation across runs, no variance/standard error calculation.
* **Sensitivity Analysis:** Completely absent. No parameter sweep infrastructure (varying agent count, rounds, temperature, initial stance).
* **Ablation Studies:** Completely absent. No feature-flagged execution (e.g. `NO_GRAPH`, `NO_COMMUNITY`, `NO_MEMORY`).
* **Baselines:** Completely absent. No direct-LLM baseline, random baseline, or non-grounded baseline.
* **Metric Provenance:** Completely absent. No backlink or JSON metadata tracing an analytical metric to its supporting simulation events, agents, or input evidence.

### 2.7 User Interface & CLI Surface — STATUS: PARTIAL & PLACEHOLDER
* **CLI (`app/cli.py`):** Fully functional for MiroFish baseline runs (`mirofish run`, `mirofish runs list`, `mirofish runs status`, `mirofish runs export`, `mirofish doctor`). **No research commands exist.**
* **Streamlit UI (`app/streamlit_app.py`):**
  * Pages for problem definition, stakeholder count, candidate decisions, and parameters accept user input.
  * Page `run_simulation` displays:
    > `st.info("Multi-scenario simulation will be implemented. For now, using single simulation workflow.")`
  * Pages `emergent_behaviour`, `social_impact`, `scenario_comparison`, `recommendation` render static `st.info` placeholder bullets.
  * No interactive graphs, community maps, temporal charts, or scenario comparison cards are rendered from live simulation data.

### 2.8 Test Suite — STATUS: ZERO RESEARCH COVERAGE
* **Total Tests:** 19 tests in repository (all passing).
* **Coverage Breakdown:**
  * `tests/test_cli_artifacts_and_visuals.py`: 6 tests (RunStore, SVG generation, CLI parser, run manifest promotion, JSON export).
  * `tests/test_ollama_llm_client.py`: 12 tests (LLMClient, JSON extraction, error handling, OASIS model bridge, live connectivity).
  * `scripts/test_profile_format.py`: 1 test (profile format validation).
* **Research Tests:** **0 tests exist** for `CommunityContextEngine`, `StakeholderDigitalTwin`, `ScenarioDesigner`, `EmergentBehaviourAnalyzer`, `SocialImpactModel`, `DecisionComparisonEngine`, or `DecisionIntelligenceEngine`.

---

## 3. Documentation vs. Implementation Audit

| README / Documentation Claim | Implementation Evidence | Actual Status | Required Remedy |
| :--- | :--- | :--- | :--- |
| **"8-dimension quantitative social impact modeling"** | Exists only in `app/research/social_impact_model.py` with simplistic keyword formulas; not invoked in pipeline. | **MISLEADING / DISCONNECTED** | Implement real mathematical metrics, connect to pipeline, label as simulated scenario indices. |
| **"Multi-scenario decision comparison & ranking"** | `DecisionComparisonEngine` exists in `app/research/` but is never called by CLI or UI. Streamlit redirects to single simulation. | **PARTIALLY TRUE / DISCONNECTED** | Build multi-scenario runner in CLI and UI; execute and compare real runs. |
| **"Knowledge graph grounded stakeholder digital twins"** | `OasisProfileGenerator` queries graph entities; `StakeholderDigitalTwin` in `app/research/` is a disconnected wrapper with dummy persona loops. | **PARTIALLY TRUE** | Refactor profile generator into digital twin pipeline with verifiable trait grounding. |
| **"Decision intelligence dossier with uncertainty markers"** | Confidence interval is hardcoded as `[score - 0.1, score + 0.1]`; not invoked in pipeline. | **MISLEADING** | Replace with empirical standard deviation / bootstrap confidence intervals over Monte Carlo runs. |
| **"Predict how citizens will react"** | Claims predictive capability in problem statement and abstract. | **SCIENTIFICALLY INVALID** | Rephrase to "Analyze simulated stakeholder responses under controlled computational scenarios". |
| **"Select socially optimal intervention"** | Claims normative optimality from fixed-weight score. | **SCIENTIFICALLY INVALID** | Rephrase to "Compare simulated scenario outcomes under configurable evaluation parameters". |

---

## 4. Mock / Hardcoded / Placeholder Audit

| File | Line / Function | Description | Type | Severity |
| :--- | :--- | :--- | :--- | :--- |
| `app/research/decision_intelligence_engine.py` | Line 472: `_estimate_confidence_intervals` | `overall_score_range: [score - 0.1, score + 0.1]` | Hardcoded Placeholder | **HIGH** |
| `app/research/social_impact_model.py` | Line 260: `_estimate_confidence` | `confidence = (sample_size/100) * factor` | Arbitrary Heuristic | **HIGH** |
| `app/research/emergent_behaviour_analyzer.py` | Line 165: `_calculate_sentiment_metrics` | Fixed keyword counting `['support', 'agree', ...]` | Naive Heuristic | **HIGH** |
| `app/research/stakeholder_digital_twin.py` | Line 163: `generate_stakeholders` | `persona = f"Community member with focus on {entity.labels}"` | Dummy Text Loop | **HIGH** |
| `app/streamlit_app.py` | Line 1281: `render_run_simulation` | `st.info("Multi-scenario simulation will be implemented...")` | UI Placeholder | **MEDIUM** |
| `app/streamlit_app.py` | Line 1312: `render_social_impact` | `st.info("Social impact evaluation requires completed simulation results...")` | UI Placeholder | **MEDIUM** |
| `app/streamlit_app.py` | Line 1332: `render_scenario_comparison` | `st.info("Scenario comparison requires multiple completed simulations...")` | UI Placeholder | **MEDIUM** |
| `app/streamlit_app.py` | Line 1349: `render_recommendation` | `st.info("Decision intelligence requires completed scenario comparison...")` | UI Placeholder | **MEDIUM** |

---

## 5. Top 10 Research Gaps

### Gap 1: Disconnected Analytics Pipeline
* **Priority:** P0 (Critical)
* **What Exists:** `app/research/` contains isolated classes. `app/cli.py` runs simulation and exits after generating report/verdict without calling analytics.
* **What Is Missing:** Direct invocation of analytics on simulation completion; persistence of `research_metrics.json`, `interaction_graph.json`, and `provenance.json` in `uploads/runs/<run_id>/`.
* **Fix:** Wire canonical event extraction and research analytics directly into `_collect_run_outputs` and create `mirosense analyze` CLI command.

### Gap 2: Absence of Canonical Event Ledger
* **Priority:** P0 (Critical)
* **What Exists:** Raw `AgentAction` with unstructured `action_args`.
* **What Is Missing:** Typed `SimulationEvent` dataclass and `EventAdapter` extracting explicit stance ($\in [-1, 1]$), target agents, parent post IDs, topics, and platforms.
* **Fix:** Implement `app/mirosense/schemas/events.py` and `app/mirosense/adapters/oasis_adapter.py`.

### Gap 3: Missing Interaction Graph & Centrality Metrics
* **Priority:** P0 (Critical)
* **What Exists:** Input knowledge graph (pre-simulation).
* **What Is Missing:** Dynamic post-simulation interaction graph (nodes: agents, posts; edges: reply, quote, like, follow, disagree) with degree, betweenness, PageRank, and density computation.
* **Fix:** Implement `app/mirosense/analytics/interaction_graph.py` using standard deterministic graph algorithms (pure Python or NetworkX).

### Gap 4: Missing Community Detection & Network Modularity
* **Priority:** P0 (Critical)
* **What Exists:** None.
* **What Is Missing:** Deterministic community detection (Louvain/Leiden or modularity-optimizing partition) over the interaction graph with community-level stance and topic distributions.
* **Fix:** Implement `app/mirosense/analytics/community_detection.py`.

### Gap 5: Scientifically Defensible Polarization Model
* **Priority:** P1 (High)
* **What Exists:** Binary balance ratio $1 - \min(pos, neg)/(pos+neg)$.
* **What Is Missing:** Decomposed polarization: $P_{total} = w_{op} P_{opinion} + w_{net} P_{network} + w_{int} P_{interaction}$ with stance variance/bimodality, network modularity, and cross-community interaction ratio.
* **Fix:** Implement `app/mirosense/analytics/polarization.py` with configurable weights and documented formulas.

### Gap 6: Temporal Dynamics Tracking
* **Priority:** P1 (High)
* **What Exists:** Only total timeline action counts (`round_num`, `twitter_actions`, `reddit_actions`).
* **What Is Missing:** Per-round trajectory of mean stance, stance variance, conflict rate, community count, and modularity across rounds $1 \dots R$.
* **Fix:** Implement `app/mirosense/analytics/temporal_analysis.py`.

### Gap 7: Scientific Validation Engine (Monte Carlo & Uncertainty)
* **Priority:** P1 (High)
* **What Exists:** Single simulation execution only. Hardcoded $\pm 0.1$ fake confidence intervals.
* **What Is Missing:** Multi-seed experiment runner (`MonteCarloExperiment`) executing $N$ runs (e.g. 5, 10, 30 seeds), computing empirical mean, standard deviation, and Student-t/bootstrap 95% confidence intervals.
* **Fix:** Implement `app/mirosense/validation/monte_carlo.py` and `app/mirosense/validation/uncertainty.py`.

### Gap 8: Sensitivity & Ablation Framework
* **Priority:** P1 (High)
* **What Exists:** None.
* **What Is Missing:** Parameter sweep runner (agent count, rounds, temperature, initial stance) and feature-flagged ablation runner (`NO_GRAPH`, `NO_MEMORY`, `NO_COMMUNITIES`).
* **Fix:** Implement `app/mirosense/validation/sensitivity.py` and `app/mirosense/validation/ablation.py`.

### Gap 9: Metric Provenance Tracing
* **Priority:** P1 (High)
* **What Exists:** None.
* **What Is Missing:** Backlink index tracing every computed metric to its constituent event IDs, agent IDs, rounds, and source document entities.
* **Fix:** Implement `app/mirosense/provenance/metric_provenance.py`.

### Gap 10: Research CLI & Dashboard Integration
* **Priority:** P2 (Medium)
* **What Exists:** `mirofish run/runs/doctor` CLI and placeholder Streamlit pages.
* **What Is Missing:** `mirosense` CLI commands (`analyze`, `communities`, `polarization`, `compare`, `experiment`) and populated Streamlit tabs displaying real charts and tables.
* **Fix:** Extend `app/cli.py` and implement interactive rendering functions in `app/streamlit_app.py`.

---

## 6. Recommended Implementation Plan

```text
PHASE 1 — Canonical Event Ledger & Data Normalization
├── Create app/mirosense/schemas/events.py (SimulationEvent dataclass)
├── Create app/mirosense/adapters/oasis_adapter.py (Normalize actions.jsonl -> SimulationEvent stream)
└── Add unit tests for event parsing and normalization

PHASE 2 — Core Research Analytics Engine
├── app/mirosense/analytics/interaction_graph.py (Agent interaction network, degree, PageRank, betweenness)
├── app/mirosense/analytics/community_detection.py (Deterministic Louvain/modularity clustering)
├── app/mirosense/analytics/opinion_dynamics.py (Explicit stance in [-1, 1], acceptance, agreement)
├── app/mirosense/analytics/polarization.py (Decomposed opinion + network + interaction model)
├── app/mirosense/analytics/temporal_analysis.py (Round-by-round metric evolution)
├── app/mirosense/analytics/conflict_analysis.py (Cross-community dispute & escalation)
├── app/mirosense/analytics/influence_analysis.py (Simulated network centrality influence)
└── app/mirosense/analytics/information_diffusion.py (Cascade size, depth, cross-community spread)

PHASE 3 — Scenario Evaluation & Comparative Analysis
├── app/mirosense/evaluation/scenario_engine.py (Formal Scenario dataclass with frozen params & seeds)
├── app/mirosense/evaluation/scenario_comparison.py (Side-by-side behavioral profiles & effect sizes)
└── app/mirosense/provenance/metric_provenance.py (Evidence -> Agent -> Event -> Metric traceability)

PHASE 4 — Scientific Validation & Experimentation
├── app/mirosense/validation/monte_carlo.py (Multi-seed simulation runner with statistical aggregation)
├── app/mirosense/validation/uncertainty.py (Empirical standard deviations & 95% confidence intervals)
├── app/mirosense/validation/sensitivity.py (Parameter sweep runner)
├── app/mirosense/validation/ablation.py (Feature-flagged ablation framework)
└── app/mirosense/validation/baselines.py (Direct LLM and random interaction baselines)

PHASE 5 — Pipeline Integration & CLI / UI Extensions
├── Connect analytics directly into RunStore and pipeline completion in app/cli.py
├── Register MiroSense CLI commands (mirosense analyze, compare, experiment, etc.)
└── Populate Streamlit research dashboard tabs with live dynamic data visualizations

PHASE 6 — Comprehensive Testing & Documentation
├── Implement full pytest test suite across all new analytics and validation modules
├── Update README.md with rigorous academic framing and exact reproducibility instructions
└── Generate RESEARCH_CONTRIBUTION.md documenting upstream vs original research contributions
```

---

## 7. Research Symposium Readiness Checklist

| Requirement | Current Status | Required Action Before Presentation |
| :--- | :---: | :--- |
| **Deterministic Data Pipeline** | PARTIAL | Ensure all analytics run deterministically on saved event logs |
| **Evidence-Grounded Digital Twins** | PASS | Existing knowledge graph extraction is operational |
| **Simulation Runtime** | PASS | OASIS dual-platform simulation is operational |
| **Network & Community Analytics** | FAIL | Must implement interaction graph & community detection |
| **Mathematical Polarization Model** | FAIL | Must implement 3-part decomposed polarization model |
| **Temporal Trajectory Tracking** | FAIL | Must implement round-by-round time series metrics |
| **Empirical Uncertainty (Monte Carlo)**| FAIL | Must implement multi-seed runner with confidence intervals |
| **Reproducibility Manifest** | PARTIAL | Must include experiment configuration hashes and seeds |
| **No Fabricated Data / Placeholders** | FAIL | Must remove all fake confidence formulas and UI placeholders |
| **Honest Academic Framing** | FAIL | Must replace all predictive claims with scenario-analysis framing |

---
