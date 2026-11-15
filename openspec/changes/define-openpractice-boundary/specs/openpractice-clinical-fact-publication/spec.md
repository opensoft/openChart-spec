## ADDED Requirements

### Requirement: CF-01 openChart publishes billing-relevant clinical facts through the versioned contract
openChart SHALL publish the clinical facts that openPractice needs for charge capture under contract `openpractice-ehr-clinical-facts/1.0`, validated against the canonical schema that PL-04 names. Publication has three parts:
- **Pointer-only notifications** (`encounter.documentation_final`, `clinical_fact.corrected`, `clinical_fact.entered_in_error`). These carry resource references and no clinical content.
- **A `capability.result`** stating whether openChart supports billable facts.
- **Authenticated FHIR R4-compatible `facts.result` reads**, containing:
  - Encounter: identifier, status, type, period, location and participating practitioners;
  - encounter-diagnosis Condition: coding, rank and encounter reference, for `confirmed` diagnoses only (ruling 87);
  - Procedure: coding, quantity where documented, performed time, performer and encounter reference;
  - a documentation-final indicator with signer reference and signed time.

Codings SHALL carry a code system and a code only, never descriptor text. Publication SHALL be limited to patients with an `active` `openpractice` link, and to integration identities authorized for the billing purpose. The one exception is ruling 88. After a link ends `revoked` or `superseded`, openChart SHALL still deliver pointer-only retractions of facts it already published under that link (CF-04). It SHALL publish no new fact and serve no read for that patient. This is consistent with `define-clinical-acts-foundation` and its tension CT-15.

#### Scenario: Documentation becomes final
- **WHEN** a clinician finalizes an encounter for a linked patient, once a clinical-encounter capability exists
- **THEN** openChart sends a pointer-only notification, and an authorized read returns the encounter, diagnoses, procedures and documentation-final indicator

#### Scenario: Patient not linked
- **WHEN** an encounter is finalized for a patient with no active `openpractice` identifier
- **THEN** openChart sends no notification and serves no read for that patient

#### Scenario: A retraction after the link is revoked
- **WHEN** a fact published under a link is retracted after that link is revoked
- **THEN** openChart delivers the pointer-only retraction, publishes nothing new and serves no read for that patient (ruling 88)

#### Scenario: Failure: an unconfirmed diagnosis
- **WHEN** a finalized encounter carries a diagnosis that is not `confirmed`
- **THEN** openChart does not publish that diagnosis (ruling 87)

### Requirement: CF-02 Only clinician-authored final documentation is published as billable
openChart SHALL mark a fact billable only when it comes from clinician-authored documentation that is final and signed. Patient-reported statements MUST NOT be published as diagnoses or procedures. This covers `OC Condition Statement` and every other intake family, consistent with the ratified rule that intake confers no clinician or autonomous authority.

#### Scenario: Patient-reported condition
- **WHEN** a linked patient's accepted intake includes a patient-reported condition
- **THEN** no encounter diagnosis is published from it

### Requirement: CF-03 Publication is minimum necessary and never by database access
Reads SHALL return only the fields the canonical schema defines. openChart MUST NOT expose note text, medication lists, results or orders through this contract. It SHALL serve the contract only through its versioned API, and MUST NOT give openPractice database or table access, even when both share a Frappe site.

#### Scenario: A consumer asks for note text
- **WHEN** a read asks for an encounter's note text
- **THEN** openChart returns only the schema's fields

### Requirement: CF-04 Corrections and retractions are published as new versions
openChart SHALL publish a corrected fact as a new version that references the version it supersedes, and a retraction as an explicit entered-in-error notification. It MUST NOT silently overwrite a published fact.

A published diagnosis that is later refuted SHALL be retracted (ruling 87). Retractions SHALL be delivered whatever the link state, under CF-01's exception (ruling 88). A retraction reason code is to be added to `openpractice-ehr-clinical-facts` by the follow-up change of ruling 93 (ruling 89). Until this change re-pins to that revision, a retraction carries no reason code.

#### Scenario: A diagnosis is corrected after publication
- **WHEN** a clinician corrects a published diagnosis
- **THEN** openChart sends `clinical_fact.corrected`, and the read returns the new version with a reference to the superseded one

#### Scenario: A published diagnosis is refuted
- **WHEN** a clinician amends a published diagnosis so that it is no longer `confirmed`
- **THEN** openChart sends `clinical_fact.entered_in_error` for it, and no later read returns it as billable (ruling 87)

### Requirement: CF-05 openChart owns no billing or accounting
openChart SHALL NOT create or store charges, claims, receivables, payments, refunds or accounting postings. It SHALL NOT produce FHIR billing resources such as ChargeItem or Claim, and SHALL NOT integrate with any accounting system. It SHALL NOT request or store guarantor, coverage or financial data from openPractice under either contract at version 1.0.

#### Scenario: A billing feature is proposed for openChart
- **WHEN** a plan proposes generating charges or accounting entries in openChart
- **THEN** the plan is out of scope for openChart; that work belongs to openPractice

### Requirement: CF-06 Until a clinical-encounter capability exists, openChart reports no billable facts
Until a separately governed openChart capability records clinician-authored encounters, diagnoses and procedures, openChart SHALL report `billable_facts_supported: false` in its `capability.result`. Every `facts.result` read SHALL return `no_billable_facts`, and openChart SHALL NOT substitute patient-reported statements. While this holds, openPractice may enter charges for linked patients manually, marked as manual.

#### Scenario: openPractice asks before encounters exist
- **WHEN** openPractice reads the capability and facts for a linked patient before the clinical-encounter capability exists
- **THEN** the capability result is false, facts reads return `no_billable_facts`, and nothing is published from intake statements
