# BeliefGraph results

## v0 on the 63 accepted scenarios (2026-10-20)

**Setup:**
- **System:** `beliefgraph` v0 (`bg-build-v1`, `bg-read-v1`); the LLM-direct baseline is `llm-direct-v1`.
- **Model:** Claude Opus 5.5 via Lyzr (`anthropic/claude-opus-5-5`), for both BeliefGraph and LLM-direct.
- **Scenarios:** the 63 accepted scenarios from `pilot40-render-v10`, `validate-v11`, `validate-v11-f3-retry` and `validate-v12`. 301 memories are scored.
- **Run:** `scripts/run_beliefgraph.py --provider lyzr --model anthropic/claude-opus-5-5 --run bg-opus55-v1`.
- **Spend:** $2.23 under a $4.00 cap, plus $0.31 for the first 12-scenario run (cached and reused). Outputs are in `data/beliefgraph/bg-opus55-v1/` (raw responses, `predictions.json`, `results.json`).
- **Harness check:** with the gold graph and gold update readings, BeliefGraph's `revise` reproduces gold on all 63 scenarios (a test).

| System | Accuracy | Macro-F1 | Stale | Over-invalidation |
|---|---|---|---|---|
| **BeliefGraph (P)** | **0.990** | 0.986 | 0.010 | 0.010 |
| P + gold graph | 1.000 | 1.000 | 0 | 0 |
| P + gold update readings | 0.990 | 0.986 | 0.010 | 0.010 |
| **LLM-direct** (same model, no graph) | **0.993** | 0.994 | 0 | 0.010 |
| Naive cascade (gold graph) | 0.528 | 0.269 | 0 | 0.365 |
| Direct-only (gold graph) | 0.674 | 0.201 | 1.000 | 0 |

**BeliefGraph components:**
- **Graph built from text:** justification-set F1 0.994; edge F1 0.998; AND/OR typing 0.986; exact node match 0.990.
- **Update reading:** exact (target, relation, reliability) 0.917.
- **Source reliability:** 0.865. Reading errors never changed an outcome here.
- **By family, P vs LLM-direct accuracy:** F1 1.00 / 1.00; F2 1.00 / 1.00; F3 0.974 / 0.974; F6 0.987 / 1.00.

**Every error:**
- **validate-v11 F6-008, P only.** BeliefGraph found no justification for D1, whose memory "listed in the commercial drone registry" names its policy's outcome "municipal fleet catalog" only loosely (noted in review). With no justification found, `revise` treats a memory as standing (keep); gold is uncertain. **Design flaw:** unsupported memories should be surfaced, not assumed to stand.
- **validate-v12 F3-009, P and LLM-direct, identically.** The policy "A, B, C and D, or alternatively E" was read by both as A ∧ B ∧ C ∧ (D ∨ E); the generator meant (A ∧ B ∧ C ∧ D) ∨ E. The grouping is genuinely ambiguous, so this is **benchmark label noise** that the review (Claude's, C10) missed.

**Reading:**
- On these scenarios (3–12 memories, explicit policies, 1–4 updates) **a frontier model revises as accurately by re-reading everything as BeliefGraph does through its graph**. H2 (Pareto dominance) holds against the no-LLM baselines but **not against LLM-direct**.
- RQ3 is answered for this setting: building the graph costs almost nothing in accuracy. That is also why this benchmark cannot separate the two approaches.
- The graph's possible advantages lie where re-reading breaks down. These are untested so far:
  1. large memory stores and long update streams;
  2. per-update cost (BeliefGraph reads only the update, while LLM-direct re-reads the whole store);
  3. weaker or cheaper models;
  4. auditability: which facts each decision rests on.

## v0.1: model × method (2026-10-20)

**v0.1 change:**
- A memory the graph builder leaves without any justification is asked about once more on its own (`bg-build-retry-v1`).
- Any memory still unsupported is reported, not silently kept.
- The harness adds a paired exact McNemar test, a scenario-level bootstrap 95% CI, and cost per method counted from every call.

**Runs:**
- **Opus 5.5:** `bg-opus55-v1`, rescored under v0.1. The cached calls were reused and only the retry was new, at $0.034. v0 results are kept as `results-v0.json`.
- **Haiku 5.5:** `bg-haiku55-v01` (all 63 scenarios), $0.13 for the run plus $0.0013 to complete one scenario that a call cap too small for the retry step had skipped (the cap has since been fixed).
- **Settings:** both via Lyzr, with Haiku 5.5 priced at $0.10/$0.50 per M tokens (Claude API reference). The same prompts, scenarios and label definitions were used for both methods.

| Model | Method | Accuracy | Macro-F1 | Stale | Over-inv. | Uncertain recall | Est. cost (63 scen.) |
|---|---|---|---|---|---|---|---|
| Opus 5.5 | **BeliefGraph** | **0.993** | 0.994 | 0 | 0.010 | 1.00 | $1.74 |
| Opus 5.5 | LLM-direct | 0.993 | 0.994 | 0 | 0.010 | 1.00 | $0.83 |
| Haiku 5.5 | **BeliefGraph** | **0.980** | 0.968 | 0.020 | 0.010 | 0.95 | **$0.083** |
| Haiku 5.5 | LLM-direct | 0.917 | 0.822 | **0.112** | 0 | 0.63 | $0.041 |

**Paired, BeliefGraph minus LLM-direct, 301 memories:**
- **Opus:** 0.000 (0 discordant memories; McNemar p = 1.0). The predictions are identical. The only error left is the ambiguous F3-009 policy, which both systems read the same way.
- **Haiku:** **+0.063, 95% CI [+0.013, +0.120]**. BeliefGraph right and LLM-direct wrong on 23 memories, the reverse on 4; **McNemar exact p = 0.0003**.

**Haiku accuracy by family (BeliefGraph / LLM-direct):**
- **F1** (chains): 0.987 / 0.987.
- **F2** (multiple supports, OR): **1.000 / 0.803**.
- **F3** (AND + alternative): 0.948 / 0.961.
- **F6** (ambiguous or weak updates): **0.987 / 0.909**.

**Haiku's BeliefGraph components:**
- graph set-F1 0.938, AND/OR typing 0.986;
- update reading exact 0.80;
- 2 memories still unsupported after the retry.
- Isolating each step: a perfect graph gives 0.993 (P-oracle-graph); perfect update readings give 0.987.

**Reading:**
1. **The graph's advantage depends on the model.** A frontier model re-reads small memories as well as the graph propagates; a smaller model does not. Haiku-direct mainly **leaves conclusions stale** (11% vs 2%) and **misses "uncertain"** (recall 0.63 vs 0.95). Its largest losses are in F2, where it must notice that *every* alternative support is gone, and in F6, where weak-source updates should leave conclusions uncertain rather than kept.
2. **Building the graph is easier than revising directly.** Haiku builds an imperfect graph (set-F1 0.94), but propagation over it still beats Haiku reasoning over the whole memory at once.
3. **Cost:** on these small stores BeliefGraph costs about 2× LLM-direct for the same model (2–3 calls vs 1). But **Haiku + BeliefGraph (0.980, $0.083) comes within 1.3 points of Opus (0.993) at about one-tenth of Opus-direct's cost ($0.83) and one-twentieth of Opus + BeliefGraph's ($1.74).**
4. **Scope:** 63 small scenarios (3–12 memories, every update applied at once), one domain, one renderer. **Not yet tested:**
   - large stores and sequential update streams, where BeliefGraph reads only each update but LLM-direct must re-read everything;
   - other model families;
   - the F3 gap (Haiku-built AND sets).

## v0.1 on a self-hosted 9B model: Qwen3.5-9B (2026-10-23)

**Setup:**
- **Model and hosting:** `Qwen/Qwen3.5-9B` (Apache-2.0, released Feb 2026; thinking mode on), served by vLLM 0.21.0 on one Modal H100 (`deploy/modal_qwen.py`), through BeliefGraph's `modal` provider.
- **Run:** `scripts/run_beliefgraph.py --provider modal --model qwen3.5-9b --workers 16 --run bg-qwen35-9b-v01`. Same 63 scenarios, prompts and scoring as for Opus and Haiku.
- **Cold start fixed from 17+ min to 4 min:** `--gdn-prefill-backend triton` (Qwen3.5's Gated-DeltaNet layers otherwise JIT-compile a FlashInfer kernel on every boot), all caches on volumes, `--max-model-len 65536`.
- **Parser fix:** a small-model answer once put an object where an id belonged; `parse_graph` now ignores such items (tested).

| Model | Method | Accuracy | Macro-F1 | Stale | Over-inv. | Uncertain recall |
|---|---|---|---|---|---|---|
| Qwen3.5-9B | **BeliefGraph** | **0.970** | 0.945 | 0.051 | 0.010 | 0.79 |
| Qwen3.5-9B | LLM-direct | 0.834 | 0.657 | 0.092 | 0.025 | 0.58 |

- **Paired (301 memories):** **+0.136, 95% CI [+0.067, +0.210]**. BeliefGraph right and LLM-direct wrong on 48 memories, the reverse on 7; **McNemar exact p = 1.3 × 10⁻⁸**.
- **By family (BeliefGraph / LLM-direct):** F1 0.987 / 0.855, F2 1.000 / 0.817, F3 0.948 / 0.805, F6 0.948 / 0.857. BeliefGraph is better in every family.
- **BeliefGraph components:**
  - graph set-F1 0.818, AND/OR typing 0.978;
  - update reading exact 0.75;
  - 5 memories still unsupported after the retry.
  - With a perfect graph P reaches 0.993; with perfect update readings, 0.977. Graph building is Qwen's main error source, yet the imperfect graph still beats direct revision by 13.6 points.
- **Tokens:** BeliefGraph 145k in / 567k out over 138 calls; LLM-direct 77k in / 414k out over 63 calls. Output is mostly thinking.

### Model × method summary (63 scenarios, 301 memories)

| Model | BeliefGraph | LLM-direct | Paired difference | McNemar p |
|---|---|---|---|---|
| Claude Opus 5.5 | 0.993 | 0.993 | 0.000 | 1.0 |
| Claude Haiku 5.5 | 0.980 | 0.917 | +0.063 [+0.013, +0.120] | 3 × 10⁻⁴ |
| Qwen3.5-9B | 0.970 | 0.834 | **+0.136 [+0.067, +0.210]** | 1 × 10⁻⁸ |

**Reading:**
- **The weaker the model, the larger the gain from an explicit graph.** BeliefGraph lets a 9B open model revise beliefs nearly as well as a frontier model (0.970 vs 0.993), while the same 9B model asked directly reaches only 0.834.
- **Building a graph is a better use of a small model than reasoning over the whole memory at once.** Its graphs are imperfect (set-F1 0.82) but propagation over them is robust.
