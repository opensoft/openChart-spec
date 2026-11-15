## ADDED Requirements

### Requirement: AW-01 AI-authored records enter openChart only through the versioned write-path contract
openChart SHALL accept content authored by an external clinical AI system only as messages under contract `openchart-ai-clinical-record-write/1.0`, owned by this change. Its canonical schema is:
- `openspec/changes/define-ai-authored-clinical-records/contracts/openchart-ai-clinical-record-write-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-ai-clinical-record-write:1.0`, at the SHA-256 recorded in this change's `contracts/SHA256SUMS`.

The digest identifies the schema even after archival moves the file. openChart SHALL validate every message it receives or sends under the contract against the schema at that digest. The messages are `consult.write`, `act.write`, `authority.notice`, `write.receipt`, `act.status`, `consult.reviewed`, `record.readback_request`, `record.readback`, `grant.readback_request`, `grant.readback` and `message.ack`. Implementations are compatible exactly when they share the MAJOR version. openChart SHALL accept a `1.x` message at a MINOR version it has declared, refuse a message whose MAJOR version it does not support with reason `unsupported_major_version`, and refuse a message that fails the schema with reason `schema_invalid`. A refusal SHALL store no clinical content. A breaking change SHALL require a new MAJOR version and a new digest, recorded in this change and in every companion that cites it. Until this change is ratified, the draft 1.0 schema MAY still change, as it did for ruling 80 and again to fit the clinical-acts foundation's recommendation record; each change records a new digest here and in every companion that cites it (design call AD-48). Every rule of the schema SHALL hold whether or not the validator asserts `format`: timestamps and UUIDs are checked by pattern only, and the timestamp pattern is the clinical-acts foundation's own, character for character (its design, section 1), so that no receiver's validator setting changes what is valid. A timestamp that names a day its month does not have, such as 30 February, passes the pattern; openChart SHALL refuse such a write as malformed, with `schema_invalid`, by a check beside the schema, as the foundation's verifier checks calendar time (its CA-08; design call AD-48).

#### Scenario: Failure: a write carries a property the schema does not define
- **WHEN** a `consult.write` arrives with a property the schema does not define, such as `diagnosis`
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: an unsupported major version arrives
- **WHEN** a `consult.write` with `contract_version` `2.0` arrives
- **THEN** openChart refuses it with reason `unsupported_major_version` and stores no clinical content

### Requirement: AW-02 Only a registered writer may write, and every write names its writer, the AI on whose behalf it writes and the source system
openChart SHALL accept write-path messages only from an authenticated integration identity that is registered for exactly one external clinical AI system, identified by its `source_system` (issuer and namespace), and exactly one practice. The identity SHALL hold a dedicated write-path integration role that is narrower than `System Manager`, is named in planning, and is authorized for subject, tenant, purpose and role, as the ratified API requirement demands. Registering an AI system SHALL be an audited act by a named human, and SHALL be refused while no AU-01 designation of the foundation is in force for the practice. The registration SHALL record the writer's system identity and its operator, and the openWallet ID of each AI that the source system may write for (ruling 80, clause 3 and part B; design call AD-49). No AI system and no agent SHALL register, widen or re-scope an integration identity, or add an openWallet ID to a registration. Removing an openWallet ID from a registration SHALL be audited and effective at once (ruling 80, clause 3). This requirement applies the foundation's AN-01 to AN-03 (`define-clinical-acts-foundation` at head `f85e742`) to the write path: an addition is refused, with nothing stored, only for a reason that concerns its writer (it cannot be identified, it is not registered, or it is suspended), each kind of party is identified in its own recorded way, and every system is registered with the practice before it adds.

**What every write names (ruling 80, clauses 2, 6 and 7).** Every `consult.write` and `act.write` SHALL name:
- `added_by`: the writer, which is the registered integration identity that delivers the write, by its system identity (issuer and namespace) and its operator, `operator_ref`;
- `on_behalf_of`: every party the write passed through before the writer, in order from the originator to the writer. The first is always the AI that produced the content, identified by its `openwallet_id`, with the `model` and `model_version` that produced it. When the writer is a relay, the second is the source system, by its system identity and operator, and its system identity equals the write's `source_system`. When the writer is the source system's own identity, the AI is the only entry. The 1.0 contract admits no other party in `on_behalf_of`, and no human.

openChart SHALL refuse with `unauthorized`, at step 2 of AW-06, and store no clinical content, a write whose writer it cannot identify or that is not registered for what the write claims: a write whose `added_by` is not the registration of the identity that sent it, or whose `on_behalf_of` names a source system that registration does not cover or names it out of the order above (ruling 80, clauses 2 and 3; the foundation's AN-01 and AN-03). A write whose writer is identified and registered, but whose AI has no `openwallet_id`, or one that the writer's registration does not cover, SHALL NOT be refused. By default openChart SHALL hold it in this path's quarantine, outside the chart and in front of a clinician, and alert the administrative role that the foundation's AU-01 names to fix the registration (the AI check of AW-06; AC-11; design call AD-60, PROPOSED). That default follows the foundation's AN-01 and its design call CD-61, a reading of ruling 90's accepted words that is with the owner as the foundation's Open Question 22. A value in `openwallet_id` that does not have openWallet's identifier shape is not an openWallet ID: the write is malformed and refused with `schema_invalid`. openChart compares the openWallet ID exactly with the registration. The schema gives it the identifier shape of openWallet's wallet record: 1 to 200 characters, a letter or digit first, then letters, digits, `.`, `_`, `:`, `/` or `-`. It identifies the AI only: it never identifies a person or a patient, openChart resolves no subject by it, and no chart function needs the wallet to be reachable (the foundation's AN-02; design call AD-49; tension AT-16). openChart SHALL record the writer as identified by the chart itself (`identity_basis` `verified_by_chart`), and the AI and the source system as asserted by the writer (`asserted_by`), because only the writer authenticates to openChart. The `model` and `model_version` are recorded as the writer states them (design call AD-49; Open Question 12).

**Relays.** The integration identity MAY be held by a relay that delivers one source system's writes and returns its receipts, as ruling 70 provides for the medical AI's records. The relay SHALL be registered for that one source system and practice. It is the writer: each write it delivers names it in `added_by`, names the source system in `source_system` and second in `on_behalf_of`, and names the AI first (ruling 80, clause 7). The registration SHALL record whether the source is relay-only. A source whose owner has ruled that it writes only through a relay SHALL be registered relay-only, by the named human, citing that ruling. For a relay-only source, openChart SHALL register only the relay's integration identity, SHALL refuse to register a direct identity for it, and SHALL refuse with `unauthorized` any write naming it that does not come from its relay. A source system's namespace SHALL be the source token that MI-12 of `define-clinical-message-inbox` uses for it, where MI-12 defines one. `healthlinc` and `openpractice_agent` SHALL NOT be write-path systems, whether as the source, the writer or any party named on a write, and `openchart` SHALL NOT be a system namespace; the schema refuses all three (design calls AD-30 and AD-49).

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

#### Scenario: A relay's write names itself, the AI and the source system
- **WHEN** a relay registered for one source system delivers a `consult.write` whose `added_by` is the relay, and whose `on_behalf_of` names first the AI, by an `openwallet_id` registered for that source, with its model and model version, and then the source system
- **THEN** openChart records the relay as the writer, identified by the chart, and the AI and the source system as asserted by the relay

#### Scenario: Failure: a write names an AI whose openWallet ID is not registered
- **WHEN** a registered relay sends a `consult.write` whose `on_behalf_of` names an `openwallet_id` that is not registered for the write's source system
- **THEN** openChart neither refuses it nor adds it to the chart: it holds the write in quarantine with `quarantine_cause` `openwallet_id_not_covered`, answers `quarantined`, puts it in front of a clinician, and alerts the administrative role to fix the registration (design call AD-60, PROPOSED)

#### Scenario: Failure: a write names its AI without an openWallet ID
- **WHEN** a registered relay sends an `act.write` whose AI carries a model and model version but no `openwallet_id`
- **THEN** openChart holds the write in quarantine with `quarantine_cause` `openwallet_id_missing`, answers `quarantined`, records no recommendation while it is held, and stores nothing in the chart

#### Scenario: Failure: a write names another writer
- **WHEN** a registered identity sends a write whose `added_by` names a different system or operator
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
openChart SHALL record a write only when its `context` is `operational`. A write whose `context` is `scenario` or `simulation` SHALL be refused with reason `non_operational_context` and SHALL store no clinical content (design call AD-18). No operational record SHALL reference a scenario or simulation output as its content, its evidence target or its authority. A refused `scenario` or `simulation` write SHALL never be listed urgently, whatever flags it carries; its refusal record keeps them (AW-06).

#### Scenario: Failure: a scenario write carries the emergency indicator
- **WHEN** a schema-valid `consult.write` with `context` `scenario` and `emergency_indicated` true names a linked patient
- **THEN** openChart refuses it with reason `non_operational_context`, the refusal record keeps the flag, and nothing is listed for that patient's clinicians

#### Scenario: Failure: a scenario consult reaches the write path
- **WHEN** a schema-valid `consult.write` with `context` `scenario` arrives
- **THEN** openChart refuses it with reason `non_operational_context` and creates no record

### Requirement: AW-05 Writes are idempotent and replay-safe
The `message_id` of each inbound message SHALL be its idempotency key. Idempotency and duplicate detection SHALL be scoped to the authenticated integration identity, that is, to its practice and source system (AW-02): a `message_id`, a `consult_id` and an `act_id` are matched only against messages and records from the same practice and source system, never across integrations. A message whose `message_id` was already processed SHALL be answered with the original receipt and SHALL change nothing. A write that repeats a `consult_id` and `consult_version`, or an `act_id` and `act_version`, under a new `message_id` with the same content digest SHALL be answered `duplicate` with the first submission's result: `first_result`, the first `record_ref` and its codes, a quarantined write's `quarantine_cause` or a recommendation's `missing_authority` and `path_reason`. It SHALL add no copy and change nothing (the foundation's AN-10). The same identifiers with a different content digest SHALL NOT be refused. openChart SHALL check the write as a new addition through the rest of AW-06, keep it as whatever that makes it, and flag it `submission_ref_conflict`, naming the first record's `record_ref` and stored content digest. It SHALL tell the writer at once, in a receipt that carries the same flag. Both records stay, and the first is never rewritten, because a record is permanent and a correction is a new dated addition (ruling 80, clause 8; the foundation's AN-10 and design call CD-64; design call AD-61). openChart SHALL also list the conflict for the medical director as an integration exception that holds only identifiers and a coded cause (design call AD-26). A quarantined consult, a held write (AC-11) and a recommendation (AW-16) are records for these rules. Nothing the AI system or its relay sends turns a quarantined consult or a held write into an accepted one, or a recommendation into a decision (ruling 151). The `message_id` of every message openChart sends SHALL be a random UUID, reused on every retry. No key SHALL carry PHI.

#### Scenario: Failure: a write is retried three times
- **WHEN** the same `consult.write` arrives three times with the same `message_id`
- **THEN** openChart holds one consult record and answers with the same receipt each time

#### Scenario: Failure: a consult version is rewritten with different content
- **WHEN** a second write for an existing `consult_id` and `consult_version` carries a different exchange
- **THEN** openChart does not refuse it: it checks the second write as a new addition, keeps it as a new record flagged `submission_ref_conflict` with the first record and its digest, answers with that flag, leaves the first record unchanged, and lists an integration exception holding only identifiers and the coded cause

#### Scenario: Failure: two integrations use the same consult identifier
- **WHEN** two practices' AI systems each write a consult with `consult_id` `SYN-CONSULT-0001` and `consult_version` 1, with different content
- **THEN** openChart records both, each under its own practice and source system, and answers neither as `duplicate` nor flags either as a conflict

#### Scenario: Failure: a recommendation is re-sent
- **WHEN** an `act.write` was recorded as a recommendation, and the AI system re-sends the same `act_id`, `act_version` and content under a new `message_id`
- **THEN** openChart answers `duplicate` with `first_result` `recorded_as_recommendation`, the original `record_ref`, `missing_authority` and `path_reason`, adds no copy, and the record stays a recommendation

### Requirement: AW-06 Every write and every notice gets exactly one receipt; only an identification, integrity, context or patient-link failure, or a suspended writer, refuses a write, and missing authority never does
openChart SHALL answer every `consult.write`, `act.write` and `authority.notice` it receives with exactly one `write.receipt`, with one of these results:
- `accepted`, with openChart's `record_ref`;
- `duplicate`, for a repeat of a write already recorded, with the first submission's result as `first_result`, its `record_ref` and its codes (AW-05; the foundation's AN-10);
- `recorded_as_recommendation`, only for an `act.write` recorded under AW-16, with the `record_ref`, which is the recommendation's identifier, the foundation's `missing_authority` codes and this contract's `path_reason`, as below (the foundation's AN-10);
- `quarantined`, for a `consult.write` kept under AC-11, or for any write held by the AI check below, with the `record_ref` and the `quarantine_cause` code. `quarantined` is this path's `held_in_quarantine` (the foundation's AN-01);
- `refused`, with one reason code from the schema and no `record_ref`.

A receipt for a write kept under AW-05's `submission_ref_conflict` carries that flag. openChart SHALL durably record every receipt it sends. An `authority.notice` is never recorded as a recommendation or quarantined.

When more than one check fails, openChart SHALL check in this order and act on the first that fails (design call AD-29). Steps 1, 2 and 4 to 6 refuse the write, each on a ground that ruling 80, clause 18 keeps and the foundation's AN-12 lists; step 3 answers a repeat and refuses nothing:
1. `schema_invalid`, then `unsupported_major_version`: the content is malformed, because the chart cannot read it or it breaks this contract's envelope (clause 18);
2. `unauthorized`: the writer cannot be identified, or is not registered for what the write claims (AW-02; clauses 2 and 3), or the practice has suspended it: it is manually suspended or deregistered, or cap-suspended for every act and for a consult without the emergency indicator or `red_flag` (AW-13; clause 18);
3. a repeat (AW-05): a replayed `message_id` is answered with the original receipt, and an identical repeat under a new `message_id` with `duplicate` and the first result; neither adds anything. A repeat of a record's identifiers with a different content digest goes on through the steps below as a new addition, flagged `submission_ref_conflict` (clause 8);
4. `non_operational_context`: test data, as its writer declares it in `context` (AW-04; clause 18). openChart never infers test data from content, as the foundation's AN-12 requires;
5. `content_digest_mismatch`: the content is malformed, because it does not match its own digest (clause 18);
6. `patient_link_unknown`, `patient_link_mismatch`, `patient_link_in_review`: the patient cannot be matched (AW-03; clause 18).

**The AI check (design call AD-60, PROPOSED).** A write that passes steps 1 to 6 and names an AI with no `openwallet_id`, or with one that the writer's registration does not cover, SHALL NOT be refused and SHALL NOT be added to the chart. By default openChart SHALL hold it in quarantine under AC-11, with `quarantine_cause` `openwallet_id_missing` or `openwallet_id_not_covered`, before any authority check, because no authority can be judged for an AI the chart cannot identify. This is the foundation's AN-01 default (its design call CD-61), which reads ruling 90's accepted words as covering this case and is with the owner as its Open Question 22. If the owner chooses another reading, this check changes with it.

Steps 7 to 9 check authority. A write that passes steps 1 to 6 and the AI check, and fails one of them, SHALL NOT be refused, because missing authority is never a reason to refuse an addition (ruling 80, clause 18; design call AD-51). An `act.write` is recorded as a recommendation under AW-16, and a `consult.write` is kept as a quarantined consult under AC-11. The code of the first check that fails, in this order, is a consult's `quarantine_cause`, or an act's `path_reason` code:
7. for an `act.write`: `tier2_not_in_force`, then `act_type_unsupported` (AA-01);
8. the grant checks, in the order of AG-06's table;
9. for an `act.write`: `emergency_management_refused`, `reserved_act_refused`, `targets_clinician_record`, `allowlist_entry_unknown`, `allowlist_entry_mismatch`, `conditions_unverified`, then, for a prescription, `prescribing_gate_not_open` (AA-03), a code that the MINOR version putting Tier 2 in force adds.

These codes keep their names, two of which say "refused": each names the authority that was missing, and none refuses a write (design call AD-56). For an `authority.notice`, steps 1 to 3 apply, then `notice_would_widen`, which refuses the notice.

**The codes of a recommendation.** A recommendation carries two code sets, as the foundation's AN-09 provides for a writing path that has reasons of its own (its design call CD-51; design call AD-57):
- `path_reason`: this contract's own code for the first check that failed, under the scheme `openchart-ai-clinical-record-write.missing_authority`, version `1.0`. It is kept for the source and the reviewer, and decides nothing;
- `missing_authority`: the code of the foundation's closed list that the path code maps to, and `no_practitioner_sign_off`. Every recommendation on this path carries `no_practitioner_sign_off`, because no practitioner has signed off an AI's act and the 1.0 contract carries no sign-off (ruling 151; the foundation's CA-04).

| `path_reason` code | `missing_authority` |
|---|---|
| `tier2_not_in_force`, `act_type_unsupported`, `mode_not_permitted`, `emergency_management_refused`, `reserved_act_refused`, `targets_clinician_record` | `no_decision_authority`, `no_practitioner_sign_off` |
| `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `approver_mismatch`, `legal_review_mismatch`, `allowlist_entry_unknown`, `allowlist_entry_mismatch`, `conditions_unverified` | `no_grant_in_force`, `no_practitioner_sign_off` |
| `prescribing_gate_not_open`, which the Tier 2 MINOR version adds (AA-03) | `no_practitioner_sign_off`, and `no_decision_authority` while an AI holds none. The gate code goes in `path_reason` only, because a safety gate is never a missing authority (the foundation's AN-09) |

The schema refuses any other combination. The foundation's contract requires `no_practitioner_sign_off` of every recommendation whose decision maker is not a human (its AN-08 and AN-09), and this contract requires it of every recommendation it reports. The foundation's other six codes are never true of an addition on this path: `decision_maker_not_confirmed`, because the AI is always the decision maker named (AW-16); `wallet_not_bound`, `licence_verification_missing`, `attestation_not_verified` and `signing_service_unavailable`, because they concern a practitioner's sign-off attempt, which the 1.0 contract does not carry; and `practice_attestation_not_in_force`, because an AI's grant rests on a recorded legal review, not on a practice attestation. While Tier 2 is not in force, every act's first failing check is `tier2_not_in_force`, so every recommendation carries `missing_authority` `no_decision_authority` and `no_practitioner_sign_off`, with `path_reason` `tier2_not_in_force`.

Whatever step refuses a schema-valid write, its refusal record SHALL keep the emergency indicator, and for a consult a declared `red_flag`, when the request carried them, whoever sent it. Such a refusal SHALL be listed urgently only when the write's `context` is `operational` and it comes from a registered identity that is active, cap-suspended or manually suspended: never from an unregistered caller or a deregistered identity, and never from a `scenario` or `simulation` context (AW-04; design call AD-43). Where it is listed, it is listed without content, and beyond the per-source ceiling of AW-13 it is collapsed into that source's digest: where the patient resolves through an existing link (AW-03, changing nothing), for the patient's responsible clinician and the medical director, with AC-11's fallback recipients; otherwise for the medical director, or, where none is designated, as an alert to the administrative role that the foundation's AU-01 names carrying an opaque reference and a coded cause. A recommendation, a quarantined consult or a held write is not a refusal: it is listed with its content under AW-16, AA-06 or AC-11, urgently when its emergency indicator is set or, for a consult, when its `review_flags` carry `red_flag`.

A refused write SHALL store no clinical content. For every refused write, openChart SHALL keep a refusal record holding only identifiers, the write kind, the act class where there is one, the claimed mode, the reason code, the time, and the emergency indicator and `red_flag` when the request declared them (design call AD-7). The refusal record SHALL be visible as AW-09, AC-06 and AA-12 state.

#### Scenario: Failure: an act write is refused for a patient-link mismatch
- **WHEN** openChart refuses an `act.write` with reason `patient_link_mismatch`
- **THEN** the receipt carries `refused` and that reason, openChart stores no part of the act's content, and the refusal record holds only identifiers and codes

#### Scenario: Failure: a consult fails the grant checks
- **WHEN** an identified, intact, operational `consult.write` for a linked patient fails the grant checks with `grant_expired`
- **THEN** the receipt carries `quarantined`, the `record_ref` and `quarantine_cause` `grant_expired`, and the consult is kept as quarantined AI communication (AC-11)

#### Scenario: Failure: an act arrives under advice only before Tier 2 exists
- **WHEN** an `act.write` arrives for a practice whose grant is `advice_only`, on a deployment where Tier 2 is not in force
- **THEN** openChart records it as a recommendation with `path_reason` `tier2_not_in_force`, which step 7 reports before the grant checks of step 8, and `missing_authority` `no_decision_authority` and `no_practitioner_sign_off`, and answers `recorded_as_recommendation` with the `record_ref` and both code sets

#### Scenario: Failure: an act lacks authority and its patient link is unknown
- **WHEN** an `act.write` that no grant authorizes names a patient reference for which no link exists
- **THEN** openChart refuses it with reason `patient_link_unknown`, because step 6 comes before the authority checks, and stores no clinical content

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

**Notice clock.** openChart owns a clock on every `authority.notice` it sends (design call AD-41). When the source has not acknowledged a notice with `message.ack` within 15 minutes of the change taking effect, openChart SHALL alert the medical director with identifiers and a coded cause, and the administrative role that the foundation's AU-01 names with an opaque reference and a coded cause only, and SHALL re-alert every 15 minutes until the source acknowledges the notice or a human acknowledges the alert. Each recipient MAY acknowledge the alert, and openChart SHALL record who did, why and when (design call AD-46). The medical director's acknowledgment stops the re-alerts for that notice. A holder of the administrative role's acknowledgment stops only the administrative role's re-alerts, never the medical director's. A human acknowledgment never stands in for the source's `message.ack`: retrying continues, except for a `deregistered` notice, whose retrying the medical director's acknowledgment, or the administrative role's where no AU-01 designation is in force, also ends, because openChart serves that identity for nothing else (AW-13). openChart applies every change itself, at once: it refuses, quarantines or records as a recommendation each write by its own records, and nothing depends on the source obeying the notice.

#### Scenario: Failure: a suspension notice is never acknowledged
- **WHEN** openChart suspends a source manually, and the source does not acknowledge the `suspended` notice within 15 minutes
- **THEN** openChart alerts the medical director, and the administrative role without content, keeps retrying and re-alerting every 15 minutes, and keeps refusing every write from the source

#### Scenario: Failure: a deregistered source is gone and never acknowledges
- **WHEN** a deregistered source never acknowledges its last notice, and the medical director acknowledges the alert
- **THEN** openChart records who acknowledged it, why and when, stops re-alerting, and stops retrying that notice

#### Scenario: Failure: the administrative role acknowledges a notice alert
- **WHEN** a `suspended` notice stays unacknowledged by the source, and a holder of the administrative role acknowledges the alert
- **THEN** openChart records the acknowledgment and stops re-alerting the administrative role, and keeps re-alerting the medical director every 15 minutes until the medical director acknowledges

#### Scenario: Failure: the AI system is unreachable
- **WHEN** the AI system is unreachable while openChart has an `authority.notice` and two `act.status` messages to send
- **THEN** the messages stay in the durable store and are delivered with their original `message_id` when the AI system returns, and no record changes state because of the outage

### Requirement: AW-09 AI authorship and the authority it rested on are shown wherever openChart shows an AI-authored record
Wherever openChart shows an AI-authored record, to a clinician or to a patient, on mobile or workstation (ruling 35), it SHALL label the record as AI-authored and name its source system. For a clinician, the label SHALL include the mode in force, the grant and its version, and for an act the allowlist entry or full-practice grant and the co-review status. Every patient-facing display that openChart originates or releases, including one that a system it drives presents, SHALL say that the content was written by an AI system, not by a clinician, and SHALL state its review or co-review status without implying a clinician's prior sign-off. AI-authored content MUST NOT be presented as clinician-authored on any surface. A consult record SHALL also carry the label of AC-04 (ruling 66). A recommendation SHALL be marked, on every display, "not an authorized decision", with the authority that was missing (AW-16; ruling 80, clause 13). The provenance of AW-15, the writer and every party on whose behalf the record was written included, SHALL be shown with every record kept from a write, to everyone who can read it (ruling 80, clause 8).

#### Scenario: Failure: a patient view would omit the AI label
- **WHEN** a patient-facing view released by openChart would show an AI consult summary without the AI-authored label
- **THEN** openChart does not release the view without the label and the review status

#### Scenario: Failure: an AI act appears in a clinician's list
- **WHEN** a clinician opens a patient's chart that holds an accepted AI-authored act
- **THEN** the act is labelled AI-authored with its source system, mode, grant version and co-review status, and is never shown as clinician-authored

#### Scenario: Failure: a recommendation would be shown without its marker
- **WHEN** a clinician or patient view would show an AI act recorded as a recommendation without the marker "not an authorized decision" and the authority that was missing
- **THEN** openChart does not show the recommendation without them

### Requirement: AW-10 openChart operates without any external clinical AI system
openChart SHALL operate fully with no external clinical AI system registered and no authority grant recorded. Every component of this change SHALL be optional. With no registered system, the write path SHALL accept nothing, and no other operation SHALL depend on it. This requirement restates the ratified `expanded-patient-intake` rule that the application must operate without MedxFactory, MedxEHR or openPractice, and does not weaken it.

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no AI system registered
- **THEN** migrations complete and the golden-patient intake tests pass

#### Scenario: Failure: a write reaches a site with no AI system registered
- **WHEN** a `consult.write` reaches an openChart site where no AI system is registered
- **THEN** openChart refuses it with reason `unauthorized`, stores no clinical content, and every other operation is unaffected

### Requirement: AW-11 The write path is covered by contract tests written first
The write path SHALL be covered by contract tests, written first, that validate every message against the schema at the digest recorded in `contracts/SHA256SUMS`, run against an AI-system double, and use synthetic data only. The fixtures in this change's `contracts/examples/` SHALL be part of the suite, which SHALL run with and without `format` assertion, every fixture behaving the same either way (AW-01). The tests SHALL cover: every reason code; idempotency, a repeat answered with the first result, and a repeat with other content kept and flagged; every patient-link case; scenario and simulation refusal; every grant check in AG-06; the always-review triggers; review and co-review outcomes; narrowing and pause; the recording of every `act.write` as a recommendation while Tier 2 is not in force, the mapping of every path code to the foundation's codes (AW-06), every receipt result, the AI check and every way a held write ends (AC-11), an identical repeat answered with the first result and a repeat with other content kept and flagged (AW-05), and the calendar check (AW-01); the identification and provenance of every write (AW-02, AW-15); readback by digest; the grant readback, its computation from every content-independent grant check, the self-contradictory shapes the schema refuses, and the reader's rules; every notice value; the notice clock and its human acknowledgment; the urgent-listing rules and the digest; the AI-authorship labels; and the absence of PHI in logs, receipts, notifications, readbacks and keys. The standalone golden-intake tests SHALL pass with the write path unconfigured.

#### Scenario: CI runs the write-path suite
- **WHEN** CI runs the write-path contract tests
- **THEN** they pass against the AI-system double with synthetic data only

#### Scenario: Failure: a fixture adds clinical text to a receipt
- **WHEN** a test builds an `act.status` that carries free text
- **THEN** schema validation fails, and the test expects that failure

### Requirement: AW-12 The writing source system can read back what openChart stored, by digest and code only
openChart SHALL answer a `record.readback_request` with exactly one `record.readback`, so that the source system that wrote a record, or a relay acting for it, can confirm what openChart stored (design call AD-28). Only the integration identity of the source system that wrote the record SHALL be answered with `found`. For a found record, the answer SHALL carry only: the record reference; the source system's record identifier and version; the stored content digest, recomputed by openChart from what it stored (for a consult, as `exchange.content_sha256` is defined; for an act, over its stored `act_content`); the time openChart received it, `received_at` (AW-15); its current state; for an accepted record, the grant version it was checked against and its review or co-review status; for a recommendation (AW-16), the state `recommendation`, its `missing_authority` codes and its `path_reason`; for a quarantined consult or a held write (AC-11), the state `quarantined` and its `quarantine_cause`; and, for a record kept under AW-05's flag, its `submission_ref_conflict`. A recommendation and a quarantined consult also carry the grant version checked where a grant existed. A readback MUST NOT carry exchange text, summary text, act content, patient identifiers or any other clinical content. A request from any other identity SHALL be answered `unauthorized`, and one for an unknown record `not_found`, each with no record detail. A quarantined consult, a held write and a recommendation are answered `found`, so that the source can confirm what was kept; none is an accepted record, and the review of none is reported (design call AD-52). A held write is answered as held while it is held; the 1.0 contract does not tell the source how it ended (AC-11).

A readback is not an interoperability read in the sense of the foundation's CA-13: it returns no record, only identifiers, digests and codes, and only to the writing source. So the foundation's audit verifier (its CA-08) does not gate it as it gates publication and interoperability reads. Its `stored_content_sha256` is recomputed at read time from what openChart stored, which is how a source detects a stored record that differs from what it sent, so openChart SHALL answer it even when the verifier has reported an integrity failure on that record (design call AD-28).

#### Scenario: A relay confirms a stored consult
- **WHEN** the writing source system requests a readback of a consult it wrote and openChart accepted
- **THEN** openChart answers `found` with the record identifiers, the stored content digest, `received_at`, the grant version checked, the state and the review status, and no clinical text

#### Scenario: Failure: another system asks for a readback
- **WHEN** an integration identity registered for a different source system requests a readback of that record
- **THEN** openChart answers `unauthorized` and discloses no record detail

#### Scenario: Failure: the record does not exist
- **WHEN** a readback names a record reference openChart does not hold
- **THEN** openChart answers `not_found` with no digest, state or status

#### Scenario: Failure: a relay confirms a recommendation
- **WHEN** the writing source system requests a readback of an act that openChart recorded as a recommendation
- **THEN** openChart answers `found` with `record_state` `recommendation`, the `missing_authority` codes and `path_reason`, the stored content digest and `received_at`, and no act content and no review status

### Requirement: AW-13 An integration identity can be suspended or deregistered, and a per-source quarantine cap suspends only its non-urgent consults
openChart SHALL provide two kinds of suspension and a deregistration of an integration identity, each audited and effective at once (design call AD-37). Each is the practice suspending a writer, which ruling 80 keeps as a reason to refuse (clauses 3 and 18); the cap suspension's urgent exemption below keeps in front of a clinician what an AI already told a patient (ruling 90).

**Manual suspension and deregistration.** A human has decided that the source is unsafe. The medical director, or a holder of the administrative role that the foundation's AU-01 names, MAY suspend an identity manually or deregister it. While it is manually suspended, and after it is deregistered, every message from it SHALL fail at step 2 of AW-06's precedence with reason `unauthorized`, and SHALL store no clinical content, except its `message.ack` of a notice openChart sent it. Only the medical director SHALL lift a manual suspension. A deregistered identity is never re-enabled; only a new registration under AW-02 restores a path.

**Cap suspension.** openChart SHALL count, per source system and practice, the consults quarantined under AC-11 in any rolling 24 hours, leaving out every consult whose emergency indicator is set or whose `review_flags` carry `red_flag`. The practice's policy sets the cap, which SHALL NOT exceed a built-in ceiling of 20; with no policy set, the ceiling applies. When a source reaches its cap, openChart SHALL quarantine that consult and cap-suspend the source at once. A cap suspension stops only non-urgent consults. A `consult.write` from a cap-suspended source without the emergency indicator or `red_flag`, and every `act.write` from it, SHALL fail at step 2 with `unauthorized` and store no clinical content. A consult with the emergency indicator or `red_flag` SHALL be exempt: after it passes steps 1 and 3 to 6, openChart SHALL keep it as quarantined AI communication and list it urgently under AC-11, even when its grant checks pass. A cap-suspended source's grant readback and its `message.ack` are still answered. Its receipt is `quarantined`, with the AI check's code as its `quarantine_cause` when its AI is not identified, the step-8 code when a grant check fails, and otherwise `source_cap_suspended`, so the source learns at once that it was kept and not accepted (design call AD-40). The medical director MAY lift a cap suspension. While no AU-01 designation is in force, a holder of the administrative role that the foundation's AU-01 names MAY lift a cap suspension too, but never a manual one. Lifting a cap suspension grants nothing: consults still meet the grant checks, and are quarantined when they fail them.

**Alerts and records.** A cap suspension SHALL alert the medical director with identifiers and a coded cause only, or, where none is designated, the administrative role that the foundation's AU-01 names with an opaque reference and a coded cause only, as AC-11 provides for that role. Every suspension, lift and deregistration SHALL be recorded with actor, reason and time, and listed for the medical director and the administrative role, naming the source and never a patient. A refused write that declared the emergency indicator or `red_flag` is listed urgently without content only where AW-06 allows it.

**Notices to the source.** openChart SHALL tell the source of every change to its standing with an `authority.notice` from openChart (design call AD-41), using these `change` values: `suspended` for a manual suspension; `cap_suspended` for a cap suspension; `deregistered` for a deregistration, sent as the last notice, after which openChart serves the identity only to deliver that notice and receive its acknowledgment; `suspension_lifted` when either kind of suspension is lifted; and `no_medical_director` when no AU-01 designation is in force, so no grant is current (AG-02). Each carries the grant identifier and configuration version where a grant exists. The notice clock of AW-08 applies. When openChart receives from a source any message other than a `message.ack` after it has sent that source a `suspended` or `deregistered` notice, or a consult without the emergency indicator or `red_flag` after it has sent a `cap_suspended` notice, whoever has acknowledged the notice or its alert, openChart SHALL raise one alert, to the medical director and to the administrative role that the foundation's AU-01 names, carrying an opaque reference to the source and a coded cause, and never a patient or content. It SHALL raise no further such alert for that suspension or deregistration (design call AD-46).

**Urgent-listing ceiling and alarm.** Per source and practice, openChart SHALL list urgent refusals, urgent quarantined consults and urgent recommendations one by one up to a ceiling in any rolling 60 minutes, which the practice's policy sets at no more than 10 (design call AD-43). Further urgent listings from that source in the interval SHALL be collapsed into a digest, sent at once with the first listing over the ceiling, and then once every 60 minutes while further listings arrive (design call AD-46). The digest goes to the medical director, by identifiers only. Where no AU-01 designation is in force, it SHALL instead be sent per patient, without content, to AC-11's fallback recipients for that patient's chart, every clinician authorized for it; the administrative role that the foundation's AU-01 names SHALL receive an alert with opaque references and coded causes only, and a listing whose patient resolves through no existing link reaches that alert only. An urgent listing of a refusal from a manually suspended or cap-suspended source, listed alone or in a digest, SHALL be acknowledged by a clinician who received it within 1 hour, the window AC-11 sets for urgent quarantined consults; otherwise it SHALL escalate as AC-11 provides, re-alerting until a clinician acknowledges it. openChart SHALL also count, per source, the consults quarantined with the emergency indicator or `red_flag`. When they reach the practice's alarm threshold, at most 10 in any rolling 24 hours, openChart SHALL alert the medical director, or, where none is designated, the administrative role, to consider a manual suspension. It SHALL NOT suspend the source itself, because an automatic suspension would stop urgent consults reaching the chart.

**Residual.** A patient who really was given emergency guidance by a deregistered or unregistered source is not listed for any clinician. openChart cannot trust anything such a caller sends, and listing it would let that caller raise urgent listings without limit. That source must hand the patient to a clinician itself (design call AD-43).

#### Scenario: Failure: the administrative role suspends an unsafe source
- **WHEN** a holder of the administrative role that the foundation's AU-01 names suspends an AI system's integration identity manually
- **THEN** every later write from it is refused with reason `unauthorized` and stores no clinical content, and the suspension is listed for the medical director

#### Scenario: Failure: an emergency consult arrives from a manually suspended source
- **WHEN** a manually suspended source sends a consult with the emergency indicator set, for a patient it is linked to
- **THEN** openChart refuses it with reason `unauthorized` and stores no clinical content; the refusal record keeps the emergency indicator, and the refusal is listed urgently, without content, for the patient's responsible clinician and the medical director, or AC-11's fallback recipients, so that a clinician knows to contact the patient

#### Scenario: Failure: someone other than the medical director lifts a manual suspension
- **WHEN** a holder of the administrative role tries to lift a manual suspension, whether or not a medical director is designated
- **THEN** the action is refused, and the identity stays suspended until the medical director lifts it

#### Scenario: Failure: a source is suspended and told
- **WHEN** the medical director suspends a source manually
- **THEN** openChart sends it an `authority.notice` with `change` `suspended`, accepts its `message.ack`, and refuses every other message from it with `unauthorized`

#### Scenario: Failure: a source is deregistered
- **WHEN** the administrative role deregisters a source
- **THEN** openChart sends a last `authority.notice` with `change` `deregistered`, accepts only its acknowledgment, and refuses everything else from that identity

#### Scenario: Failure: a deregistered source sends emergency-flagged writes
- **WHEN** a deregistered identity sends a consult with `emergency_indicated` true for a linked patient
- **THEN** openChart refuses it with `unauthorized` and stores no clinical content; the refusal record keeps the flag, and nothing is listed for the patient's clinicians

#### Scenario: Failure: a source floods urgent listings
- **WHEN** a source's eleventh urgent listing in 60 minutes arrives, with no lower ceiling set
- **THEN** a digest carrying it goes to the medical director at once, and later urgent listings from that source go into the next digest, sent 60 minutes later, not listed one by one

#### Scenario: Failure: a source floods urgent listings while no medical director is designated
- **WHEN** a source's eleventh urgent listing in 60 minutes arrives while no AU-01 designation is in force
- **THEN** the digest is sent at once, per patient and without content, to every clinician authorized for that patient's chart, and the administrative role receives an alert with opaque references and coded causes only

#### Scenario: Failure: a source keeps writing after its suspension notice was sent
- **WHEN** openChart has sent a source a `suspended` notice, which the source has not acknowledged and the medical director has, and the source then sends three consults
- **THEN** each is refused with `unauthorized` and stores no clinical content, and openChart raises one content-free alert for the medical director and the administrative role, not three

#### Scenario: Failure: nobody acknowledges an urgent refusal from a suspended source
- **WHEN** an emergency consult from a manually suspended source is refused and listed urgently, and no clinician acknowledges the listing within 1 hour
- **THEN** it escalates as AC-11 provides, to the medical director or, where none is designated, to every clinician authorized for the chart and the administrative role, re-alerting until a clinician acknowledges it

#### Scenario: Failure: flagged quarantines reach the alarm threshold
- **WHEN** a source's tenth consult in 24 hours is quarantined with the emergency indicator or `red_flag`, with no lower threshold set
- **THEN** openChart alerts the medical director to consider a manual suspension, and does not suspend the source itself

#### Scenario: Failure: an emergency consult for the wrong patient arrives from a cap-suspended source
- **WHEN** a cap-suspended source sends an emergency consult that is refused at step 6 with `patient_link_mismatch`
- **THEN** openChart stores no clinical content and does not quarantine it, because the exemption applies only after steps 1 and 3 to 6 pass

#### Scenario: Failure: a deregistered identity writes
- **WHEN** a write arrives from a deregistered integration identity
- **THEN** openChart refuses it with reason `unauthorized`, stores no clinical content, and offers no way to re-enable that identity

#### Scenario: Failure: a source reaches its quarantine cap
- **WHEN** a source's twentieth non-urgent consult in 24 hours is quarantined, with no lower cap set
- **THEN** openChart quarantines it, cap-suspends the source at once and alerts the medical director, and the source's next non-urgent consult is refused with reason `unauthorized`

#### Scenario: Failure: a red-flag consult arrives from a cap-suspended source
- **WHEN** a cap-suspended source sends a consult whose `review_flags` carry `red_flag`
- **THEN** openChart keeps it as quarantined AI communication, lists it urgently under AC-11, does not count it toward the cap, and answers `quarantined` with the step-8 code, or with `source_cap_suspended` when every grant check passes

#### Scenario: Failure: the cap is reached while no medical director is designated
- **WHEN** a source is cap-suspended while no AU-01 designation is in force, and a holder of the administrative role lifts the cap suspension
- **THEN** the lift is recorded and listed, the alert names no patient, and the source's next consult still meets the grant checks and is quarantined when it fails them

### Requirement: AW-14 A source can read back its own authority as a heartbeat, with no content
openChart SHALL answer every `grant.readback_request` with exactly one `grant.readback`, from its own records at read time (design call AD-42). Neither message carries patient or clinical content. openChart SHALL answer `unauthorized`, with no other field, to any identity other than the source's registered identity or its relay, and to a manually suspended or deregistered identity. Otherwise it SHALL compute the answer at read time from every grant check of AG-02 and AG-06 that does not depend on what a write contains (design call AD-44): whether an AU-01 designation is in force; whether a grant version is in force for the present time; whether it is paused; whether it, or the legal review it relies on, has expired; and whether it is revoked. **The readback says `grant_current` only if a well-formed `consult.write` within the grant's mode and scope, naming the grant version in force and the configuration version it records, would pass the grant checks now.** It then carries that grant's identifier, version, mode, configuration version, state `active`, effective time and expiry. Otherwise openChart SHALL answer `grant_not_current` with the reason of the first check that fails, in this order: `no_medical_director` where no AU-01 designation is in force (a write gets `no_current_grant`, AG-02); `no_grant` where no grant version is in force, with no grant attached; `grant_paused`; `grant_expired` where the grant or the legal review it relies on has expired, the grant then being in state `expired` (AG-09); and `grant_revoked`. Apart from `no_medical_director`, a write that fails these checks carries the same code, as a consult's `quarantine_cause` or an act's `path_reason`, and is never refused for it; `design.md` §13 maps each check to its write outcome, readback answer and notice. Every reason other than `no_grant` carries the grant, with its state, where one exists. Both answers carry `source_status`: `active` or `cap_suspended`. `cap_suspended` means that a consult without the emergency indicator or `red_flag` fails at step 2 whatever the grant (AW-13), so `grant_current` with `cap_suspended` allows no non-urgent consult. A narrowing or a superseding version shows as the grant version now in force. A grant readback changes nothing. The source can call it at any time, under request limits decided in planning, and bound its own authority to the narrower of its configuration and the answer.

**What openChart never sends.** openChart SHALL never send a message that contradicts itself, and the schema refuses each of these (design call AD-45):
- a `grant.readback` with `not_current_reason` `no_grant` that carries a `grant`;
- a `grant.readback` whose reason disagrees with the state of the grant it carries: `grant_paused` with a state other than `paused`, `grant_expired` with a state other than `expired`, or `grant_revoked` with a state other than `revoked`;
- an `authority.notice` with a standing `change` (`suspended`, `cap_suspended`, `deregistered`, `suspension_lifted` or `no_medical_director`) that carries `new_mode` or `removed_allowlist_entry_ids`.

**What openChart always sends.** On every grant-change notice it sends (`paused`, `narrowed`, `resumed`, `expired`, `revoked` or `superseded`), openChart SHALL include `grant_version`: the version in force once the change applies, which for `narrowed` and `superseded` is the new version (AG-01; design call AD-47). The schema requires `grant_id`, `configuration_version` and `grant_version` on every grant-change notice from openChart. Of the grant-change notices, only `narrowed` carries scope: it names the allowlist entries it removes in `removed_allowlist_entry_ids` and a lowered mode in `new_mode`; the other five carry none, and a superseding version's scope is the configuration version it records. A narrowing of a co-review window or of the reserved acts has no field in 1.0; openChart enforces it, and it concerns only the practice modes, which are off.

`contracts/examples/` holds an invalid example that breaks each of these rules, and openChart's contract tests SHALL show that the schema refuses each one and that openChart never emits one (design calls AD-45 and AD-47).

**The reader's rules.** A source that acts on these messages SHALL apply these rules (design call AD-45). They stay although the schema now refuses every self-contradictory message, because a receiver on an earlier draft digest, or one that does not validate, may still meet one, and because rules 2 to 4 order messages that are each valid:
1. A `grant.readback` or an `authority.notice` that contradicts itself, as the list above describes, is treated as not current.
2. A `grant.readback` whose `read_at` is earlier than the `effective_at` of a notice the source has received never overrides that notice.
3. A notice never widens authority by itself. The source widens its authority, by resuming or by adopting a wider grant version, only on a `grant_current` readback whose `read_at` is not earlier than the `effective_at` of every notice the source has received.
4. A notice whose `effective_at` is earlier than that of a notice the source has already applied never overrides it.

A relay passes these messages unchanged and applies none of these rules.

The 1.0 contract supports no interim version of an open consult: `ended_at` is required, and a new consult version continues or corrects an ended consult (AC-01).

#### Scenario: A heartbeat in normal operation
- **WHEN** an active source with a current grant sends a `grant.readback_request`
- **THEN** openChart answers `grant_current`, with the grant version in force and `source_status` `active`, and no patient or clinical content

#### Scenario: Failure: a manually suspended source sends a heartbeat
- **WHEN** a manually suspended source sends a `grant.readback_request`
- **THEN** openChart answers `unauthorized` with no other field

#### Scenario: Failure: the grant is paused
- **WHEN** the medical director has paused the grant, and the source sends a heartbeat
- **THEN** openChart answers `grant_not_current` with reason `grant_paused` and the paused grant

#### Scenario: Failure: no medical director is designated
- **WHEN** no AU-01 designation is in force, and the source sends a heartbeat
- **THEN** openChart answers `grant_not_current` with reason `no_medical_director`

#### Scenario: Failure: a cap-suspended source sends a heartbeat
- **WHEN** a cap-suspended source sends a heartbeat
- **THEN** openChart answers it, with `source_status` `cap_suspended`

#### Scenario: Failure: the legal review behind an active grant has lapsed
- **WHEN** the legal review that the grant relies on has passed its expiry, and the source sends a heartbeat
- **THEN** openChart answers `grant_not_current` with reason `grant_expired` and the grant in state `expired`, the reason a write then gets, and never `grant_current`

#### Scenario: Failure: the grant's expiry passes between heartbeats
- **WHEN** the grant's expiry passed a minute ago, and the source sends a heartbeat
- **THEN** openChart answers `grant_not_current` with `grant_expired`, computed at read time

#### Scenario: Failure: a readback computed before a suspension arrives after its notice
- **WHEN** a source receives a `suspended` notice effective at 10:00, and then a `grant_current` readback whose `read_at` is 09:59
- **THEN** under the reader's rules the readback does not override the notice, and the source stays stopped

#### Scenario: Failure: a retried `resumed` notice arrives after a later pause
- **WHEN** the grant is paused at 10:00, resumed at 10:10 and paused again at 10:20, and the source receives the `paused` notices of 10:00 and 10:20 before the retried `resumed` notice of 10:10
- **THEN** under rule 4 the late `resumed` notice does not override the applied pause of 10:20, under rule 3 it widens nothing by itself, and the source stays paused, as the chart's grant is

#### Scenario: Failure: a standing notice claims a mode
- **WHEN** a source receives a `suspension_lifted` notice that carries `new_mode` `full_practice`
- **THEN** the schema refuses it, openChart never sends such a notice, and under the reader's rules the source treats it as not current and widens nothing

### Requirement: AW-15 Every record kept from a write states when it was received, when it arose, where it came from, who wrote it and on whose behalf, and is permanent
Every record that openChart keeps from a write, whether an accepted consult record, a quarantined consult or a recommendation, SHALL record (ruling 80, clauses 4 to 8; design call AD-50):
- `received_at`: openChart's own clock when it received the write, which openChart also returns in the receipt and the readback;
- `occurred_at`: when the information arose. For an `act.write` it is the write's `occurred_at`. For a consult it is the consult's `ended_at`, and the record also keeps `started_at`;
- `source`: where the information came from, as a `kind` (`patient_statement`, `device_reading`, `ai_consult`, `clinician_observation`, `external_record` or `chart_entry`) and the source system's reference to it. A `consult.write` always carries `ai_consult`;
- `added_by` and `on_behalf_of`, as AW-02 states, with the identity basis of each;
- the identification of the AI: its `openwallet_id`, `model` and `model_version`.

These fields SHALL be part of the permanent record and SHALL be shown with it to everyone who can read it (AW-09). Nothing in a record kept from a write SHALL be edited or deleted. A correction SHALL be a new dated addition that points to what it corrects: a new consult version that references its predecessor (AC-01), a new act version, or a clinician's own record (ruling 80, clause 8). The general rule for every addition to the chart is the foundation's AN-04 and AN-05 (at head `f85e742`); this requirement applies it to the records this change keeps. On the foundation's recommendation record (AW-16), the writer is `added_by`, a party of kind `system` whose `system_id` is openChart's reference to the writer's registration, with its `operator_ref`; the registration holds the writer's issuer and namespace (the foundation's AN-03; design call AD-58). For a relay, the source system is the second party in `on_behalf_of`, by openChart's reference to the source that the relay's registration names, with its `operator_ref`, `asserted_by` the relay. This path names no party by `external_ref` and records none as `not_identified`: its writer is verified by the chart, its AI is identified by an openWallet ID the registration covers or the write is held, and its source system is the one the writer's registration covers (the foundation's AN-02). A new version of an AI act is a new recommendation that points to the one it corrects (`corrects`). A held write keeps the `received_at` of its first arrival, and so does the addition it becomes if it is released into the chart (AC-11; the foundation's AN-01).

#### Scenario: A relayed consult records its provenance
- **WHEN** a relay delivers a consult that an AI held with a patient from 09:00 to 09:01, and openChart receives it at 09:02
- **THEN** the record holds `received_at` 09:02, `occurred_at` 09:01 with `started_at` 09:00, `source` `ai_consult` with its reference, the relay as `added_by`, and the AI by its openWallet ID, model and model version, then the source system, in `on_behalf_of`, and every clinician who can read the chart sees them

#### Scenario: Failure: someone tries to change a record's provenance
- **WHEN** a user or a system tries to change the `received_at`, `source` or `on_behalf_of` of a record kept from a write
- **THEN** the change is refused, and a correction can only be a new dated addition that points to the record

#### Scenario: Failure: a write omits where its information came from
- **WHEN** an `act.write` arrives with no `source`
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

### Requirement: AW-16 An AI act attempted without authority is recorded in full as a recommendation that has no effect, and a clinician may adopt or decline it
An `act.write` that passes steps 1 to 6 of AW-06 and its AI check, and fails a check at step 7, 8 or 9, SHALL NOT be refused (ruling 80, clause 18; the foundation's AN-12). openChart SHALL record it in full as the clinical-acts foundation's recommendation record: `record_kind` `recommendation` of `openchart-clinical-act-content/1.0` at SHA-256 `d1c250e737158162cddffdcc6db9716a9e5f0e50fd104c1c47f019912fbfa81d`, as `define-clinical-acts-foundation` (openChart-spec#5) defines it at head `f85e742` in its AN-09 and AN-14 (ruling 80, clause 13; design calls AD-51 and AD-58). The recommendation SHALL hold:
- **the proposed act:** action `sign` for new content, or `new_version` for a write that names a target record (below); the write's `act_class` and `act_type`, kept as declared whether or not the chart defines them; and its `act_content.content` exactly as given, with `content_schema` naming the schema the write declared it under, by the identifier, version and SHA-256 of `act_content.content_schema`. The foundation checks such content only for being well formed, nothing reads it as an act's content, and the act-validity rules apply only when a clinician adopts it (its AN-09, and its design calls CD-51 and CD-56). No write on this path is a clinical note, so none becomes the foundation's information record (AC-04);
- **the decision maker:** the AI, by its `openwallet_id`, `model` and `model_version` (the foundation's AN-02);
- **identification and provenance:** `added_by`, the writer, `verified_by_chart`; `on_behalf_of`, the AI and, for a relay, the source system, each `asserted_by` the writer; `received_at`, `occurred_at` and `source`; and `submission_ref`, naming the write's `act_id` and `act_version` (its encoding is decided in planning), with `submission_ref_conflict` where AW-05 flags one (AW-02, AW-15; the foundation's AN-04 and AN-10);
- **the codes:** the marker `not_authorized_decision`, the foundation's `missing_authority` codes and this contract's `path_reason`, mapped as AW-06 states.

What the write carried that the recommendation record has no field for SHALL be kept, unedited, in this change's own record of the write, linked to the recommendation by its identifier and shown with it: the `act_id` and `act_version`, the models, the evidence references, the conditions met, the knowledge basis, the linked consult, the authority the write claimed, a declared reservation and the emergency indicator (design call AD-58). When the write supersedes an earlier AI act of its source system (`supersedes_act`), the new recommendation points to the earlier one as the one it corrects (`corrects`), because no AI act is an act of record (the foundation's AN-05). When the write names a target record (`target_record_ref`), the proposed action is `new_version`: the write's reference is kept as given in `target_as_given`, the act version it names is `target` where openChart resolves it to an act version of this patient's chart, and the content is kept as given (the foundation's AN-09, which answers tension AT-18). The 1.0 contract carries no action code, so a write with a target is always proposed as new content for that record, never as a bare discontinuation, entered-in-error mark or cancellation, and an AI's action on a clinician-authored record is `targets_clinician_record`, which maps to `no_decision_authority` (AA-10). This path names the AI as the decision maker, its identity asserted by the writer, and never records a claimed decision maker or `decision_maker_not_confirmed`, because the writer's registration covers the AI's openWallet ID (the foundation's AN-08, with its design calls CD-61 and CD-67; design call AD-58). A write whose AI the registration does not cover is held, and no recommendation is recorded while it is held (AW-06, AC-11).

A recommendation SHALL have no effect (ruling 80, clause 14). It is not an act of record: it has no act status, enters no co-review queue, cannot be signed, released, transmitted or published, is never a billable fact, and never satisfies a check or removes a warning that a decision would. Nothing is ordered, prescribed, sent, billed or treated as established because of it. A recommendation is not gated: the prescribing-safety gate applies to a clinician's own prescription when they adopt one (the foundation's AN-09 and RX-02). Wherever it is shown, to a clinician or to the patient, it SHALL be marked "not an authorized decision" and SHALL say which authority was missing (clause 13; AW-09).

openChart SHALL tell the writer at once, with a `write.receipt` whose result is `recorded_as_recommendation`, carrying the `record_ref`, which is the recommendation's identifier, and both code sets (clause 15; the foundation's AN-10). This write path's listing is the review path that the foundation's AN-11 uses for it. openChart SHALL list the recommendation, with its content, in an authenticated openChart session, for the patient's responsible clinician when that clinician holds `sign` scope for its act class, and otherwise for the medical director; a notification carries no content (AW-07). It SHALL list it urgently, for the responsible clinician and the medical director, when its emergency indicator is set (AA-06). These listings fall under AW-13's per-source ceiling and digest (design call AD-46). A listing SHALL stay open until a named clinician adopts or declines the recommendation. Its due time and escalation SHALL work as the foundation's co-signature requirement's do (its CA-07), and no timer, default or agent SHALL close it (its AN-11).

A clinician who holds the authority MAY adopt it. Adoption makes a decision of the clinician's own through the foundation's normal path, and its record names the recommendation in `adopted_from` (ruling 80, clause 16; the foundation's AN-11). For new content, it is a draft of the clinician's own that the clinician may change, then signs off. For a proposed `new_version` of an act, it is a new version that the clinician writes and signs off. The sign-off is the foundation's CA-04 (ruling 151; its AN-07). It is made in the clinician's own logged-in session, re-authenticated, with a single-use challenge (`challenge_ref`). It is over the sign-off statement, which names the action (`sign` for new content or a new version), the act and its version, the patient, the signer, the attestation code, and the content and provenance digests. The openSig attestation is over that statement's SHA-256, which openChart records as `statement_sha256`, from a wallet bound to the clinician's account in their own session (its AU-07). A prescription adopted this way meets the prescribing-safety gate at its own sign-off (the foundation's RX-02). An adoption that does not complete is recorded on the recommendation, with the clinician, the time and the reasons, and the recommendation stays open (its AN-11). The clinician MAY instead decline it, with the clinician, the time and a coded reason recorded. Either way the recommendation stays in the chart as written.

An AI's recommendation never becomes a decision through anything the AI system or its relay sends: not a repeat, a new version, a later grant, a notice, or a claim inside its content (ruling 151; AW-05). A write that claims to be made on a clinician's behalf counts as that clinician's decision only when it carries that clinician's own sign-off, made as ruling 151 states (the foundation's AN-08). Whether a sign-off made in another system could ever count is the foundation's Open Question 17, with the owner. The 1.0 contract carries no such sign-off and admits no human in `on_behalf_of`, so whatever an `act.write` says about a clinician is recorded as the AI's recommendation (ruling 80, clause 12; ruling 151). Wherever a choice could let a recommendation take effect as a decision, openChart SHALL fail closed and treat it as a recommendation.

The write path SHALL NOT be enabled for any practice until the foundation's recommendation record is built, with its feature (1), because an `act.write` could then arrive that this requirement says must be recorded and must not be refused (design call AD-55).

#### Scenario: An advice-only AI sends an act
- **WHEN** an identified AI system under an `advice_only` grant sends a schema-valid `act.write` for a linked patient, on a deployment where Tier 2 is not in force
- **THEN** openChart records the act in full as a recommendation marked `not_authorized_decision`, naming the AI as its decision maker, with `missing_authority` `no_decision_authority` and `no_practitioner_sign_off` and `path_reason` `tier2_not_in_force`, answers `recorded_as_recommendation` with the `record_ref` and both code sets, lists it with its content for the responsible clinician, and creates no order, prescription or diagnosis

#### Scenario: An act class the foundation does not define is kept as given
- **WHEN** an identified AI system sends a schema-valid `act.write` of act class `treatment_plan_change`, which the foundation does not define, with its content declared under its own content schema
- **THEN** openChart records a recommendation whose proposed act keeps the act class as declared and the content exactly as given, with `content_schema` naming the declared schema, and validates the content against no schema of its own

#### Scenario: Failure: a recommended prescription would count in a safety check
- **WHEN** a prescription recorded as a recommendation is on a patient's chart, and a safety check, a medication list or a read of billable facts runs
- **THEN** the recommendation is never counted as an active prescription, never removes a warning, never satisfies a check and is never a billable fact

#### Scenario: A clinician adopts a recommendation
- **WHEN** a clinician who holds `sign` scope for its act class adopts a recommendation, changes the draft, re-authenticates and signs it off with their openWallet and openSig over the sign-off statement and its single-use challenge, and every check of the foundation's CA-04 passes
- **THEN** a new decision of the clinician's own takes effect with `adopted_from` naming the recommendation, its sign-off records the action `sign`, the challenge and `statement_sha256`, and the recommendation stays in the chart as written

#### Scenario: An AI act on an existing record keeps its target as given
- **WHEN** an identified AI system sends a schema-valid `act.write` whose `target_record_ref` openChart cannot resolve to an act version of the patient's chart
- **THEN** openChart records a recommendation whose proposed action is `new_version`, with the reference in `target_as_given`, no `target`, and the content as given, and the reviewer sees the reference as given

#### Scenario: A clinician declines a recommendation
- **WHEN** a clinician declines a recommendation
- **THEN** the decline is recorded with the clinician, the time and a coded reason, and the recommendation stays in the chart as written, with no effect

#### Scenario: Failure: nobody adopts or declines a recommendation in time
- **WHEN** a recommendation's listing passes its due time with no adoption or decline
- **THEN** openChart escalates it to the medical director and keeps it open

#### Scenario: Failure: an act claims that a clinician approved it
- **WHEN** an `act.write` carries, in its content or its evidence, a statement that a named clinician approved it
- **THEN** openChart records it as the AI's recommendation, because it carries no sign-off of that clinician's own made as ruling 151 states

#### Scenario: Failure: the write path would be enabled before the recommendation record exists
- **WHEN** a plan proposes enabling the write path for a practice before the foundation's recommendation record is built
- **THEN** the plan is out of scope, because an `act.write` could then be neither recorded, as this requirement demands, nor refused
