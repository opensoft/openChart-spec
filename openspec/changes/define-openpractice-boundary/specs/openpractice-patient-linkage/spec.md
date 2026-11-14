## ADDED Requirements

### Requirement: OC Patient remains the clinical patient anchor
openChart SHALL keep `OC Patient` as the anchor of every clinical record of a patient who is linked to openPractice. A link to openPractice MUST NOT replace the openChart patient identifier, MUST NOT merge patients, and MUST NOT transfer ownership of any clinical record to openPractice. This requirement adds to the ratified `expanded-patient-intake` rule that an external identifier must not replace the openChart patient identifier or silently merge patients, and does not modify it.

#### Scenario: A patient is linked to openPractice
- **WHEN** an openPractice link is created for an existing `OC Patient`
- **THEN** the `OC Patient` identifier is unchanged and every clinical record still references that `OC Patient`

### Requirement: The openPractice reference is a namespaced external identifier
openChart SHALL store each openPractice link as an `OC Patient External Identifier` row with:
- `namespace` set to `openpractice`;
- `issuer_or_endpoint` set to the openPractice deployment's issuer identifier;
- `value` set to the openPractice patient identifier;
- a `status` of `active`, `superseded`, `revoked` or `identity_review`;
- an effective interval and an `identifier_version`;
- provenance naming the contract `openpractice-ehr-patient-link/1.0` and the message identifier that created or changed the row.

A revoked or superseded link SHALL remain stored with its status and effective end.

#### Scenario: A link is stored
- **WHEN** openChart links an `OC Patient` to an openPractice patient
- **THEN** an `OC Patient External Identifier` row exists with namespace `openpractice`, the openPractice issuer and patient identifier, status `active`, and provenance naming the contract and message

#### Scenario: A link is revoked
- **WHEN** a link is revoked by either system under the contract
- **THEN** the row remains with status `revoked` and an effective end, and no clinical record is changed

### Requirement: Link requests are accepted only through the versioned contract from an authorized integration identity
openChart SHALL accept `link.request` messages under contract `openpractice-ehr-patient-link/1.0` only from an authenticated integration identity authorized for the subject, tenant, purpose and role, as the ratified API requirement demands. It SHALL answer each request with exactly one `link.result`: `linked`, `identity_review` or `refused`.
- In `create_new` mode, openChart SHALL create a new `OC Patient` from the request's demographic snapshot and link it.
- In `link_existing` mode, openChart SHALL link the named `OC Patient` only when that patient's name and date of birth agree with the snapshot, and SHALL otherwise place the link in `identity_review`.

openChart MUST NOT create an openPractice link from its own demographic matching.

#### Scenario: openPractice asks openChart to create a patient
- **WHEN** an authorized openPractice integration sends a `create_new` link request
- **THEN** openChart creates a new `OC Patient` from the snapshot, stores the `openpractice` identifier as `active`, and answers `linked` with the new patient's identifier

#### Scenario: Demographics disagree on a link to an existing patient
- **WHEN** a `link_existing` request names an `OC Patient` whose date of birth differs from the snapshot
- **THEN** openChart stores the identifier with status `identity_review` and answers `identity_review`

#### Scenario: An unauthorized caller requests a link
- **WHEN** a caller without the integration authorization sends a link request
- **THEN** openChart answers `refused` and stores nothing

### Requirement: Linkage conflicts enter identity review and never merge
openChart SHALL place a link in `identity_review` in either of these cases:
- the openPractice issuer and value are already `active` on a different `OC Patient`;
- the target `OC Patient` already holds an `active` `openpractice` identifier from the same issuer with a different value.

openChart SHALL apply no demographic update on a link in review. It SHALL record each review resolution with actor, time, outcome (`confirmed` or `revoked`) and reason, and SHALL send `link.review_resolved` to openPractice. Resolution MUST NOT merge, overwrite or delete either patient's records.

#### Scenario: Two openPractice records claim one openChart patient
- **WHEN** a link request targets an `OC Patient` that already holds an active `openpractice` identifier from the same issuer with a different value
- **THEN** the new identifier enters `identity_review`, no demographics are applied on it, and no record is merged

#### Scenario: A reviewer confirms the link
- **WHEN** an authorized openChart user confirms a link in review
- **THEN** its status becomes `active`, the resolution is recorded, and `link.review_resolved` with outcome `confirmed` is sent to openPractice

### Requirement: Administrative demographic updates apply only on an active link through the contract
openChart SHALL accept administrative demographic changes for a patient linked to openPractice only as `demographics.updated` messages under contract `openpractice-ehr-patient-link/1.0`, received on an `active` link. It SHALL answer each message with exactly one `demographics.ack`:
- `applied` when the demographic version is greater than the last applied version;
- `duplicate` when the message identifier was already applied;
- `stale` when the version is lower than the last applied version, in which case nothing changes;
- `rejected` when the same version arrives with different content, when the contract major version is unsupported, or when the link is revoked or unknown;
- `identity_review` when the link is in review or the update is held under the date-of-birth rule.

Each applied version SHALL be stored as an immutable record carrying the message identifier, issuer, actor reference, source channel and reason, and every prior value SHALL remain retrievable.

#### Scenario: Updates arrive out of order
- **WHEN** openChart receives demographic version 4 after it has applied version 5 for the same link
- **THEN** it answers `stale` and keeps the values of version 5

#### Scenario: A retry repeats an applied message
- **WHEN** openPractice resends a message identifier openChart has already applied
- **THEN** openChart answers `duplicate` and changes nothing

#### Scenario: An update names an unlinked patient
- **WHEN** a `demographics.updated` message names an openPractice reference with no active link
- **THEN** openChart answers `rejected` and changes no patient

### Requirement: Date-of-birth changes are held for identity review
openChart SHALL hold a `demographics.updated` message that changes the patient's date of birth, rather than apply it. It SHALL place the change in identity review for an authorized openChart user and SHALL acknowledge it as `identity_review` until the review resolves. A confirmed change SHALL then be applied with its original provenance. A rejected change SHALL leave the prior value in place and SHALL be reported to openPractice.

#### Scenario: openPractice corrects a date of birth
- **WHEN** an update changes a linked patient's date of birth
- **THEN** openChart keeps the prior date of birth, answers `identity_review`, and applies the new value only after an authorized user confirms it

### Requirement: Administrative updates never overwrite clinical or patient-reported content
Applying an administrative demographic update SHALL change only openChart's administrative demographic attributes for the patient: legal and preferred name, date of birth, administrative sex, gender identity, pronouns, telecom and addresses. openChart SHALL reflect the applied legal name and date of birth on `OC Patient.patient_name` and `OC Patient.date_of_birth`, and every prior value SHALL remain in the applied-version history. An administrative update MUST NOT alter intake submissions, patient-reported statements or clinical records, and MUST NOT overwrite `OC Patient.sex_recorded`.

#### Scenario: Administrative sex changes
- **WHEN** an applied update changes the patient's administrative sex
- **THEN** openChart stores the new administrative sex in the applied version, leaves `OC Patient.sex_recorded` unchanged, and leaves every intake submission and statement unchanged

### Requirement: Demographics flow one way under contract version 1.0
Under contract version 1.0, openChart SHALL NOT send administrative demographic changes to openPractice. Corrections to a linked patient's administrative demographics SHALL be made in openPractice, which is their source.

#### Scenario: Clinical staff notice a wrong address
- **WHEN** an openChart user finds that a linked patient's address is wrong
- **THEN** openChart sends no demographic message to openPractice, and the correction is made in openPractice and arrives as a new demographic version

### Requirement: The openPractice boundary contracts are versioned
openChart SHALL implement contracts `openpractice-ehr-patient-link` and `openpractice-ehr-clinical-facts` at version `1.0`. It SHALL accept additive MINOR versions within MAJOR 1. It SHALL refuse a message with an unsupported MAJOR version with an explicit error, rather than partially applying it. A breaking change SHALL require a new MAJOR version agreed in both openChart's and openPractice's governed changes.

#### Scenario: An unsupported major version arrives
- **WHEN** openChart receives a `2.0` message while it supports only `1.x`
- **THEN** it rejects the message with an unsupported-version error and changes nothing

### Requirement: openChart operates without openPractice
openChart SHALL operate fully with no openPractice deployment. Patients without an `openpractice` identifier SHALL be created, charted and read exactly as before, and no openChart operation SHALL require either openPractice boundary contract. This requirement restates, and does not modify, the ratified `expanded-patient-intake` rule that the application must operate without openPractice.

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no openPractice deployment
- **THEN** migrations complete and the golden-patient intake tests pass with no openPractice link configured
