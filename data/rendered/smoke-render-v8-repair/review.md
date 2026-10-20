# Renderer review sheet (targeted repair)

## s_d13e3034f6  (F1-000, product eligibility)

*World:* The assistant tracks vendor qualification and product eligibility for municipal procurement programs.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, VeloTech Mobility Warranty Term Sheet, signed January 8, 2026] VeloTech Mobility provides a 24-month manufacturer warranty for the Velo-X1.
- `e_94fc` [2026-01-11, TÜV SÜD Certification Registry, verified January 11, 2026] Apex Medical Supplies holds ISO 13485 certification for medical equipment manufacturing.
- `e_0439` [2026-01-14, European Vehicle Safety Bureau Inspection Report, dated January 14, 2026] VeloTech Mobility holds an audit report confirming zero critical safety defects for the Velo-X1.
- `e_b5f7` [2026-01-17, VeloTech Mobility Warehouse Management System, inventory record dated January 17, 2026] VeloTech Mobility maintains a local spare parts inventory valued at $200,000 for the Velo-X1.
- `e_df05` [2026-01-20, Allianz Commercial Policy Certificate, issued January 20, 2026] VeloTech Mobility carries general liability insurance coverage of $5,000,000 for the Velo-X1.
- memories:
  - `m_c4d7` VeloTech Mobility satisfies regulatory safety standards for the Velo-X1.
  - `m_3f2d` VeloTech Mobility holds commercial service readiness for the Velo-X1.
  - `m_280b` Apex Medical Supplies meets quality system requirements for medical supplies.
  - `m_c5de` VeloTech Mobility meets post-sales support standards for the Velo-X1.
  - `m_5302` VeloTech Mobility qualifies for the Municipal Fleet Catalogue for the Velo-X1.
  - `m_4b85` Approve VeloTech Mobility for the City Transit Procurement Program for the Velo-X1.
- update `u_91ee` [2026-01-23, Regional Logistics Inspectorate Audit Report, published January 23, 2026] VeloTech Mobility maintains a local spare parts inventory valued at $80,000 for the Velo-X1.
- policies:
  - `p_fe1d` A product line achieves commercial deployment authorization when post-purchase maintenance benchmarks are met.
  - `p_5cd1` An offering is approved for civic transit listings if compliance with municipal protection norms is established and the producer carries general liability protection of at least $2,000,000.
  - `p_fbe6` Enrollment in municipal purchasing channels is granted to any product line approved for civic transit listings.
  - `p_b0aa` A healthcare manufacturer satisfies quality system criteria if the supplier possesses an active ISO 13485 credential.
  - `p_1714` Compliance with municipal protection norms is established for a vendor with commercial deployment authorization provided an official audit record confirms zero critical defects.
  - `p_4f8e` An electronic component obtains green eco-labeling if recycled material content equals or exceeds 40 percent.
  - `p_0087` Equipment satisfies post-purchase maintenance benchmarks if the producer maintains a regional spare parts inventory of at least $150,000 alongside a manufacturer warranty period of no less than 12 months.
  - `p_1a46` A distributor achieves preferred vendor status if annual revenue exceeds $10,000,000 or if a five-year clean track record is verified.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: VeloTech Mobility maintains a $200,000 spare parts inventory and a 24-month warranty for the Velo-X1, meeting the $150,000 inventory threshold and 12-month warranty requirement under the policy.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: VeloTech Mobility satisfies post-purchase maintenance benchmarks for the Velo-X1, fulfilling the condition for commercial deployment authorization.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: VeloTech Mobility holds commercial deployment authorization and an audit showing zero critical defects for the Velo-X1, establishing compliance with municipal protection norms.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: VeloTech Mobility establishes compliance with municipal protection norms and maintains $5,000,000 in general liability protection for the Velo-X1, satisfying the civic transit listing threshold of $2,000,000.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: VeloTech Mobility is approved for civic transit listings for the Velo-X1, qualifying for enrollment in municipal purchasing channels.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Apex Medical Supplies holds ISO 13485 certification, satisfying quality system criteria for healthcare manufacturers.
- `u_91ee` supersedes `e_b5f7` (reliability high)
- decoy policies: `p_1a46`, `p_4f8e`
- final state after updates (gold action -> state): `m_c5de` recompute -> fails; `m_280b` keep -> holds; `m_3f2d` recompute -> fails; `m_c4d7` recompute -> fails; `m_5302` recompute -> fails; `m_4b85` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_b5f7~p_0087` policy_echoes_evidence: "spare parts inventory" (judge under C7/C11)
- soft `e_df05~p_5cd1` policy_echoes_evidence: "carries general liability" (judge under C7/C11)

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
