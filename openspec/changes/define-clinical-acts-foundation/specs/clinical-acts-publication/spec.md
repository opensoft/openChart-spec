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
When an encounter becomes `final`, openChart SHALL write an `encounter.documentation_final` notification to the durable outbound store of `define-openpractice-boundary` PL-14, in the same transaction, carrying only resource references (resource type, identifier, version). The references SHALL cover the Encounter and each published Condition and Procedure. openChart SHALL deliver the notification at once when the patient's `openpractice` link is `active`. While the link is in `identity_review`, it SHALL hold the notification as a pending final, under PB-03.

Before it writes the notification or serves a read, openChart SHALL run the integrity verifier of CA-08 over the encounter and every record it publishes. A record that fails is not published until the failure is resolved, and the failure is reported as CA-08 states.

An authorized `facts.result` read SHALL be served only on an `active` link. It SHALL be validated against the canonical schema pinned by digest in PL-04 (`6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec`), and SHALL return:
- **Encounter:** act identifier and version; status (`final` and `amended` as `finished`); encounter types; period; location reference; participants, as practitioner references;
- **Condition:** each final `encounter_diagnosis` whose verification status is `confirmed`, as category `encounter-diagnosis`, with identifier, version, coding, rank and encounter reference. A diagnosis that is `unconfirmed`, `provisional`, `differential` or `refuted` SHALL NOT be published. This rule is owner ruling 87 (design call CD-33);
- **Procedure:** each final procedure, with identifier, version, coding, quantity where documented, performed time, performer reference and encounter reference;
- **documentation_final:** `final: true`, with the signer reference and signing time of the encounter version's signature (EN-04).

Every coding SHALL carry the code system and code only, never the version or display (CF-01, FD-11). Practitioner, location and resource references SHALL be opaque and carry no name. openPractice receives references, never copies of notes or other content (openPractice EB-13, EB-16). A read for an encounter that is not `final` or `amended`, or that has been withdrawn under PB-03, SHALL return `no_billable_facts` (design call CD-24).

#### Scenario: A linked patient's encounter is finalized
- **WHEN** a clinician signs a final encounter with one confirmed encounter diagnosis and one procedure for a patient with an active `openpractice` link
- **THEN** openChart sends `encounter.documentation_final` with three resource references, and an authorized read returns the encounter as `finished`, the diagnosis and procedure codings as system and code only, and `documentation_final` with the signer and time

#### Scenario: Failure: a refuted diagnosis is never published
- **WHEN** a final encounter for an actively linked patient carries one confirmed and one `refuted` encounter diagnosis
- **THEN** the notification and the read include only the confirmed diagnosis, and the refuted one is never published

#### Scenario: Failure: an in-progress encounter is read
- **WHEN** openPractice reads facts for an encounter that is still `in_progress`
- **THEN** openChart returns `no_billable_facts`

#### Scenario: Failure: the link is in identity review at finalization
- **WHEN** an encounter is finalized while the patient's `openpractice` link is in `identity_review`
- **THEN** openChart sends nothing and serves no read now, and holds the documentation-final notification as a pending final under PB-03

#### Scenario: Failure: the patient has no link
- **WHEN** an encounter is finalized for a patient with no `openpractice` link
- **THEN** openChart queues and sends nothing, and serves no read

### Requirement: PB-03 Every correction or retraction of a published fact is queued, whatever the link state, and delivered forward-only
openChart SHALL write each of the following to the durable outbound store, in the same transaction as its cause, whatever the state of the patient's `openpractice` link (`active`, `identity_review`, `revoked` or `superseded`) (design call CD-35). Each item applies once the encounter or fact named in it has been published.
- **A published encounter is amended (EN-05) and can still be published:** `clinical_fact.corrected`, with resource references to the new Encounter version and to every new or new-version publishable Condition and Procedure, and `supersedes` references to the versions they replace.
- **A published Condition or Procedure is withdrawn:** its latest version could no longer be published under PB-02 and PB-04. Examples: a diagnosis later refuted, or otherwise amended away from `confirmed` (owner ruling 87; CD-33), amended to the `problem_list` role, or amended to a coding the canonical schema cannot represent; or a diagnosis or procedure marked entered in error. openChart SHALL send `clinical_fact.entered_in_error` with that resource's reference.
- **A published encounter is withdrawn:** its latest version could no longer be published, because it is marked entered in error, carries a restricted act (CA-15), or holds a fact the canonical schema cannot represent. openChart SHALL send `clinical_fact.entered_in_error` with the Encounter reference and the reference of every published Condition and Procedure on it (design call CD-36). Nothing more SHALL be published for that encounter. Every later read SHALL return `no_billable_facts`, the same read whatever the reason, so that a read never reveals a restricted act.

openChart SHALL deliver queued messages in the order of their causes, each with its original `message_id`:
- **`active` link:** at once.
- **`identity_review` link:** openChart SHALL hold every queued message and every pending final (PB-02). When the link returns to `active`, it SHALL deliver them in order. Before delivering a pending final, it SHALL re-evaluate it, sending only facts that are still final, confirmed and unrestricted.
- **Link that ends `revoked` or `superseded`:** openChart SHALL deliver every queued retraction, as pointers only, and SHALL deliver every queued correction as a `clinical_fact.entered_in_error` for the published versions it supersedes. It SHALL drop pending finals, which were never published, serve no read, and record the outcome with identifiers only (owner ruling 88; tension CT-15).

openChart MUST NOT silently overwrite a published fact or reuse a published version number.

#### Scenario: A diagnosis is corrected after publication
- **WHEN** a clinician amends a published encounter to correct its primary diagnosis code, on an active link
- **THEN** openChart sends `clinical_fact.corrected` naming the new Encounter and Condition versions and superseding the old ones, and a read returns the new versions

#### Scenario: Failure: a correction arrives while the link is in identity review
- **WHEN** a published encounter is amended while the patient's link is in `identity_review` for a date-of-birth hold
- **THEN** openChart queues `clinical_fact.corrected`, and delivers it, followed by any pending finals, as soon as the link returns to `active`

#### Scenario: Failure: the link is revoked while a correction is queued
- **WHEN** the link is revoked while a `clinical_fact.corrected` is held for it
- **THEN** openChart delivers a `clinical_fact.entered_in_error` for the superseded published versions, drops pending finals, and serves no read

#### Scenario: Failure: a restricted act is added to a published encounter
- **WHEN** a clinician adds a restricted diagnosis to an encounter whose facts were already published
- **THEN** openChart sends `clinical_fact.entered_in_error` for the Encounter and every published Condition and Procedure, and publishes nothing more for that encounter

#### Scenario: Failure: a published diagnosis is moved to the problem list
- **WHEN** a clinician amends a published encounter diagnosis to the `problem_list` role
- **THEN** openChart sends `clinical_fact.entered_in_error` for that Condition, and later reads omit it

#### Scenario: Failure: a published diagnosis is later refuted
- **WHEN** a clinician amends a published, confirmed encounter diagnosis to `refuted`
- **THEN** openChart sends `clinical_fact.entered_in_error` for that Condition, and later reads omit it

#### Scenario: Failure: a published encounter is voided
- **WHEN** a clinician marks a published encounter entered in error
- **THEN** openChart sends `clinical_fact.entered_in_error` naming the encounter and its published facts, and a later read returns `no_billable_facts`, exactly as it would for an encounter withdrawn because of a restricted act

### Requirement: PB-04 Only final, confirmed, clinician-signed encounter facts are ever published
openChart SHALL NOT publish under `openpractice-ehr-clinical-facts/1.0` any of these:
- a patient-reported statement or a clinical communication record (CF-02);
- a recommendation record (AN-09), an information record (AN-14), or any other addition that is not a decision signed off with authority (AN-07);
- an encounter diagnosis whose verification status is not `confirmed` (owner ruling 87; CD-33);
- a problem-list entry, clinical note text, order, prescription, draft or cancelled act;
- an encounter that carries a restricted act (CA-15). If the encounter was already published, PB-03 retracts it;
- an encounter whose signature has an open co-signature requirement, until it is co-signed (design call CD-11);
- a fact that the canonical schema cannot represent, such as a code longer than the schema allows. For such an encounter, openChart SHALL publish nothing, serve no partial read, and record an integration exception with identifiers and a coded cause only.

#### Scenario: Failure: an order would be published
- **WHEN** a final encounter for a linked patient includes a released laboratory order
- **THEN** the order appears in no notification and no read

#### Scenario: Failure: a provisional diagnosis would be published
- **WHEN** a final encounter carries an encounter diagnosis whose verification status is `provisional`
- **THEN** that diagnosis appears in no notification and no read

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
