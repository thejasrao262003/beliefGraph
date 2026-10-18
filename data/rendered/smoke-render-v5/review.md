# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* Commercial transport compliance and medical equipment supplier evaluation for annual product eligibility programs.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Regional Energy Audit Board certificate] Vanguard Logistics maintains an annual charging efficiency rating of 88%.
- `e_94fc` [2026-01-11, Official ISO Registrar Database] Orion Medical Equipment holds ISO 13485 quality certification.
- `e_0439` [2026-01-14, Manufacturer Service Agreement] Vanguard Logistics provides a minimum 3-year battery maintenance warranty.
- `e_b5f7` [2026-01-17, State Licensing Registry entry] Vanguard Logistics operates an active electric delivery fleet of 45 vehicles.
- `e_df05` [2026-01-20, National Transport Authority filing] Vanguard Logistics completed 120 hours of driver eco-safety training this year.
- memories:
  - `m_c4d7` Vanguard Logistics gains sustainable commercial transport credentials.
  - `m_3f2d` Vanguard Logistics qualifies as an eco-friendly freight carrier.
  - `m_280b` Orion Medical Equipment fulfills medical device regulatory criteria.
  - `m_c5de` Vanguard Logistics fulfills clean transport operational benchmarks.
  - `m_5302` Vanguard Logistics secures preferred environmental supplier ranking.
  - `m_4b85` Award Vanguard Logistics the municipal clean transit grant.
- update `u_91ee` [2026-01-23, State Licensing Registry updated portal] Vanguard Logistics operates an active electric delivery fleet of 15 vehicles following fleet downsizing.
- policies:
  - `p_fe1d` A transporter is designated as a low-emission carrier provided they maintain green fleet operation standards.
  - `p_5cd1` A business earns preferred eco-vendor status when it holds sustainable logistics certification and documents a minimum of 100 driver environmental safety training hours.
  - `p_fbe6` Authorization for the Clean Transit Grant requires an applicant to possess preferred eco-vendor status.
  - `p_b0aa` A medical supplier meets healthcare manufacturing baseline requirements if it maintains active ISO 13485 accreditation.
  - `p_1714` A transporter achieves sustainable logistics certification if it is designated as a low-emission carrier and provides battery coverage of no less than 3 years.
  - `p_4f8e` An exporter obtains priority customs clearance when maintaining a compliance rating of at least 95 percent on international shipments.
  - `p_0087` An enterprise achieves green fleet operation standards if it maintains a minimum active electric transport count of 30 units and demonstrates a charging efficiency performance of at least 85%.
  - `p_1a46` A retail vendor qualifies for bulk shipping subsidies if it achieves an annual distribution volume exceeding 50000 units.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Vanguard Logistics operates 45 active electric delivery vehicles (at least 30 required) and maintains an 88% annual charging efficiency rating (at least 85% required), satisfying green fleet operation standards.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Vanguard Logistics satisfies green fleet operation standards, qualifying it for designation as a low-emission carrier.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Vanguard Logistics is designated as a low-emission carrier and provides a 3-year battery maintenance warranty (at least 3 years required), earning sustainable logistics certification.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Vanguard Logistics holds sustainable logistics certification and has documented 120 hours of driver eco-safety training (at least 100 hours required), granting it preferred eco-vendor status.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Vanguard Logistics possesses preferred eco-vendor status, fulfilling the prerequisite for authorization under the Clean Transit Grant.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Orion Medical Equipment holds active ISO 13485 accreditation, fulfilling healthcare manufacturing baseline requirements.
- `u_91ee` supersedes `e_b5f7` (reliability high)
- decoy policies: `p_1a46`, `p_4f8e`
- final state after updates (gold action -> state): `m_c5de` recompute -> fails; `m_280b` keep -> holds; `m_3f2d` recompute -> fails; `m_c4d7` recompute -> fails; `m_5302` recompute -> fails; `m_4b85` recompute -> fails

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
