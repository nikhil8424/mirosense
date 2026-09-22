# MiroSense — System Architecture & Layered Design

This document details the multi-tier software architecture of **MiroSense**, illustrating the clear separation between simulation runtimes, canonical event data layers, and deterministic research analytics.

---

## 1. System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           1. INGESTION & KNOWLEDGE LAYER                    │
│                                                                             │
│   Evidence Documents (PDF, MD, TXT) ──> DocumentParser ──> GraphBuilder     │
│                                                            │                │
│                                                            ▼                │
│                                                    Knowledge Graph          │
│                                                   (Entities/Relations)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           2. AGENT & SIMULATION LAYER                       │
│                                                                             │
│   Knowledge Graph ──> ProfileGenerator ──> Heterogeneous Stakeholder Agents │
│                                            │                                │
│                                            ▼                                │
│                                    OASIS Simulation Engine                  │
│                                   (Twitter / Reddit Platforms)              │
│                                            │                                │
│                                            ▼                                │
│                                      actions.jsonl                          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        3. CANONICAL EVENT LEDGER LAYER                      │
│                                                                             │
│      actions.jsonl ──> OasisEventAdapter ──> canonical_events.jsonl         │
│                           (Deterministic IDs, Parent Linking, Stance)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           4. RESEARCH ANALYTICS LAYER                       │
│                                                                             │
│   ┌────────────────────────┬────────────────────────┬───────────────────┐   │
│   │   InteractionGraph     │    OpinionDynamics     │ TemporalAnalyzer  │   │
│   │   - MultiDiGraph       │    - Mean Stance       │ - Round Series    │   │
│   │   - PageRank / Central.│    - Acceptance Ratio  │ - Trajectories    │   │
│   ├────────────────────────┼────────────────────────┼───────────────────┤   │
│   │   CommunityDetector    │  PolarizationAnalyzer  │  ConflictAnalyzer │   │
│   │   - Louvain Modularity │  - 3-Part Decomposition│  - Contestation   │   │
│   │   - Faction Stances    │  - P_total Score       │  - Cross-Comm.    │   │
│   ├────────────────────────┼────────────────────────┼───────────────────┤   │
│   │   InfluenceAnalyzer    │   DiffusionAnalyzer    │ ProvenanceTracker │   │
│   │   - Network Centrality │   - Cascade Trees      │ - Audit Trail     │   │
│   │   - Gini Inequality    │   - Propagation Depth  │ - Evidence Links  │   │
│   └────────────────────────┴────────────────────────┴───────────────────┘   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       5. EVALUATION & VALIDATION LAYER                      │
│                                                                             │
│   - ScenarioEngine (Parameter isolation & multi-arm scenario authoring)     │
│   - ScenarioComparator (Cohen's d effect sizes & behavioral profiles)       │
│   - MonteCarloEngine (Stochastic seed repetitions & aggregated variance)   │
│   - UncertaintyEngine (Student-t 95% confidence intervals)                 │
│   - SensitivityEngine (One-at-a-time OAT parameter sweeps)                  │
│   - AblationEngine (Subsystem ablation: Full / No-Graph / No-Community)     │
│   - BaselineEngine (Random interaction & Direct LLM benchmarks)             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       6. INTERFACE & REPORTING LAYER                        │
│                                                                             │
│   - RunStore (Immutable artifact directories & manifest.json)               │
│   - Research CLI (`mirofish analyze`, `communities`, `polarization`, etc.) │
│   - Research Dashboard (Streamlit interactive charts & provenance explorer) │
│   - ResearchReportGenerator (Structured markdown & JSON research dossiers)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure & Key Packages

```text
app/
├── mirosense/                     # MiroSense Research Architecture Upgrade
│   ├── schemas/                   # Canonical event, scenario, and manifest schemas
│   │   ├── events.py              # SimulationEvent & ActionType
│   │   ├── scenarios.py           # Scenario definition & isolation models
│   │   └── manifest.py            # ExperimentManifest & SHA-256 config hashing
│   ├── adapters/                  # Simulation log normalization
│   │   └── oasis_adapter.py       # OasisEventAdapter (actions.jsonl -> canonical_events.jsonl)
│   ├── analytics/                 # Deterministic mathematical & statistical analytics
│   │   ├── interaction_graph.py   # MultiDiGraph, PageRank, betweenness, density
│   │   ├── community_detection.py # Louvain modularity Q & faction detection
│   │   ├── opinion_dynamics.py    # Stance [-1, 1], acceptance, agreement cohesion
│   │   ├── temporal_analysis.py   # Round-by-round trajectory time-series
│   │   ├── polarization.py        # 3-part polarization decomposition (P_total)
│   │   ├── conflict_analysis.py   # Contestation and dispute analytics
│   │   ├── influence_analysis.py  # Simulated network influence & Gini index
│   │   └── information_diffusion.py # Cascade propagation trees & depth
│   ├── evaluation/                # Decision comparison & effect size
│   │   ├── effect_size.py         # Cohen's d & Hedges' g
│   │   ├── scenario_engine.py     # Multi-scenario manager
│   │   └── scenario_comparison.py # Comparative behavioral profiling
│   ├── validation/                # Scientific validation & uncertainty
│   │   ├── uncertainty.py         # Student-t 95% confidence intervals
│   │   ├── monte_carlo.py         # Monte Carlo stochastic engine
│   │   ├── sensitivity.py         # OAT parameter sweeps
│   │   ├── ablation.py            # Subsystem ablation engine
│   │   └── baselines.py           # Benchmarks (Random / Direct LLM)
│   ├── provenance/                # Metric traceability
│   │   └── metric_provenance.py   # Evidence -> Entity -> Agent -> Event -> Metric
│   └── reporting/                 # Research reporting
│       └── research_report.py     # Academic research dossier generator
├── services/                      # Upstream MiroFish / OASIS Simulation Substrate
│   ├── document_parser.py         # Ingestion
│   ├── graph_service.py           # Knowledge graph
│   ├── profile_generator.py       # Persona generation
│   └── simulation_runner.py       # OASIS multi-agent execution
├── cli.py                         # Unified MiroFish & MiroSense CLI
├── streamlit_app.py               # Empirical research dashboard
└── run_artifacts.py               # RunStore & file-backed persistence
```
