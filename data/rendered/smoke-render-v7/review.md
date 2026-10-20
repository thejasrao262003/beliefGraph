# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* An assistant evaluates vendor qualifications and product compliance statuses for municipal energy contracts and healthcare regulation.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Peak Energy signed customer service contract] Peak Energy Solutions guarantees a technical support response time under 2 hours.
- `e_94fc` [2026-01-11, FDA official registration database] Zenith Healthcare holds an active Class II medical device permit.
- `e_0439` [2026-01-14, International Accreditation Forum database] Peak Energy Solutions maintains an active ISO 9001 quality certificate.
- `e_b5f7` [2026-01-17, Peak Energy official warranty terms document] Peak Energy Solutions maintains a standard warranty coverage period of 24 months for commercial batteries.
- `e_df05` [2026-01-20, National Safety Inspectorate quarterly report] Peak Energy Solutions recorded zero major safety incidents during the previous 3 years.
- memories:
  - `m_c4d7` Peak Energy Solutions earns premier vendor designation.
  - `m_3f2d` Peak Energy Solutions secures initial supplier status.
  - `m_280b` Zenith Healthcare maintains valid regulatory manufacturing authorization.
  - `m_c5de` Peak Energy Solutions satisfies foundational service agreement guidelines.
  - `m_5302` Peak Energy Solutions clears preferred partner requirements.
  - `m_4b85` Award Peak Energy Solutions the primary supply contract for municipal grid storage.
- update `u_91ee` [2026-01-23, Peak Energy updated warranty policy statement] Peak Energy Solutions reduced its standard warranty coverage period to 6 months.
- policies:
  - `p_fe1d` Initial vendor accreditation is granted to any enterprise that fulfills service agreement parameters.
  - `p_5cd1` Preferred partner status is attained by a provider holding premier supplier classification that reports zero major safety incidents over 3 years.
  - `p_fbe6` Execution of a primary municipal power agreement requires a vendor with preferred partner status.
  - `p_b0aa` Regulatory production compliance is confirmed when an enterprise holds an active Class II medical device permit.
  - `p_1714` Premier supplier classification is conferred upon an enterprise with initial vendor accreditation that holds a verified ISO 9001 certificate.
  - `p_4f8e` Commercial export clearance is issued when an exporter provides certified shipping manifests alongside international customs approval.
  - `p_0087` Service agreement parameters are fulfilled when a vendor offers product coverage of at least 12 months alongside a technical response timeline under 4 hours.
  - `p_1a46` Tier-one distributor standing is granted to a merchant maintaining minimum annual turnover of $10,000,000 together with regional facility licensure.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Peak Energy Solutions provides 24 months of warranty coverage and a 2-hour technical support response time, meeting the policy requirements of at least 12 months of coverage and under 4 hours response time.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Peak Energy Solutions fulfills service agreement parameters, satisfying the rule for initial vendor accreditation.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Peak Energy Solutions possesses initial vendor accreditation and holds an active ISO 9001 quality certificate, qualifying for premier supplier classification.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Peak Energy Solutions holds premier supplier classification and reports zero major safety incidents over 3 years, fulfilling preferred partner status requirements.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Peak Energy Solutions achieves preferred partner status, meeting the prerequisite for executing a primary municipal power agreement.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Zenith Healthcare holds an active Class II medical device permit, confirming regulatory production compliance.
- `u_91ee` supersedes `e_b5f7` (reliability high)
- decoy policies: `p_1a46`, `p_4f8e`
- final state after updates (gold action -> state): `m_c5de` recompute -> fails; `m_280b` keep -> holds; `m_3f2d` recompute -> fails; `m_c4d7` recompute -> fails; `m_5302` recompute -> fails; `m_4b85` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `m_3f2d` order_cue: "initial" (judge under C7)
- soft `e_94fc~p_b0aa` policy_echoes_evidence: "holds an active; medical device permit" (judge under C7/C11)
- soft `e_df05~p_5cd1` policy_echoes_evidence: "major safety incidents; zero major safety" (judge under C7/C11)

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

*World:* Assessment of medical device and unmanned aerial vehicle qualifications for official distribution registries.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Federal Aviation Authority Flight Testing Ledger] Orion Drone 4 recorded a continuous flight time of 45 minutes during official battery endurance trials.
- `e_dfe6` [2026-01-11, International Standards Organisation Certification Database] The Kestrel 800 device holds an active ISO 13485 medical standard credential.
- `e_e50c` [2026-01-14, Official Quality Assurance Register] Apex Medical logged 1,200 completed safety test audits for the Kestrel 800 device over the preceding year.
- memories:
  - `m_2075` The Kestrel 800 device qualifies for the regional healthcare purchasing catalog.
  - `m_36f2` The Orion Drone 4 meets standard criteria for commercial flight authorization.
  - `m_7743` Inclusion of the Kestrel 800 device in the quarterly vendor index is approved.
- update `u_a152` [2026-01-17, Revised Quality Audit System Log] A re-audit indicates Apex Medical completed only 850 safety test audits for the Kestrel 800 device during the evaluation period.
- update `u_41fa` [2026-01-20, Official Regulatory Accreditation Board Registry] The accreditation authority formally revoked the ISO 13485 credential for the Kestrel 800 device.
- policies:
  - `p_d10e` Medical hardware secures placement in preferred health supply lists through maintaining a minimum annual safety audit count of 1,000 or holding an ISO 13485 credential.
  - `p_8779` Industrial software tools earn enterprise deployment clearance when third-party penetration reports show zero critical vulnerabilities.
  - `p_3b4c` An item is cleared for distribution database indexing provided that medical hardware secures placement in preferred health supply lists.
  - `p_4091` Unmanned aerial vehicles achieve commercial operation readiness provided their certified battery endurance reaches at least 30 minutes.
  - `p_e525` Consumer electronic goods obtain standard eco-label recognition if total plastic content contains at least 50 percent recycled material.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: The Kestrel 800 device has 1,200 completed safety test audits, satisfying the requirement of at least 1,000 audits to secure placement in preferred health supply lists.
  - set 2: The Kestrel 800 device holds an active ISO 13485 credential, meeting the alternative condition for securing placement in preferred health supply lists.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: Because the Kestrel 800 device secures placement in preferred health supply lists under B1, it qualifies for clearance in distribution database indexing.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: The Orion Drone 4 demonstrated 45 minutes of battery endurance, exceeding the 30-minute threshold required for commercial operation readiness.
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

*World:* Evaluation of product eligibility and catalog inclusion across several commercial manufacturing sectors.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, ISO central registry certificate verification portal] Apex Medical Corp maintains active ISO 13485 quality management certification.
- `e_5dd0` [2026-01-11, US FDA official clearance database] BioGlow Diagnostic Kit secured US FDA 510(k) clearance in December.
- `e_0823` [2026-01-14, National Renewable Energy Laboratory test report] Vortex Solar Inc's Helios Panel achieved a solar cell efficiency rating of 24%.
- `e_45ef` [2026-01-17, Signed liability policy binder from Hartford Insurance] Apex Medical Corp carries product liability insurance coverage of $5 million.
- `e_fdcd` [2026-01-20, USDA Organic certification audit report] Zenith Foods' PureOat Cereal contains certified organic ingredient content of 95%.
- `e_f882` [2026-01-23, National Highway Traffic Safety Administration crash report] Crestline Automotive's E-Track Scooter completed structural crash safety testing with a 5-star score.
- `e_660f` [2026-01-26, European Medicines Agency official database entry] BioGlow Diagnostic Kit received European CE mark certification last month.
- memories:
  - `m_6c9c` BioGlow Diagnostic Kit has obtained distribution authorization.
  - `m_cc95` BioGlow Diagnostic Kit is selected for the preferred vendor inventory.
  - `m_ece3` E-Track Scooter is permitted for civic commuter networks.
  - `m_e062` BioGlow Diagnostic Kit fulfills global release standards.
  - `m_bda8` Helios Panel is eligible for clean power subsidies.
  - `m_6d1e` PureOat Cereal meets natural food standards.
- update `u_99cf` [2026-01-29, Anonymous post on a medical devices discussion forum] European CE mark certification for BioGlow Diagnostic Kit was never issued.
- policies:
  - `p_cd31` An item cleared for commercial distribution satisfies international commercial readiness provided the producer maintains active ISO 13485 quality management certification.
  - `p_b65d` A product satisfying international commercial readiness is eligible for inclusion in the corporate buying registry if indemnity coverage reaches at least $5 million.
  - `p_b3f6` Packaged foodstuffs achieve natural rating status provided organic ingredient proportion is no less than 90%.
  - `p_6aef` Photovoltaic equipment receives sustainable energy incentive funding when panel efficiency equals or exceeds 22%.
  - `p_d3ca` Heavy machinery obtains site safety clearance provided operational noise levels remain under 80 decibels.
  - `p_8aeb` A medical device gains commercial distribution clearance either via European CE mark certification or through US FDA 510(k) clearance.
  - `p_c629` Cold storage units receive pharmaceutical storage compliance if internal temperature stability is maintained within 2 to 8 degrees Celsius.
  - `p_9e3e` Light mobility vehicles earn municipal transit clearance if crash safety evaluation scores reach 5 stars.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Having obtained European CE mark certification satisfies the condition for commercial distribution clearance.
  - set 2: Holding US FDA 510(k) clearance independently fulfills the condition for commercial distribution clearance.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: BioGlow Diagnostic Kit has distribution clearance, and Apex Medical Corp holds active ISO 13485 certification, satisfying the requirements for international commercial readiness.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: BioGlow Diagnostic Kit meets international commercial readiness standards and Apex Medical Corp carries $5 million in liability coverage, qualifying it for inclusion in the buying registry.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: A panel efficiency of 24% exceeds the required 22% threshold for sustainable energy incentive funding.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: An organic content level of 95% satisfies the 90% minimum threshold required for natural rating status.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: A crash test score of 5 stars satisfies the requirement for municipal transit clearance.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_3dc4~p_cd31` policy_echoes_evidence: "quality management certification" (judge under C7/C11)

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
