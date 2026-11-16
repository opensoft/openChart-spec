## ADDED Requirements

### Requirement: EN-01 An encounter records a clinician's visit with the patient
openChart SHALL record an encounter as an act of class `encounter`, linked to one `OC Patient`, with an act type from the registry, coded encounter types where the practice supplies them, a period (start, and end once known), one or more participants (each a practitioner reference with participation `primary_performer`, `participant` or `supervising`), an optional location reference and optional coded reasons. Its lifecycle SHALL be `in_progress`, `final`, `amended`, `cancelled` or `entered_in_error` (CA-03). An encounter SHALL have exactly one `primary_performer`.

#### Scenario: A clinician opens an encounter
- **WHEN** a clinician with encounter `draft` scope opens an encounter for a patient
- **THEN** openChart creates an `in_progress` encounter with the clinician as primary performer and the start time

#### Scenario: Failure: an encounter without a primary performer
- **WHEN** a client tries to create an encounter with no participant marked `primary_performer`
- **THEN** openChart refuses it with a coded reason

### Requirement: EN-02 openChart keeps an appointment reference only and never owns the appointment
openPractice is the system of record for the administrative appointment (owner ruling 31; `define-openpractice-boundary`, not yet on main; openPractice EB-19). An encounter MAY carry an optional, opaque reference to an appointment held by its system of record: issuer, namespace and value (design call CD-17). openChart SHALL perform no appointment create, update, cancel or scheduling operation, SHALL NOT copy appointment details into the encounter, and SHALL NOT require an appointment reference to open, sign or publish an encounter.

#### Scenario: A walk-in visit has no appointment
- **WHEN** a clinician documents an encounter with no appointment reference
- **THEN** the encounter is opened, signed and, for a linked patient, published like any other

#### Scenario: Failure: a plan adds appointment scheduling to openChart
- **WHEN** a plan proposes creating or rescheduling appointments in openChart
- **THEN** the plan is out of scope; openPractice owns the appointment

### Requirement: EN-03 A clinical note is clinician documentation attached to an encounter and signed by its author
openChart SHALL record a clinical note as an act of class `clinical_note` that references one encounter, with a note kind, an optional coded note type, its text and text format, and optional attachments by reference and SHA-256 digest. A note SHALL be signed by its author before it is `final` (CA-04). A later note that adds to a signed note without replacing it SHALL be recorded as a new note that names the earlier one as `addendum_to`; a change that replaces signed text SHALL be an amendment (CA-05). Clinician replies to patients are not notes: they are clinical communication records under `define-clinical-message-inbox` MI-12 (not yet on main).

#### Scenario: A clinician adds an addendum
- **WHEN** a clinician adds information to a final note signed by a colleague
- **THEN** a new signed note names the original as `addendum_to`, and the original is unchanged

#### Scenario: Failure: a note without an encounter
- **WHEN** a client tries to create a clinical note that references no encounter
- **THEN** openChart refuses it with a coded reason

### Requirement: EN-04 An encounter is signed final only when its documentation is complete
openChart SHALL let an encounter move from `in_progress` to `final` only when every one of these holds (design call CD-15):
- the signer is a participant on the encounter and holds encounter `sign` scope;
- at least one `final` clinical note references the encounter. A note kept as information (AN-14) is not a final note;
- no act that references the encounter is in `draft`;
- the encounter period has an end.

The encounter signature SHALL attest the records in its manifest: every act and information record that references the encounter and that the signing view showed, which CA-04 defines. The signing view SHALL show exactly the manifest's members, and its sign-off binds the manifest's SHA-256. The signature SHALL be the documentation-final signature that publication uses (PB-02). It attests no record outside the manifest, and never adopts a recommendation (AN-11) (CA-04; design call CD-53, PROPOSED). The manifest records what was shown at signing. An order or prescription in a signed manifest MAY later change by its own signed act, such as a release, a cancellation or a discontinuation, without an encounter amendment (EN-05); the signature still attests what was shown at signing.

A draft that blocks the signature and is not held, including one returned to its author after its recommendation was declined, does not block it indefinitely. Owner ruling 203 lets the medical director close another clinician's unfinished draft that blocks signing the visit, "but only after it has been listed and escalated. Its content stays readable, and its author is told." AN-14 lists it for its author and the primary performer with a due time, escalates it to the medical director, who may then close it, and tells them both when it is closed (design call CD-68, PROPOSED for the times and the notices). A held draft ends instead by adoption or decline, whose review escalates.

#### Scenario: An encounter is finalized
- **WHEN** the primary performer signs an encounter with a final note, a final diagnosis and no drafts
- **THEN** the encounter becomes `final`, with the signer and time recorded

#### Scenario: The encounter sign-off binds what is attached
- **WHEN** a clinician signs an encounter with one final note, one final diagnosis and one procedure attached
- **THEN** the signing view shows those three records, with any information record that references the encounter, and the sign-off statement carries `manifest_sha256` over exactly them, so the signature attests exactly them, and a later amendment of any of them is not covered by it

#### Scenario: Failure: a draft diagnosis remains
- **WHEN** a clinician tries to sign an encounter that has a diagnosis still in `draft`
- **THEN** openChart refuses, names the open draft by identifier, and the encounter stays `in_progress`

#### Scenario: Failure: another clinician's draft blocks the visit
- **WHEN** another clinician's draft diagnosis blocks the primary performer from signing an encounter, and the medical director tries to close it before it has been listed and escalated
- **THEN** openChart refuses the close; once the draft has been listed for its author and the primary performer, its due time has passed and it has escalated, the medical director may close it, its content stays readable, and its author is told

#### Scenario: Failure: no signed note
- **WHEN** a clinician tries to sign an encounter with no final clinical note
- **THEN** openChart refuses and the encounter stays `in_progress`

### Requirement: EN-05 After an encounter is final, every change goes through a signed encounter amendment
Once an encounter is `final` or `amended`, adding, amending or marking entered in error any note, diagnosis or procedure that references it SHALL be done within an encounter amendment. An order or prescription that references it changes by its own signed act, without an encounter amendment, and the signed manifest still records what was shown at signing (EN-04). An amendment is a new encounter version, status `amended`, with a reason, signed by a participant or clinician with encounter `sign` scope, whose signature binds a new manifest (design call CD-16). The prior encounter version and every prior act version SHALL stay readable. Publication SHALL treat the amendment as a forward-only correction (PB-03).

#### Scenario: A procedure is added after signing
- **WHEN** a clinician adds a procedure to a final encounter
- **THEN** the procedure is signed, the encounter becomes version 2 with status `amended`, a reason and a new signature, and version 1 stays readable

#### Scenario: Failure: an attached diagnosis is changed without an encounter amendment
- **WHEN** a clinician tries to amend a diagnosis on a final encounter without amending the encounter
- **THEN** openChart refuses the change until it is made within a signed encounter amendment

### Requirement: EN-06 Every requirement holds the same on mobile and on workstation
Every requirement in this change SHALL hold independently of the device or form factor the clinician uses (owner ruling 35). No act, signature, attestation, co-signature or check SHALL be weaker, optional or skipped on any client.

**How a practitioner signs, on a phone as on a workstation (owner ruling 208; design call CD-80, PROPOSED beyond its words).** Owner ruling 208: a practitioner signs with "A passkey or security key. Draft that change now. A smart card cannot be used from a phone." The proof profile for passkeys and security keys, `wallet-webauthn-proof`, is drafted in openWallet-spec change `add-webauthn-proof-profile` (draft pull request #11, read at `fbb74f0`), unratified. openChart verifies whatever proof a sign-off seals by openWallet's verification for the profile the proof names (CA-04), so this requirement asks nothing of a phone that it does not ask of a workstation. Until that profile is ratified, no practitioner can sign, on a phone or on a workstation, and owner ruling 152 keeps every decision off. This requirement stands; nothing in this change makes version 1 workstation-only.

#### Scenario: Signing on a phone
- **WHEN** a clinician signs an encounter from a mobile client
- **THEN** the same re-authentication, attestation, scope check and completeness rules apply as on a workstation

#### Scenario: Failure: no proof profile for passkeys and security keys is ratified yet
- **WHEN** a clinician signs off from a phone, or from a workstation, before openWallet has ratified the proof profile for passkeys and security keys
- **THEN** no sign-off is accepted and nothing takes effect; the draft stays a draft and the attempt is recorded

#### Scenario: Failure: a client offers a shortcut
- **WHEN** a client offers to sign acts without re-authentication because of its form factor
- **THEN** openChart refuses each such signature
