# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* An AI assistant evaluates enterprise partner eligibility and client technical deployment readiness across independent vendor applications.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Official certification authority registry] Aether Dynamics holds an active ISO 27001 compliance certificate.
- `e_94fc` [2026-01-11, Verified customer success database] Orion Retailers completed three successful enterprise client deployments this quarter.
- `e_0439` [2026-01-14, Internal human resources roster] Aether Dynamics employs five full-time support engineers for technical assistance.
- `e_b5f7` [2026-01-17, Signed corporate accounting ledger] Aether Dynamics logged yearly software expenditure totaling $250,000 across recent accounts.
- `e_df05` [2026-01-20, Official regulatory compliance log] Aether Dynamics recorded zero legal sanctions during recent regulatory audits.
- memories:
  - `m_c4d7` Aether Dynamics fulfills core operational support criteria for elite ranking.
  - `m_3f2d` Aether Dynamics achieves Qualified Enterprise Status.
  - `m_280b` Orion Retailers demonstrates proven deployment capability.
  - `m_c5de` Aether Dynamics meets foundational commercial standards.
  - `m_5302` Aether Dynamics meets full regulatory and technical prerequisites for enrollment.
  - `m_4b85` Grant enrollment to Aether Dynamics in the Global Partner Program.
- update `u_91ee` [2026-01-23, Audited financial restatement document] Aether Dynamics corrected its financial filings, showing yearly software expenditure reached only $150,000 across recent accounts.
- policies:
  - `p_fe1d` An applicant earns premier merchant designation once core trading prerequisites are verified.
  - `p_5cd1` An organization is cleared for partner registry inclusion if it possesses an elite operational rating while maintaining a clean regulatory record.
  - `p_fbe6` Admission into the Global Partner Program is granted when partner registry inclusion is formally confirmed.
  - `p_b0aa` Sufficient integration experience is established when a firm completes a minimum of two successful enterprise client deployments.
  - `p_1714` Elite operational rating is attained by any entity holding premier merchant designation that retains five or more dedicated technical personnel.
  - `p_4f8e` Provisional partner status is assigned to firms with at least two regional offices and a certified security audit.
  - `p_0087` An applicant fulfills core trading prerequisites provided annual billing reaches $200,000 alongside valid ISO 27001 accreditation.
  - `p_1a46` Small business tax exemption is granted to any vendor with total annual revenue under $100,000 and fewer than three staff members.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Aether Dynamics meets the minimum annual billing requirement of $200,000 and holds ISO 27001 accreditation, satisfying core trading prerequisites.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Having met core trading prerequisites, Aether Dynamics earns premier merchant designation.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: With premier merchant designation and five dedicated technical personnel, Aether Dynamics attains an elite operational rating.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: With an elite operational rating and zero legal sanctions, Aether Dynamics is cleared for partner registry inclusion.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Being cleared for partner registry inclusion, Aether Dynamics is granted admission into the Global Partner Program.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Completing three enterprise client deployments exceeds the threshold of two, establishing sufficient integration experience.
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

## s_c41a0870a2  (F6-000, product eligibility)

*World:* An assessment of product eligibility for commercial release across multiple technological and healthcare sectors.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, Clinical Research Organization Final Summary Report, verified clinical data] Lumina Health Tracker completed a 500-subject clinical trial without any severe adverse incidents.
- `e_5dd0` [2026-01-11, European Notified Body Official Registry, signed certificate] Lumina Health Tracker secured CE Mark Class IIa regulatory clearance.
- `e_0823` [2026-01-14, National Electromagnetic Compatibility Laboratory Test Report, official document] AeroGlide Sensor passed FCC Part 15 testing for electromagnetic emissions limits.
- `e_45ef` [2026-01-17, Regulatory Affairs Document Archive, verified filing receipt] Lumina Health Tracker filed a complete technical dossier accompanied by dual-language operational manuals.
- `e_fdcd` [2026-01-20, Accredited Chemical Analysis Center Report, signed certificate] Dermacool Gel showed zero prohibited synthetic preservatives in third-party chemical testing.
- `e_f882` [2026-01-23, National Acoustics Inspection Bureau, certified test log] SoundWave Earbuds maintained acoustic output under 85 decibels during standard laboratory testing.
- `e_660f` [2026-01-26, ISO Registrar Compliance Database, official audit record] Lumina Health Tracker obtained ISO 13485 medical device quality management certification.
- memories:
  - `m_6c9c` Lumina Health Tracker meets global regulatory safety parameters.
  - `m_cc95` Authorize Lumina Health Tracker for commercial rollout across European medical networks.
  - `m_ece3` SoundWave Earbuds fulfill consumer hearing safety criteria.
  - `m_e062` Lumina Health Tracker achieves clinical distribution readiness status.
  - `m_bda8` AeroGlide Sensor satisfies North American radio frequency compliance requirements.
  - `m_6d1e` Dermacool Gel meets organic cosmetics formulation standards.
- update `u_99cf` [2026-01-29, Unverified online forum post, user comment] A user on a tech forum claimed that Lumina Health Tracker lacks genuine ISO 13485 certification.
- policies:
  - `p_cd31` Equipment designated with global compliance standing reaches clinical authorization upon completing human trials of over 300 subjects free of critical harm reports.
  - `p_b65d` Full commercial release is permitted for clinically authorized hardware possessing complete dossier paperwork paired with translated instruction documentation.
  - `p_b3f6` Personal care goods qualify for eco-friendly designation provided laboratory testing confirms complete absence of restricted synthetic additives.
  - `p_6aef` Electronic equipment attains domestic spectrum approval upon demonstrating valid electromagnetic compatibility test results under regulatory thresholds.
  - `p_d3ca` Hazardous material transport clearance is granted to commercial vehicles operating with certified fire suppression equipment and quarterly inspection records.
  - `p_8aeb` Hardware units achieve global compliance standing whenever possessing valid healthcare device certification or securing recognized European approval marks.
  - `p_c629` Food service products obtain organic retail certification if raw agricultural ingredients source exclusively from certified sustainable farms.
  - `p_9e3e` Audio consumer devices receive protective health certification when maximum decibel output remains below 85 dB under standard acoustic evaluation.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Obtaining ISO 13485 certification satisfies the rule requiring valid healthcare device certification.
  - set 2: Securing CE Mark Class IIa clearance satisfies the alternative rule requiring recognized European approval marks.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Meeting global compliance standing along with completing a 500-subject trial without severe incidents satisfies the rule for clinical authorization.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Reaching clinical authorization together with filing a complete dossier and dual-language manuals fulfills the rule for full commercial release.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Passing FCC Part 15 testing satisfies the rule requiring valid electromagnetic compatibility test results under regulatory thresholds.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: Showing zero prohibited synthetic preservatives in testing fulfills the requirement for complete absence of restricted synthetic additives.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: Maintaining acoustic output under 85 decibels satisfies the rule requiring maximum decibel output below 85 dB.
- `u_99cf` retracts `e_660f` (reliability low)
- decoy policies: `p_d3ca`, `p_c629`
- final state after updates (gold action -> state): `m_6c9c` keep -> holds; `m_bda8` keep -> holds; `m_6d1e` keep -> holds; `m_ece3` keep -> holds; `m_e062` keep -> holds; `m_cc95` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `u_99cf` retraction_reads_as_hedge: "claimed"

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
