# Renderer review sheet

## s_863600dbd1  (F3-000, product eligibility)

*World:* Evaluating product eligibility and vendor qualification criteria across multiple commercial suppliers.

### A. System view (judge C7 from this alone)
- `e_228f` [2026-01-08, Apex Systems Quality Assurance Report] Apex Systems achieves an energy efficiency rating of 92%.
- `e_ec54` [2026-01-11, Apex Systems Annual Sustainability Report] Apex Systems recorded verified carbon offsets of 600 metric tons this year.
- `e_bd32` [2026-01-14, National Organic Certification Board] Crestview Foods maintains an organic farming certification.
- `e_5eed` [2026-01-17, Apex Systems Manufacturing Operations Audit] Apex Systems utilizes 55% recycled content in manufacturing.
- `e_bddf` [2026-01-20, Delta Medical Production Log] Delta Medical recorded a product defect rate of 0.02% over the last quarter.
- `e_0f20` [2026-01-23, European Conformity Database] Beacon Electronics holds an active CE Mark certification.
- `e_4166` [2026-01-26, Environmental Chemical Safety Registry] Apex Systems maintains full non-toxic material compliance.
- `e_daad` [2026-01-29, International Standards Registry] Apex Systems holds an active ISO 14001 certification.
- memories:
  - `m_9149` Apex Systems satisfies the global eco-label qualifications.
  - `m_9511` Beacon Electronics is clear for European market distribution.
  - `m_8085` Crestview Foods meets premium grocery supply standards.
  - `m_3326` Delta Medical satisfies medical device vendor compliance.
  - `m_3621` The procurement team will issue a purchasing contract for Apex Systems.
  - `m_3fc8` Apex Systems is approved for green distributor cataloging.
- update `u_b4d0` [2026-02-01, Environmental Audit Board Audit Notice] A revised audit indicates Apex Systems recorded verified carbon offsets of 400 metric tons this year.
- policies:
  - `p_398c` Commercial distribution within the European zone is permitted for products holding a valid CE Mark certification.
  - `p_a6f4` Eligibility for high-end grocery supply requires an active organic farming credential.
  - `p_48ef` Medical equipment vendor qualification requires maintaining a quarterly product defect rate below 0.05%.
  - `p_283a` An applicant receives priority retail shelf placement upon demonstrating a customer satisfaction rating above 95%.
  - `p_ea35` Commercial export authorization is granted when annual revenue exceeds 1,000,000 dollars.
  - `p_846d` Green distributor listing approval is issued for any product meeting eco-label certification standards.
  - `p_3448` A product meets eco-label certification standards either with an energy efficiency rating over 90 percent, recycled content above 50 percent, non-toxic material compliance, and yearly carbon offsets of at least 500 metric tons, or by possessing ISO 14001 certification.
  - `p_4c00` A purchasing agreement is executed for any inventory item receiving green distributor listing approval.

### B. Intended structure
- `m_9149` (B1) [policy `p_3448`] <= (`e_228f` AND `e_5eed` AND `e_4166` AND `e_ec54`) **OR** (`e_daad`); gold after update: **keep**
  - set 1: Apex Systems satisfies the first set with energy efficiency above 90%, recycled content above 50%, non-toxic material compliance, and annual carbon offsets of 600 metric tons.
  - set 2: Apex Systems satisfies the alternative set by holding an ISO 14001 certification.
- `m_3fc8` (B2) [policy `p_846d`] <= (`m_9149`); gold after update: **keep**
  - set 1: Apex Systems satisfies global eco-label qualifications, which fulfills the condition for green distributor listing approval.
- `m_3621` (D1) [policy `p_4c00`] <= (`m_3fc8`); gold after update: **keep**
  - set 1: Apex Systems achieves green distributor cataloging approval, satisfying the requirement for executing a purchasing agreement.
- `m_9511` (B3) [policy `p_398c`] <= (`e_0f20`); gold after update: **keep**
  - set 1: Beacon Electronics holds a CE Mark certification, satisfying European market distribution policy.
- `m_8085` (B4) [policy `p_a6f4`] <= (`e_bd32`); gold after update: **keep**
  - set 1: Crestview Foods possesses an organic farming certification, satisfying high-end grocery supply rules.
- `m_3326` (B5) [policy `p_48ef`] <= (`e_bddf`); gold after update: **keep**
  - set 1: Delta Medical maintains a quarterly product defect rate of 0.02%, which is lower than the required 0.05% threshold.
- `u_b4d0` supersedes `e_ec54` (reliability high)
- decoy policies: `p_283a`, `p_ea35`
- final state after updates (gold action -> state): `m_9149` keep -> holds; `m_9511` keep -> holds; `m_8085` keep -> holds; `m_3326` keep -> holds; `m_3fc8` keep -> holds; `m_3621` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_228f~p_3448` policy_echoes_evidence: "an energy efficiency; energy efficiency rating" (judge under C7/C11)
- soft `e_ec54~p_3448` policy_echoes_evidence: "carbon offsets of" (judge under C7/C11)
- soft `e_bddf~p_48ef` policy_echoes_evidence: "product defect rate" (judge under C7/C11)
- soft `e_4166~p_3448` policy_echoes_evidence: "non-toxic material compliance" (judge under C7/C11)

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
