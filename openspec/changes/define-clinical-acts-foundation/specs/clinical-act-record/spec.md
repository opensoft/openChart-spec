## ADDED Requirements

### Requirement: CA-01 One clinical act model covers six act classes under a published content schema
openChart SHALL record clinician-authored clinical content as clinical acts of exactly six act classes: `encounter`, `clinical_note`, `diagnosis_of_record`, `procedure_performed`, `order` and `prescription`. Every act SHALL share one envelope: act identifier and version, act class, act type, the openChart patient, status, author, recording time, signatures, amendment links, co-signature, derivation provenance and lifecycle events (design call CD-1). Each act SHALL reference exactly one `OC Patient` through the openChart triple (openChart issuer, `openchart`, `OC Patient` identifier). An external identifier MUST NOT replace it.

The canonical representation of one act version SHALL be contract `openchart-clinical-act-content/1.0`, schema `contracts/openchart-clinical-act-content-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-clinical-act-content:1.0`, identified by the SHA-256 recorded in `contracts/SHA256SUMS`. Each class's clinical content SHALL be addressable as `$defs/<class>Content`, so that another governed contract can pin it by digest (design call CD-28). A breaking change SHALL need a new MAJOR version and a new digest. An act class not in this list SHALL be refused.

#### Scenario: An act is stored and read back
- **WHEN** a clinician signs a clinical note for a patient
- **THEN** openChart stores one act of class `clinical_note` linked to that patient's `OC Patient`, and its read representation validates against the schema at the recorded digest

#### Scenario: Failure: an unknown act class is submitted
- **WHEN** a client submits an act of class `treatment_plan_change` or `immunization`
- **THEN** openChart refuses it with a coded reason and stores nothing

### Requirement: CA-02 Every act has a named clinician author, and the author type accepts only clinician
Every act version SHALL carry an author: an author type, the named author's reference, the author's clinical role and the reference of the role grant the author acted under (the authority basis). In this change the author type SHALL accept exactly one value, `clinician`: a named human who holds an openChart clinical role grant (AU-02) and acts through their own authenticated openChart session (design calls CD-2 and CD-3). openChart MUST refuse any act whose author type is anything else, including `ai`, `agent`, `system`, `patient` or `unknown`, and MUST refuse an act whose author is not a named human. Only a later governed change may add an author type, in a new MINOR version of the contract; this field is the hook that `define-ai-authored-clinical-records` (not yet on main) builds on.

#### Scenario: A clinician authors a diagnosis
- **WHEN** a named clinician with a diagnosis grant records a diagnosis of record
- **THEN** the act carries author type `clinician`, the clinician's reference, the role `clinician` and the grant version

#### Scenario: Failure: an act arrives with author type ai
- **WHEN** any caller submits an act whose author type is `ai`
- **THEN** openChart refuses it and stores nothing, whatever authority or grant the request claims

#### Scenario: Failure: an integration identity tries to author an act
- **WHEN** an integration identity or automated process with no named human author submits an order
- **THEN** openChart refuses it and stores nothing

### Requirement: CA-03 Each act class has a closed status lifecycle
Every act SHALL have exactly one status from its class's closed list, and SHALL move only by the transitions below (design call CD-4). Each transition SHALL be recorded as an attributed, dated lifecycle event. openChart MUST refuse any other transition.

| Act class | Statuses | Transitions |
|---|---|---|
| `encounter` | `in_progress`, `final`, `amended`, `cancelled`, `entered_in_error` | `in_progress` → `final` (signed) or `cancelled`; `final` or `amended` → `amended` (new signed version) or `entered_in_error` |
| `clinical_note`, `diagnosis_of_record`, `procedure_performed` | `draft`, `final`, `amended`, `cancelled`, `entered_in_error` | `draft` → `final` (signed) or `cancelled`; `final` or `amended` → `amended` (new signed version) or `entered_in_error` |
| `order`, `prescription` | `draft`, `pending_release`, `released`, `completed`, `discontinued`, `cancelled`, `entered_in_error` | `draft` → `pending_release` or `released` (signed) or `cancelled`; `pending_release` → `released`, `pending_release` (new signed version), `cancelled` or `entered_in_error`; `released` → `completed`, `discontinued` or `entered_in_error` |

`amended` SHALL apply only to a version after the first. `cancelled` SHALL mean the act never took effect. `entered_in_error` SHALL mean the act was recorded in error (CA-06).

#### Scenario: A draft note is signed
- **WHEN** the author signs a draft clinical note
- **THEN** its status becomes `final`, with a `signed` lifecycle event naming the signer and time

#### Scenario: Failure: an illegal transition is attempted
- **WHEN** a user tries to move a `completed` order back to `released`, or a `cancelled` note to `final`
- **THEN** openChart refuses the transition and the act is unchanged

### Requirement: CA-04 Signing is an explicit, attested act by the named signer
An act SHALL take a signed status only when the named signer performs an explicit signing action through their own authenticated openChart session. openChart SHALL require re-authentication at the moment of signing; the mechanism is decided in planning (design call CD-10). A signature SHALL bind the signer, the signer's role, the role grant and its version, an attestation statement code and version, the signing time and the SHA-256 of the canonical content signed (design call CD-9). openChart SHALL check, at the moment of signing, that the signer holds a grant in force with sign scope for the act class and act type (AU-04). It MUST refuse a signature on content whose digest differs from the content shown to the signer, a signature applied by anyone on another person's behalf, and a signature by any non-human actor.

#### Scenario: A clinician signs an encounter
- **WHEN** a clinician with encounter sign scope re-authenticates and signs an encounter
- **THEN** the signature records the clinician, role, grant version, attestation code and version, time and content digest

#### Scenario: Failure: a signer's grant has lapsed
- **WHEN** a clinician whose diagnosis grant ended yesterday tries to sign a diagnosis
- **THEN** openChart refuses the signature, the diagnosis stays `draft`, and the refusal is recorded with a coded reason

#### Scenario: Failure: content changed after it was shown
- **WHEN** the content digest at signing differs from the digest of the content displayed to the signer
- **THEN** openChart refuses the signature and asks the signer to review the current content

### Requirement: CA-05 Signed content is never edited; an amendment is a new version
The content of a signed act version MUST NOT be edited in place or deleted. A change to signed content SHALL be recorded as a new version of the same act that references the version it supersedes, states an amendment reason, and carries its own author and signature (design call CD-5). Every prior version SHALL remain stored and readable by authorized users, with the current version marked. A new version MAY be authored by any clinician who holds sign scope for that act class, and the original author SHALL be shown as the author of the superseded version. Before signing, a draft MAY be revised; every revision SHALL be audited, and an abandoned draft SHALL be closed as `cancelled`, never deleted (design call CD-8).

#### Scenario: A clinician corrects a signed diagnosis code
- **WHEN** a clinician amends a final diagnosis to a different code with a reason
- **THEN** version 2 records the new code, references version 1, carries the clinician's signature and status `amended`, and version 1 stays readable

#### Scenario: Failure: someone edits signed content in place
- **WHEN** a user or extension tries to change the text of a final clinical note in place
- **THEN** openChart refuses the edit, and the note is unchanged

#### Scenario: Failure: someone deletes a signed act
- **WHEN** a user tries to delete a signed order
- **THEN** openChart refuses the deletion; only an entered-in-error mark, a discontinuation or an amendment can change its effect

### Requirement: CA-06 An act recorded in error is marked entered in error, never deleted
openChart SHALL let the act's author, a clinician with sign scope for the act class, or the medical director mark a signed act `entered_in_error`, with actor, time and a coded reason, as an attributed lifecycle event (design call CD-7). The act's content and history SHALL stay stored for audit. An entered-in-error act SHALL stop having clinical effect, SHALL be shown labelled as entered in error wherever it appears, and SHALL NOT count as an active diagnosis, procedure, order or prescription. This mark is the void that `define-ai-authored-clinical-records` (not yet on main) names. A draft SHALL be cancelled instead.

#### Scenario: An order on the wrong patient is voided
- **WHEN** a clinician marks a released order `entered_in_error` with reason `wrong_patient`
- **THEN** the order stops having effect, is shown labelled entered in error, and its content and history remain for audit

#### Scenario: Failure: an entered-in-error mark without a reason
- **WHEN** a user tries to mark an act entered in error without a coded reason
- **THEN** openChart refuses the mark and the act is unchanged

### Requirement: CA-07 A co-signature requirement can attach to any act version
openChart SHALL support a co-signature requirement on any act version, without changing the act model, with these parts (design call CD-11):
- **source:** in this change, the author's role grant (AU-02); the requirement names the grant and its version;
- **mode:** `before_effect`, where the act does not take effect until co-signed (in this change, only orders and prescriptions, which stay `pending_release`), or `after_the_fact`, where the act takes effect and is co-reviewed within a window;
- **due time:** the signing time plus the window the source sets;
- **co-signer:** a named clinician, other than the author, holding co-sign scope for the act class;
- **outcome:** `cosigned` (the co-signer's signature is added); an amendment by the co-signer, which supersedes the version (CA-05); or an entered-in-error mark (CA-06).

A requirement whose due time passes with no outcome SHALL escalate to the medical director at once, who becomes a co-signer, and SHALL keep alerting until a named clinician records an outcome. No timer, default or agent SHALL record an outcome or close the requirement. A co-signature of a prescription SHALL also need the prescribing-safety gate (RX-02). A later governed change MAY add another source in a new MINOR version; `define-ai-authored-clinical-records` (not yet on main) intends its authority grant to be that source for owner ruling 62's co-review.

#### Scenario: A nurse's order waits for co-signature
- **WHEN** a nurse whose grant requires `before_effect` co-signature for orders signs a laboratory order
- **THEN** the order is `pending_release` until a clinician with co-sign scope co-signs it, and is then `released`

#### Scenario: Failure: a co-signature window passes
- **WHEN** an `after_the_fact` co-signature requirement passes its due time with no outcome
- **THEN** openChart escalates it to the medical director, keeps alerting, and the requirement stays open

#### Scenario: Failure: the author tries to co-sign their own act
- **WHEN** the author of an act tries to record its co-signature
- **THEN** openChart refuses it and the requirement stays pending

### Requirement: CA-08 Every act carries full provenance and an audit trail
openChart SHALL record, for every act, an append-only trail of every creation, draft revision, signature, co-signature, release, completion, discontinuation, cancellation, entered-in-error mark, amendment and co-signature escalation, each with the actor, time and coded reason where one applies. It SHALL record every read of an act by an integration identity, with the identity, time and purpose. The trail MUST NOT be edited or deleted through any supported path. The provenance of an act SHALL be readable by every user authorized for the patient's chart.

#### Scenario: An auditor reviews an amended note
- **WHEN** an authorized user opens the history of a note amended twice
- **THEN** every version, author, signature, reason and time is shown in order

#### Scenario: Failure: someone tries to edit the audit trail
- **WHEN** an extension or user tries to change or delete a lifecycle event
- **THEN** openChart refuses it and the trail is unchanged

### Requirement: CA-09 Act types are data in a registry with reserved and emergency flags
openChart SHALL keep an act-type registry: for each act class, the act types a practice uses, each with a stable code, a display name, an effective interval, a version and two flags that SHALL be set explicitly on registration: `reserved` (an act reserved to a human clinician) and `emergency_management` (design call CD-14). Only the medical director SHALL add, change or retire an entry, and every change SHALL be a new registry version. Every act SHALL name an act type that is in force in the registry for its class. This change gives the two flags no effect on clinician-authored acts; they exist for `define-ai-authored-clinical-records` (not yet on main) and its allowlist, reserved-act and emergency rules.

#### Scenario: The medical director registers an act type
- **WHEN** the medical director registers a laboratory order type with `reserved` false and `emergency_management` false
- **THEN** a new registry version records the entry, both flags and the medical director

#### Scenario: Failure: an act type is registered without its flags
- **WHEN** someone tries to register an act type without setting both flags
- **THEN** openChart refuses the entry

#### Scenario: Failure: an act names an unregistered type
- **WHEN** a clinician tries to sign an order whose act type is not in force in the registry
- **THEN** openChart refuses the signature with a coded reason

### Requirement: CA-10 Acts are created only by a named clinician through the versioned service boundary
openChart SHALL create and change acts only through its authenticated, versioned service boundary, authorized for subject, tenant, purpose and role as the ratified API requirement demands, and only on a named clinician's command (CA-02). Every client, mobile or workstation, SHALL use that boundary. Direct table writes SHALL be refused, as they are for intake today. No intake submission, patient-reported statement, clinical communication, API response, extension event, notification, timer or other automated process SHALL create an act or move it to a signed status. Extensions MAY read acts and receive pointer-only events through supported hooks, and MUST NOT create or sign one. This is how this change honors the ratified rule that "no intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order…" (tension CT-1).

#### Scenario: Failure: an extension writes a diagnosis directly
- **WHEN** an extension inserts a diagnosis row directly, outside the service boundary
- **THEN** the write is refused and no diagnosis exists

#### Scenario: Failure: an extension event tries to create an order
- **WHEN** an extension event carries a payload shaped like an order
- **THEN** no order is created, drafted or signed

### Requirement: CA-11 A clinician creates a record from patient-reported content only by an explicit, attributed action
A clinician MAY create a draft act from a patient-reported intake statement only by an explicit action, recorded with the clinician, the time and the source statement's identifier and version as derivation provenance (design call CD-22). The same SHALL hold for a clinical communication record under `define-clinical-message-inbox` (not yet on main), once it lands. The created act SHALL be a separate, clinician-authored act that follows every rule of this capability, including signing; nothing SHALL be created, drafted or signed automatically from a statement or a communication. The source statement SHALL stay unchanged and visibly patient-reported, keeping its assertion kind; openChart SHALL NOT set its `verification_state` to `clinician_verified` or change any of its fields (tension CT-3). This is the "authorized clinical workflow" that "records another assertion", in the words of the ratified requirement "Intake does not confer clinician or autonomous authority" (tension CT-2).

#### Scenario: A clinician confirms a reported condition as a diagnosis
- **WHEN** a clinician reviews a patient-reported condition and chooses to record it as an encounter diagnosis
- **THEN** a draft diagnosis is created with derivation provenance naming the statement and its version, the clinician signs it, and the statement stays patient-reported and unchanged

#### Scenario: Failure: a statement would become a diagnosis without a clinician
- **WHEN** an intake submission containing a patient-reported condition is accepted
- **THEN** no diagnosis, draft or problem-list entry is created from it

#### Scenario: Failure: a reported medication is read as a prescription
- **WHEN** a consumer reads a patient-reported medication statement
- **THEN** it is not a prescription, and no prescription exists unless a clinician recorded and signed one

### Requirement: CA-12 Codes come from practice-supplied code sets; openChart bundles none
A coding on an act SHALL store the code system, the code, the code-system version where the practice-supplied code set declares one, the display text, and a reference to the practice-supplied code-set import it came from (design call CD-23). openChart SHALL bundle no code set and SHALL assert no license status for any code system. Before any code set is bundled with or distributed by openChart, its license status MUST be verified and a separately governed change MUST approve it. A practice SHALL load code sets under its own rights, and each load SHALL be recorded with its identity, version, effective date and the loading user. A code that is not in a loaded code set in force SHALL be refused on any coded field.

#### Scenario: A practice loads a code set
- **WHEN** a practice loads a code set it supplies
- **THEN** openChart records the set's identity, version, effective date and the loading user, and codings reference that load

#### Scenario: Failure: a code set is proposed for bundling
- **WHEN** a plan proposes shipping a code set inside openChart
- **THEN** the plan is out of scope until license verification and a separately governed change approve it

#### Scenario: Failure: a code is not in any loaded set
- **WHEN** a clinician enters a diagnosis code that is not in a loaded code set in force
- **THEN** openChart refuses the coding with a coded reason

### Requirement: CA-13 Acts map to FHIR R4-compatible resources at contract level, with no conformance claim
openChart SHALL define a FHIR R4-compatible mapping for acts at contract level: `encounter` to Encounter; `diagnosis_of_record` to Condition; `procedure_performed` to Procedure; `order` to ServiceRequest; `prescription` to MedicationRequest; `clinical_note` to DocumentReference; and authorship, signatures, co-signatures and derivation to Provenance (design `design.md`, "FHIR R4-compatible mapping"; design call CD-26). openChart MUST NOT claim FHIR certification, profile conformance or validation against any implementation guide. A draft, cancelled or restricted act SHALL NOT be exposed through any interoperability read.

#### Scenario: A FHIR-compatible read of a final diagnosis
- **WHEN** an authorized consumer reads a final encounter diagnosis through an interoperability surface
- **THEN** it receives a Condition-compatible representation with category, code, clinical and verification status, encounter reference and Provenance

#### Scenario: Failure: a draft would be exposed
- **WHEN** an interoperability read would include a draft order
- **THEN** the draft is omitted

### Requirement: CA-14 Acts work without any external system, and no PHI enters logs
Every capability in this change SHALL operate with no openPractice, MedxFactory, MedxEHR, HealthLinc, medXfactory, external AI system or drug knowledge source configured, except that signing a prescription needs the gate of RX-02. The ratified standalone golden-intake tests SHALL keep passing. openChart's logs, error messages, diagnostics and coded reasons MUST NOT contain names, dates of birth, contact details, identifier values or clinical content; they SHALL reference acts by identifier and version only.

#### Scenario: Standalone deployment
- **WHEN** openChart runs with no external system configured
- **THEN** a clinician can open, document and sign an encounter, record diagnoses, procedures and orders, and the golden-intake tests pass

#### Scenario: Failure: a refusal would log clinical content
- **WHEN** openChart refuses to sign a diagnosis
- **THEN** its log entry carries the act identifier, version and a coded reason, and no code display, note text or patient detail

### Requirement: CA-15 A restricted act never leaves the chart until counsel's rules are encoded
Pending counsel's answer on sensitive record categories and minors' records (Open Question 3), openChart SHALL let a clinician mark an act `restricted` (design call CD-27). A restricted act, and any encounter that carries one, SHALL NOT be published to openPractice, exposed through any interoperability read, or sent to any external system. It SHALL stay visible in openChart's chart view to users authorized for the patient's chart. openChart SHALL assert no legal rule about which records are sensitive; a later governed change SHALL encode counsel's answer.

#### Scenario: A restricted diagnosis on a final encounter
- **WHEN** a final encounter for a linked patient carries a diagnosis marked `restricted`
- **THEN** openChart publishes nothing for that encounter to openPractice, and the encounter stays visible in the chart

#### Scenario: Failure: an interoperability read asks for a restricted act
- **WHEN** an integration identity reads an act marked `restricted`
- **THEN** openChart returns no content for it and records the read with a coded reason
