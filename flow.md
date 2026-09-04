# MiroFish CLI Architecture & Workflow

## Architecture Overview

MiroFish is a CLI social simulation engine that processes documents and requirements to generate multi-agent social media simulations with reports, verdicts, and visual snapshots.

### Core Components

#### 1. **CLI Layer** (`app/cli.py`)
- Entry point via `mirofish` command
- Orchestrates the complete pipeline
- Handles commands: `run`, `runs list/status/export`, `doctor`
- Manages Rich visual display for pipeline progress
- Persists immutable run artifacts via `RunStore`

#### 2. **Session Management** (`app/core/`)
- **`WorkbenchSession`**: Central orchestration layer that composes tools
- **`TaskManager`**: Thread-safe persistent task management for long-running operations
- **`SessionManager`**: Tracks session state across workflow phases
- **`ResourceLoader`**: Provides shared resource instances (stores, services)

#### 3. **Composable Tools** (`app/tools/`)
The pipeline is built from modular tools that can be composed independently:

- **`GenerateOntologyTool`**: Ingests documents, extracts entities/relationships via LLM
- **`BuildGraphTool`**: Constructs knowledge graph from ontology (background task)
- **`PrepareSimulationTool`**: Generates agent profiles and simulation config (background task)
- **`RunSimulationTool`**: Starts OASIS simulation subprocess
- **`GenerateReportTool`**: Creates analysis report from simulation data (background task)

#### 4. **Services Layer** (`app/services/`)
Business logic and domain services:
- **`GraphBuilderService`**: Graph construction and entity extraction
- **`SimulationRunner`**: OASIS subprocess management with real-time monitoring
- **`ReportAgent`**: Single-pass report generation
- **`OntologyGenerator`**: LLM-based entity/relationship extraction
- **`EntityReader`**: Graph entity filtering and reading
- **`SimulationManager`**: Simulation lifecycle management

#### 5. **Resource Layer** (`app/resources/`)
Persistence adapters for different data types:
- **`ProjectStore`**: Project metadata and ontology
- **`DocumentStore`**: Extracted document text
- **`SimulationStore`**: Simulation state and configuration
- **`ReportStore`**: Generated reports
- **`GraphDatabase`**: Graph storage (Kuzu DB)

#### 6. **Utilities** (`app/utils/`)
- **`LLMClient`**: CLI-only LLM client with retry logic (supports claude-cli, codex-cli, ollama)
- **`FileParser`**: Document text extraction (PDF, MD, TXT)
- **`TextProcessor`**: Text preprocessing and chunking
- **`Logger`**: Structured logging

#### 7. **Artifact Management** (`app/run_artifacts.py`)
- **`RunStore`**: Immutable run storage with manifests
- Each run creates a self-contained directory under `uploads/runs/<run_id>/`
- Tracks all artifacts: inputs, graph, simulation data, reports, visuals

#### 8. **Visual Generation** (`app/visual_snapshots.py`)
- Generates self-contained SVG visualizations (no browser needed)
- Swarm overview, cluster map, timeline, platform split charts

## Pipeline Workflow

### 1. **Input & Setup**
```
User Command: mirofish run --files f.pdf --requirement "..." --json
```
- Validates configuration (LLM provider, dependencies)
- Creates immutable run directory with manifest
- Freezes source files and requirement
- Initializes `WorkbenchSession` with shared resources

### 2. **Ontology Generation** (`GenerateOntologyTool`)
- Parses uploaded documents (PDF/MD/TXT)
- Extracts text using `FileParser`
- Preprocesses text with `TextProcessor`
- Calls LLM to generate ontology (entity types, relationship types)
- Creates project with ontology and analysis summary
- **Output**: `ontology.json`, `analysis_summary.txt`

### 3. **Graph Building** (`BuildGraphTool`)
- Runs as background task via `TaskManager`
- Splits text into chunks for processing
- Creates graph using `GraphBuilderService`
- Sets ontology definition on graph
- Adds text chunks in batches with progress tracking
- Validates entities against ontology types
- **Output**: `graph.json`, `graph_summary.json`

### 4. **Simulation Preparation** (`PrepareSimulationTool`)
- Creates simulation state linked to project and graph
- Reads entities from graph using `EntityReader`
- Generates agent profiles (capped at 150 words each) via LLM
- Creates simulation configuration JSON
- Prepares platform-specific profiles (Twitter/Reddit)
- Runs as background task with detailed progress callbacks
- **Output**: `simulation_config.json`, `twitter_profiles.csv`, `reddit_profiles.json`

### 5. **Simulation Execution** (`RunSimulationTool`)
- Starts OASIS simulation as subprocess via scripts in `scripts/`
- Supports platforms: Twitter, Reddit, or Parallel (both)
- Monitors simulation via `SimulationRunner`:
  - Real-time action logging from per-platform `actions.jsonl`
  - Round-by-round progress tracking
  - Process lifecycle management
- Optional graph memory update during simulation
- **Output**: `timeline.json`, `top_agents.json`, `actions.jsonl`, simulation logs

### 6. **Report Generation** (`GenerateReportTool`)
- Runs as background task via `TaskManager`
- `ReportAgent` analyzes simulation data
- Generates single-pass markdown report
- Extracts structured verdict for agent consumption
- **Output**: `report.md`, `verdict.json`, `summary.json`

### 7. **Visual Snapshots** (`visual_snapshots.py`)
- Generates SVG visualizations without browser dependency:
  - **Swarm Overview**: Node-link graph visualization
  - **Cluster Map**: Connected components analysis
  - **Timeline**: Activity per round chart
  - **Platform Split**: Twitter vs Reddit action volume
- **Output**: Multiple SVG files in `visuals/` directory

### 8. **Artifact Collection**
- Collects all outputs into run directory
- Updates manifest with artifact paths
- Generates final summary with verdict
- Returns complete manifest for agent consumption

## Data Flow

```
Documents → Text Extraction → Ontology → Graph → Entities → Agent Profiles → Simulation → Actions → Report → Verdict + Visuals
```

## Key Design Patterns

1. **Tool Composition**: `WorkbenchSession` composes tools like LEGO blocks
2. **Background Tasks**: Long-running operations use `TaskManager` for progress tracking
3. **Immutable Artifacts**: Each run is self-contained and never modified
4. **Resource Sharing**: `ResourceLoader` provides singleton instances to tools
5. **Session Tracking**: `SessionManager` maintains state across workflow phases
6. **Process Isolation**: Simulations run in separate subprocesses for safety
7. **Progress Callbacks**: Detailed progress reporting for UI updates

## Configuration

- **`.env` file**: LLM provider settings (ollama, claude-cli, codex-cli)
- **LLM integration**: Automatic retry with exponential backoff (3 attempts)
- **Platform support**: Twitter and Reddit simulation via OASIS framework
- **Output modes**: Rich terminal display or JSON for agent consumption

## Agent Integration

The CLI is designed for agent consumption via the `mirofish` skill. Key outputs for agents:

1. **`report/verdict.json`**: Machine-readable prediction with confidence
2. **`report/summary.json`**: High-level metrics and results
3. **`report/report.md`**: Detailed analysis (if needed)
4. **`--json` flag**: All commands return structured JSON output

## Directory Structure

```
app/
  cli.py              Entry point (console_scripts: mirofish)
  config.py            Env + validation (.env loaded automatically)
  cli_display.py       Rich visual pipeline display
  run_artifacts.py     Immutable run storage (RunStore)
  visual_snapshots.py  SVG generation (no browser needed)
  core/                WorkbenchSession, TaskManager, ResourceLoader
  tools/               Composable pipeline steps (ontology, graph, prepare, run, report)
  services/            Business logic (graph_storage, simulation_runner, report_agent)
  resources/           Persistence adapters (projects, documents, graph, simulations, reports)
  models/              Data models
  utils/
    llm_client.py      CLI-only LLM client with retry (claude-cli, codex-cli)
    logger.py          Structured logging
scripts/               OASIS simulation runner scripts (subprocess)
tests/                 pytest
uploads/               Runtime data (gitignored)
data/                  Graph JSON storage (gitignored)
```

## Commands

```bash
uv sync                                    # install
mirofish run --files f.pdf --requirement "..." --json   # run pipeline
mirofish runs list --json                  # list runs (slim: run_id, status, created_at, artifact_count)
mirofish runs status <id> --json           # full manifest for a run
mirofish runs export <id> --json           # export artifacts
mirofish --help                            # always works even with invalid/missing .env
uv run python -m pytest -x                 # tests
```

## Key Output: `report/verdict.json`

Machine-readable verdict for agent consumption — prediction, confidence (0-1), key_dynamics, and signals array. Agents should read this first, then `report/summary.json`, then `report/report.md` only if deeper analysis needed.

## Gotchas

- `mirofish runs list` returns a slim summary (`run_id`, `status`, `created_at`, `artifact_count`) so agent output stays narrow. Use `runs status <run_id>` for the full manifest.
- `Config.validate()` runs at `main()` startup before argparse. An invalid `LLM_PROVIDER` (e.g. `openai` left in `.env`) now fails fast with exit 1 instead of silently dying at the first LLM call. `--help` / `-h` / `--version` bypass the check.
- `cli_display.PipelineDisplay` honors `NO_COLOR` and `sys.stdout.isatty()` when constructing the Rich `Console`, so piped / non-tty invocations stay plain.
- Simulation runs OASIS in a subprocess via `scripts/`. The scripts add the project root to `sys.path` to import from `app.utils.oasis_llm`.
- `camel-oasis==0.2.5` and `camel-ai==0.2.78` are pinned — upgrading either can break the simulation pipeline.
- LLM calls have automatic retry with exponential backoff (3 attempts).
- CLI display (`cli_display.py`) uses `rich.Live` on stderr. Suppresses service-layer logs to WARNING during display. `--json` mode bypasses rich entirely.
- Never trash `uploads/runs/` — run artifacts are the product. Each run is immutable and self-contained.
- Process cleanup: `atexit` handler terminates OASIS subprocesses on CLI exit.
