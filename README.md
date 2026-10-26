# BeliefGraph

**BeliefGraph keeps an assistant's long-term memory consistent when facts change, using ~10B open models.**

## What it does

An assistant stores two kinds of things:

- **Facts** it observed ("Priya lives in Seattle").
- **Conclusions** it derived from facts using rules ("Recommended a Seattle gym membership to Priya").

When a fact changes, some conclusions stay valid and others do not:

- Some must be **withdrawn**.
- Some must be **re-derived** (recomputed).
- Some should be marked **uncertain**, for example when the update came from an unreliable source.
- The rest stay **unchanged**.

Common memory systems store and retrieve memories, and some overwrite a changed fact. They do not track what was derived from it, so stale conclusions linger.

BeliefGraph adds that missing layer.

1. **When a memory is written,** a small model records why it is believed. It records which rule produced it and which facts or other conclusions satisfy that rule, as an AND/OR justification graph.
2. **When an update arrives,** a small model reads only the update and its nearest facts. It identifies which fact the update changes and how (retracted, replaced or doubted), and how reliable the source is.
3. **Truth-maintenance propagation over the graph** then decides an action for every affected memory: keep, withdraw, recompute or uncertain. It is deterministic, takes milliseconds and uses no LLM.

Every LLM call is narrow and scoped, never the whole memory. So the method works with models in the 7–12B range, and the cost of each update stays flat as memory grows.

### Example

The store is in [`examples/snapshot.json`](examples/snapshot.json).

- **Update:** "I just finished settling into my new place in Austin."
  - Result: the Seattle restaurant and gym recommendations need recomputing.
  - So does the weekend plan built on them, two steps away.
- **Update:** an anonymous forum post claims the gym reimbursement ended.
  - Result: that fact is only marked uncertain, because the source is unreliable.
  - The gym recommendation still has an alternative support: Priya runs three times a week.

## Results

All results use the same model, Gemma-4-12B, self-hosted with vLLM and no fine-tuning. Scores are balanced accuracy over memories that need revising versus memories that should be kept; 0.5 = changing nothing.

| Dataset | **BeliefGraph** | Whole store in prompt | Retrieval (RAG) | Mem0 | Graphiti (Zep) |
|---|---|---|---|---|---|
| Long dossiers (ours, 579 memories) | **0.935** | 0.752 | 0.730 | 0.527 | 0.500 |
| ProofWriter (converted, deep chains) | **0.847** | 0.620 | 0.636 | 0.500 | 0.489 |
| STALE v2 (implicit updates) | **0.892** | 0.756 | 0.750 | 0.684 | 0.500 |
| MQuAKE-T, ~12-memory stores (real Wikidata edits) | 0.963 | **0.984** | 0.725 | 0.594 | — |
| MQuAKE-T, 140 memories | **0.988** | 0.717 | 0.642 | 0.533 | 0.538 |
| MQuAKE-T, 443 memories | **0.961** | 0.500 | 0.646 | 0.532 | — |

**Across six ~10B models:** Gemma-4-12B, Qwen3.5-9B, Granite-4.1-8B, Llama-3.1-8B, Ministral-3-8B and Olmo-3-7B. BeliefGraph beats both prompting baselines in 17 of 18 model × dataset cells (long dossiers, ProofWriter, STALE v2).

**Cost** (MQuAKE-T, 443 memories):

| | BeliefGraph | Whole store in prompt |
|---|---|---|
| Input tokens per update | ~1.4k | ~59k |
| Seconds per update | ~3.5 | ~196 |

The one-time graph build costs ~4–5k input tokens per memory. From about 140 memories on, BeliefGraph uses fewer tokens in total than putting the whole store in the prompt.

**Where it does not help:**

- **Very small memories** (~12 items). Putting the whole store in the prompt is as accurate and cheaper there.
- **Frontier models.** Claude Opus scored 0.993 with or without BeliefGraph on our first benchmark. The gain is largest for weaker models.
- **Models below about 4B.** Graph building fails.

**Mem0 and Graphiti** detect the changed fact (Mem0 changes it in 39–75% of updates) but almost never revise the conclusions that depend on it.

Full results, error analysis, ablations and caveats: [`docs/beliefgraph-results.md`](docs/beliefgraph-results.md).

**Caveats (work in progress):**

- Single runs, no confidence intervals yet.
- Benchmark quality checked by an AI review only, no human validation yet.
- Memory-system baselines run on Gemma only.

## Quickstart

```bash
git clone https://github.com/thejasrao262003/beliefGraph && cd beliefGraph
uv sync --all-extras            # Python >= 3.11; extras: anthropic, openai, gemini, embed

beliefgraph providers           # 14 providers and the environment variable each needs
export ANTHROPIC_API_KEY=...    # or OPENAI_API_KEY, GEMINI_API_KEY, ...
beliefgraph revise examples/snapshot.json --provider anthropic
```

**Self-hosted models (vLLM, Ollama, any OpenAI-compatible server):**

```bash
beliefgraph revise examples/snapshot.json --provider openai-compatible \
    --base-url http://localhost:8000/v1 --model <served-model-name>
```

`revise` prints three things:

- the graph;
- how each update was read;
- an action per memory.

`build -o graph.json` saves the graph, and `revise --graph graph.json` reuses it.

A **snapshot** is JSON with these fields:

| Field | Contents |
|---|---|
| `evidence` | `{id, observed, source, text}` facts |
| `memories` | `{id, text}` derived conclusions |
| `policies` | `{id, text}` rules |
| `updates` | `{id, observed, source, text}` |

**Python:**

```python
from beliefgraph.core import DecomposedBeliefGraph, revise
from beliefgraph.llm import make_llm

llm = make_llm("openai-compatible", model="gemma-4-12b-it", base_url="http://localhost:8000/v1")
bg = DecomposedBeliefGraph(llm, route_mode="assign")      # v0.8
graph = bg.build(snapshot)                                 # once; incremental: build(snapshot, only=[new ids])
readings, _ = bg.read_updates(snapshot)                    # one small call per update
actions = revise(snapshot, graph.justifications, graph.reliability, readings)
```

## Repository layout

| Path | Contents |
|---|---|
| `src/beliefgraph/` | **The tool:** graph building (`core.py`), prompts, retrieval, providers (`llm.py`), call cache, CLI |
| `src/beliefbench/` | **Benchmark:** scenario generator, deterministic gold labeller, natural-language renderer with leak checks, streaming harness, metrics, LLM baselines |
| `scripts/` | Experiment runners (below) and dataset converters (`convert_proofwriter.py`, `convert_mquake.py`, `convert_stale.py`) |
| `deploy/modal_qwen.py` | Serves any open model with vLLM on Modal (`BG_MODEL=<hf id>`) |
| `data/rendered/` | Benchmark scenarios and converted datasets (system and eval views) |
| `data/beliefgraph/` | Every run's results and cached model calls, so runs replay for free |
| `docs/` | Results, renderer design and continuity report |

**Experiment runners in `scripts/`:**

| Runner | What it runs |
|---|---|
| `run_stream.py` | BeliefGraph, whole-store and RAG |
| `run_mem0.py` | Mem0 baseline |
| `run_graphiti.py` | Graphiti baseline |
| `run_ladder.py` | All models |
| `diagnose_stores.py` | Gold graph and reading swaps |

## Reproducing

Cached model calls are committed, so re-running an experiment with the same settings replays from cache and needs no model access. To run new calls against self-hosted models:

```bash
uv sync --all-extras --all-groups
BG_MODEL=google/gemma-4-12B-it uv run --group modal modal deploy deploy/modal_qwen.py
# .env (git-ignored): BELIEFGRAPH_VLLM_KEY, BELIEFGRAPH_VLLM_URL, BELIEFGRAPH_MODAL_WORKSPACE
uv run --all-extras python scripts/run_stream.py --provider modal --model gemma-4-12b-it \
    --base-url $BELIEFGRAPH_VLLM_URL --algo v0.2 --variant v0.8 \
    --runs long-s300-p0 long-s300-p1 long-s300-p2 long-s300-p3 long-s300-p4 --per-scenario --rag
```

**Tests:** `uv run --all-extras --all-groups pytest -q`.

**Data sources:**

| Dataset | Source | License |
|---|---|---|
| ProofWriter | Tafjord et al., 2021, via the `tasksource/proofwriter` mirror | per the original release |
| MQuAKE-T | Zhong et al., 2023 | MIT |
| STALE | STALEproj/STALE | CC-BY-4.0 |
| Long dossiers | generated here; text rendered with Gemini 3.5 Flash | this repository's license |

## License

MIT, see [`LICENSE`](LICENSE). Converted third-party datasets keep their original licenses.
