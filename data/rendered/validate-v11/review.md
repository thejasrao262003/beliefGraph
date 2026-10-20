# Renderer review sheet

## s_936898d0fd  (F1-004, product eligibility)

*World:* A technical safety board evaluates product eligibility and commercial clearance for drones and power equipment.

### A. System view (judge C7 from this alone)
- `e_ecbf` [2026-01-08, Manufacturer technical specification sheet verified by the Safety Inspectorate] AeroGlide X1 has an emergency parachute deployment system response time of 0.8 seconds.
- `e_64dd` [2026-01-11, Certified lab report from Energy Standards Lab] SolarPulse Max has a peak efficiency rating of 98.5 percent.
- `e_39d3` [2026-01-14, Official flight test report from the National Aviation Testing Lab] AeroGlide X1 recorded a maximum wind resistance speed of 55 km/h during flight testing.
- `e_ec59` [2026-01-17, Logbook record certified by the Civil Aviation Authority] AeroGlide X1 completed 120 autonomous night flight hours this year.
- `e_79f5` [2026-01-20, EU Conformity Assessment Registry database entry] AeroGlide X1 carries a valid CE Mark safety certification.
- `e_42fa` [2026-01-23, Signed policy certificate from Global Aviation Underwriters] AeroGlide X1 has an annual operational insurance coverage of 5,000,000 USD.
- memories:
  - `m_9138` AeroGlide X1 satisfies flight safety baseline standards.
  - `m_392e` SolarPulse Max qualifies for Tier 1 grid integration.
  - `m_97e1` AeroGlide X1 holds commercial operating clearance.
  - `m_6cc1` AeroGlide X1 is approved for urban area deployments.
  - `m_76fd` AeroGlide X1 is selected for emergency response service.
  - `m_c668` AeroGlide X1 meets high-risk mission authorization rules.
- update `u_d261` [2026-01-26, Official public notice from the National Aviation Testing Lab] The National Aviation Testing Lab issued a formal retraction stating that AeroGlide X1 never achieved the recorded wind resistance speed during flight testing.
- policies:
  - `p_2268` An aircraft achieves safety baseline clearance if its sustained air resistance velocity equals at least 50 km/h and it possesses active CE Mark safety certification.
  - `p_ad81` A model is permitted for municipal overflight if it has commercial drone qualification alongside a parachute deployment system response time of no more than 1.0 seconds.
  - `p_efd3` A drone is designated for urgent relief dispatch when it receives elevated hazard authorization and logs a minimum of 100 autonomous night flight hours this year.
  - `p_0320` A commercial drone qualification is granted when an aircraft achieves safety baseline clearance.
  - `p_45c6` An inverter achieves premium grid interconnection eligibility if its peak efficiency rating is equal to or greater than 97.0 percent.
  - `p_f388` An aerial vehicle receives elevated hazard authorization provided it is permitted for municipal overflight and maintains annual operational insurance coverage of at least 2,000,000 USD.
  - `p_8d32` A commercial storage unit achieves utility-scale endorsement provided its thermal management threshold remains under 45 degrees Celsius.
  - `p_389e` A maritime vessel receives deep-water navigation endorsement if its hull integrity rating exceeds 90 points and it maintains active satellite tracking.

### B. Intended structure
- `m_9138` (B1) [policy `p_2268`] <= (`e_39d3` AND `e_79f5`); gold after update: **withdraw**
  - set 1: AeroGlide X1 satisfies safety baseline clearance because its wind resistance speed of 55 km/h meets the 50 km/h threshold and it holds CE Mark safety certification.
- `m_97e1` (B2) [policy `p_0320`] <= (`m_9138`); gold after update: **withdraw**
  - set 1: AeroGlide X1 achieves commercial drone qualification because it satisfies safety baseline clearance.
- `m_6cc1` (B3) [policy `p_ad81`] <= (`m_97e1` AND `e_ecbf`); gold after update: **withdraw**
  - set 1: AeroGlide X1 is permitted for municipal overflight because it holds commercial drone qualification and its parachute deployment response time of 0.8 seconds is below 1.0 seconds.
- `m_c668` (B4) [policy `p_f388`] <= (`m_6cc1` AND `e_42fa`); gold after update: **withdraw**
  - set 1: AeroGlide X1 receives elevated hazard authorization because it is permitted for municipal overflight and holds 5,000,000 USD in annual operational insurance coverage, exceeding the 2,000,000 USD requirement.
- `m_76fd` (D1) [policy `p_efd3`] <= (`m_c668` AND `e_ec59`); gold after update: **withdraw**
  - set 1: AeroGlide X1 is designated for urgent relief dispatch because it holds elevated hazard authorization and logged 120 autonomous night flight hours this year, surpassing the 100-hour threshold.
- `m_392e` (B5) [policy `p_45c6`] <= (`e_64dd`); gold after update: **keep**
  - set 1: SolarPulse Max achieves premium grid interconnection eligibility because its peak efficiency rating of 98.5 percent exceeds the required 97.0 percent.
- `u_d261` retracts `e_39d3` (reliability high)
- decoy policies: `p_389e`, `p_8d32`
- final state after updates (gold action -> state): `m_9138` withdraw -> fails; `m_392e` keep -> holds; `m_97e1` withdraw -> fails; `m_6cc1` withdraw -> fails; `m_c668` withdraw -> fails; `m_76fd` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_ecbf~p_ad81` policy_echoes_evidence: "deployment system response; parachute deployment system; response time of; system response time" (judge under C7/C11)
- soft `e_64dd~p_45c6` policy_echoes_evidence: "peak efficiency rating" (judge under C7/C11)
- soft `e_ec59~p_efd3` policy_echoes_evidence: "autonomous night flight; flight hours this; hours this year; night flight hours" (judge under C7/C11)
- soft `e_42fa~p_f388` policy_echoes_evidence: "annual operational insurance; insurance coverage of; operational insurance coverage" (judge under C7/C11)

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

## s_b916d4bc57  (F1-008, product eligibility)

*World:* A product evaluation board assesses hardware devices for specialized market eligibility based on laboratory test results and regulatory certifications.

### A. System view (judge C7 from this alone)
- `e_8d31` [2026-01-08, Certified measurement log from National Photovoltaic Laboratory.] OmniSolar 300 achieved peak output of 450 W.
- `e_fea4` [2026-01-11, Signed lab test report from Apex Engineering.] Veloce 500 logged continuous run time of 500 hours.
- `e_181b` [2026-01-14, Official certificate database of the International Accreditation Body.] Veloce 500 holds ISO 13485 certification.
- `e_3a85` [2026-01-17, Official acoustic test audit from SoundTech Labs.] AeroChill 90 recorded operational noise of 32 dB during full capacity testing.
- memories:
  - `m_9b2b` AeroChill 90 meets ultra-quiet equipment standards.
  - `m_5794` Veloce 500 holds Priority Distribution eligibility.
  - `m_d127` Veloce 500 holds extended durability designation.
  - `m_9454` Veloce 500 satisfies premium healthcare device standards.
  - `m_c28b` OmniSolar 300 achieves high-efficiency solar rating.
  - `m_2a4c` Veloce 500 is selected for fast-track clinical deployment.
- update `u_1cb3` [2026-01-20, Audit correction notice from Apex Testing Services.] Apex Testing Services issued an official statement confirming Veloce 500 did not complete continuous run time of 500 hours this year.
- policies:
  - `p_9e88` A hardware model meets standards for premium healthcare devices if it possesses ISO 13485 certification and maintains designation of extended durability.
  - `p_e3b9` A product is assigned eligibility for priority distribution provided it satisfies standards for premium healthcare devices.
  - `p_6a52` A commercial generator receives eco-label certification when its performance index reaches at least 95 percent.
  - `p_a3c4` A unit attains high-efficiency solar status if peak output is no less than 450 W.
  - `p_f56b` A cooling system qualifies for ultra-quiet equipment status when operational noise does not exceed 32 dB.
  - `p_bfc7` Authorization for clinical deployment on a fast-track basis requires eligibility for priority distribution.
  - `p_8f08` A device qualifies for designation of extended durability when its uninterrupted operational duration reaches a minimum threshold of 500 hours.
  - `p_a9d9` A fluid pump obtains marine grade authorization when its submersion depth limit reaches 50 meters.

### B. Intended structure
- `m_d127` (B1) [policy `p_8f08`] <= (`e_fea4`); gold after update: **withdraw**
  - set 1: Veloce 500 logged 500 hours of continuous run time this year, meeting the requirement of at least 500 hours within one year for extended durability designation.
- `m_9454` (B2) [policy `p_9e88`] <= (`m_d127` AND `e_181b`); gold after update: **withdraw**
  - set 1: Veloce 500 holds extended durability designation and possesses ISO 13485 certification, satisfying both criteria for premium healthcare device standards.
- `m_5794` (B3) [policy `p_e3b9`] <= (`m_9454`); gold after update: **withdraw**
  - set 1: Veloce 500 satisfies premium healthcare device standards, fulfilling the condition for Priority Distribution eligibility.
- `m_2a4c` (D1) [policy `p_bfc7`] <= (`m_5794`); gold after update: **withdraw**
  - set 1: Veloce 500 holds Priority Distribution eligibility, which grants authorization for fast-track clinical deployment.
- `m_c28b` (B4) [policy `p_a3c4`] <= (`e_8d31`); gold after update: **keep**
  - set 1: OmniSolar 300 recorded a peak output of 450 W this quarter, reaching the 450 W threshold for high-efficiency solar status.
- `m_9b2b` (B5) [policy `p_f56b`] <= (`e_3a85`); gold after update: **keep**
  - set 1: AeroChill 90 produced an operational noise level of 32 dB, remaining at or below the 32 dB limit for ultra-quiet equipment status.
- `u_1cb3` retracts `e_fea4` (reliability high)
- decoy policies: `p_6a52`, `p_a9d9`
- final state after updates (gold action -> state): `m_d127` withdraw -> fails; `m_c28b` keep -> holds; `m_9b2b` keep -> holds; `m_9454` withdraw -> fails; `m_5794` withdraw -> fails; `m_2a4c` withdraw -> fails

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

## s_2ee168f32f  (F2-002, product eligibility)

*World:* Assessment of product eligibility and market approval for commercial release.

### A. System view (judge C7 from this alone)
- `e_455b` [2026-01-08, Home Appliance Testing Institute certificate] Vortex Air Purifier has a clean air delivery rate of 350 CFM.
- `e_e8cb` [2026-01-11, Underwriters Laboratories official verification database] Titan Power Bank holds UL safety certification.
- `e_f430` [2026-01-14, Aura Energy manufacturer specifications sheet] Aura Solar Panel includes a product warranty period of 25 years.
- `e_2c74` [2026-01-17, National Renewable Energy Laboratory report] Aura Solar Panel achieved a power conversion efficiency of 22% during independent lab tests.
- `e_199f` [2026-01-20, Clean Energy Audit Board registry entry] Aura Solar Panel demonstrated a power conversion efficiency of 21% in field evaluation trials.
- memories:
  - `m_03ce` Vortex Air Purifier meets the allergy-friendly designation.
  - `m_7524` Include Aura Solar Panel in the public infrastructure catalog.
  - `m_46f9` Aura Solar Panel satisfies the top performance tier.
  - `m_057f` Aura Solar Panel is eligible for clean technology subsidies.
  - `m_436a` Aura Solar Panel maintains regional market authorization.
  - `m_d7cd` Titan Power Bank satisfies consumer safety standards.
- update `u_cdad` [2026-01-23, Clean Energy Audit Board updated report] A revised audit confirmed Aura Solar Panel has a power conversion efficiency of 18% in field testing.
- policies:
  - `p_c031` Clean technology funding requires an item holding top performance status alongside a product warranty period of no less than 20 years.
  - `p_ad9a` Electronics achieve consumer safety approval by possessing UL safety certification.
  - `p_7a40` Regional distribution clearance is granted to products approved for sustainable energy incentives.
  - `p_bead` Commercial heating units qualify for heavy-duty certification if thermal output exceeds 50000 BTU.
  - `p_f8a3` A device achieves top performance status with a power conversion efficiency of 20% or higher.
  - `p_4a8e` An appliance receives allergy-safe certification if its clean air delivery rate is 300 CFM or greater.
  - `p_28dd` Inclusion in municipal procurement listings requires equipment to have regional distribution clearance.
  - `p_84e2` A medical device gains rapid deployment clearance with ISO 13485 certification.

### B. Intended structure
- `m_46f9` (B1) [policy `p_f8a3`] <= (`e_2c74`) **OR** (`e_199f`); gold after update: **keep**
  - set 1: Aura Solar Panel has a power conversion efficiency of 22%, meeting the 20% requirement for top performance status.
  - set 2: Aura Solar Panel has a power conversion efficiency of 21%, meeting the 20% requirement for top performance status.
- `m_057f` (B2) [policy `p_c031`] <= (`m_46f9` AND `e_f430`); gold after update: **keep**
  - set 1: Aura Solar Panel achieves top performance status and has a product warranty period of 25 years, satisfying the 20-year requirement for clean technology funding.
- `m_436a` (B3) [policy `p_7a40`] <= (`m_057f`); gold after update: **keep**
  - set 1: Aura Solar Panel qualifies for clean technology funding, securing regional distribution clearance.
- `m_7524` (D1) [policy `p_28dd`] <= (`m_436a`); gold after update: **keep**
  - set 1: Aura Solar Panel holds regional distribution clearance, qualifying it for inclusion in municipal procurement listings.
- `m_03ce` (B4) [policy `p_4a8e`] <= (`e_455b`); gold after update: **keep**
  - set 1: Vortex Air Purifier has a clean air delivery rate of 350 CFM, exceeding the 300 CFM threshold for allergy-safe certification.
- `m_d7cd` (B5) [policy `p_ad9a`] <= (`e_e8cb`); gold after update: **keep**
  - set 1: Titan Power Bank holds UL safety certification, fulfilling the requirement for consumer safety approval.
- `u_cdad` supersedes `e_199f` (reliability high)
- decoy policies: `p_bead`, `p_84e2`
- final state after updates (gold action -> state): `m_46f9` keep -> holds; `m_03ce` keep -> holds; `m_d7cd` keep -> holds; `m_057f` keep -> holds; `m_436a` keep -> holds; `m_7524` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_455b~p_4a8e` policy_echoes_evidence: "air delivery rate; clean air delivery" (judge under C7/C11)
- soft `e_f430~p_c031` policy_echoes_evidence: "a product warranty; product warranty period; warranty period of" (judge under C7/C11)
- soft `e_2c74~p_f8a3` policy_echoes_evidence: "a power conversion; conversion efficiency of; power conversion efficiency" (judge under C7/C11)
- soft `e_199f~p_f8a3` policy_echoes_evidence: "a power conversion; conversion efficiency of; power conversion efficiency" (judge under C7/C11)

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

## s_ecf563bf62  (F2-003, travel logistics)

*World:* Travel logistics evaluation for regional transit operators and charter services.

### A. System view (judge C7 from this alone)
- `e_8195` [2026-01-08, National transport registry listing.] Apex Expeditions maintains a fleet size of 18 vehicles.
- `e_2b00` [2026-01-11, Signed insurer certificate.] Apex Expeditions maintains liability insurance coverage of 5,000,000 USD.
- `e_5638` [2026-01-14, Annual dispatch log summary.] Apex Expeditions completed 520 transfers this year.
- `e_c747` [2026-01-17, Official client feedback system record.] Apex Expeditions earned a customer satisfaction score of 94 this year.
- `e_0c87` [2026-01-20, Civil aviation authority portal.] Meridian Charter holds an active international charter licence.
- memories:
  - `m_a25e` Apex Expeditions is selected for the municipal contract.
  - `m_0abd` Meridian Charter is approved for cross-border routes.
  - `m_f286` Apex Expeditions is granted priority dispatch status.
- update `u_1194` [2026-01-23, Audited financial review report.] Apex Expeditions completed 410 transfers this year.
- update `u_4e74` [2026-01-26, Revised annual audit release.] Apex Expeditions received a customer satisfaction score of 82 this year.
- update `u_68a2` [2026-01-29, Updated motor carrier inspection report.] Apex Expeditions operates a fleet size of 10 vehicles.
- policies:
  - `p_d123` A marine ferry operator receives a harbour docking permit if it maintains an emergency response rating of 85 or above.
  - `p_dc1a` Cross-border route authorization is granted to any transport vendor possessing an active international charter licence.
  - `p_4b4f` A charter firm is chosen for civic service contracts provided it holds priority routing status and carries liability insurance coverage of 5,000,000 USD or higher.
  - `p_8374` Priority routing status is assigned to a travel agency that attains a customer satisfaction score of 90 or more annually, maintains a fleet size of at least 15 vehicles, or completes 500 transfers per year.
  - `p_a11e` An air cargo handler qualifies for expedited customs processing by maintaining a certified cargo handling facility and completing at least 1,000 freight movements annually.

### B. Intended structure
- `m_f286` (B1) [policy `p_8374`] <= (`e_c747`) **OR** (`e_8195`) **OR** (`e_5638`); gold after update: **recompute**
  - set 1: Apex Expeditions satisfies the priority routing rule by achieving a customer satisfaction score of 94 this year, which meets the threshold of 90.
  - set 2: Apex Expeditions satisfies the priority routing rule by operating 18 vehicles, exceeding the fleet size requirement of 15.
  - set 3: Apex Expeditions satisfies the priority routing rule by logging 520 transfers this year, exceeding the threshold of 500.
- `m_a25e` (D1) [policy `p_4b4f`] <= (`m_f286` AND `e_2b00`); gold after update: **recompute**
  - set 1: Apex Expeditions qualifies for municipal contract selection because it holds priority routing status and maintains liability insurance coverage of 5,000,000 USD.
- `m_0abd` (B2) [policy `p_dc1a`] <= (`e_0c87`); gold after update: **keep**
  - set 1: Meridian Charter satisfies the cross-border route criteria by holding an active international charter licence.
- `u_1194` supersedes `e_5638` (reliability high)
- `u_4e74` supersedes `e_c747` (reliability high)
- `u_68a2` supersedes `e_8195` (reliability high)
- decoy policies: `p_a11e`, `p_d123`
- final state after updates (gold action -> state): `m_f286` recompute -> fails; `m_0abd` keep -> holds; `m_a25e` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_8195~p_8374` policy_echoes_evidence: "a fleet size; fleet size of; maintains a fleet" (judge under C7/C11)
- soft `e_2b00~p_4b4f` policy_echoes_evidence: "insurance coverage of; liability insurance coverage" (judge under C7/C11)
- soft `e_c747~p_8374` policy_echoes_evidence: "a customer satisfaction; customer satisfaction score; satisfaction score of" (judge under C7/C11)
- soft `e_0c87~p_dc1a` policy_echoes_evidence: "active international charter; an active international; international charter licence" (judge under C7/C11)

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

## s_855e62e6dc  (F2-004, product eligibility)

*World:* Evaluating product performance data and compliance certifications across various industrial equipment lines.

### A. System view (judge C7 from this alone)
- `e_395f` [2026-01-08, Titan Motors Factory Certificate] Titan Heavy Truck demonstrates a weight rating of 18 metric tons.
- `e_3760` [2026-01-11, Lumina Health Product Manual] Lumina Medical Monitor provides a battery operation duration of 12 hours.
- `e_0781` [2026-01-14, AeroCorp Systems Specification Sheet] Apex 400 Drone incorporates redundant obstacle detection.
- `e_7909` [2026-01-17, AeroCorp Telemetry Field Log] Apex 400 Drone maintains a signal radius of 12 kilometers.
- `e_6b2f` [2026-01-20, AeroCorp Engineering Performance Sheet] Apex 400 Drone offers a continuous airtime of 45 minutes.
- `e_6624` [2026-01-23, Federal Aviation Administration Registry] Apex 400 Drone holds an active FAA Part 107 license.
- `e_0e8c` [2026-01-26, Acoustic Testing Laboratory Record] Solis HVAC Unit produces a sound emission level of 42 decibels.
- memories:
  - `m_bd24` Apex 400 Drone is assigned to priority freight routes.
  - `m_b8e0` Titan Heavy Truck earns heavy load transit approval.
  - `m_78b4` Lumina Medical Monitor meets mobile intensive care needs.
  - `m_db12` Solis HVAC Unit fulfills low-noise residential requirements.
  - `m_15e4` Apex 400 Drone achieves top-tier aviation rating.
  - `m_d5cc` Apex 400 Drone qualifies for commercial dispatch.
- update `u_648e` [2026-01-29, Federal Aviation Administration Registry Notice] The Federal Aviation Administration Registry indicates that Apex 400 Drone no longer holds an active FAA Part 107 license.
- update `u_bac7` [2026-02-01, AeroCorp Telemetry Field Log Update] A revised telemetry log confirms Apex 400 Drone maintains a signal radius of 8 kilometers.
- update `u_e470` [2026-02-04, AeroCorp Engineering Performance Sheet Revision] An updated engineering record shows Apex 400 Drone offers a continuous airtime of 35 minutes.
- policies:
  - `p_f537` An uncrewed aircraft obtains dispatch readiness when it possesses a high-grade aerial designation while incorporating redundant obstacle detection.
  - `p_b21a` Mobile care suitability is established for equipment providing a battery operation duration of no less than 8 hours.
  - `p_97df` An industrial generator achieves green facility certification if its carbon output stays below 100 grams per kilowatt-hour.
  - `p_49da` Hauling permission is granted to cargo vehicles with a weight rating exceeding 15 metric tons.
  - `p_a46c` Deployment for cargo transport occurs whenever an aircraft maintains dispatch readiness.
  - `p_9a1c` A commercial drone receives high-grade aerial designation if it provides a continuous airtime of at least 40 minutes, maintains a signal radius of at least 10 kilometers, or holds an active FAA Part 107 license.
  - `p_6abb` A marine vessel achieves coastal navigation clearance if its hull thickness is at least 25 millimeters or it carries radar tracking equipment.
  - `p_45fd` A residential climate system attains noise compliance provided its sound emission level remains under 50 decibels.

### B. Intended structure
- `m_15e4` (B1) [policy `p_9a1c`] <= (`e_6b2f`) **OR** (`e_7909`) **OR** (`e_6624`); gold after update: **recompute**
  - set 1: Apex 400 Drone provides 45 minutes of airtime, exceeding the 40-minute requirement for high-grade aerial designation.
  - set 2: Apex 400 Drone maintains a signal radius of 12 kilometers, meeting the 10-kilometer requirement for high-grade aerial designation.
  - set 3: Apex 400 Drone holds an active FAA Part 107 license, fulfilling the certification requirement for high-grade aerial designation.
- `m_d5cc` (B2) [policy `p_f537`] <= (`m_15e4` AND `e_0781`); gold after update: **recompute**
  - set 1: Apex 400 Drone achieves high-grade aerial designation and possesses redundant obstacle detection, meeting all dispatch readiness criteria.
- `m_bd24` (D1) [policy `p_a46c`] <= (`m_d5cc`); gold after update: **recompute**
  - set 1: Apex 400 Drone maintains dispatch readiness, satisfying the condition for cargo transport deployment.
- `m_78b4` (B3) [policy `p_b21a`] <= (`e_3760`); gold after update: **keep**
  - set 1: Lumina Medical Monitor provides 12 hours of battery operation duration, exceeding the 8-hour requirement for mobile care suitability.
- `m_db12` (B4) [policy `p_45fd`] <= (`e_0e8c`); gold after update: **keep**
  - set 1: Solis HVAC Unit has a sound emission level of 42 decibels, which is below the 50-decibel limit for noise compliance.
- `m_b8e0` (B5) [policy `p_49da`] <= (`e_395f`); gold after update: **keep**
  - set 1: Titan Heavy Truck has a weight rating of 18 metric tons, exceeding the 15-metric-ton threshold for hauling permission.
- `u_648e` supersedes `e_6624` (reliability high)
- `u_bac7` supersedes `e_7909` (reliability high)
- `u_e470` supersedes `e_6b2f` (reliability high)
- decoy policies: `p_6abb`, `p_97df`
- final state after updates (gold action -> state): `m_15e4` recompute -> fails; `m_78b4` keep -> holds; `m_db12` keep -> holds; `m_b8e0` keep -> holds; `m_d5cc` recompute -> fails; `m_bd24` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_395f~p_49da` policy_echoes_evidence: "a weight rating" (judge under C7/C11)
- soft `e_3760~p_b21a` policy_echoes_evidence: "a battery operation; battery operation duration; operation duration of" (judge under C7/C11)
- soft `e_0781~p_f537` policy_echoes_evidence: "redundant obstacle detection" (judge under C7/C11)
- soft `e_7909~p_9a1c` policy_echoes_evidence: "a signal radius; maintains a signal; signal radius of" (judge under C7/C11)
- soft `e_6b2f~p_9a1c` policy_echoes_evidence: "a continuous airtime; continuous airtime of" (judge under C7/C11)
- soft `e_6624~p_9a1c` policy_echoes_evidence: "holds an active" (judge under C7/C11)
- soft `e_0e8c~p_45fd` policy_echoes_evidence: "sound emission level" (judge under C7/C11)

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

## s_1e4e415b76  (F3-001, travel logistics)

*World:* Evaluations and contract decisions for passenger transportation and fleet logistics providers.

### A. System view (judge C7 from this alone)
- `e_efaf` [2026-01-08, State licensing authority database entry.] Apex Tours holds an active Commercial Passenger Transport Licence.
- `e_cecb` [2026-01-11, Quarterly performance log submitted by dispatch operations.] Horizon Charter recorded an on-time arrival rate of 98 percent this quarter.
- `e_03b9` [2026-01-14, Official fleet registry from the Department of Transportation.] Apex Tours maintains an active fleet size of 15 coaches.
- `e_9416` [2026-01-17, Service level agreement from Fleet Support Services.] Apex Tours maintains active 24-hour roadside assistance coverage.
- `e_d52f` [2026-01-20, Official registry entry from the Municipal Environmental Board.] Sol Express holds an active Green Transit Certification.
- `e_c8d9` [2026-01-23, Annual safety audit report issued by the Transit Safety Board.] Apex Tours earned a safety evaluation score of 92 points this year.
- memories:
  - `m_29fa` Horizon Charter secures premier service standing.
  - `m_c464` Sol Express qualifies for local eco-subsidy funds.
  - `m_58c3` Apex Tours receives the corporate transit contract.
  - `m_76d0` Apex Tours achieves preferred carrier status.
- update `u_5ce3` [2026-01-26, Revised safety audit report from the Transit Safety Board.] Apex Tours earned a revised safety evaluation score of 78 points this year.
- policies:
  - `p_7f75` Assignment to corporate transit agreements mandates an operator with carrier preferred designation who also maintains active 24-hour roadside assistance coverage.
  - `p_a189` Passenger rail operators obtain express corridor clearance if their automated braking efficiency measures 99 percent or greater.
  - `p_658f` Access to municipal environmental subsidies requires a transportation firm to maintain a valid Green Transit Certification.
  - `p_eab6` Top-tier service rating is awarded if a travel provider demonstrates a quarterly on-time arrival rate of 95 percent or higher.
  - `p_3c20` A maritime transport firm obtains international route clearance provided it maintains a vessel cargo volume of at least 5000 tons and holds a Maritime Safety Certificate.
  - `p_98c8` Carrier preferred designation is granted when an operator maintains a minimum active fleet size of 10 coaches, receives an annual safety evaluation score of at least 85 points, and holds a valid Commercial Passenger Transport Licence.

### B. Intended structure
- `m_76d0` (B1) [policy `p_98c8`] <= (`e_03b9` AND `e_c8d9` AND `e_efaf`); gold after update: **recompute**
  - set 1: Apex Tours has a fleet size of 15 coaches, a safety evaluation score of 92 points this year, and a Commercial Passenger Transport Licence, satisfying the requirement for carrier preferred designation.
- `m_58c3` (D1) [policy `p_7f75`] <= (`m_76d0` AND `e_9416`); gold after update: **recompute**
  - set 1: Apex Tours achieves carrier preferred designation and holds 24-hour roadside assistance coverage, satisfying the criteria for corporate transit agreements.
- `m_29fa` (B2) [policy `p_eab6`] <= (`e_cecb`); gold after update: **keep**
  - set 1: Horizon Charter achieved an on-time arrival rate of 98 percent this quarter, satisfying the condition for top-tier service rating.
- `m_c464` (B3) [policy `p_658f`] <= (`e_d52f`); gold after update: **keep**
  - set 1: Sol Express holds a Green Transit Certification, satisfying the condition for local eco-subsidy funds.
- `u_5ce3` supersedes `e_c8d9` (reliability high)
- decoy policies: `p_3c20`, `p_a189`
- final state after updates (gold action -> state): `m_76d0` recompute -> fails; `m_29fa` keep -> holds; `m_c464` keep -> holds; `m_58c3` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_cecb~p_eab6` policy_echoes_evidence: "arrival rate of; on-time arrival rate" (judge under C7/C11)
- soft `e_03b9~p_98c8` policy_echoes_evidence: "active fleet size; fleet size of" (judge under C7/C11)
- soft `e_9416~p_7f75` policy_echoes_evidence: "roadside assistance coverage" (judge under C7/C11)
- soft `e_c8d9~p_98c8` policy_echoes_evidence: "evaluation score of; safety evaluation score" (judge under C7/C11)

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

## s_793edb6c07  (F6-000, product eligibility)

*World:* An assistant tracks supplier credentials, product certifications, and contract eligibility across health, energy, and food sector vendors.

### A. System view (judge C7 from this alone)
- `e_5c64` [2026-01-08, Certified laboratory test result document] Solaria Energy achieved an efficiency rating of 22 percent this year.
- `e_589b` [2026-01-11, Signed insurance verification policy from Apex Assurance] Nexus Medical holds product liability coverage of 5,000,000 dollars.
- `e_735b` [2026-01-14, Official national medical supplier registry database] Nexus Medical holds an active ISO 13485 certification.
- `e_63cb` [2026-01-17, Municipal food safety inspection record] Crestview Foods holds a Grade A food hygiene certificate.
- `e_613e` [2026-01-20, Annual evaluation report from Health Quality Board] Nexus Medical maintains a quality audit score of 95 points this year.
- memories:
  - `m_ab27` Crestview Foods is cleared for commercial food distribution.
  - `m_5066` Nexus Medical is chosen for the national hospital procurement contract.
  - `m_d2dd` Solaria Energy qualifies for the clean energy rebate.
  - `m_dda8` Nexus Medical is designated an authorized healthcare vendor.
- update `u_35b5` [2026-01-23, Unconfirmed online message board thread] An unverified post claims Nexus Medical does not hold an active ISO 13485 certification.
- policies:
  - `p_6b28` Wholesale market distribution approval is granted to a vendor holding a Grade A food hygiene certificate.
  - `p_eaaf` Priority patent examination is granted to an applicant with an annual research investment of at least 1,000,000 dollars.
  - `p_30a2` Eligibility for sustainable technology grants requires an applicant to achieve an efficiency rating of at least 20 percent this year.
  - `p_3f5f` Healthcare supplier approval is granted to an applicant that possesses an active ISO 13485 certification or maintains a quality audit score of at least 90 points this year.
  - `p_2b0b` A maritime transport company earns premier carrier status if it manages an active fleet of at least 40 vessels.
  - `p_c15c` Awarding a major clinical supply contract requires an approved healthcare supplier that also maintains product liability coverage of at least 5,000,000 dollars.

### B. Intended structure
- `m_dda8` (B1) [policy `p_3f5f`] <= (`e_735b`) **OR** (`e_613e`); gold after update: **keep**
  - set 1: Nexus Medical holds an active ISO 13485 certification, satisfying the credential requirement for healthcare supplier approval.
  - set 2: Nexus Medical achieves a quality audit score of 95 points this year, meeting the minimum score threshold of 90 points for healthcare supplier approval.
- `m_5066` (D1) [policy `p_c15c`] <= (`m_dda8` AND `e_589b`); gold after update: **keep**
  - set 1: Nexus Medical is approved as a healthcare supplier and maintains product liability coverage of 5,000,000 dollars, fulfilling both requirements for a major clinical supply contract.
- `m_d2dd` (B2) [policy `p_30a2`] <= (`e_5c64`); gold after update: **keep**
  - set 1: Solaria Energy achieves an efficiency rating of 22 percent this year, meeting the minimum threshold of 20 percent for sustainable technology grants.
- `m_ab27` (B3) [policy `p_6b28`] <= (`e_63cb`); gold after update: **keep**
  - set 1: Crestview Foods holds a Grade A food hygiene certificate, satisfying the requirement for wholesale market distribution approval.
- `u_35b5` retracts `e_735b` (reliability low)
- decoy policies: `p_2b0b`, `p_eaaf`
- final state after updates (gold action -> state): `m_dda8` keep -> holds; `m_d2dd` keep -> holds; `m_ab27` keep -> holds; `m_5066` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_5c64~p_30a2` policy_echoes_evidence: "an efficiency rating; efficiency rating of; percent this year" (judge under C7/C11)
- soft `e_589b~p_c15c` policy_echoes_evidence: "liability coverage of; product liability coverage" (judge under C7/C11)
- soft `e_63cb~p_6b28` policy_echoes_evidence: "food hygiene certificate" (judge under C7/C11)
- soft `e_613e~p_3f5f` policy_echoes_evidence: "a quality audit; audit score of; maintains a quality; points this year; quality audit score" (judge under C7/C11)
- soft `u_35b5` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_643aada1a8  (F6-001, travel logistics)

*World:* An evaluation of travel logistics service providers and charter contractors based on performance metrics, fleet capabilities, and safety certifications.

### A. System view (judge C7 from this alone)
- `e_3824` [2026-01-08, Official quarterly audit register of Vanguard Travel] Vanguard Travel completed 150 VIP transport assignments this year.
- `e_2180` [2026-01-11, International Accreditation Forum official registry] Solis Charter holds a valid ISO 9001 certification.
- `e_18c5` [2026-01-14, Central insurance registry certificate for Vanguard Travel] Vanguard Travel holds active liability coverage of $5,000,000.
- `e_e948` [2026-01-17, Department of Transportation motor carrier database] Crestline Transport operates a fleet size of 40 luxury coaches.
- `e_8ace` [2026-01-20, Operations performance database for Zenith Couriers] Zenith Couriers achieved an average transit delay of 12 minutes.
- memories:
  - `m_46d5` Vanguard Travel will be selected for the executive retreat charter contract.
  - `m_f023` Solis Charter meets standardized quality management requirements.
  - `m_d33f` Vanguard Travel achieves premier carrier designation.
  - `m_29f2` Crestline Transport qualifies for high-capacity fleet classification.
  - `m_9e4d` Zenith Couriers satisfies punctual delivery performance criteria.
- update `u_cd3c` [2026-01-23, Official internal compliance audit memo] An official compliance review memo notes that several of Vanguard Travel's annual transport figures are unverified and undergoing re-audit.
- policies:
  - `p_f84d` Luggage handling certification is awarded to ground handlers with a quarterly baggage error rate under 0.5 percent.
  - `p_505a` An agency with premier carrier status is chosen for executive charter routing provided it maintains liability insurance of at least $2,000,000.
  - `p_2377` Qualification for high-volume transport fleet status is granted to operators maintaining a vehicle inventory of 30 or more coaches.
  - `p_8b6a` Punctuality standard compliance is recognized when a transport provider maintains a mean delay duration under 15 minutes.
  - `p_af74` Compliance with quality benchmarks requires holding an active ISO 9001 certification.
  - `p_2d74` Carrier status at the premier level requires completing a minimum threshold of 100 VIP transport assignments in a year.
  - `p_7cc4` A maritime agency earns preferred partner status if it maintains an annual booking volume of 500 voyages and holds a maritime operation license.

### B. Intended structure
- `m_d33f` (B1) [policy `p_2d74`] <= (`e_3824`); gold after update: **uncertain**
  - set 1: Vanguard Travel completed 150 VIP transport assignments this year, meeting the requirement of at least 100 assignments.
- `m_46d5` (D1) [policy `p_505a`] <= (`m_d33f` AND `e_18c5`); gold after update: **uncertain**
  - set 1: Vanguard Travel holds premier carrier status and maintains $5,000,000 in liability coverage, satisfying the required $2,000,000 threshold.
- `m_29f2` (B2) [policy `p_2377`] <= (`e_e948`); gold after update: **keep**
  - set 1: Crestline Transport operates 40 luxury coaches, satisfying the requirement of at least 30 coaches.
- `m_f023` (B3) [policy `p_af74`] <= (`e_2180`); gold after update: **keep**
  - set 1: Solis Charter holds an active ISO 9001 certification, satisfying the certification requirement.
- `m_9e4d` (B4) [policy `p_8b6a`] <= (`e_8ace`); gold after update: **keep**
  - set 1: Zenith Couriers achieved an average transit delay of 12 minutes this quarter, which is below the 15-minute threshold.
- `u_cd3c` hedges `e_3824` (reliability high)
- decoy policies: `p_7cc4`, `p_f84d`
- final state after updates (gold action -> state): `m_d33f` uncertain -> undetermined; `m_29f2` keep -> holds; `m_f023` keep -> holds; `m_9e4d` keep -> holds; `m_46d5` uncertain -> undetermined

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

## s_cd958eb0b2  (F6-004, product eligibility)

*World:* An assistant tracks compliance, safety certifications, and market eligibility for various commercial products.

### A. System view (judge C7 from this alone)
- `e_3413` [2026-01-08, Official flight acoustic test log signed by chief audio engineer.] AeroGlide X1 recorded an acoustic output level of 58 dB.
- `e_0b1d` [2026-01-11, Certified laboratory evaluation document.] VeraTherm 500 achieved a thermal resistance rating of 4.5 m²K/W.
- `e_b97e` [2026-01-14, Signed hardware audit summary from safety inspector.] AeroGlide X1 maintains an emergency reserve power duration of 25 minutes.
- `e_aef9` [2026-01-17, Official factory compliance certificate.] Solaris Prime holds a certified peak conversion efficiency of 98 percent.
- memories:
  - `m_6b8e` VeraTherm 500 satisfies high-grade insulation benchmarks.
  - `m_0517` Solaris Prime meets premium energy efficiency standards.
  - `m_96ef` AeroGlide X1 satisfies eco-friendly design criteria.
  - `m_3290` AeroGlide X1 is cleared for municipal transport service.
  - `m_cf41` AeroGlide X1 meets quiet flight criteria.
- update `u_5597` [2026-01-20, Anonymous comment posted on a tech discussion board.] An unverified blog comment claims that AeroGlide X1 never underwent sound level testing.
- policies:
  - `p_b238` A panel achieves high-grade insulation compliance if its thermal resistance rating equals 4.0 m²K/W or higher.
  - `p_c5b9` An inverter reaches top-tier energy performance rating when its peak conversion efficiency is 95 percent or greater.
  - `p_0dd6` A power tool secures industrial durability classification when its continuous load lifespan exceeds 500 hours.
  - `p_c627` An aircraft attains eco-friendly validation provided it secures quiet flight recognition.
  - `p_8c4d` A drone receives municipal transport authorization when it attains eco-friendly validation alongside an emergency reserve power duration of 20 minutes or greater.
  - `p_2cc1` An unmanned craft secures quiet flight recognition if its acoustic output level remains at or below 60 dB.
  - `p_234e` A commercial refrigeration unit obtains commercial cooling certification if its operating temperature stability remains within 2 degrees Celsius over 24 hours.

### B. Intended structure
- `m_cf41` (B1) [policy `p_2cc1`] <= (`e_3413`); gold after update: **uncertain**
  - set 1: AeroGlide X1's acoustic output level of 58 dB satisfies the policy requirement of being 60 dB or less.
- `m_96ef` (B2) [policy `p_c627`] <= (`m_cf41`); gold after update: **uncertain**
  - set 1: AeroGlide X1 secures quiet flight recognition, which satisfies the policy requirement for eco-friendly validation.
- `m_3290` (D1) [policy `p_8c4d`] <= (`m_96ef` AND `e_b97e`); gold after update: **uncertain**
  - set 1: AeroGlide X1 achieves eco-friendly validation and has an emergency reserve power duration of 25 minutes, meeting the 20-minute threshold.
- `m_6b8e` (B3) [policy `p_b238`] <= (`e_0b1d`); gold after update: **keep**
  - set 1: VeraTherm 500's thermal resistance rating of 4.5 m²K/W meets the policy requirement of at least 4.0 m²K/W.
- `m_0517` (B4) [policy `p_c5b9`] <= (`e_aef9`); gold after update: **keep**
  - set 1: Solaris Prime's peak conversion efficiency of 98 percent satisfies the policy threshold of 95 percent or higher.
- `u_5597` retracts `e_3413` (reliability low)
- decoy policies: `p_234e`, `p_0dd6`
- final state after updates (gold action -> state): `m_cf41` uncertain -> undetermined; `m_6b8e` keep -> holds; `m_0517` keep -> holds; `m_96ef` uncertain -> undetermined; `m_3290` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_3413~p_2cc1` policy_echoes_evidence: "acoustic output level" (judge under C7/C11)
- soft `e_0b1d~p_b238` policy_echoes_evidence: "thermal resistance rating" (judge under C7/C11)
- soft `e_b97e~p_8c4d` policy_echoes_evidence: "an emergency reserve; emergency reserve power; power duration of; reserve power duration" (judge under C7/C11)
- soft `e_aef9~p_c5b9` policy_echoes_evidence: "peak conversion efficiency" (judge under C7/C11)
- soft `u_5597` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_87d114947a  (F6-005, travel logistics)

*World:* AeroVanguard Logistics and BlueSky Express are evaluated for travel service designations based on fleet numbers and flight performance.

### A. System view (judge C7 from this alone)
- `e_7eaa` [2026-01-08, Transport Licensing Authority official vehicle registry statement.] AeroVanguard Logistics maintains an active fleet size of 15 coaches.
- `e_0804` [2026-01-11, Aviation Analytics quarterly performance ledger.] BlueSky Express recorded an on-time arrival rate of 98 percent this quarter.
- memories:
  - `m_0bed` AeroVanguard Logistics meets high-capacity transport operator criteria.
  - `m_7aa7` AeroVanguard Logistics is designated as the preferred ground operator for the summit.
  - `m_c44a` BlueSky Express earns premier flight punctuality recognition.
- update `u_5c8f` [2026-01-14, Unverified post on an anonymous travel message board.] An anonymous comment alleges AeroVanguard Logistics operates no coaches.
- policies:
  - `p_43ca` Maritime charter endorsement requires a vessel safety inspection score of at least 90 points annually.
  - `p_0203` Premier punctuality distinction requires an on-time arrival rate of 95 percent or higher this quarter.
  - `p_ce99` High-capacity carrier classification is granted when a firm maintains a fleet size of at least 10 coaches.
  - `p_b2ab` Freight forwarding certification is granted to air cargo handlers maintaining a minimum warehouse storage area of 50,000 square feet.
  - `p_4932` An operator with high-capacity carrier classification is chosen as preferred event transport.

### B. Intended structure
- `m_0bed` (B1) [policy `p_ce99`] <= (`e_7eaa`); gold after update: **uncertain**
  - set 1: AeroVanguard Logistics maintains a fleet size of 15 coaches, satisfying the requirement of at least 10 coaches for high-capacity carrier classification.
- `m_7aa7` (D1) [policy `p_4932`] <= (`m_0bed`); gold after update: **uncertain**
  - set 1: AeroVanguard Logistics holds high-capacity carrier classification, qualifying it as preferred event transport.
- `m_c44a` (B2) [policy `p_0203`] <= (`e_0804`); gold after update: **keep**
  - set 1: BlueSky Express achieved an on-time arrival rate of 98 percent this quarter, meeting the threshold of 95 percent for premier punctuality distinction.
- `u_5c8f` retracts `e_7eaa` (reliability low)
- decoy policies: `p_b2ab`, `p_43ca`
- final state after updates (gold action -> state): `m_0bed` uncertain -> undetermined; `m_c44a` keep -> holds; `m_7aa7` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_7eaa~p_ce99` policy_echoes_evidence: "fleet size of" (judge under C7/C11)
- soft `e_0804~p_0203` policy_echoes_evidence: "an on-time arrival; arrival rate of; on-time arrival rate" (judge under C7/C11)
- soft `u_5c8f` retraction_reads_as_hedge: "alleges" (judge under C4)

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

## s_b89d0430a7  (F6-007, travel logistics)

*World:* Travel logistics operations are being reviewed to select charter carriers, ferry providers, and land transit contractors.

### A. System view (judge C7 from this alone)
- `e_30d2` [2026-01-08, Official IATA registry database export.] Vanguard Air Charter maintains an active IATA ground handling certification.
- `e_ad50` [2026-01-11, Maritime Coastguard Agency official fleet register.] BlueWave Ferries operates 12 passenger vessels in its active fleet.
- `e_7288` [2026-01-14, Quarterly transport authority compliance summary.] Summit Overland logged 150000 completed passenger trips this quarter.
- memories:
  - `m_3c17` Summit Overland achieves preferred land transport vendor status.
  - `m_7c6f` BlueWave Ferries meets standard maritime transit volume requirements.
  - `m_5d65` Vanguard Air Charter satisfies international airfield safety standards.
  - `m_7d81` Reserve Vanguard Air Charter for the European executive transport contract.
  - `m_886f` Vanguard Air Charter is approved for priority runway access.
- update `u_c874` [2026-01-17, Anonymous message on an aviation discussion forum.] An unverified forum post claims that Vanguard Air Charter had its IATA ground handling certification revoked.
- policies:
  - `p_25d6` A charter firm with expedited flight scheduling should be selected for high-priority corporate flight bookings.
  - `p_3c91` A rail freight provider qualifies for green logistics certification if at least 80 percent of its locomotives utilize electric propulsion.
  - `p_28cd` Cargo handlers receive expedited customs clearance when maintaining an annual error rate below 1 percent on waybills.
  - `p_9a41` Ground safety compliance is recognized for any carrier holding an active IATA ground handling certification.
  - `p_6f11` A regional ferry operator fulfills transport capacity benchmarks provided it maintains a fleet of at least 10 passenger vessels.
  - `p_882f` Expedited flight scheduling is granted to any air operator with confirmed ground safety compliance.
  - `p_7ba6` A ground transit service earns high-tier operator status when achieving a minimum volume of 100000 passenger trips in a quarterly period.

### B. Intended structure
- `m_5d65` (B1) [policy `p_9a41`] <= (`e_30d2`); gold after update: **uncertain**
  - set 1: Vanguard Air Charter holds an active IATA ground handling certification, satisfying the policy requirement for ground safety compliance.
- `m_886f` (B2) [policy `p_882f`] <= (`m_5d65`); gold after update: **uncertain**
  - set 1: Vanguard Air Charter meets ground safety compliance requirements, which qualifies it for expedited flight scheduling under the policy.
- `m_7d81` (D1) [policy `p_25d6`] <= (`m_886f`); gold after update: **uncertain**
  - set 1: Vanguard Air Charter possesses expedited flight scheduling, satisfying the policy requirement for high-priority corporate flight bookings.
- `m_7c6f` (B3) [policy `p_6f11`] <= (`e_ad50`); gold after update: **keep**
  - set 1: BlueWave Ferries operates 12 passenger vessels, exceeding the policy threshold of 10 vessels for regional transport capacity benchmarks.
- `m_3c17` (B4) [policy `p_7ba6`] <= (`e_7288`); gold after update: **keep**
  - set 1: Summit Overland logged 150000 quarterly passenger trips, exceeding the policy requirement of 100000 trips for high-tier operator status.
- `u_c874` retracts `e_30d2` (reliability low)
- decoy policies: `p_3c91`, `p_28cd`
- final state after updates (gold action -> state): `m_5d65` uncertain -> undetermined; `m_7c6f` keep -> holds; `m_3c17` keep -> holds; `m_886f` uncertain -> undetermined; `m_7d81` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_30d2~p_9a41` policy_echoes_evidence: "ground handling certification" (judge under C7/C11)
- soft `u_c874` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_5db5faefb1  (F6-008, product eligibility)

*World:* An assistant evaluates product compliance and authorization for commercial fleet inclusion and market listing.

### A. System view (judge C7 from this alone)
- `e_ed95` [2026-01-08, Certified lab report from ElectroTest Laboratories on January 7, 2026.] Solaris PowerPack 500 holds an IP67 waterproof certification.
- `e_b99d` [2026-01-11, Official test certificate issued by Aviation Standards Authority on January 10, 2026.] AeroGlide X1 achieved an obstacle avoidance efficiency rating of 98% in official testing.
- memories:
  - `m_7e90` Solaris PowerPack 500 meets outdoor environmental durability standards.
  - `m_5eea` AeroGlide X1 qualifies for urban airspace operation.
  - `m_5f6f` AeroGlide X1 complies with autonomous flight safety requirements.
  - `m_0fba` AeroGlide X1 will be listed in the commercial drone registry.
- update `u_daf2` [2026-01-14, Formal audit notification from the Civil Aviation Audit Office.] An audit by regulatory inspectors questioned whether AeroGlide X1 achieved an obstacle avoidance efficiency rating of 98%, citing sensor calibration concerns.
- policies:
  - `p_3c06` Hospital equipment accreditation is assigned to medical devices that maintain an operational failure rate below 0.1% per year.
  - `p_2983` Authorization for flight in populated areas is issued to an aircraft that has satisfied safety conditions for autonomous piloting.
  - `p_2c1a` Autonomous flight safety clearance is granted when an uncrewed aircraft attains an obstacle avoidance efficiency rating of at least 95%.
  - `p_5847` Green tech rebate eligibility is extended to energy systems with an annual energy conversion efficiency of at least 90%.
  - `p_4660` Inclusion in the municipal fleet catalog requires that an uncrewed vehicle is approved for flights within populated areas.
  - `p_4fcc` Exterior ruggedness approval is conferred if an energy module possesses an IP67 waterproof certification.

### B. Intended structure
- `m_5f6f` (B1) [policy `p_2c1a`] <= (`e_b99d`); gold after update: **uncertain**
  - set 1: AeroGlide X1 achieved an obstacle avoidance efficiency rating of 98%, which satisfies the minimum threshold of 95% required for autonomous flight safety clearance.
- `m_5eea` (B2) [policy `p_2983`] <= (`m_5f6f`); gold after update: **uncertain**
  - set 1: AeroGlide X1 complies with autonomous flight safety requirements, meeting the standard for urban flight authorization.
- `m_0fba` (D1) [policy `p_4660`] <= (`m_5eea`); gold after update: **uncertain**
  - set 1: AeroGlide X1 qualifies for urban airspace operation, fulfilling the requirement for listing in the municipal fleet catalog.
- `m_7e90` (B3) [policy `p_4fcc`] <= (`e_ed95`); gold after update: **keep**
  - set 1: Solaris PowerPack 500 holds an IP67 waterproof certification, which satisfies the condition for exterior ruggedness approval.
- `u_daf2` hedges `e_b99d` (reliability high)
- decoy policies: `p_5847`, `p_3c06`
- final state after updates (gold action -> state): `m_5f6f` uncertain -> undetermined; `m_7e90` keep -> holds; `m_5eea` uncertain -> undetermined; `m_0fba` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_b99d~p_2c1a` policy_echoes_evidence: "an obstacle avoidance; avoidance efficiency rating; efficiency rating of; obstacle avoidance efficiency" (judge under C7/C11)

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
