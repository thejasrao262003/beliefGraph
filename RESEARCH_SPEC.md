# BeliefGraph — Research Specification v0.2

*Status (2026-10-18): literature audit + novelty gate done (v0.2). Generator, gold labeller (differentially verified against Veritas-TMS), no-LLM baselines incl. PACMI-style (S5) and Atlas-style (S7), and metrics implemented in `src/beliefbench`; results in §5 (pilot-1, 1b, 1c). No LLM system yet. Verification debt (§1) partly open.*

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
- **Scoop risk is high.** PACMI (5 Oct 2026) App. J explicitly proposes branching topologies, unaffected connected nodes and oracle-vs-induced edges (verified; none run). Veritas-TMS (17 Oct 2026) ships the oracle-edge mechanism. Move quickly, and position the work as complementary to PACMI.
- **v0.2 narrowing (audit 2026-10-18):** the contribution is the *error-type-resolved* study of LLM-induced AND/OR justifications under selective revision, plus a method that targets the costly error types. See §2.

---

## 1. Literature matrix

Legend: ✅ demonstrated · ◐ partial / claimed without evaluation · ✗ absent · ? not verified

| Work | Type / status | Explicit dep. graph | Edges induced from text | Multi-support (OR) preserved | Recompute vs flag | Uncertain / ambiguous evidence | Measures over-invalidation | Measures stale downstream | Cost metric |
|---|---|---|---|---|---|---|---|---|---|
| **PACMI** (Wang et al., arXiv 2610.05732, Oct 2026) | Method + 100-case benchmark, preprint | ✅ supports / used-by | ✗ annotation (assumption A1). **Proposed** in App. J (oracle vs text-induced vs corrupted edges), not run | ✗ max-state rule; one lost support → needs-verification | Flag only ("non-destructive") | ✗ | ✗ "cannot be tested" (fixed 2-hop topology). Branching / unaffected-connected nodes **proposed** in App. J, not run | ✅ | ✗ (LLM call counts only) |
| **Kumiho** (Park, arXiv 2603.17244, Mar 2026) | Architecture + AGM proofs, preprint | ✅ Depends_On / Derived_From / Supersedes | ✗ (NL→triple is "lossy by design") | ✗ | Flag (AnalyzeImpact is query-time, read-only) | ✗ | ✗ | ✗ (LoCoMo QA + 49 AGM compliance tests) | ◐ traversal latency |
| **Atlas / Ripple** (Schefren, GitHub, alpha) | Open-source system | ✅ Depends_On + strength | ✗ "does not infer dependency edges" | ✗ **verified in source**: `reassess.py` perturbs each dependent by `β·strength·Δupstream` per changed edge, with no check for alternative support. Soft over-invalidation by design | ◐ damped confidence update → proposals; not auto-applied | ◐ heuristic confidence | ✗ | ◐ self-authored BusinessMemBench (synthetic, 149 Q) | ✗ |
| **Agents Retrieve but Do Not Re-Derive** (Goswami et al., NeurIPS 2026 **Workshop on Resource-Aware Agentic AI**, poster; full text not yet read) | Empirical + GuardWrite protocol | ◐ validity predicates at write time | ✗ | ✗ not tested | ✅ rewrite with corrected conclusion | ◐ safe refusal | ✗ | ✅ 91–100% stale-following on premise entries | ✗ |
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
| **Lemmalog** (GitHub) | Datalog memory engine | ✅ rules + provenance | ◐ LLM extracts facts. `examples/llm_rules.rs` has the LLM *author rules* from an explicit NL request; not induced from memory text, not evaluated | ✅ verified: retraction clears dependent derived predicates and re-derives from the remaining facts, so alternative derivations survive | ✅ re-derive | ◐ confidence on facts | ✗ | ◐ LongMemEval knowledge-update | ✗ |
| **Veritas-TMS** (PyPI v0.16.0, 2026-10-17, MIT; github.com/Iam-Raghava/veritas) | JTMS library with agent-memory helpers | ✅ Horn-clause justifications | ✗ **caller supplies** `justifications=[...]`; LLM only detects contradictions ("the LLM judges, Veritas still decides") | ✅ **verified in source**: doomed iff *every* justification set has a doomed premise (`store.py`). Entrenchment capped by best proof | ✅ retract / cascade | ◐ entrenchment, calibration tracker | ✗ | ✗ (unit / property / differential tests and throughput only) | ✅ throughput |
| **NeuSymMS** (arXiv 2605.17596), **SSGM** (arXiv 2603.11768) | TMS-style memory | ✅ | ◐ | ? not verified | ✅ retract | ✗ | ✗ | ✗ | ✗ |
| **AGM-Bench** (Jenkins, ICLR 2026 workshop) | In-context LLM benchmark, 2,400 scenarios | ✗ | n/a | ? | n/a | ✗ | ◐ "collateral damage" / Preservation violations reported; scoring procedure not given | ✗ | ✗ |
| **DeltaLogic** (Dhanda, arXiv 2604.02733, ICLR 2026 workshop) | In-context premise-edit episodes (FOLIO / ProofWriter) | ✗ | n/a | ? | n/a | ◐ abstention | ◐ some episodes are stable, but no over-revision metric; reports inertia | ✅ inertia | ✗ |
| **ReviseQA** (Helwe et al., ICML 2025 workshop), **Belief-R** (arXiv 2406.19764) | In-context multi-turn revision | ✗ | n/a | ? not read | n/a | ✗ | ? | ✅ | ✗ |
| **Classical JTMS / ATMS** (Doyle 1979; de Kleer 1986) | Theory | ✅ | ✗ | ✅ **this is the core idea** | ✅ | ATMS: assumption sets | — | — | ✅ complexity |

### What the matrix says

1. **Column "Multi-support preserved" + "Measures over-invalidation" is empty for LLM-agent work.** Classical TMS has the mechanism, and Veritas-TMS ships it as an agent-memory library (with caller-supplied justifications). No LLM-agent paper has measured it. The closest measurement is eviction precision in Invalidation Contracts, but there the edges are declared by an API server. In-context benchmarks (AGM-Bench, DeltaLogic) report related failures (collateral damage, inertia) for a model reasoning over premises in its prompt. That is a different setting from a persistent memory with stored conclusions. *A stated limitation or proposed extension is evidence of an open opportunity, not proof that nobody has solved it.*
2. **Column "Edges induced from text" is the real bottleneck.** Every system with a correct propagation rule gets its dependency edges from a human or a server. Nobody has measured how revision quality degrades when an LLM must infer *which* premises a conclusion rests on and *whether* they are jointly necessary (AND) or alternatives (OR).
3. **Flag vs recompute matters.** The re-derivation gap paper shows agents follow stale conclusions even when premises are updated, so flagging (PACMI, Kumiho) leaves the hard part undone.

### Still to read before the spec freezes (verification debt)

- [x] PACMI full paper, including App. J. Verified 2026-10-18: App. J *proposes* (i) depth > 2, branching and confluence, plus unaffected dependency-connected nodes to measure over-invalidation; (ii) oracle vs text-induced vs corrupted edges; (iii) larger memory stores; (iv) more backbones, a cross-family judge and a human study. **None were run.** Nothing on AND/OR, alternative support, recomputation or uncertainty. Ablation without cascading: 3 vs 11 errors / 300 queries, p = 0.0574. Code release: not checked.
- [ ] Kumiho §15–16 (limitations / future work were truncated in my read).
- [x] Atlas source (`atlas_core/ripple/reassess.py`, `analyze_impact.py`): BFS over incoming DEPENDS_ON edges, then a per-dependent damped additive update. No alternative-support logic.
- [x] Veritas-TMS (`veritas/store.py`): correct OR-of-AND JTMS doom check; justifications supplied by the caller. Lemmalog (`src/eval.rs`): retraction → clear dependent derived predicates → re-derive.
- [ ] "Agents Retrieve but Do Not Re-Derive": full paper. **Blocked**: the NeurIPS page links only OpenReview (`forum?id=vNQcrBtiMb`), which serves a browser challenge to automated fetches, and there is no arXiv version. Download the PDF manually. Confirmed: workshop poster, not main track.
- [ ] AGM-Bench: how "collateral damage" is scored, and whether any scenarios contain derived beliefs with alternative support.
- [ ] RippleEdits (Cohen et al., 2024): its "preservation" checks are the closest prior metric to over-invalidation in the parametric setting.
- [~] Classical: Doyle (1979), de Kleer (1986), Gärdenfors & Rott on AGM base revision, Hansson's belief bases. Summary below is from standard knowledge of these works; primary texts still to be read for exact citations.
  - *JTMS* (Doyle, "A Truth Maintenance System", AIJ 12, 1979): a node is IN iff some justification is valid (all IN-list premises IN, all OUT-list premises OUT). Retraction relabels the affected nodes. **Borrowed by us:** OR-of-AND support semantics (our labeller is a monotone JTMS with no OUT-lists, extended with UNK and STALE).
  - *ATMS* (de Kleer, AIJ 28, 1986): each node carries a label, the minimal sets of assumptions under which it holds. Multiple contexts coexist without retraction. **Relevant to F6:** an `uncertain` node can be represented as "holds under assumption {E is still valid}" rather than flattened to UNK. This is a possible refinement, not adopted yet.
  - **Not in either:** where justifications come from. Both assume the problem solver hands them over. That is exactly the step an LLM agent has to perform from text.
- [ ] One more sweep (Nov 2026) for anything citing PACMI.

---

## 2. Novelty gate

**Proposed contribution (v0.2, narrowed after the 2026-10-18 audit):**

> When an LLM agent must infer *why* it holds each stored conclusion, which premises it needs jointly (AND) and which are alternatives (OR), how do errors in that inferred structure affect selective revision? We (i) measure the real distribution of LLM justification-induction errors *by type*, on controlled scenarios where some descendants of a changed fact must be revised and others stay independently supported; (ii) show that the error type decides the failure direction: missing links and AND→OR confusion leave stale conclusions, while OR→AND confusion and missed alternatives destroy supported ones (pilot-1b shows this with simulated errors; the LLM pilot must confirm it with real ones); and (iii) test whether a revision procedure that targets the costly error types improves the stale / over-invalidation trade-off over credible baselines.

What this deliberately does **not** claim:
- Propagation through dependencies: established (PACMI, Kumiho, Atlas, JTMS).
- Preserving independently supported conclusions: established mechanism (JTMS 1979; shipped in Veritas-TMS).
- Running branching topologies or oracle-vs-induced edges *as such*: proposed in PACMI App. J. Doing these is necessary for our study, but they are not the novelty.
- Separating extraction error from revision error: good experimental design, not a contribution by itself.
- Uncertainty handling and NL recomputation: included only as far as the pilot can test them meaningfully. Otherwise they are future work.

Candidate method for (iii), to be fixed only after the LLM pilot shows the real error mix: induce justifications at write time, propagate with the JTMS labeller, then run **asymmetric verification at update time**. Before withdrawing or recomputing a node, re-check the remaining evidence for an alternative support (this targets OR→AND errors and missed alternatives). After an update, re-check affected-region nodes that have no extracted link to the change (this targets unlink errors). Cost: LLM calls only on the affected region.

#### Positioning against the closest work

| Work | What it establishes | What it leaves open, relevant to us | How we use / differ |
|---|---|---|---|
| **PACMI** (arXiv 2610.05732) | Typed provenance graph + 4-state validity lattice; validity-aware retrieval; premise checker. 100 cases, fixed 2-hop chain, annotated edges | Over-invalidation untestable by construction; App. J *proposes* branching, unaffected connected nodes and induced/corrupted edges, but none were run. No AND/OR, no alternative support, flag-only | Baseline S5. We run its proposed axes as a means, and add AND/OR typing, error-type decomposition and alternative-support cases |
| **Re-derivation gap / GuardWrite** (NeurIPS 2026 workshop) | Agents follow stale *conclusions* when only premises change (91–100% on mid-scale models); validity predicates + rewrite fix it | (Abstract only; full text unread.) No evidence of alternative support or branching. It assumes we already know *which* entries are invalid | Motivates recompute over flag. We address the step before it: deciding which conclusions are still justified |
| **Veritas-TMS** (v0.16.0) | Correct OR-of-AND JTMS for agent memory, entrenchment, LLM contradiction detection | Justifications are supplied by the caller; no revision-correctness benchmark | Reference implementation of our oracle track. Differential-test our labeller against it. It is the "if edges were given, a TMS solves it" point made concrete |
| **Classical JTMS / ATMS** | The propagation semantics we borrow | Where justifications come from | Cite as the source of the mechanism; ATMS labels are a candidate refinement for F6 |
| **Atlas / Ripple** | Engineered propagation: BFS + damped per-edge confidence updates | No alternative-support check (verified in source); self-authored eval only | Add as a soft-propagation baseline (S7). Prediction: OIR > 0 on F2 even with correct edges |
| **Lemmalog** | Datalog re-derivation preserves alternative derivations; LLM can author rules on request | No induction from memory text; no revision evaluation | Shows rule-level induction is feasible. Our setting is instance-level justifications from stored NL memories |
| **AGM-Bench, DeltaLogic, ReviseQA** | In-context LLMs show collateral damage, inertia and inconsistency under premise edits | Premises sit in the prompt, with no persistent memory of stored conclusions | Related failure modes in a different setting; cite, and contrast with persistent memory |

**Closest competitors and what they do not show:**

| Competitor | What it lacks that we must demonstrate |
|---|---|
| PACMI | Over-invalidation on multi-support nodes (proposed, not run); induced edges (proposed, not run); **AND/OR typing and error-type effects (not proposed)**; recomputation; uncertain evidence |
| Re-derivation gap / GuardWrite | Dependency structure beyond a single predicate; independent support (pending full-text check) |
| Kumiho / Atlas | Any empirical evaluation of propagation correctness |
| Classical JTMS / Veritas-TMS | An LLM in the loop: justifications from natural language, and how their errors propagate |

**Gate criteria (all must hold to proceed past the pilot):**

1. Final read of PACMI and the re-derivation-gap paper confirms neither measures preservation of independently supported conclusions. *PACMI: confirmed 2026-10-18 (proposed in App. J, not run). Re-derivation gap: pending the full text.*
2. The benchmark produces the opposing failures across seeds. *Confirmed at the rule-based level in pilot-1b (20 seeds).* Still needed: flat LLM memory shows high SCR and naive cascade shows high OIR with real LLM systems.
3. Real LLM justification induction is **measurably imperfect** on the controlled scenarios, *and* its error mix includes the types that matter (pilot-1b shows the direction depends on type). If induction is near-perfect, the contribution shrinks to "use a JTMS", which is not a paper.
4. The proposed method improves the SCR/OIR trade-off over **credible** baselines (PACMI-style, Atlas-style, flat LLM memory, re-derive-all), not just over the deliberately simple rules.
5. Before the renderer spend: a fresh search (≥ 2026-11) for work citing PACMI or running its App. J extensions.

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
| S7 | Atlas-style soft propagation | BFS over dependents + damped per-edge confidence update (`α, β·strength·Δ`). Native discrete mapping uses Atlas's own routing floor (\|Δ\| ≥ 0.15 → flagged); plus a threshold sweep on applied confidences |

**S5 / S7 implementation notes** (`src/beliefbench/prior_art.py`, pinned by `tests/test_prior_art.py`):

- *S5 faithful:* direct targets → superseded; `supports` → needs-verification, `used-by` → historical-only; on multiple paths the stronger state wins; no AND/OR reasoning.
  - **A-P1** (adaptation): our graphs have no edge types, so an edge into a decision is `used-by` and every other edge is `supports`.
  - **A-P2** (assumption): "stronger" follows the paper's listing order, active < needs-verification < historical-only < superseded.
  - **A-P3** (adaptation): PACMI has no reliability, recency or hedge handling, so every update makes its target superseded.
  - **A-P4** (prespecified mapping): active→keep, needs-verification→recompute (alternative: uncertain; SCR/OIR identical under either), historical-only→withdraw, superseded→withdraw or supersede.
- *S7 faithful (from `reassess.py`, `analyze_impact.py`, `adjudication.py`):* default weights α 0.5, β 0.3, γ 0.15, δ 0.05; the `HeuristicReassessor` (Δ clipped to ±0.5); decay(None) = 0.5; BFS depth cap 10. Every impacted node is reassessed against the *origin's* Δ with strength 1.0. Proposals are not written back (Atlas has no automatic consumer). Routing: \|Δ\| ≥ 0.15 → strategic review.
  - **A-A1** (adaptation): all nodes start at confidence c0 = 0.8.
  - **A-A2** (adaptation): retracts / supersedes set the target to 0; hedges halve it; reliability and recency are ignored, since Atlas has neither.
  - **A-A3** (mapping): a flagged node gets the gold class of its cause (charitable; affects macro-F1 only).
  - The threshold sweep applies all proposals sequentially and revises a node iff its final confidence < τ.
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

1. **Finish the verification-debt reads** (§1 checklist). Update the matrix. Re-run the gate. *Mostly done 2026-10-18. Still open: the full re-derivation-gap paper (manual PDF download), AGM-Bench scoring, Kumiho §15–16, and primary JTMS/ATMS texts.*
1b. ~~**Model-free checks:** differential-test `labeler.py` against Veritas-TMS; implement S5 (PACMI lattice) and S7 (Atlas-style) as deterministic baselines.~~ **Done**, see pilot-1c.
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
- The 0.25 and 0.5 rows looked non-monotonic. Pilot-1b below resolves this: it was noise, and only in accuracy and single-family metrics.
- Simulated perturbations are not LLM errors. They only show the scoring pipeline can detect extraction damage.

### Pilot-1b: seed stability (20 seeds × 40 scenarios; generator, labeller and metrics unchanged)

Reproduce: `uv run python scripts/seed_stability.py --seeds 20`. Full output is in `data/seed-stability.results.txt`. Values are the mean ±95% CI over seeds.

| System (all families) | SCR | OIR | macro-F1 |
|---|---|---|---|
| direct_only | 0.565 ±0.015 | 0.000 | 0.564 ±0.011 |
| naive_cascade | 0.000 | 0.160 ±0.009 | 0.551 ±0.011 |
| extraction error @ 0.1 | 0.092 ±0.017 | 0.006 ±0.003 | 0.950 ±0.009 |
| extraction error @ 0.25 | 0.205 ±0.022 | 0.013 ±0.006 | 0.882 ±0.017 |
| extraction error @ 0.5 | 0.384 ±0.020 | 0.019 ±0.005 | 0.770 ±0.014 |

Naive cascade's OIR by family: F1 0.000 · F2 **0.271 ±0.019** · F3 0.144 ±0.013 · F6 0.165 ±0.028.

- **The opposing failures hold across seeds**, with tight intervals (first go/no-go condition, at the rule-based level).
- **The pilot-1 "reversal" was noise.** With all 40 scenarios pooled, SCR and macro-F1 degrade from 0.25 to 0.5 in 20/20 seeds; plain accuracy flips in 2/20. Within one family (10 scenarios), a metric moves the wrong way in 1–5/20 seeds. *Correction:* pilot-1's overall SCR was in fact monotonic (0.277 → 0.307); the non-monotonic numbers were accuracy and F1's per-family SCR. Note too that `cli evaluate --by-family` re-draws the perturbations for each family, so its per-family numbers differ from slices of the pooled run. Neither is wrong, but they are not comparable.
- **The direction of failure depends on the error type** (one error type at a time, rate 0.5):

| Extraction error | SCR | OIR | Fails toward |
|---|---|---|---|
| unlink (no justification found) | 0.401 | 0.000 | stale |
| and_to_or (conjunction read as alternatives) | 0.231 | 0.000 | stale |
| drop_premise | 0.123 | 0.000 | stale |
| or_to_and (alternatives read as conjunction) | 0.000 | 0.079 | over-invalidation |
| drop_alternative | 0.000 | 0.029 | over-invalidation |

  So the "extraction errors cause staleness" finding from pilot-1 depends on the mix of error types. Missing links and AND→OR confusion leave conclusions stale; OR→AND confusion and missed alternatives destroy supported ones. **What the first LLM experiment must measure is the real mix of error types**, not just extraction F1. Add per-error-type counts to the extraction report when LLM extraction lands.
- **Per-family results need more scenarios.** 10 scenarios per family gives wide intervals (e.g. F1 SCR@0.25 ±0.064). The LLM pilot should use ≥ 25 per family, or several seeds.

### Pilot-1c: model-free validation and prior-art baselines (2026-10-18)

Reproduce: `uv sync --all-groups && uv run python scripts/prior_art_report.py --seeds 20 --fuzz 5000`. Full output is in `data/prior-art.results.txt`. Generator, labeller and metrics are unchanged.

**Differential test vs Veritas-TMS 0.16.0: exact agreement.**
- Coverage: 295 pilot retraction scenarios (seeds 0–19) plus 5,000 random DAGs, 50,682 nodes in total. **0 disagreeing scenarios.**
- Structural features exercised (random DAGs): diamond 3,746 · multi-support 4,317 · conjunctive 4,546 · multiple retraction 3,188 · partial support loss 2,435 · all supports lost 2,178 · unaffected parts 4,320.
- Scope: retract-only updates, reliability ≥ target's, not outdated. Not compared, because Veritas has no equivalent representation (documented rather than mapped away): supersede/STALE, hedge/UNK, low-reliability and outdated updates. Veritas handles reliability through entrenchment at assert time, which is a different mechanism.
- A greedy minimiser is in place for any future disagreement (`diffcheck.minimize`, tested on a planted fault).

**Baselines (20 seeds × 40 scenarios, mean ±95% CI):**

| System | SCR | OIR | macro-F1 | F2 OIR |
|---|---|---|---|---|
| direct_only | 0.565 ±0.015 | 0.000 | 0.564 | 0.000 |
| naive_cascade | 0.000 | 0.160 ±0.009 | 0.551 | 0.271 |
| S5 PACMI-style | 0.000 | 0.160 ±0.009 | 0.546 | 0.271 |
| S7 Atlas-style (native routing) | 0.066 ±0.016 | 0.139 ±0.009 | 0.741 | 0.271 |
| S7 Atlas-style (applied, c < 0.5) | 0.505 ±0.027 | 0.037 ±0.008 | 0.602 | 0.127 |
| S7 Atlas-style (applied, c < 0.75) | 0.000 | 0.160 ±0.009 | 0.783 | 0.271 |
| oracle JTMS (= Veritas on shared subset) | 0 | 0 | 1.000 | 0 |

What this shows:
- **PACMI-style propagation matches naive cascade on SCR and OIR exactly.** Its lattice changes *which* non-keep label a node gets, not *whether* it is touched. That is expected from its design (no alternative-support logic), and now measured: OIR 0.271 on F2.
- **Atlas's confidence carries no information about independent support.** The mean confidence drop for gold-keep vs gold-revise nodes is identical (0.1575 vs 0.1575 in F1–F3), because every impacted node is reassessed against the origin's Δ. So **no threshold can separate them**, and the sweep only trades one failure for the other: (SCR 0.505, OIR 0.037) at τ = 0.5 to (SCR 0, OIR 0.160) at τ = 0.75. In F2 the only OIR reduction comes from accumulating several retractions, not from support reasoning.
- **Atlas misses hedged updates.** A hedge moves confidence by 0.09, below the 0.15 routing floor, so uncertain conclusions stay keep (F6 SCR 0.293).
- **Minimal failure graphs** (in the results file): `B1 <= (E1) | (E2)`, retract E2. PACMI sends B1 to needs-verification and Atlas flags it, while gold is keep. For Atlas staleness: `B1 <= (E1)`, hedge E1; gold is uncertain, Atlas keeps it.
- **Caveat:** these are reproductions on our graphs with documented adaptations (A-P1…4, A-A1…3), not the original systems end to end. PACMI's LLM relation classifier and premise checker, and Atlas's contradiction detection and LLM reassessor, are not modelled.
- **Consequence for the gate:** on the explicit track, the credible prior-art mechanisms reproduce the naive-cascade failure on independent support, while a correct JTMS has none. That is expected, and it confirms why the explicit track cannot be the headline: the open question is still whether *induced* justifications keep that advantage.

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
- Veritas-TMS — https://pypi.org/project/veritas-tms/ · https://github.com/Iam-Raghava/veritas
- Atlas source — https://github.com/RichSchefren/atlas/tree/main/atlas_core/ripple
- Re-derivation gap (OpenReview) — https://openreview.net/forum?id=vNQcrBtiMb
- AGM-Bench — https://iclr.cc/virtual/2026/10017503
- DeltaLogic — https://arxiv.org/abs/2604.02733
- ReviseQA — https://icml.cc/virtual/2025/49130
- Belief-R — https://arxiv.org/abs/2406.19764
- MemTX (adjacent: transactional memory writes) — https://arxiv.org/abs/2607.23929
