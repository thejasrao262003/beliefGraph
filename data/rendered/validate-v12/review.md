# Renderer review sheet

## s_8e620b415c  (F1-001, travel logistics)

*World:* Assessment of transport operator safety standards, bidding qualifications, and service authorizations across regional travel logistics networks.

### A. System view (judge C7 from this alone)
- `e_a2a1` [2026-01-08, Official permit record from the Regional Transport Department on January 8, 2026.] Summit Alpine Shuttles possesses a winter road operation licence.
- `e_a118` [2026-01-11, Official audit certificate issued by the National Transit Authority on January 11, 2026.] Meridian Charters maintained a vehicle fleet safety inspection pass rate of 98 percent last year nationally.
- `e_9a33` [2026-01-14, Verified financial filing from City Commerce Bank on January 14, 2026.] Meridian Charters submitted performance bonding coverage of $5,000,000.
- `e_ef3b` [2026-01-17, Certified annual record from the Transport Regulatory Board on January 17, 2026.] Meridian Charters logged 12 driver safety training sessions this year.
- `e_d5cd` [2026-01-20, Quarterly operational log published by the Rail Logistics Oversight Committee on January 20, 2026.] Pacific Rail Express maintains an on-time arrival rate of 92 percent this quarter.
- memories:
  - `m_8991` Meridian Charters holds preferred passenger carrier designation.
  - `m_0a0a` Meridian Charters maintains premier transit safety compliance.
  - `m_3fc5` Pacific Rail Express fulfills priority cargo dispatch standards.
  - `m_4eee` Award the regional school route contract to Meridian Charters.
  - `m_693b` Summit Alpine Shuttles operates as an authorized mountain route vendor.
  - `m_1283` Meridian Charters qualifies for municipal transit contract bidding.
- update `u_2fc0` [2026-01-23, Official revocation bulletin from the National Transit Authority on January 23, 2026.] The National Transit Authority issued a formal revocation notice stating that Meridian Charters did not maintain a vehicle fleet safety inspection pass rate of 98 percent last year nationally.
- policies:
  - `p_d1ab` A carrier receives preferred transit status when holding top-tier safety compliance.
  - `p_96a1` An agency is eligible for city service procurement upon obtaining preferred transit status.
  - `p_09d3` A shuttle agency gains recognized alpine transport endorsement provided it holds valid cold-season transit authorization.
  - `p_52bf` A railway carrier achieves expedited freight service status by maintaining a quarterly punctuality metric of 90 percent or higher.
  - `p_400f` A car rental company earns eco-fleet certification when electric vehicles represent at least 40 percent of its total inventory.
  - `p_81a0` A transit contract for regional educational transport shall be assigned to an operator eligible for city service procurement that provides performance guarantee indemnity of at least $5,000,000.
  - `p_7632` A maritime charter company obtains deep-sea navigation clearance if it conducts 15 crew emergency drills annually.
  - `p_9918` A transport provider achieves top-tier safety compliance when maintaining an annual vehicle safety inspection rating of at least 95 percent across national operations alongside at least 10 annual driver instruction seminars.

### B. Intended structure
- `m_0a0a` (B1) [policy `p_9918`] <= (`e_a118` AND `e_ef3b`); gold after update: **withdraw**
  - set 1: Meridian Charters meets gold standard transport safety protocols because its 98 percent national vehicle inspection rate satisfies the 95 percent threshold and its 12 driver safety training sessions meet the requirement of 10.
- `m_8991` (B2) [policy `p_d1ab`] <= (`m_0a0a`); gold after update: **withdraw**
  - set 1: Meridian Charters holds preferred passenger carrier designation because it meets gold standard transport safety protocols.
- `m_1283` (B3) [policy `p_96a1`] <= (`m_8991`); gold after update: **withdraw**
  - set 1: Meridian Charters qualifies for municipal transit contract bidding because it holds preferred passenger carrier designation.
- `m_4eee` (D1) [policy `p_81a0`] <= (`m_1283` AND `e_9a33`); gold after update: **withdraw**
  - set 1: Awarding the regional school route contract to Meridian Charters is supported because the company qualifies for municipal transit contract bidding and provides $5,000,000 in performance bonding coverage.
- `m_3fc5` (B4) [policy `p_52bf`] <= (`e_d5cd`); gold after update: **keep**
  - set 1: Pacific Rail Express fulfills priority cargo dispatch standards because its quarterly on-time arrival rate of 92 percent meets the 90 percent requirement.
- `m_693b` (B5) [policy `p_09d3`] <= (`e_a2a1`); gold after update: **keep**
  - set 1: Summit Alpine Shuttles operates as an authorized mountain route vendor because it holds a winter road operation licence.
- `u_2fc0` retracts `e_a118` (reliability high)
- decoy policies: `p_7632`, `p_400f`
- final state after updates (gold action -> state): `m_0a0a` withdraw -> fails; `m_3fc5` keep -> holds; `m_693b` keep -> holds; `m_8991` withdraw -> fails; `m_1283` withdraw -> fails; `m_4eee` withdraw -> fails

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

## s_23a31467bd  (F1-002, product eligibility)

*World:* Product eligibility evaluations for industrial equipment, renewable energy modules, and medical devices.

### A. System view (judge C7 from this alone)
- `e_38fc` [2026-01-08, Environmental Chamber Test Report] Vortex Pro Drone demonstrated a minimum operating temperature of 20 degrees Celsius.
- `e_2798` [2026-01-11, National Renewable Energy Test Bench] Helios Solar Panel produced an annual energy output of 450 kilowatt-hours.
- `e_935b` [2026-01-14, International Ingress Protection Registry] Vortex Pro Drone holds an IP67 dust and water resistance certification.
- `e_b958` [2026-01-17, Annual Flight Operations Audit] Vortex Pro Drone completed 150 successful automated test flights this year.
- `e_3517` [2026-01-20, Manufacturer Product Specification Sheet] Vortex Pro Drone carries a payload capacity of 12 kilograms.
- `e_1d0f` [2026-01-23, Flight Testing Log, Engineering Department] Vortex Pro Drone achieved a flight time of 45 minutes on a standard battery charge.
- `e_7cfc` [2026-01-26, FDA Regulatory Database] Apex Medical Kit holds FDA Class II clearance.
- memories:
  - `m_ef84` Vortex Pro Drone earns extreme climate qualification.
  - `m_3d37` Vortex Pro Drone qualifies for commercial field operations.
  - `m_6714` Apex Medical Kit is approved for clinical distribution.
  - `m_5e55` Vortex Pro Drone is classified as a heavy-duty cargo transport unit.
  - `m_85a4` Recommend Vortex Pro Drone for government infrastructure contract bidding.
  - `m_8313` Helios Solar Panel satisfies high-efficiency performance criteria.
  - `m_500e` Vortex Pro Drone achieves elite fleet status.
- update `u_474b` [2026-01-29, Independent Quality Oversight Board] A formal audit confirmed that Vortex Pro Drone did not achieve a flight time of 45 minutes on a standard battery charge.
- policies:
  - `p_d26b` An equipment unit receives premier fleet standing when it holds heavy freight designation and completes no fewer than 100 annual autonomous trial runs.
  - `p_164c` A consumer appliance receives energy star endorsement provided its standby power consumption remains below 0.5 watts.
  - `p_cd8a` An electronic component obtains marine environment authorization if it survives 500 hours of salt spray exposure.
  - `p_45da` An industrial unit gains commercial operational clearance when it achieves an endurance threshold of 40 minutes on battery power while maintaining a certified ingress protection rating of IP67.
  - `p_a3be` A photovoltaic module reaches top tier efficiency standing if its yearly energy output equals or exceeds 400 kilowatt-hours.
  - `p_28c3` A product is designated for public sector procurement inclusion provided it maintains premier fleet standing.
  - `p_0509` A device verified for extreme climate conditions earns heavy freight designation if its carrying capacity reaches at least 10 kilograms.
  - `p_5a8f` A medical package is authorized for healthcare supply channels once it possesses FDA Class II clearance.
  - `p_145c` An equipment unit achieves extreme climate validation provided it holds commercial operational clearance and maintains a cold operating threshold of 25 degrees Celsius or lower.

### B. Intended structure
- `m_3d37` (B1) [policy `p_45da`] <= (`e_1d0f` AND `e_935b`); gold after update: **withdraw**
  - set 1: Vortex Pro Drone meets the commercial operational clearance criteria because its flight time of 45 minutes exceeds 40 minutes and it possesses IP67 dust and water resistance certification.
- `m_ef84` (B2) [policy `p_145c`] <= (`m_3d37` AND `e_38fc`); gold after update: **withdraw**
  - set 1: Vortex Pro Drone qualifies for extreme climate validation because it holds commercial operational clearance and its minimum operating temperature of -20 degrees Celsius is at or below -15 degrees Celsius.
- `m_5e55` (B3) [policy `p_0509`] <= (`m_ef84` AND `e_3517`); gold after update: **withdraw**
  - set 1: Vortex Pro Drone receives heavy freight designation because it has extreme climate validation and its payload capacity of 12 kilograms meets the 10 kilogram threshold.
- `m_500e` (B4) [policy `p_d26b`] <= (`m_5e55` AND `e_b958`); gold after update: **withdraw**
  - set 1: Vortex Pro Drone attains premier fleet standing because it holds heavy freight designation and its 150 annual automated test flights satisfy the 100 flight requirement.
- `m_85a4` (D1) [policy `p_28c3`] <= (`m_500e`); gold after update: **withdraw**
  - set 1: Vortex Pro Drone is approved for public sector procurement inclusion because it holds premier fleet standing.
- `m_8313` (B5) [policy `p_a3be`] <= (`e_2798`); gold after update: **keep**
  - set 1: Helios Solar Panel reaches top tier efficiency standing because its annual energy output of 450 kilowatt-hours exceeds the 400 kilowatt-hour requirement.
- `m_6714` (B6) [policy `p_5a8f`] <= (`e_7cfc`); gold after update: **keep**
  - set 1: Apex Medical Kit is authorized for healthcare supply channels because it holds FDA Class II clearance.
- `u_474b` retracts `e_1d0f` (reliability high)
- decoy policies: `p_cd8a`, `p_164c`
- final state after updates (gold action -> state): `m_3d37` withdraw -> fails; `m_8313` keep -> holds; `m_6714` keep -> holds; `m_ef84` withdraw -> fails; `m_5e55` withdraw -> fails; `m_500e` withdraw -> fails; `m_85a4` withdraw -> fails

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

## s_f0bd308356  (F1-004, product eligibility)

*World:* Assessment of commercial product eligibility and regulatory compliance across three distinct hardware product lines.

### A. System view (judge C7 from this alone)
- `e_3c6e` [2026-01-08, Signed laboratory test certificate from Energy Analytics Institute.] Titan Battery Pack demonstrated an energy density of 280 Wh/kg.
- `e_8872` [2026-01-11, Official European Conformity registry database entry.] AeroGlide Scooter holds an active European Conformity certificate.
- `e_07ec` [2026-01-14, Official test results from the National Safety Testing Laboratory.] AeroGlide Scooter recorded a top speed of 25 km/h during safety testing.
- `e_f394` [2026-01-17, Annual audit report signed by Quality Management Services.] Lumina Medical Monitor completed 12 quality control audits this year.
- memories:
  - `m_0ae4` Titan Battery Pack qualifies for commercial transport clearance.
  - `m_017e` Lumina Medical Monitor maintains ISO 13485 compliance status.
  - `m_0e02` AeroGlide Scooter is approved for urban retail distribution.
- update `u_b601` [2026-01-20, Official follow-up audit report from the National Safety Testing Laboratory.] An official re-test showed AeroGlide Scooter achieved a top speed of 38 km/h.
- policies:
  - `p_b478` A personal protection garment achieves heavy-duty classification when its tear resistance measures at least 150 Newtons.
  - `p_c4e4` An industrial lubricant gets environmental certification if its biodegradable fraction exceeds 85 percent.
  - `p_07b3` A healthcare instrument secures ISO 13485 regulatory certification if it undergoes a minimum of 10 quality control audits per year.
  - `p_e9e1` An energy storage product earns approval for freight transport provided its energy concentration reaches at least 250 Wh/kg.
  - `p_9039` An electric mobility device receives authorization for city retail sales when its maximum velocity does not exceed 30 km/h alongside an active European Conformity certificate.

### B. Intended structure
- `m_0e02` (D1) [policy `p_9039`] <= (`e_07ec` AND `e_8872`); gold after update: **recompute**
  - set 1: AeroGlide Scooter satisfies the policy by having a top speed of 25 km/h, which is within the 30 km/h maximum limit, and maintaining an active European Conformity certificate.
- `m_0ae4` (B1) [policy `p_e9e1`] <= (`e_3c6e`); gold after update: **keep**
  - set 1: Titan Battery Pack fulfills the rule by demonstrating an energy density of 280 Wh/kg, exceeding the required threshold of 250 Wh/kg.
- `m_017e` (B2) [policy `p_07b3`] <= (`e_f394`); gold after update: **keep**
  - set 1: Lumina Medical Monitor meets the policy condition by completing 12 quality control audits this year, surpassing the required minimum of 10.
- `u_b601` supersedes `e_07ec` (reliability high)
- decoy policies: `p_b478`, `p_c4e4`
- final state after updates (gold action -> state): `m_0e02` recompute -> fails; `m_0ae4` keep -> holds; `m_017e` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_f394~p_07b3` policy_echoes_evidence: "quality control audits" (judge under C7/C11)

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

## s_6d772a8094  (F1-008, product eligibility)

*World:* An evaluation assistant assesses product eligibility and cataloging classifications across various hardware lines based on technical test results and certifications.

### A. System view (judge C7 from this alone)
- `e_9eee` [2026-01-08, Electrical Safety Compliance Audit, published January 8, 2026] Solis Solar Panel Kit holds an IP67 weatherproof rating.
- `e_8e3f` [2026-01-11, Defense Testing Bureau Registry, logged January 11, 2026] Apex Drone Model X1 maintains an encrypted transmission distance of 15 kilometers.
- `e_ad4f` [2026-01-14, Official Manufacturer Specification Sheet, updated January 14, 2026] Apex Drone Model X1 has an operational flight ceiling of 4,500 meters.
- `e_f0c0` [2026-01-17, National Sanitation Foundation Certificate, issued January 17, 2026] BioPure Water Filter produces a daily purified volume of 800 liters.
- `e_ba0f` [2026-01-20, Transport Certification Agency Report, logged January 20, 2026] AeroGlide Electric Scooter has a peak motor output of 750 watts.
- memories:
  - `m_f723` Apex Drone Model X1 is rated for high-altitude flight operations.
  - `m_7a10` AeroGlide Electric Scooter qualifies as a heavy-duty commuter vehicle.
  - `m_d4f6` Solis Solar Panel Kit is designated for outdoor installation.
  - `m_6e73` Apex Drone Model X1 satisfies extreme climate durability requirements.
  - `m_313d` BioPure Water Filter earns eco-label certification.
  - `m_6394` Include Apex Drone Model X1 in the high-altitude surveillance procurement catalog.
  - `m_9b5a` Apex Drone Model X1 qualifies for severe weather operational clearance.
  - `m_0843` Apex Drone Model X1 meets specialized defense deployment standards.
- update `u_8a0a` [2026-01-23, Revised Flight Test Registry, issued January 23, 2026] Apex Drone Model X1 has an operational flight ceiling of 3,200 meters.
- policies:
  - `p_76e4` Aerial equipment achieves high-altitude rating when its maximum service ceiling reaches or exceeds 4,000 meters.
  - `p_e66e` Cataloging for remote surveillance programs requires defense deployment status along with a transmission distance of at least 10 kilometers.
  - `p_efa8` A filtration unit gains eco-certification if its daily purified volume reaches 500 liters or more.
  - `p_4f49` A vehicle receives extreme climate designation provided it has an approved high-altitude rating.
  - `p_e4c1` Severe weather clearance is granted to hardware demonstrating extreme climate designation.
  - `p_fed6` Solar hardware is approved for exterior deployment provided it possesses an IP67 weatherproof rating.
  - `p_6ee3` An item secures defense deployment status if it holds severe weather clearance.
  - `p_fb29` Personal mobility devices qualify for heavy-duty commuter classification when peak motor output is at least 500 watts.
  - `p_aeef` Commercial transport trailers are granted priority logistics routing when maximum payload capacity exceeds 10,000 kilograms.
  - `p_5ebc` Industrial heat pumps receive energy efficiency endorsement if seasonal performance factor is at least 4.0.

### B. Intended structure
- `m_f723` (B1) [policy `p_76e4`] <= (`e_ad4f`); gold after update: **recompute**
  - set 1: Apex Drone Model X1 has a flight ceiling of 4,500 meters, meeting the 4,000-meter minimum threshold for high-altitude rating.
- `m_6e73` (B2) [policy `p_4f49`] <= (`m_f723`); gold after update: **recompute**
  - set 1: Apex Drone Model X1 holds a high-altitude rating, fulfilling the requirement for extreme climate designation.
- `m_9b5a` (B3) [policy `p_e4c1`] <= (`m_6e73`); gold after update: **recompute**
  - set 1: Apex Drone Model X1 possesses extreme climate designation, satisfying the prerequisite for severe weather clearance.
- `m_0843` (B4) [policy `p_6ee3`] <= (`m_9b5a`); gold after update: **recompute**
  - set 1: Apex Drone Model X1 maintains severe weather clearance, qualifying it for defense deployment status.
- `m_6394` (D1) [policy `p_e66e`] <= (`m_0843` AND `e_8e3f`); gold after update: **recompute**
  - set 1: Apex Drone Model X1 holds defense deployment status and has a transmission distance of 15 kilometers, satisfying both prerequisites for cataloging.
- `m_313d` (B5) [policy `p_efa8`] <= (`e_f0c0`); gold after update: **keep**
  - set 1: BioPure Water Filter yields a daily purified volume of 800 liters, exceeding the 500-liter requirement for eco-certification.
- `m_d4f6` (B6) [policy `p_fed6`] <= (`e_9eee`); gold after update: **keep**
  - set 1: Solis Solar Panel Kit maintains an IP67 weatherproof rating, satisfying the credential needed for outdoor installation.
- `m_7a10` (B7) [policy `p_fb29`] <= (`e_ba0f`); gold after update: **keep**
  - set 1: AeroGlide Electric Scooter features a peak motor output of 750 watts, exceeding the 500-watt requirement for heavy-duty commuter status.
- `u_8a0a` supersedes `e_ad4f` (reliability high)
- decoy policies: `p_aeef`, `p_5ebc`
- final state after updates (gold action -> state): `m_f723` recompute -> fails; `m_313d` keep -> holds; `m_d4f6` keep -> holds; `m_7a10` keep -> holds; `m_6e73` recompute -> fails; `m_9b5a` recompute -> fails; `m_0843` recompute -> fails; `m_6394` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_8e3f~p_e66e` policy_echoes_evidence: "transmission distance of" (judge under C7/C11)
- soft `e_f0c0~p_efa8` policy_echoes_evidence: "daily purified volume" (judge under C7/C11)
- soft `e_ba0f~p_fb29` policy_echoes_evidence: "peak motor output" (judge under C7/C11)

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

## s_5b4d5b6b6d  (F2-000, product eligibility)

*World:* Assessment of commercial equipment eligibility for utility programs and municipal rebate registration.

### A. System view (judge C7 from this alone)
- `e_0292` [2026-01-08, Acoustic Testing Labs certified noise report dated January 7, 2026.] Titan HVAC Unit emitted an acoustic sound level of 48 dB.
- `e_c342` [2026-01-11, Pressure Systems Safety Audit report dated January 10, 2026.] Titan HVAC Unit features a maximum operating pressure rating of 450 PSI.
- `e_7b3c` [2026-01-14, Airflow Dynamics inspection certificate dated January 13, 2026.] Titan HVAC Unit delivered a volumetric airflow rate of 2400 CFM.
- `e_6a14` [2026-01-17, AHRI directory database listing dated January 16, 2026.] Titan HVAC Unit holds an active AHRI accreditation.
- `e_e636` [2026-01-20, Titan Climate Systems product specification sheet dated January 19, 2026.] Titan HVAC Unit carries a warranty duration of 10 years.
- `e_9d52` [2026-01-23, Titan Climate Systems engineering test report dated January 22, 2026.] Titan HVAC Unit demonstrated a seasonal energy efficiency ratio of 22.
- `e_bff1` [2026-01-26, Underwriters Laboratories compliance certificate dated January 25, 2026.] Solis Solar Inverter possesses UL 1741 compliance.
- memories:
  - `m_ce2c` Titan HVAC Unit should be added to the city utility supplier catalog.
  - `m_ee1b` Solis Solar Inverter is permitted for utility grid interconnection.
  - `m_2aab` Titan HVAC Unit holds municipal incentive program eligibility.
  - `m_d191` Titan HVAC Unit is approved for commercial rebate tier status.
- update `u_149a` [2026-01-29, Airflow Dynamics re-inspection report dated January 28, 2026.] A revised audit confirmed Titan HVAC Unit delivers a volumetric airflow rate of 1800 CFM.
- update `u_a129` [2026-02-01, Acoustic Testing Labs updated audit report dated January 31, 2026.] An updated measurement established that Titan HVAC Unit emits an acoustic sound level of 56 dB.
- update `u_6f90` [2026-02-04, AHRI directory update notification dated February 3, 2026.] An updated compliance notice stated Titan HVAC Unit no longer holds an active AHRI accreditation.
- update `u_12c8` [2026-02-07, Titan Climate Systems official laboratory re-test record dated February 6, 2026.] A re-testing certificate verified Titan HVAC Unit demonstrated a seasonal energy efficiency ratio of 18.
- policies:
  - `p_9e2f` An electric vehicle charger qualifies for fleet grant funding when it delivers a continuous power output of at least 11 kW.
  - `p_0d10` A commercial equipment item granted high-efficiency rebate status becomes eligible for municipal incentive registration provided its manufacturer warranty duration reaches at least 8 years.
  - `p_1ae3` An HVAC system achieves high-efficiency rebate status if it maintains a seasonal energy efficiency ratio of 20 or higher, an acoustic sound level of 50 dB or lower, a volumetric airflow rate of 2000 CFM or above, or an active AHRI accreditation.
  - `p_f839` An equipment model clear for municipal incentive registration is recommended for immediate utility catalog inclusion when rated for maximum operating pressure of 400 PSI or greater.
  - `p_a183` A power conversion unit secures grid connection authorization provided it holds valid UL 1741 compliance.
  - `p_ef5c` A domestic water heater gains energy star clearance if its thermal efficiency score reaches 90 percent or higher.

### B. Intended structure
- `m_d191` (B1) [policy `p_1ae3`] <= (`e_9d52`) **OR** (`e_0292`) **OR** (`e_7b3c`) **OR** (`e_6a14`); gold after update: **recompute**
  - set 1: Titan HVAC Unit achieves high-efficiency rebate status because its seasonal energy efficiency ratio of 22 meets the minimum requirement of 20.
  - set 2: Titan HVAC Unit achieves high-efficiency rebate status because its acoustic sound level of 48 dB is within the maximum limit of 50 dB.
  - set 3: Titan HVAC Unit achieves high-efficiency rebate status because its volumetric airflow rate of 2400 CFM exceeds the threshold of 2000 CFM.
  - set 4: Titan HVAC Unit achieves high-efficiency rebate status because it holds active AHRI accreditation.
- `m_2aab` (B2) [policy `p_0d10`] <= (`m_d191` AND `e_e636`); gold after update: **recompute**
  - set 1: Titan HVAC Unit qualifies for municipal incentive registration because it holds high-efficiency rebate status and its warranty duration of 10 years satisfies the 8-year requirement.
- `m_ce2c` (D1) [policy `p_f839`] <= (`m_2aab` AND `e_c342`); gold after update: **recompute**
  - set 1: Titan HVAC Unit is recommended for utility catalog inclusion because it is eligible for municipal incentive registration and its maximum operating pressure of 450 PSI meets the 400 PSI threshold.
- `m_ee1b` (B3) [policy `p_a183`] <= (`e_bff1`); gold after update: **keep**
  - set 1: Solis Solar Inverter secures grid connection authorization because it possesses valid UL 1741 compliance.
- `u_149a` supersedes `e_7b3c` (reliability high)
- `u_a129` supersedes `e_0292` (reliability high)
- `u_6f90` supersedes `e_6a14` (reliability high)
- `u_12c8` supersedes `e_9d52` (reliability high)
- decoy policies: `p_ef5c`, `p_9e2f`
- final state after updates (gold action -> state): `m_d191` recompute -> fails; `m_ee1b` keep -> holds; `m_2aab` recompute -> fails; `m_ce2c` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `p_1ae3` date_in_policy: "2000-01-01"
- soft `e_0292~p_1ae3` policy_echoes_evidence: "acoustic sound level; an acoustic sound; sound level of" (judge under C7/C11)
- soft `e_c342~p_f839` policy_echoes_evidence: "maximum operating pressure" (judge under C7/C11)
- soft `e_7b3c~p_1ae3` policy_echoes_evidence: "a volumetric airflow; airflow rate of; volumetric airflow rate" (judge under C7/C11)
- soft `e_9d52~p_1ae3` policy_echoes_evidence: "a seasonal energy; efficiency ratio of; energy efficiency ratio; seasonal energy efficiency" (judge under C7/C11)

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

## s_7ebb2988ff  (F2-002, product eligibility)

*World:* The assistant evaluates commercial authorization and operational assignments for unmanned delivery hardware and network equipment.

### A. System view (judge C7 from this alone)
- `e_e5ac` [2026-01-08, AeroGlide Flight Analytics Center] AeroGlide Drone recorded a flight safety evaluation rating of 92 points this quarter.
- `e_6181` [2026-01-11, Underwriters Laboratories Certification Registry] SentryGuard Hub secured an official UL 2900 cybersecurity certification.
- `e_b5f8` [2026-01-14, Federal Communications Commission Licensing Database] AeroGlide Drone possesses an active FCC Class B broadcast permit.
- memories:
  - `m_8975` AeroGlide Drone is selected for regional delivery operations.
  - `m_e40f` AeroGlide Drone qualifies for commercial deployment status.
  - `m_acd2` SentryGuard Hub meets enterprise network insertion standards.
- update `u_3e59` [2026-01-17, AeroGlide Quality Assurance Registry] An official audit memo confirms that AeroGlide Drone never recorded a flight safety evaluation rating of 92 points this quarter.
- policies:
  - `p_4fb3` An industrial power supply obtains heavy utility approval when it demonstrates an operational efficiency score of at least 95 percent over six months.
  - `p_6992` A delivery vehicle is approved for regional distribution tasks provided it has received market deployment authorization.
  - `p_4799` Market deployment authorization is granted to an uncrewed aircraft if it holds an official broadcast permit or achieves a quarterly flight safety evaluation rating of at least 90 points.
  - `p_c476` An IoT hardware platform attains enterprise network clearance upon receiving a UL 2900 cybersecurity certification.
  - `p_3547` A thermal insulation panel gains eco-friendly building compliance if it maintains a heat resistance factor of at least 40 units.

### B. Intended structure
- `m_e40f` (B1) [policy `p_4799`] <= (`e_b5f8`) **OR** (`e_e5ac`); gold after update: **keep**
  - set 1: AeroGlide Drone holds an FCC Class B broadcast permit, which satisfies the broadcast permit requirement for market deployment authorization.
  - set 2: AeroGlide Drone earned a flight safety evaluation rating of 92 points this quarter, meeting the minimum 90 points threshold for market deployment authorization.
- `m_8975` (D1) [policy `p_6992`] <= (`m_e40f`); gold after update: **keep**
  - set 1: AeroGlide Drone has market deployment authorization, fulfilling the requirement for regional distribution task assignment.
- `m_acd2` (B2) [policy `p_c476`] <= (`e_6181`); gold after update: **keep**
  - set 1: SentryGuard Hub secured a UL 2900 cybersecurity certification, satisfying the criterion for enterprise network clearance.
- `u_3e59` retracts `e_e5ac` (reliability high)
- decoy policies: `p_4fb3`, `p_3547`
- final state after updates (gold action -> state): `m_e40f` keep -> holds; `m_acd2` keep -> holds; `m_8975` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_e5ac~p_4799` policy_echoes_evidence: "evaluation rating of; flight safety evaluation; safety evaluation rating" (judge under C7/C11)

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

## s_6ec759a73c  (F2-004, product eligibility)

*World:* Commercial retail qualification and product safety evaluations for technological hardware and equipment.

### A. System view (judge C7 from this alone)
- `e_cee9` [2026-01-08, Federal Communications Laboratory audit dated January 7, 2026.] AeroGlide Drone achieved an electromagnetic compliance score of 95 points.
- `e_2880` [2026-01-11, National Aviation Safety Lab test report dated January 10, 2026.] AeroGlide Drone scored 85 points on the structural impact test.
- `e_1abb` [2026-01-14, Energy Star official product registry entry dated January 13, 2026.] Lumina Smart Lamp holds Energy Star certification.
- `e_eb78` [2026-01-17, AeroGlide Drone commercial warranty statement filed January 16, 2026.] AeroGlide Drone provides a distributor warranty pledge of 3 years.
- `e_0e7d` [2026-01-20, BioPure Filter laboratory verification certificate dated January 19, 2026.] BioPure Filter achieved a pathogen filtration efficiency of 99.9%.
- `e_410c` [2026-01-23, Solaris Power Cell lab test datasheet dated January 22, 2026.] Solaris Power Cell recorded an energy density of 250 Wh/kg.
- `e_24d0` [2026-01-26, Thermal Systems Inspection Office registry dated January 25, 2026.] AeroGlide Drone holds a battery thermal clearance certificate.
- `e_65c5` [2026-01-29, Aerospace Quality Board evaluation dated January 28, 2026.] AeroGlide Drone received a flight stability rating of 90 points.
- memories:
  - `m_9c8f` AeroGlide Drone qualifies for regional retail distribution.
  - `m_69f1` Lumina Smart Lamp is eligible for green rebate enrollment.
  - `m_118a` AeroGlide Drone is sanctioned for release on Apex Retail.
  - `m_8428` BioPure Filter secures clinical grade certification.
  - `m_38d2` AeroGlide Drone maintains commercial safety authorization.
  - `m_6189` Solaris Power Cell earns high-capacity energy designation.
- update `u_4f13` [2026-02-01, Aerospace Quality Board audit summary dated January 31, 2026.] A re-evaluation confirmed AeroGlide Drone received a flight stability rating of 40 points.
- update `u_ef57` [2026-02-04, National Aviation Safety Lab re-inspection report dated February 3, 2026.] A revised collision test showed AeroGlide Drone scored 50 points on the structural impact test.
- update `u_bdef` [2026-02-07, Federal Communications Laboratory audit update dated February 6, 2026.] A calibrated test indicated AeroGlide Drone achieved an electromagnetic compliance score of 60 points.
- update `u_4933` [2026-02-10, Thermal Systems Inspection Office official registry notice dated February 9, 2026.] Thermal Systems Inspection Office announced AeroGlide Drone does not hold a battery thermal clearance certificate.
- policies:
  - `p_6fdc` An item earns commercial safety approval whenever it demonstrates a structural impact score of at least 80 points, a flight stability rating of 80 points or higher, a valid battery thermal clearance certificate, or an electromagnetic compliance score of no less than 80 points.
  - `p_0dcc` A medical equipment unit obtains pediatric clearance if its operating acoustic noise stays below 35 dB.
  - `p_4bc6` An industrial component receives heavy-duty rating if its tensile strength reaches at least 500 MPa.
  - `p_b919` An energy storage unit achieves high-capacity status provided its energy density reaches 200 Wh/kg or higher.
  - `p_0054` An item is eligible for regional store distribution provided it secures commercial safety approval.
  - `p_f635` A filtration device attains clinical rating when its pathogen filtration efficiency is at least 95%.
  - `p_54af` A product gets authorized for listing on Apex Retail if it meets regional store distribution criteria while featuring a distributor warranty pledge of at least 2 years.
  - `p_b39a` A lighting product qualifies for eco rebate program participation if it maintains Energy Star certification.

### B. Intended structure
- `m_38d2` (B1) [policy `p_6fdc`] <= (`e_2880`) **OR** (`e_65c5`) **OR** (`e_24d0`) **OR** (`e_cee9`); gold after update: **recompute**
  - set 1: AeroGlide Drone scored 85 points on the structural impact test, which meets the structural impact score threshold of 80 points.
  - set 2: AeroGlide Drone received a flight stability rating of 90 points, meeting the requirement of at least 80 points.
  - set 3: AeroGlide Drone holds a battery thermal clearance certificate, satisfying the battery thermal clearance condition.
  - set 4: AeroGlide Drone achieved an electromagnetic compliance score of 95 points, which satisfies the required threshold of 80 points.
- `m_9c8f` (B2) [policy `p_0054`] <= (`m_38d2`); gold after update: **recompute**
  - set 1: AeroGlide Drone maintains commercial safety authorization, satisfying the commercial safety approval requirement.
- `m_118a` (D1) [policy `p_54af`] <= (`m_9c8f` AND `e_eb78`); gold after update: **recompute**
  - set 1: AeroGlide Drone qualifies for regional retail distribution and provides a distributor warranty pledge of 3 years, fulfilling both store distribution and warranty criteria.
- `m_6189` (B3) [policy `p_b919`] <= (`e_410c`); gold after update: **keep**
  - set 1: Solaris Power Cell recorded an energy density of 250 Wh/kg, exceeding the threshold of 200 Wh/kg.
- `m_8428` (B4) [policy `p_f635`] <= (`e_0e7d`); gold after update: **keep**
  - set 1: BioPure Filter achieved a pathogen filtration efficiency of 99.9%, meeting the requirement of at least 95%.
- `m_69f1` (B5) [policy `p_b39a`] <= (`e_1abb`); gold after update: **keep**
  - set 1: Lumina Smart Lamp holds Energy Star certification, satisfying the rebate program requirement.
- `u_4f13` supersedes `e_65c5` (reliability high)
- `u_ef57` supersedes `e_2880` (reliability high)
- `u_bdef` supersedes `e_cee9` (reliability high)
- `u_4933` supersedes `e_24d0` (reliability high)
- decoy policies: `p_4bc6`, `p_0dcc`
- final state after updates (gold action -> state): `m_38d2` recompute -> fails; `m_6189` keep -> holds; `m_8428` keep -> holds; `m_69f1` keep -> holds; `m_9c8f` recompute -> fails; `m_118a` recompute -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_cee9~p_6fdc` policy_echoes_evidence: "an electromagnetic compliance; compliance score of; electromagnetic compliance score" (judge under C7/C11)
- soft `e_eb78~p_54af` policy_echoes_evidence: "a distributor warranty; distributor warranty pledge; warranty pledge of" (judge under C7/C11)
- soft `e_0e7d~p_f635` policy_echoes_evidence: "pathogen filtration efficiency" (judge under C7/C11)
- soft `e_24d0~p_6fdc` policy_echoes_evidence: "battery thermal clearance; thermal clearance certificate" (judge under C7/C11)
- soft `e_65c5~p_6fdc` policy_echoes_evidence: "a flight stability; flight stability rating; stability rating of" (judge under C7/C11)

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

## s_c8ff4df286  (F2-009, travel logistics)

*World:* Logistics evaluations and contract allocations are being updated for air, sea, and charter transport partners.

### A. System view (judge C7 from this alone)
- `e_a3ba` [2026-01-08, IATA Member Portal] An official trade record states that AeroExpress Logistics holds IATA Cargo Agent Accreditation.
- `e_cdcc` [2026-01-11, ISO Compliance Database] A compliance certificate indicates that AeroExpress Logistics retains ISO 9001 Quality Certification.
- `e_8e43` [2026-01-14, Civil Aviation Authority registry] Civil aviation logs report that AeroExpress Logistics completed 600 yearly departures.
- `e_2482` [2026-01-17, Quarterly Carrier Performance Report] Performance audits show AeroExpress Logistics registered a quarterly punctuality mark of 96 percent.
- `e_1a72` [2026-01-20, National Aviation Fleet Registry] Fleet registration records show AeroExpress Logistics maintains a fleet size of 18 planes.
- `e_4a07` [2026-01-23, FAA Licensing Directory] Federal aviation records confirm Zenith Air Charter holds an FAA Part 135 Certificate.
- `e_90a1` [2026-01-26, Maritime Transport Authority] Maritime registry filings show Sovereign Maritime commands an active ocean freighter count of 20 vessels.
- memories:
  - `m_8f9d` Route high-value medical shipments through AeroExpress Logistics.
  - `m_7cbe` AeroExpress Logistics secures premier freight classification.
  - `m_a253` AeroExpress Logistics is approved for priority routing.
  - `m_93aa` Zenith Air Charter is cleared for executive flights.
  - `m_960c` Sovereign Maritime qualifies as a heavy cargo operator.
  - `m_94c8` AeroExpress Logistics satisfies preferred carrier credentials.
- update `u_7add` [2026-01-29, IATA Member Portal Bulletin] An official IATA directory update states that AeroExpress Logistics does not hold IATA Cargo Agent Accreditation.
- update `u_b45f` [2026-02-01, ISO Registrar Audit Notice] A formal auditor notice confirms that AeroExpress Logistics does not hold ISO 9001 Quality Certification.
- update `u_4398` [2026-02-04, Civil Aviation Authority Audit] A revised aviation ledger clarifies that AeroExpress Logistics did not complete 600 yearly departures.
- policies:
  - `p_f180` A transport provider obtains top-tier priority status if qualified for expedited dispatch options while sustaining a quarterly punctuality mark of at least 92 percent.
  - `p_cc84` A transport provider achieves preferred logistics status when yearly departures reach at least 500, or when holding IATA Cargo Agent Accreditation, or if fleet size is at least 15, or with ISO 9001 Quality Certification.
  - `p_cc16` High-value pharmaceutical transport should be assigned to any provider holding top-tier priority status.
  - `p_99cd` A warehouse vendor earns elite storage certification if maintaining an annual inventory accuracy threshold of 99 percent.
  - `p_086f` An aviation firm receives passenger charter authorization upon securing an FAA Part 135 Certificate.
  - `p_e5c3` A rail network gains rapid transit authorization when operating at least 50 dedicated locomotives.
  - `p_6f5d` A shipping firm is recognized as a heavy-freight carrier if its ocean freighter count reaches 15 or more.
  - `p_6963` A transport provider qualifies for expedited dispatch options if cleared for preferred logistics status.

### B. Intended structure
- `m_94c8` (B1) [policy `p_cc84`] <= (`e_8e43`) **OR** (`e_a3ba`) **OR** (`e_1a72`) **OR** (`e_cdcc`); gold after update: **keep**
  - set 1: AeroExpress Logistics logged 600 yearly departures, meeting the minimum departure requirement of 500 under the preferred status policy.
  - set 2: AeroExpress Logistics holds IATA Cargo Agent Accreditation, fulfilling the credential alternative under the preferred status policy.
  - set 3: AeroExpress Logistics has a fleet size of 18 planes, which satisfies the fleet requirement of at least 15 under the preferred status policy.
  - set 4: AeroExpress Logistics holds ISO 9001 Quality Certification, satisfying the quality credential path under the preferred status policy.
- `m_a253` (B2) [policy `p_6963`] <= (`m_94c8`); gold after update: **keep**
  - set 1: AeroExpress Logistics satisfies preferred logistics status, granting approval for expedited dispatch options under the policy.
- `m_7cbe` (B3) [policy `p_f180`] <= (`m_a253` AND `e_2482`); gold after update: **keep**
  - set 1: AeroExpress Logistics qualifies for expedited dispatch options and registered a quarterly punctuality mark of 96 percent, exceeding the 92 percent requirement for top-tier priority status.
- `m_8f9d` (D1) [policy `p_cc16`] <= (`m_7cbe`); gold after update: **keep**
  - set 1: AeroExpress Logistics holds top-tier priority status, directing high-value pharmaceutical transport assignment to them under the allocation policy.
- `m_960c` (B4) [policy `p_6f5d`] <= (`e_90a1`); gold after update: **keep**
  - set 1: Sovereign Maritime commands 20 ocean freighters, satisfying the minimum count of 15 needed for heavy-freight carrier recognition.
- `m_93aa` (B5) [policy `p_086f`] <= (`e_4a07`); gold after update: **keep**
  - set 1: Zenith Air Charter holds an FAA Part 135 Certificate, satisfying the credential requirement for passenger charter authorization.
- `u_7add` retracts `e_a3ba` (reliability high)
- `u_b45f` retracts `e_cdcc` (reliability high)
- `u_4398` retracts `e_8e43` (reliability high)
- decoy policies: `p_99cd`, `p_e5c3`
- final state after updates (gold action -> state): `m_94c8` keep -> holds; `m_960c` keep -> holds; `m_93aa` keep -> holds; `m_a253` keep -> holds; `m_7cbe` keep -> holds; `m_8f9d` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2482~p_f180` policy_echoes_evidence: "a quarterly punctuality; punctuality mark of; quarterly punctuality mark" (judge under C7/C11)
- soft `e_90a1~p_6f5d` policy_echoes_evidence: "ocean freighter count" (judge under C7/C11)
- soft `e_1a72->m_94c8` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_8e43->m_94c8` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_a3ba->m_94c8` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_cdcc->m_94c8` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_94c8->m_a253` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_2482->m_7cbe` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_a253->m_7cbe` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_7cbe->m_8f9d` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_4a07->m_93aa` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

## s_10e29b8719  (F3-004, product eligibility)

*World:* An evaluation of consumer and industrial products to determine their qualification for specialized certifications, retail listings, and rebate programs.

### A. System view (judge C7 from this alone)
- `e_0131` [2026-01-08, State Chemical Laboratory Certificate] Chemical composition analysis verifies that BioShield 200 Sanitizer has an alcohol concentration of 75 percent.
- `e_dbf0` [2026-01-11, Air Quality Testing Laboratory Report] Laboratory testing confirms that AeroPure X7 Filter has a clean air delivery rate of 450 CFM.
- `e_b318` [2026-01-14, Acoustic Certification Bureau Data] Acoustic measurement records show that AeroPure X7 Filter operates at an operational noise level of 42 dB.
- `e_d6ce` [2026-01-17, National Appliance Energy Audit] Standardized power audit logs indicate that AeroPure X7 Filter has an annual energy consumption of 120 kWh.
- `e_6a6b` [2026-01-20, AHAM Directory Listing] Product directory records confirm that AeroPure X7 Filter holds an AHAM Verifide certification.
- `e_00dd` [2026-01-23, Tire Safety Standards Bureau Registry] Automotive testing documentation shows that OmniGrip Winter Tire holds a Three-Peak Mountain Snowflake rating.
- memories:
  - `m_eb24` AeroPure X7 Filter satisfies residential indoor air quality benchmarks.
  - `m_d6ba` AeroPure X7 Filter is listed for the Green Home Rebate Program.
  - `m_bd95` OmniGrip Winter Tire achieves severe snow traction clearance.
  - `m_8068` AeroPure X7 Filter obtains EcoEnergy Plus compliance.
  - `m_f585` BioShield 200 Sanitizer is suitable for hospital disinfectant listing.
- update `u_7625` [2026-01-26, AHAM Verification Registry Notice] An official registry notice clarifies that AeroPure X7 Filter does not hold an AHAM Verifide certification.
- policies:
  - `p_60fe` A commercial lighting fixture receives an Energy Star rating if its luminous efficacy exceeds 100 lumens per watt.
  - `p_e47b` A product is enrolled in the Green Home Rebate Program provided it achieves EcoEnergy Plus status.
  - `p_ccea` A water heater qualifies for municipal efficiency grants provided its standby thermal loss is below 15 watts.
  - `p_f511` A sanitation formula is accepted for hospital antimicrobial listing if its alcohol concentration is at least 70 percent.
  - `p_3990` A ventilation appliance qualifies for residential air standards when it has a minimum clean air delivery rate of 400 CFM, a maximum operational noise level of 45 dB, and maintains an AHAM Verifide credential.
  - `p_85f1` An air processing unit cleared on residential air standards attains EcoEnergy Plus status if its yearly energy consumption does not exceed 150 kWh.
  - `p_c42d` A vehicle tire achieves severe weather compliance when it possesses a Three-Peak Mountain Snowflake rating.

### B. Intended structure
- `m_eb24` (B1) [policy `p_3990`] <= (`e_dbf0` AND `e_b318` AND `e_6a6b`); gold after update: **withdraw**
  - set 1: AeroPure X7 Filter satisfies residential indoor air quality benchmarks because its clean air delivery rate of 450 CFM exceeds 400 CFM, its operational noise level of 42 dB is below 45 dB, and it possesses an AHAM Verifide certification.
- `m_8068` (B2) [policy `p_85f1`] <= (`m_eb24` AND `e_d6ce`); gold after update: **withdraw**
  - set 1: AeroPure X7 Filter obtains EcoEnergy Plus compliance because it satisfies residential indoor air quality benchmarks and its annual energy consumption of 120 kWh does not exceed 150 kWh.
- `m_d6ba` (D1) [policy `p_e47b`] <= (`m_8068`); gold after update: **withdraw**
  - set 1: AeroPure X7 Filter is listed for the Green Home Rebate Program because it holds EcoEnergy Plus compliance.
- `m_f585` (B3) [policy `p_f511`] <= (`e_0131`); gold after update: **keep**
  - set 1: BioShield 200 Sanitizer is suitable for hospital disinfectant listing because its alcohol concentration of 75 percent meets the minimum 70 percent requirement.
- `m_bd95` (B4) [policy `p_c42d`] <= (`e_00dd`); gold after update: **keep**
  - set 1: OmniGrip Winter Tire achieves severe snow traction clearance because it holds a Three-Peak Mountain Snowflake rating.
- `u_7625` retracts `e_6a6b` (reliability high)
- decoy policies: `p_60fe`, `p_ccea`
- final state after updates (gold action -> state): `m_eb24` withdraw -> fails; `m_f585` keep -> holds; `m_bd95` keep -> holds; `m_8068` withdraw -> fails; `m_d6ba` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_dbf0~p_3990` policy_echoes_evidence: "air delivery rate; clean air delivery; delivery rate of" (judge under C7/C11)
- soft `e_b318~p_3990` policy_echoes_evidence: "noise level of; operational noise level" (judge under C7/C11)
- soft `e_6a6b->m_eb24` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_b318->m_eb24` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_dbf0->m_eb24` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_d6ce->m_8068` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_eb24->m_8068` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `m_8068->m_d6ba` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_0131->m_f585` subject_uncertain: "no known entity named in memory" (judge under C6/C8)
- soft `e_00dd->m_bd95` subject_uncertain: "no known entity named in memory" (judge under C6/C8)

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

## s_632c0797fe  (F3-005, travel logistics)

*World:* An evaluation of regional transport providers across aviation, freight, ground shuttle, and maritime sectors.

### A. System view (judge C7 from this alone)
- `e_31df` [2026-01-08, International Air Transport Association registry] BlueSky Express retains active IATA accreditation.
- `e_e58b` [2026-01-11, State vehicle licensing department records] Crestline Shuttles operates 25 electric vans.
- `e_1a18` [2026-01-14, Official aviation registry records] Apex Charters operates a fleet size of 18 jets.
- `e_d453` [2026-01-17, Quarterly flight schedule announcement] Apex Charters serves 12 international routes.
- `e_e597` [2026-01-20, Civil Aviation Authority audit report] Apex Charters has a safety score of 92 points.
- `e_8e11` [2026-01-23, Transport ministry annual mobility ledger] Apex Charters logged annual passenger volume of 550000 travelers this year.
- `e_470c` [2026-01-26, Maritime Safety Agency annual report] Danube Ferries recorded annual safety incidents of 0 occurrences this year.
- memories:
  - `m_b0f1` BlueSky Express possesses certified cargo handling privileges.
  - `m_a862` Danube Ferries maintains exemplary safety rating status.
  - `m_b326` Crestline Shuttles qualifies for green transit subsidies.
  - `m_512d` Apex Charters is assigned to the preferred vendor roster.
  - `m_d49d` Apex Charters holds corporate flight clearance.
- update `u_71e0` [2026-01-29, Revised flight operations bulletin] Apex Charters serves 8 international routes.
- policies:
  - `p_0d52` Nautical passenger operators attain premier safety standing by logging annual safety incidents of 2 or fewer occurrences.
  - `p_0653` Port facility managers achieve eco-port recognition by maintaining renewable energy usage of at least 40 percent.
  - `p_a559` Freight logistics firms receive global cargo clearance upon holding valid IATA accreditation.
  - `p_6d9a` Commercial charter operators attain flight authorization either by maintaining a safety score of at least 90 points, maintaining a fleet size of at least 15 jets, and serving an international routes count of at least 10, or by recording annual passenger volume of at least 500000 travelers.
  - `p_e20c` Ground transport services secure eco-friendly funding when deploying a fleet size of at least 20 electric vans.
  - `p_e353` Air transport providers with flight authorization qualify for inclusion on preferred supplier lists.
  - `p_9d13` Regional rail operators earn priority track access by maintaining an on-time arrival rate of at least 95 percent.

### B. Intended structure
- `m_d49d` (B1) [policy `p_6d9a`] <= (`e_e597` AND `e_1a18` AND `e_d453`) **OR** (`e_8e11`); gold after update: **keep**
  - set 1: Apex Charters meets the primary flight authorization rule through a safety score of 92 points, a fleet size of 18 jets, and 12 international routes.
  - set 2: Apex Charters meets the alternative flight authorization rule by recording 550000 annual passenger volume.
- `m_512d` (D1) [policy `p_e353`] <= (`m_d49d`); gold after update: **keep**
  - set 1: Apex Charters qualifies for preferred supplier placement based on holding flight authorization.
- `m_b0f1` (B2) [policy `p_a559`] <= (`e_31df`); gold after update: **keep**
  - set 1: BlueSky Express achieves global cargo clearance by maintaining active IATA accreditation.
- `m_b326` (B3) [policy `p_e20c`] <= (`e_e58b`); gold after update: **keep**
  - set 1: Crestline Shuttles secures eco-friendly funding by operating 25 electric vans.
- `m_a862` (B4) [policy `p_0d52`] <= (`e_470c`); gold after update: **keep**
  - set 1: Danube Ferries attains premier safety standing by recording 0 annual safety incidents.
- `u_71e0` supersedes `e_d453` (reliability high)
- decoy policies: `p_9d13`, `p_0653`
- final state after updates (gold action -> state): `m_d49d` keep -> holds; `m_b0f1` keep -> holds; `m_b326` keep -> holds; `m_a862` keep -> holds; `m_512d` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_1a18~p_6d9a` policy_echoes_evidence: "a fleet size; fleet size of" (judge under C7/C11)
- soft `e_1a18~p_e20c` policy_echoes_evidence: "a fleet size; fleet size of" (judge under C7/C11)
- soft `e_e597~p_6d9a` policy_echoes_evidence: "a safety score; safety score of" (judge under C7/C11)
- soft `e_8e11~p_6d9a` policy_echoes_evidence: "annual passenger volume; passenger volume of" (judge under C7/C11)
- soft `e_470c~p_0d52` policy_echoes_evidence: "annual safety incidents; safety incidents of" (judge under C7/C11)

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

## s_1a8d336ed3  (F3-007, travel logistics)

*World:* The assistant evaluates compliance, licensing, and operational metrics to assign transit service contracts and carrier accreditations.

### A. System view (judge C7 from this alone)
- `e_1aa3` [2026-01-08, Maritime transit punctuality portal.] BlueWave Ferries recorded an on-time arrival rate of 92 percent this month.
- `e_9d70` [2026-01-11, State licensing board database entry.] Vanguard Coaches holds an official passenger transit licence.
- `e_ffaa` [2026-01-14, International logistics authorization database.] Apex Cargo holds an active international freight permit.
- `e_9df7` [2026-01-17, Department of Transportation annual compliance record.] Vanguard Coaches completed 150 safety audits this year.
- `e_76b2` [2026-01-20, Quarterly baggage operations audit.] Horizon Charters logged a baggage misplacement rate of 0.2 percent this quarter.
- `e_b742` [2026-01-23, Official safety inspection report filed on January 22, 2026.] Vanguard Coaches operates a certified driver fatigue monitoring system.
- `e_631a` [2026-01-26, Municipal transit vehicle registry export.] Vanguard Coaches maintains an active fleet size of 25 vehicles.
- memories:
  - `m_6e73` Vanguard Coaches achieves tier-one transport compliance standing.
  - `m_ccbc` Vanguard Coaches shall be selected for the downtown express route.
  - `m_8536` Vanguard Coaches is authorized for major urban transit routes.
  - `m_fc23` Horizon Charters maintains elite luggage handling status.
  - `m_f64e` Apex Cargo is eligible for cross-border logistics dispatch.
  - `m_9793` BlueWave Ferries qualifies for preferred maritime partner status.
- update `u_69c1` [2026-01-29, Updated municipal vehicle registry audit dated January 29, 2026.] Vanguard Coaches does not maintain an active fleet size of 25 vehicles.
- policies:
  - `p_5a31` A regional rail operator receives green railway certification when its yearly electrification ratio exceeds 80 percent.
  - `p_3448` A charter enterprise earns premier baggage service standing when its baggage misplacement rate is no greater than 0.5 percent this quarter.
  - `p_7649` A sea transport company achieves priority water carrier ranking provided its monthly on-time arrival rate reaches 90 percent or higher.
  - `p_bcb5` A carrier with first-level regulatory clearance gains approval for high-capacity city transit lines provided it holds an official passenger transit licence.
  - `p_2bb6` Allocation to the central express transit contract is open to any carrier with approval for high-capacity city transit lines.
  - `p_c2f7` A transit provider attains first-level regulatory clearance if it utilizes an automated driver fatigue monitoring system, completes at least 100 safety audits a year, and maintains an active fleet size of at least 20 vehicles.
  - `p_d050` A shipping firm gains clearance for international transport assignment when it maintains an active international freight permit.
  - `p_c0f8` An aviation vendor obtains priority slot reservation if its annual safety incident count remains below two.

### B. Intended structure
- `m_6e73` (B1) [policy `p_c2f7`] <= (`e_b742` AND `e_9df7` AND `e_631a`); gold after update: **withdraw**
  - set 1: Vanguard Coaches meets tier-one transport compliance standing by operating a driver fatigue monitoring system, completing 150 safety audits this year (meeting the threshold of 100), and maintaining an active fleet size of 25 vehicles (meeting the threshold of 20).
- `m_8536` (B2) [policy `p_bcb5`] <= (`m_6e73` AND `e_9d70`); gold after update: **withdraw**
  - set 1: Vanguard Coaches is authorized for major urban transit routes because it holds tier-one transport compliance standing and possesses an official passenger transit licence.
- `m_ccbc` (D1) [policy `p_2bb6`] <= (`m_8536`); gold after update: **withdraw**
  - set 1: Vanguard Coaches is selected for the downtown express route because it is authorized for major urban transit routes.
- `m_fc23` (B3) [policy `p_3448`] <= (`e_76b2`); gold after update: **keep**
  - set 1: Horizon Charters maintains elite luggage handling status because its quarterly baggage misplacement rate of 0.2 percent is at or below 0.5 percent.
- `m_9793` (B4) [policy `p_7649`] <= (`e_1aa3`); gold after update: **keep**
  - set 1: BlueWave Ferries qualifies for preferred maritime partner status because its monthly on-time arrival rate of 92 percent reaches the required 90 percent threshold.
- `m_f64e` (B5) [policy `p_d050`] <= (`e_ffaa`); gold after update: **keep**
  - set 1: Apex Cargo is eligible for cross-border logistics dispatch because it holds an active international freight permit.
- `u_69c1` retracts `e_631a` (reliability high)
- decoy policies: `p_5a31`, `p_c0f8`
- final state after updates (gold action -> state): `m_6e73` withdraw -> fails; `m_fc23` keep -> holds; `m_9793` keep -> holds; `m_f64e` keep -> holds; `m_8536` withdraw -> fails; `m_ccbc` withdraw -> fails

### C. Automated flags (for review, not verdicts)
- soft `e_1aa3~p_7649` policy_echoes_evidence: "on-time arrival rate" (judge under C7/C11)
- soft `e_9d70~p_bcb5` policy_echoes_evidence: "an official passenger; holds an official; official passenger transit; passenger transit licence" (judge under C7/C11)
- soft `e_ffaa~p_d050` policy_echoes_evidence: "active international freight; an active international; international freight permit" (judge under C7/C11)
- soft `e_76b2~p_3448` policy_echoes_evidence: "baggage misplacement rate; percent this quarter" (judge under C7/C11)
- soft `e_b742~p_c2f7` policy_echoes_evidence: "driver fatigue monitoring; fatigue monitoring system" (judge under C7/C11)
- soft `e_631a~p_c2f7` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of; maintains an active" (judge under C7/C11)
- soft `e_631a~p_d050` policy_echoes_evidence: "maintains an active" (judge under C7/C11)

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

## s_3a83f07da1  (F3-009, travel logistics)

*World:* Evaluation of commercial transport operators and travel service providers for route authorizations and dispatch contracts.

### A. System view (judge C7 from this alone)
- `e_0da1` [2026-01-08, Maritime Port Authority database] Nautilus Express maintains a vessel capacity of 12000 TEU.
- `e_3390` [2026-01-11, International Air Transport Association registry] AeroMove Freight holds an IATA Cargo Certificate.
- `e_fdd5` [2026-01-14, AeroMove Freight quarterly operational log] AeroMove Freight recorded an on-time rate of 96 percent this quarter.
- `e_f15e` [2026-01-17, Civil Aviation Authority licensing database] AeroMove Freight holds an Aviation Master Licence.
- `e_dbc0` [2026-01-20, Department of Tourism official registry] Wayfare Travels holds a Certified Tour Operator License.
- `e_97ce` [2026-01-23, Civil Aviation Authority safety evaluation] AeroMove Freight achieved a safety score of 92 points.
- `e_5cb8` [2026-01-26, AeroMove Freight fleet registry entry] AeroMove Freight operates a fleet size of 18 aircraft.
- memories:
  - `m_7e51` AeroMove Freight is selected for the urgent government transport contract.
  - `m_3b28` AeroMove Freight is designated for expedited charter routing.
  - `m_0a4a` Nautilus Express qualifies for deep-sea container service routes.
  - `m_5347` Wayfare Travels meets international travel agency standards.
- update `u_98ab` [2026-01-29, Civil Aviation Authority amended audit file] A revised audit report shows that AeroMove Freight achieved a safety score of 84 points.
- policies:
  - `p_9c75` A regional transit hub receives eco-transit funding if it achieves an annual carbon reduction of 15 percent.
  - `p_924d` Priority dispatch rights are granted to any carrier that satisfies a baseline fleet count of 15 planes, maintains a quarterly punctuality rate of 95 percent or higher, earns an evaluation rating of at least 90 points, and possesses valid cargo handling accreditation, or alternatively maintains an aviation master permit.
  - `p_227a` Transoceanic shipping clearance is assigned to any freight line providing a fleet cargo volume of 10000 TEU or greater.
  - `p_6e1b` Hazardous freight warehouse authorization requires a facility containment rating of 85 points.
  - `p_8e30` Global tour operator accreditation is conferred upon an agency possessing a recognized tour provider certificate.
  - `p_bc16` Awarding of sensitive government shipment orders requires that a logistics vendor holds priority dispatch rights.

### B. Intended structure
- `m_3b28` (B1) [policy `p_924d`] <= (`e_5cb8` AND `e_fdd5` AND `e_97ce` AND `e_3390`) **OR** (`e_f15e`); gold after update: **keep**
  - set 1: AeroMove Freight meets the requirements for priority dispatch rights through its baseline fleet count of 18 aircraft, quarterly punctuality rate of 96 percent, evaluation rating of 92 points, and IATA Cargo Certificate.
  - set 2: AeroMove Freight satisfies the alternative condition for priority dispatch rights by holding an Aviation Master Licence.
- `m_7e51` (D1) [policy `p_bc16`] <= (`m_3b28`); gold after update: **keep**
  - set 1: AeroMove Freight qualifies for sensitive government shipment orders because it holds priority dispatch rights.
- `m_0a4a` (B2) [policy `p_227a`] <= (`e_0da1`); gold after update: **keep**
  - set 1: Nautilus Express receives transoceanic shipping clearance because its vessel capacity of 12000 TEU meets the 10000 TEU threshold.
- `m_5347` (B3) [policy `p_8e30`] <= (`e_dbc0`); gold after update: **keep**
  - set 1: Wayfare Travels obtains global tour operator accreditation because it holds a Certified Tour Operator License.
- `u_98ab` supersedes `e_97ce` (reliability high)
- decoy policies: `p_9c75`, `p_6e1b`
- final state after updates (gold action -> state): `m_3b28` keep -> holds; `m_0a4a` keep -> holds; `m_5347` keep -> holds; `m_7e51` keep -> holds

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

## s_21f80e97c7  (F6-000, product eligibility)

*World:* An evaluation of hardware products against regional eligibility criteria for market programs and catalog listings.

### A. System view (judge C7 from this alone)
- `e_528e` [2026-01-08, Verified performance report issued by the Water Quality Association] AquaPure Filtration Unit has a daily water production capacity of 500 gallons.
- `e_50c0` [2026-01-11, Official test report from the National Renewable Energy Laboratory] Solaria Solar Panel has an efficiency rating of 22 percent.
- `e_bad7` [2026-01-14, Official compliance certificate published in the TUV Rheinland registry] Solaria Solar Panel holds a TUV Rheinland Safety Certificate.
- `e_2579` [2026-01-17, Signed testing statement from the International Electrotechnical Commission] VoltMax Battery Pack carries an IP67 waterproof rating certificate.
- `e_b830` [2026-01-20, Certified product listing in the Energy Star public database] EcoBreeze Air Conditioner has a seasonal energy efficiency ratio of 18.
- memories:
  - `m_4a31` Solaria Solar Panel qualifies for the Green Energy Rebate Program.
  - `m_039a` AquaPure Filtration Unit is designated for municipal emergency supply.
  - `m_4a3e` EcoBreeze Air Conditioner meets the premium efficiency standard.
  - `m_a2d4` Solaria Solar Panel is selected for the state procurement catalog.
  - `m_232c` VoltMax Battery Pack achieves heavy-duty industrial clearance.
- update `u_491c` [2026-01-23, Unverified comment on a public tech discussion forum] An anonymous forum post claims that Solaria Solar Panel does not have an efficiency rating of 22 percent.
- policies:
  - `p_db82` Water treatment systems gain civic disaster deployment status if daily water production capacity reaches 400 gallons or more.
  - `p_40b8` Cooling equipment achieves premier efficiency status if its seasonal energy efficiency ratio is at least 16.
  - `p_62da` A product is added to government purchasing listings if it gains green energy program approval.
  - `p_f881` Boilers achieve residential tax credit eligibility if fuel conversion rating is 90 percent or higher.
  - `p_6c34` Storage units earn severe-environment authorization when possessing an IP67 waterproof rating certificate.
  - `p_c65b` Lighting fixtures gain commercial grant access when operational lifespan reaches 50000 hours.
  - `p_0a66` Energy hardware receives green energy program approval either with an efficiency rating of 20 percent or higher, or by holding a TUV Rheinland Safety Certificate.

### B. Intended structure
- `m_4a31` (B1) [policy `p_0a66`] <= (`e_50c0`) **OR** (`e_bad7`); gold after update: **keep**
  - set 1: Solaria Solar Panel has an efficiency rating of 22 percent, which meets the required threshold of 20 percent for green energy program approval.
  - set 2: Solaria Solar Panel holds a TUV Rheinland Safety Certificate, satisfying the alternative requirement for green energy program approval.
- `m_a2d4` (D1) [policy `p_62da`] <= (`m_4a31`); gold after update: **keep**
  - set 1: Solaria Solar Panel gains green energy program approval, satisfying the condition for inclusion in government purchasing listings.
- `m_4a3e` (B2) [policy `p_40b8`] <= (`e_b830`); gold after update: **keep**
  - set 1: EcoBreeze Air Conditioner has a seasonal energy efficiency ratio of 18, exceeding the required minimum ratio of 16 for premier efficiency status.
- `m_232c` (B3) [policy `p_6c34`] <= (`e_2579`); gold after update: **keep**
  - set 1: VoltMax Battery Pack holds an IP67 waterproof rating certificate, fulfilling the requirement for severe-environment authorization.
- `m_039a` (B4) [policy `p_db82`] <= (`e_528e`); gold after update: **keep**
  - set 1: AquaPure Filtration Unit provides a daily water production capacity of 500 gallons, meeting the 400-gallon threshold for civic disaster deployment status.
- `u_491c` retracts `e_50c0` (reliability low)
- decoy policies: `p_c65b`, `p_f881`
- final state after updates (gold action -> state): `m_4a31` keep -> holds; `m_4a3e` keep -> holds; `m_232c` keep -> holds; `m_039a` keep -> holds; `m_a2d4` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_528e~p_db82` policy_echoes_evidence: "daily water production; water production capacity" (judge under C7/C11)
- soft `e_50c0~p_0a66` policy_echoes_evidence: "an efficiency rating; efficiency rating of" (judge under C7/C11)
- soft `e_2579~p_6c34` policy_echoes_evidence: "waterproof rating certificate" (judge under C7/C11)
- soft `e_b830~p_40b8` policy_echoes_evidence: "energy efficiency ratio; seasonal energy efficiency" (judge under C7/C11)
- soft `u_491c` retraction_reads_as_hedge: "claims" (judge under C4)

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

## s_93f6a93ba3  (F6-002, product eligibility)

*World:* Evaluation of equipment performance metrics and commercial deployment eligibility for specialized electronic products.

### A. System view (judge C7 from this alone)
- `e_c517` [2026-01-08, Certified Product Specification Sheet from KryoTech Engineering] AeroDry 3000 maintains a peak moisture extraction capacity of 55 liters per day.
- `e_9f40` [2026-01-11, Performance Validation Certificate from TechBench Testing] OptiScan P20 completed an optical processing speed test of 120 pages per minute.
- `e_83ad` [2026-01-14, Standard Warranty Term Agreement from KryoTech Engineering] AeroDry 3000 includes a commercial warranty period of 3 years.
- `e_2967` [2026-01-17, Official Acoustic Testing Report from SoundLab Audits] AeroDry 3000 demonstrated an operational sound level of 42 decibels during testing.
- memories:
  - `m_dfa2` AeroDry 3000 holds high-efficiency dehumidifier status.
  - `m_7a30` AeroDry 3000 satisfies low-noise acoustic criteria.
  - `m_bc9e` OptiScan P20 qualifies for high-speed document processing listing.
  - `m_e78c` AeroDry 3000 is approved for deployment in commercial healthcare facilities.
- update `u_8d8a` [2026-01-20, Formal Audit Notice from SoundLab Audits] An audit statement from SoundLab Audits indicates that the operational sound level measurements for AeroDry 3000 are currently under review due to sensor calibration queries.
- policies:
  - `p_8eeb` Entry into the high-velocity document scanner registry requires a document throughput rate of at least 100 pages per minute.
  - `p_9f97` Authorization for installation in medical commercial sites is granted to a device designated as a high-performance dehumidifying system that features a commercial coverage term of no less than 2 years.
  - `p_caf6` Acoustic compliance is met for equipment demonstrating a maximum operational sound level of 45 decibels.
  - `p_a99b` Eligibility for regional distribution rebates requires a minimum annual order volume of 500 units.
  - `p_1c1a` A unit attains classification as a high-performance dehumidifying system when equipment that satisfies sound guidelines also delivers a daily moisture removal capacity of at least 50 liters.
  - `p_daad` An equipment item secures premium industrial tier endorsement when possessing a continuous operating rating above 12 hours.

### B. Intended structure
- `m_7a30` (B1) [policy `p_caf6`] <= (`e_2967`); gold after update: **uncertain**
  - set 1: AeroDry 3000 has an operational sound level of 42 decibels, which satisfies the maximum threshold of 45 decibels required for acoustic compliance.
- `m_dfa2` (B2) [policy `p_1c1a`] <= (`m_7a30` AND `e_c517`); gold after update: **uncertain**
  - set 1: AeroDry 3000 meets sound guidelines through its acoustic compliance and has a peak moisture extraction capacity of 55 liters per day, satisfying the 50 liters per day threshold for classification as a high-performance dehumidifying system.
- `m_e78c` (D1) [policy `p_9f97`] <= (`m_dfa2` AND `e_83ad`); gold after update: **uncertain**
  - set 1: AeroDry 3000 is classified as a high-performance dehumidifying system and holds a commercial warranty period of 3 years, meeting the minimum 2-year coverage requirement for installation authorization in medical commercial sites.
- `m_bc9e` (B3) [policy `p_8eeb`] <= (`e_9f40`); gold after update: **keep**
  - set 1: OptiScan P20 has an optical processing speed of 120 pages per minute, meeting the minimum requirement of 100 pages per minute for entry into the high-velocity document scanner registry.
- `u_8d8a` hedges `e_2967` (reliability high)
- decoy policies: `p_daad`, `p_a99b`
- final state after updates (gold action -> state): `m_7a30` uncertain -> undetermined; `m_bc9e` keep -> holds; `m_dfa2` uncertain -> undetermined; `m_e78c` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_9f40~p_8eeb` policy_echoes_evidence: "pages per minute" (judge under C7/C11)
- soft `e_2967~p_caf6` policy_echoes_evidence: "operational sound level; sound level of" (judge under C7/C11)

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

## s_bbf57cda27  (F6-005, travel logistics)

*World:* Travel logistics operators are evaluated for dispatch privileges, passenger flight clearances, and terminal dock access.

### A. System view (judge C7 from this alone)
- `e_7ede` [2026-01-08, Civil Aviation Authority registry database.] AeroGlobe Logistics maintains an active fleet size of 15 cargo aircraft.
- `e_ffd4` [2026-01-11, Ministry of Tourism official registry.] Solis Expeditions holds an active international tour operator license.
- `e_7f8b` [2026-01-14, International Aviation Safety Agency audit report.] AeroGlobe Logistics achieved an annual safety compliance rating of 98 percent this year.
- `e_3734` [2026-01-17, Port Authority annual throughput statement.] Vantage Freight recorded an annual volume of 50000 metric tons of cargo handled this year.
- memories:
  - `m_dc31` AeroGlobe Logistics holds status as a certified heavy-fleet operator.
  - `m_63e7` Vantage Freight qualifies for deep-sea terminal access.
  - `m_23c2` AeroGlobe Logistics maintains tier-one flight dispatch approval.
  - `m_f35c` Solis Expeditions is eligible for cross-border passenger routing.
  - `m_45d3` AeroGlobe Logistics should be selected for the priority cargo contract.
- update `u_5c81` [2026-01-20, Anonymous user on an online aviation forum.] An unverified forum post claims that AeroGlobe Logistics does not maintain an active fleet size of 15 aircraft.
- policies:
  - `p_5aca` Customs expedited clearance is granted to shipping agencies that log at least 500 container transfers monthly.
  - `p_7006` Regional shuttle permits are issued to transit providers operating more than 20 commuter buses.
  - `p_b055` Deep-water dock privileges are assigned to freight firms with an annual cargo handling volume of at least 40000 metric tons.
  - `p_0504` Awarding priority freight agreements requires an enterprise with dispatch clearance at tier one.
  - `p_cccd` Authorization for cross-border travel operations is granted to any company holding an active international tour operator license.
  - `p_be59` Carrier designation for heavy fleets requires maintaining an active fleet size of 10 aircraft or above.
  - `p_e192` Dispatch clearance at tier one requires a carrier designated as a heavy fleet operator to demonstrate an annual safety rating of at least 95 percent.

### B. Intended structure
- `m_dc31` (B1) [policy `p_be59`] <= (`e_7ede`); gold after update: **uncertain**
  - set 1: Having an active fleet size of 15 aircraft satisfies the minimum fleet threshold of 10 aircraft to qualify as a heavy fleet carrier.
- `m_23c2` (B2) [policy `p_e192`] <= (`m_dc31` AND `e_7f8b`); gold after update: **uncertain**
  - set 1: Being designated as a heavy fleet operator along with an annual safety compliance rating of 98 percent satisfies the 95 percent threshold required for tier-one dispatch clearance.
- `m_45d3` (D1) [policy `p_0504`] <= (`m_23c2`); gold after update: **uncertain**
  - set 1: Holding tier-one flight dispatch approval satisfies the policy requirement to be selected for the priority freight contract.
- `m_f35c` (B3) [policy `p_cccd`] <= (`e_ffd4`); gold after update: **keep**
  - set 1: Holding an active international tour operator license meets the mandate for cross-border travel authorization.
- `m_63e7` (B4) [policy `p_b055`] <= (`e_3734`); gold after update: **keep**
  - set 1: Handling an annual volume of 50000 metric tons of cargo exceeds the 40000 metric tons minimum threshold required for deep-water dock privileges.
- `u_5c81` retracts `e_7ede` (reliability low)
- decoy policies: `p_5aca`, `p_7006`
- final state after updates (gold action -> state): `m_dc31` uncertain -> undetermined; `m_f35c` keep -> holds; `m_63e7` keep -> holds; `m_23c2` uncertain -> undetermined; `m_45d3` uncertain -> undetermined

### C. Automated flags (for review, not verdicts)
- soft `e_7ede~p_be59` policy_echoes_evidence: "active fleet size; an active fleet; fleet size of" (judge under C7/C11)
- soft `e_ffd4~p_cccd` policy_echoes_evidence: "active international tour; an active international; international tour operator; tour operator license" (judge under C7/C11)
- soft `e_7f8b~p_e192` policy_echoes_evidence: "an annual safety" (judge under C7/C11)
- soft `u_5c81` retraction_reads_as_hedge: "claims" (judge under C4)

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
