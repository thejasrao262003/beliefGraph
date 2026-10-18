# Renderer design: natural-language scenarios (for approval)

*Status: design + model-free implementation, 2026-10-18. **No model calls have been made.** Nothing runs until the decisions in §9 are approved.*

## 1. Question

> Can we reliably generate natural-language scenarios that preserve the intended AND/OR justification structure, without making that structure obvious to the evaluated system?

This is a validation of the rendering process, not an evaluation of any revision method. If it fails, no downstream result on the implicit track is trustworthy.

Scope: 40 scenarios (pilot suite, seed 0, 10 each of F1, F2, F3, F6; 2 domains). The ≥ 100-scenario evaluation pilot (25 per family) has a **separate budget** (§8B) and needs its own approval.

The generator, labeller and metrics are unchanged. The renderer is a separate module, `src/beliefbench/render/`, with its own tests (`tests/test_render.py`).

## 2. Model

| | Choice | Why |
|---|---|---|
| Renderer | **`gemini-4-argon`** (Google) | Strongest available model from a family we do *not* plan to evaluate. Rendering fidelity (C2/C3 below) is the hard part, and the cost difference from Flash is a few dollars at this scale |
| Fallback | `gemini-3.8-flash` | If Argon is unavailable, or for cheaper regeneration |
| Evaluated systems (later) | Anthropic Claude + one open-weights model (spec §4.7) | **Must exclude Google models**, so the renderer and the system under test never share a family |

Recorded per call: the requested model id, the `modelVersion` returned by the API, the prompt version (`render-v1`), a hash of the payload, temperature, the thinking budget, and token usage. Settings: temperature 1.0 (we want lexical variety), JSON response mode, thinking budget capped at 8,000 tokens, and one call per scenario (the whole scenario at once, so the world stays coherent). Raw responses are cached by `(scenario, prompt version, model, payload hash)`, so a rerun never re-bills.

## 3. Input, output, and separation

**Renderer input** (`render/prompt.py: renderer_payload`): domain; evidence ids with reliability; derived ids with kind (belief/decision) and justification sets; updates with target, relation and reliability; and a *group* number per node (its connected component, so distractors are written about unrelated entities). **Not included:** gold labels, family name, meta, or any hint of which nodes are distractors other than the group number.

**Renderer output** (validated by `parse_response`): a one-sentence world; text for every node; a source description for every evidence item and update; and one rationale sentence per justification set. Structural errors (missing ids, wrong rationale count, extra ids, invalid JSON) trigger a retry with the errors fed back.

**Two files per scenario, never mixed** (`render/views.py`):

| System view: given to the evaluated system | Eval view: scoring and human review only |
|---|---|
| opaque scenario id (`s_<hash>`), domain | source scenario id, family, meta |
| evidence: opaque id (`e_xxxx`), date, source, text | id map (original ↔ opaque) |
| memories: opaque id (`m_xxxx`), text, **in random order** | gold actions, justifications (opaque ids) |
| updates: opaque id, date, source, text | update target / relation / reliability, world, rationale |

Two structural leaks are removed in the view layer:
- **Generation order.** Memories are shuffled, and evidence gets a random timeline.
- **Distractor timing.** The frozen generator creates distractor evidence after the updates, so distractors would be the only evidence dated after an update. In the view, all updates follow all evidence. A guard re-runs the labeller on the re-timed scenario and **refuses** any scenario whose gold labels change; this is tested for outdated updates.

The future evaluation harness loads only `system/`; `eval/` is read only by the scorer.

## 4. Prompt

The full text is in `render/prompt.py` (`SYSTEM_PROMPT`, version `render-v1`). Key rules:
- For every justification set, its facts *together* suffice, and *each* fact is necessary. Alternative sets each suffice on their own and use genuinely different facts. Different groups are about unrelated entities.
- Memory text states the conclusion only. It never explains why, cites sources, or counts them (an explicit banned-word list, e.g. because, therefore, based on, both, either, independently).
- Don't copy a fact's wording into a conclusion; vary sentence structure.
- Updates speak only about their target: retracts / supersedes with a new specific value / hedges. Source descriptions match reliability (high = authoritative, low = anonymous / unverified).
- No node ids or label words in any text; every text under 40 words.
- **No few-shot examples**, deliberately: an example would become the template.

## 5. Automated leakage checks (`render/leakcheck.py`)

Each check either blocks acceptance or only flags the scenario for review:

| Check | What it flags | Effect |
|---|---|---|
| Graph ids / label words | `E1`, `B2`, `m_3fa2`…; premise, justification, dependency, gold, withdraw, recompute, supersede, node | **Hard**: must be zero in accepted scenarios. Regenerate |
| Unexpected keys in the system view | anything beyond scenario / domain / evidence / memories / updates | **Hard** |
| Memory explains its reason | because, since, therefore, based on, according to, due to, supported by… | Soft: reviewer decides (C7) |
| Memory mentions sources | "both reports", "two sources", "independently", "evidence", "records show" | Soft (C7) |
| Update states an implication | "which means", "therefore", "no longer recommend" | Soft (C4) |
| **Lexical structure recovery** | A bag-of-words heuristic predicts each memory's premises from token overlap using the system view only, scored with the frozen `ExtractionScore` | **Suite gate (prespecified):** justification-set F1 ≤ 0.50 on the accepted set. If word matching recovers the graph, the benchmark measures matching, not inference. The heuristic is also the floor any LLM extractor must beat |
| Premise-overlap AUC | P(a true premise overlaps its conclusion more than a non-premise does). 0.5 = no lexical signal | Reported only. Shared entity names legitimately push it above 0.5, as you noted. Scenarios at AUC = 1.0 are reviewed first |
| Template repetition | content trigrams in > 25% of memory texts across ≥ 8 scenarios | Soft: if present, revise the prompt |

Known limit: these checks are lexical. A semantic cue an LLM could exploit (for example, a conclusion that paraphrases only one of its alternative supports) is only caught by human check C7. The definitive test of "structure not obvious" is the induced-edge experiment itself.

## 6. Human review (`render/review.py`)

The sheet per scenario shows **the system view first** (judge C7 blind), then the intended structure, gold labels, rationale, and the automated flags. Decisions are recorded in a CSV, and a failed item requires a reason (enforced by `read_decisions`).

| Item | Check |
|---|---|
| C1 meaning | Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan) |
| C2 AND | Within each set, the facts together entail the conclusion, and dropping any one breaks it |
| C3 OR | Each alternative set alone entails the conclusion, using genuinely different facts |
| C4 updates | Each update matches its relation (retract / supersede with a new value / hedge), speaks only about its target, and its source matches its reliability |
| C5 sources | Evidence source descriptions match reliability |
| C6 distractors | Different groups are unrelated |
| C7 no reveal | Reading the system view alone, the wording doesn't reveal which facts support which memory beyond what the meaning implies |

Decision per scenario: **accept**, **revise** (regenerate with the reviewer's notes, at most 2 times), or **reject**.

Procedure:
- The primary reviewer checks all 40.
- A second reviewer independently checks ≥ 10 of them, and we report Cohen's κ on the accept decision and on C2/C3.
- If no second reviewer is available, that is recorded as a limitation, not hidden.

## 7. Success criteria (prespecified)

The renderer passes if **all** of these hold on the 40 scenarios:
1. ≥ 90% accepted after at most 2 regenerations. (First-attempt acceptance is reported but not gated.)
2. 0 hard leakage flags in accepted system views.
3. Lexical-heuristic justification-set F1 ≤ 0.50.
4. No unresolved template-repetition flags.
5. If a second reviewer exists: κ ≥ 0.6 on accept decisions.

**If it fails:**
- Revise the prompt (`render-v2`, with the change documented) and rerun within the remaining budget.
- If two prompt versions fail, stop and reconsider the approach. One option is templated rendering over a hand-written lexicon: more leakage risk, but full control.

## 8. Cost estimate

Built from the real prompts (`scripts/render_cost_estimate.py`). Assumptions:
- Prices: official Gemini pricing page, last updated 2026-10-16.
- Input tokens: chars ÷ 4, ±25%.
- Visible output: estimated from the schema.
- Thinking tokens: 2,000 expected, 8,000 upper bound (cap).
- Calls per scenario, including retries: 1.3 expected, 3.0 upper bound.

**A. Renderer validation pilot: 40 scenarios** (~1,160 input + ~1,200 visible output tokens per call)

| Model | Price (per 1M in / out) | Expected | Conservative upper bound |
|---|---|---|---|
| `gemini-4-argon` | intro, until 2026-11-30: $2 / $10 | **$1.79** | $11.32 |
| `gemini-4-argon` | from 2026-12-01: $4 / $20 | $3.57 | **$22.64** |
| `gemini-3.8-flash` | intro, until 2026-12-31: $0.75 / $3.75 | $0.67 | $4.24 |
| `gemini-3.8-flash` | from 2027-01-01: $1.50 / $7.50 | $1.34 | $8.49 |

**B. Evaluation-pilot rendering: 100 scenarios (separate budget, later approval)**

| Model | Price | Expected | Upper bound |
|---|---|---|---|
| `gemini-4-argon` | intro | $4.42 | $28.20 |
| `gemini-4-argon` | after intro | $8.84 | $56.40 |

**Not included:** evaluated-system calls, judge calls, and any optional LLM entailment pre-screen. Each needs its own estimate and approval.

**Spend cap:** the client (to be written after approval) totals the billed tokens from each response's usage metadata and stops before exceeding the approved cap.

## 9. Decisions needed before any model call

1. **Renderer model:** `gemini-4-argon` (recommended) or `gemini-3.8-flash`.
2. **Budget cap for A:** recommended **$25**, which covers the Argon upper bound even at post-intro prices.
3. **Evaluated families:** confirm no Google models (planned: a Claude model + one open-weights model).
4. **API access:** a Gemini API key available as `GEMINI_API_KEY` in the environment, never committed.
5. **Second reviewer:** who, if anyone, for the κ subset.

## 10. Smoke test 1 (2026-10-18): 4 scenarios, `render-v1`, `gemini-2.5-flash` via Lyzr

Command: `uv run --group lyzr python scripts/render_run.py --run smoke-render-v1 --limit 4 --budget-usd 0.25`. Outputs are in `data/rendered/smoke-render-v1/`.

- **Mechanics:** 4/4 rendered; 3 on the first attempt, 1 retry (F6). 5 calls. Conservative estimated spend **$0.11**, assuming the full 8k thinking allowance on every call. Lyzr's response metadata reports **no token usage**, so actual spend must be read from the Lyzr dashboard.
- **Automated checks:** 0 hard / 0 soft flags in accepted renderings; lexical-heuristic justification-set F1 **0.22** (gate ≤ 0.50); premise-overlap AUC 0.70; no template trigrams.

Pre-review by Claude (not the human review the protocol requires) found problems the automated checks don't catch:

| # | Problem | Example | Fix proposed for `render-v2` |
|---|---|---|---|
| P1 | **AND/OR structure is not recoverable from the system view.** The rule that makes facts jointly necessary or alternatively sufficient lives only in the hidden rationale, so gold labels are undeterminable from the text. Invalid for the implicit track | F3: (clean record ∧ credit 750) ∨ (Civic with safety features) → insurance eligibility. After credit → 680, nothing visible says the Civic alone suffices | Add a **policy** text per derived node, visible to the system: the general rule (conditions, AND within / OR across) stated about *kinds* of facts, never about specific evidence items. The task becomes "link stored conclusions to policies and facts", which is how real agents derive conclusions. The lexical gate still applies |
| P2 | Hidden reliability label leaked into source fields | F6 sources `high` / `low`; F3 "Site Survey Report, high" | Prompt: never write the reliability word. New **hard** check on source fields for `high|medium|low` as a bare label |
| P3 | Hard-flag false positive cost a retry | F6 attempt 1 rejected for "Gold" (a card tier) | Make `gold` a soft flag (natural word, low leak risk) |
| P4 | Distractor about the same entity as the main chain (C6) | F6 "Platinum Member Club" belief about the same customer | Prompt: each group uses distinct named entities; never "the customer" unnamed |
| P5 | Absolute dates in text conflict with view dates | Texts say October 2026, view dates are Jan 2026 | Prompt: no calendar dates or years in texts (relative time only) |
| P6 | Chain order leaked through ordinal wording | F1: initial → preliminary → advanced → fully qualifies | Prompt: no stage/sequence words that encode derivation order. Soft check for them |

**Status:** do not render the 40 with `render-v1`. P1 changes what the evaluated system sees, so it is a design decision for approval.

## 11. Model update (2026-10-18): `gemini-3.5-flash` via Lyzr

`gemini-2.5-flash` (smoke test 1) is outdated. Lyzr's live catalogue (`GET /v3/providers/type?provider_type=lyzr-llm`) ranks the Google models by intelligence index:

| Model | Index | Tier |
|---|---|---|
| **`gemini-3.5-flash`** | **33** | balanced |
| `gemini-3.1-pro-preview` | 30 | high reasoning |
| `gemini-3-flash-preview` | 26 | balanced |
| `gemini-2.5-flash` | 13 | balanced |

The renderer now defaults to **`gemini-3.5-flash`**.
- **SDK workaround:** lyzr-adk 0.1.12's local registry predates it, so `register_gemini_model` adds it at runtime, with the same Google / `lyzr_google` mapping the SDK uses for 2.5 Flash.
- **Live check:** `render_run.py` refuses to run a model that isn't in the live catalogue.
- **Spend guard price:** proxied at $1.50 / $7.50 per 1M (gemini-3.8-flash post-intro list price), because Google's pricing page has no "3.5 Flash" entry. That puts the worst case for the 40-scenario run at ~$3.7 per attempt round.

For the later evaluation, the top models by provider in the same catalogue: Anthropic `claude-opus-5-5` (58) / `claude-sonnet-5-5` (56); OpenAI `gpt-6-astra` (53); open-weights `groq/openai/gpt-oss-120b` (12) and `groq/moonshotai/kimi-k2-instruct` (15).
