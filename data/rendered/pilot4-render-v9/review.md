# Renderer review sheet

## s_3d821bdd07  (F2-000, product eligibility)

*World:* Assessment of medical supplier and software provider qualifications for catalog distribution tiers and partner status.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Quarterly enterprise feedback summary dashboard] Beacon Software logged a customer satisfaction score of 4.6 stars this quarter.
- `e_dfe6` [2026-01-11, Registry portal of certified medical equipment suppliers] Apex Medical holds an active ISO 13485 certification.
- `e_e50c` [2026-01-14, Official audit report from the health product compliance board] Apex Medical achieved an annual quality compliance rating of 92%.
- memories:
  - `m_2075` Apex Medical is authorized for priority catalog listing.
  - `m_36f2` Beacon Software qualifies for premium vendor membership.
  - `m_7743` Apex Medical holds global distribution status.
- update `u_a152` [2026-01-17, Revised annual audit statement from the health product compliance board] Apex Medical's annual quality compliance rating was recalculated to 78%.
- update `u_41fa` [2026-01-20, Official bulletin from the certification registry agency] Apex Medical's ISO 13485 certification was formally suspended following an investigation.
- policies:
  - `p_d10e` Authorization for listing on the priority catalog is granted when a merchant achieves a yearly quality compliance rating above 85% or holds an active ISO 13485 certification.
  - `p_8779` Commercial warranty protection is extended if an equipment manufacturer maintains a nationwide network of at least 10 service centers.
  - `p_3b4c` Distribution status at the global tier is granted to any enterprise with authorization for listing on the priority catalog.
  - `p_4091` Vendor membership at the premium level is awarded to a firm that maintains a quarterly customer satisfaction score of at least 4.2 stars.
  - `p_e525` A product line qualifies for eco-label certification when its operational energy consumption remains below 150 kWh per month.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: Apex Medical's annual quality compliance rating of 92% exceeds the 85% threshold required for priority catalog listing authorization.
  - set 2: Apex Medical's active ISO 13485 certification satisfies the accreditation requirement for priority catalog listing authorization.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: Apex Medical's authorization for listing on the priority catalog satisfies the prerequisite for global distribution status.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: Beacon Software's quarterly customer satisfaction score of 4.6 stars meets the 4.2 star requirement for premium vendor membership.
- `u_a152` supersedes `e_e50c` (reliability high)
- `u_41fa` supersedes `e_dfe6` (reliability high)
- decoy policies: `p_e525`, `p_8779`
- final state after updates (gold action -> state): `m_2075` recompute -> fails; `m_36f2` keep -> holds; `m_7743` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_1552~p_4091` policy_echoes_evidence: "customer satisfaction score; satisfaction score of" (judge under C7/C11)
- soft `e_dfe6~p_d10e` policy_echoes_evidence: "holds an active" (judge under C7/C11)
- soft `e_e50c~p_d10e` policy_echoes_evidence: "quality compliance rating" (judge under C7/C11)

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

## s_94a4bc8c87  (F3-000, product eligibility)

*World:* Evaluating product eligibility for regional eco-incentives and premium retail catalog placement.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Independent testing laboratory certified test report] Laboratory test logs confirm Lumina Desk Lamp demonstrates an operating efficiency of 95 lm/W.
- `e_2787` [2026-01-11, Signed manufacturer warranty schedule] Warranty documentation confirms Veloce E-Bike carries a battery warranty of 4 years.
- `e_124c` [2026-01-14, EU EcoCert official registry database] Regulatory filings confirm Veloce E-Bike holds an EU EcoCert Badge.
- `e_ac4d` [2026-01-17, National Consumer Safety Board audit report] Testing records show Veloce E-Bike achieved a customer safety score of 90 points.
- `e_c8d5` [2026-01-20, Official technical specifications sheet from Veloce Motors] Product documentation indicates Veloce E-Bike features an electric motor power of 350 W.
- memories:
  - `m_4677` Lumina Desk Lamp fulfills Energy Star compliance criteria.
  - `m_aeef` Veloce E-Bike meets EcoTransport Rebate eligibility standards.
  - `m_b7fc` Veloce E-Bike is designated for featured catalog placement.
- update `u_84c2` [2026-01-23, Updated warranty filing from Veloce Motors legal department] A revised warranty declaration indicates Veloce E-Bike carries a battery warranty of 2 years.
- policies:
  - `p_b875` A model is chosen for showcase catalog listing provided it secures EcoTransport Rebate clearance and achieves a customer safety score of 85 points or above.
  - `p_ba9f` A lighting fixture satisfies Energy Star benchmarks when its operating efficiency equals or exceeds 80 lm/W.
  - `p_4b46` A device receives Green Choice Certification if its recycled material content reaches at least 40 percent.
  - `p_0c4c` An appliance is granted Priority Logistics Status provided its unit shipping weight remains under 12 kg.
  - `p_81ec` An item achieves EcoTransport Rebate clearance either by featuring an electric motor power of at least 250 W alongside a battery warranty of 3 years or greater, or by maintaining an EU EcoCert Badge.

### B. Intended structure
- `m_aeef` (B1) [policy `p_81ec`] <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: Veloce E-Bike satisfies the motor power requirement with 350 W and the battery warranty requirement with 4 years.
  - set 2: Veloce E-Bike holds the EU EcoCert Badge.
- `m_b7fc` (D1) [policy `p_b875`] <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: Veloce E-Bike maintains EcoTransport Rebate clearance and achieves a customer safety score of 90 points, meeting the 85 points minimum.
- `m_4677` (B2) [policy `p_ba9f`] <= (`e_4667`); gold after update: **keep**
  - set 1: Lumina Desk Lamp achieves an operating efficiency of 95 lm/W, exceeding the required threshold of 80 lm/W.
- `u_84c2` supersedes `e_2787` (reliability high)
- decoy policies: `p_4b46`, `p_0c4c`
- final state after updates (gold action -> state): `m_aeef` keep -> holds; `m_4677` keep -> holds; `m_b7fc` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2787~p_81ec` policy_echoes_evidence: "a battery warranty; battery warranty of" (judge under C7/C11)
- soft `e_ac4d~p_b875` policy_echoes_evidence: "a customer safety; customer safety score; safety score of" (judge under C7/C11)
- soft `e_c8d5~p_81ec` policy_echoes_evidence: "an electric motor; electric motor power; motor power of" (judge under C7/C11)
- soft `e_124c->m_aeef` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_2787->m_aeef` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_c8d5->m_aeef` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_ac4d->m_b7fc` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_aeef->m_b7fc` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_4667->m_4677` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

*World:* Evaluation of commercial vendor eligibility and product catalog placements across partner companies.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, Annual safety audit summary dated January 8, 2026.] Apex Robotics recorded zero severe safety incidents this year.
- `e_5dd0` [2026-01-11, Quality management registry record accessed on January 11, 2026.] Apex Robotics holds ISO 9001 Certification.
- `e_0823` [2026-01-14, Official agricultural registry certificate issued on January 14, 2026.] Biomix Tech holds organic product certification.
- `e_45ef` [2026-01-17, Verified insurance policy schedule submitted on January 17, 2026.] Apex Robotics maintains annual commercial liability coverage of $5,000,000.
- `e_fdcd` [2026-01-20, Certified sales report published on January 20, 2026.] Crestview Audio recorded annual sales of 50,000 units.
- `e_f882` [2026-01-23, Signed warranty agreement dated January 23, 2026.] Delta Solar maintains a warranty duration of 10 years.
- `e_660f` [2026-01-26, Official R&D audit report filed on January 26, 2026.] Apex Robotics maintains annual research spending of $500,000.
- memories:
  - `m_6c9c` Apex Robotics is admitted to the Premier Vendor Network.
  - `m_cc95` Apex Robotics is selected for priority catalog placement.
  - `m_ece3` Delta Solar qualifies for the Extended Protection Program.
  - `m_e062` Apex Robotics achieves Tier 1 Supplier Status.
  - `m_bda8` Biomix Tech is listed in the Green Goods Index.
  - `m_6d1e` Crestview Audio obtains high volume distributor rights.
- update `u_99cf` [2026-01-29, Unverified forum post dated January 29, 2026.] Apex Robotics holds no recorded annual research spending.
- policies:
  - `p_cd31` Vendor designation as a Tier 1 supplier requires an enterprise admitted to the Premier Vendor Network that registers zero severe safety incidents per year.
  - `p_b65d` Top product placement in the catalog is assigned to any business achieving Tier 1 Supplier Status that maintains yearly commercial liability coverage of at least $2,000,000.
  - `p_b3f6` Wholesale distribution authorization at high volumes requires minimum annual sales of 20,000 units.
  - `p_6aef` Inclusion in the Green Goods Index is granted to any entity holding organic product certification.
  - `p_d3ca` Special trade concessions are granted to exporters maintaining an annual shipping output of at least 1,000 metric tons.
  - `p_8aeb` Listing in the Premier Vendor Network requires either yearly research spending of at least $400,000 or holding ISO 9001 Certification.
  - `p_c629` Fast-track patent processing is permitted for applicants maintaining five or more active utility patents.
  - `p_9e3e` Enrollment in the Extended Protection Program is open to products carrying a warranty duration of at least 5 years.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Apex Robotics satisfies the Premier Vendor Network policy via annual research spending of $500,000, meeting the $400,000 minimum requirement.
  - set 2: Apex Robotics satisfies the Premier Vendor Network policy by holding ISO 9001 Certification.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Apex Robotics meets Tier 1 Supplier Status criteria by being admitted to the Premier Vendor Network and maintaining zero severe safety incidents this year.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Apex Robotics qualifies for priority catalog placement by holding Tier 1 Supplier Status and maintaining $5,000,000 in annual commercial liability coverage.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Biomix Tech qualifies for the Green Goods Index by maintaining organic product certification.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: Crestview Audio obtains high volume distributor rights by achieving annual sales of 50,000 units, exceeding the 20,000 unit threshold.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: Delta Solar qualifies for the Extended Protection Program by having a 10-year warranty duration, exceeding the 5-year requirement.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_3dc4~p_cd31` policy_echoes_evidence: "severe safety incidents; zero severe safety" (judge under C7/C11)
- soft `e_0823~p_6aef` policy_echoes_evidence: "organic product certification" (judge under C7/C11)
- soft `e_45ef~p_b65d` policy_echoes_evidence: "commercial liability coverage; liability coverage of" (judge under C7/C11)
- soft `e_fdcd~p_b3f6` policy_echoes_evidence: "annual sales of" (judge under C7/C11)
- soft `e_f882~p_9e3e` policy_echoes_evidence: "a warranty duration; warranty duration of" (judge under C7/C11)
- soft `e_660f~p_8aeb` policy_echoes_evidence: "research spending of" (judge under C7/C11)

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
