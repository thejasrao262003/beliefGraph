# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* Evaluation of corporate client account statuses and product eligibility qualifications across commercial partners.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Verified CRM telemetry export] Apex Dynamics maintains an annual customer retention rate of 92%.
- `e_94fc` [2026-01-11, State Department of Motor Vehicles registry] Orion Freight Corp operates a commercial fleet consisting of 80% electric delivery vehicles.
- `e_0439` [2026-01-14, Certified third-party compliance portal] Apex Dynamics successfully completed an independent SOC 2 Type II audit.
- `e_b5f7` [2026-01-17, Signed annual financial audit report] Apex Dynamics reported $3.5 million in annual recurring revenue for the previous fiscal period.
- `e_df05` [2026-01-20, Internal client management portal] Apex Dynamics was assigned a dedicated account executive management team.
- memories:
  - `m_c4d7` Apex Dynamics meets the operational risk threshold for enterprise status.
  - `m_3f2d` Apex Dynamics holds Tier-1 designation.
  - `m_280b` Orion Freight Corp qualifies for the Eco-Transport Subsidy.
  - `m_c5de` Apex Dynamics satisfies the commercial stability benchmark.
  - `m_5302` Apex Dynamics satisfies all prerequisite criteria for the Preferred Partner Discount.
  - `m_4b85` Enroll Apex Dynamics in the Preferred Partner Discount program.
- update `u_91ee` [2026-01-23, Official restated financial statement] A revised accounting audit confirms Apex Dynamics generated $1.2 million in annual recurring revenue for the fiscal period.
- policies:
  - `p_fe1d` Tier-1 designation is conferred upon any organizational client that achieves verified commercial stability status.
  - `p_5cd1` Preferred Partner Discount prerequisites are fulfilled when an account meets the operational risk threshold for enterprise status and retains a designated account executive team.
  - `p_fbe6` Program enrollment for the Preferred Partner Discount is authorized for any corporate client that satisfies all prerequisite discount criteria.
  - `p_b0aa` The Eco-Transport Subsidy is awarded to transport operators maintaining a minimum 75% zero-emission vehicle ratio.
  - `p_1714` The operational risk threshold for enterprise status requires Tier-1 designation combined with an active third-party security certification.
  - `p_4f8e` Fast-track underwriting is approved for commercial entities with a credit rating of AA or higher and no registered legal encumbrances.
  - `p_0087` Commercial stability status is attained when an enterprise maintains an annual recurring revenue of at least $2.5 million alongside a customer retention benchmark exceeding 90%.
  - `p_1a46` A promotional hardware credit is extended to business accounts that maintain an active multi-year contract and spend over $500,000 annually on cloud infrastructure.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Annual recurring revenue of $3.5 million meets the $2.5 million requirement and a 92% retention rate exceeds the 90% threshold.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Apex Dynamics holds commercial stability status.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Tier-1 designation together with an active SOC 2 Type II audit fulfills the operational risk requirements.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Meeting operational risk requirements along with a dedicated account executive team satisfies all discount prerequisites.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Fulfilling all discount prerequisites authorizes enrollment in the Preferred Partner Discount program.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: An 80% electric vehicle fleet meets the 75% zero-emission threshold.
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

*World:* An evaluation of client account records for commercial partnership benefits and trade-in program eligibility.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Certified sales registry records] Vortex Dynamics acquired ten industrial processing units during the last quarter.
- `e_dfe6` [2026-01-11, Verified system administration portal] Apex Tech Solutions maintained 600 active licenses during the previous month.
- `e_e50c` [2026-01-14, Official corporate financial audit report] Apex Tech Solutions recorded annual recurring revenue of $120,000 over the past year.
- memories:
  - `m_2075` Apex Tech Solutions qualifies for standard partner tier standing.
  - `m_36f2` Vortex Dynamics satisfies volume requirements for equipment trade-in incentives.
  - `m_7743` Apex Tech Solutions receives a dedicated client specialist.
- update `u_a152` [2026-01-17, Amended corporate financial audit report] Apex Tech Solutions restated its annual recurring revenue for the past year to $85,000.
- update `u_41fa` [2026-01-20, Updated system administration portal log] Apex Tech Solutions corrected its seat count to 350 active licenses following a user audit.
- policies:
  - `p_d10e` Standard partner tier standing is conferred upon any account generating at least $100,000 in annual recurring revenue, or maintaining an active seat threshold of 500 licenses.
  - `p_8779` Priority order dispatch is granted when a customer places an emergency replacement request or operates within an accredited healthcare sector.
  - `p_3b4c` A dedicated client specialist is designated for any account possessing standard partner tier standing.
  - `p_4091` Equipment trade-in incentives require a client to purchase no fewer than eight industrial hardware units within a single quarter.
  - `p_e525` Custom software deployment support is available to organizations that hold an active enterprise subscription and maintain zero open critical security tickets.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: The annual recurring revenue of $120,000 satisfies the minimum requirement of $100,000 needed for standard partner tier standing.
  - set 2: The active license count of 600 meets the threshold of 500 licenses required for standard partner tier standing.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: Holding standard partner tier standing satisfies the requirement to be assigned a dedicated client specialist.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: Purchasing ten industrial processing units meets the threshold of acquiring at least eight hardware units in a quarter for trade-in incentives.
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

*World:* A vendor management system evaluates technology partners and logistics suppliers for program tiering and marketing funding.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Official EcoVadis Assessment Registry platform.] Zenith Logistics holds an active EcoVadis Gold sustainability rating.
- `e_2787` [2026-01-11, Audited financial report signed by an independent CPA firm.] Apex Tech recorded $2.5 million in annual recurring software revenue over the past fiscal year.
- `e_124c` [2026-01-14, Official IAF CertSearch global database registry.] Apex Tech holds an active ISO 27001 information security certification.
- `e_ac4d` [2026-01-17, Signed strategic partnership agreement.] Apex Tech submitted a joint marketing plan committing $100,000 in co-investment.
- `e_c8d5` [2026-01-20, Partner Success Portal verified deployment logs.] Apex Tech has completed 15 certified customer software implementations.
- memories:
  - `m_4677` Zenith Logistics is designated as a Green Channel Tier 1 vendor.
  - `m_aeef` Apex Tech meets Gold Tier partner status criteria.
  - `m_b7fc` Apex Tech receives a $50,000 co-marketing fund allocation.
- update `u_84c2` [2026-01-23, Amended corporate tax return submitted to the regulatory portal.] Apex Tech revised its financial filing, reporting $1.2 million in annual recurring software revenue.
- policies:
  - `p_b875` Co-marketing grant allocation is approved for any vendor holding Gold tier status that submits a joint promotional proposal exceeding $75,000 in committed funds.
  - `p_ba9f` Green Channel Tier 1 vendor ranking is awarded to any logistics supplier holding a valid EcoVadis Gold rating.
  - `p_4b46` Platinum partner tier recognition requires an annual software revenue of at least $5,000,000 and 25 certified client implementations.
  - `p_0c4c` Express procurement channel access is granted to suppliers with at least five years of continuous operational history.
  - `p_81ec` Partner status at the Gold tier is granted to any vendor that either achieves an annual software revenue of at least $2,000,000 alongside a minimum of 10 certified client implementations, or maintains a valid ISO 27001 accreditation.

### B. Intended structure
- `m_aeef` (B1) [policy `p_81ec`] <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: Apex Tech's annual recurring revenue of $2.5 million meets the $2,000,000 threshold and its 15 customer implementations meet the minimum requirement of 10 implementations under the rule.
  - set 2: Apex Tech's active ISO 27001 certification satisfies the accreditation requirement under the rule.
- `m_b7fc` (D1) [policy `p_b875`] <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: Apex Tech meets Gold tier status and its $100,000 proposal exceeds the $75,000 co-investment requirement under the policy.
- `m_4677` (B2) [policy `p_ba9f`] <= (`e_4667`); gold after update: **keep**
  - set 1: Zenith Logistics holds an active EcoVadis Gold rating, fulfilling the requirement for Green Channel Tier 1 ranking.
- `u_84c2` supersedes `e_2787` (reliability high)
- decoy policies: `p_4b46`, `p_0c4c`
- final state after updates (gold action -> state): `m_aeef` keep -> holds; `m_4677` keep -> holds; `m_b7fc` keep -> holds

### C. Automated flags (for review, not verdicts)
- soft `groups 1/2` cross_group_entity: "Gold,Tier"

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

*World:* An evaluation of commercial partners and vendors for enterprise product distribution and service tier eligibility.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, ISO accreditation body register entry] Apex BioTech operates an ISO 13485 certified quality management facility.
- `e_5dd0` [2026-01-11, Official patent registry database extract] Apex BioTech maintains an active portfolio of 15 granted international patents.
- `e_0823` [2026-01-14, Executed customer operations sign-off record] Vanguard Tech completed 25 successful enterprise deployments with zero SLA breaches last year.
- `e_45ef` [2026-01-17, FDA enforcement database registry record] Apex BioTech holds a regulatory compliance record with zero FDA warning letters over five years.
- `e_fdcd` [2026-01-20, Regional power grid authority audit log] Luminary Solar generates 500 megawatts of renewable power per hour across its solar facilities.
- `e_f882` [2026-01-23, Certified policy document from Lloyd's syndicate] Aether Dynamics maintains a liability insurance policy covering up to $50 million in commercial losses.
- `e_660f` [2026-01-26, Deloitte audited annual financial report] Apex BioTech committed $12 million to its research and development budget during the recent fiscal year.
- memories:
  - `m_6c9c` Apex BioTech meets the technical capability criteria for medical distribution.
  - `m_cc95` Apex BioTech receives authorization for the MedTech Tier-1 Distribution License.
  - `m_ece3` Aether Dynamics fulfills the high-risk vendor coverage requirement.
  - `m_e062` Apex BioTech achieves prerequisite status for the Tier-1 distribution program.
  - `m_bda8` Vanguard Tech qualifies for the Premier Enterprise Support SLA.
  - `m_6d1e` Luminary Solar meets the green utility supplier threshold.
- update `u_99cf` [2026-01-29, Anonymous online discussion board] An unverified forum post claims Apex BioTech inflated its reported annual research expenditure.
- policies:
  - `p_cd31` A candidate attains prerequisite eligibility for tier-1 distribution when maintaining technical distribution eligibility alongside an accredited quality management facility.
  - `p_b65d` Full licensing under the tier-1 program is granted to candidates with prerequisite eligibility who demonstrate no regulatory compliance violations over a five-year period.
  - `p_b3f6` Clean energy supplier classification applies to power generation facilities producing an hourly output of at least 300 megawatts from renewable infrastructure.
  - `p_6aef` Specialized service level tiering is granted to corporate clients completing a minimum of 20 breach-free deployments within a single year.
  - `p_d3ca` Commercial partners qualify for expedited contract renewal if they maintain a quarterly transaction volume exceeding $5 million.
  - `p_8aeb` Technical distribution eligibility is awarded to an enterprise that either commits an annual research budget of at least $10 million or holds 10 or more active international patents.
  - `p_c629` A vendor receives preferred supplier status when achieving a customer satisfaction rating above 95% across three regional hubs.
  - `p_9e3e` Commercial vendor risk approval requires a vendor to hold operational liability protection valued at $25 million or higher.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: An annual research budget of $12 million satisfies the $10 million threshold required for technical distribution eligibility.
  - set 2: Holding 15 active patents satisfies the alternative requirement of at least 10 international patents for technical distribution eligibility.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Meeting technical distribution eligibility combined with operating an ISO 13485 certified quality management facility fulfills the prerequisite requirements.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Achieving prerequisite eligibility alongside a five-year record free of FDA warning letters qualifies Apex BioTech for the MedTech Tier-1 Distribution License.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Completing 25 breach-free deployments exceeds the threshold of 20 incident-free deployments needed for Premier Enterprise Support SLA.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: A renewable output of 500 megawatts per hour exceeds the 300 megawatt requirement for green utility supplier status.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: Possessing $50 million in liability insurance exceeds the $25 million coverage threshold for high-risk vendor approval.
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
