# Renderer review sheet

## s_d13e3034f6  (F1-000, product eligibility)

*World:* A financial institution is evaluating a customer's application for a premium credit card and a company's eligibility for a business loan.

### A. System view (judge C7 from this alone)
- `e_f61e` [2026-01-08, Credit bureau report] Sarah Chen's current FICO credit score is 780.
- `e_94fc` [2026-01-11, Certified company financial audit] Alpha Solutions Inc.'s total revenue for the previous fiscal year was $5,000,000.
- `e_0439` [2026-01-14, National Financial Registry] No bankruptcies have been filed by Sarah Chen in the past seven years.
- `e_b5f7` [2026-01-17, Official tax records] Sarah Chen's verified annual income for the last year was $150,000.
- `e_df05` [2026-01-20, Internal banking records] Sarah Chen has maintained a primary checking account with our bank for over five years without any overdrafts.
- memories:
  - `m_c4d7` Sarah Chen satisfies the advanced eligibility requirements for the premium credit card.
  - `m_3f2d` Sarah Chen's preliminary eligibility for the premium credit card is established.
  - `m_280b` Alpha Solutions Inc. has met the minimum revenue requirement for a medium-sized business loan.
  - `m_c5de` Sarah Chen meets the initial financial criteria for a premium credit card.
  - `m_5302` Sarah Chen fully qualifies for the Black Diamond Premium Credit Card.
  - `m_4b85` Recommend Sarah Chen's application for the Black Diamond Premium Credit Card be approved.
- update `u_91ee` [2026-01-23, Revised official tax record] A corrected tax filing indicates Sarah Chen's annual income is $145,000.

### B. Intended structure
- `m_c5de` (B1) <= (`e_b5f7` AND `e_f61e`); gold after update: **recompute**
  - set 1: Sarah's initial financial standing for the card is determined by considering both her high annual income and her excellent credit score.
- `m_3f2d` (B2) <= (`m_c5de`); gold after update: **recompute**
  - set 1: Sarah's preliminary eligibility for the card is confirmed if her initial financial criteria are met.
- `m_c4d7` (B3) <= (`m_3f2d` AND `e_0439`); gold after update: **recompute**
  - set 1: Sarah's advanced eligibility is met if her preliminary eligibility is established and she has no recent bankruptcies.
- `m_5302` (B4) <= (`m_c4d7` AND `e_df05`); gold after update: **recompute**
  - set 1: Sarah's full qualification for the card is confirmed if she satisfies the advanced eligibility requirements and has a positive long-standing banking relationship.
- `m_4b85` (D1) <= (`m_5302`); gold after update: **recompute**
  - set 1: The decision to recommend approval for the card is made if Sarah fully qualifies for it.
- `m_280b` (B5) <= (`e_94fc`); gold after update: **keep**
  - set 1: Alpha Solutions Inc.'s eligibility for a medium-sized business loan is supported by its significant last fiscal year revenue.
- `u_91ee` supersedes `e_b5f7` (reliability high)

### Checklist (record pass/fail + reason in the CSV)
- [ ] **C1_meaning** Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan).
- [ ] **C2_and** Within each justification set, all facts together entail the conclusion, and dropping any one breaks it.
- [ ] **C3_or** Each alternative justification set alone entails the conclusion, using genuinely different facts.
- [ ] **C4_updates** Each update says what its relation requires (retracts / supersedes with a new value / hedges), speaks only about its target, and its source matches the stated reliability.
- [ ] **C5_sources** Evidence source descriptions match their reliability (high / medium / low).
- [ ] **C6_distractors** Facts and memories in different groups are unrelated: nothing in one bears on another.
- [ ] **C7_no_reveal** Read as the system would (system view only): the wording does not reveal which facts support which memory, beyond what the meaning itself implies.

## s_3d821bdd07  (F2-000, product eligibility)

*World:* The company evaluates customer accounts for eligibility to various software products and features.

### A. System view (judge C7 from this alone)
- `e_1552` [2026-01-08, Billing Department Invoice Status] Customer Y successfully paid the annual fee for 'Product B Advanced Features' on October 10, 2026.
- `e_dfe6` [2026-01-11, Learning Management System Report] Customer X has completed the mandatory 'Product A Onboarding' training module on September 28, 2026.
- `e_e50c` [2026-01-14, CRM System Record] Customer X's account shows an active 'Premium Support' subscription as of October 1, 2026.
- memories:
  - `m_2075` Customer X is eligible to receive Product A.
  - `m_36f2` Customer Y's account has access to Product B Advanced Features.
  - `m_7743` Provision Product A license to Customer X.
- update `u_a152` [2026-01-17, CRM System Update Log] Customer X's 'Premium Support' subscription status was updated to 'Inactive' effective October 15, 2026.
- update `u_41fa` [2026-01-20, LMS Administrator Correction] The 'Product A Onboarding' module completion for Customer X was an error; their status is now 'Incomplete'.

### B. Intended structure
- `m_2075` (B1) <= (`e_e50c`) **OR** (`e_dfe6`); gold after update: **recompute**
  - set 1: If Customer X has an active Premium Support subscription, they are eligible for Product A.
  - set 2: If Customer X completed the mandatory Product A Onboarding training, they are eligible for Product A.
- `m_7743` (D1) <= (`m_2075`); gold after update: **recompute**
  - set 1: If Customer X is eligible to receive Product A, then a Product A license should be provisioned for them.
- `m_36f2` (B2) <= (`e_1552`); gold after update: **keep**
  - set 1: If Customer Y successfully paid the annual fee for 'Product B Advanced Features', then their account has access to those features.
- `u_a152` supersedes `e_e50c` (reliability high)
- `u_41fa` supersedes `e_dfe6` (reliability high)

### Checklist (record pass/fail + reason in the CSV)
- [ ] **C1_meaning** Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan).
- [ ] **C2_and** Within each justification set, all facts together entail the conclusion, and dropping any one breaks it.
- [ ] **C3_or** Each alternative justification set alone entails the conclusion, using genuinely different facts.
- [ ] **C4_updates** Each update says what its relation requires (retracts / supersedes with a new value / hedges), speaks only about its target, and its source matches the stated reliability.
- [ ] **C5_sources** Evidence source descriptions match their reliability (high / medium / low).
- [ ] **C6_distractors** Facts and memories in different groups are unrelated: nothing in one bears on another.
- [ ] **C7_no_reveal** Read as the system would (system view only): the wording does not reveal which facts support which memory, beyond what the meaning itself implies.

## s_94a4bc8c87  (F3-000, product eligibility)

*World:* An AI assistant evaluates customer eligibility for various products based on provided criteria.

### A. System view (judge C7 from this alone)
- `e_4667` [2026-01-08, Site Survey Report, high] The property at 123 Oak Street has a south-facing roof with minimal shading.
- `e_2787` [2026-01-11, Credit Bureau Report, high] Sarah Chen's credit score is reported as 750.
- `e_124c` [2026-01-14, Vehicle Manufacturer Specifications, high] Sarah Chen's current vehicle is a 2022 Honda Civic, equipped with advanced safety features.
- `e_ac4d` [2026-01-17, Application Form, high] The requested coverage limit for property damage is $100,000.
- `e_c8d5` [2026-01-20, DMV Official Report, high] The applicant, Sarah Chen, has maintained a clean driving record for 5 consecutive years.
- memories:
  - `m_4677` The 123 Oak Street property is suitable for the EcoBoost Solar Panel System installation.
  - `m_aeef` Sarah Chen is eligible for the Premium Shield Auto Insurance package.
  - `m_b7fc` Recommend approving Sarah Chen for the Premium Shield Auto Insurance policy.
- update `u_84c2` [2026-01-23, Credit Bureau Update, high] Sarah Chen's updated credit score is 680, reported on October 18, 2026.

### B. Intended structure
- `m_aeef` (B1) <= (`e_c8d5` AND `e_2787`) **OR** (`e_124c`); gold after update: **keep**
  - set 1: If the applicant has a clean driving record and a credit score of 750, they are eligible for the package.
  - set 2: If the applicant's vehicle is a 2022 Honda Civic with advanced safety features, they are eligible for the package.
- `m_b7fc` (D1) <= (`m_aeef` AND `e_ac4d`); gold after update: **keep**
  - set 1: If Sarah Chen is eligible for the Premium Shield package and the requested coverage limit is $100,000, then the policy should be approved.
- `m_4677` (B2) <= (`e_4667`); gold after update: **keep**
  - set 1: If the property at 123 Oak Street has a south-facing roof with minimal shading, it is suitable for the solar panel system.
- `u_84c2` supersedes `e_2787` (reliability high)

### Checklist (record pass/fail + reason in the CSV)
- [ ] **C1_meaning** Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan).
- [ ] **C2_and** Within each justification set, all facts together entail the conclusion, and dropping any one breaks it.
- [ ] **C3_or** Each alternative justification set alone entails the conclusion, using genuinely different facts.
- [ ] **C4_updates** Each update says what its relation requires (retracts / supersedes with a new value / hedges), speaks only about its target, and its source matches the stated reliability.
- [ ] **C5_sources** Evidence source descriptions match their reliability (high / medium / low).
- [ ] **C6_distractors** Facts and memories in different groups are unrelated: nothing in one bears on another.
- [ ] **C7_no_reveal** Read as the system would (system view only): the wording does not reveal which facts support which memory, beyond what the meaning itself implies.

## s_c41a0870a2  (F6-000, product eligibility)

*World:* This scenario involves determining a customer's eligibility for various financial products and services offered by a bank.

### A. System view (judge C7 from this alone)
- `e_3dc4` [2026-01-08, high] The client actively holds an investment portfolio with our firm.
- `e_5dd0` [2026-01-11, high] Client's average daily balance across all savings accounts exceeds $12,000 over the past year.
- `e_0823` [2026-01-14, high] The business's gross revenue was reported as $620,000 in the last fiscal year.
- `e_45ef` [2026-01-17, high] The 'Elite Savings Account' currently offers a 1.50% annual percentage yield promotion.
- `e_fdcd` [2026-01-20, high] The residential property address is outside any designated flood hazard zone.
- `e_f882` [2026-01-23, high] The customer has maintained a Platinum-tier credit card for over six years.
- `e_660f` [2026-01-26, high] The client's current credit score, reported by TransUnion, is 745.
- memories:
  - `m_6c9c` The customer satisfies the primary financial requirements for premium banking products.
  - `m_cc95` Recommend the Elite Savings Account with the current promotional rate.
  - `m_ece3` The customer is eligible for Platinum Member Club benefits.
  - `m_e062` The customer qualifies for the Elite Savings Account tier.
  - `m_bda8` The small business meets the minimum revenue criteria for a commercial loan.
  - `m_6d1e` The property is eligible for a standard homeowner's insurance policy.
- update `u_99cf` [2026-01-29, low] A temporary system error caused some credit scores to be inaccurately displayed recently.

### B. Intended structure
- `m_6c9c` (B1) <= (`e_660f`) **OR** (`e_5dd0`); gold after update: **keep**
  - set 1: If the client's credit score is above 700, they meet a key financial criterion for premium products.
  - set 2: If the client's average daily balance is over $10,000, they meet a key financial criterion for premium products.
- `m_e062` (B2) <= (`m_6c9c` AND `e_3dc4`); gold after update: **keep**
  - set 1: If the customer meets primary financial criteria and holds an investment portfolio, they qualify for the Elite Savings Account tier.
- `m_cc95` (D1) <= (`m_e062` AND `e_45ef`); gold after update: **keep**
  - set 1: If the customer qualifies for the Elite Savings Account tier and there is a current promotional rate, recommending it with that rate is appropriate.
- `m_bda8` (B3) <= (`e_0823`); gold after update: **keep**
  - set 1: If the business revenue exceeds $500,000, it satisfies the minimum revenue threshold for a small business loan.
- `m_6d1e` (B4) <= (`e_fdcd`); gold after update: **keep**
  - set 1: If the property is located in a low-risk flood zone, it is eligible for standard homeowners insurance coverage.
- `m_ece3` (B5) <= (`e_f882`); gold after update: **keep**
  - set 1: If the customer has held a high-tier credit card for over five years, they qualify for Platinum Club membership.
- `u_99cf` retracts `e_660f` (reliability low)

### Checklist (record pass/fail + reason in the CSV)
- [ ] **C1_meaning** Each text says what its node is meant to say (evidence = a fact; memory = a conclusion or plan).
- [ ] **C2_and** Within each justification set, all facts together entail the conclusion, and dropping any one breaks it.
- [ ] **C3_or** Each alternative justification set alone entails the conclusion, using genuinely different facts.
- [ ] **C4_updates** Each update says what its relation requires (retracts / supersedes with a new value / hedges), speaks only about its target, and its source matches the stated reliability.
- [ ] **C5_sources** Evidence source descriptions match their reliability (high / medium / low).
- [ ] **C6_distractors** Facts and memories in different groups are unrelated: nothing in one bears on another.
- [ ] **C7_no_reveal** Read as the system would (system view only): the wording does not reveal which facts support which memory, beyond what the meaning itself implies.
