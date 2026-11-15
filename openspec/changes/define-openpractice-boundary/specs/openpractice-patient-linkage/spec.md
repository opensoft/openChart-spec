## ADDED Requirements

### Requirement: PL-01 OC Patient remains the clinical patient anchor
openChart SHALL keep `OC Patient` as the anchor of every clinical record for a patient linked to openPractice. A link MUST NOT replace the openChart patient identifier, MUST NOT merge patients, and MUST NOT transfer ownership of any clinical record to openPractice. This requirement adds to the ratified `expanded-patient-intake` rule that an external identifier must not replace the openChart patient identifier or silently merge patients. It does not modify that rule.

#### Scenario: A patient is linked
- **WHEN** an openPractice link is created for an existing `OC Patient`
- **THEN** the `OC Patient` identifier is unchanged and every clinical record still references it

### Requirement: PL-02 The openPractice reference is a namespaced external identifier
openChart SHALL store each openPractice link as an `OC Patient External Identifier` row with these fields:
- `namespace` set to `openpractice`;
- `issuer_or_endpoint` set to the openPractice deployment's issuer;
- `value` set to the openPractice patient identifier;
- `status` set to one of `active`, `superseded`, `revoked` or `identity_review`;
- an effective interval and an `identifier_version`;
- provenance naming the contract `openpractice-ehr-patient-link/1.0`, the `link_id`, and the message that created or changed the row.

A revoked or superseded row SHALL remain stored with its status and effective end.

#### Scenario: A link is stored
- **WHEN** openChart links an `OC Patient` to an openPractice patient
- **THEN** a row exists with namespace `openpractice`, the openPractice issuer and identifier, status `active`, and provenance naming the contract, `link_id` and message

### Requirement: PL-03 openChart has a configured issuer and compares references as triples
openChart SHALL have a configured, stable issuer identifier that is unique across deployments and is never derived from a host path. openChart SHALL identify its patients to openPractice as (openChart issuer, `openchart`, `OC Patient` identifier). It SHALL compare `openpractice` references as (issuer, namespace, value) triples, never by value alone.

#### Scenario: Two openChart sites
- **WHEN** two openChart deployments both have `OC-PAT-00001` and link to the same openPractice deployment
- **THEN** each identifies its patient with its own issuer, and openPractice holds two distinct links

### Requirement: PL-04 openChart validates against openPractice's canonical schemas by digest
openChart SHALL validate every message it sends or receives under the two contracts against the canonical schemas owned by `opensoft/openPractice-spec` change `define-mvp-practice-foundation`:
- `openspec/changes/define-mvp-practice-foundation/contracts/openpractice-ehr-patient-link-1.0.schema.json`, SHA-256 `76f465e144893000de4bd2240adb9f547899e2e8100315f698c3cc6cb885b802`
- `openspec/changes/define-mvp-practice-foundation/contracts/openpractice-ehr-clinical-facts-1.0.schema.json`, SHA-256 `6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec`

The digest identifies the schema even after archival moves the file. openChart SHALL NOT implement against a schema whose digest differs from the digest recorded here, until both changes record the same new digest.

#### Scenario: A received message fails the schema
- **WHEN** openChart receives a message that fails validation against the recorded schema
- **THEN** it answers `rejected` with reason `schema_invalid` and changes nothing

### Requirement: PL-05 Link requests come only from a dedicated integration role and are checked deterministically
openChart SHALL accept `link.request` messages only from an authenticated integration identity that holds a dedicated openChart integration role. The role SHALL be narrower than `System Manager`, and its name and permissions SHALL be fixed in planning. It SHALL be authorized for subject, tenant, purpose and role, as the ratified API requirement demands. openChart SHALL answer each request with exactly one `link.result`: `linked`, `identity_review` or `refused`.

- **`create_new`.** openChart SHALL create an `OC Patient` from the snapshot and link it.
- **`link_existing`.** openChart SHALL link the named `OC Patient` only when both of these hold:
  - the snapshot's legal name, projected as the canonical schema defines, equals `OC Patient.patient_name`, after both are normalized (Unicode NFKC, case folding, trimming, and collapsing internal whitespace to one space);
  - the snapshot's date of birth equals `OC Patient.date_of_birth`.

  A difference in either SHALL place the link in `identity_review`, as SHALL an empty `OC Patient.date_of_birth`.

openChart MUST NOT create a link from its own matching.

#### Scenario: Names agree after normalization
- **WHEN** the snapshot's projected name is `Ana  María Example` and `OC Patient.patient_name` is `ana maría example`, and the dates of birth are equal
- **THEN** openChart links the patient and answers `linked`

#### Scenario: openChart's record has no date of birth
- **WHEN** a `link_existing` request names an `OC Patient` whose `date_of_birth` is empty
- **THEN** the link enters `identity_review` with reason `date_of_birth_empty`

#### Scenario: Unauthorized caller
- **WHEN** a caller without the integration role sends a link request
- **THEN** openChart answers `refused` and stores nothing

### Requirement: PL-06 Linkage conflicts enter identity review with a single resolver
openChart SHALL place a link in `identity_review` in either of these cases:
- the openPractice issuer and value are already `active` on another `OC Patient`;
- the target `OC Patient` already holds an `active` `openpractice` identifier from the same issuer with a different value.

The side that raised a review SHALL be its only resolver. For reviews it raises, openChart SHALL record the outcome (`confirmed` or `revoked`) with actor, time and reason, and send `link.review_resolved`. A review of the second kind SHALL NOT resolve as `confirmed`. A `link.revoked` for the same `link_id` from either side SHALL win over any confirmation. No demographic update SHALL apply on a link in review, and resolution MUST NOT merge, overwrite or delete records. Version counters SHALL be tracked per `link_id`.

#### Scenario: Two openPractice records claim one patient
- **WHEN** a link request targets an `OC Patient` that already holds an active `openpractice` identifier from the same issuer with a different value
- **THEN** the new link enters review, openChart resolves it, it cannot resolve as `confirmed`, and nothing merges

#### Scenario: Revocation crosses confirmation
- **WHEN** openPractice revokes a link while an openChart reviewer is confirming it
- **THEN** the link ends `revoked`

### Requirement: PL-07 Administrative demographic updates apply only on an active link through the contract
openChart SHALL accept administrative demographic changes for linked patients only as `demographics.updated` messages on an `active` link. It SHALL compare each message's version with the last version applied on that `link_id`, and answer with exactly one result:

| Result | When |
|---|---|
| `applied` | The version is greater than the last applied version. |
| `duplicate` | The `message_id` was already applied, or the same version arrives with identical content under a new `message_id`. |
| `stale` | The version is lower than the last applied version. Nothing changes. |
| `rejected` | The same version arrives with different content, the MAJOR version is unsupported, or the link is revoked, superseded or unknown. |
| `identity_review` | The link is in review, or the update is held. |

Each applied version SHALL be stored as an immutable record with the `message_id`, issuer, actor reference, source and coded reason. Prior values SHALL remain retrievable.

#### Scenario: Out of order
- **WHEN** version 4 arrives after version 5 was applied on the same link
- **THEN** openChart answers `stale` and keeps version 5

#### Scenario: Republish
- **WHEN** an already-applied version arrives again with identical content under a new `message_id`
- **THEN** openChart answers `duplicate`

### Requirement: PL-08 A date-of-birth change suspends demographic application on the link
When an incoming snapshot's date of birth differs from the date of birth openChart has currently applied for that link, openChart SHALL hold the update. It SHALL set the link's identifier status to `identity_review` and answer `identity_review` with a `review_id`. While the hold is open, every later version on that link SHALL also be held, unapplied. openChart is the resolver.

- **On confirmation**, openChart SHALL apply the latest held snapshot, set the status to `active`, and send `link.review_resolved` with outcome `confirmed` and the applied version.
- **On rejection**, openChart SHALL apply none of the held versions, set the status back to `active`, and send `demographics.hold_rejected` listing the held versions.

A later snapshot whose date of birth still differs from the applied value SHALL start a new hold.

#### Scenario: Two held versions are confirmed
- **WHEN** version 5 changes the date of birth, version 6 arrives during the review, and the reviewer confirms
- **THEN** openChart applies version 6, the link becomes `active`, and `link.review_resolved` reports version 6

#### Scenario: A full snapshot cannot bypass the hold
- **WHEN** a hold is open for version 5 and version 6 carries the same new date of birth plus an address change
- **THEN** version 6 is held too, and nothing is applied until the review resolves

#### Scenario: The change is rejected
- **WHEN** the reviewer rejects a held date-of-birth change
- **THEN** the prior date of birth stays, the link returns to `active`, and openChart sends `demographics.hold_rejected` listing the held versions

### Requirement: PL-09 Applied name and date of birth are projected onto OC Patient; nothing clinical is overwritten
openChart SHALL project the applied legal name onto `OC Patient.patient_name`, using the canonical schema's projection, and the applied date of birth onto `OC Patient.date_of_birth`. Every prior value SHALL be kept in the applied-version history. Administrative sex, gender identity, pronouns, preferred language, telecom, addresses and confidential-communication instructions SHALL live in the applied-version record. An administrative update MUST NOT alter intake submissions, patient-reported statements or clinical records, and MUST NOT overwrite `OC Patient.sex_recorded`.

#### Scenario: Administrative sex changes
- **WHEN** an applied update changes administrative sex
- **THEN** the applied version records it, `OC Patient.sex_recorded` is unchanged, and no submission or statement changes

### Requirement: PL-10 Direct edits to a linked patient's projected fields are refused and routed to openPractice
For a patient whose `openpractice` link has status `active` or `identity_review`, including during a date-of-birth hold (PL-08), openChart SHALL refuse every direct edit to `OC Patient.patient_name` or `OC Patient.date_of_birth`, whether it comes from openChart staff or from an intake flow such as HealthLinc. openChart SHALL instead send the proposed change to openPractice as a `demographics.correction_requested` message, and record the request. An intake submission carrying identity data SHALL still be accepted and persisted under the ratified intake requirements. Only the change to the projected fields is withheld and routed. Under contract version 1.0, openChart SHALL NOT send `demographics.updated` messages to openPractice. After the link is revoked or superseded, the refusal no longer applies.

#### Scenario: Staff edit a linked patient's name
- **WHEN** an openChart user edits the name of a patient with an active openPractice link
- **THEN** the edit is refused, a correction request is sent to openPractice, and the name changes only if openPractice applies the correction and publishes a new version

#### Scenario: An intake carries a different date of birth
- **WHEN** a HealthLinc intake for a linked patient reports a date of birth that differs from the projected one
- **THEN** the intake submission is accepted and persisted, `OC Patient.date_of_birth` is unchanged, and a correction request is sent to openPractice

#### Scenario: Staff edit during a date-of-birth hold
- **WHEN** an openChart user edits the date of birth of a patient whose link is in `identity_review` because of a date-of-birth hold
- **THEN** the edit is refused and routed to openPractice as a correction request, as it would be on an `active` link

### Requirement: PL-11 openChart accepts and sends link revocations
openChart SHALL accept `link.revoked` from openPractice. It SHALL set the identifier row's status to `revoked`, set its effective end, and answer with `message.ack`. openChart MAY send `link.revoked` itself, with a coded reason. Revocation SHALL win over any concurrent or later confirmation of the same `link_id`, and no clinical record SHALL change.

#### Scenario: openPractice revokes a link
- **WHEN** openChart receives `link.revoked` for an active link
- **THEN** the row becomes `revoked` with an effective end, openChart acknowledges it, and later updates on that `link_id` are answered `rejected`

### Requirement: PL-12 The boundary contracts are versioned and compatible within a MAJOR version
openChart SHALL implement `openpractice-ehr-patient-link` and `openpractice-ehr-clinical-facts` at version `1.0`. Implementations are compatible exactly when they share the same MAJOR version. openChart SHALL refuse a message with an unsupported MAJOR version, with reason `unsupported_major_version`. A breaking change SHALL require a new MAJOR version and a new schema digest, recorded in both changes.

#### Scenario: Unsupported major version
- **WHEN** a `2.0` message arrives
- **THEN** openChart rejects it with `unsupported_major_version` and changes nothing

### Requirement: PL-13 No PHI in logs, errors, diagnostics or rejection reasons
openChart's logs, error messages, diagnostic bundles and every reason it sends under the two contracts MUST NOT contain names, dates of birth, contact details, identifier values or clinical content. Every reason SHALL use the canonical schema's coded values. Diagnostics SHALL reference messages by `message_id` and `link_id` only.

#### Scenario: An update is rejected
- **WHEN** openChart rejects a demographic message
- **THEN** its log entry and acknowledgement carry the `message_id`, `link_id` and a coded reason, and no demographic value

### Requirement: PL-14 Outbound contract messages use durable delivery
Every message openChart sends under the two contracts SHALL be written to a durable outbound store in the same transaction as the change that caused it. This covers link results, acknowledgements, hold rejections, correction requests, review resolutions, revocations and clinical-fact notifications. openChart SHALL deliver them to the configured openPractice endpoint with retries that reuse the original `message_id`. The mechanism SHALL be decided in planning. Delivery MUST NOT rely on `frappe.publish_realtime` or any other site-local event that never leaves the site.

#### Scenario: openPractice is unreachable
- **WHEN** openPractice is unreachable while openChart has acknowledgements to send
- **THEN** the messages stay in the durable store and are delivered with their original `message_id` when openPractice returns

### Requirement: PL-15 openChart operates without openPractice
openChart SHALL operate fully with no openPractice deployment. Patients without an `openpractice` identifier SHALL be created, edited, charted and read exactly as before, and no operation SHALL require either contract. This requirement restates the ratified `expanded-patient-intake` rule that the application must operate without openPractice. It does not modify that rule.

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no openPractice
- **THEN** migrations complete and the golden-patient intake tests pass

### Requirement: PL-16 openChart honors confidential-communication instructions in every communication it originates
For a patient whose `openpractice` link has status `active` or `identity_review`, openChart SHALL apply the confidential-communication instructions of the latest applied demographic version to every patient communication it originates. After the link is revoked or superseded, openChart SHALL keep honoring the last applied instructions and SHALL NOT drop them because the link ended. This includes communications from any system it drives, such as HealthLinc intake (ruling 27). It MUST NOT send to an address or channel that the instructions restrict, and it SHALL use the alternate address or channel they name. While updates are held (PL-08), openChart SHALL honor every restriction in the applied version and in every held version. A communication that cannot satisfy the instructions SHALL be withheld, and the withholding SHALL be recorded with a coded reason and no PHI in logs (PL-13).

#### Scenario: A no-voicemail patient gets an automated reminder
- **WHEN** a HealthLinc flow driven by openChart would leave a voicemail for a linked patient whose instructions carry `no_voicemail`
- **THEN** no voicemail is left, and the communication is sent only through a permitted channel or withheld

#### Scenario: Mail goes to the alternate address
- **WHEN** openChart sends a letter to a linked patient whose instructions carry `no_home_mail` and an alternate address
- **THEN** the letter goes only to the alternate address

#### Scenario: A new restriction arrives in a held update
- **WHEN** a held update adds `no_text_messages` while a date-of-birth review is open
- **THEN** openChart stops sending text messages to that patient at once, even though the held version is not yet applied

#### Scenario: The link is revoked
- **WHEN** a link whose last applied instructions carry `no_home_mail` and an alternate address is revoked, and openChart later sends a letter
- **THEN** the letter goes only to the alternate address, because openChart keeps honoring the last applied instructions

#### Scenario: No permitted channel remains
- **WHEN** a communication can reach the patient only through restricted channels
- **THEN** openChart withholds it and records a coded reason, with no demographic value in the log
