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
