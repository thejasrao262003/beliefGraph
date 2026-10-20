# Renderer review sheet

## s_c41a0870a2  (F6-000, product eligibility)

*World:* An evaluation assistant checks whether technical equipment and materials meet eligibility thresholds for healthcare procurement, rebate programs, municipal supply, and tax credits.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, Signed hospital network safety audit report] Vortex 500 Ventilator recorded 0 critical safety incidents in the last year.
- `e_5dd0` [2026-01-11, European Conformity registry official certificate listing] Vortex 500 Ventilator holds an active CE mark certification.
- `e_0823` [2026-01-14, Accredited energy testing laboratory report] SolarPulse X Charger achieved an energy efficiency rating of 92 percent.
- `e_45ef` [2026-01-17, Certified liability certificate from insurance underwriter] Vortex 500 Ventilator maintains liability insurance coverage of 5000000 USD.
- `e_fdcd` [2026-01-20, Official NSF product compliance registry] AquaClean Filter possesses a NSF/ANSI Standard 53 certification.
- `e_f882` [2026-01-23, Official materials testing laboratory compliance statement] ThermaShield Insulation recorded a thermal resistance value of 30 R-value.
- `e_660f` [2026-01-26, Official medical device registry export signed by the registrar] Vortex 500 Ventilator holds an active ISO 13485 certification.
- memories:
  - `m_6c9c` Vortex 500 Ventilator satisfies baseline quality criteria.
  - `m_cc95` Vortex 500 Ventilator is authorized for hospital procurement.
  - `m_ece3` ThermaShield Insulation is eligible for green building credit.
  - `m_e062` Vortex 500 Ventilator holds tier-one safety classification.
  - `m_bda8` SolarPulse X Charger qualifies for high-efficiency rebate.
  - `m_6d1e` AquaClean Filter meets municipal water filtration standards.
- update `u_99cf` [2026-01-29, Anonymous online comment] An unverified forum post claims that Vortex 500 Ventilator lacks an active ISO 13485 certification.
- policies:
  - `p_cd31` A medical device meeting baseline quality standards achieves tier-one safety status if its annual critical safety incidents do not exceed 0.
  - `p_b65d` Hospital purchasing approval is granted for a device with premier safety standing that maintains liability insurance coverage of at least 5000000 USD.
  - `p_b3f6` Municipal water filtration compliance requires a filter to possess a NSF/ANSI Standard 53 credential.
  - `p_6aef` Rebate eligibility for high efficiency is awarded to a charger with an energy efficiency rating of at least 90 percent.
  - `p_d3ca` Commercial lighting fixtures receive utility tariff discounts when their power factor exceeds 0.95.
  - `p_8aeb` Baseline quality compliance is granted to a medical device holding either a valid ISO 13485 credential or an active CE mark credential.
  - `p_c629` Industrial protective helmets receive severe-impact clearance if they pass a drop test threshold of 100 joules.
  - `p_9e3e` Green building tax credits apply to insulation demonstrating a thermal resistance value of at least 30 R-value.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Holding an active ISO 13485 certification directly satisfies the baseline quality compliance policy.
  - set 2: Holding an active CE mark certification directly satisfies the baseline quality compliance policy.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Meeting baseline quality standards combined with recording 0 critical safety incidents over the last year fulfills tier-one safety criteria.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Achieving tier-one safety classification and maintaining 5000000 USD in liability insurance coverage permits hospital purchasing approval.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: An energy efficiency rating of 92 percent satisfies the minimum 90 percent threshold for high-efficiency rebate eligibility.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: Possessing a NSF/ANSI Standard 53 certification satisfies the requirements for municipal water filtration compliance.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: A thermal resistance value of 30 R-value fulfills the threshold required to receive green building tax credits.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_3dc4~p_cd31` policy_echoes_evidence: "critical safety incidents" (judge under C7/C11)
- soft `e_0823~p_6aef` policy_echoes_evidence: "an energy efficiency; efficiency rating of; energy efficiency rating" (judge under C7/C11)
- soft `e_45ef~p_b65d` policy_echoes_evidence: "insurance coverage of; liability insurance coverage; maintains liability insurance" (judge under C7/C11)
- soft `e_f882~p_9e3e` policy_echoes_evidence: "a thermal resistance; resistance value of; thermal resistance value" (judge under C7/C11)
- soft `u_99cf` retraction_reads_as_hedge: "claims" (judge under C4)

### Checklist (record pass/fail + reason in the CSV)
- [ ] **C1_meaning** Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan).
- [ ] **C2_and** Within each justification set, all facts together entail the conclusion, and dropping any one breaks it.
- [ ] **C3_or** Each alternative justification set alone entails the conclusion, using genuinely different facts.
- [ ] **C4_updates** Each update says what its relation requires (retracts / supersedes with a new value / hedges), speaks only about its target, and its source matches the stated reliability.
- [ ] **C5_sources** Evidence source descriptions match their reliability (high / medium / low).
- [ ] **C6_distractors** Facts and memories in different groups are unrelated: nothing in one bears on another.
- [ ] **C7_no_reveal** Read as the system would (system view only): the wording does not reveal which facts support which memory, beyond what the meaning itself implies.
- [ ] **C8_inferable** From the visible facts and policies alone, the intended AND/OR structure can be inferred.
- [ ] **C9_no_hidden_needed** Every gold label can be derived without the hidden rationale or any eval metadata.
- [ ] **C10_unambiguous** No reasonable alternative reading of the text would make a gold label wrong.
- [ ] **C11_policy_not_graph** Policies state reusable rules about kinds of facts; they do not name the specific entity, quote evidence, or otherwise disclose which item supports which memory.
- [ ] **C12_decoys_inert** Decoy policies govern nothing here and offer no alternative route to any memory.
- [ ] **C13_final_state** The renderer's after-update state for each memory follows from the policies and the facts that remain credible (and recompute results are right).
