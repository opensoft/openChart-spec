## ADDED Requirements

### Requirement: BD-01 openChart works with no knowledge source, except for signing prescriptions
Every openChart capability SHALL work with no knowledge source connected, except signing a prescription, which PG-01 refuses. Allergy and medication lists, drafting a prescription (with every check shown as unavailable), encounters, notes, diagnoses, procedures, orders and intake SHALL be unaffected. The ratified standalone golden-intake tests SHALL keep passing.

#### Scenario: A deployment with no source
- **WHEN** a practice runs openChart with no source connected
- **THEN** clinicians keep the lists, draft prescriptions and document encounters, and no prescription can be signed

#### Scenario: Failure: a source outage would block charting
- **WHEN** the source is unavailable
- **THEN** only prescription signing is affected, under PG-02, and every other act proceeds

### Requirement: BD-02 No list, check or alert content goes to openPractice
openChart SHALL NOT send allergy entries, medication list entries, check records, alerts, overrides or flags to openPractice under any contract. This is consistent with `define-openpractice-boundary` CF-03 (not yet on main) and owner ruling 34. medXfactory and MedxEHR are named in this change only as cross-references. This change defines no interface to either.

#### Scenario: Failure: a publication would include an override
- **WHEN** a final encounter is published to openPractice and a prescription in it carried an override
- **THEN** no override, alert or list content is in any notification or read

### Requirement: BD-03 Lists and alerts map to FHIR R4-compatible resources at contract level, with no conformance claim
openChart SHALL define a FHIR R4-compatible mapping at contract level:
- allergy entries to AllergyIntolerance;
- medication list entries to MedicationStatement;
- openChart prescriptions to MedicationRequest, as in `define-clinical-acts-foundation`;
- alerts and their responses to DetectedIssue, with each override as a mitigation by the clinician;
- check records to Provenance.

openChart MUST NOT claim FHIR certification, profile conformance or validation against any implementation guide. A draft or entered-in-error entry SHALL NOT be exposed as active.

#### Scenario: An override is read
- **WHEN** an authorized consumer reads a signed prescription's alerts through an interoperability surface
- **THEN** it receives DetectedIssue-compatible items, each override as a mitigation with the clinician and reason

#### Scenario: Failure: a draft allergy would be read as active
- **WHEN** an interoperability read would include a draft allergy entry
- **THEN** the entry is omitted

### Requirement: BD-04 No PHI enters logs, and every check failure is visible
openChart's logs, error messages, diagnostics and coded reasons MUST NOT contain names, dates of birth, contact details, identifier values, medication or allergy text, or alert text. They SHALL reference prescriptions, checks and inputs by identifier and version only. A check that cannot run SHALL always be visible to the clinician (PC-02, KA-05), and SHALL never be visible only in a log.

#### Scenario: Failure: an adapter error is logged
- **WHEN** an adapter returns `source_unavailable` during a check
- **THEN** the log entry holds the check identifier, the error code and the time, and no medication or patient detail, and the clinician sees the unavailability on screen
