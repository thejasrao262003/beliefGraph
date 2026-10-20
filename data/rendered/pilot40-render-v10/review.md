# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* An evaluation of medical scalpel product compliance and commercial drone authorization for institutional procurement catalog inclusion.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Quality registry certificate] OmniSurg Scalpel maintains an active ISO 13485 quality certification.
- `e_94fc` [2026-01-11, Federal Aviation Administration registry entry] Zephyr Cargo Drone holds FAA commercial flight authorization.
- `e_0439` [2026-01-14, Policy document from Apex Mutual Insurance] OmniSurg Scalpel carries liability insurance coverage of $5,000,000.
- `e_b5f7` [2026-01-17, Official testing log from National Surgical Lab] OmniSurg Scalpel achieved a material durability rating of 88 points on the standard stress test.
- `e_df05` [2026-01-20, Official FDA approval database export] OmniSurg Scalpel holds valid FDA clearance for surgical operations.
- memories:
  - `m_c4d7` OmniSurg Scalpel qualifies for regional health system procurement.
  - `m_3f2d` OmniSurg Scalpel is approved for general clinical hospital use.
  - `m_280b` Zephyr Cargo Drone is cleared for commercial flight operations.
  - `m_c5de` OmniSurg Scalpel satisfies standard manufacturing quality criteria.
  - `m_5302` OmniSurg Scalpel meets full institutional catalog listing requirements.
  - `m_4b85` Authorize the automated purchase agreement for OmniSurg Scalpel.
- update `u_91ee` [2026-01-23, Re-inspection report from National Surgical Lab] A re-inspection revealed that OmniSurg Scalpel achieved a material durability rating of 72 points on the standard stress test.
- policies:
  - `p_fe1d` An instrument receives standard hospital usage clearance provided it satisfies baseline manufacturing quality compliance.
  - `p_5cd1` A surgical device qualifies for master supply catalog placement when it achieves health network purchasing eligibility and retains active FDA clearance.
  - `p_fbe6` Execution of supply contracts is recommended for any medical device that qualifies for master supply catalog placement.
  - `p_b0aa` An unmanned aerial system obtains commercial operation clearance provided it maintains valid FAA commercial flight authorization.
  - `p_1714` A medical item attains health network purchasing eligibility if it holds standard hospital usage clearance and possesses product indemnity coverage of no less than $3,000,000.
  - `p_4f8e` An educational institution obtains elite accreditation status provided its student graduation rate exceeds 90 percent over five years.
  - `p_0087` A product achieves baseline manufacturing quality compliance when it demonstrates a material stress rating of at least 80 points alongside valid ISO 13485 quality certification status.
  - `p_1a46` An office building receives a green facility designation if its annual energy consumption is under 150 kWh per square meter and it possesses a certified LEED badge.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: OmniSurg Scalpel's stress score of 88 points meets the 80-point threshold and it holds valid ISO 13485 certification.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: OmniSurg Scalpel fulfills baseline manufacturing quality compliance.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: OmniSurg Scalpel has hospital usage clearance and holds $5,000,000 in liability insurance, exceeding the $3,000,000 threshold.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: OmniSurg Scalpel has health network purchasing eligibility and retains active FDA clearance.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: OmniSurg Scalpel qualifies for master supply catalog placement.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Zephyr Cargo Drone holds active FAA commercial flight authorization.
- `u_91ee` supersedes `e_b5f7` (reliability high)
- decoy policies: `p_1a46`, `p_4f8e`
- final state after updates (gold action -> state): `m_c5de` recompute -> fails; `m_280b` keep -> holds; `m_3f2d` recompute -> fails; `m_c4d7` recompute -> fails; `m_5302` recompute -> fails; `m_4b85` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_94fc~p_b0aa` policy_echoes_evidence: "commercial flight authorization" (judge under C7/C11)

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

## s_9dcc85b8eb  (F1-001, travel logistics)

*World:* An evaluation of travel logistics service providers for corporate flight, ferry, and overland operations.

### A. System view (judge C7 from this alone)
- `e_2341` [2026-01-08, Maritime Transit Authority annual report, published 2026-01-08.] BlueWave Ferries recorded an annual passenger volume of 250000 passengers this year.
- `e_7cac` [2026-01-11, International Logistics Standards Board database, verified 2026-01-11.] Vanguard Overland holds an ISO 9001 Certification.
- `e_cfd6` [2026-01-14, Civil Aviation Authority registry report, dated 2026-01-14.] AeroJet Logistics maintains a fleet size of 15 aircraft.
- `e_943c` [2026-01-17, International Air Transport Association database, accessed 2026-01-17.] AeroJet Logistics holds an IATA Safety Certificate.
- memories:
  - `m_c9de` Vanguard Overland meets premier ground transport standards.
  - `m_bba5` BlueWave Ferries qualifies for priority port docking privileges.
  - `m_0430` Approve AeroJet Logistics for executive route scheduling.
- update `u_7b69` [2026-01-20, Civil Aviation Authority official filing, dated 2026-01-20.] AeroJet Logistics does not maintain a fleet size of 15 aircraft.
- policies:
  - `p_b42b` A charter flight firm is granted international customs pre-clearance when it completes 500 international flights per quarter.
  - `p_2cf5` A cargo carrier receives green environmental clearance if its annual carbon offset equals at least 5000 metric tons each year.
  - `p_9e27` A transport provider is designated for corporate transfer management if the fleet size is at least 10 aircraft and holds an IATA Safety Certificate.
  - `p_5068` A maritime carrier obtains preferred berth access if its annual passenger volume reaches at least 200000 passengers each year.
  - `p_50f3` A land transport vendor satisfies top-tier operational criteria provided it maintains an ISO 9001 Certification.

### B. Intended structure
- `m_0430` (D1) [policy `p_9e27`] <= (`e_cfd6` AND `e_943c`); gold after update: **withdraw**
  - set 1: AeroJet Logistics satisfies the criteria by having a fleet size of 15 aircraft, meeting the minimum requirement of 10 aircraft, and holding an IATA Safety Certificate.
- `m_bba5` (B1) [policy `p_5068`] <= (`e_2341`); gold after update: **keep**
  - set 1: BlueWave Ferries satisfies the policy threshold with an annual passenger volume of 250000 passengers this year, exceeding the minimum requirement of 200000 passengers.
- `m_c9de` (B2) [policy `p_50f3`] <= (`e_7cac`); gold after update: **keep**
  - set 1: Vanguard Overland meets the policy requirement by holding an ISO 9001 Certification.
- `u_7b69` retracts `e_cfd6` (reliability high)
- decoy policies: `p_2cf5`, `p_b42b`
- final state after updates (gold action -> state): `m_0430` withdraw -> fails; `m_bba5` keep -> holds; `m_c9de` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2341~p_5068` policy_echoes_evidence: "annual passenger volume" (judge under C7/C11)

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

## s_505ced526e  (F1-002, product eligibility)

*World:* An assistant evaluates product eligibility across distinct commercial compliance frameworks and product catalogs.

### A. System view (judge C7 from this alone)
- `e_c8b9` [2026-01-08, Official ISO registry database.] Apex Drone X1 holds an active ISO 9001 quality certificate.
- `e_4fa4` [2026-01-11, Certified laboratory test report.] Solis Solar Panel Model S4 generates peak power output of 450 W.
- `e_b2d8` [2026-01-14, Certified insurance policy schedule.] Apex Drone X1 carries third-party liability insurance coverage of $5,000,000 this year.
- `e_77ac` [2026-01-17, Official flight operations logbook.] Apex Drone X1 logged 120 test flight hours this year.
- `e_6292` [2026-01-20, Manufacturer technical datasheet.] Apex Drone X1 maintains a maximum payload weight capacity of 25 kg.
- `e_800b` [2026-01-23, Accredited testing facility certificate.] Vortex Water Pump V2 holds an active IP68 ingress protection rating.
- memories:
  - `m_3264` Apex Drone X1 secures heavy-duty commercial deployment authorization.
  - `m_4e26` Apex Drone X1 is granted entry into the EU Commercial Fleet Listing.
  - `m_6d59` Vortex Water Pump V2 meets all-weather submersion criteria.
  - `m_9eb1` Solis Solar Panel Model S4 achieves High-Output Energy Tier designation.
  - `m_8b64` Apex Drone X1 fulfills baseline manufacturing safety criteria.
- update `u_7214` [2026-01-26, Audited flight log registry.] Apex Drone X1 logged 60 test flight hours this year.
- policies:
  - `p_218c` An equipment model is granted commercial deployment status for heavy-duty uses if it fulfills foundational production safety norms and carries a maximum payload weight capacity of at least 20 kg.
  - `p_4dd9` Authorization for the EU Commercial Fleet Listing is conferred when a candidate has commercial deployment status for heavy-duty uses and holds third-party liability insurance coverage of at least $3,000,000 in a year.
  - `p_09ec` An apparatus satisfies all-weather submersion standards provided that it maintains an IP68 ingress protection rating.
  - `p_06ba` An industrial chiller obtains Green Ventilation Certification if it records an annual seasonal performance ratio of at least 15 and maintains an operational noise level under 50 dB.
  - `p_c6c7` An industrial battery system qualifies for Grid Reserve Status when its nominal storage capacity exceeds 500 kWh.
  - `p_5f11` A device meets foundational production safety norms when it completes a minimum of 100 test flight hours per year while holding an ISO 9001 quality certificate.
  - `p_887f` Designation under the High-Output Energy Tier is awarded to panels providing a peak power output of 400 W or greater.

### B. Intended structure
- `m_8b64` (B1) [policy `p_5f11`] <= (`e_77ac` AND `e_c8b9`); gold after update: **recompute**
  - set 1: Apex Drone X1 completed 120 test flight hours this year, meeting the 100-hour threshold, and maintains an ISO 9001 quality certificate, fulfilling baseline manufacturing safety criteria.
- `m_3264` (B2) [policy `p_218c`] <= (`m_8b64` AND `e_6292`); gold after update: **recompute**
  - set 1: Apex Drone X1 fulfills baseline manufacturing safety criteria and features a maximum payload weight capacity of 25 kg, exceeding the 20 kg minimum required for heavy-duty commercial deployment authorization.
- `m_4e26` (D1) [policy `p_4dd9`] <= (`m_3264` AND `e_b2d8`); gold after update: **recompute**
  - set 1: Apex Drone X1 holds heavy-duty commercial deployment authorization and maintains $5,000,000 in third-party liability insurance coverage, exceeding the $3,000,000 requirement for EU Commercial Fleet Listing.
- `m_9eb1` (B3) [policy `p_887f`] <= (`e_4fa4`); gold after update: **keep**
  - set 1: Solis Solar Panel Model S4 produces a peak power output of 450 W, satisfying the 400 W requirement for High-Output Energy Tier designation.
- `m_6d59` (B4) [policy `p_09ec`] <= (`e_800b`); gold after update: **keep**
  - set 1: Vortex Water Pump V2 holds an IP68 ingress protection rating, fulfilling all-weather submersion criteria.
- `u_7214` supersedes `e_77ac` (reliability high)
- decoy policies: `p_06ba`, `p_c6c7`
- final state after updates (gold action -> state): `m_8b64` recompute -> fails; `m_9eb1` keep -> holds; `m_6d59` keep -> holds; `m_3264` recompute -> fails; `m_4e26` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_4fa4~p_887f` policy_echoes_evidence: "peak power output; power output of" (judge under C7/C11)
- soft `e_b2d8~p_4dd9` policy_echoes_evidence: "insurance coverage of; liability insurance coverage; third-party liability insurance" (judge under C7/C11)
- soft `e_77ac~p_5f11` policy_echoes_evidence: "test flight hours" (judge under C7/C11)
- soft `e_6292~p_218c` policy_echoes_evidence: "a maximum payload; maximum payload weight; payload weight capacity; weight capacity of" (judge under C7/C11)
- soft `e_800b~p_09ec` policy_echoes_evidence: "ingress protection rating" (judge under C7/C11)

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

## s_77a028505e  (F1-003, travel logistics)

*World:* Assessment of commercial transport operators across air, rail, and maritime logistics networks.

### A. System view (judge C7 from this alone)
- `e_ca9d` [2026-01-08, State Rail Authority quarterly report, January 8, 2026.] Audit logs confirm Vanguard Rail Systems maintains an emergency response time of 25 minutes.
- `e_33ad` [2026-01-11, Port Authority compliance database, January 11, 2026.] Maritime port logs confirm Pacific Maritime Logistics holds an ISO 28000 security certification.
- `e_d70d` [2026-01-14, Federal Aviation Administration registry, January 14, 2026.] Official FAA registry records confirm AeroSwift Freight operates an active fleet size of 15 aircraft.
- `e_99aa` [2026-01-17, IATA audit summary document, January 17, 2026.] A safety audit report confirms AeroSwift Freight holds a valid IATA Safety Audit certificate.
- memories:
  - `m_dcef` AeroSwift Freight is selected for urgent cargo dispatch.
  - `m_50ea` Pacific Maritime Logistics is cleared for restricted dock access.
  - `m_5ffd` AeroSwift Freight holds official flight operator authorization.
  - `m_0082` Vanguard Rail Systems meets rapid incident handling standards.
- update `u_9335` [2026-01-20, Federal Aviation Administration registry update, January 20, 2026.] Updated FAA registry logs show AeroSwift Freight reduced its active fleet size to 8 aircraft.
- policies:
  - `p_a25d` A regional bus service qualifies for municipal transport subsidies when achieving an on-time arrival rate of 95 percent across the trailing quarter.
  - `p_2c54` Allocation of urgent cargo routing is conferred on a carrier that maintains recognized flight authority status.
  - `p_42e5` Entry into restricted dock facilities requires that a maritime enterprise holds an ISO 28000 security certification.
  - `p_9bc5` An enterprise secures recognized flight authority status when maintaining an active fleet size of at least 10 aircraft while holding an IATA Safety Audit certificate.
  - `p_ec25` Commercial storage licensing is awarded to a venue maintaining total indoor volume of at least 5000 cubic meters.
  - `p_b6c4` A railway network satisfies rapid incident response criteria if demonstrating an emergency response time of 30 minutes or less.

### B. Intended structure
- `m_5ffd` (B1) [policy `p_9bc5`] <= (`e_d70d` AND `e_99aa`); gold after update: **recompute**
  - set 1: AeroSwift Freight operates an active fleet size of 15 aircraft, which meets the threshold of 10 or more aircraft, and holds an IATA Safety Audit certificate, satisfying the policy requirements for recognized flight authority status.
- `m_dcef` (D1) [policy `p_2c54`] <= (`m_5ffd`); gold after update: **recompute**
  - set 1: AeroSwift Freight holds recognized flight authority status, which fulfills the policy requirement for allocation of urgent cargo routing.
- `m_0082` (B2) [policy `p_b6c4`] <= (`e_ca9d`); gold after update: **keep**
  - set 1: Vanguard Rail Systems maintains an emergency response time of 25 minutes, which satisfies the policy threshold of 30 minutes or less for rapid incident response criteria.
- `m_50ea` (B3) [policy `p_42e5`] <= (`e_33ad`); gold after update: **keep**
  - set 1: Pacific Maritime Logistics holds an ISO 28000 security certification, which meets the policy condition for entry into restricted dock facilities.
- `u_9335` supersedes `e_d70d` (reliability high)
- decoy policies: `p_a25d`, `p_ec25`
- final state after updates (gold action -> state): `m_5ffd` recompute -> fails; `m_0082` keep -> holds; `m_50ea` keep -> holds; `m_dcef` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `p_9bc5` policy_names_subject: "Audit" (judge under C11)
- soft `e_ca9d~p_b6c4` policy_echoes_evidence: "an emergency response; emergency response time; response time of" (judge under C7/C11)
- soft `e_d70d~p_9bc5` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of" (judge under C7/C11)
- soft `groups 1/2` cross_group_entity: "Audit" (judge under C6)
- soft `e_99aa->m_5ffd` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_d70d->m_5ffd` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_5ffd->m_dcef` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_ca9d->m_0082` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

## s_cdfd15e143  (F1-005, travel logistics)

*World:* The assistant tracks operational qualifications, port logistics performance, and safety compliance across various commercial transport providers.

### A. System view (judge C7 from this alone)
- `e_49bc` [2026-01-08, Civil Aviation Authority Fleet Registry] According to the civil aviation register, Horizon Charters operates an active fleet size of 12 aircraft.
- `e_549f` [2026-01-11, Port Authority Monthly Operations Log] Port authority records show Pacific Maritime reported a port dwell time of 18 hours last month.
- `e_01d4` [2026-01-14, National Transport Safety Board Registry] Official records from the national transport agency confirm Transit Link holds Safety First Certification.
- memories:
  - `m_7952` Pacific Maritime maintains optimal cargo turnaround performance.
  - `m_300a` Transit Link fulfills mandatory passenger safety standards.
  - `m_23c9` Horizon Charters is assigned to enterprise flight contracts.
- update `u_bd7b` [2026-01-17, Civil Aviation Authority Updated Fleet Registry] An updated filing from the civil aviation authority indicates Horizon Charters currently has an active fleet size of 8 aircraft.
- policies:
  - `p_c299` Travel operators satisfy core security requirements provided they hold Safety First Certification on a national level.
  - `p_d4ba` Baggage handling service providers qualify for tier-one priority access with an annual incident rate under 5 claims per ten thousand bags.
  - `p_0f0d` A freight dispatcher earns green routing compliance if annual fuel efficiency exceeds 15 kilometers per liter across regional operations.
  - `p_d329` Charter service providers qualify for heavy corporate transit agreements when maintaining an active fleet size of 10 aircraft or more.
  - `p_d77b` A shipping line achieves fast-track logistics status if its average port dwell time remains under 24 hours per container monthly.

### B. Intended structure
- `m_23c9` (D1) [policy `p_d329`] <= (`e_49bc`); gold after update: **recompute**
  - set 1: Horizon Charters meets the policy requirement because its active fleet size of 12 aircraft is at least the required 10 aircraft.
- `m_7952` (B1) [policy `p_d77b`] <= (`e_549f`); gold after update: **keep**
  - set 1: Pacific Maritime meets the policy requirement because its port dwell time of 18 hours is less than the 24 hours monthly threshold.
- `m_300a` (B2) [policy `p_c299`] <= (`e_01d4`); gold after update: **keep**
  - set 1: Transit Link meets the policy requirement because it holds Safety First Certification at the national level.
- `u_bd7b` supersedes `e_49bc` (reliability high)
- decoy policies: `p_0f0d`, `p_d4ba`
- final state after updates (gold action -> state): `m_23c9` recompute -> fails; `m_7952` keep -> holds; `m_300a` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_49bc~p_d329` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of" (judge under C7/C11)
- soft `e_549f~p_d77b` policy_echoes_evidence: "port dwell time" (judge under C7/C11)
- soft `e_49bc->m_23c9` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_549f->m_7952` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_01d4->m_300a` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

## s_4b1b069c1f  (F1-007, travel logistics)

*World:* An AI assistant updates its evaluation of regional passenger transport companies and excursion operators based on safety records, capacity data, and sustainability certifications.

### A. System view (judge C7 from this alone)
- `e_a030` [2026-01-08, Annual regional transport department statistics.] Solis Express logged annual passenger transit of 450,000 travelers this year.
- `e_31c2` [2026-01-11, National aviation safety board database.] Skyward Charters possesses an active Aviation Safety Certificate.
- `e_a4b0` [2026-01-14, Civil aviation authority fleet registry entry.] Skyward Charters maintains an active fleet size of 12 aircraft.
- `e_905a` [2026-01-17, International sustainable tourism council registry.] Nomad Tours holds an official Eco Tourism Accreditation.
- memories:
  - `m_e1c4` Recognize Solis Express as a major surface carrier.
  - `m_66a7` Designate Nomad Tours an approved sustainable excursion vendor.
  - `m_7f83` Assign Skyward Charters primary charter status.
- update `u_870a` [2026-01-20, Aviation regulatory compliance audit.] Recent audit confirms Skyward Charters does not maintain a fleet size of 12 aircraft.
- policies:
  - `p_fa6d` A tour agency gains sustainable excursion certification if it secures an official Eco Tourism Accreditation.
  - `p_d9af` A logistics station receives automated customs clearance when maintaining a minimum warehouse capacity of 5,000 metric tons.
  - `p_8e63` A ground transportation business earns major surface transport designation whenever its annual passenger transit reaches at least 400,000 travelers.
  - `p_c32e` A transport carrier attains primary charter authorization if it maintains a fleet size of 10 or more aircraft and possesses an active Aviation Safety Certificate.
  - `p_0ed9` A maritime freight operator achieves premier port priority provided it registers a dedicated cargo vessel count of at least five ships.

### B. Intended structure
- `m_7f83` (D1) [policy `p_c32e`] <= (`e_a4b0` AND `e_31c2`); gold after update: **withdraw**
  - set 1: Skyward Charters maintains a fleet size of 12 aircraft, meeting the minimum required threshold of 10, and possesses an active Aviation Safety Certificate.
- `m_e1c4` (B1) [policy `p_8e63`] <= (`e_a030`); gold after update: **keep**
  - set 1: Solis Express recorded an annual passenger transit of 450,000 travelers, satisfying the threshold of 400,000 travelers.
- `m_66a7` (B2) [policy `p_fa6d`] <= (`e_905a`); gold after update: **keep**
  - set 1: Nomad Tours holds an official Eco Tourism Accreditation.
- `u_870a` retracts `e_a4b0` (reliability high)
- decoy policies: `p_d9af`, `p_0ed9`
- final state after updates (gold action -> state): `m_7f83` withdraw -> fails; `m_e1c4` keep -> holds; `m_66a7` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_a030~p_8e63` policy_echoes_evidence: "annual passenger transit" (judge under C7/C11)
- soft `e_31c2~p_c32e` policy_echoes_evidence: "possesses an active" (judge under C7/C11)
- soft `e_a4b0~p_c32e` policy_echoes_evidence: "fleet size of" (judge under C7/C11)

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

## s_139ea9d6e9  (F1-008, product eligibility)

*World:* Assessment of commercial product eligibility, grant qualifications, and vendor tier approvals across various industry sectors.

### A. System view (judge C7 from this alone)
- `e_bf52` [2026-01-08, Green Power Verification Board report] Apex Agritech maintains a solar energy share of 60% this year.
- `e_0772` [2026-01-11, Zenith Robotics Annual Financial Audit] Zenith Robotics records an annual research expenditure of $12,000,000 this year.
- `e_5b13` [2026-01-14, FDA Official Registry listing] Novagen Pharma holds an active FDA Clean Facility Certification.
- `e_58c2` [2026-01-17, Corporate Insurance Portal policy record] Lumina Medical retains an indemnity protection limit of $10,000,000.
- `e_15c2` [2026-01-20, Central Audit Registry annual inspection document] Lumina Medical records a manufacturing defect rate of 0.4% this year.
- memories:
  - `m_0f29` Lumina Medical holds Tier-1 Quality Approval.
  - `m_997f` Lumina Medical is approved for Fast-Track Distribution.
  - `m_d46f` Novagen Pharma meets clinical safety requirements.
  - `m_ff90` Zenith Robotics qualifies for the Tech Innovation Grant.
  - `m_2b23` Apex Agritech achieves Green Vendor Designation.
  - `m_c84b` Lumina Medical satisfies the hardware durability standard.
- update `u_2dd3` [2026-01-23, Updated Central Audit Registry inspection report] Lumina Medical records a manufacturing defect rate of 2.1% this year.
- policies:
  - `p_7b59` A commercial enterprise receives preferred contractor status if its staff compliance score exceeds 90 points.
  - `p_7347` Priority marketplace entry is granted to a supplier with top-tier quality certification that maintains an indemnity protection limit of at least $5,000,000.
  - `p_eb0e` An enterprise is eligible for technology funding if its yearly turnover dedicated to research reaches at least $10,000,000.
  - `p_ed5d` A supplier gains eco-friendly provider status if its yearly renewable power fraction reaches at least 50%.
  - `p_44e7` Equipment approval on durability grounds requires a yearly failure proportion of 1.0% or less.
  - `p_d97f` Commercial partners receive expedited customs clearance if they hold an active ISO 14001 certification.
  - `p_173f` A firm attains clinical safety validation if it possesses valid regulatory sanitary site authorization.
  - `p_7645` An entity gains top-tier quality certification provided it meets equipment approval on durability grounds.

### B. Intended structure
- `m_c84b` (B1) [policy `p_44e7`] <= (`e_15c2`); gold after update: **recompute**
  - set 1: Lumina Medical's defect rate of 0.4% meets the requirement of being 1.0% or less.
- `m_0f29` (B2) [policy `p_7645`] <= (`m_c84b`); gold after update: **recompute**
  - set 1: Lumina Medical satisfies the hardware reliability standard, fulfilling the prerequisite for top-tier quality certification.
- `m_997f` (D1) [policy `p_7347`] <= (`m_0f29` AND `e_58c2`); gold after update: **recompute**
  - set 1: Lumina Medical holds Tier-1 Quality Approval and maintains an indemnity protection limit of $10,000,000, meeting the $5,000,000 threshold.
- `m_d46f` (B3) [policy `p_173f`] <= (`e_5b13`); gold after update: **keep**
  - set 1: Novagen Pharma holds an FDA Clean Facility Certification, satisfying the regulatory sanitary site condition.
- `m_ff90` (B4) [policy `p_eb0e`] <= (`e_0772`); gold after update: **keep**
  - set 1: Zenith Robotics has an annual research expenditure of $12,000,000, which exceeds the $10,000,000 minimum.
- `m_2b23` (B5) [policy `p_ed5d`] <= (`e_bf52`); gold after update: **keep**
  - set 1: Apex Agritech achieves a 60% solar energy share, surpassing the 50% threshold for eco-friendly status.
- `u_2dd3` supersedes `e_15c2` (reliability high)
- decoy policies: `p_7b59`, `p_d97f`
- final state after updates (gold action -> state): `m_c84b` recompute -> fails; `m_d46f` keep -> holds; `m_ff90` keep -> holds; `m_2b23` keep -> holds; `m_0f29` recompute -> fails; `m_997f` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_58c2~p_7347` policy_echoes_evidence: "an indemnity protection; indemnity protection limit; protection limit of" (judge under C7/C11)

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

## s_48a66886ab  (F1-009, travel logistics)

*World:* Travel logistics firm compliance evaluations, operator accreditations, and route expansion authorisations.

### A. System view (judge C7 from this alone)
- `e_c1f6` [2026-01-08, Quality standards organization registry.] Meridian Charters holds ISO 9001 quality management certification.
- `e_c4b4` [2026-01-11, Transport safety board annual report.] Vanguard Logistics achieved a yearly safety compliance score of 95 percent.
- `e_47ca` [2026-01-14, Certified bank balance statement.] Vanguard Logistics holds corporate escrow reserves of 2000000 USD.
- `e_c548` [2026-01-17, Regional transit authority report.] Horizon Express recorded an annual passenger volume of 500000 travelers this year.
- `e_0834` [2026-01-20, Aviation fleet audit registry.] Vanguard Logistics operates an active fleet of 15 charter aircraft.
- `e_5cda` [2026-01-23, Department of Transportation commercial vehicle register.] Solis Freight maintains a total vehicle count of 50 cargo trucks.
- memories:
  - `m_b1bf` Vanguard Logistics satisfies premium carrier credentials.
  - `m_0c41` Vanguard Logistics receives diplomatic transport assignment approval.
  - `m_206c` Vanguard Logistics holds fleet-scale operator classification.
  - `m_cad9` Vanguard Logistics earns elite transit vendor designation.
  - `m_fb2b` Vanguard Logistics secures high-capacity contract authorization.
  - `m_6e6a` Horizon Express qualifies for regional route expansion clearance.
  - `m_0ad9` Meridian Charters attains international Quality Assurance standard compliance.
  - `m_afd9` Solis Freight meets national cargo logistics provider eligibility.
- update `u_6bfd` [2026-01-26, Updated aviation fleet audit registry.] Vanguard Logistics now operates an active fleet of 8 charter aircraft.
- policies:
  - `p_f404` Diplomatic travel missions are assigned to enterprise carriers with major scale contract clearance.
  - `p_2b2e` Standard quality assurance recognition is accorded to any provider maintaining ISO 9001 certification.
  - `p_1782` Authorization for high-capacity operations requires elite vendor standing combined with liquid corporate reserves reaching at least 1500000 USD.
  - `p_cd15` Premium carrier status is awarded to a fleet-scale operator whose yearly safety audit rating is 90 percent or higher.
  - `p_638c` An operator receives fleet-scale classification provided their active charter aircraft tally reaches 10 units or more.
  - `p_6950` Logistics provider eligibility nationwide requires a minimum commercial vehicle fleet size of 30 trucks.
  - `p_8825` Vendor designation at the elite level is conferred on any organization possessing premium carrier status.
  - `p_65b4` Deep-sea harbor access is granted to shipping companies maintaining an annual container volume above 1000000 TEU.
  - `p_d7f7` Express rail service privileges require a punctual arrival percentage of at least 98 percent over the preceding quarter.
  - `p_700c` Approval for regional territory expansion is granted to transit operators carrying a yearly passenger count exceeding 400000 travelers.

### B. Intended structure
- `m_206c` (B1) [policy `p_638c`] <= (`e_0834`); gold after update: **recompute**
  - set 1: Vanguard Logistics operates 15 charter aircraft, which meets the policy threshold of at least 10 active units.
- `m_b1bf` (B2) [policy `p_cd15`] <= (`m_206c` AND `e_c4b4`); gold after update: **recompute**
  - set 1: Vanguard Logistics holds fleet-scale operator classification and achieved a 95 percent safety score, surpassing the 90 percent policy requirement.
- `m_cad9` (B3) [policy `p_8825`] <= (`m_b1bf`); gold after update: **recompute**
  - set 1: Vanguard Logistics satisfies premium carrier credentials, fulfilling the sole requirement for elite vendor status.
- `m_fb2b` (B4) [policy `p_1782`] <= (`m_cad9` AND `e_47ca`); gold after update: **recompute**
  - set 1: Vanguard Logistics holds elite transit vendor designation and has 2000000 USD in escrow, exceeding the 1500000 USD reserve requirement.
- `m_0c41` (D1) [policy `p_f404`] <= (`m_fb2b`); gold after update: **recompute**
  - set 1: Vanguard Logistics possesses high-capacity contract authorization, satisfying the single condition for diplomatic assignment clearance.
- `m_6e6a` (B5) [policy `p_700c`] <= (`e_c548`); gold after update: **keep**
  - set 1: Horizon Express recorded 500000 yearly passengers, exceeding the required threshold of 400000 travelers.
- `m_0ad9` (B6) [policy `p_2b2e`] <= (`e_c1f6`); gold after update: **keep**
  - set 1: Meridian Charters holds ISO 9001 certification, fulfilling the credential requirement for Quality Assurance compliance.
- `m_afd9` (B7) [policy `p_6950`] <= (`e_5cda`); gold after update: **keep**
  - set 1: Solis Freight maintains 50 cargo trucks, satisfying the threshold of at least 30 commercial vehicles.
- `u_6bfd` supersedes `e_0834` (reliability high)
- decoy policies: `p_65b4`, `p_d7f7`
- final state after updates (gold action -> state): `m_206c` recompute -> fails; `m_6e6a` keep -> holds; `m_0ad9` keep -> holds; `m_afd9` keep -> holds; `m_b1bf` recompute -> fails; `m_cad9` recompute -> fails; `m_fb2b` recompute -> fails; `m_0c41` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `groups 1/4` cross_group_entity: "Logistics" (judge under C6)

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

## s_3d821bdd07  (F2-000, product eligibility)

*World:* Assessment of commercial partners for product distribution and discount eligibility based on audited figures and certified credentials.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Transport Safety Authority certified fleet register dated 2026-01-08.] Orion Dynamics maintains a fleet size of 50 commercial vehicles.
- `e_dfe6` [2026-01-11, National Industry Licensing Board registry entry from 2026-01-11.] ValenTech holds a Tier-1 Supplier License.
- `e_e50c` [2026-01-14, Audit Corp, official financial audit report dated 2026-01-14.] ValenTech recorded annual sales revenue of 2000000 USD for the year.
- memories:
  - `m_2075` ValenTech satisfies approved supplier standards.
  - `m_36f2` Orion Dynamics obtains fleet discount eligibility.
  - `m_7743` ValenTech gains enrollment within the premier vendor directory.
- update `u_a152` [2026-01-17, Audit Corp, corrected official filing dated 2026-01-17.] ValenTech recorded annual sales revenue of 1000000 USD for the year.
- update `u_41fa` [2026-01-20, National Industry Licensing Board official cancellation notice dated 2026-01-20.] ValenTech holds no Tier-1 Supplier License.
- policies:
  - `p_d10e` An enterprise achieves approved supplier qualification when its annual sales revenue equals 1500000 USD or more over the year, or when it holds a Tier-1 Supplier License.
  - `p_8779` Commercial clients receive extended payment terms when maintaining a safety compliance score above 85 points.
  - `p_3b4c` Placement on the top vendor registry is authorized for every firm that maintains approved supplier criteria.
  - `p_4091` A business secures fleet rate reductions if its fleet size equals at least 30 commercial vehicles.
  - `p_e525` A distributor qualifies for fast-track shipping if their warehouse capacity exceeds 10000 square meters.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: ValenTech's annual sales revenue of 2,000,000 USD meets the required threshold of 1,500,000 USD for approved supplier qualification.
  - set 2: ValenTech holds a Tier-1 Supplier License, satisfying the alternative requirement for approved supplier qualification.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: ValenTech satisfies approved supplier standards, granting it placement on the top vendor registry.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: Orion Dynamics maintains 50 commercial vehicles, exceeding the threshold of 30 required for fleet rate reductions.
- `u_a152` supersedes `e_e50c` (reliability high)
- `u_41fa` supersedes `e_dfe6` (reliability high)
- decoy policies: `p_e525`, `p_8779`
- final state after updates (gold action -> state): `m_2075` recompute -> fails; `m_36f2` keep -> holds; `m_7743` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_e50c~p_d10e` policy_echoes_evidence: "annual sales revenue" (judge under C7/C11)

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

## s_e572517607  (F2-002, product eligibility)

*World:* An evaluation of technical hardware products determines their market compliance, sales authorizations, and eligibility for support incentives.

### A. System view (judge C7 from this alone)
- `e_35ea` [2026-01-08, ISO Central Registry audit report] AeroGlider X1 holds an ISO 9001 quality certificate.
- `e_d8ee` [2026-01-11, Federal Aviation Administration public ledger] AeroGlider X1 possesses an FAA Airworthiness endorsement.
- `e_a75c` [2026-01-14, Water Quality Association official register] BioPure Filter V possesses a Water Quality Association certification.
- `e_92fd` [2026-01-17, Laboratory performance testing report] SolarPulse 500 achieved a peak efficiency rating of 98% this quarter.
- `e_f9a9` [2026-01-20, European Conformity database entry] AeroGlider X1 holds a European Conformity mark.
- `e_071c` [2026-01-23, Annual quality assurance report] AeroGlider X1 recorded a defect rate of 0.2% this year.
- memories:
  - `m_fb27` SolarPulse 500 qualifies for high-efficiency rebate schemes.
  - `m_c375` AeroGlider X1 should be approved for wholesale listing.
  - `m_17b3` BioPure Filter V is eligible for public health procurement.
  - `m_6ff2` AeroGlider X1 is qualified for commercial distribution.
  - `m_2e83` AeroGlider X1 satisfies primary safety standard requirements.
- update `u_4f0d` [2026-01-26, ISO Oversight Board revocation filing] Official registry filings confirm AeroGlider X1 never received an ISO 9001 quality certificate.
- update `u_2cf7` [2026-01-29, FAA Regulatory Update Bulletin] Federal records show AeroGlider X1 does not hold an FAA Airworthiness endorsement.
- update `u_17b6` [2026-02-01, EU Market Surveillance report] European compliance filings indicate AeroGlider X1 lacks a European Conformity mark.
- policies:
  - `p_b2ab` Premium warranty coverage is extended to industrial equipment operating with a continuous thermal output under 40 degrees Celsius.
  - `p_8238` Priority supply chain routing is assigned to orders with a minimum batch volume of 500 units.
  - `p_fc6a` High-efficiency rebate eligibility is granted to equipment demonstrating a quarterly peak energy output efficiency of at least 95%.
  - `p_eb81` Wholesale listing approval requires a product with commercial distribution clearance to maintain an annual defect frequency below 0.5%.
  - `p_388b` Public health procurement endorsement requires a device to maintain Water Quality Association certification.
  - `p_3448` Baseline safety compliance is established when a device holds an ISO 9001 quality certificate, a European Conformity mark, or an FAA Airworthiness endorsement.
  - `p_21c5` Commercial distribution clearance is granted to any product that maintains baseline safety compliance.

### B. Intended structure
- `m_2e83` (B1) [policy `p_3448`] <= (`e_35ea`) **OR** (`e_f9a9`) **OR** (`e_d8ee`); gold after update: **withdraw**
  - set 1: AeroGlider X1 holding an ISO 9001 quality certificate satisfies the baseline safety compliance rule.
  - set 2: AeroGlider X1 holding a European Conformity mark satisfies the baseline safety compliance rule.
  - set 3: AeroGlider X1 possessing an FAA Airworthiness endorsement satisfies the baseline safety compliance rule.
- `m_6ff2` (B2) [policy `p_21c5`] <= (`m_2e83`); gold after update: **withdraw**
  - set 1: AeroGlider X1 satisfying baseline safety compliance meets the condition for commercial distribution clearance.
- `m_c375` (D1) [policy `p_eb81`] <= (`m_6ff2` AND `e_071c`); gold after update: **withdraw**
  - set 1: AeroGlider X1 having commercial distribution clearance and a yearly defect rate of 0.2%, which is under 0.5%, fulfills the requirements for wholesale listing approval.
- `m_fb27` (B3) [policy `p_fc6a`] <= (`e_92fd`); gold after update: **keep**
  - set 1: SolarPulse 500 achieving a quarterly peak efficiency rating of 98%, exceeding the 95% threshold, satisfies the high-efficiency rebate requirement.
- `m_17b3` (B4) [policy `p_388b`] <= (`e_a75c`); gold after update: **keep**
  - set 1: BioPure Filter V holding a Water Quality Association certification satisfies the public health procurement policy.
- `u_4f0d` retracts `e_35ea` (reliability high)
- `u_2cf7` retracts `e_d8ee` (reliability high)
- `u_17b6` retracts `e_f9a9` (reliability high)
- decoy policies: `p_b2ab`, `p_8238`
- final state after updates (gold action -> state): `m_2e83` withdraw -> fails; `m_fb27` keep -> holds; `m_17b3` keep -> holds; `m_6ff2` withdraw -> fails; `m_c375` withdraw -> fails

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

## s_daf211471b  (F2-003, travel logistics)

*World:* Corporate travel managers evaluate charter flight providers, maritime carriers, and regional shuttle services for transport contracts.

### A. System view (judge C7 from this alone)
- `e_2285` [2026-01-08, Regional Transit Board authorization filing] Summit Alpine Shuttles holds an official Passenger Transport License.
- `e_79a9` [2026-01-11, Maritime Transport Authority registry report] Mariner Freight operates an active fleet size of 25 cargo vessels.
- `e_2f03` [2026-01-14, AeroWay Express fleet registry report] AeroWay Express maintains a fleet size of 12 operating jets.
- `e_83ee` [2026-01-17, Civil Aviation Authority annual traffic summary] AeroWay Express registered an annual passenger volume of 50,000 travelers last year.
- `e_46ad` [2026-01-20, ISO online accreditation directory] AeroWay Express possesses an active ISO 9001 quality certificate.
- `e_3da2` [2026-01-23, Federal Aviation Administration registry entry] AeroWay Express holds an official FAA Air Carrier Certificate.
- `e_68a5` [2026-01-26, Global Aerospace underwriters policy document] AeroWay Express maintains liability insurance coverage of 50 million dollars.
- memories:
  - `m_bc5c` Mariner Freight satisfies maritime carrier requirements.
  - `m_a1ea` Summit Alpine Shuttles maintains valid shuttle operator approval.
  - `m_6269` Assign AeroWay Express as the primary flight service provider.
  - `m_c517` AeroWay Express retains preferred corporate partner status.
  - `m_debe` AeroWay Express meets approved charter service criteria.
- update `u_a73f` [2026-01-29, Civil Aviation Authority corrected audit statement] A recent audit revealed that AeroWay Express did not register an annual passenger volume of 50,000 travelers last year.
- update `u_e5b8` [2026-02-01, Federal Aviation Administration notice] Federal regulatory updates confirm that AeroWay Express does not hold an official FAA Air Carrier Certificate.
- update `u_fb90` [2026-02-04, AeroWay Express revised fleet filing] An updated equipment audit states that AeroWay Express does not maintain a fleet size of 12 operating jets.
- policies:
  - `p_5085` A transport carrier is selected as chief flight provider if backed by corporate partner standing and liability insurance coverage of at least 30 million dollars.
  - `p_0001` A transit firm receives eco-accreditation if it manages a vehicle count of at least 15 electric buses.
  - `p_615b` An aviation enterprise attains charter accreditation if it operates a minimum fleet size of 10 aircraft, maintains valid ISO 9001 certification, moves at least 40000 passengers annually, or possesses an FAA Air Carrier Certificate.
  - `p_4087` An aviation firm receives corporate partner standing provided it achieves charter accreditation.
  - `p_9f69` A dock management company obtains priority berth access if it records an annual cargo throughput of at least 100000 metric tons.
  - `p_4efc` A transit agency secures shuttle operator authorization if it holds a Passenger Transport License.
  - `p_772f` A shipping firm achieves maritime carrier accreditation if it operates a minimum fleet size of 20 cargo vessels.

### B. Intended structure
- `m_debe` (B1) [policy `p_615b`] <= (`e_2f03`) **OR** (`e_46ad`) **OR** (`e_83ee`) **OR** (`e_3da2`); gold after update: **keep**
  - set 1: AeroWay Express satisfies the charter accreditation requirement by operating a fleet size of 12 jets, exceeding the 10 jet threshold.
  - set 2: AeroWay Express fulfills the charter accreditation requirement by holding an active ISO 9001 quality certificate.
  - set 3: AeroWay Express satisfies the charter accreditation requirement by recording an annual passenger volume of 50,000 travelers, exceeding the 40,000 traveler threshold.
  - set 4: AeroWay Express meets the charter accreditation requirement by holding an official FAA Air Carrier Certificate.
- `m_c517` (B2) [policy `p_4087`] <= (`m_debe`); gold after update: **keep**
  - set 1: AeroWay Express obtains corporate partner standing because it holds charter accreditation.
- `m_6269` (D1) [policy `p_5085`] <= (`m_c517` AND `e_68a5`); gold after update: **keep**
  - set 1: AeroWay Express is designated as chief flight provider because it possesses corporate partner standing and maintains liability insurance coverage of 50 million dollars, exceeding the 30 million dollar threshold.
- `m_bc5c` (B3) [policy `p_772f`] <= (`e_79a9`); gold after update: **keep**
  - set 1: Mariner Freight secures maritime carrier accreditation by operating a fleet size of 25 cargo vessels, exceeding the 20 vessel threshold.
- `m_a1ea` (B4) [policy `p_4efc`] <= (`e_2285`); gold after update: **keep**
  - set 1: Summit Alpine Shuttles attains shuttle operator authorization by holding a Passenger Transport License.
- `u_a73f` retracts `e_83ee` (reliability high)
- `u_e5b8` retracts `e_3da2` (reliability high)
- `u_fb90` retracts `e_2f03` (reliability high)
- decoy policies: `p_0001`, `p_9f69`
- final state after updates (gold action -> state): `m_debe` keep -> holds; `m_bc5c` keep -> holds; `m_a1ea` keep -> holds; `m_c517` keep -> holds; `m_6269` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_79a9~p_615b` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_79a9~p_772f` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_2f03~p_615b` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_2f03~p_772f` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_68a5~p_5085` policy_echoes_evidence: "insurance coverage of; liability insurance coverage" (judge under C7/C11)

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

## s_b6bb9f7f71  (F2-005, travel logistics)

*World:* A evaluation of air, overland, and maritime shipping logistics providers for compliance and charter contract allocations.

### A. System view (judge C7 from this alone)
- `e_7f19` [2026-01-08, Annual audit report issued by the Customs Bureau.] AeroSwift Logistics maintains a customs compliance score of 94 percent.
- `e_de69` [2026-01-11, Official fleet register report from the Civil Aviation Authority.] AeroSwift Logistics maintains an active fleet size of 18 aircraft.
- `e_d065` [2026-01-14, Certified payroll and staffing log from the safety compliance department.] AeroSwift Logistics retains a safety supervisor headcount of 4 officers.
- `e_4c18` [2026-01-17, Cold storage facility audit report by Quality Standards Inspection.] Zenith Express maintains a warehouse temperature control rating of 98 percent.
- `e_b312` [2026-01-20, Vehicle registration database from the Department of Transportation.] Portside Haulage operates an active heavy vehicle fleet of 25 trucks.
- `e_54d4` [2026-01-23, Official permit registry of the Port Safety Authority.] BlueWave Logistics possesses a maritime hazard handling permit.
- `e_86fa` [2026-01-26, Certificate of insurance provided by Commercial Maritime & Aviation Insurers.] AeroSwift Logistics holds transit liability insurance coverage of $6,000,000.
- `e_df43` [2026-01-29, Verified monthly dispatch summary from the flight operations desk.] AeroSwift Logistics completed a monthly shipment volume of 110 cargo flights in December.
- memories:
  - `m_cb1b` AeroSwift Logistics is cleared for expedited border routing.
  - `m_d367` AeroSwift Logistics meets international dispatch prerequisites.
  - `m_435d` Zenith Express achieves cold-chain authorization.
  - `m_e6eb` Portside Haulage fulfills overland freight criteria.
  - `m_c8c2` AeroSwift Logistics should be selected for the global freight agreement.
  - `m_9bc2` BlueWave Logistics is designated for hazmat transit.
  - `m_99a9` AeroSwift Logistics holds Preferred Transit Status.
- update `u_ea5b` [2026-02-01, Corrected quarterly audit from the Civil Aviation Authority.] A revised flight operations audit indicates AeroSwift Logistics completed a monthly shipment volume of 85 cargo flights in December.
- policies:
  - `p_3041` Hazardous cargo transit clearance is issued when a shipping enterprise possesses a maritime hazard handling permit.
  - `p_c5bb` Expedited border pass authorization is granted to a company with preferred level transit status that maintains a customs compliance score of at least 90 percent.
  - `p_cff7` Cold-chain operating approval is granted when a logistics firm maintains a warehouse temperature control rating of at least 95 percent.
  - `p_adfd` An aviation provider receives high-altitude flight approval when maintaining an annual crew safety score of at least 90 points.
  - `p_4272` A rail transport operator secures trackway access rights by maintaining a network line length of at least 500 kilometers.
  - `p_b757` Qualification for international dispatch services requires a freight firm with expedited border pass authorization to retain a safety supervisor headcount of at least 3 officers.
  - `p_bf8b` Overland freight qualification is established when a transport company operates an active heavy vehicle fleet of at least 20 trucks.
  - `p_2123` Transit status at the preferred level is awarded when a freight enterprise maintains an active fleet size of at least 15 aircraft or completes a monthly shipment volume of at least 100 cargo flights.
  - `p_6054` Awarding of a worldwide logistics charter is recommended for a freight company cleared for international dispatch that maintains transit liability insurance coverage of at least $5,000,000.

### B. Intended structure
- `m_99a9` (B1) [policy `p_2123`] <= (`e_de69`) **OR** (`e_df43`); gold after update: **keep**
  - set 1: AeroSwift Logistics maintains an active fleet size of 18 aircraft, which meets the requirement of at least 15 aircraft.
  - set 2: AeroSwift Logistics completed a monthly shipment volume of 110 cargo flights, which meets the requirement of at least 100 cargo flights.
- `m_cb1b` (B2) [policy `p_c5bb`] <= (`m_99a9` AND `e_7f19`); gold after update: **keep**
  - set 1: AeroSwift Logistics holds Preferred Transit Status and maintains a customs compliance score of 94 percent, satisfying both prerequisites for expedited border pass authorization.
- `m_d367` (B3) [policy `p_b757`] <= (`m_cb1b` AND `e_d065`); gold after update: **keep**
  - set 1: AeroSwift Logistics is cleared for expedited border routing and retains a safety supervisor headcount of 4 officers, fulfilling all conditions for international dispatch qualification.
- `m_c8c2` (D1) [policy `p_6054`] <= (`m_d367` AND `e_86fa`); gold after update: **keep**
  - set 1: AeroSwift Logistics meets international dispatch prerequisites and holds transit liability insurance coverage of 6 million dollars, meeting all criteria for global freight agreement selection.
- `m_435d` (B4) [policy `p_cff7`] <= (`e_4c18`); gold after update: **keep**
  - set 1: Zenith Express maintains a warehouse temperature control rating of 98 percent, exceeding the 95 percent threshold required for cold-chain operating approval.
- `m_e6eb` (B5) [policy `p_bf8b`] <= (`e_b312`); gold after update: **keep**
  - set 1: Portside Haulage operates an active heavy vehicle fleet of 25 trucks, meeting the 20 truck threshold for overland freight qualification.
- `m_9bc2` (B6) [policy `p_3041`] <= (`e_54d4`); gold after update: **keep**
  - set 1: BlueWave Logistics possesses a maritime hazard handling permit, satisfying the credential requirement for hazardous cargo transit clearance.
- `u_ea5b` supersedes `e_df43` (reliability high)
- decoy policies: `p_adfd`, `p_4272`
- final state after updates (gold action -> state): `m_99a9` keep -> holds; `m_435d` keep -> holds; `m_e6eb` keep -> holds; `m_9bc2` keep -> holds; `m_cb1b` keep -> holds; `m_d367` keep -> holds; `m_c8c2` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_7f19~p_c5bb` policy_echoes_evidence: "a customs compliance; compliance score of; customs compliance score; maintains a customs" (judge under C7/C11)
- soft `e_de69~p_2123` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of; maintains an active" (judge under C7/C11)
- soft `e_d065~p_b757` policy_echoes_evidence: "a safety supervisor; safety supervisor headcount; supervisor headcount of" (judge under C7/C11)
- soft `e_4c18~p_cff7` policy_echoes_evidence: "a warehouse temperature; control rating of; maintains a warehouse; temperature control rating; warehouse temperature control" (judge under C7/C11)
- soft `e_b312~p_bf8b` policy_echoes_evidence: "active heavy vehicle; an active heavy; heavy vehicle fleet; operates an active; vehicle fleet of" (judge under C7/C11)
- soft `e_54d4~p_3041` policy_echoes_evidence: "a maritime hazard; hazard handling permit; maritime hazard handling; possesses a maritime" (judge under C7/C11)
- soft `e_86fa~p_6054` policy_echoes_evidence: "insurance coverage of; liability insurance coverage; transit liability insurance" (judge under C7/C11)
- soft `e_df43~p_2123` policy_echoes_evidence: "a monthly shipment; monthly shipment volume; shipment volume of" (judge under C7/C11)
- soft `groups 1/4` cross_group_entity: "Logistics" (judge under C6)

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

## s_807b8dbf81  (F2-006, product eligibility)

*World:* Evaluating product eligibility and certification status across several market categories based on compliance and performance metrics.

### A. System view (judge C7 from this alone)
- `e_94ea` [2026-01-08, EU compliance database] Compliance records verify that Solaris Power Station possesses a CE mark.
- `e_3f67` [2026-01-11, Stellar Tech official registry] Stellar Tech confirmed that Solaris Power Station holds an Energy Star certification.
- `e_a3a3` [2026-01-14, Product technical datasheet] Technical specifications confirm that Lumina Panel has an operational lifespan of 50000 hours.
- `e_246e` [2026-01-17, Annual consumer survey report] Market research indicates that Solaris Power Station scored a customer satisfaction index of 90 points.
- `e_82d9` [2026-01-20, Certified lab test report] Laboratory testing recorded that Solaris Power Station achieved an efficiency rating of 95 percent.
- `e_6f9b` [2026-01-23, FAA public registry] Federal records show that Glide Drone holds an FAA flight authorization.
- `e_7024` [2026-01-26, Internal QA assay report] Quality assurance reported that BioShield Sanitizer has an active alcohol concentration of 75 percent.
- `e_4162` [2026-01-29, Manufacturer warranty agreement] Product documentation states that Solaris Power Station includes a warranty period of 5 years.
- memories:
  - `m_cacb` Glide Drone is approved for commercial operation.
  - `m_1a3f` Solaris Power Station is selected for the premium catalog.
  - `m_c1e1` Solaris Power Station is granted green status.
  - `m_45fd` Lumina Panel qualifies for long-life certification.
  - `m_b8b5` BioShield Sanitizer meets hospital standards.
- update `u_8292` [2026-02-01, Regulatory audit report] An audit revealed that Solaris Power Station never received an Energy Star certification.
- update `u_096c` [2026-02-04, Lab re-calibration notice] A re-calibration showed that Solaris Power Station's efficiency rating was invalid and retracted.
- policies:
  - `p_caf7` A disinfectant achieves clinical approval when its primary agent content is at least 70 percent.
  - `p_e493` An item receives eco-friendly designation if it holds an Energy Star certification, demonstrates an energy conversion ratio of at least 90 percent, possesses a CE mark, or achieves a consumer approval score of 85 points or higher.
  - `p_a610` A light fixture earns an extended durability rating provided its expected service duration is at least 40000 hours.
  - `p_0c78` An offering is placed in the luxury inventory if it has achieved eco-friendly designation and provides a guarantee duration of 3 years or more.
  - `p_b277` A vehicle is assigned fleet eligibility if its annual maintenance cost does not exceed 1000 dollars.
  - `p_9587` An unmanned aircraft is cleared for business activity if it maintains an FAA flight authorization.
  - `p_5c49` A food product achieves organic clearance if its natural ingredient proportion is at least 95 percent and it maintains zero artificial preservatives.

### B. Intended structure
- `m_c1e1` (B1) [policy `p_e493`] <= (`e_3f67`) **OR** (`e_82d9`) **OR** (`e_94ea`) **OR** (`e_246e`); gold after update: **keep**
  - set 1: Holding an Energy Star certification satisfies the requirement for eco-friendly designation.
  - set 2: An efficiency rating of 95 percent exceeds the 90 percent threshold for eco-friendly designation.
  - set 3: Possessing a CE mark satisfies the requirement for eco-friendly designation.
  - set 4: A customer satisfaction index of 90 points exceeds the 85 points threshold for eco-friendly designation.
- `m_1a3f` (D1) [policy `p_0c78`] <= (`m_c1e1` AND `e_4162`); gold after update: **keep**
  - set 1: Achieving green status combined with a warranty period of 5 years satisfies the requirements of eco-friendly designation and a guarantee duration of at least 3 years.
- `m_b8b5` (B2) [policy `p_caf7`] <= (`e_7024`); gold after update: **keep**
  - set 1: An active alcohol concentration of 75 percent exceeds the 70 percent threshold for clinical approval.
- `m_cacb` (B3) [policy `p_9587`] <= (`e_6f9b`); gold after update: **keep**
  - set 1: Holding an FAA flight authorization satisfies the condition for business activity clearance.
- `m_45fd` (B4) [policy `p_a610`] <= (`e_a3a3`); gold after update: **keep**
  - set 1: An operational lifespan of 50000 hours exceeds the 40000 hours threshold for an extended durability rating.
- `u_8292` retracts `e_3f67` (reliability high)
- `u_096c` retracts `e_82d9` (reliability high)
- decoy policies: `p_5c49`, `p_b277`
- final state after updates (gold action -> state): `m_c1e1` keep -> holds; `m_b8b5` keep -> holds; `m_cacb` keep -> holds; `m_45fd` keep -> holds; `m_1a3f` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_246e->m_c1e1` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_3f67->m_c1e1` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_82d9->m_c1e1` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_94ea->m_c1e1` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_4162->m_1a3f` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_c1e1->m_1a3f` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_7024->m_b8b5` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_6f9b->m_cacb` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_a3a3->m_45fd` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

## s_0415d9554b  (F2-007, travel logistics)

*World:* Travel logistics evaluation for regional passenger charter operators, shuttle services, and cruise lines.

### A. System view (judge C7 from this alone)
- `e_42f8` [2026-01-08, Maritime Authority Database] Solstice Cruises maintains a certified maritime safety record.
- `e_b1d8` [2026-01-11, Official Fleet Registry] Apex Charters maintains an operational fleet count of 15 motorcoaches.
- `e_c062` [2026-01-14, Department of Transportation Portal] Apex Charters possesses Gold Safety Transport Accreditation.
- `e_e594` [2026-01-17, Operations Control Center Log] Horizon Express recorded an average quarterly punctuality rate of 96 percent.
- `e_a800` [2026-01-20, Underwriter Certification Statement] Apex Charters carries indemnification protection of 10000000 USD.
- `e_7b91` [2026-01-23, Client Audit Database] Apex Charters recorded a client satisfaction score of 4.8 points.
- memories:
  - `m_f9b0` Horizon Express attains preferred shuttle provider standing.
  - `m_81f8` Solstice Cruises qualifies for international vessel chartering.
  - `m_0dba` Apex Charters holds approved transit operator status.
  - `m_f69f` Apex Charters is selected for primary corporate travel contracts.
- update `u_17bd` [2026-01-26, Annual Compliance Audit Report] A transport audit confirmed that Apex Charters does not maintain an operational fleet count of 15 motorcoaches.
- policies:
  - `p_4819` A shuttle service achieves preferred vendor standing when its quarterly arrival timeliness equals or exceeds 90 percent.
  - `p_b598` An airport ground handler earns premium terminal access when holding an active baggage handling certification and maintaining a quarterly baggage loss rate below 0.1 percent.
  - `p_0e69` A maritime operator receives approval for international charter operations upon maintaining a certified maritime safety record.
  - `p_a8e0` Selection for key enterprise travel agreements requires a transit authorized carrier that maintains minimum indemnification protection of 5000000 USD.
  - `p_8243` A carrier receives transit authorization whenever fleet volume reaches at least 10 motorcoaches, Gold Safety Transport Accreditation is maintained, or client satisfaction reaches a minimum rating of 4.5 points.
  - `p_3641` A freight transport company receives priority routing privileges when maintaining an average driver experience level of at least 8 years.

### B. Intended structure
- `m_0dba` (B1) [policy `p_8243`] <= (`e_b1d8`) **OR** (`e_c062`) **OR** (`e_7b91`); gold after update: **keep**
  - set 1: Apex Charters maintains an operational fleet count of 15 motorcoaches, satisfying the threshold of at least 10 motorcoaches.
  - set 2: Apex Charters possesses Gold Safety Transport Accreditation, satisfying the accreditation requirement.
  - set 3: Apex Charters recorded a client satisfaction score of 4.8 points, meeting the threshold of at least 4.5 points.
- `m_f69f` (D1) [policy `p_a8e0`] <= (`m_0dba` AND `e_a800`); gold after update: **keep**
  - set 1: Apex Charters holds approved transit operator status and carries indemnification protection of 10000000 USD, exceeding the 5000000 USD threshold.
- `m_f9b0` (B2) [policy `p_4819`] <= (`e_e594`); gold after update: **keep**
  - set 1: Horizon Express achieved a quarterly punctuality rate of 96 percent, exceeding the 90 percent threshold.
- `m_81f8` (B3) [policy `p_0e69`] <= (`e_42f8`); gold after update: **keep**
  - set 1: Solstice Cruises maintains a certified maritime safety record, satisfying the safety credential requirement.
- `u_17bd` retracts `e_b1d8` (reliability high)
- decoy policies: `p_b598`, `p_3641`
- final state after updates (gold action -> state): `m_0dba` keep -> holds; `m_f9b0` keep -> holds; `m_81f8` keep -> holds; `m_f69f` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_42f8~p_0e69` policy_echoes_evidence: "a certified maritime; certified maritime safety; maritime safety record" (judge under C7/C11)
- soft `e_a800~p_a8e0` policy_echoes_evidence: "indemnification protection of" (judge under C7/C11)

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

## s_ca2f78b26a  (F2-008, product eligibility)

*World:* Evaluation of hardware equipment and generator components for catalog listing and performance tier assignment.

### A. System view (judge C7 from this alone)
- `e_fab3` [2026-01-08, Field Demonstration Log, Energy Systems Assessment] Apex X1 Inverter has a peak electrical output of 50 kilowatts during field trials.
- `e_66ff` [2026-01-11, Manufacturer Product Specification Sheet, Apex Dynamics] Apex X1 Inverter carries a warranty period of 5 years from the manufacturer.
- `e_25ee` [2026-01-14, Testing Log Summary, Solar Tech Labs] Apex X1 Inverter recorded a maximum operating temperature of 78 degrees Celsius during stress testing.
- `e_6332` [2026-01-17, Ingress Protection Verification, Durability Testing Services] Cygnus Battery Module holds an IP67 water resistance certification.
- `e_2936` [2026-01-20, Quality Registry Certificate, Standards Body] Apex X1 Inverter holds an ISO 9001 quality certificate from the standards bureau.
- `e_4897` [2026-01-23, Efficiency Inspection Certificate, Wind Energy Association] Boreas Wind Turbine registered an operational efficiency rating of 92 percent.
- `e_4ad9` [2026-01-26, Thermal Performance Report, Thermal Assurance Group] Apex X1 Inverter achieved a heat dissipation rating of 135 watts in laboratory testing.
- `e_f959` [2026-01-29, Acoustic Audit Report, Sound & Vibration Institute] DynaFlux Generator recorded noise emissions of 62 decibels under full load.
- memories:
  - `m_d1b7` DynaFlux Generator satisfies low-noise environment thresholds.
  - `m_1fe6` Apex X1 Inverter satisfies the thermal safety criteria.
  - `m_155c` Apex X1 Inverter will be listed in the preferred enterprise catalog.
  - `m_eba4` Apex X1 Inverter qualifies for industrial deployment designation.
  - `m_099b` Boreas Wind Turbine secures tier-one performance status.
  - `m_be68` Cygnus Battery Module meets outdoor durability standards.
  - `m_1e96` Apex X1 Inverter is compliant with general equipment safety specifications.
- update `u_e0fe` [2026-02-01, Secondary Thermal Audit, Thermal Assurance Group] A re-test showed that Apex X1 Inverter achieved a heat dissipation rating of 110 watts.
- update `u_3f9c` [2026-02-04, Standards Compliance Registry Update, International Standards Body] A compliance audit confirmed that Apex X1 Inverter does not hold an ISO 9001 quality certificate.
- policies:
  - `p_105a` Priority maintenance service is assigned to systems with a continuous run duration exceeding 1000 hours.
  - `p_9742` Outdoor durability qualification is granted to hardware holding an IP67 water resistance certification.
  - `p_51f3` Industrial deployment readiness requires a product with basic safety compliance that also delivers a peak electrical output of at least 40 kilowatts.
  - `p_a071` An equipment unit achieves basic safety compliance if it is cleared on thermal safety grounds.
  - `p_03cc` Catalog listing is approved for models with industrial deployment readiness that offer a warranty period of 3 years or longer.
  - `p_875d` Commercial rebate authorization requires a minimum energy efficiency index of 88 points.
  - `p_5c6c` A low-noise classification requires noise emissions of 65 decibels or lower.
  - `p_e794` Thermal safety clearance is granted when an item exhibits an operating temperature of 85 degrees Celsius or lower, a heat dissipation rating of 120 watts or greater, or holds an ISO 9001 quality certificate.
  - `p_e13d` Tier-one performance recognition requires an operational efficiency rating of 90 percent or higher.

### B. Intended structure
- `m_1fe6` (B1) [policy `p_e794`] <= (`e_25ee`) **OR** (`e_4ad9`) **OR** (`e_2936`); gold after update: **keep**
  - set 1: Apex X1 Inverter recorded an operating temperature of 78 degrees Celsius, which satisfies the maximum threshold of 85 degrees Celsius for thermal safety clearance.
  - set 2: Apex X1 Inverter achieved a heat dissipation rating of 135 watts, exceeding the 120 watts required for thermal safety clearance.
  - set 3: Apex X1 Inverter holds an ISO 9001 quality certificate, which independently qualifies it for thermal safety clearance.
- `m_1e96` (B2) [policy `p_a071`] <= (`m_1fe6`); gold after update: **keep**
  - set 1: Apex X1 Inverter holds thermal safety clearance, which grants it basic safety compliance.
- `m_eba4` (B3) [policy `p_51f3`] <= (`m_1e96` AND `e_fab3`); gold after update: **keep**
  - set 1: Apex X1 Inverter has basic safety compliance and produces a peak electrical output of 50 kilowatts, exceeding the 40 kilowatts threshold required for industrial deployment readiness.
- `m_155c` (D1) [policy `p_03cc`] <= (`m_eba4` AND `e_66ff`); gold after update: **keep**
  - set 1: Apex X1 Inverter meets industrial deployment readiness and offers a warranty period of 5 years, satisfying the 3 years minimum for catalog listing.
- `m_099b` (B4) [policy `p_e13d`] <= (`e_4897`); gold after update: **keep**
  - set 1: Boreas Wind Turbine achieved an operational efficiency rating of 92 percent, meeting the 90 percent requirement for tier-one performance recognition.
- `m_be68` (B5) [policy `p_9742`] <= (`e_6332`); gold after update: **keep**
  - set 1: Cygnus Battery Module holds an IP67 water resistance certification, which qualifies it for outdoor durability.
- `m_d1b7` (B6) [policy `p_5c6c`] <= (`e_f959`); gold after update: **keep**
  - set 1: DynaFlux Generator recorded noise emissions of 62 decibels, which is below the 65 decibels limit for low-noise classification.
- `u_e0fe` supersedes `e_4ad9` (reliability high)
- `u_3f9c` supersedes `e_2936` (reliability high)
- decoy policies: `p_875d`, `p_105a`
- final state after updates (gold action -> state): `m_1fe6` keep -> holds; `m_099b` keep -> holds; `m_be68` keep -> holds; `m_d1b7` keep -> holds; `m_1e96` keep -> holds; `m_eba4` keep -> holds; `m_155c` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_fab3~p_51f3` policy_echoes_evidence: "a peak electrical; electrical output of; peak electrical output" (judge under C7/C11)
- soft `e_66ff~p_03cc` policy_echoes_evidence: "a warranty period; warranty period of" (judge under C7/C11)
- soft `e_25ee~p_e794` policy_echoes_evidence: "operating temperature of" (judge under C7/C11)
- soft `e_6332~p_9742` policy_echoes_evidence: "water resistance certification" (judge under C7/C11)
- soft `e_4897~p_e13d` policy_echoes_evidence: "an operational efficiency; efficiency rating of; operational efficiency rating" (judge under C7/C11)
- soft `e_4ad9~p_e794` policy_echoes_evidence: "a heat dissipation; dissipation rating of; heat dissipation rating" (judge under C7/C11)
- soft `e_f959~p_5c6c` policy_echoes_evidence: "noise emissions of" (judge under C7/C11)

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

## s_94a4bc8c87  (F3-000, product eligibility)

*World:* An evaluation of device sales channels and retail program eligibility for consumer electronics products.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Marine Testing Institute certificate] Lumina Light Bar maintains a certified IP67 ingress rating.
- `e_2787` [2026-01-11, Annual factory quality control system log] AuraSense Pro recorded an annual failure percentage of 1.5%.
- `e_124c` [2026-01-14, Standards Council registry database] AuraSense Pro maintains a valid ISO 13485 credential.
- `e_ac4d` [2026-01-17, Annual regional distribution report] AuraSense Pro reached an annual regional distribution volume of 12,000 units.
- `e_c8d5` [2026-01-20, National Testing Labs official audit report] AuraSense Pro achieved a laboratory rating of 94 points in quality testing.
- memories:
  - `m_4677` Lumina Light Bar is approved for aquatic trade distribution.
  - `m_aeef` AuraSense Pro satisfies catalog listing safety criteria.
  - `m_b7fc` AuraSense Pro is selected for prime showcase placement.
- update `u_84c2` [2026-01-23, Factory quality control system log] AuraSense Pro recorded a failure percentage of 2.8% over one year.
- policies:
  - `p_b875` A device gains top promotional feature positioning when it achieves listing safety clearance and records an annual regional distribution volume of at least 10,000 units.
  - `p_ba9f` An accessory gains aquatic trade approval provided it holds a certified IP67 ingress rating.
  - `p_4b46` A commercial appliance achieves energy efficiency endorsement when it demonstrates a thermal coefficient of at least 85% and maintains an operating voltage under 240 volts.
  - `p_0c4c` A food container obtains commercial packaging certification if it holds an active FDA compliance seal.
  - `p_81ec` An item achieves listing safety clearance either by securing a laboratory rating of at least 90 points together with an annual failure percentage of no more than 2.0%, or by maintaining valid ISO 13485 credentials.

### B. Intended structure
- `m_aeef` (B1) [policy `p_81ec`] <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: AuraSense Pro achieves listing safety clearance under its policy because its laboratory rating of 94 points meets the 90 point threshold and its 1.5% failure percentage is within the 2.0% limit over one year.
  - set 2: AuraSense Pro achieves listing safety clearance under its policy because it holds a valid ISO 13485 credential.
- `m_b7fc` (D1) [policy `p_b875`] <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: AuraSense Pro gains top promotional feature positioning under its policy because it achieves listing safety clearance and its regional distribution volume of 12,000 units over one year meets the 10,000 unit requirement.
- `m_4677` (B2) [policy `p_ba9f`] <= (`e_4667`); gold after update: **keep**
  - set 1: Lumina Light Bar gains aquatic trade approval under its policy because it holds a certified IP67 ingress rating.
- `u_84c2` supersedes `e_2787` (reliability high)
- decoy policies: `p_4b46`, `p_0c4c`
- final state after updates (gold action -> state): `m_aeef` keep -> holds; `m_4677` keep -> holds; `m_b7fc` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2787~p_81ec` policy_echoes_evidence: "an annual failure; annual failure percentage; failure percentage of" (judge under C7/C11)
- soft `e_ac4d~p_b875` policy_echoes_evidence: "an annual regional; annual regional distribution; distribution volume of; regional distribution volume" (judge under C7/C11)
- soft `e_c8d5~p_81ec` policy_echoes_evidence: "a laboratory rating; laboratory rating of" (judge under C7/C11)
- soft `u_84c2` update_window_unclear: "none vs year" (judge under C4/C10)

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

## s_1be1205fa3  (F3-003, travel logistics)

*World:* A travel logistics management system evaluates transport providers and partners for routing privileges, priority dispatch, and security classifications based on performance metrics and certifications.

### A. System view (judge C7 from this alone)
- `e_454e` [2026-01-08, Baggage handling audit] Apex Global Travel reported an annual luggage loss rate of 0.2 percent.
- `e_d8a0` [2026-01-11, Fleet sustainability audit] Delta Way Transit achieved an annual fleet electrification rate of 60 percent.
- `e_42e9` [2026-01-14, Transport statistics office] Blue Sky Express recorded an annual passenger volume of 800000 travelers.
- `e_dfd6` [2026-01-17, Flight tracking database] Apex Global Travel recorded an annual punctuality score of 95 percent.
- `e_1177` [2026-01-20, Transport Licensing Board] Apex Global Travel holds Premier Carrier Certification.
- `e_756a` [2026-01-23, Fleet operations log] Apex Global Travel manages 12 annual operational bases.
- `e_96ab` [2026-01-26, Security standards registry] Crestview Logistics maintains ISO 28000 Certification.
- `e_7909` [2026-01-29, Financial escrow registry] Apex Global Travel deposited a security bond of 200000 USD.
- `e_d43e` [2026-02-01, Civil Aviation Authority filing] Apex Global Travel logged 500 annual charter flights.
- memories:
  - `m_321d` Apex Global Travel is assigned top-priority dispatch slots.
  - `m_b915` Delta Way Transit gains green fleet designation.
  - `m_5908` Blue Sky Express secures major hub priority.
  - `m_8bfa` Apex Global Travel attains elite operator status.
  - `m_f384` Apex Global Travel holds preferred routing access.
  - `m_aa0f` Crestview Logistics meets secure supply chain criteria.
- update `u_2905` [2026-02-04, Central aviation regulatory record] A revised audit revealed Apex Global Travel maintains no operational bases.
- policies:
  - `p_7123` A freight forwarder achieves rapid customs clearance if its annual customs declaration volume exceeds 10000 filings.
  - `p_936e` A enterprise gets top-priority dispatch allocations provided it maintains preferred route access along with a security bond of no less than 150000 USD.
  - `p_7c0f` A carrier fulfills secure supply network standards if it possesses ISO 28000 Certification.
  - `p_6557` A provider obtains major terminal priority when its annual passenger volume reaches 500000 travelers or more.
  - `p_743a` An organization earns elite operator recognition either by logging 400 or more annual charter flights together with managing at least 10 annual operational bases, keeping an annual luggage loss rate of 0.5 percent or less, and maintaining an annual punctuality score of 90 percent or higher, or by holding Premier Carrier Certification.
  - `p_7a3b` An operator acquires green fleet authorization when achieving an annual fleet electrification rate of at least 50 percent.
  - `p_67f6` A maritime contractor obtains deepwater berth rights when managing 15 or more commercial vessels.
  - `p_0f9a` An agency receives preferred routing privileges provided the entity reaches elite operator standing.

### B. Intended structure
- `m_8bfa` (B1) [policy `p_743a`] <= (`e_d43e` AND `e_756a` AND `e_454e` AND `e_dfd6`) **OR** (`e_1177`); gold after update: **keep**
  - set 1: Apex Global Travel meets the multi-part requirement with 500 annual charter flights, 12 annual operational bases, a 0.2 percent annual luggage loss rate, and a 95 percent annual punctuality score.
  - set 2: Apex Global Travel holds Premier Carrier Certification, which independently satisfies the policy criteria.
- `m_f384` (B2) [policy `p_0f9a`] <= (`m_8bfa`); gold after update: **keep**
  - set 1: Apex Global Travel attains elite operator status, satisfying the condition for preferred routing access.
- `m_321d` (D1) [policy `p_936e`] <= (`m_f384` AND `e_7909`); gold after update: **keep**
  - set 1: Apex Global Travel holds preferred routing access and maintains a security bond of 200000 USD, meeting the criteria for top-priority dispatch slots.
- `m_5908` (B3) [policy `p_6557`] <= (`e_42e9`); gold after update: **keep**
  - set 1: Blue Sky Express achieves an annual passenger volume of 800000 travelers, exceeding the threshold of 500000 travelers required for major hub priority.
- `m_aa0f` (B4) [policy `p_7c0f`] <= (`e_96ab`); gold after update: **keep**
  - set 1: Crestview Logistics maintains International ISO 28000 Certification, fulfilling the secure supply chain criteria.
- `m_b915` (B5) [policy `p_7a3b`] <= (`e_d8a0`); gold after update: **keep**
  - set 1: Delta Way Transit achieves an annual fleet electrification rate of 60 percent, satisfying the threshold for green fleet designation.
- `u_2905` retracts `e_756a` (reliability high)
- decoy policies: `p_7123`, `p_67f6`
- final state after updates (gold action -> state): `m_8bfa` keep -> holds; `m_5908` keep -> holds; `m_aa0f` keep -> holds; `m_b915` keep -> holds; `m_f384` keep -> holds; `m_321d` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_454e~p_743a` policy_echoes_evidence: "an annual luggage; annual luggage loss; loss rate of; luggage loss rate" (judge under C7/C11)
- soft `e_d8a0~p_7a3b` policy_echoes_evidence: "an annual fleet; annual fleet electrification; electrification rate of; fleet electrification rate" (judge under C7/C11)
- soft `e_42e9~p_6557` policy_echoes_evidence: "annual passenger volume" (judge under C7/C11)
- soft `e_dfd6~p_743a` policy_echoes_evidence: "an annual punctuality; annual punctuality score; punctuality score of" (judge under C7/C11)
- soft `e_756a~p_743a` policy_echoes_evidence: "annual operational bases" (judge under C7/C11)
- soft `e_7909~p_936e` policy_echoes_evidence: "a security bond; security bond of" (judge under C7/C11)
- soft `e_d43e~p_743a` policy_echoes_evidence: "annual charter flights" (judge under C7/C11)
- soft `groups 1/3` cross_group_entity: "Certification" (judge under C6)

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

## s_7e4db8da56  (F3-004, product eligibility)

*World:* Evaluations of medical products for regulatory compliance, catalog inclusion, and market access designations.

### A. System view (judge C7 from this alone)
- `e_0419` [2026-01-08, Clinical trials database registry record, dated January 8, 2026.] Apex Monitor completed a clinical trial with a clinical study size of 500 subjects this year.
- `e_8c48` [2026-01-11, Stress-testing engineering report, dated January 11, 2026.] Cardia Patch demonstrates an operational lifespan of 5 years.
- `e_0966` [2026-01-14, Internal quality assessment report, dated January 14, 2026.] Apex Monitor recorded a manufacturing defect rate of 0.02 defects per unit this year.
- `e_851c` [2026-01-17, European regulatory compliance database entry, dated January 17, 2026.] BioFlow Pump maintains CE mark certification.
- `e_151b` [2026-01-20, Independent testing laboratory evaluation sheet, dated January 20, 2026.] Apex Monitor operates on a battery run time of 24 hours between charges.
- `e_09d4` [2026-01-23, Testing facility performance log, dated January 23, 2026.] Lumina Sensor recorded a testing volume of 1200 units this year.
- `e_8ed3` [2026-01-26, Manufacturer commercial terms disclosure, dated January 26, 2026.] Apex Monitor comes with a warranty coverage period of 3 years.
- `e_4899` [2026-01-29, Official ISO certification registry document, dated January 29, 2026.] Apex Monitor holds ISO 13485 quality certification.
- memories:
  - `m_e7dc` Lumina Sensor meets fast-track market access criteria.
  - `m_330c` BioFlow Pump holds European distribution clearance.
  - `m_314c` Apex Monitor achieves regulatory compliance status.
  - `m_c6e8` Cardia Patch fulfills long-term durability criteria.
  - `m_fd6c` Apex Monitor satisfies technical safety standards.
  - `m_1592` Apex Monitor is approved for national healthcare listing.
- update `u_9072` [2026-02-01, Quality audit summary report from the main factory, dated February 1, 2026.] Apex Monitor recorded a manufacturing defect rate of 0.08 defects per unit this year.
- policies:
  - `p_4897` European market authorization requires a device to hold CE mark certification.
  - `p_4de6` Regulatory compliance recognition is granted to a device that receives technical safety verification.
  - `p_0f20` National healthcare catalog placement is authorized for a device holding regulatory compliance recognition together with a warranty coverage period of at least 2 years.
  - `p_f848` Global export licensing requires a minimum annual liability protection level of 2000000 dollars.
  - `p_0351` Commercial retail channel authorization is granted to a supplier maintaining an annual customer satisfaction rating of at least 85 percent.
  - `p_07c5` Technical safety verification is approved when a device maintains a battery run time of at least 18 hours, a clinical study size of at least 400 subjects per year, a manufacturing defect rate of 0.05 defects per unit per year or lower, and holds ISO 13485 quality certification.
  - `p_437f` Extended service durability designation applies to a product with an operational lifespan of at least 4 years.
  - `p_21c1` Expedited market access is granted to a device with a testing volume of at least 1000 units per year.

### B. Intended structure
- `m_fd6c` (B1) [policy `p_07c5`] <= (`e_151b` AND `e_0419` AND `e_0966` AND `e_4899`); gold after update: **recompute**
  - set 1: Apex Monitor meets all technical safety requirements by operating for 24 hours on battery, maintaining a clinical study size of 500 subjects, keeping manufacturing defects at 0.02 per unit, and holding ISO 13485 quality certification.
- `m_314c` (B2) [policy `p_4de6`] <= (`m_fd6c`); gold after update: **recompute**
  - set 1: Apex Monitor satisfies regulatory compliance recognition by obtaining technical safety verification.
- `m_1592` (D1) [policy `p_0f20`] <= (`m_314c` AND `e_8ed3`); gold after update: **recompute**
  - set 1: Apex Monitor achieves national healthcare catalog placement by securing regulatory compliance recognition and offering a 3-year warranty coverage period.
- `m_e7dc` (B3) [policy `p_21c1`] <= (`e_09d4`); gold after update: **keep**
  - set 1: Lumina Sensor qualifies for expedited market access by achieving a testing volume of 1200 units this year.
- `m_330c` (B4) [policy `p_4897`] <= (`e_851c`); gold after update: **keep**
  - set 1: BioFlow Pump receives European market authorization by maintaining CE mark certification.
- `m_c6e8` (B5) [policy `p_437f`] <= (`e_8c48`); gold after update: **keep**
  - set 1: Cardia Patch earns extended service durability designation with an operational lifespan of 5 years.
- `u_9072` supersedes `e_0966` (reliability high)
- decoy policies: `p_0351`, `p_f848`
- final state after updates (gold action -> state): `m_fd6c` recompute -> fails; `m_e7dc` keep -> holds; `m_330c` keep -> holds; `m_c6e8` keep -> holds; `m_314c` recompute -> fails; `m_1592` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_0419~p_07c5` policy_echoes_evidence: "a clinical study; clinical study size; study size of" (judge under C7/C11)
- soft `e_8c48~p_437f` policy_echoes_evidence: "an operational lifespan; operational lifespan of" (judge under C7/C11)
- soft `e_0966~p_07c5` policy_echoes_evidence: "a manufacturing defect; defect rate of; defects per unit; manufacturing defect rate" (judge under C7/C11)
- soft `e_151b~p_07c5` policy_echoes_evidence: "a battery run; battery run time; run time of" (judge under C7/C11)
- soft `e_09d4~p_21c1` policy_echoes_evidence: "a testing volume; testing volume of" (judge under C7/C11)
- soft `e_8ed3~p_0f20` policy_echoes_evidence: "a warranty coverage; coverage period of; warranty coverage period" (judge under C7/C11)

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

## s_f43204cac0  (F3-005, travel logistics)

*World:* Evaluating corporate charter flight and ground transit provider qualifications for corporate logistics planning.

### A. System view (judge C7 from this alone)
- `e_323c` [2026-01-08, State Transport Board fleet registry, published last month.] BlueWave Tours currently operates a motorcoach fleet size of 20 buses.
- `e_2bab` [2026-01-11, Aviation Safety Network database extract, dated last week.] AeroJet Logistics holds a valid ARGUS Platinum certification.
- `e_d0df` [2026-01-14, Underwriter certificate of insurance, filed last week.] AeroJet Logistics holds guaranteed liability coverage of $50,000,000.
- `e_563e` [2026-01-17, Department of Transportation annual performance summary, issued last week.] AeroJet Logistics recorded an annual flight delay rate of 2.5 percent this year.
- `e_b7ed` [2026-01-20, Civil Aviation Authority register entry, checked last month.] AeroJet Logistics currently maintains an active fleet size of 15 aircraft.
- memories:
  - `m_f57c` AeroJet Logistics holds premier status.
  - `m_4b41` BlueWave Tours holds transit clearance.
  - `m_92bc` AeroJet Logistics holds executive clearance.
  - `m_116f` AeroJet Logistics holds lead status.
- update `u_f747` [2026-01-23, Official fleet audit report, published recently.] AeroJet Logistics now maintains an active fleet size of 8 aircraft.
- policies:
  - `p_031b` An air provider receives lead status if it possesses executive clearance and maintains guaranteed liability coverage of at least $25,000,000.
  - `p_0257` A travel vendor receives transit clearance when operating a motorcoach fleet size of 15 buses or greater.
  - `p_309e` An air supplier secures executive clearance by maintaining premier status.
  - `p_af30` Regional cargo priority is assigned to freight companies that record a yearly lost shipment percentage below 1.0 percent.
  - `p_b51c` A carrier achieves premier status if it maintains an active fleet size of at least 10 aircraft, holds ARGUS Platinum certification, and keeps an annual flight delay rate of 5.0 percent or lower.
  - `p_50c5` Maritime passenger endorsement is granted to any vessel operator maintaining a fleet of at least 5 cruise ships and holding Solas Safety Certification.

### B. Intended structure
- `m_f57c` (B1) [policy `p_b51c`] <= (`e_b7ed` AND `e_2bab` AND `e_563e`); gold after update: **recompute**
  - set 1: AeroJet Logistics has an active fleet size of 15 aircraft (meeting the 10 aircraft threshold), holds ARGUS Platinum certification, and records an annual flight delay rate of 2.5 percent (below the 5.0 percent maximum), satisfying the premier status rule.
- `m_92bc` (B2) [policy `p_309e`] <= (`m_f57c`); gold after update: **recompute**
  - set 1: AeroJet Logistics holds premier status, satisfying the condition for executive clearance.
- `m_116f` (D1) [policy `p_031b`] <= (`m_92bc` AND `e_d0df`); gold after update: **recompute**
  - set 1: AeroJet Logistics holds executive clearance and maintains guaranteed liability coverage of 50 million dollars (exceeding the 25 million dollars requirement), satisfying the lead status rule.
- `m_4b41` (B3) [policy `p_0257`] <= (`e_323c`); gold after update: **keep**
  - set 1: BlueWave Tours operates a motorcoach fleet size of 20 buses, exceeding the 15 buses threshold for transit clearance.
- `u_f747` supersedes `e_b7ed` (reliability high)
- decoy policies: `p_50c5`, `p_af30`
- final state after updates (gold action -> state): `m_f57c` recompute -> fails; `m_4b41` keep -> holds; `m_92bc` recompute -> fails; `m_116f` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_323c~p_0257` policy_echoes_evidence: "a motorcoach fleet; fleet size of; motorcoach fleet size" (judge under C7/C11)
- soft `e_323c~p_b51c` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_d0df~p_031b` policy_echoes_evidence: "guaranteed liability coverage; liability coverage of" (judge under C7/C11)
- soft `e_563e~p_b51c` policy_echoes_evidence: "an annual flight; annual flight delay; delay rate of; flight delay rate" (judge under C7/C11)
- soft `e_b7ed~p_0257` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_b7ed~p_b51c` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of; maintains an active" (judge under C7/C11)

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

## s_064a1a325a  (F3-006, product eligibility)

*World:* An evaluation assistant assesses commercial energy and cooling systems for government equipment procurement and vendor registries.

### A. System view (judge C7 from this alone)
- `e_fbb4` [2026-01-08, European compliance registry filing] AeroGrid Station holds a valid CE mark credential.
- `e_02f2` [2026-01-11, Official technical specification sheet] AeroGrid Station maintains an operational efficiency rating of 92%.
- `e_882c` [2026-01-14, Signed corporate financial audit statement] Boreas Chill System achieved gross revenue of $2500000 this year.
- `e_312f` [2026-01-17, Safety oversight board database] AeroGrid Station has recorded 0 critical safety failures over the last year.
- `e_3e7b` [2026-01-20, Lab certification report from January 2026] AeroGrid Station demonstrates a peak output of 150 kW in lab testing.
- memories:
  - `m_e36a` Boreas Chill System earns High-Volume Market Vendor designation.
  - `m_8983` AeroGrid Station meets European Commercial Grid approval criteria.
  - `m_a13d` AeroGrid Station is placed on the Municipal Procurement Register.
  - `m_2bb5` AeroGrid Station achieves Tier-1 Power Unit qualification.
- update `u_479a` [2026-01-23, Audit lab test report] A re-calibrated bench test confirms AeroGrid Station reaches a peak output of only 80 kW.
- policies:
  - `p_8fc6` A product attains High-Volume Market Vendor designation when yearly turnover reaches $2000000 or greater.
  - `p_9feb` A candidate product secures Eco-Label Endorsement if its annual energy consumption remains under 500 kWh and it holds a zero-emission certificate.
  - `p_fefc` An item cleared as a Tier-1 Power Unit that also possesses a valid CE mark credential attains European Commercial Grid certification.
  - `p_6e8c` Equipment receives Tier-1 Power Unit status provided its peak output is at least 100 kW and its operational efficiency rating equals or exceeds 90%.
  - `p_2629` A product with European Commercial Grid certification qualifies for the Municipal Procurement Register provided it logs at most 0 critical safety failures over the last year.
  - `p_0b97` An enterprise obtains Priority Distributor Authorization provided its global workforce exceeds 500 personnel.

### B. Intended structure
- `m_2bb5` (B1) [policy `p_6e8c`] <= (`e_3e7b` AND `e_02f2`); gold after update: **recompute**
  - set 1: AeroGrid Station has a peak output of 150 kW and an operational efficiency rating of 92%, satisfying the requirements for Tier-1 Power Unit status.
- `m_8983` (B2) [policy `p_fefc`] <= (`m_2bb5` AND `e_fbb4`); gold after update: **recompute**
  - set 1: AeroGrid Station is a Tier-1 Power Unit and holds a CE mark credential, satisfying European Commercial Grid certification.
- `m_a13d` (D1) [policy `p_2629`] <= (`m_8983` AND `e_312f`); gold after update: **recompute**
  - set 1: AeroGrid Station holds European Commercial Grid certification and has recorded 0 critical safety failures over the last year, qualifying it for the Municipal Procurement Register.
- `m_e36a` (B3) [policy `p_8fc6`] <= (`e_882c`); gold after update: **keep**
  - set 1: Boreas Chill System recorded gross revenue of $2500000 this year, meeting the threshold for High-Volume Market Vendor designation.
- `u_479a` supersedes `e_3e7b` (reliability high)
- decoy policies: `p_9feb`, `p_0b97`
- final state after updates (gold action -> state): `m_2bb5` recompute -> fails; `m_e36a` keep -> holds; `m_8983` recompute -> fails; `m_a13d` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_02f2~p_6e8c` policy_echoes_evidence: "operational efficiency rating" (judge under C7/C11)
- soft `e_312f~p_2629` policy_echoes_evidence: "critical safety failures; safety failures over; the last year" (judge under C7/C11)

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

## s_d077ecc605  (F3-007, travel logistics)

*World:* A corporate travel management platform evaluates flight charter suppliers and ground shuttle partners for corporate transport contracts.

### A. System view (judge C7 from this alone)
- `e_3530` [2026-01-08, Certification directory of the International Standards Audit.] AeroSkies Charter holds an active ISO 9001 quality management certification.
- `e_b478` [2026-01-11, Annual performance report from the Flight Monitoring Bureau.] AeroSkies Charter achieved an on-time arrival rate of 92% this year.
- `e_3ec2` [2026-01-14, Insurance certificate filed with Commercial Aviation Risk Management.] AeroSkies Charter maintains passenger liability coverage of 50,000,000 USD.
- `e_f842` [2026-01-17, Official fleet register from the Civil Aviation Authority.] AeroSkies Charter operates a fleet size of 15 aircraft.
- `e_4df3` [2026-01-20, Safety audit summary from the National Transport Safety Board.] AeroSkies Charter logged a total of 0 safety violations this year.
- `e_2863` [2026-01-23, Customer survey report published by Regional Travel Analytics.] Horizon Express maintains a passenger satisfaction rating of 4.8 points.
- `e_ac94` [2026-01-26, Global Aviation Alliance partner database.] AeroSkies Charter holds an active Platinum Flight Operations Accreditation.
- memories:
  - `m_087b` Horizon Express holds Premier Shuttle Partner status.
  - `m_3cd1` AeroSkies Charter meets executive flight contracting criteria.
  - `m_8994` AeroSkies Charter is assigned to manage corporate transport services.
  - `m_08c4` AeroSkies Charter holds Approved Flight Supplier status.
- update `u_ab44` [2026-01-29, Updated fleet register from the Civil Aviation Authority.] AeroSkies Charter operates a fleet size of 8 aircraft.
- policies:
  - `p_32d6` An air transport carrier is cleared for executive charter contracts if it holds preferred provider designation and maintains minimum passenger liability coverage of 30,000,000 USD.
  - `p_3a65` A lodging venue qualifies for luxury listing if it maintains an accommodation rating of at least 4.5 stars and provides 24-hour desk coverage.
  - `p_56f9` A freight distributor receives priority customs clearance when maintaining a fleet compliance score above 95% and zero cargo loss incidents over 12 months.
  - `p_d94f` An air transport carrier is awarded preferred provider designation either by demonstrating a yearly punctuality percentage of at least 90%, operating an active aircraft count of no fewer than 10, holding valid ISO 9001 quality management certification, and recording under 2 yearly safety infractions, or by holding valid Platinum Flight Operations Accreditation.
  - `p_32a7` An air transport carrier is selected to handle corporate travel operations provided it is cleared for executive charter contracts.
  - `p_7f1a` A ground transit provider gains top-tier shuttle endorsement when its customer feedback score reaches at least 4.5 points.

### B. Intended structure
- `m_08c4` (B1) [policy `p_d94f`] <= (`e_b478` AND `e_f842` AND `e_3530` AND `e_4df3`) **OR** (`e_ac94`); gold after update: **keep**
  - set 1: AeroSkies Charter initially met set 1 with a 92% on-time arrival rate, 15 aircraft, ISO 9001 certification, and 0 safety violations.
  - set 2: AeroSkies Charter holds Platinum Flight Operations Accreditation, satisfying set 2 independently.
- `m_3cd1` (B2) [policy `p_32d6`] <= (`m_08c4` AND `e_3ec2`); gold after update: **keep**
  - set 1: AeroSkies Charter holds Approved Flight Supplier status and maintains 50 million USD in passenger liability coverage.
- `m_8994` (D1) [policy `p_32a7`] <= (`m_3cd1`); gold after update: **keep**
  - set 1: AeroSkies Charter meets executive flight contracting criteria.
- `m_087b` (B3) [policy `p_7f1a`] <= (`e_2863`); gold after update: **keep**
  - set 1: Horizon Express has a passenger satisfaction rating of 4.8 points, meeting the required threshold of 4.5 points.
- `u_ab44` supersedes `e_f842` (reliability high)
- decoy policies: `p_3a65`, `p_56f9`
- final state after updates (gold action -> state): `m_08c4` keep -> holds; `m_087b` keep -> holds; `m_3cd1` keep -> holds; `m_8994` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_3530~p_d94f` policy_echoes_evidence: "quality management certification" (judge under C7/C11)
- soft `e_3ec2~p_32d6` policy_echoes_evidence: "liability coverage of; passenger liability coverage" (judge under C7/C11)

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

## s_b9b4c5c11a  (F3-008, product eligibility)

*World:* Evaluating commercial product eligibility for enterprise vendor catalogs and government procurement registries.

### A. System view (judge C7 from this alone)
- `e_68ce` [2026-01-08, TechLab Benchmarks published test report] Lumina Tab 10 has a battery lifespan rating of 18 hours.
- `e_a38b` [2026-01-11, SkyTech Testing Facility flight records] AeroGlide 500 logged 120 hours of flight safety testing this year.
- `e_70a5` [2026-01-14, Energy Standards Institute official test log] SolarPulse 200 delivers an energy conversion efficiency of 98 percent.
- `e_e7d1` [2026-01-17, Federal Aviation Administration public register] AeroGlide 500 holds a FAA Commercial Airworthiness Certificate.
- `e_40dc` [2026-01-20, National Environmental Board official registry] EcoClean Pro holds a Green Seal Certification.
- `e_accf` [2026-01-23, SkyTech Compliance Office audit report] AeroGlide 500 holds an ISO 9001 quality certificate.
- memories:
  - `m_515d` AeroGlide 500 meets regional aviation fleet criteria.
  - `m_c1c6` Lumina Tab 10 meets long-life device benchmarks.
  - `m_dabd` AeroGlide 500 is clear for vendor catalog placement.
  - `m_9ab0` SolarPulse 200 meets high-efficiency equipment specifications.
  - `m_eff2` EcoClean Pro meets sustainable product requirements.
- update `u_97cb` [2026-01-26, SkyTech Compliance Office official notice] SkyTech Compliance Office announced that AeroGlide 500 does not hold an ISO 9001 quality certificate, as the application was formally withdrawn.
- policies:
  - `p_98b3` An uncrewed aircraft obtains regional flight clearance either by demonstrating a flight safety evaluation duration of at least 100 hours in a year together with holding an ISO 9001 quality certificate, or by securing a FAA Commercial Airworthiness Certificate.
  - `p_7171` A cleaning solution earns eco-label endorsement if it maintains a Green Seal Certification.
  - `p_ff3b` An aircraft model is authorized for government portal indexing if it has obtained regional flight clearance.
  - `p_3ea2` An electronic monitor qualifies for workplace ergonomics subsidy when its height adjustment range equals or exceeds 15 centimeters.
  - `p_7cdd` A commercial refrigeration unit gains fast-track procurement approval if its operating sound emission level remains below 40 decibels.
  - `p_dca5` A solar power inverter achieves premium grade qualification when its power conversion ratio is 95 percent or greater.
  - `p_8e44` A consumer tablet qualifies for extended power status provided its battery operation duration reaches at least 15 hours.

### B. Intended structure
- `m_515d` (B1) [policy `p_98b3`] <= (`e_a38b` AND `e_accf`) **OR** (`e_e7d1`); gold after update: **keep**
  - set 1: AeroGlide 500 meets regional flight clearance requirements by completing 120 hours of flight safety testing this year, exceeding the 100-hour threshold, and holding an ISO 9001 quality certificate.
  - set 2: AeroGlide 500 independently obtains regional flight clearance by holding a FAA Commercial Airworthiness Certificate.
- `m_dabd` (D1) [policy `p_ff3b`] <= (`m_515d`); gold after update: **keep**
  - set 1: AeroGlide 500 is authorized for government portal indexing because it has obtained regional flight clearance.
- `m_c1c6` (B2) [policy `p_8e44`] <= (`e_68ce`); gold after update: **keep**
  - set 1: Lumina Tab 10 qualifies for extended power status because its battery lifespan of 18 hours exceeds the 15-hour threshold.
- `m_eff2` (B3) [policy `p_7171`] <= (`e_40dc`); gold after update: **keep**
  - set 1: EcoClean Pro earns eco-label endorsement because it holds a Green Seal Certification.
- `m_9ab0` (B4) [policy `p_dca5`] <= (`e_70a5`); gold after update: **keep**
  - set 1: SolarPulse 200 achieves premium grade qualification because its energy conversion efficiency of 98 percent exceeds the 95 percent threshold.
- `u_97cb` retracts `e_accf` (reliability high)
- decoy policies: `p_7cdd`, `p_3ea2`
- final state after updates (gold action -> state): `m_515d` keep -> holds; `m_c1c6` keep -> holds; `m_eff2` keep -> holds; `m_9ab0` keep -> holds; `m_dabd` keep -> holds

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

## s_40741d0f7c  (F3-009, travel logistics)

*World:* Evaluating operational permissions, route clearances, and partnership statuses across several commercial air freight and logistics providers.

### A. System view (judge C7 from this alone)
- `e_b780` [2026-01-08, National Transport Authority sustainability compliance record] Beacon Transit holds a certified green transport rating.
- `e_9737` [2026-01-11, Federal Aviation Administration regulatory database record] Apex Air Freight holds an active Class 1 air carrier certificate.
- `e_43d6` [2026-01-14, International Civil Aviation Organization official registry] Apex Air Freight holds a Global VIP Operator Permit.
- `e_b043` [2026-01-17, Annual safety audit report from the Department of Transportation] Crestview Tours achieved an annual safety score of 92 points.
- `e_653e` [2026-01-20, Official fleet registration ledger dated January 20, 2026] Apex Air Freight operates a fleet of 15 active cargo airplanes.
- `e_a1eb` [2026-01-23, Signed corporate insurance binder document] Apex Air Freight maintains emergency response insurance coverage of 20 million USD.
- `e_f2fd` [2026-01-26, Monthly logistics performance audit certified by Port Authority] Delta Cargo maintained a monthly on-time delivery rate of 96 percent.
- memories:
  - `m_0796` Beacon Transit meets corporate sustainability standards.
  - `m_4993` Delta Cargo is eligible for expedited customs clearance.
  - `m_6701` Apex Air Freight holds high-risk corridor certification.
  - `m_c370` Apex Air Freight is approved for priority cargo charter operations.
  - `m_dfe2` Crestview Tours qualifies for preferred vendor status.
  - `m_af98` Dispatch a transatlantic transit permit for Apex Air Freight.
- update `u_eb04` [2026-01-29, Audited fleet inventory report dated January 29, 2026] Apex Air Freight operates a fleet of 8 active cargo airplanes.
- policies:
  - `p_7e6b` Charter clearance is granted to a transport provider that either possesses a Class 1 air carrier certificate along with a fleet size of at least 10 active cargo airplanes, or holds a Global VIP Operator Permit.
  - `p_4763` A maritime fleet operator gains express docking privileges provided its vessels maintain an average turn-around time of under 4 hours.
  - `p_6831` An oceanic crossing dispatch release is granted to any transport provider certified for hazardous routes.
  - `p_9e65` A railway contractor receives top tier recognition upon logging 500 fault-free journeys.
  - `p_1dfd` A logistics company secures fast-track border processing with a monthly on-time delivery rate of 90 percent or higher.
  - `p_1c43` An organization satisfies environmental responsibility guidelines when holding a certified green transport rating.
  - `p_2880` A transport provider cleared for charter operations gains clearance for high-risk corridors when maintaining emergency response insurance coverage of at least 15 million USD.
  - `p_d2f0` A service provider obtains priority partner standing if its annual safety score is at least 90 points.

### B. Intended structure
- `m_c370` (B1) [policy `p_7e6b`] <= (`e_9737` AND `e_653e`) **OR** (`e_43d6`); gold after update: **keep**
  - set 1: Apex Air Freight holds a Class 1 air carrier certificate and operates 15 active cargo airplanes, exceeding the 10 airplane threshold.
  - set 2: Apex Air Freight holds a Global VIP Operator Permit.
- `m_6701` (B2) [policy `p_2880`] <= (`m_c370` AND `e_a1eb`); gold after update: **keep**
  - set 1: Apex Air Freight is approved for priority cargo charter operations and maintains $20 million in emergency response insurance coverage, meeting the $15 million threshold.
- `m_af98` (D1) [policy `p_6831`] <= (`m_6701`); gold after update: **keep**
  - set 1: Apex Air Freight holds high-risk corridor certification.
- `m_0796` (B3) [policy `p_1c43`] <= (`e_b780`); gold after update: **keep**
  - set 1: Beacon Transit holds a certified green transport rating.
- `m_dfe2` (B4) [policy `p_d2f0`] <= (`e_b043`); gold after update: **keep**
  - set 1: Crestview Tours achieved an annual safety score of 92 points, meeting the 90 point minimum requirement.
- `m_4993` (B5) [policy `p_1dfd`] <= (`e_f2fd`); gold after update: **keep**
  - set 1: Delta Cargo maintained a monthly on-time delivery rate of 96 percent, exceeding the 90 percent minimum requirement.
- `u_eb04` supersedes `e_653e` (reliability high)
- decoy policies: `p_4763`, `p_9e65`
- final state after updates (gold action -> state): `m_c370` keep -> holds; `m_0796` keep -> holds; `m_dfe2` keep -> holds; `m_4993` keep -> holds; `m_6701` keep -> holds; `m_af98` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_b780~p_1c43` policy_echoes_evidence: "a certified green; certified green transport; green transport rating" (judge under C7/C11)
- soft `e_9737~p_7e6b` policy_echoes_evidence: "air carrier certificate" (judge under C7/C11)
- soft `e_b043~p_d2f0` policy_echoes_evidence: "annual safety score" (judge under C7/C11)
- soft `e_653e~p_7e6b` policy_echoes_evidence: "active cargo airplanes" (judge under C7/C11)
- soft `e_a1eb~p_2880` policy_echoes_evidence: "emergency response insurance; insurance coverage of; response insurance coverage" (judge under C7/C11)
- soft `e_f2fd~p_1dfd` policy_echoes_evidence: "a monthly on-time; delivery rate of; monthly on-time delivery; on-time delivery rate" (judge under C7/C11)

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

## s_9a0888f8b9  (F6-002, product eligibility)

*World:* An assessment of medical product eligibility and vendor listing standards across commercial medical device suppliers.

### A. System view (judge C7 from this alone)
- `e_7b3b` [2026-01-08, Manufacturer Product Specification sheet] VeloCart comes with a structural warranty of 5 years as recorded in the specification sheet.
- `e_9d85` [2026-01-11, Medical Device Registry entry] SurgiShield XL holds an active ISO 13485 credential according to the medical device registry.
- `e_6f4b` [2026-01-14, Annual Quality Control Audit report] SurgiShield XL recorded a defect rate of 0.02% over the last year according to the quality audit.
- `e_4080` [2026-01-17, Quarterly Client Feedback Report] OptiLube Ultra attained a customer satisfaction score of 88% over the last quarter in the client survey.
- `e_923c` [2026-01-20, FDA Clearance Database record] SurgiShield XL obtained FDA Class II clearance as documented in the clearance register.
- memories:
  - `m_cd7d` SurgiShield XL is qualified for medical hospital distribution.
  - `m_1652` SurgiShield XL fulfills primary requirements for safety compliance.
  - `m_81aa` SurgiShield XL shall be included in the vendor catalog.
  - `m_12fa` OptiLube Ultra satisfies preferred vendor criteria.
  - `m_5010` VeloCart fulfills extended durability benchmarks.
- update `u_436c` [2026-01-23, Industry forum message board post] An unverified forum post claims SurgiShield XL never held an active ISO 13485 credential.
- policies:
  - `p_b9af` A product meets primary safety compliance requirements if it holds active ISO 13485 certification or maintains FDA Class II clearance.
  - `p_4422` A product meets preferred vendor standards if its quarterly customer satisfaction score reaches 80% or higher.
  - `p_e93c` A device gains priority export approval if it maintains international freight insurance covering at least $100,000 per shipment.
  - `p_632f` A product meets extended durability standards if it provides a structural warranty of at least 5 years.
  - `p_46dc` An item secures qualification for clinical hospital placement when an applicant cleared on primary safety compliance requirements also maintains a yearly defect rate of 0.05% or lower.
  - `p_7995` A product is listed in the master vendor catalog provided that it qualifies for hospital distribution.
  - `p_2b2f` An equipment model receives green manufacturing status provided that its annual energy consumption remains below 50 kWh.

### B. Intended structure
- `m_1652` (B1) [policy `p_b9af`] <= (`e_9d85`) **OR** (`e_923c`); gold after update: **keep**
  - set 1: Holding ISO 13485 certification fulfills the primary safety compliance standards requirement.
  - set 2: Holding FDA Class II clearance fulfills the primary safety compliance standards requirement.
- `m_cd7d` (B2) [policy `p_46dc`] <= (`m_1652` AND `e_6f4b`); gold after update: **keep**
  - set 1: Meeting primary safety compliance standards together with an annual defect rate of 0.02%, which is below the 0.05% maximum threshold, qualifies SurgiShield XL for hospital distribution.
- `m_81aa` (D1) [policy `p_7995`] <= (`m_cd7d`); gold after update: **keep**
  - set 1: Being qualified for hospital distribution satisfies the rule for inclusion in the master vendor catalog.
- `m_12fa` (B3) [policy `p_4422`] <= (`e_4080`); gold after update: **keep**
  - set 1: A quarterly customer satisfaction score of 88% exceeds the required 80% threshold to meet preferred vendor standards.
- `m_5010` (B4) [policy `p_632f`] <= (`e_7b3b`); gold after update: **keep**
  - set 1: A 5-year structural warranty satisfies the requirement for extended durability standards.
- `u_436c` retracts `e_9d85` (reliability low)
- decoy policies: `p_e93c`, `p_2b2f`
- final state after updates (gold action -> state): `m_1652` keep -> holds; `m_12fa` keep -> holds; `m_5010` keep -> holds; `m_cd7d` keep -> holds; `m_81aa` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_7b3b~p_632f` policy_echoes_evidence: "a structural warranty; structural warranty of" (judge under C7/C11)
- soft `e_6f4b~p_46dc` policy_echoes_evidence: "defect rate of" (judge under C7/C11)
- soft `e_4080~p_4422` policy_echoes_evidence: "customer satisfaction score" (judge under C7/C11)
- soft `u_436c` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_20ddc4f6ae  (F6-003, travel logistics)

*World:* Regional travel logistics assessments evaluate transport service providers across road, maritime, rail, and air sectors.

### A. System view (judge C7 from this alone)
- `e_80df` [2026-01-08, Official fleet registry filing from the Department of Transportation.] Apex Transit maintains an active fleet size of 45 vehicles across its operational network.
- `e_cadb` [2026-01-11, Civil Aviation Authority annual database entry.] Skyward Charter achieved annual flight completions of 300 flights.
- `e_e6e4` [2026-01-14, Port authority quarterly log.] BlueWave Express recorded quarterly freight tonnage of 12000 metric tons.
- `e_c34b` [2026-01-17, Registry record from the International Safety Board.] Apex Transit holds an ISO 39001 road traffic safety accreditation.
- `e_ee33` [2026-01-20, National Railway Administration portal entry.] Crestline Rail maintains a Class A safety license.
- memories:
  - `m_b9ef` Apex Transit holds preferred regional carrier status.
  - `m_258e` Skyward Charter meets the primary air carrier standard.
  - `m_2cfb` BlueWave Express receives tier-one port priority clearance.
  - `m_4787` Apex Transit is assigned to manage executive shuttle operations for the summit.
  - `m_64fd` Crestline Rail is eligible for high-speed corridor routing.
- update `u_4eb9` [2026-01-23, Anonymous online transit forum comment.] An unverified forum post claims Apex Transit does not maintain an active fleet size of 45 vehicles.
- policies:
  - `p_fcc6` A rail operator gains express line access privileges provided the carrier maintains a Class A safety license.
  - `p_cfb3` A logistics provider is chosen for executive transfer management if the transport vendor achieves regional partnership at the preferred carrier level.
  - `p_f7e2` A freight agency gains fast-track customs authorization when maintaining a minimum warehouse capacity of 50000 square meters.
  - `p_1dfb` An aviation service firm satisfies core flight supplier criteria if annual flight completions total at least 250 flights.
  - `p_44d3` A maritime carrier secures premier harbor dispatch status when quarterly freight tonnage reaches at least 10000 metric tons.
  - `p_8b9f` A transport vendor achieves regional partnership at the preferred carrier level by maintaining an active fleet size of at least 40 vehicles or securing ISO 39001 road traffic safety accreditation.
  - `p_5b73` A rental vehicle business achieves prime terminal placement upon maintaining an annual traveler satisfaction score of 95 percent.

### B. Intended structure
- `m_b9ef` (B1) [policy `p_8b9f`] <= (`e_80df`) **OR** (`e_c34b`); gold after update: **keep**
  - set 1: Apex Transit maintains an active fleet size of 45 vehicles, satisfying the requirement of at least 40 vehicles under the policy.
  - set 2: Apex Transit holds an ISO 39001 road traffic safety accreditation, satisfying the safety credential branch of the policy.
- `m_4787` (D1) [policy `p_cfb3`] <= (`m_b9ef`); gold after update: **keep**
  - set 1: Apex Transit holds preferred regional carrier status, satisfying the supplier requirement under the policy for shuttle operations management.
- `m_2cfb` (B2) [policy `p_44d3`] <= (`e_e6e4`); gold after update: **keep**
  - set 1: BlueWave Express logged quarterly freight tonnage of 12000 metric tons, exceeding the 10000 metric tons threshold required by the policy.
- `m_64fd` (B3) [policy `p_fcc6`] <= (`e_ee33`); gold after update: **keep**
  - set 1: Crestline Rail holds a Class A safety license, fulfilling the credential requirement under the policy.
- `m_258e` (B4) [policy `p_1dfb`] <= (`e_cadb`); gold after update: **keep**
  - set 1: Skyward Charter completed 300 annual flights, exceeding the 250 flights threshold mandated by the policy.
- `u_4eb9` retracts `e_80df` (reliability low)
- decoy policies: `p_f7e2`, `p_5b73`
- final state after updates (gold action -> state): `m_b9ef` keep -> holds; `m_2cfb` keep -> holds; `m_64fd` keep -> holds; `m_258e` keep -> holds; `m_4787` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_80df~p_8b9f` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of" (judge under C7/C11)
- soft `e_cadb~p_1dfb` policy_echoes_evidence: "annual flight completions" (judge under C7/C11)
- soft `e_e6e4~p_44d3` policy_echoes_evidence: "quarterly freight tonnage" (judge under C7/C11)
- soft `e_c34b~p_8b9f` policy_echoes_evidence: "road traffic safety; traffic safety accreditation" (judge under C7/C11)
- soft `u_4eb9` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_93d9704dc4  (F6-004, product eligibility)

*World:* Verification of equipment certifications and specifications for product catalog inclusion and incentive eligibility.

### A. System view (judge C7 from this alone)
- `e_c9df` [2026-01-08, Department of Transportation Registration Log] Titan Hauler has a maximum payload capacity of 12 metric tons.
- `e_4157` [2026-01-11, Underwriters Laboratories Registry] AeroPulse X1 holds a valid UL 60601 safety clearance.
- `e_0fca` [2026-01-14, Solar Testing Authority Datasheet] Solaria Prime has a peak power output of 450 W.
- `e_55cd` [2026-01-17, National Health Regulatory Database] AeroPulse X1 holds an active ISO 13485 quality certification.
- `e_d2db` [2026-01-20, European Conformity Portal] AeroPulse X1 maintains a valid CE Mark certification.
- memories:
  - `m_08da` Solaria Prime is eligible for clean energy grants.
  - `m_3d7c` AeroPulse X1 is qualified for institutional health deployment.
  - `m_b9a9` AeroPulse X1 satisfies regional clinical equipment standards.
  - `m_48cf` Titan Hauler is approved for heavy transport permits.
  - `m_895e` Include AeroPulse X1 in the regional hospital supply catalog.
- update `u_57b3` [2026-01-23, Medical Standards Board Inspection Report] An auditor's note indicates potential irregularities in the documentation for AeroPulse X1's active ISO 13485 quality certification.
- policies:
  - `p_0963` A vehicle receives commercial oversized haulage authorization when its maximum payload capacity equals or exceeds 10 metric tons.
  - `p_cf62` Regulatory compliance for medical hardware is granted if an item possesses an active ISO 13485 quality certification or maintains a valid CE Mark certification.
  - `p_31ab` A commercial fleet vehicle qualifies for urban low-emission access if its electric driving range exceeds 300 km.
  - `p_6c70` An industrial storage facility receives class-A hazardous material clearance provided its emergency containment volume is at least 50 cubic meters.
  - `p_475a` A solar module earns green technology subsidies when its peak power output is at least 400 W.
  - `p_c71e` An item meets health hardware criteria if it achieves regulatory compliance for medical hardware.
  - `p_60e3` A medical device is added to the public healthcare index provided it meets health hardware criteria and holds a valid UL 60601 safety clearance.

### B. Intended structure
- `m_b9a9` (B1) [policy `p_cf62`] <= (`e_55cd`) **OR** (`e_d2db`); gold after update: **keep**
  - set 1: AeroPulse X1 achieves regulatory compliance for medical hardware because it holds an active ISO 13485 quality certification.
  - set 2: AeroPulse X1 achieves regulatory compliance for medical hardware because it maintains a valid CE Mark certification.
- `m_3d7c` (B2) [policy `p_c71e`] <= (`m_b9a9`); gold after update: **keep**
  - set 1: AeroPulse X1 meets health hardware criteria because it achieves regulatory compliance for medical hardware.
- `m_895e` (D1) [policy `p_60e3`] <= (`m_3d7c` AND `e_4157`); gold after update: **keep**
  - set 1: AeroPulse X1 is added to the public healthcare index because it meets health hardware criteria and holds a valid UL 60601 safety clearance.
- `m_08da` (B3) [policy `p_475a`] <= (`e_0fca`); gold after update: **keep**
  - set 1: Solaria Prime earns green technology subsidies because its peak power output of 450 W meets the minimum requirement of 400 W.
- `m_48cf` (B4) [policy `p_0963`] <= (`e_c9df`); gold after update: **keep**
  - set 1: Titan Hauler receives commercial oversized haulage authorization because its maximum payload capacity of 12 metric tons meets the threshold of 10 metric tons.
- `u_57b3` hedges `e_55cd` (reliability high)
- decoy policies: `p_31ab`, `p_6c70`
- final state after updates (gold action -> state): `m_b9a9` keep -> holds; `m_08da` keep -> holds; `m_48cf` keep -> holds; `m_3d7c` keep -> holds; `m_895e` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_c9df~p_0963` policy_echoes_evidence: "maximum payload capacity" (judge under C7/C11)
- soft `e_4157~p_60e3` policy_echoes_evidence: "holds a valid" (judge under C7/C11)
- soft `e_0fca~p_475a` policy_echoes_evidence: "peak power output" (judge under C7/C11)
- soft `e_d2db~p_cf62` policy_echoes_evidence: "maintains a valid" (judge under C7/C11)

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

## s_43bbc7e02a  (F6-006, product eligibility)

*World:* An evaluation of commercial partners is being conducted to assign procurement preferences and safety compliance ratings.

### A. System view (judge C7 from this alone)
- `e_594f` [2026-01-08, Corporate quality audit filing] Apex Dynamics holds an official ISO 9001 certification.
- `e_46f7` [2026-01-11, Annual corporate compliance record] Vortex Industries recorded a safety compliance rating of 92%.
- `e_8e03` [2026-01-14, Official security audit certificate registry] Apex Dynamics holds an official ISO 27001 certification.
- memories:
  - `m_641a` Vortex Industries maintains top safety execution standards.
  - `m_136e` Apex Dynamics is designated a preferred supplier.
  - `m_2e3c` Apex Dynamics is selected for strategic purchasing.
- update `u_64fe` [2026-01-17, Unverified post on a public discussion board] An unverified forum post claims Apex Dynamics lost its ISO 9001 certification.
- policies:
  - `p_3ba7` A commercial vendor achieves preferred supplier status when maintaining either an ISO 9001 certification or an ISO 27001 certification.
  - `p_73ff` An enterprise holding preferred supplier status becomes eligible for strategic procurement.
  - `p_4622` A facility qualifies for green operational clearance provided its renewable energy ratio is at least 80 percent.
  - `p_da85` An organization attains high safety performance recognition when its safety compliance rating is 90% or higher.
  - `p_29dd` A vendor achieves premium tier vendor status if its annual contract value exceeds 1000000 dollars.

### B. Intended structure
- `m_136e` (B1) [policy `p_3ba7`] <= (`e_594f`) **OR** (`e_8e03`); gold after update: **keep**
  - set 1: Apex Dynamics holds an ISO 9001 certification, satisfying the condition to achieve preferred supplier status.
  - set 2: Apex Dynamics holds an ISO 27001 certification, satisfying the condition to achieve preferred supplier status.
- `m_2e3c` (D1) [policy `p_73ff`] <= (`m_136e`); gold after update: **keep**
  - set 1: Apex Dynamics is designated a preferred supplier, satisfying the requirement for strategic procurement eligibility.
- `m_641a` (B2) [policy `p_da85`] <= (`e_46f7`); gold after update: **keep**
  - set 1: Vortex Industries recorded a safety compliance rating of 92%, which meets the minimum threshold of 90% for high safety performance recognition.
- `u_64fe` retracts `e_594f` (reliability low)
- decoy policies: `p_29dd`, `p_4622`
- final state after updates (gold action -> state): `m_136e` keep -> holds; `m_641a` keep -> holds; `m_2e3c` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_46f7~p_da85` policy_echoes_evidence: "safety compliance rating" (judge under C7/C11)
- soft `u_64fe` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_09ce161ca2  (F6-007, travel logistics)

*World:* Evaluations of transport service providers across bus, rail, and maritime sectors for enterprise logistics contracts.

### A. System view (judge C7 from this alone)
- `e_4530` [2026-01-08, International Maritime Standards Registry.] BlueWave Marine holds an active ISO 14001 environmental certification.
- `e_9abc` [2026-01-11, Annual audit summary by Fleet Inspectorate.] Apex Charters maintains an active fleet size of 15 luxury coaches.
- `e_f1ad` [2026-01-14, National Rail Operations quarterly performance database.] Horizon Rail recorded a quarterly on-time arrival rate of 94 percent.
- `e_da98` [2026-01-17, State Licensing Authority official portal extract.] Apex Charters holds a Class A Passenger Transport Permit.
- memories:
  - `m_d46f` BlueWave Marine satisfies sustainable maritime fleet standards.
  - `m_0aac` Horizon Rail meets premier passenger train benchmarks.
  - `m_e6ca` Apex Charters meets executive ground mobility requirements.
  - `m_828c` Select Apex Charters for the corporate retreat transport contract.
- update `u_53ca` [2026-01-20, Department of Transportation public advisory bulletin.] A regulatory inquiry has raised questions regarding the validity of Apex Charters' Class A Passenger Transport Permit.
- policies:
  - `p_eb34` A cargo shipping company fulfills sustainable ocean fleet criteria if it holds an active ISO 14001 environmental certification.
  - `p_9142` An aviation provider gains fast-track customs clearance when its annual flight safety index exceeds 98 points.
  - `p_6d55` A logistics company receives expedited cargo privileges if its audited damage rate stays below 1 percent.
  - `p_5c03` A railway company fulfills top-tier passenger train criteria when its quarterly on-time arrival rate is 90 percent or higher.
  - `p_b79b` A transport firm satisfies executive ground travel specifications either by securing a Class A Passenger Transport Permit or by maintaining a luxury coach fleet size of at least 10 coaches.
  - `p_bb0a` A transit vendor fulfilling executive ground travel specifications is awarded corporate excursion transport agreements.

### B. Intended structure
- `m_e6ca` (B1) [policy `p_b79b`] <= (`e_da98`) **OR** (`e_9abc`); gold after update: **keep**
  - set 1: Apex Charters holds a Class A Passenger Transport Permit, satisfying the permit requirement.
  - set 2: Apex Charters maintains a luxury coach fleet size of 15 coaches, exceeding the minimum threshold of 10 coaches.
- `m_828c` (D1) [policy `p_bb0a`] <= (`m_e6ca`); gold after update: **keep**
  - set 1: Apex Charters satisfies executive ground travel specifications, qualifying it for corporate excursion transport agreements.
- `m_0aac` (B2) [policy `p_5c03`] <= (`e_f1ad`); gold after update: **keep**
  - set 1: Horizon Rail achieved an on-time arrival rate of 94 percent last quarter, exceeding the 90 percent threshold.
- `m_d46f` (B3) [policy `p_eb34`] <= (`e_4530`); gold after update: **keep**
  - set 1: BlueWave Marine holds an active ISO 14001 environmental certification, meeting sustainable ocean fleet criteria.
- `u_53ca` hedges `e_da98` (reliability high)
- decoy policies: `p_9142`, `p_6d55`
- final state after updates (gold action -> state): `m_e6ca` keep -> holds; `m_0aac` keep -> holds; `m_d46f` keep -> holds; `m_828c` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_4530~p_eb34` policy_echoes_evidence: "holds an active" (judge under C7/C11)
- soft `e_9abc~p_b79b` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_f1ad~p_5c03` policy_echoes_evidence: "on-time arrival rate; quarterly on-time arrival" (judge under C7/C11)

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

## s_1de8120cdc  (F6-008, product eligibility)

*World:* An evaluation assistant assesses healthcare and environmental products for procurement standards and regulatory clearance.

### A. System view (judge C7 from this alone)
- `e_7327` [2026-01-08, Certified environmental laboratory test log] AquaTech's BioPure Filter achieved a microparticle filtration efficiency of 99.8% this year.
- `e_7785` [2026-01-11, Official quality management registry] Apex Health's AuraScan Pro holds an ISO 13485 certification.
- `e_2854` [2026-01-14, Official clinical trial registry statement] Apex Health's AuraScan Pro achieved a clinical trial accuracy rate of 95% this year.
- `e_a28b` [2026-01-17, European regulatory agency database entry] NovaMed's ThermaGel Patch earned a European CE mark authorization.
- `e_9437` [2026-01-20, Audited manufacturing quality report] Apex Health's AuraScan Pro recorded a defect rate of 0.5% this year.
- memories:
  - `m_c94c` AuraScan Pro meets fundamental quality standards.
  - `m_88bd` BioPure Filter is eligible for municipal water contract bidding.
  - `m_5b70` AuraScan Pro attains preferred hospital procurement status.
  - `m_6583` AuraScan Pro is recommended for national hospital group supply contracts.
  - `m_6305` ThermaGel Patch is cleared for commercial distribution across Europe.
- update `u_b3d8` [2026-01-23, Anonymous user comment on a discussion forum] An online post states that AuraScan Pro never achieved a clinical trial accuracy rate of 95% this year.
- policies:
  - `p_d0b7` An industrial lubricant receives heavy-duty rating when its flash point exceeds 200 degrees Celsius.
  - `p_f1fe` A therapeutic product gains European market clearance when it secures a CE mark authorization.
  - `p_06e0` A device is granted premier health network approval provided it satisfies core benchmark criteria and maintains an annual manufacturing flaw frequency under 1.0%.
  - `p_0b59` A product is selected for nationwide network delivery agreements once it receives premier health network approval.
  - `p_5bad` Diagnostic hardware satisfies core benchmark criteria if it either registers a clinical trial precision percentage of at least 90% during the current year or holds an ISO 13485 certification.
  - `p_b49c` A purification system qualifies for public utility supply tenders if its yearly particulate capture rating exceeds 95%.
  - `p_8eca` A photovoltaic unit earns top-tier distinction provided its annual degradation rate remains below 0.5%.

### B. Intended structure
- `m_c94c` (B1) [policy `p_5bad`] <= (`e_2854`) **OR** (`e_7785`); gold after update: **keep**
  - set 1: AuraScan Pro meets fundamental quality standards because its 95% clinical trial accuracy rate this year satisfies the minimum requirement of 90%.
  - set 2: AuraScan Pro meets fundamental quality standards because it holds an ISO 13485 certification.
- `m_5b70` (B2) [policy `p_06e0`] <= (`m_c94c` AND `e_9437`); gold after update: **keep**
  - set 1: AuraScan Pro attains preferred hospital procurement status because it satisfies core benchmark criteria and its 0.5% defect rate this year is below the maximum allowed threshold of 1.0%.
- `m_6583` (D1) [policy `p_0b59`] <= (`m_5b70`); gold after update: **keep**
  - set 1: AuraScan Pro is recommended for national hospital group supply contracts because it has gained premier health network approval.
- `m_88bd` (B3) [policy `p_b49c`] <= (`e_7327`); gold after update: **keep**
  - set 1: BioPure Filter is eligible for municipal water contract bidding because its 99.8% microparticle filtration efficiency this year exceeds the required threshold of 95%.
- `m_6305` (B4) [policy `p_f1fe`] <= (`e_a28b`); gold after update: **keep**
  - set 1: ThermaGel Patch is cleared for commercial distribution across Europe because it holds a European CE mark authorization.
- `u_b3d8` retracts `e_2854` (reliability low)
- decoy policies: `p_d0b7`, `p_8eca`
- final state after updates (gold action -> state): `m_c94c` keep -> holds; `m_88bd` keep -> holds; `m_6305` keep -> holds; `m_5b70` keep -> holds; `m_6583` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2854~p_5bad` policy_echoes_evidence: "a clinical trial" (judge under C7/C11)

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
