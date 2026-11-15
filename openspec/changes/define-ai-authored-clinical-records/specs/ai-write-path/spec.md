## ADDED Requirements

### Requirement: AW-01 AI-authored records enter openChart only through the versioned write-path contract
openChart SHALL accept content authored by an external clinical AI system only as messages under contract `openchart-ai-clinical-record-write/1.0`, owned by this change. Its canonical schema is:
- `openspec/changes/define-ai-authored-clinical-records/contracts/openchart-ai-clinical-record-write-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-ai-clinical-record-write:1.0`, at the SHA-256 recorded in this change's `contracts/SHA256SUMS`.

The digest identifies the schema even after archival moves the file. openChart SHALL validate every message it receives or sends under the contract against the schema at that digest. The messages are `consult.write`, `act.write`, `authority.notice`, `write.receipt`, `act.status`, `consult.reviewed`, `record.readback_request`, `record.readback` and `message.ack`. Implementations are compatible exactly when they share the MAJOR version. openChart SHALL accept a `1.x` message at a MINOR version it has declared, refuse a message whose MAJOR version it does not support with reason `unsupported_major_version`, and refuse a message that fails the schema with reason `schema_invalid`. A refusal SHALL store no clinical content. A breaking change SHALL require a new MAJOR version and a new digest, recorded in this change and in every companion that cites it.

#### Scenario: Failure: a write carries a property the schema does not define
- **WHEN** a `consult.write` arrives with a property the schema does not define, such as `diagnosis`
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: an unsupported major version arrives
- **WHEN** a `consult.write` with `contract_version` `2.0` arrives
- **THEN** openChart refuses it with reason `unsupported_major_version` and stores no clinical content

### Requirement: AW-02 Only a registered AI system's integration identity may write, for one source system and one practice
openChart SHALL accept write-path messages only from an authenticated integration identity that is registered for exactly one external clinical AI system, identified by its `source_system` (issuer and namespace), and exactly one practice. The identity SHALL hold a dedicated write-path integration role that is narrower than `System Manager`, is named in planning, and is authorized for subject, tenant, purpose and role, as the ratified API requirement demands. Registering an AI system SHALL be an audited act by a named human, and SHALL be refused while no AU-01 designation of the foundation is in force for the practice. No AI system and no agent SHALL register, widen or re-scope an integration identity.

The integration identity MAY be held by a relay that delivers one source system's writes and returns its receipts, as ruling 70 provides for the medical AI's records. The relay SHALL be registered for that one source system and practice, and each write SHALL still name the source system, not the relay. The registration SHALL record whether the source is relay-only. A source whose owner has ruled that it writes only through a relay SHALL be registered relay-only, by the named human, citing that ruling. For a relay-only source, openChart SHALL register only the relay's integration identity, SHALL refuse to register a direct identity for it, and SHALL refuse with `unauthorized` any write naming it that does not come from its relay. A source system's namespace SHALL be the source token that MI-12 of `define-clinical-message-inbox` uses for it, where MI-12 defines one. `healthlinc` and `openpractice_agent` SHALL NOT be write-path sources, and `openchart` SHALL NOT be a source namespace; the schema refuses all three (design call AD-30).

#### Scenario: Failure: registration while no medical director is designated
- **WHEN** a named human tries to register an AI system for a practice with no AU-01 designation in force
- **THEN** the registration is refused, and no integration identity is registered

#### Scenario: Failure: an unregistered caller writes
- **WHEN** a caller without the write-path integration role sends a `consult.write`
- **THEN** openChart refuses it with reason `unauthorized` and stores no clinical content

#### Scenario: Failure: a direct identity is registered for a relay-only source
- **WHEN** a named human tries to register a direct integration identity for a source registered as relay-only
- **THEN** the registration is refused, and only the relay's identity stays registered for that source

#### Scenario: Failure: a relay-only source writes without its relay
- **WHEN** a write naming a relay-only source arrives from any identity other than its registered relay
- **THEN** openChart refuses it with reason `unauthorized` and stores no clinical content

#### Scenario: Failure: a write names HealthLinc as its source
- **WHEN** a `consult.write` arrives whose `source_system` namespace is `healthlinc`
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: an identity claims another source system
- **WHEN** an identity registered for one source system sends a write whose `source_system` names a different system or practice
- **THEN** openChart refuses it with reason `unauthorized` and stores no clinical content

### Requirement: AW-03 A write resolves the patient only through an existing link
openChart SHALL resolve the patient of a write only through links that already exist. The write SHALL name the openChart patient triple (openChart issuer, `openchart`, `OC Patient` identifier) and the source system's reference for that patient on its link with openChart. That reference need not be, and should not be, the source system's internal patient identifier; a value minted for this one link suffices. openChart SHALL accept the write only when an `active` `OC Patient External Identifier` row on that `OC Patient` carries the source system's namespace, issuer and value. The link is registered through the ratified external-identifier path or a later governed link contract (design call AD-23).

openChart MUST NOT match on names, dates of birth or other demographics. It MUST NOT create, change, merge or re-point a patient or a link while handling a write. The source system's reference MUST NOT replace the openChart patient identifier. This restates the ratified `expanded-patient-intake` rule on external identifiers and does not modify it.

#### Scenario: Failure: the references name different patients
- **WHEN** a write names `OC-PAT-00001`, but the active row for the source system's reference belongs to another `OC Patient`
- **THEN** openChart refuses it with reason `patient_link_mismatch`, stores no clinical content, and records an integration exception holding only identifiers and a coded cause for identity review (design call AD-26)

#### Scenario: Failure: the link is in identity review
- **WHEN** the source system's identifier row on the named patient has status `identity_review`
- **THEN** openChart refuses the write with reason `patient_link_in_review` and changes no identifier

#### Scenario: Failure: no link exists
- **WHEN** no row for the source system's reference exists
- **THEN** openChart refuses the write with reason `patient_link_unknown` and creates no patient or link

### Requirement: AW-04 Only operational writes are recorded; scenario and simulation content never reaches operational records
openChart SHALL record a write only when its `context` is `operational`. A write whose `context` is `scenario` or `simulation` SHALL be refused with reason `non_operational_context` and SHALL store no clinical content (design call AD-18). No operational record SHALL reference a scenario or simulation output as its content, its evidence target or its authority.

#### Scenario: Failure: a scenario consult reaches the write path
- **WHEN** a schema-valid `consult.write` with `context` `scenario` arrives
- **THEN** openChart refuses it with reason `non_operational_context` and creates no record

### Requirement: AW-05 Writes are idempotent and replay-safe
The `message_id` of each inbound message SHALL be its idempotency key. Idempotency and duplicate detection SHALL be scoped to the authenticated integration identity, that is, to its practice and source system (AW-02): a `message_id`, a `consult_id` and an `act_id` are matched only against messages and records from the same practice and source system, never across integrations. A message whose `message_id` was already processed SHALL be answered with the original receipt and SHALL change nothing. A write that repeats a `consult_id` and `consult_version`, or an `act_id` and `act_version`, under a new `message_id` with identical content SHALL be answered `duplicate` with the original `record_ref`. The same identifiers with different content SHALL be refused with reason `conflicting_duplicate`, SHALL leave the existing record unchanged, and SHALL be recorded as an integration exception that holds only identifiers and a coded cause. A quarantined consult (AC-11) counts for these rules only as follows: a repeat with identical content is evaluated afresh and refused as AC-11 states, adding no copy; a repeat with different content is refused with `conflicting_duplicate`, and the first quarantined copy is kept unchanged. The `message_id` of every message openChart sends SHALL be a random UUID, reused on every retry. No key SHALL carry PHI.

#### Scenario: Failure: a write is retried three times
- **WHEN** the same `consult.write` arrives three times with the same `message_id`
- **THEN** openChart holds one consult record and answers with the same receipt each time

#### Scenario: Failure: a consult version is rewritten with different content
- **WHEN** a second write for an existing `consult_id` and `consult_version` carries a different exchange
- **THEN** openChart refuses it with reason `conflicting_duplicate`, the existing record is unchanged, and an integration exception holds only identifiers and the coded cause

#### Scenario: Failure: two integrations use the same consult identifier
- **WHEN** two practices' AI systems each write a consult with `consult_id` `SYN-CONSULT-0001` and `consult_version` 1, with different content
- **THEN** openChart records both, each under its own practice and source system, and answers neither as `duplicate` or `conflicting_duplicate`

### Requirement: AW-06 Every write and every notice gets exactly one receipt, and a refused write stores no clinical content
openChart SHALL answer every `consult.write`, `act.write` and `authority.notice` it receives with exactly one `write.receipt`. The receipt SHALL carry `accepted`, `duplicate` or `refused`. An accepted or duplicate receipt SHALL carry openChart's `record_ref`. A refused receipt SHALL carry one reason code from the schema and no `record_ref`. openChart SHALL durably record every receipt it sends.

When more than one refusal reason applies, openChart SHALL check in this order and report the first that applies (design call AD-29):
1. `schema_invalid`, then `unsupported_major_version`;
2. `unauthorized`;
3. a replayed `message_id` (the original receipt), then `duplicate` or `conflicting_duplicate` (AW-05);
4. `non_operational_context`;
5. `content_digest_mismatch`;
6. `patient_link_unknown`, `patient_link_mismatch`, `patient_link_in_review`;
7. for an `act.write`: `tier2_not_in_force`, then `act_type_unsupported` (AA-01);
8. the grant checks, in the order of AG-06's table;
9. for an `act.write`: `emergency_management_refused`, `reserved_act_refused`, `targets_clinician_record`, `allowlist_entry_unknown`, `allowlist_entry_mismatch`, `conditions_unverified`, then, for a prescription, `prescribing_gate_not_open` (AA-03), a reason that the MINOR version putting Tier 2 in force adds.

For an `authority.notice`, steps 1 to 3 apply, then `notice_would_widen`. Whatever reason a refused `act.write` carries, a set emergency indicator SHALL make its refusal record urgent for the patient's responsible clinician and the medical director (AA-06).

A refused write SHALL store no clinical content, with one exception. A `consult.write` refused at step 8, after passing steps 1 to 6, SHALL be kept as quarantined AI communication under AC-11, because its answer has already reached the patient, and its source, content and patient are established. What is stored then is exactly what AC-11 lists, and none of it is returned to the source system. No refused `act.write`, and no write refused at any other step, stores clinical content. For every refused write, openChart SHALL keep a refusal record holding only identifiers, the write kind, the act class where there is one, the claimed mode, the reason code and the time (design call AD-7). The refusal record SHALL be visible as AW-09, AC-06 and AA-12 state.

#### Scenario: Failure: an act write is refused
- **WHEN** openChart refuses an `act.write`
- **THEN** the receipt carries `refused` and one reason code, openChart stores no part of the act's content, and the refusal record holds only identifiers and codes

#### Scenario: Failure: a consult is refused at the grant checks
- **WHEN** an authenticated, intact, operational `consult.write` for a linked patient is refused with reason `grant_expired`
- **THEN** the receipt carries `refused`, the reason and no `record_ref`; the refusal record holds identifiers and codes; and the consult is kept only as quarantined AI communication (AC-11)

#### Scenario: Failure: an act arrives under advice only before Tier 2 exists
- **WHEN** an `act.write` arrives for a practice whose grant is `advice_only`, on a deployment where Tier 2 is not in force
- **THEN** openChart refuses it with reason `tier2_not_in_force`, which step 7 reports before the grant checks of step 8

### Requirement: AW-07 No PHI in logs, errors, receipts, notifications, diagnostics or keys
openChart's logs, errors, diagnostics, idempotency keys, clinician notifications and every receipt, notice and status message it sends under the contract MUST NOT contain names, dates of birth, contact details, patient identifier values, exchange or summary text, act content or any other clinical content. Diagnostics SHALL reference writes only by `message_id`, `consult_id`, `act_id`, `record_ref` and grant identifiers. A clinician notification on any device SHALL say only that a record awaits attention, with a coded cause and an opaque reference. Opening the record SHALL require an authenticated openChart session.

#### Scenario: Failure: a write is refused for a patient-link mismatch
- **WHEN** openChart refuses a write with reason `patient_link_mismatch`
- **THEN** the log entry and the receipt carry the `message_id` and the coded reason, and no patient identifier value or clinical text

#### Scenario: Failure: an always-review consult notifies the patient's doctor
- **WHEN** openChart notifies a clinician that an AI consult was selected for review
- **THEN** the notification carries only the coded cause and an opaque record reference

### Requirement: AW-08 openChart's outbound messages under the contract use durable delivery
Every `write.receipt` that is not returned synchronously, and every `act.status`, `consult.reviewed`, `authority.notice` and `message.ack` openChart sends, SHALL be written to a durable outbound store in the same transaction as its cause. openChart SHALL deliver them to the registered AI system with retries that reuse the original `message_id`, until the AI system answers with `message.ack` where the message calls for one. This follows the pattern of PL-14 in `define-openpractice-boundary` (not yet on main); the mechanism is decided in planning. Delivery MUST NOT rely on `frappe.publish_realtime` or any other site-local event.

#### Scenario: Failure: the AI system is unreachable
- **WHEN** the AI system is unreachable while openChart has an `authority.notice` and two `act.status` messages to send
- **THEN** the messages stay in the durable store and are delivered with their original `message_id` when the AI system returns, and no record changes state because of the outage

### Requirement: AW-09 AI authorship and the authority it rested on are shown wherever openChart shows an AI-authored record
Wherever openChart shows an AI-authored record, to a clinician or to a patient, on mobile or workstation (ruling 35), it SHALL label the record as AI-authored and name its source system. For a clinician, the label SHALL include the mode in force, the grant and its version, and for an act the allowlist entry or full-practice grant and the co-review status. Every patient-facing display that openChart originates or releases, including one that a system it drives presents, SHALL say that the content was written by an AI system, not by a clinician, and SHALL state its review or co-review status without implying a clinician's prior sign-off. AI-authored content MUST NOT be presented as clinician-authored on any surface. A consult record SHALL also carry the label of AC-04 (ruling 66).

#### Scenario: Failure: a patient view would omit the AI label
- **WHEN** a patient-facing view released by openChart would show an AI consult summary without the AI-authored label
- **THEN** openChart does not release the view without the label and the review status

#### Scenario: Failure: an AI act appears in a clinician's list
- **WHEN** a clinician opens a patient's chart that holds an accepted AI-authored act
- **THEN** the act is labelled AI-authored with its source system, mode, grant version and co-review status, and is never shown as clinician-authored

### Requirement: AW-10 openChart operates without any external clinical AI system
openChart SHALL operate fully with no external clinical AI system registered and no authority grant recorded. Every component of this change SHALL be optional. With no registered system, the write path SHALL accept nothing, and no other operation SHALL depend on it. This requirement restates the ratified `expanded-patient-intake` rule that the application must operate without MedxFactory, MedxEHR or openPractice, and does not weaken it.

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no AI system registered
- **THEN** migrations complete and the golden-patient intake tests pass

#### Scenario: Failure: a write reaches a site with no AI system registered
- **WHEN** a `consult.write` reaches an openChart site where no AI system is registered
- **THEN** openChart refuses it with reason `unauthorized`, stores no clinical content, and every other operation is unaffected

### Requirement: AW-11 The write path is covered by contract tests written first
The write path SHALL be covered by contract tests, written first, that validate every message against the schema at the digest recorded in `contracts/SHA256SUMS`, run against an AI-system double, and use synthetic data only. The fixtures in this change's `contracts/examples/` SHALL be part of the suite. The tests SHALL cover: every reason code; idempotency, duplicates and conflicting duplicates; every patient-link case; scenario and simulation refusal; every grant check in AG-06; the always-review triggers; review and co-review outcomes; narrowing and pause; refusal of every `act.write` while Tier 2 is not in force; readback by digest; the AI-authorship labels; and the absence of PHI in logs, receipts, notifications, readbacks and keys. The standalone golden-intake tests SHALL pass with the write path unconfigured.

#### Scenario: CI runs the write-path suite
- **WHEN** CI runs the write-path contract tests
- **THEN** they pass against the AI-system double with synthetic data only

#### Scenario: Failure: a fixture adds clinical text to a receipt
- **WHEN** a test builds an `act.status` that carries free text
- **THEN** schema validation fails, and the test expects that failure

### Requirement: AW-12 The writing source system can read back what openChart stored, by digest and code only
openChart SHALL answer a `record.readback_request` with exactly one `record.readback`, so that the source system that wrote a record, or a relay acting for it, can confirm what openChart stored (design call AD-28). Only the integration identity of the source system that wrote the record SHALL be answered with `found`. For a found record, the answer SHALL carry only: the record reference; the source system's record identifier and version; the stored content digest, recomputed by openChart from what it stored (for a consult, as `exchange.content_sha256` is defined; for an act, over its stored `act_content`); the grant version it was checked against; its current state; and its review or co-review status. A readback MUST NOT carry exchange text, summary text, act content, patient identifiers or any other clinical content. A request from any other identity SHALL be answered `unauthorized`, and one for an unknown record `not_found`, each with no record detail. A quarantined consult (AC-11) is not an accepted record: its reference is never sent to the source system, and a readback that names it SHALL be answered `not_found`.

#### Scenario: A relay confirms a stored consult
- **WHEN** the writing source system requests a readback of a consult it wrote and openChart accepted
- **THEN** openChart answers `found` with the record identifiers, the stored content digest, the grant version checked, the state and the review status, and no clinical text

#### Scenario: Failure: another system asks for a readback
- **WHEN** an integration identity registered for a different source system requests a readback of that record
- **THEN** openChart answers `unauthorized` and discloses no record detail

#### Scenario: Failure: the record does not exist
- **WHEN** a readback names a record reference openChart does not hold
- **THEN** openChart answers `not_found` with no digest, state or status

### Requirement: AW-13 An integration identity can be suspended or deregistered at once, and a per-source quarantine cap suspends it
openChart SHALL provide an audited suspend act and an audited deregister act on an integration identity, each effective at once (design call AD-37). While an identity is suspended, and after it is deregistered, every message from it SHALL fail at step 2 of AW-06's precedence with reason `unauthorized`, and SHALL store no clinical content; nothing it sends is quarantined. The medical director, or a holder of the administrative role that the foundation's AU-01 names, MAY suspend an identity. Only the medical director SHALL lift a suspension. The medical director or a holder of that administrative role MAY deregister an identity; a deregistered identity is never re-enabled, and only a new registration under AW-02 restores a path. Every suspension, lift and deregistration SHALL be recorded with actor, reason and time, and listed for the medical director and the administrative role.

openChart SHALL count, per source system and practice, the consults quarantined under AC-11 in any rolling 24 hours. The practice's policy sets the cap, which SHALL NOT exceed a built-in ceiling of 20; with no policy set, the ceiling applies (design call AD-37). When a source reaches its cap, openChart SHALL quarantine that consult, suspend the source's identity at once as if by the suspend act, and alert the medical director, or, where none is designated, the administrative role, with identifiers and a coded cause only.

#### Scenario: Failure: the administrative role suspends an unsafe source
- **WHEN** a holder of the administrative role that the foundation's AU-01 names suspends an AI system's integration identity
- **THEN** every later write from it is refused with reason `unauthorized` and stores no clinical content, and the suspension is listed for the medical director

#### Scenario: Failure: someone other than the medical director lifts a suspension
- **WHEN** a holder of the administrative role tries to lift a suspension
- **THEN** the action is refused, and the identity stays suspended until the medical director lifts it

#### Scenario: Failure: a deregistered identity writes
- **WHEN** a write arrives from a deregistered integration identity
- **THEN** openChart refuses it with reason `unauthorized`, stores no clinical content, and offers no way to re-enable that identity

#### Scenario: Failure: a source reaches its quarantine cap
- **WHEN** a source's twentieth consult in 24 hours is quarantined, with no lower cap set
- **THEN** openChart quarantines it, suspends the source's identity at once, and alerts the medical director; the next write from that source is refused with reason `unauthorized`
