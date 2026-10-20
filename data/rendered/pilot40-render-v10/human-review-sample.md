# Independent human review sample (blind)

11 scenarios from `pilot40-render-v10`, sampled with a fixed seed and stratified by family and by the AI decision
(the composition is recorded in docs/renderer-design.md §21; please read it only after reviewing), shuffled.
The AI review (`review.csv`) is deliberately NOT shown: please judge
C1-C13 independently, with C8, C10 and C12 explicitly, and record pass/fail + reasons in
`human-review-sample.csv`. Agreement (Cohen's kappa) will be computed only from these independent decisions.

## s_f48def6c8c  (F6-009, travel logistics)

*World:* A regional transport authority evaluates charter fleet providers and service operators for annual executive contracts.

### A. System view (judge C7 from this alone)
- `e_b475` [2026-01-08, Official ISO registry portal] Meridian Shuttles holds an ISO 9001 quality management certification.
- `e_1207` [2026-01-11, Official transport audit report] Vanguard Travel maintains a vehicle count of 20 coaches.
- memories:
  - `m_eeb4` Vanguard Travel is assigned to manage the European Executive Shuttle contract.
  - `m_f770` Vanguard Travel achieves Tier-1 Logistics Vendor designation.
  - `m_67e3` Vanguard Travel qualifies for high-capacity carrier status.
  - `m_49d1` Meridian Shuttles fulfills the premier safety criteria.
- update `u_00ef` [2026-01-14, Unverified online forum comment] An anonymous blog post asserts Vanguard Travel no longer maintains any coaches.
- policies:
  - `p_2d03` High-capacity transport authorization is granted to any carrier maintaining a vehicle count of at least 15 coaches.
  - `p_1ae8` Allocation of the European Executive Shuttle route requires a firm with Tier-1 partner classification.
  - `p_b203` Tier-1 partner classification requires an entity to hold high-capacity transport authorization.
  - `p_6f71` VIP charter registration requires a driver staffing count of at least 50 licensed chauffeurs.
  - `p_d895` Premier safety approval is awarded to transport providers holding an ISO 9001 quality management certification.
  - `p_c084` Express freight clearance is granted to companies maintaining annual fuel reserves of 100,000 liters.

### B. Intended structure
- `m_67e3` (B1) [policy `p_2d03`] <= (`e_1207`); gold after update: **uncertain**
  - set 1: Vanguard Travel maintains 20 coaches, which exceeds the required threshold of 15 coaches.
- `m_f770` (B2) [policy `p_b203`] <= (`m_67e3`); gold after update: **uncertain**
  - set 1: Vanguard Travel qualifies for high-capacity carrier status, fulfilling the condition for Tier-1 partner classification.
- `m_eeb4` (D1) [policy `p_1ae8`] <= (`m_f770`); gold after update: **uncertain**
  - set 1: Vanguard Travel holds Tier-1 Logistics Vendor designation, satisfying the prerequisite for the European Executive Shuttle route.
- `m_49d1` (B3) [policy `p_d895`] <= (`e_b475`); gold after update: **keep**
  - set 1: Meridian Shuttles possesses the ISO 9001 quality management certification necessary for premier safety approval.
- `u_00ef` retracts `e_1207` (reliability low)
- decoy policies: `p_6f71`, `p_c084`
- final state after updates (gold action -> state): `m_67e3` uncertain -> undetermined; `m_49d1` keep -> holds; `m_f770` uncertain -> undetermined; `m_eeb4` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_b475~p_d895` policy_echoes_evidence: "quality management certification" (judge under C7/C11)
- soft `e_1207~p_2d03` policy_echoes_evidence: "a vehicle count; vehicle count of" (judge under C7/C11)
- soft `m_67e3` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)
- soft `m_f770` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)
- soft `m_eeb4` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)

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

## s_3b96e1e9d0  (F2-004, product eligibility)

*World:* An evaluation of energy product specifications and material ratings for green technology certification and incentive programs.

### A. System view (judge C7 from this alone)
- `e_eca9` [2026-01-08, Building Material Certification Board database] Vesta Insulation Wrap provides a thermal resistance rating of 4 R-value.
- `e_b621` [2026-01-11, Manufacturer Product Warranty Register entry] Kuro Solar Inverter carries a product warranty duration of 5 years.
- `e_d328` [2026-01-14, Official Energy Star Product Database record] Kuro Solar Inverter holds an Energy Star certification.
- `e_5f73` [2026-01-17, ISO Central Audit Bureau portal] Kuro Solar Inverter holds an ISO 14001 environmental badge.
- `e_0976` [2026-01-20, Certified National Testing Laboratory report] Kuro Solar Inverter achieved an energy conversion efficiency of 96%.
- memories:
  - `m_78a4` Authorize Kuro Solar Inverter for the Municipal Clean Tech Incentive Program.
  - `m_9d86` Vesta Insulation Wrap meets the regional building efficiency baseline.
  - `m_e7ed` Kuro Solar Inverter qualifies for the National Green Equipment Registry.
- update `u_ea7f` [2026-01-23, National Metrology Institute re-testing notice] A re-testing audit confirmed that Kuro Solar Inverter does not have an energy conversion efficiency of 96%.
- update `u_4ea5` [2026-01-26, ISO Central Registry compliance revocation summary] A certification audit confirmed that Kuro Solar Inverter does not hold an ISO 14001 environmental badge.
- policies:
  - `p_c92c` Commercial refrigeration units receive priority tariff exemption if they utilize natural A1 refrigerants and maintain a storage capacity of at least 500 liters.
  - `p_6e99` An industrial lubricant achieves high-load certification when its kinematic viscosity exceeds 100 centistokes at 40 degrees Celsius.
  - `p_85f0` Listing on the national green equipment catalog is granted to a solar conversion unit that holds an Energy Star certification, maintains an ISO 14001 environmental badge, or achieves a minimum energy conversion efficiency of 95%.
  - `p_c837` Municipal clean tech incentive clearance is issued for a registered eco-friendly unit that additionally offers a product warranty duration of 5 years or more.
  - `p_b5ce` Compliance with local structure thermal standards requires an insulating material to achieve a minimum thermal resistance rating of 4 R-value.

### B. Intended structure
- `m_e7ed` (B1) [policy `p_85f0`] <= (`e_d328`) **OR** (`e_5f73`) **OR** (`e_0976`); gold after update: **keep**
  - set 1: Kuro Solar Inverter holds an Energy Star certification, which satisfies the requirement for green catalog listing.
  - set 2: Kuro Solar Inverter maintains an ISO 14001 environmental badge, fulfilling the alternative credential option for catalog entry.
  - set 3: Kuro Solar Inverter achieved an energy conversion efficiency of 96%, meeting the 95% minimum standard for listing.
- `m_78a4` (D1) [policy `p_c837`] <= (`m_e7ed` AND `e_b621`); gold after update: **keep**
  - set 1: Kuro Solar Inverter is registered on the green equipment catalog and carries a product warranty duration of 5 years, meeting both requirements for incentive clearance.
- `m_9d86` (B2) [policy `p_b5ce`] <= (`e_eca9`); gold after update: **keep**
  - set 1: Vesta Insulation Wrap provides a thermal resistance rating of 4 R-value, satisfying the minimum thermal standard for local building compliance.
- `u_ea7f` retracts `e_0976` (reliability high)
- `u_4ea5` retracts `e_5f73` (reliability high)
- decoy policies: `p_c92c`, `p_6e99`
- final state after updates (gold action -> state): `m_e7ed` keep -> holds; `m_9d86` keep -> holds; `m_78a4` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_eca9~p_b5ce` policy_echoes_evidence: "resistance rating of; thermal resistance rating" (judge under C7/C11)
- soft `e_b621~p_c837` policy_echoes_evidence: "a product warranty; product warranty duration; warranty duration of" (judge under C7/C11)
- soft `e_0976~p_85f0` policy_echoes_evidence: "conversion efficiency of; energy conversion efficiency" (judge under C7/C11)
- soft `e_d328->m_e7ed` record_scope_word_in_policy_clause: "record none, clause national" (judge under C10)

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

## s_4713369499  (F1-006, product eligibility)

*World:* An AI assistant tracks product specifications and certification data to determine eligibility for various distribution networks, quality badges, and retail programs.

### A. System view (judge C7 from this alone)
- `e_43f4` [2026-01-08, Materials Testing Laboratory Report] Biolabs NanoGrip Surgical Glove contains verified organic latex content of 92%.
- `e_1d9c` [2026-01-11, Quality Assurance Database] Vortex 500 Lab Centrifuge recorded a failure rate of 0.02% during the last quarter.
- `e_3a37` [2026-01-14, Energy Efficiency Program Portal] SunPure Purifier holds an active Energy Star certification.
- `e_a4c7` [2026-01-17, International Standards Registry] Vortex 500 Lab Centrifuge holds an active ISO 9001 credential.
- `e_759e` [2026-01-20, National Safety Compliance Board] AeroHelmet Pro sustained impact resistance of 450 joules during safety testing.
- memories:
  - `m_d602` Vortex 500 Lab Centrifuge satisfies premier operational standards.
  - `m_98ac` SunPure Purifier meets efficiency program guidelines.
  - `m_3763` Biolabs NanoGrip Surgical Glove qualifies for EcoHealth certification.
  - `m_02b9` Vortex 500 Lab Centrifuge is cleared for Clinical Supply Network placement.
  - `m_23b8` AeroHelmet Pro satisfies standard safety criteria.
- update `u_a11d` [2026-01-23, Annual Quality Audit Audit Summary] The compliance board confirmed that Vortex 500 Lab Centrifuge recorded no valid failure rate during the last quarter due to logging failures.
- policies:
  - `p_7836` An item attains premier operational status whenever its quarterly proportion of operational failures remains below 0.05% and it possesses a valid ISO 9001 credential.
  - `p_39ae` An equipment model is eligible for placement with Clinical Supply Network provided the item earns premier operational status.
  - `p_ba57` A commercial lighting fixture earns Sustainable Building Rebates if its annual energy consumption remains under 50 kilowatt-hours.
  - `p_e206` An industrial lubricant receives Premium Fleet Approval when its viscosity index exceeds 110 and its flash point reaches at least 200 degrees Celsius.
  - `p_9006` An appliance complies with energy guidelines when it possesses an active Energy Star certification.
  - `p_d6fa` Headwear earns safety clearance if its impact resistance measures 400 joules or higher.
  - `p_25ea` A medical item gains EcoHealth certification provided its organic latex content reaches at least 90%.

### B. Intended structure
- `m_d602` (B1) [policy `p_7836`] <= (`e_1d9c` AND `e_a4c7`); gold after update: **withdraw**
  - set 1: Vortex 500 Lab Centrifuge registered a failure rate of 0.02% during the last quarter, which is below the 0.05% threshold, and holds a active ISO 9001 credential.
- `m_02b9` (D1) [policy `p_39ae`] <= (`m_d602`); gold after update: **withdraw**
  - set 1: Vortex 500 Lab Centrifuge earns high-reliability status, making it eligible for placement with Clinical Supply Network.
- `m_3763` (B2) [policy `p_25ea`] <= (`e_43f4`); gold after update: **keep**
  - set 1: Biolabs NanoGrip Surgical Glove contains 92% organic latex content, satisfying the minimum requirement of 90%.
- `m_23b8` (B3) [policy `p_d6fa`] <= (`e_759e`); gold after update: **keep**
  - set 1: AeroHelmet Pro achieved an impact resistance of 450 joules, exceeding the 400 joules requirement.
- `m_98ac` (B4) [policy `p_9006`] <= (`e_3a37`); gold after update: **keep**
  - set 1: SunPure Purifier holds an active Energy Star certification, satisfying the program guideline.
- `u_a11d` retracts `e_1d9c` (reliability high)
- decoy policies: `p_e206`, `p_ba57`
- final state after updates (gold action -> state): `m_d602` withdraw -> fails; `m_3763` keep -> holds; `m_23b8` keep -> holds; `m_98ac` keep -> holds; `m_02b9` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_43f4~p_25ea` policy_echoes_evidence: "organic latex content" (judge under C7/C11)

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

## s_fc9e19bba7  (F2-009, travel logistics)

*World:* Assessment of carrier credentials and compliance for corporate travel contracts.

### A. System view (judge C7 from this alone)
- `e_5e0f` [2026-01-08, AeroSwift Charter Fleet Register] AeroSwift Charter currently operates an active fleet count of 18 units.
- `e_b232` [2026-01-11, Annual Aviation Logistics Review] AeroSwift Charter achieved a yearly consumer approval rating of 94 percent.
- `e_93b8` [2026-01-14, National Maritime Authority Records] BlueWave Cruises maintains an active Maritime Safety Authority Permit.
- `e_5020` [2026-01-17, IATA Registry Database] AeroSwift Charter holds a valid IOSA Certification for operational safety.
- `e_0d1e` [2026-01-20, AeroSwift Commercial Agreement] AeroSwift Charter provides a dedicated account management team.
- `e_eb8d` [2026-01-23, Civil Aviation Operations Log] AeroSwift Charter completed 620 annual flight dispatches over the past twelve months.
- `e_67a2` [2026-01-26, Bureau Veritas Compliance Certificate] AeroSwift Charter maintains a verified ISO 9001 Quality Management System credential.
- memories:
  - `m_3bd8` AeroSwift Charter is recognized as a Tier-One Operator.
  - `m_ef92` AeroSwift Charter should be selected for the Corporate Travel Framework contract.
  - `m_06ee` AeroSwift Charter is approved for Preferred Carrier Network membership.
  - `m_8f51` BlueWave Cruises satisfies the Coastal Passage License requirement.
- update `u_68c8` [2026-01-29, AeroSwift Charter Fleet Audit Report] AeroSwift Charter operates an active fleet count of 12 units following aircraft retirements.
- update `u_6c6f` [2026-02-01, Revised Aviation Logistics Audit] AeroSwift Charter recorded a yearly consumer approval rating of 82 percent.
- policies:
  - `p_fb19` A cargo freight provider gains Expedited Customs Authorization if its verified customs clearance time is under two hours and it maintains a surety bond of at least 1000000 dollars.
  - `p_f14d` A passenger vessel operator gains authorization for Coastal Passage License issuance when it possesses a valid Maritime Safety Authority Permit.
  - `p_2524` A ground transit service obtains Metropolitan Express Clearance whenever its vehicle fleet age is under four years.
  - `p_fbdc` A charter firm earns classification as a Tier-One Operator whenever its active fleet count reaches 15 units or higher, or it maintains valid IOSA Certification, or its yearly consumer approval rating is 90 percent or above, or its annual flight dispatches exceed 500 dispatches.
  - `p_5e11` An organization is chosen for the Corporate Travel Framework agreement provided it retains Preferred Carrier Network membership and provides a dedicated account management team.
  - `p_9a98` A transport entity enters the Preferred Carrier Network if it is classified as a Tier-One Operator and holds an active ISO 9001 Quality Management System credential.

### B. Intended structure
- `m_3bd8` (B1) [policy `p_fbdc`] <= (`e_5e0f`) **OR** (`e_5020`) **OR** (`e_b232`) **OR** (`e_eb8d`); gold after update: **keep**
  - set 1: AeroSwift Charter's active fleet count of 18 units meets the minimum requirement of 15 units.
  - set 2: AeroSwift Charter holds a valid IOSA Certification.
  - set 3: AeroSwift Charter's yearly consumer approval rating of 94 percent meets the required threshold of 90 percent.
  - set 4: AeroSwift Charter's annual flight dispatches of 620 exceed the minimum threshold of 500 dispatches.
- `m_06ee` (B2) [policy `p_9a98`] <= (`m_3bd8` AND `e_67a2`); gold after update: **keep**
  - set 1: AeroSwift Charter is recognized as a Tier-One Operator and holds an active ISO 9001 Quality Management System credential.
- `m_ef92` (D1) [policy `p_5e11`] <= (`m_06ee` AND `e_0d1e`); gold after update: **keep**
  - set 1: AeroSwift Charter is approved for Preferred Carrier Network membership and provides a dedicated account management team.
- `m_8f51` (B3) [policy `p_f14d`] <= (`e_93b8`); gold after update: **keep**
  - set 1: BlueWave Cruises maintains a valid Maritime Safety Authority Permit.
- `u_68c8` supersedes `e_5e0f` (reliability high)
- `u_6c6f` supersedes `e_b232` (reliability high)
- decoy policies: `p_fb19`, `p_2524`
- final state after updates (gold action -> state): `m_3bd8` keep -> holds; `m_8f51` keep -> holds; `m_06ee` keep -> holds; `m_ef92` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_5e0f~p_fbdc` policy_echoes_evidence: "active fleet count" (judge under C7/C11)
- soft `e_b232~p_fbdc` policy_echoes_evidence: "consumer approval rating; yearly consumer approval" (judge under C7/C11)
- soft `e_0d1e~p_5e11` policy_echoes_evidence: "a dedicated account; account management team; dedicated account management; provides a dedicated" (judge under C7/C11)
- soft `e_eb8d~p_fbdc` policy_echoes_evidence: "annual flight dispatches" (judge under C7/C11)

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

## s_5722a225fe  (F1-004, product eligibility)

*World:* An evaluation assistant assesses consumer hardware products for compliance and catalog eligibility across multiple retail distribution channels.

### A. System view (judge C7 from this alone)
- `e_b88d` [2026-01-08, Hardware Verification Registry, dated January 8, 2026.] Lumina Smart Ring demonstrated a battery standby time of 12 days.
- `e_c40d` [2026-01-11, Annual Quality Audit Report, dated January 11, 2026.] Apex Pro Headset recorded a customer returns rate of 2 percent this year.
- `e_edab` [2026-01-14, Official testing log from Audio Certification Lab, dated January 14, 2026.] Apex Pro Headset achieved an acoustic safety rating of 85 points.
- `e_ac57` [2026-01-17, EU Regulatory Compliance Register, dated January 17, 2026.] Apex Pro Headset maintains an active CE mark certification.
- `e_bec5` [2026-01-20, Environmental Test Center Filing, dated January 20, 2026.] Solis Solar Charger holds an IP67 waterproof certification.
- memories:
  - `m_3838` Apex Pro Headset satisfies regional health standards.
  - `m_9458` Solis Solar Charger meets rugged outdoor usage criteria.
  - `m_cb22` We recommend listing Apex Pro Headset for retail distribution.
  - `m_b0eb` Lumina Smart Ring qualifies for extended battery assurance.
- update `u_fa43` [2026-01-23, Audio Certification Lab amendment memo, dated January 23, 2026.] The lab report asserting an acoustic safety rating for Apex Pro Headset was retracted.
- policies:
  - `p_34d1` Authorization for commercial store placement is granted for a product meeting regional safety compliance that keeps its customer returns rate at or below 5 percent this year.
  - `p_7221` Outdoor durability approval requires equipment to possess IP67 waterproof certification.
  - `p_055a` Long-life power endorsement is granted when a wearable demonstrates a battery standby time exceeding 10 days.
  - `p_43fe` A commercial item receives green packaging designation if its recyclable content proportion equals or exceeds 75 percent.
  - `p_50a5` Regional safety compliance is achieved when an item maintains an acoustic safety rating of at least 80 points along with holding CE mark certification.
  - `p_c90a` A merchant account gains express fulfillment privileges when maintaining an order accuracy metric of at least 98 percent this quarter.

### B. Intended structure
- `m_3838` (B1) [policy `p_50a5`] <= (`e_edab` AND `e_ac57`); gold after update: **withdraw**
  - set 1: Apex Pro Headset has an acoustic safety rating of 85 points (meeting the 80 point threshold) and holds a CE mark certification, satisfying the requirements for regional safety compliance.
- `m_cb22` (D1) [policy `p_34d1`] <= (`m_3838` AND `e_c40d`); gold after update: **withdraw**
  - set 1: Apex Pro Headset meets regional safety compliance and has a customer returns rate of 2 percent this year (at or below the 5 percent limit), qualifying for retail distribution placement.
- `m_b0eb` (B2) [policy `p_055a`] <= (`e_b88d`); gold after update: **keep**
  - set 1: Lumina Smart Ring has a battery standby time of 12 days, exceeding the 10-day threshold required for long-life power endorsement.
- `m_9458` (B3) [policy `p_7221`] <= (`e_bec5`); gold after update: **keep**
  - set 1: Solis Solar Charger possesses an IP67 waterproof certification, satisfying the rule for outdoor durability approval.
- `u_fa43` retracts `e_edab` (reliability high)
- decoy policies: `p_c90a`, `p_43fe`
- final state after updates (gold action -> state): `m_3838` withdraw -> fails; `m_b0eb` keep -> holds; `m_9458` keep -> holds; `m_cb22` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_b88d~p_055a` policy_echoes_evidence: "a battery standby; battery standby time" (judge under C7/C11)
- soft `e_c40d~p_34d1` policy_echoes_evidence: "customer returns rate; percent this year" (judge under C7/C11)
- soft `e_edab~p_50a5` policy_echoes_evidence: "acoustic safety rating; an acoustic safety; safety rating of" (judge under C7/C11)
- soft `e_c40d->m_cb22` record_scope_word_in_policy_clause: "record none, clause regional" (judge under C10)

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

## s_0036b5549a  (F2-001, travel logistics)

*World:* An assessment of transportation vendors across various travel logistics sectors for client service contracts.

### A. System view (judge C7 from this alone)
- `e_eceb` [2026-01-08, Corporate fleet audit log] Apex Global Logistics maintains a fleet of 12 active executive shuttles.
- `e_81c4` [2026-01-11, Quality assurance registry] Horizon Aviation holds ISO 9001 certification.
- `e_eded` [2026-01-14, Aviation flight log database] Solstice Air logged 500 flight hours.
- `e_fb13` [2026-01-17, Harbour master logbook] Mariner Marine logged 150 port visits.
- `e_e8b9` [2026-01-20, Client service fulfillment record] Apex Global Logistics completed 50 successful corporate trips.
- `e_1253` [2026-01-23, Transport booking registry] Apex Global Logistics booked 15 luxury coach transfers.
- memories:
  - `m_50dc` Apex Global Logistics holds preferred transport provider status.
  - `m_795c` Apex Global Logistics meets the ground transportation capacity benchmark.
  - `m_87d2` Horizon Aviation maintains verified quality management systems.
  - `m_695c` Apex Global Logistics should be assigned to manage the executive summit logistics.
  - `m_8023` Solstice Air satisfies flight volume requirements.
  - `m_39c0` Mariner Marine satisfies maritime frequency metrics.
  - `m_a5f3` Apex Global Logistics qualifies for top-tier VIP travel handling.
- update `u_54c2` [2026-01-26, Audited transport booking registry] Apex Global Logistics booked 8 luxury coach transfers this quarter.
- update `u_06ea` [2026-01-29, Updated corporate fleet audit log] Apex Global Logistics maintains a fleet of 6 active executive shuttles.
- policies:
  - `p_232a` Ground transit capability standards are satisfied either by arranging at least 10 luxury coach transfers or by operating a fleet of no fewer than 10 active executive shuttles.
  - `p_7ddb` Express rail freight clearance is granted to any rail operator achieving a safety rating of at least 95 percent.
  - `p_a1d6` Eco-friendly fleet designation is awarded to commercial bus lines recording average carbon emissions below 120 grams per kilometer.
  - `p_3fa3` Provider preference designation is assigned to any operator that satisfies ground transit capability standards.
  - `p_0a97` Managing leadership conference transport is recommended for entities holding VIP travel service accreditation.
  - `p_9d6d` VIP travel service accreditation requires an operator with provider preference designation along with a record of at least 40 completed corporate trips.
  - `p_2272` An airline fulfills operational flight thresholds when registering a minimum of 300 flight hours.
  - `p_174c` Maritime service activity criteria are met by completing at least 100 port visits.
  - `p_fcba` Quality assurance validation is granted to any aviation service holding ISO 9001 certification.

### B. Intended structure
- `m_795c` (B1) [policy `p_232a`] <= (`e_1253`) **OR** (`e_eceb`); gold after update: **recompute**
  - set 1: Booking 15 luxury coach transfers in the quarter satisfies the threshold of 10 coach transfers.
  - set 2: Maintaining 12 active executive shuttles satisfies the threshold of 10 shuttles.
- `m_50dc` (B2) [policy `p_3fa3`] <= (`m_795c`); gold after update: **recompute**
  - set 1: Meeting ground transit capability standards grants provider preference designation.
- `m_a5f3` (B3) [policy `p_9d6d`] <= (`m_50dc` AND `e_e8b9`); gold after update: **recompute**
  - set 1: Holding provider preference designation together with completing 50 corporate trips during the quarter satisfies both criteria for VIP travel service accreditation.
- `m_695c` (D1) [policy `p_0a97`] <= (`m_a5f3`); gold after update: **recompute**
  - set 1: Holding VIP travel service accreditation satisfies the requirement for managing leadership conference transport.
- `m_8023` (B4) [policy `p_2272`] <= (`e_eded`); gold after update: **keep**
  - set 1: Logging 500 flight hours in the quarter satisfies the threshold of 300 flight hours.
- `m_87d2` (B5) [policy `p_fcba`] <= (`e_81c4`); gold after update: **keep**
  - set 1: Holding ISO 9001 certification satisfies the quality assurance validation requirement.
- `m_39c0` (B6) [policy `p_174c`] <= (`e_fb13`); gold after update: **keep**
  - set 1: Logging 150 port visits in the quarter satisfies the threshold of 100 port visits.
- `u_54c2` supersedes `e_1253` (reliability high)
- `u_06ea` supersedes `e_eceb` (reliability high)
- decoy policies: `p_7ddb`, `p_a1d6`
- final state after updates (gold action -> state): `m_795c` recompute -> fails; `m_8023` keep -> holds; `m_87d2` keep -> holds; `m_39c0` keep -> holds; `m_50dc` recompute -> fails; `m_a5f3` recompute -> fails; `m_695c` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_eceb~p_232a` policy_echoes_evidence: "active executive shuttles" (judge under C7/C11)
- soft `e_1253~p_232a` policy_echoes_evidence: "luxury coach transfers" (judge under C7/C11)
- soft `u_54c2` update_window_unstated: "none -> quarter" (judge under C4)

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

## s_1b054ddf3e  (F6-005, travel logistics)

*World:* A travel logistics assistant evaluates transport service providers, emergency preparedness, and delivery performance across regional operations.

### A. System view (judge C7 from this alone)
- `e_24b3` [2026-01-08, Quarterly logistics audit report.] AeroJet Logistics recorded a quarterly on-time delivery rate of 96 percent.
- `e_6746` [2026-01-11, National transit safety authority record.] Solaria Express holds an emergency response protocol certification.
- `e_97bc` [2026-01-14, Official state transport department registry extract.] Vance Chartering holds a valid commercial transport licence.
- `e_16ec` [2026-01-17, Annual transit safety board report.] Vance Chartering maintains a passenger safety score of 4.8 points.
- `e_a5c7` [2026-01-20, Verified fleet management database audit.] Vance Chartering manages an active fleet count of 15 vehicles.
- memories:
  - `m_23ff` AeroJet Logistics qualifies for premium route priority.
  - `m_6731` Vance Chartering maintains standard operational clearance.
  - `m_6a60` Vance Chartering is chosen for exclusive summit shuttle operations.
  - `m_081b` Vance Chartering holds preferred carrier designation.
  - `m_80fd` Solaria Express meets critical incident preparedness benchmarks.
- update `u_2653` [2026-01-23, Unverified online transport blog comment.] An anonymous forum posting states Vance Chartering never held a valid commercial transport licence.
- policies:
  - `p_9803` An aviation vendor earns flight corridor permission when logging zero safety infractions over a two year period.
  - `p_47ca` A maritime shipping firm receives deepwater docking authorization provided it possesses a total cargo capacity of 50000 tons.
  - `p_60fc` A transit agency obtains standard operational authorization provided it holds a valid commercial transport licence.
  - `p_0297` A regional carrier satisfies emergency readiness criteria once it obtains an emergency response protocol certification.
  - `p_9317` A freight operator earns high-priority dispatch handling when demonstrating a quarterly on-time delivery rate of 90 percent or higher.
  - `p_a6f9` A passenger carrier is assigned to premier summit transit duties provided it holds priority carrier recognition and maintains a passenger safety rating of at least 4.5 points.
  - `p_3fa2` A transit agency gains preferred carrier status if it holds standard operational authorization and manages an active fleet count of 10 vehicles or more.

### B. Intended structure
- `m_6731` (B1) [policy `p_60fc`] <= (`e_97bc`); gold after update: **uncertain**
  - set 1: Vance Chartering holds a valid commercial transport licence, satisfying the requirement for standard operational authorization.
- `m_081b` (B2) [policy `p_3fa2`] <= (`m_6731` AND `e_a5c7`); gold after update: **uncertain**
  - set 1: Vance Chartering possesses standard operational authorization and operates 15 active fleet vehicles, meeting the 10-vehicle threshold for preferred carrier status.
- `m_6a60` (D1) [policy `p_a6f9`] <= (`m_081b` AND `e_16ec`); gold after update: **uncertain**
  - set 1: Vance Chartering has attained preferred carrier status and recorded a passenger safety score of 4.8 points, exceeding the required 4.5 points threshold.
- `m_80fd` (B3) [policy `p_0297`] <= (`e_6746`); gold after update: **keep**
  - set 1: Solaria Express holds an active emergency response protocol certification, fulfilling the standard for emergency readiness.
- `m_23ff` (B4) [policy `p_9317`] <= (`e_24b3`); gold after update: **keep**
  - set 1: AeroJet Logistics registered a quarterly on-time delivery rate of 96 percent, exceeding the 90 percent threshold for high-priority dispatch handling.
- `u_2653` retracts `e_97bc` (reliability low)
- decoy policies: `p_47ca`, `p_9803`
- final state after updates (gold action -> state): `m_6731` uncertain -> undetermined; `m_80fd` keep -> holds; `m_23ff` keep -> holds; `m_081b` uncertain -> undetermined; `m_6a60` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_24b3~p_9317` policy_echoes_evidence: "a quarterly on-time; delivery rate of; on-time delivery rate; quarterly on-time delivery" (judge under C7/C11)
- soft `e_6746~p_0297` policy_echoes_evidence: "an emergency response; emergency response protocol; response protocol certification" (judge under C7/C11)
- soft `e_97bc~p_60fc` policy_echoes_evidence: "a valid commercial; commercial transport licence; holds a valid; valid commercial transport" (judge under C7/C11)
- soft `e_16ec~p_a6f9` policy_echoes_evidence: "a passenger safety; maintains a passenger" (judge under C7/C11)
- soft `e_a5c7~p_3fa2` policy_echoes_evidence: "active fleet count; an active fleet; fleet count of; manages an active" (judge under C7/C11)
- soft `m_6731` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)
- soft `m_081b` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)
- soft `m_6a60` final_state_mismatch: "gold uncertain, renderer fails" (judge under C13)

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

## s_ed05733e74  (F6-001, travel logistics)

*World:* Evaluating charter carrier qualifications and regional transport operators for upcoming travel logistics agreements.

### A. System view (judge C7 from this alone)
- `e_ad97` [2026-01-08, Federal Aviation Administration registry, January 2026.] AeroLuxe Charters holds an active FAA Part 135 certificate.
- `e_2481` [2026-01-11, Aviation Safety Council annual review, January 2026.] AeroLuxe Charters achieved a fleet safety rating of 4.9 stars.
- `e_6bbd` [2026-01-14, Maritime Travel Association annual report, January 2026.] Mariner Tours recorded an annual passenger volume of 150,000 customers this year.
- memories:
  - `m_af9d` AeroLuxe Charters holds premier flight status.
  - `m_4bf1` AeroLuxe Charters will handle executive travel for the upcoming summit.
  - `m_2075` AeroLuxe Charters is authorized for corporate VIP charter contracts.
  - `m_6cfe` Mariner Tours qualifies as a major regional ferry provider.
- update `u_3b06` [2026-01-17, Industry bulletin report, January 2026.] A recent audit inquiry has raised questions regarding whether AeroLuxe Charters holds an active FAA Part 135 certificate.
- policies:
  - `p_25f6` Priority customs clearance is extended to freight forwarders processing at least 500 metric tons of cargo per quarter.
  - `p_3a2e` An air carrier cleared for executive charter work must possess flight status at the premier level.
  - `p_8b31` Major regional transport provider status is granted to a marine line recording an annual passenger volume of at least 100,000 customers.
  - `p_d5fb` Flight status at the premier level is awarded to an operator maintaining an active FAA Part 135 certificate, or securing a fleet safety rating of 4.8 stars or higher.
  - `p_adb9` Preferred hotel alliance privileges are granted to lodging agencies with annual booking revenue exceeding 2,000,000 dollars.
  - `p_2245` Booking an airline operator for global conference transportation requires a service provider cleared for executive charter work.

### B. Intended structure
- `m_af9d` (B1) [policy `p_d5fb`] <= (`e_ad97`) **OR** (`e_2481`); gold after update: **keep**
  - set 1: AeroLuxe Charters holds an active FAA Part 135 certificate as required by the policy.
  - set 2: AeroLuxe Charters has a fleet safety rating of 4.9 stars, which meets the 4.8 stars requirement.
- `m_2075` (B2) [policy `p_3a2e`] <= (`m_af9d`); gold after update: **keep**
  - set 1: AeroLuxe Charters holds premier flight status, satisfying the condition for executive charter clearance.
- `m_4bf1` (D1) [policy `p_2245`] <= (`m_2075`); gold after update: **keep**
  - set 1: AeroLuxe Charters is authorized for corporate VIP charter contracts, satisfying the policy requirement for summit booking.
- `m_6cfe` (B3) [policy `p_8b31`] <= (`e_6bbd`); gold after update: **keep**
  - set 1: Mariner Tours recorded an annual passenger volume of 150,000 customers, exceeding the 100,000 threshold.
- `u_3b06` hedges `e_ad97` (reliability high)
- decoy policies: `p_25f6`, `p_adb9`
- final state after updates (gold action -> state): `m_af9d` keep -> holds; `m_6cfe` keep -> holds; `m_2075` keep -> holds; `m_4bf1` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2481~p_d5fb` policy_echoes_evidence: "a fleet safety; fleet safety rating; safety rating of" (judge under C7/C11)
- soft `e_6bbd~p_8b31` policy_echoes_evidence: "an annual passenger; annual passenger volume; passenger volume of" (judge under C7/C11)
- soft `e_6bbd->m_6cfe` record_scope_word_in_policy_clause: "record none, clause regional" (judge under C10)

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

## s_5aefca25cb  (F3-002, product eligibility)

*World:* Evaluation of commercial products against compliance and retail marketing eligibility standards.

### A. System view (judge C7 from this alone)
- `e_1f8c` [2026-01-08, Photovoltaic Testing Institute Standard Report] Helios Panel 300 achieved a peak power rating of 320 watts during standard testing.
- `e_d996` [2026-01-11, Apex Quality Assurance Audit Report] Zenith Pro Laptop has a recycled plastic content of 40 percent.
- `e_578c` [2026-01-14, European Consumer Safety Board Database] AeroShield Helmet maintains an official CE Safety Certification.
- `e_57ed` [2026-01-17, National Water Safety Lab Report] BioPure Water Filter demonstrated a lead removal rate of 99 percent in laboratory testing.
- `e_5cf1` [2026-01-20, EPA Public Certification Registry] Zenith Pro Laptop holds an official Energy Star certification.
- memories:
  - `m_c21d` BioPure Water Filter is designated for municipal distribution standard.
  - `m_4c87` Zenith Pro Laptop meets eco-friendly catalog criteria.
  - `m_9596` AeroShield Helmet satisfies international import safety regulations.
  - `m_9526` Zenith Pro Laptop is assigned to the sustainable product promotional showcase.
  - `m_d340` Helios Panel 300 qualifies for high-efficiency grid rebates.
- update `u_f74c` [2026-01-23, EPA Compliance Database Update] EPA compliance notice confirms Zenith Pro Laptop does not hold an Energy Star certification due to audit failure.
- policies:
  - `p_0158` A product is approved for green catalog listing provided it holds an Energy Star certification while maintaining a recycled plastic content of at least 35 percent.
  - `p_0173` Equipment earns municipal distribution approval if its lead removal rate reaches at least 95 percent.
  - `p_52ee` A solar module gains high-efficiency rebate status provided its peak power rating equals or exceeds 300 watts.
  - `p_8a9b` An item receives inclusion in promotional showcases when it is approved for green catalog listing.
  - `p_22d3` Industrial machinery qualifies for priority customs processing when backed by an ISO 9001 certification.
  - `p_99b6` Protective headgear clears cross-border trade requirements whenever it holds a valid CE Safety Certification.
  - `p_db02` A commercial appliance receives premium tier rating if its annual energy consumption remains below 200 kilowatt-hours.

### B. Intended structure
- `m_4c87` (B1) [policy `p_0158`] <= (`e_5cf1` AND `e_d996`); gold after update: **withdraw**
  - set 1: Zenith Pro Laptop holds an Energy Star certification and has a recycled plastic content of 40 percent, satisfying the requirements for green catalog listing.
- `m_9526` (D1) [policy `p_8a9b`] <= (`m_4c87`); gold after update: **withdraw**
  - set 1: Zenith Pro Laptop is approved for green catalog listing, qualifying it for inclusion in promotional showcases.
- `m_c21d` (B2) [policy `p_0173`] <= (`e_57ed`); gold after update: **keep**
  - set 1: BioPure Water Filter has a lead removal rate of 99 percent, exceeding the 95 percent requirement for municipal distribution approval.
- `m_d340` (B3) [policy `p_52ee`] <= (`e_1f8c`); gold after update: **keep**
  - set 1: Helios Panel 300 has a peak power rating of 320 watts, exceeding the 300 watt requirement for high-efficiency rebate status.
- `m_9596` (B4) [policy `p_99b6`] <= (`e_578c`); gold after update: **keep**
  - set 1: AeroShield Helmet possesses a CE Safety Certification, satisfying cross-border trade requirements.
- `u_f74c` retracts `e_5cf1` (reliability high)
- decoy policies: `p_db02`, `p_22d3`
- final state after updates (gold action -> state): `m_4c87` withdraw -> fails; `m_c21d` keep -> holds; `m_d340` keep -> holds; `m_9596` keep -> holds; `m_9526` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_1f8c~p_52ee` policy_echoes_evidence: "peak power rating" (judge under C7/C11)
- soft `e_d996~p_0158` policy_echoes_evidence: "a recycled plastic; plastic content of; recycled plastic content" (judge under C7/C11)
- soft `e_57ed~p_0173` policy_echoes_evidence: "lead removal rate" (judge under C7/C11)

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

## s_e1b163f207  (F3-001, travel logistics)

*World:* An evaluation of travel logistics service providers for specialized transport contracts.

### A. System view (judge C7 from this alone)
- `e_371c` [2026-01-08, Official member database of the International Air Transport Association.] Vanguard Logistics holds an IATA Cargo Operator Certificate.
- `e_2b12` [2026-01-11, Official registry of the International Freight Association.] Vanguard Logistics holds a Premier Air Carrier Accreditation.
- `e_73d6` [2026-01-14, Official public database of the Maritime Regulatory Authority.] Solstice Expeditions holds an International Maritime Charter License.
- `e_8417` [2026-01-17, Internal equipment log confirmed by the station manager.] Vanguard Logistics maintains a dedicated ground handler fleet of 20 vehicles.
- `e_22a8` [2026-01-20, Official fleet register from the Civil Aviation Authority.] Vanguard Logistics maintains an operational fleet of 15 cargo aircraft.
- `e_b867` [2026-01-23, Signed annual audit from Port Authority Logistics.] Vanguard Logistics handled an annual freight volume of 50000 metric tons last year.
- `e_c612` [2026-01-26, Official report from the Customs and Border Agency.] Vanguard Logistics achieved an annual customs clearance accuracy rate of 98 percent last year.
- memories:
  - `m_f65a` Vanguard Logistics holds Priority Freight Gateway Clearance.
  - `m_5274` Solstice Expeditions is approved for Oceanic Transport Routing.
  - `m_3d06` Vanguard Logistics meets Tier-1 Logistics Provider criteria.
  - `m_fdfc` Select Vanguard Logistics as the lead handler for the Express Airport Charter Contract.
- update `u_4526` [2026-01-29, Correction notice published by the Customs and Border Agency.] An official audit statement declared that Vanguard Logistics never attained an annual customs clearance accuracy rate of 98 percent last year.
- policies:
  - `p_d7b8` A maritime agency qualifies for Oceanic Transport Routing if the firm possesses an International Maritime Charter License.
  - `p_e690` A travel agency gains Preferred Rail Partner status if it maintains an annual rail ticket volume of at least 10000 tickets during the previous year.
  - `p_6574` An alpine tour operator receives Mountain Shuttle Certification provided it operates a snow coach fleet size of no fewer than 5 vehicles.
  - `p_ccef` An air carrier is awarded Priority Freight Gateway Clearance provided it maintains Premier Air Carrier Accreditation, or if it retains an IATA Cargo Operator Certificate alongside a cargo aircraft fleet size of 12 aircraft minimum, a yearly cargo weight transported of at least 40000 metric tons over the previous year, and an annual customs clearance accuracy rate of no lower than 95 percent during last year.
  - `p_439a` A logistics company is designated to oversee the Express Airport Charter Contract if the provider fulfills Tier-1 Logistics Provider criteria.
  - `p_bd81` A logistics firm satisfies Tier-1 Logistics Provider criteria when cleared for Priority Freight Gateway Clearance while simultaneously operating a minimum dedicated ground handler fleet size of 15 vehicles.

### B. Intended structure
- `m_f65a` (B1) [policy `p_ccef`] <= (`e_22a8` AND `e_c612` AND `e_b867` AND `e_371c`) **OR** (`e_2b12`); gold after update: **keep**
  - set 1: Vanguard Logistics satisfies the first justification set by maintaining 15 cargo aircraft against the 12 required, having a 98 percent customs accuracy rate versus 95 percent needed, recording 50000 metric tons of annual freight volume surpassing 40000, and holding an IATA Cargo Operator Certificate.
  - set 2: Vanguard Logistics satisfies the second justification set independently by holding Premier Air Carrier Accreditation.
- `m_3d06` (B2) [policy `p_bd81`] <= (`m_f65a` AND `e_8417`); gold after update: **keep**
  - set 1: Vanguard Logistics holds Priority Freight Gateway Clearance and maintains 20 ground handler vehicles, exceeding the threshold of 15.
- `m_fdfc` (D1) [policy `p_439a`] <= (`m_3d06`); gold after update: **keep**
  - set 1: Vanguard Logistics meets Tier-1 Logistics Provider criteria, qualifying it for designation over the Express Airport Charter Contract.
- `m_5274` (B3) [policy `p_d7b8`] <= (`e_73d6`); gold after update: **keep**
  - set 1: Solstice Expeditions holds an International Maritime Charter License, satisfying the condition for Oceanic Transport Routing.
- `u_4526` retracts `e_c612` (reliability high)
- decoy policies: `p_e690`, `p_6574`
- final state after updates (gold action -> state): `m_f65a` keep -> holds; `m_5274` keep -> holds; `m_3d06` keep -> holds; `m_fdfc` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_8417~p_bd81` policy_echoes_evidence: "dedicated ground handler; ground handler fleet" (judge under C7/C11)
- soft `e_c612~p_ccef` policy_echoes_evidence: "accuracy rate of; an annual customs; annual customs clearance; clearance accuracy rate; customs clearance accuracy" (judge under C7/C11)
- soft `groups 1/2` cross_group_entity: "Charter" (judge under C6)

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

*World:* Commercial hardware products are evaluated for corporate catalog distribution, retail promotion programs, and special deployment certifications based on safety testing, quality standards, and performance metrics.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, Flight telemetry logs, recorded January 8, 2026.] Vortex Pro Drone logged 120 zero-incident operational hours this quarter.
- `e_5dd0` [2026-01-11, International Standards Registry database entry, updated January 11, 2026.] Vortex Pro Drone holds an active ISO 9001 certification.
- `e_0823` [2026-01-14, Verified purchaser feedback summary, issued January 14, 2026.] Aura Smart Ring achieved a quarterly customer satisfaction score of 4.6 points.
- `e_45ef` [2026-01-17, Corporate risk management ledger, filed January 17, 2026.] Vortex Pro Drone carries commercial liability insurance coverage of $2,000,000 this year.
- `e_fdcd` [2026-01-20, National appliance lab report, certified January 20, 2026.] EcoChill Refrigerator recorded an annual energy consumption of 220 kWh.
- `e_f882` [2026-01-23, Independent testing lab certificate, delivered January 23, 2026.] Titanium Tech Laptop holds military-grade durability compliance.
- `e_660f` [2026-01-26, Skyward Robotics flight test report, logged January 26, 2026.] Vortex Pro Drone earned a flight safety score of 88 points on yearly evaluation.
- memories:
  - `m_6c9c` Vortex Pro Drone satisfies core manufacturing standards.
  - `m_cc95` Vortex Pro Drone is approved for the Enterprise Fleet Catalog.
  - `m_ece3` Titanium Tech Laptop is certified for rugged field usage.
  - `m_e062` Vortex Pro Drone is cleared for controlled airspace operations.
  - `m_bda8` Aura Smart Ring qualifies for the Premium Retail Placement program.
  - `m_6d1e` EcoChill Refrigerator earns the Green Home Energy designation.
- update `u_99cf` [2026-01-29, Tech Forum discussion thread, posted January 29, 2026.] An unverified blog post claims Vortex Pro Drone never completed annual safety testing.
- policies:
  - `p_cd31` An item with production quality clearance receives flight authorization for controlled skyways if it registers at least 100 zero-incident operational hours quarterly.
  - `p_b65d` Models possessing flight authorization for controlled skyways gain enrollment in the Enterprise Fleet Catalog when backed by $1,000,000 or more in annual commercial liability insurance coverage.
  - `p_b3f6` An appliance obtains the Green Home Energy designation if its annual energy consumption is no greater than 250 kWh.
  - `p_6aef` A product secures placement in the Premium Retail Placement program provided its quarterly customer satisfaction score reaches at least 4.5 points.
  - `p_d3ca` A mobile device achieves international trade clearance if it retains an FCC regulatory permit and demonstrates a battery lifetime of 20 hours or more.
  - `p_8aeb` Commercial hardware achieves production quality clearance either by retaining an active ISO 9001 certification or by earning a flight safety score of at least 85 points on yearly evaluation.
  - `p_c629` Commercial software attains global export authorization when it maintains SOC 2 audit verification.
  - `p_9e3e` A hardware device receives military deployment clearance whenever it maintains military-grade durability compliance.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Vortex Pro Drone achieved a flight safety score of 88 points during annual testing, satisfying the 85-point policy threshold.
  - set 2: Vortex Pro Drone holds an active ISO 9001 certification, fulfilling the credential requirement for production quality clearance.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Vortex Pro Drone satisfies production quality clearance and completed 120 zero-incident operational hours this quarter, exceeding the 100-hour requirement.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Vortex Pro Drone holds flight authorization for controlled skyways and maintains $2,000,000 in annual commercial liability insurance coverage, exceeding the $1,000,000 threshold.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Aura Smart Ring achieved a quarterly customer satisfaction score of 4.6 points, meeting the 4.5-point policy minimum.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: EcoChill Refrigerator recorded an annual energy consumption of 220 kWh, which is below the 250 kWh maximum limit.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: Titanium Tech Laptop holds military-grade durability compliance, satisfying the requirement for military deployment clearance.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_3dc4~p_cd31` policy_echoes_evidence: "zero-incident operational hours" (judge under C7/C11)
- soft `e_0823~p_6aef` policy_echoes_evidence: "customer satisfaction score; quarterly customer satisfaction" (judge under C7/C11)
- soft `e_45ef~p_b65d` policy_echoes_evidence: "commercial liability insurance; liability insurance coverage" (judge under C7/C11)
- soft `e_fdcd~p_b3f6` policy_echoes_evidence: "annual energy consumption" (judge under C7/C11)
- soft `e_f882~p_9e3e` policy_echoes_evidence: "military-grade durability compliance" (judge under C7/C11)
- soft `e_660f~p_8aeb` policy_echoes_evidence: "a flight safety; flight safety score; on yearly evaluation; points on yearly; safety score of" (judge under C7/C11)
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
