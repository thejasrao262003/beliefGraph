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

## 12. Smoke test 2 (2026-10-18): 4 scenarios, `render-v2`, `gemini-3.5-flash` via Lyzr

Command: `uv run --group lyzr python scripts/render_run.py --run smoke-render-v2 --limit 4 --budget-usd 0.50`. Outputs are in `data/rendered/smoke-render-v2/`.

**Run facts**
- The live catalogue check passed at run time: `gemini/gemini-3.5-flash`, balanced tier, index 33, credential `lyzr_google`, `reasoning_effort` default `medium`.
- **Lyzr does report token usage**, in `raw_response` (`prompt_tokens`, `completion_tokens`). Smoke test 1 missed it because the client discarded `raw_response`.
- Usage: 8,967 input + 12,107 output tokens over 4 calls. **$0.104 at the proxy price; the guard charged $0.156** (with the 1.5× safety factor). Actual Lyzr credit cost must still be checked in the dashboard.
- 4/4 rendered on the first attempt, 0 hard flags.

**Smoke-test-1 problems: all resolved**

| | Status in v2 |
|---|---|
| P1 structure not inferable | **Fixed.** E.g. F3: the policy states "(account ≥ 2 years AND spend ≥ $200k) OR Tier-1 accreditation". After spend drops to $180k, the visible accreditation keeps the conclusion. Determinable from the system view |
| P2 reliability labels | Fixed: "Unverified community forum post" for low; authoritative registries for high |
| P3 gold false positive | Fixed (regression tested) |
| P4 same-entity distractors | Fixed: every group has distinct named entities (Boreal Health, Crestview Foods, DynaTek…) |
| P5 dates | Fixed: no absolute dates in any text |
| P6 order cues | Fixed: none present |

**New problem: P7, the policies hand over the graph lexically. The gate fails.**
- **Numbers:** the policy-assisted heuristic recovers **0.67** justification-set F1 (gate ≤ 0.50); word matching alone, 0.27. Premise-overlap AUC is 0.88.
- **Cause:** each policy restates its memory nearly verbatim in its head and its premises verbatim in its body. Example from F1:
  - memory: "Apex Tech Solutions meets enterprise security compliance criteria"
  - policy: "An account meets enterprise security compliance criteria if it qualifies for priority support routing and maintains at least two certified security officers"
  - evidence: "…maintains two certified security officers on staff"
- **Effect:** memory → policy → premises becomes string matching, which is exactly the risk raised in review. One policy per memory also makes the mapping 1:1.

**Other observations (pre-review by Claude, not the human review)**
- **F2, supersedes on a boolean fact:** "certification was formally suspended / report revoked". The gold label is `recompute`, and re-deriving under the policy flips the conclusion, so outcome-wise it equals `withdraw`. Not wrong, but scoring should treat "recompute that flips" consistently. To decide before the evaluation.
- **`policy_shares_name` is noisy:** 5 soft flags, all standard or product names (ISO, SOC, Tier, Grade), none of them the subject entity. The heuristic needs narrowing to subject names.

**Proposed `render-v3`** (needs approval before any further calls):
1. **Vocabulary separation.** Policies and memories must not reuse each other's head phrase, and policy conditions must describe requirements in category terms, not the facts' wording ("a security staffing requirement of two or more certified officers", not "maintains two certified security officers"). The C8 human check guards determinability.
2. **Decoy policies.** Per scenario, 1–2 plausible rules from the same domain that govern nothing in the scenario, so the policy-to-memory mapping is not 1:1.
3. **Narrow `policy_shares_name`** to subject entities only.
4. Re-run the same 4-scenario smoke test (expected ≈ $0.10, cap $0.50). The gate stays at ≤ 0.50 on the worse heuristic.

## 13. Smoke test 3 (2026-10-18): 4 scenarios, `render-v3`, `gemini-3.5-flash` via Lyzr

Command: `uv run --group lyzr python scripts/render_run.py --run smoke-render-v3 --limit 4 --budget-usd 0.50`. Outputs are in `data/rendered/smoke-render-v3/`. The v2 outputs are untouched; v2 replays from cache with 0 calls and identical views.

**Run facts**
- Live catalogue check passed at run time.
- 5 calls: 3 scenarios first-attempt, 1 retry (F3: the word "reliability" in a policy, caught by the hard check).
- Usage: 12,832 input + 19,357 output tokens. **$0.164 at the proxy price; the guard charged $0.247** (with the 1.5× factor). Cap $0.50. The actual Lyzr credit charge must be checked in the dashboard.

**Leakage gate (heuristics and threshold unchanged from v2):**

| | v2 | **v3** |
|---|---|---|
| Policy-assisted justification-set F1 | 0.67 (fail) | **0.41 (pass)** |
| precision / recall | 0.72 / 0.62 | 0.44 / 0.38 |
| Word-matching-only set F1 | 0.27 | 0.23 |
| Policy-assisted edge F1 | n/a | 0.61 (P 0.56 / R 0.68) |
| Premise-overlap AUC | 0.88 | 0.84 |

Below the gate is necessary, not sufficient: four scenarios is a small sample, and the 40-scenario run must re-measure it.

**Semantic consistency:** 0 `final_state_mismatch` / `recompute_unresolved` flags. The renderer's post-update state agrees with gold in all 4 scenarios: F1/F2 recompute → fails; F3/F6 alternatives hold → keep → holds.

**Pre-review by Claude** (C8–C13; *not* the human review the protocol requires):

| Scenario | C8 inferable | C10 unambiguous | C11 policy ≠ graph | C12 decoys inert | Notes |
|---|---|---|---|---|---|
| F1 chain, ARR $3.5M → $1.2M | ✓ the chain follows from the policies; the $2.5M threshold fails | ✓ | ◐ "operational risk threshold for enterprise status" is **verbatim** in a memory and two policies, violating vocabulary separation | ✓ (underwriting, hardware credit) | |
| F2 two alternatives, both superseded below threshold | ✓ ($85k < $100k, 350 < 500) | ✓ | ✓ | ✓ | |
| F3 (spend ∧ implementations) ∨ ISO 27001; spend drops | ✓ ISO keeps Gold tier | ✓ | ✓ | ✓ (Platinum decoy uses similar categories but governs no memory) | Soft flag: "Gold/Tier" in both groups (EcoVadis Gold vs Gold tier). Different entities, but lexically confusable |
| F6 OR(R&D $12M, 15 patents); low-reliability claim against R&D | ✓ patents keep it | ✓ | ✓ good paraphrase ("technical capability criteria" vs "technical distribution eligibility") | ✓ | "500 megawatts … per hour" is a unit error (C1) |

**Residual issues for the human review to judge:**
- **R1 (F1):** vocabulary separation is only partly followed.
- **R2:** the gate margin is modest (0.41 vs 0.50) on n = 4.
- **R3 (F3):** cross-group vocabulary overlap.
- **R4 (F6):** a unit error.

None changes a gold label.

**Status:** smoke tests are complete. Before the 40-scenario validation run, the human review of these 4 (`review.md` + `review.csv`) is needed. Any further calls need approval.

## 14. External review of smoke test 3, and render-v4 (2026-10-18)

**Review provenance.** The 4 v3 scenarios were reviewed against C1–C13 by **an external AI assistant, supplied by the user, not a human**. The original file is stored verbatim as `smoke-render-v3/review-external-ai.long.csv`, and converted (validated by `read_decisions`) into `smoke-render-v3/review.csv` with that reviewer recorded. **The protocol's human review is still outstanding.**

| Scenario | Verdict | Failed items |
|---|---|---|
| F1 | revise | C7, C11: "operational risk threshold for enterprise status" / "commercial stability" repeated across memory and policies |
| F2 | accept | none |
| F3 | accept | none ("Gold/Tier" judged a lexical collision, not a dependency) |
| F6 | revise | C4: the low-reliability `retracts` update *alleges* inflation rather than denying the fact; C10: "500 megawatts … per hour" |

**Inconsistency found when automating the F1 criterion.** F2 has the same pattern as F1: "standard partner tier standing" appears in its memory, in its own policy, *and* as a condition of the specialist policy, which exposes the B1→D1 link. The reviewer passed F2. The rule is now enforced mechanically and uniformly (below). Under it F2 would also need re-rendering; F3 and F6 are clean.

**render-v4** (v3 kept verbatim, pinned by SHA-256 `d20ac3c3…`; v4 = v3 + 3 asserted edits):
1. **Prompt, hard no-shared-phrase rule:** no ordinary 3-word phrase in both a memory and any policy, including policies that use another conclusion as a condition. Proper names are exempt. **Code:** `leakcheck.echo_flags`, a *hard* flag that triggers regeneration. On the stored v3 outputs it fires for F1 (3 pairs) and F2 (3 pairs) only.
2. **Prompt:** `retracts` must flatly assert falsity, even from a weak source; questioning or alleging is `hedges`. **Code:** `leakcheck.relation_flags`, a soft flag on hedge language in a `retracts` update. On v3 it fires for F6 ("claims") only.
3. **Prompt:** realistic, dimensionally correct units; policy thresholds in the same unit as the fact.

Next: re-render **F1-000 and F6-000 only**, cap $0.25 (`--only F1-000 F6-000`).

## 15. Targeted re-render (2026-10-18): F1-000 and F6-000, `render-v4`

Command: `uv run --group lyzr python scripts/render_run.py --run smoke-render-v4 --only F1-000 F6-000 --budget-usd 0.25`. Outputs are in `data/rendered/smoke-render-v4/`.

**Run facts**
- 2 calls, both accepted on the first attempt; 0 hard flags, so the no-shared-phrase rule was met without retries.
- 5,767 input + 10,677 output tokens. **$0.089 at the proxy price; the guard charged $0.133** (cap $0.25).

**Gate** (same heuristics and threshold):

| | Worse heuristic, justification-set F1 | Precision / recall |
|---|---|---|
| These 2 scenarios in v3 | (part of 0.41 overall) | |
| **v4** | **0.17 (pass)** | 0.20 / 0.15 |

Word-only heuristic: 0.09.

**Pre-review by Claude** (the human review is still required):

| Scenario | Fixed | New concern |
|---|---|---|
| F1 | No shared phrases (C7/C11); chain logic correct ($250k → $150k < $200k ⇒ chain fails, consistent with gold) | **Over-paraphrase (C8/C10):** "Qualified Enterprise Status" ↔ "premier merchant designation" and "prerequisites for enrollment" ↔ "partner registry inclusion" are hard to map with confidence. The fact's "software expenditure" vs the policy's "annual billing" may not be the same quantity |
| F6 | Units correct (dB). The update now denies the target fact ("lacks genuine ISO 13485 certification") from an unverified forum post. The soft `retraction_reads_as_hedge` flag fires on "claimed", which is natural framing for a weak source | **Decoy closer than the real policy (C12/C10):** decoy "organic retail certification" (food) is lexically closer to the Dermacool memory ("organic cosmetics formulation standards") than its real policy ("eco-friendly designation"). Sources have awkward appended tags (", signed certificate", ", user comment") |

**Reading:** v4 removes lexical shortcuts, but the paraphrase pressure can push mappings past what a careful reader can verify. The leakage gate cannot detect that; C8/C10 can. A possible v5 adjustment, *not yet made*:
- the outcome named in a policy must be a recognisable synonym of the memory's outcome, not a different concept name;
- decoys must not share a distinctive content word with any memory.

The human review of these two scenarios should decide whether this is needed.

## 16. render-v5 (2026-10-18): bounded pilot for F1, F2, F6

**Principle (adopted):** the lexical leakage score is a **diagnostic ceiling** (≤ 0.50), not an objective to minimise. A lower score obtained by making concepts harder to identify is worse, not better. The target is scenarios that are semantically clear (C8/C10), structurally inferable, and resistant to phrase matching.

v5 = verbatim v4 (SHA-256 `dd74235d…`, pinned in tests) + 2 asserted edits:

| Rule | Prompt | Automated check |
|---|---|---|
| **Outcome naming:** a policy names its outcome with a clear synonym or close paraphrase of the memory's conclusion, recognisably the same concept | ✓ | none possible lexically; **human C8/C10** |
| **Quantity naming:** a condition names the same measured quantity as its fact (revenue ≠ spending ≠ billing) | ✓ | human C10 |
| **Decoy words:** a decoy may not share a distinctive content word with any memory | ✓ | **hard** `decoy_shares_memory_word`, excluding numbers and a generic rule-word list calibrated on smoke tests 3–4. On stored outputs it fires for v4-F6 "organic", and for v3-F3 "partner/tier"/"channel" |
| No shared ordinary 3-word phrase (v4) | ✓ | hard `policy_echoes_memory`. Kept, but passing it is not evidence of semantic quality |
| Flat-denial retractions, units (v4) | ✓ | soft `retraction_reads_as_hedge` |

**Approval conditions for the 40-scenario run** (from review):
1. F1, F2 and F6 rendered under the existing cap.
2. All checks run, with complete logs kept.
3. **A human** independently reviews them against C1–C13, especially C6/C8/C10/C12.
4. That review is recorded separately from any AI review, with its provenance.
5. All three pass. A failing scenario is revised individually, and checks are never relaxed globally.

### 16a. v5 run (2026-10-18): stopped by the spend guard after F1

Command: `... --run smoke-render-v5 --only F1-000 F2-000 F6-000 --budget-usd 0.25`. Outputs are in `data/rendered/smoke-render-v5/`.

**Calls:** 2 calls, guard-charged **$0.124**; 5,817 input + 9,877 output tokens, ≈ $0.083 at the proxy price.
- F1: accepted on the first attempt.
- F2 attempt 1: rejected by the hard check.
- F2 attempt 2: **refused by the guard** (spent + worst case > $0.25).
- F6: not attempted.

The cap held. Both responses are cached and will not be re-billed.

**F1 (v5), pre-review by Claude, not the human review:** 0 hard / 0 soft flags; worse heuristic 0.17.
- **Outcome naming is now recognisable:** "clean transport operational benchmarks" ↔ "green fleet operation standards"; "eco-friendly freight carrier" ↔ "low-emission carrier"; "preferred environmental supplier ranking" ↔ "preferred eco-vendor status".
- **Quantities match:** an electric fleet of 45 vehicles ↔ an active electric transport count ≥ 30. The update to 15 vehicles breaks the chain, consistent with gold (all recompute → fails).
- Decoys (customs clearance, bulk shipping subsidy) are inert.

**F2 attempt 1, rejection cause:** `decoy_shares_memory_word: "logistic"`.
- The decoy reads "A **logistics** firm secures Executive Vendor Status…". The shared word comes from the memory's *entity name* "Apex **Logistics**", not from any outcome concept. No memory states Executive Vendor Status.
- By the stated intent ("words that create a plausible association"), this looks like a **false positive** in the check's definition: entity names were not excluded.
- **Not changed unilaterally.** Review conditions forbid relaxing checks after seeing results. Proposed refinement, for approval: exclude words of subject-entity names (`leakcheck.subject_names`) from the memory vocabulary. Outcome and programme words, e.g. "Tier-1 Freight Coverage", would still count.

### 16b. Decoy-check refinement and cumulative cap (approved 2026-10-18)

- **Refinement:** `decoy_word_flags` now strips subject-entity-name spans (`subject_names`) from each memory before comparing vocabularies. Only the *name span* is removed, so a word that also appears in a memory's outcome wording still counts.
- **Regression tests:**
  - "Apex Logistics" vs a decoy "a logistics firm…": allowed.
  - "Tier-1 Freight Coverage" vs a decoy "Tier-2 Freight Coverage…": rejected.
  - "logistics" in both the name and the outcome ("logistics excellence award"): rejected.
- **On stored outputs** the refined check still flags v4-F6 "organic", v3-F3 "partner/tier" and "channel", and v4-F1 "partner".
- **Log:** the original F2 rejection stays recorded in `smoke-render-v5/raw/` and §16a.
- **Cap accounting:** the spend guard is per-run. The approved $0.30 is applied cumulatively via `--prior-spend-usd 0.124`, leaving $0.176 of headroom.

### 16c. v5 completion run (2026-10-18): F2 and F6

Command: `... --run smoke-render-v5b --only F2-000 F6-000 --max-attempts 2 --budget-usd 0.30 --prior-spend-usd 0.124`. Outputs are in `data/rendered/smoke-render-v5b/`. F2's raw response was copied from `smoke-render-v5/raw/` and **reused from cache: no API call, $0**.

**Spend:** F6 took 1 call (3,116 in / 6,197 out tokens, $0.077 guard-charged). **Cumulative: $0.2007 of the $0.30 cap.** No retries were needed.

- **F2:** the cached attempt 1, previously rejected only by the entity-name false positive, passes all checks under the refined rule. 0 flags.
- **F6:** first attempt, 0 hard and 0 soft flags.

**Gate:** the prespecified definition is suite-level over the assessed set, using the worse of the two heuristics.

| Set | Policy-assisted set F1 | Verdict |
|---|---|---|
| This run (F2 + F6) | **0.60** | fail |
| Whole v5 pilot (F1 + F2 + F6) | 0.44 | pass |
| F1 alone | 0.17 | n/a (per-scenario diagnostic) |
| F2 alone | 0.29 | n/a |
| F6 alone | **0.77** | n/a |

Both suite numbers are reported. Neither aggregation is chosen to make the result pass.

**Diagnosis of F6:**
- Its 3 distractors are single-premise beliefs about distinct named entities, recovered by entity-name matching. That is legitimate and structural.
- **But** main-chain B2 and D1 are also recovered, because **two policies copy evidence wording verbatim**:
  - p_cd31 "valid **state pharmaceutical distribution license**" ↔ fact "active state pharmaceutical distribution license";
  - p_b3f6 "official **organic processing certification**" ↔ fact.
- The prompt has forbidden fact wording in policies since v3. The automated echo check covers memory↔policy only, so **policy↔evidence echoes are an unchecked gap**.

**F6 otherwise (pre-review by Claude, not the human review):**
- C4: the retraction is now a flat denial ("asserts … did **not** achieve $650,000") from an unverified forum post.
- C10: quantities match (purchases ↔ yearly purchases ≥ $500k).
- The ISO 13485 alternative keeps preferred-partner status, consistent with gold.
- **C11 likely fails** on the evidence-wording copies.

**Proposed** (needs approval, not applied):
- extend `echo_flags` to policy↔evidence (same hard 3-word rule, proper names exempt), with regression tests built from these two phrases;
- re-render F6 only. That needs a new cap: the remaining $0.099 is below the guard's worst case for one call ($0.14).

### 16d. Policy↔evidence echo check, AI pre-review of F2/F6, and predeclared scoring scope (2026-10-18)

**Check extension (approved):**
- `echo_flags` now also compares every policy with every evidence item. It uses the same hard 3-word rule, with capitalised spans (product, programme, standard names) exempt. Kind: `policy_echoes_evidence`.
- **Quantity phrases with a number are exempt** ("2,500 square meters" vs "1,500 square meters"). Since v4, thresholds must use the same unit as their fact, so number+unit overlap is mandated. This exemption was added *before* the check was used for any gate decision.
- Regression tests: both v5-F6 phrases are flagged; an unrelated-paraphrase control passes; a quantity phrase passes; the F2 standard-name case is pinned as not flagged.
- On stored outputs: v5 F1 and v5b F2 are clean; v5b F6 is flagged on exactly its two leaks. Older runs also show echoes (v3: "annual recurring revenue", "quality management facility"; v4-F1: "enterprise client deployments").
- **Known tension:** QUANTITY NAMING requires the same measured quantity, while the echo rule forbids repeating its 3-word name ("annual recurring revenue"). It must be named the same *in meaning*, worded differently. The v5 renders show this is achievable; human C10 guards the meaning.

**AI pre-review of v5 F2/F6** (external AI assistant via the user, **not** the human review). Stored verbatim as `smoke-render-v5b/ai-prereview-f2-f6.csv`, deliberately *not* as `review.csv`, which is reserved for the human review.

| Scenario | AI verdict | Failed items | Note |
|---|---|---|---|
| F2 | revise | C7, C11: policy "active ISO 22000 certification" echoes the evidence | **Conflicts with the documented rule:** standard names are exempt, and the policy must name ISO 22000 for C8. Not re-rendered (not in the approved scope); **for the human reviewer to decide** |
| F6 | revise | C7, C11: the two evidence-wording echoes | Agrees with the automated finding; F6 is re-rendered |

**Predeclared scoring scope for the next result** (written before the F6 re-render):
- **Pilot gate:** the worse heuristic's justification-set F1 ≤ 0.50, **pooled over the three pilot scenarios in their candidate versions**: F1 from `smoke-render-v5`, F2 from `smoke-render-v5b`, F6 from the new run `smoke-render-v5c`.
- **Diagnostic only, not a gate:** the run-level score (F6 alone) and the per-scenario scores. They are reported, not used to pass or fail.
- **Run:** F6-000 only, fresh (no cache), `--max-attempts 2`, new isolated cap **$0.20**. The v5/v5b outputs and their gate results stay untouched.

### 16e. Fresh F6 render (2026-10-18): attempt 1 rejected, retry refused by the guard

Command: `... --run smoke-render-v5c --only F6-000 --max-attempts 2 --budget-usd 0.20`. Outputs are in `data/rendered/smoke-render-v5c/`.

**Run facts**
- Attempt 1: 3,116 in / 5,364 out tokens, **$0.067** guard-charged.
- Rejected by **5 hard `policy_echoes_evidence` flags**.
- The retry was **refused by the guard**: $0.067 spent + $0.141 worst case > $0.20. **0 scenarios rendered.**
- The cap held. The rejected response is cached.

**Rejection cause:** each echo is the policy reusing the fact's *name for the quantity or credential*:
- "gross annual revenue"
- "fleet-wide average carbon emission level"
- "converted … to electric vehicles"
- "certified annual carbon offset"
- "active corporate membership"

The v5 prompt already says conditions must be "never in the fact's words", but the model does not comply when naming a measured quantity.

**Finding:** the echo rule and determinability (C8/C10) pull against each other. The most natural unambiguous reference to a fact is its own name for the quantity. The retry path sends the exact echoed phrases back as feedback, but the guard's worst-case assumption (12,000 output tokens; observed completions 3.7k–6.2k) leaves no room for it under $0.20.

**Options for decision (none applied):**
- **A.** Allow one retry with feedback: a new isolated run reusing the cached attempt 1 for free, with the cap raised so that $0.067 + one worst-case call fits (≥ $0.21; e.g. $0.25 cumulative).
- **B.** render-v6: promote "no fact wording in policies" to an explicit HARD RULE in the prompt, mirroring the memory rule, then re-render F6 (≈ $0.07 expected, same cap logic).
- **C.** Revisit the rule: allow the *quantity / credential name* to be shared (as standard names and number+unit phrases already are), and rely on human C7/C11 for genuine leaks. This would relax a check after seeing results, so it needs an explicit decision.

### 16f. render-v6 and the single approved F6 retry (2026-10-18)

- **Prompt:** render-v6 = verbatim v5 (SHA-256 `d8368d88…`, pinned) + one asserted edit: "HARD RULE (facts)".
  - No ordinary 3-word phrase may be shared by an evidence item and a policy.
  - Refer to the fact's quantity or credential by a clear, unambiguous equivalent ("gross annual revenue" → "yearly turnover"), never a vague one.
  - The proper-name and number+unit exemptions are unchanged.
- **Retry mechanics:** new run `smoke-render-v5d`.
  - **Attempt 1** = the rejected v5c response, copied unchanged. Its record keeps `prompt_version: render-v5`. It is stored under the v6 cache key so the pipeline reuses it with **no API call**.
  - **Attempt 2** = one v6 call, carrying the attempt-1 rejection feedback (the 5 echoed phrases).
- **Cap:** `--max-attempts 2 --budget-usd 0.25 --prior-spend-usd 0.067`, leaving $0.183 of headroom. The guard stays authoritative.

### 16g. Result of the single approved F6 retry (2026-10-18): rejected; stopped as instructed

`smoke-render-v5d`:
- **Attempt 1:** the cached v5c response (render-v5), $0.
- **Attempt 2:** render-v6 with feedback. 3,409 in / **9,097 out** tokens, **$0.110** guard-charged.
- **F6 cumulative: $0.177 of the $0.25 cap.** 0 scenarios rendered. No further calls; no exemption added; no new prompt version.

**Hard failures of attempt 2:**

| Flag | Phrases | Assessment |
|---|---|---|
| `policy_echoes_evidence` | fact "85 **g/km across all** trucks" ↔ policy "under 90 **g/km across all** vehicles" ("g km across", "km across all") | Tokeniser edge: "g/km" splits into "g" + "km", so the existing number+unit exemption (which needs a digit inside the 3-gram) does not apply. Same class as the exempted unit overlap. Covering it **would be a new exemption** and is not applied |
| `decoy_shares_memory_word` | decoy "upfront **security** deposits" ↔ memory "corporate IT **security** prerequisites" | Same word, different sense; weak association. A hit under the rule as defined |

**Semantic quality** (pre-review by Claude, not the human review), the risk named in the approval:
- **D1 policy:** "audited annual **balance credits** of 5,000 metric tons" for the fact "verified yearly **carbon offsets** totaling 10,000 metric tons". This is a vague replacement of a clear quantity and would likely fail **C8/C10** even if all automated checks passed.
- **B3:** "total annual income" for "gross yearly earnings" is borderline.
- **Fine:** B1 ("four-fifths of its transport vehicles" for 80 percent) and B2 ("continuous corporate standing within an accredited freight consortium" for paid membership).
- Soft: the retraction reads "A blog entry **claims** … **never** converted…", which is a flat denial in reported speech.
- Diagnostic only: F6 alone, worse heuristic 0.62.

**Reading:** under the strict lexical rules, F6 (one chain plus three single-premise distractors, many named quantities) pushes the renderer either into echoes or into vague paraphrase. Raising the lexical bar further is unlikely to produce a scenario that passes C8/C10. **Decision needed.** The pooled pilot gate cannot be computed until a final F6 exists.

### 16h. Decision on F6 and the pilot (user, 2026-10-20)

| Item | Decision |
|---|---|
| Third F6 model call | **Not approved.** The approval covered one retry and required stopping if it failed. A third attempt would be a new experiment, and the remaining $0.073 is a ceiling, not budget to spend |
| New lexical exemptions (e.g. `g/km` unit tokens, word-sense decoy hits) | **Not approved for this pilot** |
| Policy↔evidence echo check | **Unchanged** for the frozen pilot. Changing it after two observed failures would alter the acceptance criteria post hoc |
| F6 | **Failed / unresolved.** Excluded from the accepted pilot set. Both attempts (`smoke-render-v5c`, `smoke-render-v5d`) and their rejection reasons stay in the trail |
| F1, F2 | Proceed to **human review** independently. Being sent to review is not passing it |
| 40-scenario run | **Blocked** until the required human reviews and acceptance gates are complete |

**Effect on the predeclared gate (§16d):** the pooled gate was declared over F1 + F2 + F6. With F6 excluded, that gate **cannot be evaluated as declared**. It is not silently re-scoped to F1 + F2. Any new scope must be declared before it is scored.

**Human review packets:**
- **F1:** `smoke-render-v5/review.md` → record in `smoke-render-v5/review.csv`. The AI pre-assessment (chain consistent with the fleet update) is not a verdict.
- **F2:** the `s_3d821bdd07` section of `smoke-render-v5b/review.md` → record in the F2 row of `smoke-render-v5b/review.csv`. Leave the F6 section and row (`s_c41a0870a2`) blank, because F6 is excluded. **Reviewer to adjudicate explicitly:** whether the policy wording "active ISO 22000 certification" against the evidence "active ISO 22000 food safety management certification" fails C7 or C11. The standard name is exempt by the documented rule and is needed for C8. The AI pre-review (`ai-prereview-f2-f6.csv`) says it fails.

**Candidate design for the next renderer revision** (recorded only; needs new explicit approval before any implementation or model call):
- **Hard structural checks:** policy→memory leakage and the other directly prohibited disclosures.
- **Soft lexical flags:** policy↔evidence overlap, surfaced for human judgement under C7 and C11 rather than rejecting the render. Shared technical terms (`g/km`, "carbon offsets", a named certification) are not inherently structural leaks, and a phrase-overlap check is only a proxy.
- **Measured leakage:** the predeclared pooled gate over the declared scenario set.
- **Semantic quality:** C8 and C10, which no lexical score replaces. F6 attempt 2 shows that a render can pass the automated checks while getting harder to interpret ("balance credits" for "carbon offsets").
- **Scenario design:** consider an F6 variant with fewer independent named quantities.

### 16i. F1 human review recorded (2026-10-20)

- **Result:** `smoke-render-v5/review.csv`, reviewer `thejasrao262003`: all 13 checks pass; decision **accept**.
- **Provenance:** an AI assistant drafted the analysis. The user reviewed F1 against C1–C13 and confirmed it as their own verdict.
- **Normalised to the validator's format:** C3 "N/A" became `pass` (vacuous, since there are no OR sets); the decision "PASS" became `accept`.
- **Notes cover:** C3, C4 and C13 only. C7, C8, C10 and C11 pass without specific notes.
- **Still open:** F2 human review (with the ISO 22000 C7/C11 question). The gate stays unscored: F6 is excluded, and the predeclared F1+F2+F6 scope is not re-scoped. The 40-scenario run stays blocked.

### 16j. F2 human review recorded (2026-10-20)

- **Result:** the `s_3d821bdd07` row of `smoke-render-v5b/review.csv`, reviewer `thejasrao262003`: all 13 checks pass; decision **accept**. The F6 row (`s_c41a0870a2`) is left blank on purpose, since F6 is excluded, so only the F2 row was validated with `read_decisions`.
- **Decision value:** the user gave verdicts for all checks but did not state a decision. `accept` was recorded because every check passed.
- **ISO 22000 adjudication:** C7 and C11 both pass. The policy names the standard but not the entity, and does not point to `e_dfe6`. The name is needed for C8 and is covered by the existing standard-name exemption. The overlap is lexical, not structural. **This overrules the AI pre-review** (`ai-prereview-f2-f6.csv`), which failed both checks.
- **Pilot status:** F1 and F2 are both human-accepted. F6 is excluded. The predeclared pooled gate (F1+F2+F6, §16d) **remains unscored**. Scoring F1+F2 alone would be a new scope and needs to be declared and approved first. The 40-scenario run stays blocked.

## 17. render-v7 revision and pilot-2 proposal (2026-10-20)

**Approved by the user on 2026-10-20:** the renderer revision and its design work (below). **Not approved:** any model call or spend. Pilot-1 stays recorded as it is in §16h–16j: F1 accepted, F2 accepted, F6 excluded, the pooled gate unscored. Nothing in this section relabels pilot-1.

### 17a. Implemented (model-free; 87 tests pass)

| Layer | Change | Where |
|---|---|---|
| **Hard structural checks** | Unchanged: graph ids, label words, reliability labels, impossible dates, unexpected keys, **policy↔memory echo**, decoy↔memory words | `leakcheck` |
| **Soft lexical flag** | **policy↔evidence echo** is soft from render-v7. Same detection, same matches, but it no longer triggers regeneration. It is shown on the review sheet as "(judge under C7/C11)". v2–v6 keep it hard (`STRICT_EVIDENCE_ECHO_VERSIONS`), so earlier results are not reinterpreted | `leakcheck.evidence_echo_hard`, `render_run.py`, `review.FLAG_ITEMS` |
| **Measured leakage** | Unchanged and separate: the worse heuristic's justification-set F1 ≤ 0.50, pooled over a predeclared set. Soft-flag counts are reported next to it, never folded into it | `LeakReport.summary` |
| **Semantic quality** | `read_decisions` now refuses `accept` unless **C8 and C10 pass**, however clean the automated report | `review.REQUIRED_FOR_ACCEPT` |
| **Prompt** | **render-v7** = verbatim v6 (SHA-256 `e0ba8888…`, pinned) + 2 edits: (1) the "HARD RULE (facts)" becomes **clarity-first fact wording**: prefer a clear equivalent, but use the standard term when it is the only clear name; never a vague or invented substitute ("balance credits" for carbon offsets is named as the anti-example); copying other wording of the fact (its verbs, qualifiers, sentence) remains disallowed. (2) **Plain facts**: each evidence item states one measurable value or one held credential, named in one or two common words, without stacked qualifiers; numeric thresholds only where a fact is naturally a number. The decoy rule adds "even in a different sense" (the v5d "security" collision). The memory↔policy HARD RULE is unchanged | `prompt.py` |

Recorded F1/F2 reviews still validate under the new accept rule.

**Diagnostic on the stored F6 attempts** (no calls; shows what the check change does and does not do):
- v5c attempt 1 (render-v5): 5 hard echoes under the strict profile, 0 hard flags under the v7 profile. It is **not reused or counted**. It was rendered and rejected under v5's rules, and the cache key includes the prompt version, so a v7 run cannot pick it up.
- v5d attempt 2 (render-v6): under the v7 profile it is **still rejected** (decoy "security"). Its "balance credits" problem would be a C8/C10 failure in review regardless.

### 17b. F6 design

The generator is frozen (`pilot-1-model-free`), so **the F6-000 graph does not change**: B1 ⇐ E1 OR E2; B2 ⇐ B1 AND E3; D1 ⇐ B2 AND E4; three single-premise distractors (B3–B5); a low-reliability retraction of E1, with gold *keep* because E2 still supports B1. Changing the graph would change the frozen suite and labels, and would make F6 a different test.

The redesign is in how F6 is **worded**, via render-v7:
- **Fewer, simpler named quantities.** Both v6-era failures came from multi-word quantity or credential names ("fleet-wide average carbon emission level", "certified annual carbon offset plan"). Plain facts mean one value or credential per fact, named in one or two common words. That leaves fewer phrases to echo and fewer to paraphrase vaguely.
- **Credentials as yes/no conditions.** A licence or membership is a yes/no condition, not a number; numbers are used only where a fact is naturally a number.
- **Structure is not weakened:** the AND/OR sets, the update, reliability and gold are untouched. The memory↔policy hard rule and the decoy rule still apply.
- **Accidental clues:** allowing a standard term in both a fact and a policy can raise lexical recoverability. It is measured, not assumed away: the gate below is unchanged, and each soft echo goes to C7/C11 review.

### 17c. Proposed scope, gate and budget (for approval; nothing runs before it)

**Option A (recommended): pilot-2 = F1-000, F2-000, F6-000, all rendered fresh under render-v7.** The 40-scenario run would use render-v7, so the pilot should validate render-v7 on every family it covers. Mixing v5 F1/F2 with a v7 F6 would gate a prompt combination that no later run uses.

| Item | Proposal |
|---|---|
| Run | `--run smoke-render-v7 --prompt-version render-v7 --only F1-000 F2-000 F6-000 --max-attempts 2`, seed 0, `gemini-3.5-flash` via Lyzr, no cache reuse from earlier runs |
| Per-scenario acceptance | 0 hard flags under the v7 profile within 2 attempts; then a **human review** of C1–C13 recorded in `smoke-render-v7/review.csv`, decision `accept`, with **C8 and C10 passing** (enforced) |
| Measured leakage gate | Worse heuristic's justification-set F1 **≤ 0.50, pooled over these three v7 scenarios**. Per-scenario and soft-flag numbers are diagnostic only |
| Soft flags | Every `policy_echoes_evidence` flag is listed on the sheet; the reviewer judges each under C7/C11. A flag is not a fail by itself |
| Pass | All three accepted and the gate ≤ 0.50. The 40-scenario run then still needs its own approval (§8) |
| Fail | Any scenario not rendered in 2 attempts, not accepted, or gate > 0.50 means pilot-2 fails: stop, report, no further calls. A reviewer's `revise` also needs a new approval before any regeneration. No check or threshold is changed after results are seen |
| Pilot-1 | Stays recorded (F1, F2 accepted; F6 excluded; gate unscored). Pilot-1 reviews do not carry over: the v7 F1/F2 are new texts and need new reviews |
| **Budget** | **New pilot-2 cap: $0.60 cumulative** (`--budget-usd 0.60`; later runs in pilot-2 count against it via `--prior-spend-usd`). Guard worst case is $0.141 per call (3 first attempts $0.42; all 6 attempts $0.85). Observed v5/v6 calls cost $0.062–$0.110 (mean ≈ $0.08). Expected ≈ $0.25 if all three pass first time. $0.60 allows the three first attempts plus about one retry under the guard's worst-case rule; the guard stays authoritative and refuses any call that could exceed the cap |

**Option B (cheaper, not recommended):** render only F6 under v7 (cap $0.30: two worst-case attempts = $0.283) and pool it with F1 (v5) and F2 (v5b). This reuses accepted reviews, but the gate would mix prompt versions and leave render-v7 untested on F1/F2.

### 17d. Pilot-2 render (2026-10-20): 3/3 rendered on the first attempt; gate 0.31

Approved by the user: Option A, with the controls in §17c, enforced as: guard cap $0.60 cumulative, `--max-attempts 2`, `--stop-on-failure` (added for this run), render-v7 prompt pinned in tests (SHA-256 `83b02a66039a981fba0fd4aa6cf098d69dd313496b42c1e04da0958468f5f402`).

Command: `uv run --group lyzr python scripts/render_run.py --run smoke-render-v7 --prompt-version render-v7 --only F1-000 F2-000 F6-000 --max-attempts 2 --budget-usd 0.60 --stop-on-failure`. Outputs are in `data/rendered/smoke-render-v7/`.

| Scenario | Attempt | Tokens in / out | Guard-charged | Hard flags | Soft flags | Word-only set F1 | Policy-assisted set F1 |
|---|---|---|---|---|---|---|---|
| F1-000 `s_d13e3034f6` | 1 | 3,254 / 5,629 | $0.0706 | 0 | 2 `policy_echoes_evidence` ("holds an active … medical device permit"; "zero major safety incidents"), 1 `order_cue` ("initial") | 0.00 | 0.33 |
| F2-000 `s_3d821bdd07` | 1 | 3,045 / 4,304 | $0.0553 | 0 | 0 | 0.29 | 0.29 |
| F6-000 `s_c41a0870a2` | 1 | 3,357 / 6,138 | $0.0766 | 0 | 1 `policy_echoes_evidence` ("quality management certification") | 0.18 | 0.31 |
| **Pooled (the predeclared gate)** | | | **$0.2025 of $0.60** | **0** | **4** | 0.14 | **0.31 ≤ 0.50: pass** |

- 3 calls, no retries.
- Per-scenario scores are diagnostic only.
- Premise-overlap AUC (reported only): F1 0.73, F2 0.86, F6 0.80.
- No template trigrams.

**Status:** automated stage passed. **Pilot-2 is not accepted.** That needs a human review of all three (`smoke-render-v7/review.md` → `review.csv`), each `accept` with C8 and C10 passing. Any fail or `revise` stops the pilot (§17c). Pilot-1 reviews do not carry over.

**Pre-review by Claude (not the human review; for the reviewer to confirm or reject):**
- **F6, likely C8/C9/C10 problem.** B2 and D1 are about *BioGlow Diagnostic Kit*, but their co-premises E3 and E4 are about *Apex Medical Corp* (ISO 13485; $5M liability cover). The policies say "provided **the producer** maintains …", yet nothing visible says Apex Medical Corp produces BioGlow. Only the hidden rationale makes that link. A system reading only the system view could fairly treat Apex as an unrelated distractor (the distractors are also separate named products), so the link B2 ⇐ B1 AND E3 is not inferable. The retraction (flat denial, anonymous forum post) and the FDA 510(k) alternative keeping B1 are correct.
- **F1, C7 to judge.** The memory "secures **initial** supplier status" and its policy "**Initial** vendor accreditation" use a stage word, flagged as `order_cue`. Here it is the outcome's name, but it hints at the chain's first rung. The chain logic is consistent: warranty 24 → 6 months, below the 12-month minimum, so every chain memory fails; the Zenith distractor holds. The two evidence echoes are standard terms ("Class II medical device permit", "zero major safety incidents").
- **F2, C10 to judge.** The policy requires an *annual* audit count of 1,000. The fact gives 1,200 "over the preceding year", but the update's 850 is "during the evaluation period". This is probably the same period, but worded differently. The ISO 13485 revocation is a supersede with a new status. "quarterly vendor index" ↔ "distribution database indexing" is a looser outcome match than the others.

### 17e. External AI pre-review of pilot-2 (2026-10-20); human review outstanding

An external AI assistant, supplied by the user, reviewed the three v7 sheets. It is **not the human review**. It is stored verbatim as `smoke-render-v7/ai-prereview-v7.tsv`. `review.csv` stays blank and is reserved for the human review.

| Scenario | AI decision | Failed items | Finding |
|---|---|---|---|
| F1 | accept | none | "initial" is a soft C7 consideration, not a fail; the echoes are generic terms |
| F2 | revise | C4, C10, C13 | the update's 850 audits are "during the evaluation period", but the policy needs an *annual* count, and nothing equates the two |
| F6 | revise | C6, C8, C9, C10, C13 | the Apex Medical Corp facts (ISO 13485, $5M cover) are never linked to BioGlow Diagnostic Kit in the system view ("the producer" does not establish it) |

- **Agreement with Claude's pre-review (§17d):** both name the F6 entity-link gap and the F2 period wording. They differ on F2 severity: Claude rated it "to judge"; the AI rates it fail.
- **Status:**
  - Pilot-2 stays at the automated stage. No calls are made in the meantime.
  - The stop rule in §17c is triggered by a **human** fail or `revise`, so it turns on the human review.
  - If the human review confirms either finding, pilot-2 stops as failed. A redesign or retry would then need a new approval.

### 17f. Human review of pilot-2 (2026-10-20): F2 and F6 revise; pilot-2 stopped as failed

- **Recorded in:** `smoke-render-v7/review.csv`, reviewer `thejasrao262003`, validated by `read_decisions`.
- **Provenance:** the user verified the external AI pre-review (§17e) against the sheets and adopts its verdicts as their own human review.
- **Normalised to the validator's format:** PASS/FAIL became lowercase; F1's C3 "N/A" became `pass` (vacuous; noted); the "AI pre-review, not a human verdict" prefix was removed from the notes. The verbatim AI file is kept unchanged.

| Scenario | Decision | Failed items |
|---|---|---|
| F1 `s_d13e3034f6` | **accept** | none |
| F2 `s_3d821bdd07` | **revise** | C4, C10, C13 (annual threshold vs an update "during the evaluation period") |
| F6 `s_c41a0870a2` | **revise** | C6, C8, C9, C10, C13 (no visible link between Apex Medical Corp and BioGlow Diagnostic Kit) |

**Outcome under the predeclared rule (§17c):** a human `revise` stops the pilot. **Pilot-2 has failed.**
- No regeneration, no further calls (spend stays $0.2025 of $0.60), no change to checks or acceptance criteria.
- The automated gate (0.31) is reported as measured, but it does not rescue the pilot: acceptance required all three to be accepted.
- Pilot-1 and pilot-2 are both recorded as they stand. **The 40-scenario run stays blocked.**

**What the failures show** (for the next design decision, nothing applied):
- **F6:** the renderer split one subject into two entities (a product and its maker) without stating the relation. No current check looks for this. A *subject-continuity* check could catch it: within a justification set, every premise must be about the conclusion's entity or one explicitly linked to it in the visible text. Possible hard-check candidate; a prompt rule would also be needed.
- **F2:** a superseding value must be stated over the same period or unit as the fact and the policy threshold. This extends the v4 "same unit" rule to time windows. A prompt rule, judged by the reviewer under C4/C10.
- Both are **semantic** failures that the lexical gate cannot see. That confirms the decision to make C8/C10 acceptance independent of the gate.

## 18. render-v8 proposal (2026-10-20): subject and time-window continuity

*Proposal only. **Nothing here is implemented, and no calls are authorised.** Pilot-2 stays recorded as failed (§17f), and pilot-1 as recorded (§16h–16j).*

**Why the current checks missed both failures:** every automated check is lexical (shared phrases, shared words, bag-of-words recovery). The F2 and F6 failures are about *reference*: which entity a fact is about, and which time window a number covers. Two text pairs can share no wording and still disagree on reference.

### 18a. Check 1: subject continuity (proposed hard)

**Rule:** for every derived memory *m* and every **evidence** premise *e* in any of *m*'s justification sets (from the eval view, as the decoy check already does), *e*'s text must name *m*'s entity. A premise about a different entity passes only if *e*'s own text states the link (e.g. "Apex Medical Corp, maker of the BioGlow Diagnostic Kit, …"). A derived premise (a memory used as a condition) must have the same entity as *m*.

- **Why the link must sit in the premise itself:** the frozen generator fixes the number of evidence items, so the renderer cannot add a separate "Apex makes BioGlow" fact. The link has to live inside the premise.
- **Entity detection needs a new extractor.** `subject_names` returns nothing for "The Kestrel 800 device" (it skips a leading "The"), and treats "Vortex Solar Inc's Helios Panel" as a single name. Proposed: capitalised spans anywhere in the text, possessives split into owner + item, so both "Vortex Solar Inc" and "Helios Panel" count.
- **Hard or soft:** **hard** when both texts contain a detected name and they share none. **Soft** (for C6/C8 review) when either side has no detectable name. A false hard flag costs one retry; a missed link costs a failed human review.
- **Prompt rule (v8):** "SUBJECT CONTINUITY: every fact that supports a conclusion names the conclusion's entity. If a fact is about a related entity (maker, parent, owner), state the relation inside that fact."

### 18b. Check 2: time-window continuity (proposed hard for a mismatch, soft for an unknown window)

**Rule:** for every `supersedes` update, the time window of its new value must match the window of the target fact and of the threshold in the governing policy.

- **Window detection:** normalise phrases to {year, quarter, month, multi-year N, unknown}:
  - annual / yearly / per year / over the preceding year / last year → year;
  - "quarterly" and "this quarter" → quarter, and so on;
  - vague windows ("the evaluation period", "recently") → **unknown**.
- **Value vs window:** a duration that *is* the quantity ("warranty period of 24 months → 6 months", "fleet age of 5.8 years") is the measured value, not a window, and must not trigger the check. Only window phrases attached to a count or amount ("during", "over", "per", "in the …") count.
- **Hard or soft:** **hard** if the fact or policy has a window and the update states a **different** one. **Soft** (C4/C10) if the fact has a window and the update's is **unknown or missing**.
  - The F2 case ("over the preceding year" vs "during the evaluation period") is the *unknown* case, so under this design it would be soft: the reviewer still decides, but the sheet now points at it.
  - Making the unknown case hard instead is a choice for you. It catches more, at the cost of extra retries.
- **Prompt rule (v8):** "An update that replaces a value states it over the same time window as the original fact (if the fact is annual, the new value is annual)."

### 18c. Tests (to be written before any check code is trusted)

Regressions from stored outputs (no calls):

| Test | Input | Expected |
|---|---|---|
| R1 | v7 F6: `e_3dc4`, `e_45ef` (Apex Medical Corp) under BioGlow memories | **subject flag (hard)** on both |
| R2 | v7 F2: `u_a152` "during the evaluation period" vs fact "over the preceding year" and policy "annual" | **window flag (soft, unknown)** |
| C1 | v7 F2 `e_e50c` "Apex Medical logged … audits **for the Kestrel 800 device**" | no subject flag: the premise names the conclusion's entity |
| C2 | v5 F1, v5b F2, v5b F6 (all premises name the same company), v7 F1 | no flags from either check |
| C3 | v7 F1 update "warranty coverage period to 6 months"; v5b F2 "vehicle age of 5.8 years" | no window flag (value, not window) |
| C4 | v5b F6 update "… $650,000 … during the previous year" (a retraction) | not checked: only `supersedes` is |
| S1 | synthetic: "Apex Medical Corp, maker of the BioGlow Diagnostic Kit, holds …" | no subject flag |
| S2 | synthetic: fact "annual revenue of $2M", update "revenue last quarter of $400k" | **window flag (hard, mismatch)** |
| S3 | synthetic: "The Kestrel 800 device …" and a possessive "Vortex Solar Inc's Helios Panel …" | extractor finds "Kestrel 800"; "Helios Panel" matches a memory naming only the panel |
| S4 | distractor facts in no justification set | never subject-checked |

Before any call, I will also report what both checks flag on **every stored run** (smoke v1–v7), so you can see their false-positive rate on real output.

### 18d. Proposed pilot-3: scope, gate, budget (for approval after the code and tests are reviewed)

| Item | Proposal |
|---|---|
| Prompt | render-v8 = verbatim v7 (pinned) + the two prompt rules above; v8 hash pinned before the run |
| Scope | **Option A:** F1-000, F2-000, F6-000 fresh under v8 (same as pilot-2). **Option B:** also add **F3-000**. The 40-scenario run includes F3 (10 scenarios, the AND-heavy family), and F3 has not been rendered since smoke test 3 (render-v3). I recommend B |
| Per-scenario acceptance | 0 hard flags (including both new checks) within 2 attempts; human review of C1–C13; `accept` with C8 and C10 passing |
| Gate | Worse heuristic's justification-set F1 ≤ 0.50, pooled over exactly the declared set; per-scenario numbers and soft-flag counts reported alongside |
| Stop rule | As in pilot-2: an automated failure after 2 attempts, a guard refusal, or any human fail/`revise` stops the pilot. No scope change, no criteria change |
| Budget | New pilot-3 cap, cumulative. **A: $0.60** (3 × $0.141 first attempts + about one retry). **B: $0.80** (4 × $0.141 + about one retry). Expected ≈ $0.21 (A) / ≈ $0.28 (B), at the pilot-2 rate of ≈ $0.068 per call |
| History | Pilot-1 and pilot-2 stay recorded as they are; no review carries over |

**Decisions needed, in order:**
1. Approve implementing §18a–18c (code + tests + the stored-output report). Still no calls.
2. Choose hard or soft for the *unknown window* case.
3. After reviewing the code and report: choose scope A or B and approve the cap.

### 18e. Continuity checks implemented; stored-output report (2026-10-20)

**Approved by the user on 2026-10-20:** implement §18a–18c and report on stored outputs; unknown windows are soft. **Not approved:** model calls, a v8 prompt, or pilot-3. No stored run, review or verdict was changed (no diff under `data/`).

**Implementation** (`leakcheck`; 109 tests pass, 22 of them new):

| Function | Behaviour |
|---|---|
| `evidence_entities` | Conservative names: the leading capitalised run of each evidence sentence. A leading "The" is skipped, digits are allowed after a name ("Kestrel 800"), and possessives are split into owner and item. A sentence opening with a generic word yields no name |
| `subject_flags` | For each premise→memory pair in the eval view's justifications: **hard** `premise_about_other_entity` if both name known entities and share none; **soft** `subject_uncertain` if either names none. A relation counts only if it is stated **in the premise itself**; an association stated elsewhere does not rescue it (tested) |
| `windows` / `condition_windows` | Aggregation windows (year, quarter, month, week, N years; "unknown" for vague). Durations that are the measured value match none. A policy window is attributed only to the condition clause that best matches the fact; a tie or no overlap attributes none |
| `window_flags` | `supersedes` only. **Hard** `update_window_mismatch` (different stated window) and `fact_policy_window_mismatch` (disjoint fact/condition windows). **Soft** `update_window_unclear` (vague or no window when the fact or condition has one) |
| Gating | `continuity_enforced(version)` is off for render-v2…v7, so earlier runs are never re-judged; it applies from render-v8, which does not exist yet. `render_run` adds continuity hard flags to retries, and `check(..., continuity=True)` adds them to reports, only when it is enforced |
| Review sheet | Soft flags labelled "(judge under C6/C8)" and "(judge under C4/C10)" |

**Stored-output report:** `docs/continuity-report.md` (`scripts/continuity_report.py`).
- **Scope:** every raw response under `data/rendered/*/raw/`, including rejected attempts. 26 files; 24 unique responses after removing byte-identical cache copies (each listed with all the runs holding it); 24 parsed, 0 unparsed, 0 excluded.
- **Denominators:** 179 premise→memory pairs; 20 superseding updates; 101 evidence→policy-condition pairs (render-v1 has no policies).

| Check | Flags | Known genuine | Likely false positive | Rate |
|---|---|---|---|---|
| `premise_about_other_entity` (hard) | 2 | **2**: v7 F6 `e_3dc4`, `e_45ef` (Apex Medical Corp vs BioGlow) | 0 | hard false positives 0 / 177 other pairs; 0 / 23 other renderings |
| `subject_uncertain` (soft) | 13, all in render-v1 (3 of 24 renderings) | 11 genuinely unnamed subjects ("The customer", "The client", "The business's", "The requested coverage limit"). render-v1 predates the naming rule | 2 detector limits: an address ("123 Oak Street") and a quoted name ("'Elite Savings Account'") | 0 / 142 pairs in render-v2…v7 |
| `update_window_unclear` (soft) | 2 of 20 updates | **1**: v7 F2 `u_a152` ("during the evaluation period" vs "over the preceding year") | 1 borderline: v3 F2 `u_41fa` "corrected its seat count to 350 … following a user audit" vs a monthly fact. A correction plausibly keeps the window but does not say so | — |
| `update_window_mismatch` (hard) | 0 / 20 | — | — | 0 |
| `fact_policy_window_mismatch` (hard) | 0 / 101 | — | — | 0 |

- **Required outcomes:**
  - Both known pilot-2 failures are detected: F6 hard, exactly the two failing pairs; F2 soft, as approved, with no hard flag.
  - All four human-accepted controls are clean: v5 F1, v5/v5b F2 (one response), v7 F1.
  - The Kestrel 800 premise passes.
- **Disclosure of calibration on this data:** the first implementation attributed a policy's windows to the whole policy. On these outputs that produced one hard false positive (v3 F2: "annual" belongs to the revenue condition, not the monthly licence count) and one soft one (v7 F2's ISO revocation). It also had a possessive bug ("Sarah Chen's …" at the end of a name), which made 6 render-v1 pairs uncertain. Both were fixed before this report: clause-level attribution and possessive splitting, each with a regression test.
  - These are fixes to the check's definition made on historical data, before the check gates anything. No pilot result depends on them.
  - The cost of the fix: a window stated only in a policy is now ignored when the clause match is ambiguous, so a mismatch hidden there can be missed (conservative by design).
- **Known limits:**
  - **Subject check:** addresses and quoted names are not recognised as entities (they give a soft flag, never a hard one).
  - **Window check:** it only knows the listed phrases; a window phrased otherwise is invisible to it. Both checks are aids to human review, not replacements for C6/C8/C10.

### 18f. Pilot-3 proposal (for approval; nothing runs before it)

**Proposed render-v8 prompt** = verbatim v7 (pinned `83b02a66…`) + two rules, to be pinned before any call:
1. "SUBJECT CONTINUITY: every fact that supports a conclusion names the conclusion's entity. If a fact is about a related entity (maker, parent, owner), state the relation inside that same fact (e.g. 'Apex Medical Corp, maker of the BioGlow Diagnostic Kit, …'). Responses that break this are rejected."
2. "TIME WINDOWS: a count or amount states the window it covers (annual, last quarter, …), and the policy condition it is compared with uses the same window. An update that replaces such a value states it over the same window as the original fact, never a vague one such as 'the evaluation period'."

| Item | Proposal |
|---|---|
| Checks | All existing hard checks, plus `premise_about_other_entity`, `update_window_mismatch` and `fact_policy_window_mismatch` as hard. `subject_uncertain`, `update_window_unclear` and the policy↔evidence echo are soft, judged by the reviewer |
| Scope | **Option B (recommended): F1-000, F2-000, F3-000, F6-000**, fresh under v8. On stored output the new hard checks raised 0 false positives (0 / 177 pairs, 0 / 20 updates, 0 / 101 conditions), so they are unlikely to burn the budget on spurious retries. F3 is in the 40-scenario run and was last rendered under render-v3. **Option A:** F1, F2, F6 only |
| Acceptance | Unchanged from pilot-2: 0 hard flags within 2 attempts; a human review of C1–C13 for every scenario; `accept` with C8 and C10 passing |
| Gate | Worse heuristic's justification-set F1 ≤ 0.50, pooled over exactly the declared set. Per-scenario scores and soft-flag counts are reported alongside |
| Stop rule | Unchanged: a failure after 2 attempts, a guard refusal, or any human fail/`revise` stops the pilot. No scope or criteria change after results |
| Budget | New pilot-3 cap, cumulative: **B $0.80**, **A $0.60**. Guard worst case $0.141 per call. Expected ≈ $0.27 (B) / ≈ $0.20 (A), at the pilot-2 rate of ≈ $0.068 per call |
| History | Pilot-1 and pilot-2 remain as recorded; no review carries over |

### 18g. Pilot-3 (2026-10-20): stopped. F1 failed both attempts on existing hard checks

Approved by the user: render-v8 = v7 + exactly the two insertions (SHA-256 `1239470d…`, pinned; commit `7fa11ee`); scope F1, F2, F3, F6; 2 attempts each; cap $0.80; `--stop-on-failure`. Command run as approved, unchanged. Outputs are in `data/rendered/smoke-render-v8/`; both raw responses are kept.

| Call | Tokens in / out | Guard-charged | Result |
|---|---|---|---|
| F1 attempt 1 | 3,458 / 5,561 | $0.0703 | **Rejected:** HARD `decoy_shares_memory_word` "sale". Decoy "…if annual **sales** volume exceeds $10,000,000…" vs memory "meets post-**sales** support standards". Soft: 2 policy↔evidence echoes ("spare parts inventory", "carries general liability"). Continuity checks: **clean** (every premise names VeloTech Mobility; the update keeps the point-in-time inventory value) |
| F1 attempt 2 (with the attempt-1 feedback) | 3,494 / 5,063 | $0.0648 | **Rejected:** HARD `reliability_word` in memory B2 "achieves clinical **reliability** authorization". Soft: 1 policy↔evidence echo; 9 `subject_uncertain` (see below) |
| **Total** | | **$0.1352 of $0.80** | **F1 failed; run stopped.** F2, F3, F6 not attempted |

**Outcome under the predeclared rule:** a hard failure after 2 attempts stops the pilot. **Pilot-3 has failed.**
- 0 scenarios rendered; the gate is unscored; nothing to review.
- No third attempt, no re-render, no change to any check, no budget change.
- Pilots 1–2 stay as recorded. The 40-scenario run stays blocked.

**Observations** (for the next decision; nothing applied):
- **Neither rejection came from the new v8 rules.** Both are long-standing hard checks catching a word used in another sense: "sales" (a decoy's sales volume vs post-sales support) and "reliability" (a clinical outcome name vs the ban on reliability labels). This is the same class as pilot-2-era "security".
- **A retry rewrites the whole scenario.** Attempt 2 is a different world (Aura Diagnostic System, not VeloTech): it fixed the attempt-1 flag but rolled the dice on every other check, and introduced a new hard failure. With 2 attempts per scenario and 4 scenarios, the chance that every scenario clears every hard check is the binding constraint, separate from semantic quality.
- **Detector limit, seen on new output.** Attempt 2's evidence opens with source phrasing ("An audit log from Apex Medical confirms that the Aura Diagnostic System …"), so `evidence_entities` found no subject names. The result was 9 soft `subject_uncertain` flags and no hard ones; the premises do name the system. This is conservative as designed, but it shows the uncertain rate depends on sentence form.
- **Attempt 1 otherwise looked sound** on the continuity rules, but it was rejected under the rules in force and is not counted.

### 18h. Targeted repair: mechanism (implemented, model-free) and proposal for one call

**Approved by the user on 2026-10-20:** the targeted-repair *direction*, with pilot-3 F1 attempt 1 as the base, existing checks unchanged, and a single attempt. **Not approved:** the call itself, pending this mechanism and cap. Pilot-3 stays recorded as failed (§18g); nothing below changes that.

**Why:** a retry under `render_run` regenerates the whole scenario, so fixing one flag re-rolls every other check. Pilot-3 F1 attempt 2 was a different world with a new hard failure.

**Mechanism** (`render/repair.py`, `scripts/repair_run.py`; 121 tests pass, 11 of them new):
1. **Frozen base.** `data/rendered/smoke-render-v8/raw/F1-000.46ddd88bb57031c7.a1.json` (SHA-256 `390a14ae…`). It is read, never written (tested). It is parsed and checked exactly as the pipeline does.
2. **Permitted fields come from the hard flags.** `editable_paths` maps each hard flag to one field of the original JSON; a flag that cannot be mapped makes the base unrepairable. For this base it yields **exactly one field, `decoy_policies[0]`** ("A distributor achieves preferred vendor status if annual **sales** volume exceeds $10,000,000 or if a five-year clean trade history is verified"), with the reason in plain words.
3. **One call, prompt `repair-v1`** (SHA-256 `a49158f2…`, pinned in tests) = the full pinned render-v8 prompt + repair instructions: return only `{"replacements": {field: text}}` for exactly the listed fields; keep each field's role (a decoy still governs nothing); introduce no new problem. Temperature 0.3, one fresh agent, `max_calls=1`.
4. **Merge and diff gate.** `apply_repair` refuses any reply that is not exactly the permitted edit: an extra or missing field, an empty text, a wrapper key, invalid JSON, or any change outside the permitted fields after merging. All are tested.
5. **All hard checks re-run, unchanged.** `leakcheck.hard_flags` is now the single definition used by both `render_run` and the repair: lexical checks, decoy words, reliability/label words, and subject and window continuity under render-v8. Soft flags are all kept and appear on the review sheet.
6. **No fallback.** If the repair is refused or any hard flag remains, the experiment stops. There is no second repair, no whole-scenario re-render, and no check change. The run directory must not already exist (one shot).

Tests cover the base mapping to `decoy_policies[0]`, an attempt-2-style memory flag mapping to `nodes.B2.text`, a clean replacement passing every hard check with a diff equal to exactly the one field, a replacement that keeps "sales" still failing the unchanged decoy check, and five malformed or over-broad replies being refused.

**Proposed execution (needs approval):**

| Item | Proposal |
|---|---|
| Command | `uv run --group lyzr python scripts/repair_run.py --base data/rendered/smoke-render-v8/raw/F1-000.46ddd88bb57031c7.a1.json --run smoke-render-v8-repair --budget-usd 0.20` |
| Hard cap | **$0.20**, 1 call. The guard's worst case for this call is **$0.1444** (12,000 output tokens assumed), so it refuses anything that could exceed the cap. Expected ≈ $0.02–0.04: ≈ 4k input tokens; the reply is one sentence plus any reasoning |
| Automated success | The reply is exactly the permitted edit (diff = `decoy_policies[0]`) **and** 0 hard flags under render-v8 |
| Acceptance | Then a fresh human review of the repaired F1 on C1–C13: `accept`, C8 and C10 passing, and **C12 checked specifically** (the new decoy must still govern nothing). The AI pre-review stays separate |
| What it does and does not establish | It tests whether a bounded repair can clear a word-level hard failure without disturbing an otherwise sound scenario. It is **not** a pilot pass: one scenario, no pooled gate. F2, F3 and F6 stay unrun. Using repair as the retry step in a future pilot would need its own approval, scope, gate and cap |
| Record | `repair.json` (base hash, permitted fields, raw reply, diff, hard flags after), `spend.json`; review files only if the automated stage passes |

### 18i. Targeted repair result (2026-10-20): automated stage passed; human review outstanding

Approved by the user: one call, cap $0.20, scope `decoy_policies[0]` only. Command run exactly as approved. Outputs are in `data/rendered/smoke-render-v8-repair/`: `repair.json` (base hash, permitted field, raw reply, diff, hard flags after), `spend.json`, `system/`, `eval/`, `leak-report.json`, `review.md`, and a blank `review.csv`. The frozen base is byte-identical to its committed version.

| Item | Result |
|---|---|
| Call | 1; 4,368 in / 968 out tokens; **$0.0207 of $0.20** |
| Diff gate | **Passed:** the reply replaced exactly `decoy_policies[0]`; nothing else changed |
| Before | "A distributor achieves preferred vendor status if annual **sales volume** exceeds $10,000,000 or if a five-year clean **trade history** is verified." |
| After | "A distributor achieves preferred vendor status if annual **revenue** exceeds $10,000,000 or if a five-year clean **track record** is verified." Inside the permitted field the model also reworded "trade history"; nothing outside it changed |
| Hard checks (render-v8, unchanged; including subject and window continuity) | **0** |
| Soft flags | 2 `policy_echoes_evidence` ("spare parts inventory"; "carries general liability"), both judged under C7/C11. Unchanged from the base |
| Lexical heuristics (diagnostic; one scenario, no pooled gate) | Worse heuristic set F1 0.17; word-only 0.17; premise-overlap AUC 0.71 |

**Status:**
- The repair cleared a word-level hard failure without rewriting the scenario or changing any check.
- The repaired F1 is **not accepted** until a fresh human review (C1–C13; C8 and C10 must pass; C12 confirmed explicitly).
- Pilot-3 remains failed. F2, F3 and F6 remain unrun. Using repair as a retry step in a future pilot needs its own approval.

**Pre-review by Claude** (not a human verdict; points for the reviewer):
- **C12:** the new decoy concerns "preferred vendor status" (no memory states it). Its conditions (annual revenue, a five-year track record) match no fact in the scenario, so it looks inert.
- **C13:** the chain logic is consistent. The spare-parts inventory goes from $200,000 to $80,000, below the $150,000 minimum, so every VeloTech memory fails on recomputation; the Apex Medical Supplies distractor holds. The inventory is a point-in-time value, so no time window is needed.
- **C10:** the policy says "**regional** spare parts inventory", the fact says "**local**". These are probably the same, but the words differ.
- **C5:** two high-reliability sources are VeloTech's own records ("Warranty Term Sheet, signed"; "Warehouse Management System"). Whether a company's own system of record reads as authoritative is the reviewer's call.
- **C7/C11:** the two shared phrases are the standard names of the quantities. Every VeloTech memory ends "for the Velo-X1", which is uniform but names the product rather than a support.

### 18j. External AI pre-review of the repaired F1 (2026-10-20); human review outstanding

An external AI assistant, supplied by the user, reviewed the repaired F1. It is stored verbatim as `smoke-render-v8-repair/ai-prereview.md`. **It is not the human review;** `review.csv` stays blank.

- **AI disposition:** revise.
- **Fails:** C2, C8, C9, C10 and C13. The policy requires a **regional** spare-parts inventory, while the fact and update state a **local** one, so the inventory condition is not established as written.
- **Passes:** C12 (the repaired decoy is inert). C5 and C7 pass with qualifications.
- **Relation to the repair:** the repair worked as designed (one field, 0 hard flags), but it could only touch the flagged decoy, so it could not fix a mismatch that no check flags. This is the C10 point Claude's pre-review (§18i) raised as "to judge". The AI review rates it a fail.
- **Status:** the stop rule turns on the human verdict. No further repair or re-render of this scenario is authorised.

### 18k. Human review of the repaired F1 (2026-10-20): revise

- **Recorded in:** `smoke-render-v8-repair/review.csv`, reviewer `thejasrao262003`, validated by `read_decisions`. The verdicts are the user's own, given per criterion.
- **Decision: revise.** Failed: C2, C8, C9, C10 and C13 (a "local" spare-parts inventory in the fact and update vs a "regional" one in the policy condition). Passed: C1, C3 (vacuous), C4, C5 (sources fit their claims, though not independent), C6, C7, C11, C12 (the repaired decoy and the eco-label decoy are inert).
- **Reading:**
  - **The repair mechanism worked as specified:** exactly the permitted field changed, the unchanged hard checks passed, $0.0207 spent.
  - **The scenario failed on a semantic mismatch that no hard check detects:** the geographic scope of a quantity. This is the same class as pilot-2's reference failures (entity, time window), now on location. A scope check alongside the window check, and a matching prompt rule, are a candidate for a future proposal; nothing is applied.
- **Status:**
  - The repaired F1 is **not accepted**.
  - No further repair or re-render of it.
  - Pilot-3 remains failed; F2, F3 and F6 remain unrun; the 40-scenario run stays blocked.
  - Total spent on pilot-3 and the repair: $0.1352 + $0.0207 = $0.1559.

## 19. Proposal: structured condition records (render-v9) and pilot-4

*Proposal only. **Nothing is implemented, and no calls are authorised.** Pilots 1–3 and the repair stay as recorded.*

### 19a. Why

Six renders have had a human review. Three were accepted (v5 F1, v5b F2, v7 F1). Three came back as revise, and **all three were reference mismatches between a fact and the policy condition it is meant to satisfy**:

| Render | Mismatch | Dimension |
|---|---|---|
| v7 F6 | facts about Apex Medical Corp support memories about BioGlow Diagnostic Kit | entity |
| v7 F2 | annual audit count vs an update "during the evaluation period" | time window |
| v8 F1 (repaired) | "local" inventory vs a "regional" inventory condition | scope |

The lexical checks cannot see these, and each new check (§18) has covered only the dimension that had just failed. The proposal is to make the renderer **declare** what each fact and condition refers to, and to check all dimensions at once, in code, against both the other record and the text.

### 19b. Records (eval view only; never shown to the evaluated system)

render-v9 = verbatim v8 + one output section. For every evidence item and update, a **fact record**. For every premise of every justification set, a **condition record** in the governing policy:

```json
"facts": {
  "E1": {"entity": "VeloTech Mobility", "kind": "number", "quantity": "spare parts inventory value",
         "value": 200000, "unit": "USD", "window": "none", "scope": "local"},
  "U1": {"entity": "VeloTech Mobility", "kind": "number", "quantity": "spare parts inventory value",
         "value": 80000, "unit": "USD", "window": "none", "scope": "local"}
},
"conditions": {
  "B1": [{"premise": "E1", "entity": "same", "kind": "number", "quantity": "spare parts inventory value",
          "comparator": ">=", "threshold": 150000, "unit": "USD", "window": "none", "scope": "regional"}]
}
```

- **Field values:**
  - `kind`: number or credential (yes/no).
  - `window`: year, quarter, month, week, N years, or none (point-in-time).
  - `scope`: a controlled list: none, local, regional, national, international, or a named area.
  - `entity`: "same", or a relation ("maker of", "parent of", "owner of") that must then be stated in the fact.
  - A conclusion used as a condition gets `{"premise": "B1", "kind": "conclusion"}`.
- **Where they go:** records are parsed into the eval view next to the rationale. The system view is unchanged (`SYSTEM_VIEW_KEYS` and its test enforce this).

### 19c. Checks

| Check | What it compares | Severity |
|---|---|---|
| **Record agreement** | Each premise's fact record vs its condition record: quantity label, unit, window, scope equal; entity "same" or a declared relation | **Hard.** The renderer has declared a mismatch itself (the repaired F1 would fail here, on local ≠ regional) |
| **Satisfaction** | value *comparator* threshold must hold for every original fact. After applying each update's record, the comparisons must reproduce the renderer's `after_updates` and therefore the gold final state | **Hard.** An automated C13: it checks the arithmetic the reviewer now does by hand |
| **Text grounding: numbers** | The record's value and threshold appear in the fact and policy text (numbers normalised: $, commas, %, units) | **Hard** |
| **Text grounding: entity** | The record's entity string appears in the fact text. A declared relation must be stated in that fact (§18a rule) | **Hard** (v7 F6 fails here) |
| **Text grounding: window** | `windows(text)` agrees with the record: a known text window must equal the record's; a record window ≠ none must appear in the text; a vague text window fails | **Hard** (v7 F2 fails here). The extractor exists and is tested (§18e) |
| **Text grounding: scope** | The record's scope word (local, regional, …) appears in both texts; scope none means neither text uses a scope word | **Hard** |
| **Quantity label vs text** | The quantity label vs the wording in the fact and policy | **Soft** (paraphrase is allowed and cannot be checked lexically; the reviewer judges under C10) |

The §18 subject and window checks stay as an independent second line. All existing hard checks are unchanged.

### 19d. Tests (written before any render)

The stored renders have no records, so the tests use **hand-annotated record fixtures** for six renders. They test the *checker*, not whether the renderer fills records honestly:
- **Must fail:** v7 F6 (entity grounding), v7 F2 (window grounding), v8-repair F1 (record agreement on scope, *or* scope grounding if the records hide it).
- **Must pass:** v5 F1, v5b F2, v7 F1. These are the human-accepted controls; satisfaction must reproduce their gold final states.
- **Synthetic cases:**
  - a record that agrees with its pair but contradicts its own text (grounding must catch it);
  - a value that does not satisfy its threshold;
  - an update whose new value flips the outcome against `after_updates`;
  - a declared relation that is not stated in the fact;
  - a credential condition;
  - a conclusion condition.
- **View test:** no record field reaches the system view.

### 19e. Limits (stated now, not discovered later)

- **The renderer could write records that agree with each other while the text says otherwise.** Grounding catches this for numbers, entity names, windows and scope words, not for quantity names (soft only). The "balance credits" for "carbon offsets" case (v5d attempt 2, never human-reviewed) would only be a soft flag.
- **Records add output tokens.** An estimated +20–40% per call, roughly $0.08–0.10 instead of $0.07.
- **Records do not replace review.** Human review of C1–C13 stays mandatory.

### 19f. Pilot-4 (for approval after the code and tests are reviewed)

| Item | Proposal |
|---|---|
| Prompt | render-v9 = verbatim v8 (`1239470d…`) + the record section, pinned before any call |
| Scope | F1-000, F2-000, F3-000, F6-000, fresh |
| Retry | **Decision needed.** (a) As before: up to 2 whole-scenario attempts. (b) Attempt 2 = a **targeted repair** (§18h) of only the flagged fields, text and record together; a flag that cannot be mapped to fields stops the scenario. Recommend (b): pilot-3 showed whole re-rolls trade one failure for another, and the repair mechanism worked as specified |
| Acceptance, gate, stop rule | Unchanged: 0 hard flags; a fresh human review of all four; `accept` with C8 and C10; pooled worse-heuristic set F1 ≤ 0.50 over the four; any fail or `revise` stops the pilot |
| Budget | New cap **$0.80**, cumulative. Guard worst case ≈ $0.14 per call; expected ≈ $0.35–0.40 |

**Decisions needed, in order:**
1. Approve implementing §19b–19d (the parser, checks and fixtures; no calls).
2. After reviewing the code and test results: approve the exact v9 prompt text, the retry mode (a or b), and the cap.

### 19g. Built and run (2026-10-20): render-v9/v10 records; pilot-4 and pilot-4b

**Process change (user, 2026-10-20):**
- Stop gating model-free work on approval.
- Claude may review scenarios itself and run model calls, within a stated budget.
- Reviews below are **Claude's**, recorded as `claude-ai-review (delegated by user …; not human)`.
- Budget set by Claude: **$1.00 cumulative** for pilot-4 and pilot-4b.

**Built:**
- **render-v9:** eval-only fact and condition records. `leakcheck.record_flags` checks agreement, satisfaction, the post-update outcome and grounding against the text.
- **Hand-annotated fixtures for the six human-reviewed renders:** the 3 accepted controls raise no hard flag; the F6 entity failure and the repaired-F1 scope failure are hard; F2's vague window is soft, per the earlier decision.
- **Rule design, refined on the controls before any run:**
  - a condition's window or scope of "none" means "no restriction";
  - credentials have no accumulation window;
  - an unstated or vague window or scope is soft;
  - policy clauses split at "provided / if / through …".
- **render-v10:** v9 + one clarification (below).
- **Tests:** 133 pass. One commit (`f7bcd54`) was pushed with 26 failing tests: a `| tail` hid pytest's exit code. Fixed in `0523ff3`; commits are now gated on the real exit code.

**Pilot-4 (render-v9, `data/rendered/pilot4-render-v9/`, $0.4351):**
- F2, F3 and F6 rendered on the first attempt with 0 hard flags.
- F1 failed both attempts. Attempt 1: a record said "no window" while its policy clause said quarterly, a genuine catch. Attempt 2: a policy↔memory echo.
- **Gate 0.59 > 0.50: fail.**
- **Diagnosis:** the policies copied the facts' quantity names ("customer safety score", "electric motor power", "warranty duration"). That gave 12 policy↔evidence echoes, against 4 in pilot-2.
  - Masking entity names leaves 0.52 (the word-only score drops to 0), so the leak is the policy wording, not the names.
  - Cause: v9's "the same quantity name as the fact", written for the records, leaked into the policy text.
- **Fix, render-v10:** records are labels only; the policy text still follows the clarity-first wording rule, with two examples.

**Pilot-4b (render-v10, `data/rendered/pilot4b-render-v10/`, cumulative $0.8970 of $1.00):**

| Scenario | Attempts | Hard flags | Claude review |
|---|---|---|---|
| F1 | 2 (attempt 1: policy↔memory echo "standard impact safety", plus a record/clause window mismatch) | 0 | **accept** |
| F2 | 1 | 0 | **accept**, with a C10 note: the update "8 Gbps under standardized load" vs the spec "reaching 12 Gbps" is read as a correction of the same quantity |
| F3 | 2 (attempt 1: record window not in policy) | 0 | **accept** (the alternative-survives case keeps B1 and D1 after efficiency 22 → 18%) |
| F6 | **not attempted:** the guard refused ($0.897 + $0.143 worst case > $1.00) | — | — |

- **Gate over the three rendered:** worse heuristic 0.23 (word-only 0.23, policy-assisted 0.15); 2 soft echoes.
- **Status:** the declared four-scenario scope is incomplete until F6 is rendered. The gate over three is reported, not claimed as a pass for four.

### 19h. Pilot-4b F6 (2026-10-20): failed both attempts; four-scenario pilot not complete

- **Approved by the user:** raise the cumulative cap to $1.20; F6 only; v10 unchanged.
- **Run:** `--run pilot4b-render-v10-f6 --only F6-000 --max-attempts 2 --budget-usd 1.20 --prior-spend-usd 0.897`. Outputs are in `data/rendered/pilot4b-render-v10-f6/`; both raw responses are kept.

| Attempt | Tokens in / out | Cost | Hard flags | Assessment |
|---|---|---|---|---|
| 1 | 4,143 / 9,659 | $0.1180 | `record_scope_not_in_policy` E4→D1: "record none, clause national" | **False positive of the check.** Policy: "Listing in **national** inventory schedules is granted to equipment with primary hospital qualification carrying a guarantee period of 4 years or higher." The scope word belongs to the outcome's name; `_RECORD_CLAUSE_SPLIT` did not separate the outcome from the condition (no split at "granted to … with … carrying"). The record (scope none) was right. No other hard flag |
| 2 (with the attempt-1 feedback) | 4,182 / 7,593 | $0.0948 | `reliability_word` in E3's source; `decoy_shares_memory_word` "authorization, transport" | Genuine under the existing word checks: a decoy about "heavy transport authorization" against memories using "authorized" and "transport"; the banned word "reliability" in a source |

- **Cumulative spend:** $1.1098 of $1.20. No further call fits the guard's worst case.
- **Outcome:**
  - F6 is not rendered, so the **four-scenario pilot is not complete** and the four-scenario gate is unscored.
  - F1, F2 and F3 remain accepted (§19g; gate over those three 0.23, reported only).
  - Nothing is retroactively passed. The 40-scenario run stays unauthorised.
- **Observations (nothing applied):**
  - **Check bug:** scope words in an *outcome name* ("national inventory schedules", "international commercial readiness") can be attributed to a condition. Candidate fixes: make "record none vs a scope word in the clause" soft (a stated *different* scope stays hard), or split clauses at "granted to / awarded to / with". Either must be declared before the next run and must not be used to re-judge this one.
  - **The word-level hard checks remain the main cause of rejection:** pilot-3 F1 ("sales", "reliability"), pilot-4b F1 attempt 1, F6 attempt 2. Each whole-scenario retry re-rolls every check (§18g). Using the targeted repair (§18h, shown to work once) as attempt 2 would address this.
