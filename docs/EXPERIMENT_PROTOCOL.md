# MiroSense — Experiment Protocol & Reproducibility Standard

This protocol defines the formal experimental methodology required to execute, validate, and reproduce research experiments in MiroSense.

---

## 1. Experiment Execution Protocol

Every experimental investigation in MiroSense follows a strict six-stage lifecycle:

```text
Evidence Ingestion (PDF / Markdown / TXT)
                  ↓
Knowledge Graph Extraction & Grounding
                  ↓
Stakeholder Agent Persona Instantiation
                  ↓
Multi-Platform OASIS Simulation Run
                  ↓
Canonical Event Ledger Transformation (actions.jsonl → canonical_events.jsonl)
                  ↓
Topological, Community, Stance & Provenance Analytics
                  ↓
Validation Suite (Monte Carlo, Sensitivity, Ablation, Baselines)
                  ↓
Machine-Readable Artifact Persistence & Research Dossier
```

---

## 2. Parameter Control & Isolation Rules

When conducting controlled scenario comparisons (e.g. Policy A vs. Policy B):
1. **Identical Knowledge Base:** Both scenarios must be conditioned on the same underlying background evidence document corpus.
2. **Fixed Random Seeds:** Stochastic agent initializations must share the identical seed base unless running a Monte Carlo variance evaluation.
3. **Isolated Variable Changes:** Only explicitly defined policy intervention parameters (e.g. fare level, eligibility, schedule) may differ between scenarios.
4. **No Dynamic Prompt Drift:** System prompts and agent profile schemas must remain constant across comparison arms.

---

## 3. Experiment Artifact Standard

Every completed research run is stored under `uploads/runs/<run_id>/` with the following immutable artifact structure:

```text
uploads/runs/<run_id>/
├── input/
│   └── source_files/              # Exact frozen source evidence documents
├── graph/
│   ├── graph.json                 # Knowledge graph entities and relationships
│   └── graph_summary.json         # Graph topology summary
├── simulation/
│   ├── actions.jsonl              # Raw multi-platform simulation action log
│   ├── canonical_events.jsonl     # Normalized, typed canonical event ledger
│   ├── reddit_profiles.json       # Agent personas and community affiliations
│   └── twitter_profiles.csv       # Platform profiles
├── analytics/
│   ├── interaction_graph.json     # MultiDiGraph structure with edge weights
│   ├── network_metrics.json       # Density, reciprocity, PageRank, betweenness
│   ├── communities.json           # Louvain partitions and community metrics
│   ├── opinion_dynamics.json      # Stance distribution, acceptance, agreement
│   ├── temporal_metrics.json      # Round-by-round trajectory series
│   ├── polarization.json          # Decomposed 3-part polarization metrics
│   ├── conflict.json              # Contestation rates and cross-community friction
│   ├── influence.json             # Top agents and Gini concentration index
│   └── diffusion.json             # Information cascade propagation trees
├── provenance/
│   └── provenance.json            # Metric-to-event verifiable audit index
├── report/
│   ├── report.md                  # Narrative simulation summary
│   ├── research_report.md         # Comprehensive academic research report
│   └── verdict.json               # Machine-readable evaluation verdict
└── manifest.json                  # Immutable experiment manifest & artifact registry
```

---

## 4. Exact Reproduction Commands

### 1. Execute an End-to-End Simulation Run
```bash
mirofish run \
  --files docs/demo_transit_policy.md \
  --requirement "Evaluate simulated stakeholder response to fare-free weekend transit" \
  --platform parallel \
  --agent-count 10 \
  --max-rounds 3 \
  --json
```

### 2. Run Complete Research Analytics Suite on Existing Run
```bash
mirofish analyze <run_id> --json
```

### 3. Inspect Community Structure & Modularity $Q$
```bash
mirofish communities <run_id> --json
```

### 4. Inspect Decomposed Polarization Index ($P_{\text{total}}$)
```bash
mirofish polarization <run_id> --json
```

### 5. Compare Two Scenarios with Effect Size
```bash
mirofish compare <run_id_baseline> <run_id_alternative> --json
```

### 6. Audit Metric Provenance
```bash
mirofish provenance <run_id> --metric acceptance --json
```

### 7. Export Comprehensive Research Report
```bash
mirofish report <run_id>
```
