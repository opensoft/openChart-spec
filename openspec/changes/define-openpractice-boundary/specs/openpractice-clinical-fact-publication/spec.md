## ADDED Requirements

### Requirement: openChart publishes billing-relevant clinical facts through the versioned contract
openChart SHALL publish the clinical facts that openPractice needs for charge capture under contract `openpractice-ehr-clinical-facts/1.0`, in two forms.

**Pointer-only notifications.** These are `encounter.documentation_final`, `clinical_fact.corrected` and `clinical_fact.entered_in_error`. They carry resource references and no clinical content.

**Authenticated FHIR R4-compatible reads**, limited to these resources and fields:
- Encounter: identifier, status, type, period, location and participating practitioners;
- Condition in the encounter-diagnosis category: code system, code, rank and encounter reference;
- Procedure: code system, code, quantity where documented, performed time, performer and encounter reference;
- a documentation-final indicator with signer reference and signed time.

Publication SHALL be limited to patients with an `active` `openpractice` link and to integration identities authorized for the billing purpose.

#### Scenario: An encounter's documentation becomes final
- **WHEN** a clinician finalizes the documentation of an encounter for a linked patient
- **THEN** openChart sends an `encounter.documentation_final` notification with references only, and an authorized openPractice read returns the encounter, its encounter diagnoses and its procedures with the documentation-final indicator

#### Scenario: A patient has no openPractice link
- **WHEN** an encounter is finalized for a patient with no active `openpractice` identifier
- **THEN** openChart sends no notification and serves no read under this contract for that patient

### Requirement: Only clinician-authored final documentation is published as billable
openChart SHALL mark a fact billable only when it comes from clinician-authored documentation that is final and signed. Patient-reported statements MUST NOT be published as diagnoses or procedures under this contract. This covers `OC Condition Statement` and every other intake statement family. The rule is consistent with the ratified requirement that intake does not confer clinician or autonomous authority.

#### Scenario: A patient reported a condition at intake
- **WHEN** a linked patient's accepted intake includes a patient-reported condition statement
- **THEN** openChart publishes no encounter diagnosis from it

### Requirement: Publication is minimum necessary and never by database access
Reads under this contract SHALL return only the fields the contract defines. openChart MUST NOT expose note text, medication lists, results or orders through this contract. It SHALL serve the contract only through its versioned API surface, and MUST NOT give openPractice database or table access, even when both applications share a Frappe site.

#### Scenario: A consumer asks for note text
- **WHEN** a read under this contract asks for an encounter's note text
- **THEN** openChart returns only the contract's defined fields and no note text

### Requirement: Corrections and retractions are published as new versions
openChart SHALL publish a corrected fact as a new version that references the version it supersedes, and a retraction as an explicit entered-in-error signal. openChart MUST NOT silently overwrite a fact it has already published.

#### Scenario: A diagnosis is corrected after publication
- **WHEN** a clinician corrects an encounter diagnosis that was already published
- **THEN** openChart publishes a `clinical_fact.corrected` notification, and the read returns the new version with a reference to the superseded one

### Requirement: openChart owns no billing or accounting
openChart SHALL NOT create or store charges, claims, receivables, payments, refunds or accounting postings. It SHALL NOT produce FHIR billing resources such as ChargeItem or Claim under this contract, and SHALL NOT integrate with any accounting system. Under either openPractice boundary contract at version 1.0, openChart SHALL NOT request or store guarantor, coverage or financial data from openPractice.

#### Scenario: A billing feature is proposed for openChart
- **WHEN** a feature plan proposes generating charges or accounting entries inside openChart
- **THEN** the plan is out of scope for openChart and belongs to openPractice

### Requirement: Billable publication waits for a governed clinical-encounter capability
Until a separately governed openChart capability records clinician-authored encounters, diagnoses and procedures, openChart SHALL publish no billable facts under this contract. During that period it SHALL answer reads with an explicit no-billable-facts result rather than substituting patient-reported statements.

#### Scenario: openPractice reads facts before encounters exist in openChart
- **WHEN** openPractice reads billable facts for a linked patient while openChart has no clinical-encounter capability
- **THEN** openChart returns an explicit no-billable-facts result and publishes nothing from intake statements
