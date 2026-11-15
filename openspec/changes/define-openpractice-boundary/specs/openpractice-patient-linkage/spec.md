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

A link is **established** from the moment it first becomes `active`: when openChart answers `linked` to its `link.request` (PL-05), or when a review of it resolves `confirmed` (PL-06). It stays established until it is revoked or superseded, including while a date-of-birth hold puts it in `identity_review` (PL-08). A link that has been in `identity_review` since its request, because the agree check failed (PL-05) or a conflict was found (PL-06), has never been established: nothing has confirmed that its openPractice patient and the `OC Patient` are the same person. openChart SHALL record, for each `openpractice` row, whether the link has been established. Planning decides how (⚑ design call 1 in `design.md`). Only an established link carries edit refusals, correction requests, applied demographics or confidential-communication instructions (PL-07 to PL-10, PL-16).

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
| `identity_review` | The link is in review, or the update is held. On a link that has never been established (PL-02), the update is neither applied nor held. |

Each applied version SHALL be stored as an immutable record with the `message_id`, issuer, actor reference, source and coded reason. Prior values SHALL remain retrievable.

An update on a link that has never been established (PL-02) SHALL be answered `identity_review`, with the `review_id` of the link's review. It SHALL NOT be applied, held under PL-08 or projected (PL-09), and nothing in it SHALL direct a communication (PL-16). openChart keeps it only as a received message, which the link's reviewer may compare with the `OC Patient`.

#### Scenario: Out of order
- **WHEN** version 4 arrives after version 5 was applied on the same link
- **THEN** openChart answers `stale` and keeps version 5

#### Scenario: Republish
- **WHEN** an already-applied version arrives again with identical content under a new `message_id`
- **THEN** openChart answers `duplicate`

#### Scenario: An update on a link that was never confirmed
- **WHEN** a `demographics.updated` message arrives on a link that has been in `identity_review` since its request and has never been `active`
- **THEN** openChart answers `identity_review` with the link's `review_id`, applies and projects nothing, starts no hold, and takes no communication instruction from the snapshot

### Requirement: PL-08 A date-of-birth change suspends demographic application on the link
When an incoming snapshot's date of birth differs from the date of birth openChart has currently applied for that link, openChart SHALL hold the update. It SHALL set the link's identifier status to `identity_review` and answer `identity_review` with a `review_id`. While the hold is open, every later version on that link SHALL also be held, unapplied. openChart is the resolver.

- **On confirmation**, openChart SHALL apply the latest held snapshot, set the status to `active`, and send `link.review_resolved` with outcome `confirmed` and the applied version.
- **On rejection**, openChart SHALL apply none of the held versions, set the status back to `active`, and send `demographics.hold_rejected` listing the held versions.

A later snapshot whose date of birth still differs from the applied value SHALL start a new hold.

A hold arises only on an established link (PL-02), which has a date of birth applied. On a link that has never been established, an update is answered under PL-07 and starts no hold.

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
openChart SHALL project the applied legal name onto `OC Patient.patient_name`, using the canonical schema's projection, and the applied date of birth onto `OC Patient.date_of_birth`. Every prior value SHALL be kept in the applied-version history. Administrative sex, gender identity, pronouns, preferred language, telecom, addresses and confidential-communication instructions SHALL live in the applied-version record. An administrative update MUST NOT alter intake submissions, patient-reported statements or clinical records, and MUST NOT overwrite `OC Patient.sex_recorded`. Nothing SHALL be projected from a link that has never been established (PL-02). Until the link is confirmed, the patient's `patient_name` and `date_of_birth` stay openChart's own.

#### Scenario: Administrative sex changes
- **WHEN** an applied update changes administrative sex
- **THEN** the applied version records it, `OC Patient.sex_recorded` is unchanged, and no submission or statement changes

### Requirement: PL-10 Direct edits to the projected fields of a patient with an established link are refused and routed to openPractice
For a patient whose `openpractice` link is established (PL-02) and has status `active`, or `identity_review` because of a date-of-birth hold (PL-08), openChart SHALL refuse every direct edit to `OC Patient.patient_name` or `OC Patient.date_of_birth`, whether it comes from openChart staff or from an intake flow such as HealthLinc. openChart SHALL instead send the proposed change to openPractice as a `demographics.correction_requested` message through that link, and record the request. An intake submission carrying identity data SHALL still be accepted and persisted under the ratified intake requirements. Only the change to the projected fields is withheld and routed. Under contract version 1.0, openChart SHALL NOT send `demographics.updated` messages to openPractice. After the link is revoked or superseded, the refusal no longer applies.

**A link that has never been established.** A link that has been in `identity_review` since its request (PL-05, PL-06) has not been confirmed as the same person, and may name an unrelated openPractice record. openChart SHALL refuse no edit for its sake, and SHALL send no `demographics.correction_requested` through it. The patient's `patient_name` and `date_of_birth` stay openChart's own until the link is confirmed (⚑ design call 1 in `design.md`). An edit made meanwhile changes openChart's record only, under its ordinary rules, as for a patient with no link. Nothing is sent to openPractice, and the link's reviewer compares the records as they stand at resolution. Where the patient also has an established link, that link governs: the edit is refused and routed through the established link alone, and nothing is sent through the link that has never been established.

#### Scenario: Staff edit a linked patient's name
- **WHEN** an openChart user edits the name of a patient with an active openPractice link
- **THEN** the edit is refused, a correction request is sent to openPractice, and the name changes only if openPractice applies the correction and publishes a new version

#### Scenario: An intake carries a different date of birth
- **WHEN** a HealthLinc intake for a patient with an active link reports a date of birth that differs from the projected one
- **THEN** the intake submission is accepted and persisted, `OC Patient.date_of_birth` is unchanged, and a correction request is sent to openPractice

#### Scenario: Staff edit during a date-of-birth hold
- **WHEN** an openChart user edits the date of birth of a patient whose link is in `identity_review` because of a date-of-birth hold
- **THEN** the edit is refused and routed to openPractice as a correction request, as it would be on an `active` link

#### Scenario: Staff edit a patient whose link was never confirmed
- **WHEN** a `link_existing` request failed the agree check, its link has been in `identity_review` since the request and has never been `active`, the patient has no other `openpractice` link, and an openChart user edits the patient's date of birth
- **THEN** the edit is made to `OC Patient.date_of_birth` under openChart's ordinary rules, as for a patient with no link, and no `demographics.correction_requested` is sent through that link or to openPractice at all

#### Scenario: A second link in review on a patient with an active link
- **WHEN** a patient has an active link and a second link from the same issuer in `identity_review` under PL-06 that has never been `active`, and an openChart user edits the patient's name
- **THEN** the edit is refused, the correction request is sent through the active link only, and nothing is sent through the second link

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
For a patient whose `openpractice` link is established (PL-02) and has status `active` or `identity_review`, openChart SHALL apply the confidential-communication instructions of the latest applied demographic version to every patient communication it originates. After the link is revoked or superseded, openChart SHALL keep honoring the last applied instructions and SHALL NOT drop them because the link ended. This includes communications from any system it drives, such as HealthLinc intake (ruling 27). It MUST NOT send to an address or channel that the instructions restrict, and it SHALL use the alternate address or channel they name. While updates are held (PL-08), openChart SHALL honor every restriction in the applied version and in every held version. A communication that cannot satisfy the instructions SHALL be withheld, and the withholding SHALL be recorded with a coded reason and no PHI in logs (PL-13).

A link that has never been established gives openChart no instructions. openChart SHALL take no restriction, alternate address or alternate channel from its snapshots, because nothing has confirmed that they belong to this patient (⚑ design call 2 in `design.md`). A patient whose only `openpractice` link has never been established is treated as a patient with no link. A patient who also has an established link, or the last applied instructions of an ended one, is governed by those.

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

#### Scenario: A link that was never confirmed names an alternate address
- **WHEN** a patient's only `openpractice` link has been in `identity_review` since its request and has never been `active`, its snapshot carries `no_home_mail` and an alternate address, and openChart sends the patient a letter
- **THEN** nothing in that snapshot directs the letter: it is never sent to that alternate address, and openChart addresses it as it would for a patient with no link
