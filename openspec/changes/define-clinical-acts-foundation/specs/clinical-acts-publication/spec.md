## ADDED Requirements

### Requirement: PB-01 This change is the clinical-encounter capability that replaces the no-billable-facts placeholder
This change SHALL be the "separately governed openChart capability [that] records clinician-authored encounters, diagnoses and procedures" named by `define-openpractice-boundary` CF-06 (not yet on main). It does not edit that change. In a deployment where this change's encounter, diagnosis and procedure capabilities are built and enabled, and where `define-openpractice-boundary`'s clinical-fact publication surface is built, openChart SHALL report `billable_facts_supported: true` in its `capability.result` under `openpractice-ehr-clinical-facts/1.0`. In any other deployment, CF-06 SHALL keep applying: the capability result is false and every facts read returns `no_billable_facts`. Disabling this change's capabilities SHALL return the capability result to false at once (design call CD-24).

#### Scenario: Both capabilities are present
- **WHEN** a deployment has this change's diagnoses and procedures enabled and the boundary change's publication surface built
- **THEN** openChart's `capability.result` reports `billable_facts_supported: true`

#### Scenario: Failure: the boundary surface exists but this capability is disabled
- **WHEN** a deployment has the publication surface but this change's diagnoses and procedures are disabled
- **THEN** the capability result is false and every facts read returns `no_billable_facts`

### Requirement: PB-02 A signed, final encounter is published by reference under the clinical-facts contract
For a patient with an `active` `openpractice` link, when an encounter becomes `final`, openChart SHALL send `encounter.documentation_final` through the durable outbound delivery of `define-openpractice-boundary` PL-14, carrying only resource references (resource type, identifier, version) for the Encounter and for each final encounter diagnosis and final procedure that references it. An authorized `facts.result` read SHALL return, validated against the canonical schema pinned by digest in PL-04 (`6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec`):
- **Encounter:** act identifier and version; status (`final` and `amended` as `finished`); encounter types; period; location reference; participants, as practitioner references;
- **Condition:** each final `encounter_diagnosis`, as category `encounter-diagnosis`, with identifier, version, coding, rank and encounter reference;
- **Procedure:** each final procedure, with identifier, version, coding, quantity where documented, performed time, performer reference and encounter reference;
- **documentation_final:** `final: true`, with the signer reference and signing time of the encounter version's signature (EN-04).

Every coding SHALL carry the code system and code only, never the version or display (CF-01, FD-11). Practitioner, location and resource references SHALL be opaque and carry no name. openPractice receives references, never copies of notes or other content (openPractice EB-13, EB-16). A read for an encounter that is not `final`, `amended` or `entered_in_error` SHALL return `no_billable_facts` (design call CD-24).

#### Scenario: A linked patient's encounter is finalized
- **WHEN** a clinician signs a final encounter with one confirmed encounter diagnosis and one procedure for a patient with an active `openpractice` link
- **THEN** openChart sends `encounter.documentation_final` with three resource references, and an authorized read returns the encounter as `finished`, the diagnosis and procedure codings as system and code only, and `documentation_final` with the signer and time

#### Scenario: Failure: an in-progress encounter is read
- **WHEN** openPractice reads facts for an encounter that is still `in_progress`
- **THEN** openChart returns `no_billable_facts`

#### Scenario: Failure: the patient has no active link
- **WHEN** an encounter is finalized for a patient whose `openpractice` link is in `identity_review`, revoked or absent
- **THEN** openChart sends no notification and serves no read for that patient

### Requirement: PB-03 Amendments and retractions are published forward-only
When a published encounter is amended (EN-05), openChart SHALL send `clinical_fact.corrected`, with resource references to the new Encounter version and to every new or new-version Condition and Procedure, and `supersedes` references to the versions they replace. When a published encounter diagnosis or procedure is marked entered in error within an amendment, openChart SHALL send `clinical_fact.entered_in_error` with that resource's reference. When a published encounter is marked entered in error, openChart SHALL send `clinical_fact.entered_in_error` with the Encounter reference and the reference of every published Condition and Procedure on it, and a read SHALL return the encounter with status `entered-in-error`, no conditions, no procedures and `documentation_final.final` false. openChart MUST NOT silently overwrite a published fact or reuse a published version number.

#### Scenario: A diagnosis is corrected after publication
- **WHEN** a clinician amends a published encounter to correct its primary diagnosis code
- **THEN** openChart sends `clinical_fact.corrected` naming the new Encounter and Condition versions and superseding the old ones, and a read returns the new versions

#### Scenario: Failure: a published encounter is voided
- **WHEN** a clinician marks a published encounter entered in error
- **THEN** openChart sends `clinical_fact.entered_in_error` naming the encounter and its published facts, and a read returns status `entered-in-error` with no conditions or procedures

### Requirement: PB-04 Only final, clinician-signed encounter facts are ever published
openChart SHALL NOT publish under `openpractice-ehr-clinical-facts/1.0` any of these:
- a patient-reported statement or a clinical communication record (CF-02);
- a problem-list entry, clinical note text, order, prescription, draft or cancelled act;
- an encounter that carries a restricted act (CA-15);
- an encounter whose signature has an open co-signature requirement, until it is co-signed (design call CD-11);
- a fact that the canonical schema cannot represent, such as a code longer than the schema allows. For such an encounter, openChart SHALL publish nothing, serve no partial read, and record an integration exception with identifiers and a coded cause only.

#### Scenario: Failure: an order would be published
- **WHEN** a final encounter for a linked patient includes a released laboratory order
- **THEN** the order appears in no notification and no read

#### Scenario: Failure: a co-signature is still pending
- **WHEN** an encounter is signed by a clinician whose grant requires co-signature, and the co-signature is not yet recorded
- **THEN** openChart publishes nothing for it until the co-signature is recorded

#### Scenario: Failure: a code does not fit the contract
- **WHEN** a final encounter carries a procedure code longer than the canonical schema allows
- **THEN** openChart publishes nothing for that encounter and records an integration exception with identifiers and a coded cause

### Requirement: PB-05 Publication is optional and never blocks charting
Publication SHALL be optional. openChart SHALL open, document, sign, amend and void encounters, diagnoses and procedures exactly the same with no openPractice deployment, with a link in review, or while openPractice is unreachable (`define-openpractice-boundary` PL-15; ratified `expanded-patient-intake`). A delivery failure SHALL leave the message in the durable outbound store and SHALL NOT block or delay any clinical act.

#### Scenario: Standalone charting
- **WHEN** no openPractice is configured
- **THEN** encounters are documented and signed, and nothing is published

#### Scenario: Failure: openPractice is unreachable at signing
- **WHEN** openPractice is unreachable when a clinician signs a linked patient's encounter
- **THEN** the signature completes, and the notification waits in the durable store and is delivered later with its original `message_id`
