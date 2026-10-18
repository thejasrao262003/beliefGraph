# BeliefGraph — Research Specification v0.1

*Status (2026-10-18): literature audit + novelty gate done. Scenario generator, deterministic gold labeller, no-LLM baselines and metrics implemented (`src/beliefbench`; pilot-1 results in §5). No LLM system yet. Verification debt (§1) still open.*

---

## 0. TL;DR

- **Verdict: conditional GO, with a narrower claim than the original pitch.**
- "A graph of beliefs that propagates revisions downstream" is **not novel**. Kumiho, Atlas, PACMI, Revok, Lemmalog and NeuSymMS all do some version of it.
- "Keep a conclusion that still has independent support" is **not novel as an algorithm** either. It is the core of classical truth maintenance (Doyle's JTMS, 1979; de Kleer's ATMS, 1986), and Datalog DRed-style retraction already does it in software.
- **The gap that remains is empirical and LLM-specific.** No peer-reviewed LLM-agent work evaluates *selective* revision, meaning it measures both stale conclusions **and** over-invalidated, independently supported conclusions, under:
  1. **branching / multi-support dependency structures** (PACMI explicitly cannot test over-invalidation);
  2. **dependency edges and justification types induced by the LLM**, not supplied by annotation (PACMI, Atlas and Kumiho all assume edges are given);
  3. **incomplete or ambiguous evidence**, where "uncertain" is the correct answer rather than revise or keep;
  4. **recomputing** the downstream conclusion, not just flagging it (PACMI and Kumiho flag; the "re-derivation gap" paper shows flagging is not enough).
- **Critical consequence for the design:** if dependency edges are given as ground truth, the proposed method collapses to a JTMS and the result is a foregone conclusion. The research is only interesting where **justification structure must be inferred from text**. The method, benchmark and ablations must be built around that.
- **Scoop risk is high.** PACMI (5 Oct 2026) lists "deeper and branching dependencies" as future work. Move quickly, and position the work as complementary to PACMI.

---

## 1. Literature matrix

Legend: ✅ demonstrated · ◐ partial / claimed without evaluation · ✗ absent · ? not verified

| Work | Type / status | Explicit dep. graph | Edges induced from text | Multi-support (OR) preserved | Recompute vs flag | Uncertain / ambiguous evidence | Measures over-invalidation | Measures stale downstream | Cost metric |
|---|---|---|---|---|---|---|---|---|---|
| **PACMI** (Wang et al., arXiv 2610.05732, Oct 2026) | Method + 100-case benchmark, preprint | ✅ supports / used-by | ✗ annotation (assumption A1) | ✗ max-state rule; one lost support → needs-verification | Flag only ("non-destructive") | ✗ | ✗ "cannot be tested" (fixed 2-hop topology) | ✅ | ✗ (LLM call counts only) |
| **Kumiho** (Park, arXiv 2603.17244, Mar 2026) | Architecture + AGM proofs, preprint | ✅ Depends_On / Derived_From / Supersedes | ✗ (NL→triple is "lossy by design") | ✗ | Flag (AnalyzeImpact is query-time, read-only) | ✗ | ✗ | ✗ (LoCoMo QA + 49 AGM compliance tests) | ◐ traversal latency |
| **Atlas / Ripple** (Schefren, GitHub, alpha) | Open-source system | ✅ Depends_On + strength | ✗ "does not infer dependency edges" | ? not described | ◐ damped confidence update → proposals; not auto-applied | ◐ heuristic confidence | ✗ | ◐ self-authored BusinessMemBench (synthetic, 149 Q) | ✗ |
| **Agents Retrieve but Do Not Re-Derive** (Goswami et al., NeurIPS 2026) | Empirical + GuardWrite protocol | ◐ validity predicates at write time | ✗ | ✗ not tested | ✅ rewrite with corrected conclusion | ◐ safe refusal | ✗ | ✅ 91–100% stale-following on premise entries | ✗ |
| **STALE** (Chao et al., arXiv 2605.06527) | Benchmark, 400 scenarios | ✗ | n/a | ✗ no "should stay valid" cases | n/a | ◐ CUPMem can block uncertain updates | ✗ | ✅ Type II "propagated" conflicts, IPA probe | ✗ |
| **StateAuditor** (Sun & He, arXiv 2608.01619) | Method on STALE | ✗ | ◐ LLM proposes transitions | ✗ | ✅ repairs response | ✗ | ◐ "false invalidation controlled" | ✅ | ◐ matched call budget |
| **BeliefShift** (Myakala et al., arXiv 2603.23848) | Benchmark, 2,400 trajectories | ✗ | n/a | ✗ | n/a | ✗ binary evidence (stated limitation) | ✗ | ✗ directly revised belief only | ✗ |
| **BeliefMem (AGM)** (Meng, Wu, McAuley; ACL ARR 2026) | Memory system, under review | ◐ predecessor pointers | ◐ LLM resolver (EXP/REV/DUP/CON) | ✗ | n/a | ✗ | ✗ | ✗ (LoCoMo, BEAM) | ✗ |
| **Belief Memory** (Liao et al., arXiv 2605.05583) | Probabilistic memory | ✗ independent candidates | ◐ | ◐ Noisy-OR combines evidence | n/a | ✅ probabilities | ✗ | ✗ | ✗ |
| **Invalidation Contracts** (Wu & Canedo, arXiv 2609.00243) | Protocol, API caches | ✅ dependency vectors | ✗ server-declared | n/a | Evict | ✗ | ✅ eviction precision (table 0.25 vs row 1.00) | ✅ | ✅ tokens |
| **EvolveBench** (Zhu et al., ACL 2025) | Temporal-awareness benchmark | ✗ | n/a | ✗ | n/a | ◐ temporal misalignment | ✗ | ✗ | ✗ |
| **MQuAKE / RippleEdits / EchoEdit** | Parametric knowledge editing | ◐ RippleGraph (EchoEdit) | — | ✗ | — | ✗ | ◐ RippleEdits "relation specificity" | ✅ multi-hop | ✗ |
| **Graphiti / Zep** | Temporal KG product | ✅ bi-temporal edges | ✅ LLM extraction | ✗ edge-level invalidation only | Invalidate edge | ✗ | ✗ | ✗ | ✗ |
| **Revok** (PyPI, 2026) | Library | ✅ causal graph, BFS | ✗ | ? not described | Degrade confidence | ◐ decay + pressure | ✗ | ✗ no eval | ✗ |
| **Lemmalog** (GitHub) | Datalog memory engine | ✅ rules + provenance | ◐ LLM extracts facts, not rules | ◐ DRed-lite re-derivation (likely preserves alt. derivations) | ✅ re-derive | ◐ confidence on facts | ✗ | ◐ LongMemEval knowledge-update | ✗ |
| **NeuSymMS** (arXiv 2605.17596), **SSGM** (arXiv 2603.11768), **Veritas-TMS** (PyPI) | TMS-style memory | ✅ | ◐ | ◐ Veritas claims "unless it stands on its own source" (page failed to load, **unverified**) | ✅ retract | ✗ | ✗ | ✗ | ✗ |
| **Classical JTMS / ATMS** (Doyle 1979; de Kleer 1986) | Theory | ✅ | ✗ | ✅ **this is the core idea** | ✅ | ATMS: assumption sets | — | — | ✅ complexity |

### What the matrix says

1. **Column "Multi-support preserved" + "Measures over-invalidation" is empty for LLM-agent work.** Classical TMS has the mechanism. No LLM-agent paper has measured it. The closest measurement is eviction precision in Invalidation Contracts, but there the edges are declared by an API server.
2. **Column "Edges induced from text" is the real bottleneck.** Every system with a correct propagation rule gets its dependency edges from a human or a server. Nobody has measured how revision quality degrades when an LLM must infer *which* premises a conclusion rests on and *whether* they are jointly necessary (AND) or alternatives (OR).
3. **Flag vs recompute matters.** The re-derivation gap paper shows agents follow stale conclusions even when premises are updated, so flagging (PACMI, Kumiho) leaves the hard part undone.

### Still to read before the spec freezes (verification debt)

- [ ] PACMI §5–7 in full, and its released code if any. It is the main baseline and the main scoop risk.
- [ ] Kumiho §15–16 (limitations / future work were truncated in my read).
- [ ] Atlas source code: how the Ripple formula treats multiple Depends_On parents.
- [ ] Veritas-TMS docs (page failed to load) and Lemmalog's DRed-lite: do they handle OR-support correctly?
- [ ] "Agents Retrieve but Do Not Re-Derive": full paper, especially whether any condition has independent support.
- [ ] RippleEdits (Cohen et al., 2024): its "preservation" checks are the closest prior metric to over-invalidation in the parametric setting.
- [ ] Classical: Doyle (1979), de Kleer (1986), Gärdenfors & Rott on AGM base revision, Hansson's belief bases. Needed to state precisely what is *borrowed*.
- [ ] One more sweep (Nov 2026) for anything citing PACMI.

---

## 2. Novelty gate

**Proposed contribution (revised):**

> We study *selective* belief revision in LLM agents, where a new piece of evidence should withdraw some beliefs, trigger recomputation of some conclusions, leave others intact because they have independent support, and mark others uncertain. We (i) introduce a benchmark with branching, multi-support, and ambiguous-evidence dependency structures, labelled with gold revision actions for every node; (ii) show that existing approaches fail in opposite directions, with flat LLM memory leaving stale conclusions and descendant-cascade methods destroying supported ones; and (iii) propose justification-aware revision, where the LLM induces typed justifications (AND-premises within a justification, OR across justifications) at write time and a TMS-style label propagation decides keep / recompute / withdraw / uncertain. We quantify how much of the remaining error comes from justification induction rather than propagation.

**Closest competitors and what they do not show:**

| Competitor | What it lacks that we must demonstrate |
|---|---|
| PACMI | Over-invalidation on multi-support nodes; induced edges; recomputation; uncertain evidence |
| Re-derivation gap / GuardWrite | Dependency structure beyond a single predicate; independent support |
| Kumiho / Atlas | Any empirical evaluation of propagation correctness |
| Classical JTMS | An LLM in the loop: justifications from natural language, and natural-language recomputation |

**Gate criteria (all must hold to proceed past the pilot):**

1. Final read of PACMI and the re-derivation-gap paper confirms neither measures preservation of independently supported conclusions.
2. In the pilot, the naive-cascade baseline has a **meaningfully high** over-invalidation rate and flat LLM memory has a **meaningfully high** stale rate. If both baselines are already fine, there is no problem to solve.
3. In the pilot, **oracle-edge JTMS ≫ LLM-induced-edge JTMS**. If induction is trivially easy, the contribution shrinks to "use a JTMS", which is not a paper.

**Kill / pivot conditions:**

- A paper appears that measures over-invalidation with induced justifications. Pivot to the uncertain/ambiguous-evidence track, or to cost-optimal recomputation.
- Gate criterion 3 fails. Pivot to a benchmark-only contribution (still publishable as a datasets & benchmarks paper if it exposes failures in current systems).

---

## 3. Research questions & hypotheses

- **RQ1:** Do current LLM-agent memory approaches make *opposite* errors under evidence change? Flat memory under-revises; descendant-cascade over-revises.
  - *H1:* Naive cascade has an over-invalidation rate ≥ 30% on multi-support cases. Flat LLM memory has a stale-conclusion rate ≥ 30% on depth ≥ 2 cases.
- **RQ2:** Does justification-aware (AND/OR) revision reduce both error types at once?
  - *H2:* It dominates both baselines on stale-rate *and* over-invalidation-rate (a Pareto improvement), not just a trade-off.
- **RQ3:** How much of the remaining error comes from justification induction?
  - *H3:* The oracle-edge vs induced-edge gap accounts for most of the proposed method's residual error, and it grows with depth and fan-in.
- **RQ4:** Does recompute beat flag on downstream decision accuracy, and at what cost?
  - *H4:* Recompute improves decision accuracy over flag-only. Selective recompute reaches it with far fewer LLM calls than recomputing everything.

The thresholds in H1 are placeholders for the pilot to calibrate, not commitments.

---

## 4. Benchmark specification (BeliefGraph-Bench)

### 4.1 Unit: a scenario

```yaml
scenario_id: thai-product-x-017
domain: product_eligibility          # 5 domains, see 4.4
evidence:                            # what the agent saw, in order
  - {id: E1, t: 1, source: catalog_2026Q1, reliability: high, text: "Product X is available in Thailand."}
  - {id: E2, t: 2, source: policy_doc,     reliability: high, text: "Product X is offered to customers aged 18-60."}
  - {id: E4, t: 3, source: regional_api,   reliability: high, text: "Product X is stocked by the Bangkok partner network."}
beliefs:                             # what the agent derived (rendered as NL memories)
  - {id: B1, text: "Product X is available in Thailand.",
     justifications: [[E1], [E4]]}   # OR of ANDs: E1 alone, OR E4 alone
  - {id: B2, text: "Customer C (age 34, Thailand) is eligible for X.",
     justifications: [[B1, E2]]}     # AND
  - {id: D1, text: "Recommend Product X to customer C.", kind: decision,
     justifications: [[B2]]}
update:
  - {id: E3, t: 4, source: catalog_2026Q3, reliability: high,
     text: "Product X is no longer listed in the Thai catalog.",
     relation: {target: E1, type: retracts}}
gold:                                # per-node gold action after the update
  E1: withdraw
  B1: keep          # still supported by E4  <- the case naive cascade gets wrong
  B2: keep
  D1: keep
probes:                              # downstream questions answered after revision
  - {q: "Should we recommend Product X to customer C?", gold: "yes"}
  - {q: "Why is X still considered available in Thailand?", gold_support: [E4]}
```

Gold actions per node: `keep` · `withdraw` · `recompute` (premises changed; the conclusion must be re-derived and may flip) · `uncertain` (evidence insufficient to decide) · `supersede` (replaced by a new value).

### 4.2 Scenario families (controlled factors)

| Family | What varies | Why it matters |
|---|---|---|
| F1 Chain depth | Depth 1–5, single support | Staleness baseline; replicates PACMI and STALE Type II |
| F2 Independent support | Fan-in 2–4 OR-justifications; retract 1..k of them | **Core case**: over-invalidation |
| F3 Conjunctive premises | AND-justifications; retract one premise | Must recompute even though other premises hold |
| F4 Diamond / multi-path | Shared ancestors reaching a node by several paths | Multi-path resolution (untested in PACMI) |
| F5 Recompute-and-flip | Premise changes value (not just retracted); conclusion must be re-derived | Flag vs recompute |
| F6 Ambiguous / partial update | Update is hedged, scoped ("in Bangkok"), or from a low-reliability source | Gold = `uncertain` or scoped keep |
| F7 Outdated update | The "new" evidence is actually older than the retained support (bi-temporal) | Recency ≠ validity |
| F8 Distractors | Topically similar but unrelated evidence | Precision of impact analysis |

Each scenario family is also generated in **implicit** form: justifications are *not* given and the system sees only evidence and derived memories as text. This is the main track. The explicit form, with justifications given, is the oracle track.

### 4.3 Ground truth

- Scenarios are generated **from the graph first**: sample a justification structure, then compute gold labels deterministically with a JTMS. Only afterwards are the nodes rendered to natural language with an LLM.
- Validate the NL rendering: ≥ 2 human annotators on a ≥ 10% sample check that the text actually entails the intended justification structure. Report agreement (κ). Cases where the text doesn't support the graph are dropped.
- **Labelling semantics** (implemented in `labeler.py`): three-valued JTMS-style propagation over the total order `OUT < UNK < STALE < IN`. An AND-justification takes the min over its premises; a node takes the max over its justifications. Update effect on its target evidence: older than the target (valid time) → ignored; hedged, or less reliable than the target → `UNK`; `retracts` → `OUT`; `supersedes` → `STALE`. Status maps to action as IN→keep, STALE→recompute, UNK→uncertain, OUT→withdraw. Targeted evidence gets withdraw / supersede / uncertain. Updates target evidence only (base revision); derived nodes change only through propagation.
- This makes labels in the **explicit** track a function of topology. PACMI flags this as a weakness of its benchmark, so the explicit track is a sanity/upper-bound track only. The **implicit** track is the real test.

### 4.4 Domains & size (target)

5 domains (product eligibility, travel/logistics, medical-administrative (non-clinical), software dependency/config, personal preferences) × 8 families × ~25 scenarios ≈ **1,000 scenarios**. Pilot: **5 per family in 2 domains = 80**.

### 4.5 Metrics

Per node, with gold action *g* and predicted action *p*:

| Metric | Definition |
|---|---|
| **Revision accuracy** | Macro-F1 over {keep, withdraw, recompute, uncertain, supersede} |
| **Stale-conclusion rate (SCR)** | Fraction of nodes with g ∈ {withdraw, recompute, supersede, uncertain} that the system leaves as keep |
| **Over-invalidation rate (OIR)** | Fraction of nodes with g = keep that the system withdraws, recomputes or marks uncertain |
| **Support-preservation recall** | On F2: fraction of OR-supported nodes correctly kept *and* attributed to the surviving support |
| **Calibration on F6** | Precision/recall of `uncertain` |
| **Downstream decision accuracy** | Accuracy on probe questions (LLM judge from a *different* model family than the system, plus a human-checked subset) |
| **Recomputation cost** | LLM calls and tokens per update; nodes touched per update |

Report SCR vs OIR as a 2-D plot. The claim is a Pareto improvement. **Plain accuracy is not a headline metric.** It is dominated by trivially-kept nodes (untargeted evidence, distractors). In pilot-1, a 50% extraction-error rate still scored 0.91 accuracy, while SCR rose to 0.31.

**Justification extraction is scored separately from revision** (implemented in `metrics.py`). Otherwise good propagation can hide poor extraction, or good extraction can hide weak revision logic:

| Extraction metric | Definition |
|---|---|
| Edge F1 | Over (premise → conclusion) pairs |
| Justification-set F1 | Over whole AND-sets, as (conclusion, frozenset(premises)) |
| Node exact match | Fraction of derived nodes whose full OR-of-ANDs structure is recovered |
| AND/OR typing accuracy | Over gold premise pairs of a node where both premises were extracted: are they recovered as conjoint vs alternative? |
| Affected-region set F1 | Justification-set F1 restricted to descendants of the updated evidence |

**Error decomposition.** For any system that exposes its justifications, also score the *implied* actions: correct propagation run over its predicted justifications (`gold_actions(s, predicted)`). Then:
- gold − implied = error caused by extraction;
- implied − end-to-end = error caused by revision logic / recomputation.

Report both for every system that exposes justifications (P, S4, S5). For systems that don't expose them (S1–S3, S6), report end-to-end only, and say so.

### 4.6 Systems compared

All systems use the **same base LLM** and see the **same evidence stream**.

| # | System | Description |
|---|---|---|
| S1 | Vector RAG | Retrieve evidence + memories at query time; no revision |
| S2 | Recency RAG | S1 with newest-wins on conflicts |
| S3 | Flat LLM memory | LLM rewrites a memory list on each update (Mem0-style ADD/UPDATE/DELETE) |
| S4 | Naive cascade | Explicit graph; withdraw every descendant of the changed node |
| S5 | PACMI-style lattice | Reimplementation of PACMI's 4-state propagation (or their code, if released) |
| S6 | Re-derive-all | Recompute every belief from current evidence after each update (accuracy ceiling for LLM-only; cost ceiling) |
| **P** | **Justification-aware revision** | LLM induces OR-of-AND justifications at write time; TMS label propagation decides; LLM recomputes only nodes labelled recompute; LLM adjudicates `uncertain` on F6 |
| P-oracle | P with gold justifications | Upper bound; isolates induction error |

**Ablations of P:** AND/OR → single-parent edges · no recompute (flag only) · no uncertain state · induced edges at write time vs lazily at update time · source reliability ignored.

### 4.7 Statistics

- 3 seeds × temperature > 0, or report the temperature-0 nondeterminism explicitly.
- Paired tests per scenario (McNemar for accuracy; paired bootstrap 95% CIs for SCR/OIR).
- Pre-register H1–H4 thresholds after the pilot and before the full run.
- At least 2 base-model families (e.g. a Claude model + an open-weights model) so results are not tied to one model.

---

## 5. Pilot plan (next steps)

1. **Finish the verification-debt reads** (§1 checklist). Update the matrix. Re-run the gate. *(~1 week)*
2. ~~**Scenario generator v0**: graph sampler + JTMS gold labeller for F1, F2, F3, F6. 40 scenarios.~~ **Done**, without NL rendering. See pilot-1 below.
2b. **NL renderer** (the first step that costs model calls): render each graph to evidence and memory text without stating its justification structure. Use a different model family from the systems under test.
3. **Hand-check 40 scenarios** for rendering fidelity.
4. **Run S3, S4, P-oracle, and a first P** on the 40 scenarios.
5. **Gate check:** H1 is directionally true (S3 high SCR, S4 high OIR). P-oracle ≫ P (induction is non-trivial). If not, apply the kill/pivot rules in §2.
6. Only then: remaining families, remaining baselines, full benchmark.

### Pilot-1: graph-only, no LLM (seed 0, 10 scenarios × F1/F2/F3/F6)

Reproduce: `uv run beliefbench generate --n-per-family 10 --seed 0 --out data/pilot.jsonl && uv run beliefbench evaluate data/pilot.jsonl --by-family`

| System (all 40) | acc | macro-F1 | SCR | OIR | jset-F1 |
|---|---|---|---|---|---|
| direct_only (revise the target, never propagate) | 0.858 | 0.584 | 0.505 | 0.000 | – |
| naive_cascade (withdraw all descendants) | 0.746 | 0.516 | 0.000 | 0.185 | – |
| oracle JTMS (sanity check) | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 |
| JTMS + simulated extraction error @ 0.25 | 0.910 | 0.829 | 0.277 | 0.029 | 0.784 |
| JTMS + simulated extraction error @ 0.5 | 0.912 | 0.826 | 0.307 | 0.016 | 0.627 |

Naive cascade's OIR by family: F1 0.00, F2 0.24, F3 0.18, F6 0.28.

What pilot-1 does and doesn't show:
- The benchmark separates the two failure directions as designed: one system leaves conclusions stale, the other over-invalidates. These are rule-based stand-ins for S3 and S4, though, so **H1 is not yet tested**. It needs the LLM systems.
- Extraction errors show up mainly as **staleness**, not over-invalidation: an unlinked or mis-typed node is often left as keep. This suggests induced-edge systems will fail toward under-revision, which is worth checking with real extraction.
- The 0.25 and 0.5 rows aren't monotonic. That's one seed on 40 scenarios with uniform perturbation. Use several seeds before reading the curve.
- Simulated perturbations are not LLM errors. They only show the scoring pipeline can detect extraction damage.

---

## 6. Threats to validity

- **Synthetic rendering artefacts**: the LLM that renders scenarios may leak structure through wording that the system LLM picks up. Mitigations: use different model families for rendering and evaluation, paraphrase, and run a human check.
- **Judge bias**: use a cross-family judge and a human-labelled subset (a known weakness of PACMI).
- **Topology-determined labels**: the explicit track is trivially solved by a JTMS. Report it separately, and never as the headline.
- **Toy scale**: PACMI's 6-memory cases saturated retrieval. Include long-horizon variants with ≥ 100 memories per scenario so retrieval is non-trivial.
- **"It's just a TMS" critique**: address it head-on. State what is borrowed from Doyle and de Kleer and what is new: induction from text, NL recomputation, and the measurement.

---

## Sources

- PACMI — https://arxiv.org/html/2610.05732
- Kumiho — https://arxiv.org/html/2603.17244
- Atlas — https://github.com/RichSchefren/atlas
- BeliefShift — https://arxiv.org/abs/2603.23848
- STALE — https://arxiv.org/abs/2605.06527
- StateAuditor — https://arxiv.org/abs/2608.01619
- Agents Retrieve but Do Not Re-Derive — https://neurips.cc/virtual/2026/170668
- Belief Memory (Noisy-OR) — https://arxiv.org/abs/2605.05583
- BeliefMem (AGM, ARR submission) — https://cseweb.ucsd.edu/~jmcauley/reviews/emnlp26d.pdf
- Invalidation Contracts — https://huggingface.co/papers/2609.00243
- Supersede — https://arxiv.org/html/2606.27472v1
- EvolveBench — https://aclanthology.org/2025.acl-long.788
- MQuAKE — https://aclanthology.org/2023.emnlp-main.971
- EchoEdit — https://ojs.aaai.org/index.php/AAAI/article/view/39013
- Graphiti temporal model — https://mintlify.com/getzep/graphiti/concepts/temporal-model
- Revok — https://pypi.org/project/revok/
- Lemmalog — https://github.com/JordyZomer/lemmalog
- NeuSymMS — https://arxiv.org/pdf/2605.17596
- SSGM — https://arxiv.org/pdf/2603.11768
- Veritas-TMS — https://pypi.org/project/veritas-tms/0.15.0/ (not verified)
