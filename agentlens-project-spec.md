# AgentLens — Project Spec
> **PyPI package name: `agentstats`** (selected by user 2026-08-05, pending PyPI manual check)

## Problem
Multi-agent LLM systems (LangGraph, Claude Code, Ollama, OpenRouter-based agents) fail silently — when something breaks, developers see the final broken output but not *which* agent step failed, *why* it failed, or *what it cost* to get there. Existing tools (Langfuse, MLflow, AgentTrace) already cover this space, but push users toward cloud dashboards and web UIs, and none classify failure *causes* — only pass/fail.

## Core Idea
A terminal-native, zero-signup, zero-cloud Python library that:
1. Auto-instruments LLM/agent calls with **no code rewrite** (`agentlens.watch()`)
2. Tracks latency, token cost, and errors per step, showing them **live in the terminal**
3. Classifies *why* a step failed using a research-backed error taxonomy, not just that it failed
4. Exports results as JSON for CI pipelines or later comparison
5. Compares two runs side-by-side (e.g., Ollama vs. OpenRouter vs. Claude Code) on cost/latency/failure type

## Why This Could Stand Out (vs. existing tools)
- **No rewrite required** — patches existing SDK methods (OpenAI-compatible client for Ollama/OpenRouter, Anthropic SDK for Claude Code) rather than requiring manual wrapping
- **Terminal-first** — works over SSH, no browser/dashboard dependency, serves an underserved CLI-first audience
- **Failure taxonomy classifier** — reuses the author's own FOSSEE/IIT Bombay research: a 6-category taxonomy for classifying LLM coding errors (Boundary/Indexing, Conditional/Boolean, State Management, Algorithmic Strategy, Edge Case Handling, Specification Misunderstanding), validated across 6 LLMs. No existing tool in this space does cause-classification — this is the actual moat.
- **Cost-safe by design** — the classifier is opt-in, batches failures into one call, routes to a local model when available (free), and shows a cost estimate before running

## Realistic Positioning
- **Not** a competitor to Langfuse/MLflow at the market level (those are funded, multi-year, full-team products)
- **Realistic ceiling:** a niche tool with a small, loyal audience — not an "industry staple"
- **Resume value is strong regardless of adoption scale**: verifiable PyPI package + GitHub repo + tests + real design tradeoffs + direct link to prior research work (taxonomy → productized tool)

## Architecture

```
Adapter Layer (per-tool hooks)
  - OpenAI-compatible adapter → covers Ollama + OpenRouter (same API shape)
  - Anthropic SDK adapter → covers Claude Code
        │  emits Span events
        ▼
Recorder (core)
  - in-memory span tree (nested agent → sub-agent → tool call)
  - tracks tokens, cost, latency, status, retries
        │
   ┌────┼─────────────┐
   ▼    ▼              ▼
Classifier   Terminal UI   JSON Exporter
 (2-tier)   (rich/textual)  (versioned schema)
   │
   ▼
Compare/Diff CLI (run vs. run)
```

### Span data model
```python
Span(
  id, parent_id, tool_name, model,
  start_ts, end_ts, tokens_in, tokens_out,
  cost_estimate, status, raw_error, retries
)
```

### Classifier — two tiers
- **Tier 1 (free, instant):** rule/regex heuristics on exception type — timeout, rate-limit, tool-not-found, malformed JSON. Covers infrastructure-level failures.
- **Tier 2 (opt-in, model-based):** for failures caused by wrong logic/decisions, classifies against the taxonomy below.

#### Failure Taxonomy (decided)
```python
class FailureCategory(Enum):
    # ── Core taxonomy: FOSSEE/IIT Bombay research-validated (code-generation errors) ──
    BOUNDARY_INDEXING          = "boundary_indexing"
    CONDITIONAL_BOOLEAN        = "conditional_boolean"
    STATE_MANAGEMENT           = "state_management"
    ALGORITHMIC_STRATEGY       = "algorithmic_strategy"
    EDGE_CASE_HANDLING         = "edge_case_handling"
    SPEC_MISUNDERSTANDING      = "specification_misunderstanding"
    # ── Extension: agent-orchestration errors (v1, not yet formally validated) ──
    TOOL_ORCHESTRATION_ERROR   = "tool_orchestration_error"
    # ── Fallback ──
    NONE                       = "none"
```

> **Design rationale:** The original 6 categories classify *why generated code is wrong* (validated across 6 LLMs). `TOOL_ORCHESTRATION_ERROR` covers a distinct failure surface — wrong tool selected, wrong sub-agent routed to, undetected loops — which cannot be cleanly mapped to the code-gen taxonomy without misclassifying. It is labeled explicitly as an extension pending its own validation pass (a potential blog post / follow-up research note).



## Public API (target UX)
```python
import agentlens

agentlens.watch()                    # auto-patches detected SDKs
# ... existing agent code runs unchanged ...
agentlens.report()                   # live terminal summary
agentlens.report(classify=True)      # adds Tier 2 classification, shows cost estimate first
agentlens.export("run.json")         # JSON export
```
```bash
agentlens compare run_ollama.json run_openrouter.json
```

## v1 Scope (decided)
- **Tools supported:** Ollama, OpenRouter, Claude Code
- **Classifier:** Tier 1 + Tier 2 together in v1
- **Timeline:** 3-4 weeks, polished/resume-ready (not a quick MVP)

### Deferred to v2
- LangGraph adapter
- Web/hosted dashboard
- Additional taxonomy categories (e.g. `TOOL_ORCHESTRATION_ERROR`)

## Build Plan
- **Week 1:** Span schema, recorder, OpenAI-compatible adapter (Ollama + OpenRouter), basic terminal output, tests
- **Week 2:** Anthropic adapter (Claude Code), Tier 1 rule-based classifier, rich/textual live terminal UI, JSON export
- **Week 3:** Tier 2 taxonomy classifier, cost-estimate confirmation flow, local-model routing, batched classification
- **Week 4:** Compare mode, README + demo GIF, PyPI packaging (`pyproject.toml`, `build`, `twine`), CI via GitHub Actions

## Package Structure
```
agentlens/
├── agentlens/
│   ├── __init__.py          # public API: watch(), report(), compare()
│   ├── span.py
│   ├── adapters/
│   │   ├── openai_compat.py
│   │   └── anthropic.py
│   ├── classifier/
│   │   ├── tier1_rules.py
│   │   └── tier2_taxonomy.py
│   ├── ui/terminal.py
│   ├── export/json_report.py
│   └── compare.py
├── tests/
├── examples/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Publishing
- PyPI package, name TBD pending availability check (candidates: `agentlens`, `tracewise`, `llmscope`, `agentsight`)
- Standard flow: `pip install build twine` → `python -m build` → `twine upload dist/*`

## Promotion Plan (post-launch)
- Strong README with quickstart + terminal UI demo GIF, real before/after example
- Launch posts: Show HN, r/LocalLLaMA, r/LangChain, r/MachineLearning — framed as sharing a real problem/solution, not self-promotion
- Blog/dev.to post connecting the taxonomy research story to the tool
- Track real signals: GitHub issues from strangers, external PRs, PyPI download counts — more meaningful than star count
- Consider sending 1-2 real PRs to an existing project (e.g. Langfuse, LiteLLM) once familiar with the space, to also have a "contributor to X" resume line alongside the original project

## Open Questions
- Final package name (pending PyPI availability check)
- Whether `TOOL_ORCHESTRATION_ERROR` (or similar) needs to be added to the taxonomy for agent-decision failures, vs. code-generation failures the original taxonomy was designed for
