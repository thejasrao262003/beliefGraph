# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* Assessment of protective gear models for compliance, distribution authorization, and deployment suitability.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Certified laboratory audit report, issued earlier this month.] Apex Guard 500 holds a shell penetration resistance score of 40 points.
- `e_94fc` [2026-01-11, Ballistics testing registry entry, documented earlier this month.] Vortex Shield contains a ballistic fragment resistance threshold of 600 m/s.
- `e_0439` [2026-01-14, Quality control inspection log from assembly plant, filed mid-month.] Apex Guard 500 features a secondary chin-strap retention load threshold of 250 newtons.
- `e_b5f7` [2026-01-17, Official test report from National Safety Testing Institute, effective last week.] Apex Guard 500 recorded a crash impact attenuation score of 85 points.
- `e_df05` [2026-01-20, Verification statement from global underwriting firm, recorded recently.] Apex Guard 500 maintains an active manufacturer liability insurance policy of 2,000,000 USD annually.
- memories:
  - `m_c4d7` Apex Guard 500 complies with commercial distribution standards.
  - `m_3f2d` Apex Guard 500 secures baseline protective certification.
  - `m_280b` Vortex Shield qualifies for tactical equipment deployment.
  - `m_c5de` Apex Guard 500 satisfies basic structural shock requirements.
  - `m_5302` Apex Guard 500 achieves full enterprise catalog clearance.
  - `m_4b85` Apex Guard 500 should be placed into regional retail stores.
- update `u_91ee` [2026-01-23, Revised laboratory re-test certificate, issued yesterday.] Apex Guard 500 achieved a crash impact attenuation score of 70 points in re-testing.
- policies:
  - `p_fe1d` A product is awarded standard safety clearance provided it fulfills baseline shock absorption criteria.
  - `p_5cd1` An offering qualifies for master inventory listing when it receives retail distribution authorization and carries vendor indemnity coverage of no less than 1,500,000 USD annually.
  - `p_fbe6` A product is approved for store shelf rollout provided it has achieved master inventory listing.
  - `p_b0aa` A visor is cleared for field service operations if its projectile protection metric reaches at least 550 m/s.
  - `p_1714` A helmet gains retail distribution authorization if it holds standard safety clearance and maintains a strap tensile strength rating of at least 200 newtons.
  - `p_4f8e` A medical device gains hospital procurement sanction when its operational acoustic emission stays below 40 decibels.
  - `p_0087` An item meets baseline shock absorption criteria when its collision energy dissipation rating is at least 80 points alongside a penetration deflection value of no less than 35 points.
  - `p_1a46` A maritime vessel receives open-water navigation permit if its hull thickness measures at least 25 millimeters and it carries automated location transmitters.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Apex Guard 500 meets baseline shock absorption criteria because its crash impact attenuation score of 85 points meets the 80 points threshold and its shell penetration resistance score of 40 points meets the 35 points threshold.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Apex Guard 500 receives standard safety clearance because it fulfills baseline shock absorption criteria.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Apex Guard 500 gains retail distribution authorization because it holds standard safety clearance and its chin-strap retention load threshold of 250 newtons meets the 200 newtons threshold.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Apex Guard 500 qualifies for master inventory listing because it receives retail distribution authorization and its manufacturer liability insurance policy of 2,000,000 USD annually meets the 1,500,000 USD annually threshold.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Apex Guard 500 is approved for store shelf rollout because it has achieved master inventory listing.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Vortex Shield is cleared for field service operations because its ballistic fragment resistance threshold of 600 m/s meets the 550 m/s threshold.
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

## s_3d821bdd07  (F2-000, product eligibility)

*World:* An evaluation of hardware products against corporate and institutional procurement standards.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Underwriters Laboratories certification directory entry from January 8, 2026.] Lumino Desk Lamp possesses a UL safety certification.
- `e_dfe6` [2026-01-11, Global Compliance Registry database entry from January 11, 2026.] AeroGrid Router holds an ISO 27001 certification.
- `e_e50c` [2026-01-14, Official technical specification sheet from the manufacturer released on January 14, 2026.] AeroGrid Router features data throughput reaching 12 Gbps.
- memories:
  - `m_2075` AeroGrid Router qualifies for enterprise status.
  - `m_36f2` Lumino Desk Lamp satisfies residential safety benchmarks.
  - `m_7743` AeroGrid Router is included in government procurement catalogues.
- update `u_a152` [2026-01-17, Auditor testing report dated January 17, 2026.] AeroGrid Router provides data throughput of 8 Gbps under standardized load conditions.
- update `u_41fa` [2026-01-20, Compliance authority notice issued on January 20, 2026.] AeroGrid Router lacks an active ISO 27001 certification following non-compliance findings.
- policies:
  - `p_d10e` An enterprise designation is granted when network hardware exhibits data throughput of at least 10 Gbps or maintains an ISO 27001 certification.
  - `p_8779` An electronic component is approved for export when its lead content remains under 0.1 percent.
  - `p_3b4c` A hardware device is listed on public purchasing registers provided the system has earned enterprise designation.
  - `p_4091` A lighting fixture achieves domestic electrical compliance whenever the product carries a UL safety certification.
  - `p_e525` A commercial appliance receives premium tier rating if its operational noise level stays below 40 dB.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: AeroGrid Router exhibits data throughput of 12 Gbps, which meets the 10 Gbps threshold for enterprise designation.
  - set 2: AeroGrid Router holds an ISO 27001 certification, satisfying the compliance requirement for enterprise designation.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: AeroGrid Router qualifies for enterprise status, satisfying the prerequisite for public purchasing register listing.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: Lumino Desk Lamp carries a UL safety certification, fulfilling the requirement for domestic electrical compliance.
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

## s_94a4bc8c87  (F3-000, product eligibility)

*World:* Assessment of equipment compliance and commercial rebate eligibility for sustainable technology products.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Manufacturer spec sheet recorded on January 8, 2026.] Vanguard EcoDrive Motor maintains an acoustic output of 45 dB.
- `e_2787` [2026-01-11, Laboratory test report published on January 11, 2026.] Solaria Volt 400 has an efficiency rating of 22 percent.
- `e_124c` [2026-01-14, Registry entry verified on January 14, 2026.] Solaria Volt 400 holds a TUV Rheinland Excellence Seal.
- `e_ac4d` [2026-01-17, Distribution contract signed on January 17, 2026.] Solaria Volt 400 includes a warranty duration of 10 years.
- `e_c8d5` [2026-01-20, Official technical sheet from Solaria Quality Assurance, retrieved January 20, 2026.] Solaria Volt 400 carries an IP67 waterproof certification.
- memories:
  - `m_4677` Vanguard EcoDrive Motor is certified for low-noise operation.
  - `m_aeef` Solaria Volt 400 is designated as a premium green product.
  - `m_b7fc` Solaria Volt 400 is approved for commercial rebate listing.
- update `u_84c2` [2026-01-23, Updated audit memo issued on January 23, 2026.] Solaria Volt 400 has an efficiency rating of 18 percent.
- policies:
  - `p_b875` An item qualified for green status that features a warranty duration of 8 years or longer gains eligibility for commercial rebates.
  - `p_ba9f` A unit achieves quiet operational clearance if its acoustic output does not exceed 50 dB.
  - `p_4b46` A device secures industrial heavy-duty classification when it possesses a dust resistance rating of 5 or higher.
  - `p_0c4c` Agricultural machinery receives high-yield energy certification provided its power factor exceeds 0.95.
  - `p_81ec` Equipment attains premium green status either with an IP67 waterproof certification alongside an efficiency rating of at least 20 percent, or by securing a TUV Rheinland Excellence Seal.

### B. Intended structure
- `m_aeef` (B1) [policy `p_81ec`] <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: Solaria Volt 400 holds an IP67 waterproof certification and has an efficiency rating of 22 percent, satisfying the combined criteria for premium green status.
  - set 2: Solaria Volt 400 possesses a TUV Rheinland Excellence Seal, which independently qualifies it for premium green status.
- `m_b7fc` (D1) [policy `p_b875`] <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: Solaria Volt 400 achieves green status and features a warranty duration of 10 years, satisfying the policy requirements for commercial rebate eligibility.
- `m_4677` (B2) [policy `p_ba9f`] <= (`e_4667`); gold after update: **keep**
  - set 1: Vanguard EcoDrive Motor has an acoustic output of 45 dB, which does not exceed the maximum threshold of 50 dB required for low-noise clearance.
- `u_84c2` supersedes `e_2787` (reliability high)
- decoy policies: `p_4b46`, `p_0c4c`
- final state after updates (gold action -> state): `m_aeef` keep -> holds; `m_4677` keep -> holds; `m_b7fc` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `e_2787~p_81ec` policy_echoes_evidence: "an efficiency rating; efficiency rating of" (judge under C7/C11)
- soft `e_ac4d~p_b875` policy_echoes_evidence: "a warranty duration; warranty duration of" (judge under C7/C11)

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
