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
