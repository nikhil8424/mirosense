# Mirosence

A social simulation scenario engine. Feed it documents describing any scenario, and MiroFish simulates AI agents interacting on social media to explore how events might unfold. Designed for agent-driven workflows — outputs include a machine-readable `verdict.json` alongside visual snapshots and a comprehensive analytical report.

> Fork of [666ghj/MiroFish](https://github.com/666ghj/MiroFish) — fully translated to English, streamlined CLI-only architecture, local Ollama (Qwen3) inference, and Claude/Codex CLI bridge support.

---

## What it does

1. **Feed reality seeds** — Ingest PDFs, markdown, or plain text files (e.g., news articles, policy drafts, market research, or scenario notes).
2. **Describe what to predict** — Define a natural language objective (e.g., *"Predict how citizens and taxpayers will react to the fare-free weekend bus policy"*).
3. **MiroFish builds a world** — Extracts entities and relationships into a knowledge graph, then generates AI agent personas with distinct personalities, stances, and backgrounds.
4. **Agents simulate social media** — Runs a multi-agent simulation on Twitter, Reddit, or dual-platform parallel mode where agents post, reply, upvote/downvote, argue, and follow each other.
5. **Get a prediction report & verdict** — Synthesizes simulation events into an analytical report, SVG visual snapshots, and a machine-readable `verdict.json` with confidence scores and signals.

---

## Quick Start

### Prerequisites

- **Python**: 3.11 – 3.12
- **Package Manager**: [uv](https://docs.astral.sh/uv/)
- **LLM Engine** (choose one):
  - [Ollama](https://ollama.com/) (recommended for local/offline execution — default: `qwen3:8b`)
  - [Claude Code CLI](https://claude.ai/code) (`claude` binary on PATH)
  - [Codex CLI](https://github.com/openai/codex) (`codex` binary on PATH)

### Setup

```bash
# 1. Clone the repository and install dependencies
uv sync

# 2. Configure environment (copy example configuration)
# On macOS / Linux / PowerShell:
cp .env.example .env
# On Windows CMD:
# copy .env.example .env

# 3. Run diagnostics to verify your environment, provider, and model availability
uv run mirofish doctor
```

### Run a simulation

**Single-line (Recommended for PowerShell & CMD):**
```powershell
uv run mirofish run --files demo_transit_policy.md --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" --platform reddit --max-rounds 3
```

**macOS / Linux (Bash / Zsh):**
```bash
# Rich visual progress
uv run mirofish run \
  --files demo_transit_policy.md \
  --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" \
  --platform reddit \
  --max-rounds 3

# JSON output for programmatic pipelines
uv run mirofish run \
  --files demo_transit_policy.md \
  --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" \
  --platform reddit \
  --max-rounds 3 \
  --json
```

**Windows (PowerShell multi-line):**
```powershell
uv run mirofish run `
  --files demo_transit_policy.md `
  --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" `
  --platform reddit `
  --max-rounds 3
```

### Inspect prior runs

```bash
# List prior runs (slim summary: run_id, status, created_at, artifact_count)
uv run mirofish runs list --json

# Check run status and view full manifest (replace <run_id> with actual ID e.g. run_8cfa25d36dc9)
uv run mirofish runs status run_8cfa25d36dc9 --json

# Export all artifact paths or a specific artifact
uv run mirofish runs export run_8cfa25d36dc9 --json
uv run mirofish runs export run_8cfa25d36dc9 --artifact report/verdict.json --json
```

---

## Streamlit Web UI

MiroFish includes a web-based interface built with Streamlit for interactive simulation management.

### Launch the UI

```bash
uv run streamlit run app/streamlit_app.py
```

The UI provides:
- **Dashboard**: View recent simulations, their status, and key metrics
- **New Simulation**: Upload documents, set requirements, configure agent count (5-500), platform, and simulation rounds
- **Pipeline Progress**: Real-time monitoring of simulation preparation and execution
- **Results**: View simulation reports, visualizations, and agent statistics

### UI Features

- **Agent Count Control**: Specify the number of agents to simulate (5-500, default 50)
- **Document Upload**: Support for PDF, Markdown, and TXT files
- **Platform Selection**: Choose between Twitter, Reddit, or parallel simulation
- **Progress Tracking**: Visual progress indicators for each pipeline stage
- **Results Display**: Interactive charts, agent statistics, and downloadable artifacts

The Streamlit UI shares the same backend pipeline and RunStore as the CLI, ensuring consistency across interfaces.

---

## CLI Reference

### Commands

| Command | Description |
|---------|-------------|
| `mirofish doctor` | Run environment, `.env`, provider, and local model diagnostics |
| `mirofish run` | Execute end-to-end simulation pipeline and persist artifacts |
| `mirofish runs list` | List prior runs and high-level metadata (slim format) |
| `mirofish runs status <id>` | View full execution status and manifest for a run |
| `mirofish runs export <id>` | Resolve absolute paths to persisted run artifacts |

### Options for `mirofish run`

```text
mirofish run
  --files FILE [FILE ...]     One or more source files (pdf/md/txt) used to ground ontology and personas
  --requirement TEXT          Plain-English simulation requirement (e.g. "How will voters react to X?")
  --platform PLATFORM         Simulation platform: parallel (default), twitter, or reddit
  --max-rounds N              Max simulation rounds (default: 10)
  --agent-count N             Number of agents to simulate (5-500, default: 50)
  --wait                      Accepted for consistency (pipeline waits by default)
  --output-dir PATH           Custom directory to store run artifacts
  --json                      Emit machine-readable JSON on stdout
```

- **Output formatting**:
  - Without `--json`: Renders a rich visual pipeline display on `stderr` (automatically respects `NO_COLOR` and non-TTY environments).
  - With `--json`: Emits structured JSON to `stdout` with plain progress logs on `stderr`.
- **Exit codes**: `0` on success, `1` on error (including configuration and validation errors).
- `--help` and `--version` work without requiring a configured `.env`.

---

## LLM Providers & Configuration

MiroFish supports local offline models via Ollama as well as subscription CLI bridges. Set `LLM_PROVIDER` in `.env`:

| Provider | `.env` Setting | Requirements / Details |
|----------|---------------|------------------------|
| **Ollama** *(Local, Free)* | `LLM_PROVIDER=ollama` | Local Ollama instance running (e.g., `qwen3:8b`) — zero API cost, offline & private |
| **Claude CLI** | `LLM_PROVIDER=claude-cli` | `claude` CLI binary installed and authenticated with Claude Code subscription |
| **Codex CLI** | `LLM_PROVIDER=codex-cli` | `codex` CLI binary installed and authenticated with Codex subscription |

### Environment Variables (`.env`)

```env
# LLM Provider selection: ollama | claude-cli | codex-cli
LLM_PROVIDER=ollama

# Ollama-specific settings (used when LLM_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
OLLAMA_TIMEOUT=600.0

# Concurrency tuning (optional)
# OASIS_CLI_SEMAPHORE=1   # Concurrency limit (default: 1 for ollama to prevent GPU contention, 5 for CLI)
```

### Reasoning Models & Robust JSON Parsing

MiroFish includes built-in preprocessing for modern reasoning models (such as Qwen 2.5/3 or DeepSeek):
- Automatically strips `<think>...</think>` reasoning tokens before downstream parsing.
- Uses strict `format: "json"` with multi-layer JSON extraction (markdown block detection, bracket bounding, and direct fallback) to ensure robust structured responses.

---

## Local Ollama Setup (Qwen3)

MiroFish is optimized for local inference with **Qwen3 8B** via Ollama.

### 1. Install & start Ollama
Download and install Ollama from [ollama.com](https://ollama.com/).

### 2. Pull the model
```bash
ollama pull qwen3:8b
```

### 3. Verify Ollama is running
```bash
ollama run qwen3:8b "Say hello in one sentence"
```

### 4. Run MiroFish Diagnostics
```bash
uv run mirofish doctor
```
Expected output:
```text
  [PASS] LLM_PROVIDER set
  [PASS] LLM_PROVIDER valid
  [PASS] Ollama reachable at http://localhost:11434
  [PASS] Ollama model 'qwen3:8b' installed

doctor: all checks passed
```

### 5. Hardware & Performance Guidance

> [!TIP]
> **Performance Guidance for Local Hardware**:
> - **Inference Speed**: Local execution speed depends directly on available VRAM and GPU/CPU layer offloading.
> - **Concurrency**: Concurrency defaults to `1` when using Ollama to avoid request queuing bottlenecks and VRAM thrashing.
> - **Recommended Scope**: For quick local runs, keep simulations focused (e.g., 5–10 personas, 2–3 rounds). For larger simulations, scale up `--max-rounds` as needed.

---

## Run Artifacts

Every simulation execution generates an immutable, self-contained directory under `uploads/runs/<run_id>/`:

```text
uploads/runs/<run_id>/
  manifest.json               # Full execution manifest, status, and artifact index
  input/
    requirement.txt           # Input requirement text
    source_files/             # Copies of input files used for the run
    ontology.json             # Extracted ontology definition
    simulation_config.json    # Generated simulation parameters
  graph/
    graph.json                # Knowledge graph nodes and edges
    graph_summary.json        # Graph statistics and entity counts
  simulation/
    timeline.json             # Round-by-round event timeline
    top_agents.json           # Most active and influential agents
    actions.jsonl             # Complete log of all simulated social actions
    config.json               # OASIS runtime configuration
  report/
    verdict.json              # Key machine-readable predictions, confidence & signals
    summary.json              # Executive summary
    report.md                 # Full markdown analytical report
  visuals/
    swarm-overview.svg        # Swarm activity visualization
    cluster-map.svg           # Persona community cluster snapshot
    timeline.svg              # Sentiment / activity trajectory
    platform-split.svg        # Cross-platform sentiment comparison
  logs/
    run.log                   # Detailed pipeline execution logs
```

### Key Agent Output: `verdict.json`

For automated agent pipelines, `report/verdict.json` provides a clean, machine-parsable summary of simulation findings:

```json
{
  "prediction": "Strong initial skepticism shifting to positive adoption once fare benefits are realized.",
  "confidence": 0.82,
  "key_dynamics": [
    "Initial concerns focused on tax burden and service frequency.",
    "Transit advocates drove viral positive sentiment on Reddit."
  ],
  "signals": [
    {"signal": "Public support", "direction": "positive", "strength": "high"},
    {"signal": "Budget scrutiny", "direction": "neutral", "strength": "medium"}
  ]
}
```

---

## Testing

MiroFish includes unit and integration tests with pytest:

```bash
# Run all tests (including live Ollama integration tests if Ollama is running)
uv run python -m pytest tests/

# Run fast unit tests only (skipping live Ollama service calls)
uv run python -m pytest tests/ -m "not integration"
```

---

## Architecture

```text
app/
  _agent_cli.py           Reusable CLI helper utilities (diagnostics runner)
  cli.py                  CLI entry point and command dispatch
  cli_display.py          Rich terminal live pipeline display
  config.py               Configuration loading & validation (.env)
  run_artifacts.py        Immutable RunStore artifact management
  visual_snapshots.py     Pure Python SVG visualization generator
  core/                   WorkbenchSession, TaskManager, ResourceLoader
  resources/              Persistence adapters (projects, documents, graph, simulations, reports)
  tools/                  Composable pipeline steps (ontology, graph, prepare, run, report)
  services/
    graph_storage.py      JSON graph backend
    graph_db.py           Graph query facade
    entity_extractor.py   LLM-based entity & relationship extraction
    graph_builder.py      Ontology -> knowledge graph pipeline
    oasis_profile_generator.py Persona generation and stance assignment
    simulation_runner.py  OASIS simulation subprocess runner & monitor
    report_agent.py       Single-pass simulation analysis and report synthesis
    graph_tools.py        Graph search, agent interviews, and sub-graph analysis
  utils/
    llm_client.py         Unified LLM client (Ollama HTTP + Claude/Codex CLI bridge)
    oasis_llm.py          CAMEL/OASIS LLM bridge adapter
    logger.py             Structured logging
scripts/                  OASIS simulation runner scripts (subprocess)
tests/                    Pytest test suite
```

---

## Acknowledgments

- [MiroFish](https://github.com/666ghj/MiroFish) by 666ghj — original concept and design
- [OASIS](https://github.com/camel-ai/oasis) by CAMEL-AI — multi-agent social media simulation environment

---

## License

[AGPL-3.0](LICENSE)

##---------------------------------
To run MiroFish, follow these simple steps:

---

### Step 1: Verify Environment & Provider Setup

Run the diagnostic tool to check that your `.env` and LLM provider (Ollama, Claude CLI, or Codex CLI) are ready:

```bash
uv run mirofish doctor
```

*(If you are using Ollama, ensure the Ollama service is running and you have pulled the model with `ollama pull qwen3:8b`)*.

---

### Step 2: Run a Simulation

You pass in your source document(s) (PDF, Markdown, or TXT) and your natural-language prediction goal.

#### Single-line Command (All platforms / PowerShell):
```powershell
uv run mirofish run --files demo_transit_policy.md --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" --platform reddit --max-rounds 2
```

#### Option A: Interactive / Rich Terminal Output
```bash
# macOS / Linux (Bash):
uv run mirofish run \
  --files demo_transit_policy.md \
  --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" \
  --platform reddit \
  --max-rounds 2

# Windows (PowerShell):
uv run mirofish run `
  --files demo_transit_policy.md `
  --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" `
  --platform reddit `
  --max-rounds 2
```

#### Option B: JSON Output (For programmatic scripts / agent pipelines)
```bash
uv run mirofish run --files demo_transit_policy.md --requirement "Predict how citizens and taxpayers will react to the fare-free weekend bus policy" --platform reddit --max-rounds 2 --json
```

**Common Flags:**
- `--files`: Path to one or more seed documents (`.pdf`, `.md`, `.txt`).
- `--requirement`: Natural-language description of what you want to forecast.
- `--platform`: Social platform to simulate (`reddit`, `twitter`, or `parallel` for both).
- `--max-rounds`: Number of simulation rounds (default: `10`; use `2` or `3` for quick test runs).
- `--agent-count`: Number of agents to simulate (5-500, default: `50`).

---

### Step 3: Inspect Results & Artifacts

All outputs are saved to `uploads/runs/<run_id>/`.

```bash
# List all previous runs
uv run mirofish runs list --json

# View run status and full manifest (substitute your actual run ID)
uv run mirofish runs status run_8cfa25d36dc9 --json

# Export artifact file paths
uv run mirofish runs export run_8cfa25d36dc9 --json
```

### Key Generated Files:
- **`report/verdict.json`**: Machine-readable prediction, confidence score, and signals.
- **`report/report.md`**: Full analytical report.
- **`visuals/`**: SVG visual snapshots (`swarm-overview.svg`, `cluster-map.svg`, `timeline.svg`, `platform-split.svg`).
"# mirosense" 
