# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* Assessment of client account qualifications and product program eligibility across commercial partners.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Signed corporate contract agreement] Apex Tech Solutions has maintained an active service contract for 18 months.
- `e_94fc` [2026-01-11, State department registry database] Solstice Retail holds an active state commercial merchant license.
- `e_0439` [2026-01-14, Certified compliance audit record] Apex Tech Solutions maintains two certified security officers on staff.
- `e_b5f7` [2026-01-17, Official billing system registry] Apex Tech Solutions maintains a monthly software spend of $60,000.
- `e_df05` [2026-01-20, Corporate governance portal document] Apex Tech Solutions submitted an executive board authorization statement.
- memories:
  - `m_c4d7` Apex Tech Solutions meets enterprise security compliance criteria.
  - `m_3f2d` Apex Tech Solutions qualifies for priority support routing.
  - `m_280b` Solstice Retail qualifies for tax-exempt wholesale purchasing.
  - `m_c5de` Apex Tech Solutions holds premier enterprise account status.
  - `m_5302` Apex Tech Solutions fulfills Platinum Partner status requirements.
  - `m_4b85` Grant Apex Tech Solutions access to the Platinum Partner program benefits.
- update `u_91ee` [2026-01-23, Official billing system registry] Apex Tech Solutions reduced its account subscription, dropping its monthly software spend to $35,000.
- policies:
  - `p_fe1d` An account qualifies for priority support routing if it holds premier enterprise account status.
  - `p_fbe6` An account is granted access to Platinum Partner program benefits if it fulfills Platinum Partner status requirements.
  - `p_b0aa` A business qualifies for tax-exempt wholesale purchasing if it holds an active state commercial merchant license.
  - `p_5cd1` An account fulfills Platinum Partner status requirements if it meets enterprise security compliance criteria and provides executive board authorization.
  - `p_1714` An account meets enterprise security compliance criteria if it qualifies for priority support routing and maintains at least two certified security officers.
  - `p_0087` An account holds premier enterprise account status if its monthly software spend is at least $50,000 and its active contract length exceeds 12 months.

### B. Intended structure
- `m_c5de` (B1) [policy `p_0087`] <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: A monthly software spend of $60,000 combined with an 18-month active contract satisfies the requirements of a $50,000 spend and a contract exceeding 12 months.
- `m_3f2d` (B2) [policy `p_fe1d`] <= (`m_c5de`); gold after update: **recompute**
  - set 1: Holding premier enterprise account status satisfies the single requirement for priority support routing.
- `m_c4d7` (B3) [policy `p_1714`] <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Qualifying for priority support routing alongside having two certified security officers meets both necessary criteria for enterprise security compliance.
- `m_5302` (B4) [policy `p_5cd1`] <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Meeting enterprise security compliance criteria together with submitting executive board authorization fulfills the Platinum Partner status requirements.
- `m_4b85` (D1) [policy `p_fbe6`] <= (`m_5302`); gold after update: **recompute**
  - set 1: Fulfilling Platinum Partner status requirements justifies granting access to the Platinum Partner program benefits.
- `m_280b` (B5) [policy `p_b0aa`] <= (`e_94fc`); gold after update: **keep**
  - set 1: Holding an active state commercial merchant license satisfies the requirement for tax-exempt wholesale purchasing.
- `u_91ee` supersedes `e_b5f7` (reliability high)

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

## s_3d821bdd07  (F2-000, product eligibility)

*World:* Evaluation of software application security compliance and operational criteria for software procurement.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Service level agreement contract] DataPulse Suite guarantees an operational uptime of 99.95%.
- `e_dfe6` [2026-01-11, Independent auditor summary report] CloudShield Pro maintains a valid SOC 2 Type II compliance report.
- `e_e50c` [2026-01-14, Official ISO certification registry] CloudShield Pro holds an active ISO/IEC 27001 certification.
- memories:
  - `m_2075` CloudShield Pro satisfies enterprise security compliance criteria.
  - `m_36f2` DataPulse Suite meets high-availability operational standards.
  - `m_7743` CloudShield Pro is cleared for network deployment.
- update `u_a152` [2026-01-17, Official ISO certification registry notice] CloudShield Pro's ISO/IEC 27001 certification was formally suspended.
- update `u_41fa` [2026-01-20, Auditing firm official bulletin] CloudShield Pro's SOC 2 Type II compliance report was revoked.
- policies:
  - `p_d10e` A software product satisfies enterprise security compliance criteria if it holds an active ISO/IEC 27001 certification or maintains a valid SOC 2 Type II compliance report.
  - `p_3b4c` A software product is cleared for network deployment if it satisfies enterprise security compliance criteria.
  - `p_4091` A software solution meets high-availability operational standards if its contractual operational uptime guarantee is at least 99.9%.

### B. Intended structure
- `m_2075` (B1) [policy `p_d10e`] <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: Holding an active ISO/IEC 27001 certification satisfies the enterprise security compliance policy requirement.
  - set 2: Maintaining a valid SOC 2 Type II compliance report satisfies the enterprise security compliance policy requirement.
- `m_7743` (D1) [policy `p_3b4c`] <= (`m_2075`); gold after update: **recompute**
  - set 1: Satisfying enterprise security compliance criteria fulfills the policy requirement for network deployment clearance.
- `m_36f2` (B2) [policy `p_4091`] <= (`e_1552`); gold after update: **keep**
  - set 1: A guaranteed operational uptime of 99.95% meets the required 99.9% threshold for high-availability operational standards.
- `u_a152` supersedes `e_e50c` (reliability high)
- `u_41fa` supersedes `e_dfe6` (reliability high)

### C. Automated flags (for review, not verdicts)
- soft `p_d10e` policy_shares_name: "IEC,ISO,SOC,Type"

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

## s_94a4bc8c87  (F3-000, product eligibility)

*World:* Assessment of commercial client eligibility for preferred tier status and financing terms.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Regional energy board audit record] Solaris Energy installed certified Grade-A commercial solar panels on its primary headquarters.
- `e_2787` [2026-01-11, Verified sales ledger record] Apex Innovations achieved an annual spending volume of $250,000.
- `e_124c` [2026-01-14, Partner portal verification registry] Apex Innovations holds an active Tier-1 Certified Partner accreditation.
- `e_ac4d` [2026-01-17, Official credit bureau statement] Apex Innovations recorded no late payments on its account during the past 12 months.
- `e_c8d5` [2026-01-20, Official CRM account database] Apex Innovations has maintained an active corporate account for three consecutive years.
- memories:
  - `m_4677` Solaris Energy qualifies for the Green Eco-Rebate grant.
  - `m_aeef` Apex Innovations qualifies for Enterprise Tier account benefits.
  - `m_b7fc` Apex Innovations is designated for extended 90-day invoice payment terms.
- update `u_84c2` [2026-01-23, Audited accounting report] Apex Innovations achieved a revised annual spending volume of $180,000.
- policies:
  - `p_ba9f` A business qualifies for the Green Eco-Rebate grant if it has installed certified Grade-A commercial solar panels on its primary headquarters.
  - `p_81ec` A client qualifies for Enterprise Tier account benefits either by maintaining an active corporate account for at least two years along with an annual spending volume of at least $200,000, or by holding an active Tier-1 Certified Partner accreditation.
  - `p_b875` A client is designated for extended 90-day invoice payment terms if they qualify for Enterprise Tier account benefits and have no late payments on their account during the past 12 months.

### B. Intended structure
- `m_aeef` (B1) [policy `p_81ec`] <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: Apex Innovations has maintained an active account for three years and achieved an annual spending volume of $250,000, satisfying the dual requirements for Enterprise Tier account benefits.
  - set 2: Apex Innovations holds an active Tier-1 Certified Partner accreditation, which independently satisfies the policy requirement for Enterprise Tier account benefits.
- `m_b7fc` (D1) [policy `p_b875`] <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: Apex Innovations qualifies for Enterprise Tier account benefits and has recorded no late payments in the past 12 months, fulfilling all conditions for extended 90-day invoice payment terms.
- `m_4677` (B2) [policy `p_ba9f`] <= (`e_4667`); gold after update: **keep**
  - set 1: Solaris Energy installed certified Grade-A commercial solar panels on its headquarters, fulfilling the policy condition for the Green Eco-Rebate grant.
- `u_84c2` supersedes `e_2787` (reliability high)

### C. Automated flags (for review, not verdicts)
- soft `p_ba9f` policy_shares_name: "Grade"
- soft `p_81ec` policy_shares_name: "Certified,Partner,Tier"
- soft `p_b875` policy_shares_name: "Tier"

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

## s_c41a0870a2  (F6-000, product eligibility)

*World:* An enterprise product portal evaluates customer accounts and vendors for product tier access and partner privileges.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, Central telemetry logs] Astra Dynamics has operated an active system integration for 14 consecutive months.
- `e_5dd0` [2026-01-11, Executed corporate contract portal] Astra Dynamics signed an annual service contract valued at $650,000.
- `e_0823` [2026-01-14, Verified insurer policy portal] Boreal Health maintains $2,000,000 in active commercial liability insurance.
- `e_45ef` [2026-01-17, Enterprise legal document repository] Astra Dynamics filed a signed mutual non-disclosure agreement with legal compliance.
- `e_fdcd` [2026-01-20, State health department public portal] Crestview Foods scored 96 out of 100 on its recent facility health inspection.
- `e_f882` [2026-01-23, Audited corporate financial statement] DynaTek Manufacturing maintains an average payment turnaround time of 18 days.
- `e_660f` [2026-01-26, Official ISO certification registry] Astra Dynamics holds a valid ISO-27001 compliance certificate.
- memories:
  - `m_6c9c` Astra Dynamics holds Preferred Enterprise Account status.
  - `m_cc95` Issue an Enterprise Partner Key to Astra Dynamics.
  - `m_ece3` DynaTek Manufacturing is eligible for accelerated payment terms.
  - `m_e062` Astra Dynamics is approved for the Unlimited API Integration Package.
  - `m_bda8` Boreal Health meets the liability insurance threshold for medical device distribution.
  - `m_6d1e` Crestview Foods meets the sanitary compliance requirement for vendor listing.
- update `u_99cf` [2026-01-29, Unverified community forum post] An anonymous online post claims Astra Dynamics' ISO-27001 certification was revoked.
- policies:
  - `p_6aef` A distributor meets the liability insurance threshold if they hold at least $1,000,000 in commercial liability coverage.
  - `p_cd31` A client is approved for the Unlimited API Integration Package if they are a Preferred Enterprise Account and have maintained an active integration for at least 12 months.
  - `p_9e3e` A supplier qualifies for accelerated payment terms if their documented payment turnaround time is 30 days or fewer.
  - `p_b3f6` A vendor meets the sanitary compliance requirement if their latest facility inspection score is at least 90.
  - `p_8aeb` An applicant qualifies as a Preferred Enterprise Account either by maintaining an annual contract exceeding $500,000 or by holding a verified ISO-27001 compliance certificate.
  - `p_b65d` An Enterprise Partner Key is issued to a client who is approved for the Unlimited API Integration Package and has a signed non-disclosure agreement on file.

### B. Intended structure
- `m_6c9c` (B1) [policy `p_8aeb`] <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: Astra Dynamics holds a valid ISO-27001 certificate, which satisfies the policy requirement for Preferred Enterprise Account status.
  - set 2: Astra Dynamics maintains an annual contract exceeding $500,000, which independently qualifies it as a Preferred Enterprise Account under the policy.
- `m_e062` (B2) [policy `p_cd31`] <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: Astra Dynamics is a Preferred Enterprise Account and has maintained an active integration for over 12 months, fulfilling both conditions for the Unlimited API Integration Package.
- `m_cc95` (D1) [policy `p_b65d`] <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: Astra Dynamics is approved for the Unlimited API Integration Package and has a signed non-disclosure agreement on file, satisfying the requirements to issue an Enterprise Partner Key.
- `m_bda8` (B3) [policy `p_6aef`] <= (`e_0823`); gold after update: **keep**
  - set 1: Boreal Health holds $2,000,000 in commercial liability coverage, satisfying the $1,000,000 insurance threshold for medical device distribution.
- `m_6d1e` (B4) [policy `p_b3f6`] <= (`e_fdcd`); gold after update: **keep**
  - set 1: Crestview Foods achieved a health inspection score of 96, satisfying the minimum score of 90 required for sanitary compliance.
- `m_ece3` (B5) [policy `p_9e3e`] <= (`e_f882`); gold after update: **keep**
  - set 1: DynaTek Manufacturing maintains an 18-day payment turnaround time, meeting the requirement of 30 days or fewer for accelerated payment terms.
- `u_99cf` retracts `e_660f` (reliability low)

### C. Automated flags (for review, not verdicts)
- soft `p_8aeb` policy_shares_name: "ISO"

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
