# Renderer review sheet

## s_c41a0870a2  (F6-000, product eligibility)

*World:* Evaluations of product qualification and eligibility across various technical and commercial items.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, National Flight Test Center certified summary] A certified summary from the Central Flight Test Center confirms AeroFlyer Pro completed 150 hours of flight testing this year.
- `e_5dd0` [2026-01-11, European Union Aviation Safety Agency database] Official records from the European Union Aviation Safety Agency confirm AeroFlyer Pro holds an EU Aviation Safety Certificate.
- `e_0823` [2026-01-14, International Standards Registry official registry] An official registry entry from the Quality Standards Registry confirms Solaris PowerPack holds an ISO 9001 quality audit.
- `e_45ef` [2026-01-17, AeroFlyer official commercial price sheet] An official price sheet from the manufacturer lists AeroFlyer Pro at a unit price of $4500.
- `e_fdcd` [2026-01-20, Appliance Testing Laboratory official report] An official report from the Appliance Testing Laboratory states Vortex Air Purifier recorded a clean air delivery rate of 350 cubic feet per minute.
- `e_f882` [2026-01-23, Chemical Inspection Agency laboratory analysis] A laboratory analysis from the Chemical Inspection Agency confirms BioShield Hand Sanitizer maintains an alcohol concentration of 75 percent.
- `e_660f` [2026-01-26, Aviation Safety Board official evaluation log] An official log from the Aviation Safety Board shows AeroFlyer Pro recorded an overall safety score of 92 points on its evaluation.
- memories:
  - `m_6c9c` AeroFlyer Pro meets regional flight operation standards.
  - `m_cc95` AeroFlyer Pro is recommended for government procurement.
  - `m_ece3` BioShield Hand Sanitizer complies with hospital hygiene standards.
  - `m_e062` AeroFlyer Pro qualifies for commercial pilot usage.
  - `m_bda8` Solaris PowerPack qualifies for long-term warranty support.
  - `m_6d1e` Vortex Air Purifier meets high-efficiency filtration benchmarks.
- update `u_99cf` [2026-01-29, Anonymous online forum posting] An anonymous online post claims AeroFlyer Pro never recorded an overall safety score of 92 points on its evaluation.
- policies:
  - `p_cd31` A model receives commercial pilot clearance if an item satisfies regional flight criteria and logs a minimum of 100 testing hours in a year.
  - `p_b65d` An item is approved for public sector acquisition if it has commercial pilot clearance and maintains a unit price not exceeding $5000.
  - `p_b3f6` An appliance achieves high-efficiency filtration status if its clean air delivery rate reaches at least 300 cubic feet per minute.
  - `p_6aef` A device gains extended warranty coverage if it passes an ISO 9001 quality audit.
  - `p_d3ca` A commercial vehicle receives eco-badge certification if its annual carbon dioxide emissions remain below 120 grams per kilometer.
  - `p_8aeb` An item satisfies regional flight criteria either by achieving an aviation evaluation score of 90 points or higher, or by holding an EU Aviation Safety Certificate.
  - `p_c629` An industrial pump is certified for undersea deployment provided it maintains an operational pressure threshold of 50 bar.
  - `p_9e3e` A formula satisfies medical hygiene criteria if its alcohol concentration is 70 percent or higher.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: A safety score of 92 points satisfies the requirement of an evaluation score of 90 points or higher.
  - set 2: Holding an EU Aviation Safety Certificate satisfies the certification requirement directly.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Satisfying regional flight criteria together with 150 flight testing hours meets the requirement of 100 testing hours in a year.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Having commercial pilot clearance with a unit price of $4500 satisfies the threshold of $5000 or less.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Passing the ISO 9001 quality audit satisfies the quality requirement.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: A clean air delivery rate of 350 cubic feet per minute satisfies the threshold of 300 cubic feet per minute.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: An alcohol concentration of 75 percent satisfies the threshold of 70 percent or higher.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_45ef~p_b65d` policy_echoes_evidence: "a unit price" (judge under C7/C11)
- soft `e_fdcd~p_b3f6` policy_echoes_evidence: "air delivery rate; clean air delivery; cubic feet per; feet per minute" (judge under C7/C11)
- soft `groups 1/4` cross_group_entity: "Agency" (judge under C6)
- soft `u_99cf` retraction_reads_as_hedge: "claims" (judge under C4)
- soft `e_5dd0->m_6c9c` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_660f->m_6c9c` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_3dc4->m_e062` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_6c9c->m_e062` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_45ef->m_cc95` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_e062->m_cc95` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_0823->m_bda8` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_fdcd->m_6d1e` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_f882->m_ece3` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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
