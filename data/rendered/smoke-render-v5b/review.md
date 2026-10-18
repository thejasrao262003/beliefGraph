# Renderer review sheet

## s_3d821bdd07  (F2-000, product eligibility)

*World:* Evaluation of commercial transport companies for specialized freight insurance tiers and service program enrollments.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Commercial transport authority audit report from January 8, 2026.] Veloce Courier operates a motorized transport fleet with 15 heavy cargo vans.
- `e_dfe6` [2026-01-11, Global Standards Registrar database extract dated January 11, 2026.] Apex Logistics holds an active ISO 22000 food safety management certification.
- `e_e50c` [2026-01-14, Official vehicle registry filing submitted January 14, 2026.] Apex Logistics maintains an average commercial vehicle age of 3.2 years across its regional fleet.
- memories:
  - `m_2075` Apex Logistics meets the qualification criteria for Tier-1 Freight Coverage.
  - `m_36f2` Veloce Courier is eligible for Same-Day Heavy Cargo enrollment.
  - `m_7743` Apex Logistics should be issued the automated premium discount rate for fleet policies.
- update `u_a152` [2026-01-17, Updated transport authority audit released January 17, 2026.] A revised fleet inspection shows Apex Logistics has an average commercial vehicle age of 5.8 years.
- update `u_41fa` [2026-01-20, Global Standards Registrar status update published January 20, 2026.] An official notice confirms the ISO 22000 food safety certification for Apex Logistics expired last month and was not renewed.
- policies:
  - `p_d10e` An enterprise is granted approval for Tier-1 Freight Coverage if its mean vehicle fleet age remains under 4 years, or if it maintains active ISO 22000 certification.
  - `p_8779` A logistics firm secures Executive Vendor Status provided its annual billing exceeds 5 million dollars or it operates across four international regions.
  - `p_3b4c` An applicant approved for Tier-1 Freight Coverage receives automatic rate discounting across commercial fleet insurance.
  - `p_4091` Participation in Same-Day Heavy Cargo is granted to any transport firm maintaining an active fleet of at least 10 heavy transport vans.
  - `p_e525` An applicant qualifies for Hazardous Materials Clearance if it maintains specialized spill containment kits and holds a valid ISO 14001 environmental management credential.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: Set 1 entails B1 because Apex Logistics maintains a mean vehicle fleet age of 3.2 years, which satisfies the requirement of remaining under 4 years for Tier-1 Freight Coverage.
  - set 2: Set 2 entails B1 because Apex Logistics holds active ISO 22000 certification, which independently qualifies an enterprise for Tier-1 Freight Coverage.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: Set 1 entails D1 because Apex Logistics qualifies for Tier-1 Freight Coverage, meeting the condition for automatic rate discounting on commercial fleet insurance.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: Set 1 entails B2 because Veloce Courier operates 15 heavy transport vans, exceeding the threshold of at least 10 heavy transport vans for Same-Day Heavy Cargo participation.
- `u_a152` supersedes `e_e50c` (reliability high)
- `u_41fa` supersedes `e_dfe6` (reliability high)
- decoy policies: `p_e525`, `p_8779`
- final state after updates (gold action -> state): `m_2075` recompute -> fails; `m_36f2` keep -> holds; `m_7743` recompute -> fails

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

## s_c41a0870a2  (F6-000, product eligibility)

*World:* The assistant tracks commercial qualification status and catalog distribution access for regional product vendors.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, State Department of Health online registry] Vance Medical Supplies possesses an active state pharmaceutical distribution license.
- `e_5dd0` [2026-01-11, Official certificate from the International Standards Registrar] Vance Medical Supplies received ISO 13485 quality management accreditation.
- `e_0823` [2026-01-14, National Industrial Safety Board registry] Kira Robotics maintains an active safety compliance rating of Class 4.
- `e_45ef` [2026-01-17, Facility inspection report from Regulatory Compliance Services] Vance Medical Supplies operates a dedicated refrigerated storage facility measuring 2,500 square meters.
- `e_fdcd` [2026-01-20, Federal Agriculture Certification Database] Oakhaven Farms holds official organic processing certification from the Department of Agriculture.
- `e_f882` [2026-01-23, Third-party auditor compliance certificate] Solaris Tech Solutions completed a cybersecurity risk assessment yielding a score of 92.
- `e_660f` [2026-01-26, Audited annual sales statement from Apex Financial] Vance Medical Supplies logged $650,000 in direct purchases during the previous calendar year.
- memories:
  - `m_6c9c` Vance Medical Supplies holds preferred partner status.
  - `m_cc95` Vance Medical Supplies should receive access to the BioFreeze vaccine catalog.
  - `m_ece3` Solaris Tech Solutions meets cloud infrastructure vendor requirements.
  - `m_e062` Vance Medical Supplies is approved to handle thermal-sensitive pharmaceuticals.
  - `m_bda8` Kira Robotics is permitted to market automated heavy machinery.
  - `m_6d1e` Oakhaven Farms qualifies for premium eco-label distribution.
- update `u_99cf` [2026-01-29, Unverified user comment on a trade discussion board] An anonymous post on an industry forum asserts Vance Medical Supplies did not achieve $650,000 in direct purchases during the previous year.
- policies:
  - `p_cd31` Clearance for thermal-sensitive pharmaceuticals requires preferred partner rating alongside a valid state pharmaceutical distribution license.
  - `p_b65d` Catalog access for BioFreeze vaccines is extended to a distributor cleared for thermal-sensitive pharmaceuticals that operates a cold storage facility of no less than 1,500 square meters.
  - `p_b3f6` ECO-label trade rights are granted to an agricultural producer maintaining official organic processing certification.
  - `p_6aef` Commercial clearance for automated heavy equipment requires an active industrial safety rating of Class 4 or above.
  - `p_d3ca` Specialty chemical handling credentials are issued to any logistics provider maintaining a hazard response squad of at least five personnel.
  - `p_8aeb` Preferred partner rating is conferred if a merchant logs at least $500,000 in yearly purchases or maintains active ISO 13485 accreditation.
  - `p_c629` Priority freight scheduling is awarded to carriers achieving an on-time transit rating above 98 percent.
  - `p_9e3e` Cloud platform vendor authorization requires a verified digital security assessment score of 85 or greater.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Vance Medical Supplies recorded $650,000 in direct purchases, meeting the minimum $500,000 annual spending threshold.
  - set 2: Vance Medical Supplies possesses ISO 13485 accreditation, satisfying the alternative quality certification requirement.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Vance Medical Supplies holds preferred partner status and maintains a valid state pharmaceutical distribution license, fulfilling both necessary conditions.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Vance Medical Supplies is cleared for thermal-sensitive pharmaceuticals and operates 2,500 square meters of cold storage, meeting all requirements for catalog access.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Kira Robotics holds a Class 4 safety rating, meeting the minimum Class 4 requirement for commercial clearance.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: Oakhaven Farms holds official organic processing certification, qualifying it for trade rights.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: Solaris Tech Solutions scored 92 on its security assessment, exceeding the required threshold of 85.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

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
