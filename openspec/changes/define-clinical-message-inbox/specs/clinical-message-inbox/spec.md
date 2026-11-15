## ADDED Requirements

### Requirement: MI-01 openChart receives routed clinical items in a clinical message inbox
openChart SHALL provide a clinical message inbox that receives the clinical items openPractice routes under contract `openpractice-clinical-handoff/1.0`. That contract is owned by `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation` (on `opensoft/openPractice-spec` `main` at `0a82fc2`, still draft and unratified; ER-04 and ER-05 there). openChart is the doctor's clinical interface (ruling 34): the clinician reads and answers routed clinical questions in openChart. HealthLinc is the patient's gateway to their doctor: the patient may connect to their human doctor, through openPractice to openChart, or to medXfactory's medical AI (ruling 51). This inbox is the human-doctor path.

openChart SHALL accept handoff messages only from an authenticated openPractice integration identity. That identity SHALL hold a dedicated openChart integration role that is narrower than `System Manager`, is named in planning, and is authorized for subject, tenant, purpose and role, as the ratified API requirement demands. openChart SHALL use only the messages the pinned contract defines: `handoff.offer`, `handoff.ack`, `handoff.urgency_raised`, `handoff.clinician_urgency_raised`, `handoff.status`, `clinical_need.marker` and `message.ack`. It SHALL define no message of its own toward openPractice. Toward the systems that hold patient conversations, openChart uses only the conversation-retrieval contract it owns, `openchart-conversation-retrieval/1.0` (ruling 69; MI-02, MI-03).

Every requirement in this capability SHALL apply in the same way on every client through which a clinician uses openChart, whether mobile or workstation (ruling 35, a current-phase decision). No requirement depends on a device.

#### Scenario: A clinician works from a phone
- **WHEN** a clinician opens a routed item on a mobile client
- **THEN** the same ownership, clock, reply and authorship rules apply as on a workstation

#### Scenario: Failure: an unauthorized caller sends an offer
- **WHEN** a caller without the integration role sends a `handoff.offer`
- **THEN** openChart answers `handoff.ack` `rejected` with reason `unauthorized` and creates no item

### Requirement: MI-02 Handoff and conversation-retrieval messages are validated against canonical schemas, pinned by path and digest
openChart SHALL validate every message it receives or sends under its two inbox contracts against that contract's canonical schema:
- **`openpractice-clinical-handoff/1.0`**, owned by change `define-patient-gateway-and-escalation` in `opensoft/openPractice-spec`: `openspec/changes/define-patient-gateway-and-escalation/contracts/openpractice-clinical-handoff-1.0.schema.json`, at revision `0a82fc2` (`main`, still draft and unratified), SHA-256 `19dff20f95cd31afdef02270119a123a7c4662a4fcc5b20ef09d5b9cd5d91e2d`;
- **`openchart-conversation-retrieval/1.0`**, owned by this change (ruling 69): `openspec/changes/define-clinical-message-inbox/contracts/openchart-conversation-retrieval-1.0.schema.json` in `opensoft/openChart-spec`, SHA-256 `6b2157b33e9f0b2f28e28be1b99e2faad27e35545f109324bc6b42604dc51782`, as listed in this change's `contracts/SHA256SUMS`. HealthLinc and medXfactory implement it (MI-03).

Each digest identifies its schema even after archival moves the file. openChart SHALL NOT implement against a handoff schema whose digest differs from the digest recorded here, until both changes record the same new digest. When that change's schema changes, this pin SHALL be updated in a governed revision of this change. The retrieval schema SHALL change only in a governed revision of this change that records its new digest, and a system that implements it SHALL record the same digest before it interoperates with openChart.

The pinned schema names the conversation's holder in `conversation_source` (`healthlinc` or `medxfactory`), with a matching `conversation_ref` (ruling 51). `healthlinc` names any conversation HealthLinc holds: a coach conversation, a direct message to the doctor or an administrative thread. It defines `clinical_need.marker` (ER-18 in the openPractice change), which MI-25 sends.

It also carries:
- the offer field `identity_state`, one of `linked`, `link_in_review` or `unlinked`;
- for an `unlinked` offer, `unlinked_identity`, which holds exactly `legal_name`, `birth_date` and `administrative_sex` from the `openpractice-ehr-patient-link/1.0` snapshot, and no `link_id` or `ehr_patient`;
- the message `handoff.clinician_urgency_raised`;
- the `handoff.urgency_raised` sources `coach_triage`, `medical_ai_triage` and `patient_checklist`, alongside `staff`, `agent_proposal` and `routing_rule`. `patient_checklist` is a patient's raise through HealthLinc's red-flag checklist (ruling 71). openChart SHALL accept it wherever it lists urgency sources, and records it as the patient's (MI-12).

In that schema, `link_id` is optional on `handoff.ack`, `handoff.urgency_raised`, `handoff.status` and `handoff.clinician_urgency_raised`, and `message.ack` names a `handoff_id`, a `link_id` or both.

Under either contract, openChart SHALL accept a `1.x` message at a MINOR version it has declared. It SHALL refuse a message whose MAJOR version it does not support with reason `unsupported_major_version`, and a message that fails the schema with reason `schema_invalid`. A refusal SHALL change nothing (the PL-12 pattern; PG-01 and ER-04 in the openPractice change). Each contract keeps its own codes: the handoff schema's reject reasons, and the retrieval schema's single set of error codes (design call MD-22).

#### Scenario: Failure: an offer fails the schema
- **WHEN** an offer carries a property the schema does not define
- **THEN** openChart answers `rejected` with reason `schema_invalid` and creates no item

#### Scenario: Failure: an unsupported major version arrives
- **WHEN** a `2.0` `handoff.offer` arrives
- **THEN** openChart answers `rejected` with reason `unsupported_major_version` and creates no item

#### Scenario: Failure: the canonical schema changes before both changes record it
- **WHEN** the openPractice change publishes a schema with a new digest that this change has not recorded
- **THEN** openChart keeps validating against the recorded digest and does not implement the new schema

#### Scenario: Failure: a retrieval result fails the schema
- **WHEN** a holder's `conversation.result` carries a property the retrieval schema does not define
- **THEN** openChart answers `message.ack` `rejected` with `schema_invalid`, stores none of it, and treats the retrieval as failed under MI-03

### Requirement: MI-03 openChart obtains the escalated conversation by reference from the system that holds it, never from openPractice
The handoff is reference-only (ER-05 in the openPractice change). openChart SHALL obtain the escalated conversation from the system that `conversation_source` names (ruling 51), over openChart's own authorized integration with that system (ruling 39), under the contract openChart owns, `openchart-conversation-retrieval/1.0` (ruling 69; design Decision 14):
- **`healthlinc`:** from HealthLinc, for any conversation it holds: with its coach, a direct message to the doctor, or an administrative thread;
- **`medxfactory`:** from medXfactory, for a conversation with medXfactory's medical AI.

openChart SHALL send `conversation.retrieve`, naming the item's `handoff_id`, the offer's `conversation_ref`, the offer's `healthlinc_message_ref` as `request_ref`, and the item's current `urgency`. When the item's urgency rises to `priority` or `urgent` after a retrieval, openChart SHALL retrieve again with the new urgency. The holder answers with `conversation.result`, or refuses with `message.ack` `rejected` and a code from the contract's error set. Every holder SHALL support retrieval. Reply delivery, the delivery-failure callback and split are optional capabilities that a holder declares in `capabilities.result`, in answer to openChart's `capabilities.request` or unprompted when they change. The latest declaration governs. openChart SHALL NOT send a message for a capability the holder has not declared (design call MD-22).

Each returned turn carries its `turn_id`, author type and source token, which openChart records per turn under MI-12. The result carries the patient's sharing-consent reference, `consent_ref`, and the urgency the holder applied, which openChart records. Every result SHALL carry at least one request turn: a turn marked `request_turn`, written by the patient or a representative, carrying the retrieve's `request_ref`, whose text has at least one character that is not whitespace. A request turn SHALL hold the request itself, as the patient or representative wrote it, and never a placeholder, summary or redaction marker in its place. Only a request turn carries `request_ref`. For a `priority` or `urgent` item, the request turns SHALL always be shared on the basis `urgent_escalation`, with the patient told (`patient_told_at`); the patient's choice of what else to share never removes them. The retrieval schema enforces each of these rules except two: that a request turn's `request_ref` matches the retrieve's, which openChart checks below, and that the turn holds the request itself, which no schema can check (design call MD-29). Beyond them, the contract allows a holder, without requiring it, to return only the turns the patient confirmed. When a result reports withheld turns, openChart SHALL show the owner that the view is partial, with the count, and SHALL NOT present it as the whole conversation (design call MD-25).

The offer's `healthlinc_message_ref` is HealthLinc's reference for the patient's request. openChart SHALL keep it in the record (MI-12), send it as the retrieve's `request_ref`, and use it for split requests (MI-16), but SHALL NOT use it in place of `conversation_ref`. For a conversation that medXfactory holds, the request turns must carry this HealthLinc reference too (tension MT-25). openChart MUST NOT request, accept or store message content from openPractice.

A result MAY name, in `origin_conversation_ref`, the earlier conversation this one began from, at the same holder or another. Its value is an opaque token that carries no PHI. openChart SHALL record and show that reference (MI-12), SHALL NOT retrieve the earlier conversation on its own, and SHALL NOT use the reference to resolve, link or file a patient, as for a holder's `ehr_patient` (design call MD-19). Reading it would be a separate retrieval from the holder the reference names, under that holder's consent rules, made only at a named clinician's explicit request. Version 1.0 defines no purpose for that retrieval, so openChart SHALL NOT read an origin conversation until a MINOR version adds one (design call MD-32).

A retrieval SHALL succeed only with a schema-valid `conversation.result` that answers it: the same `handoff_id` and `conversation_ref`, the urgency openChart sent, and at least one request turn whose `request_ref` equals the retrieve's, compared as an (issuer, namespace, value) triple. Every other outcome SHALL be a failed retrieval (design call MD-29):
- a refusal, `consent_not_granted` included, or no answer;
- a result that fails the schema, which openChart refuses with `schema_invalid`. That includes an empty result, a result with no request turn, a request turn without `request_ref` or whose text is empty or only whitespace, and a `priority` or `urgent` result whose request turns are not shared as `urgent_escalation` with `patient_told_at`;
- a schema-valid result that does not answer the retrieve, which openChart refuses with `result_mismatch`. That includes a result in which no request turn's `request_ref` matches, so a placeholder sent under another reference fails;
- a result whose request turn the owner records as not holding the patient's request, for example a placeholder. openChart SHALL let the owner record that, and SHALL then treat the retrieval as failed and retrieve again.

No schema or reference check can tell a placeholder, or a short text such as a greeting, from the patient's request when it carries the matching `request_ref`. Only the holder's conformance to this requirement, which its own contract tests check, and the owner's reading of the turn can catch it.

A result that withholds only turns other than the request turns is a successful but partial retrieval (design call MD-25). When retrieval fails, openChart SHALL keep the item open and owned, keep retrying, and show the owner that the content is unavailable. The same applies when openChart has no retrieval configured for the source system, for example a `medxfactory` conversation at a practice that has not configured medXfactory retrieval (design call MD-12). openChart SHALL report `content_unavailable` to openPractice (MI-06): at the first failed retrieval for an `urgent` or `priority` item, so that openPractice's fallback or tracked on-call alert runs at once, and when the retry policy is exhausted for a `routine` item (design call MD-15). An item SHALL NOT close because its content is unavailable.

#### Scenario: The conversation is retrieved
- **WHEN** openChart accepts an offer with `conversation_source` `healthlinc`, and HealthLinc answers `conversation.retrieve` for its `conversation_ref` with `conversation.result`
- **THEN** the owner sees each turn with its author type and source, and nothing is requested from openPractice

#### Scenario: A medical-AI conversation is retrieved
- **WHEN** openChart accepts an offer with `conversation_source` `medxfactory`, and medXfactory answers `conversation.retrieve` for its `conversation_ref` with `conversation.result`
- **THEN** the owner sees it labelled as medXfactory's medical AI, and the item records it by reference only (MI-24)

#### Scenario: Failure: the source system is unreachable for an urgent item
- **WHEN** openChart cannot retrieve the conversation for an accepted `urgent` item from the system that holds it
- **THEN** openChart reports `content_unavailable` at once, keeps the item open and owned, retries the retrieval, and shows the owner the urgency and the missing content

#### Scenario: Failure: openChart has no retrieval for the source system
- **WHEN** an accepted item's conversation is held by a system for which openChart has no configured retrieval
- **THEN** the item stays open and owned, openChart reports `content_unavailable`, and it does not ask openPractice for the content

#### Scenario: Failure: the holder withholds turns under the patient's consent
- **WHEN** a `conversation.result` for a `routine` item carries the request turn and reports three withheld turns
- **THEN** the retrieval succeeds as a partial one, and the owner sees the request turn and that the view is partial, with the count

#### Scenario: Failure: an empty result
- **WHEN** a holder answers `conversation.retrieve` with a `conversation.result` that holds no turns
- **THEN** openChart refuses it with `schema_invalid`, treats the retrieval as failed, keeps the item open and owned, and reports `content_unavailable` under this requirement

#### Scenario: Failure: a result lacks the request turn
- **WHEN** a `priority` item's `conversation.result` holds turns, but none is marked `request_turn`
- **THEN** openChart refuses it with `schema_invalid`, treats the retrieval as failed, and reports `content_unavailable` at once, so openPractice's tracked on-call alert runs

#### Scenario: Failure: an urgent item with withheld turns
- **WHEN** the patient's consent withholds turns from an `urgent` item's conversation
- **THEN** the result still carries the request turn on the basis `urgent_escalation` with `patient_told_at`, and the owner sees it with the count of withheld turns. A result without them fails the schema, is a failed retrieval, and is reported at once as `content_unavailable`, so openPractice's fallback runs

#### Scenario: Failure: a result answers a different retrieval
- **WHEN** a schema-valid `conversation.result` names another `conversation_ref`, or a lower urgency than openChart sent
- **THEN** openChart refuses it with `result_mismatch`, stores none of it, and treats the retrieval as failed

#### Scenario: Failure: a request turn holds only whitespace
- **WHEN** an `urgent` item's `conversation.result` carries a request turn whose text is a single space
- **THEN** openChart refuses it with `schema_invalid`, treats the retrieval as failed, and reports `content_unavailable` at once, so openPractice's fallback runs

#### Scenario: Failure: a placeholder under another request reference
- **WHEN** a schema-valid `conversation.result` carries a request turn with placeholder text whose `request_ref` does not match the retrieve's, and no other request turn matches
- **THEN** openChart refuses it with `result_mismatch`, stores none of it, and treats the retrieval as failed

#### Scenario: Failure: the owner finds a placeholder under the matching reference
- **WHEN** the owner of a `priority` item records that its request turn, which carries the matching `request_ref`, holds a placeholder rather than the patient's request
- **THEN** openChart treats the retrieval as failed, reports `content_unavailable` at once, keeps the item open and owned, and retrieves again

#### Scenario: A result names its origin conversation
- **WHEN** a medXfactory `conversation.result` carries an `origin_conversation_ref` that names a HealthLinc conversation
- **THEN** openChart records and shows the reference, and retrieves nothing from HealthLinc on its own

#### Scenario: Failure: an origin reference is used to find a patient
- **WHEN** someone tries to resolve or file an unfiled item's patient through its result's `origin_conversation_ref`
- **THEN** openChart refuses, and the item stays unfiled

#### Scenario: Failure: the holder refuses under the patient's consent
- **WHEN** a holder refuses `conversation.retrieve` with `consent_not_granted`
- **THEN** the item stays open and owned, the owner sees that the content is withheld, and openChart reports `content_unavailable` as for any failed retrieval

### Requirement: MI-04 Every offer is acknowledged, and handling is idempotent and replay-safe
openChart SHALL answer every schema-valid, authorized `handoff.offer` with exactly one `handoff.ack`. The two results mean:
- **`accepted`:** openChart has durably created the inbox item, assigned it a named owner (MI-07) and started its clock (MI-05). This is system acceptance, not a clinician reading the item (design call MD-1). openChart SHALL NOT answer `accepted` without a named owner; an offer that no one can own is held under MI-08 until one can.
- **`rejected`:** the acknowledgment carries a reason code from the schema.

The `message_id` of each inbound message is its idempotency key. A message whose `message_id` was already processed SHALL be answered with the original result and SHALL change nothing. openChart SHALL keep exactly one inbox item per `handoff_id`. A later offer for an existing `handoff_id` under a new `message_id` SHALL be answered with the original result and SHALL NOT alter the item. If that offer's content differs from the original, openChart SHALL also record an integration exception that holds only identifiers and a coded cause (design call MD-14). The `message_id` of every message openChart sends SHALL be a random UUID, reused on every retry. No key SHALL carry PHI (PL-13).

#### Scenario: Failure: an offer is retried
- **WHEN** the same offer arrives three times with the same `message_id`
- **THEN** openChart holds one item and answers with the same `handoff.ack` result each time

#### Scenario: Failure: a conflicting offer reuses a handoff id
- **WHEN** a second offer for an existing `handoff_id` names a different `link_id`
- **THEN** the item is unchanged, openChart answers with the original result, and it records an integration exception holding only identifiers and a coded cause

### Requirement: MI-05 openChart owns the queue and the response clock
openChart SHALL own the queue and the response clock for every routed clinical item (ruling 43). The acknowledgment window, the response window and the escalation interval SHALL come from an openChart response policy that the practice's medical director, a named human designated under AU-01 of `define-clinical-acts-foundation` (openChart-spec#5), approves. No agent SHALL approve it.

Until a policy version is approved, openChart SHALL use the offer's `ack_by` and `respond_by` (design call MD-2). The windows in the openPractice change (its design call DC-3, for example acknowledge `urgent` items within 5 minutes and respond within 60 minutes) are proposed defaults in an unratified change. They are not facts and not clinical standards, and this change adopts no window of its own.

Once a policy version is approved, each item's effective deadline SHALL be the earlier of the policy's deadline and the offer's. No event SHALL extend an item's effective deadline: not reassignment, cover, filing, an urgency raise or a policy change. Each item SHALL record the policy version, or `offered_times`, that set its deadlines. The windows are alerting thresholds, not clinical standards.

openPractice treats `clock_expired`, or silence past `respond_by`, as `clinical_response_overdue`. For an urgent item it runs its fallback, with a tracked alert to openPractice's on-call clinician (ER-07 and ER-09 in the openPractice change). An effective response deadline therefore SHALL never fall after the offer's `respond_by`, and SHALL end at once for an `urgent` or `priority` item that has no possible owner (MI-08). openChart SHALL report `clock_expired` the moment that deadline passes (MI-06).

#### Scenario: No policy is approved yet
- **WHEN** an offer arrives before any openChart response policy is approved
- **THEN** the item's deadlines are the offer's `ack_by` and `respond_by`, and the item records `offered_times`

#### Scenario: Failure: an agent tries to approve the policy
- **WHEN** an AI agent tries to approve an openChart response policy version
- **THEN** the approval is refused

#### Scenario: Failure: an approved window is longer than the offer's
- **WHEN** the approved policy's response deadline for an item falls after the offer's `respond_by`
- **THEN** the offer's earlier deadline governs the item

### Requirement: MI-06 openChart reports acknowledgment, response and clock expiry to openPractice over durable delivery
openChart SHALL report each item's progress to openPractice with `handoff.status`, using only the schema's codes:
- `responded` as soon as HealthLinc has accepted the clinician's reply for delivery (MI-11);
- `clock_expired` the moment the item's effective response deadline passes with no reply, which for an `urgent` or `priority` item with no possible owner is at once (MI-08);
- `returned_not_clinical` when a clinician returns the item as administrative (MI-15);
- `content_unavailable` under MI-03;
- `closed` when a holder of `close` records the item's closing outcome (MI-07).

`returned_not_clinical` SHALL be the last status for its item. After `responded`, openChart SHALL send `closed` when the item closes. openChart SHALL answer each `handoff.urgency_raised` with `message.ack`. A `responded` or `clock_expired` status SHALL be written in the same transaction as HealthLinc's acceptance or the expiry, and SHALL NOT wait for any batch or schedule.

Every message openChart sends about a handoff SHALL carry its `handoff_id`. It SHALL also carry the `link_id` when the handoff has a link (`identity_state` `linked` or `link_in_review`), and SHALL carry no `link_id` for an `unlinked` handoff. This covers `handoff.ack`, `handoff.status`, `handoff.clinician_urgency_raised`, and the `message.ack` that answers `handoff.urgency_raised`.

Every `handoff.ack`, `handoff.status`, `handoff.clinician_urgency_raised`, `clinical_need.marker` and `message.ack` openChart sends SHALL be written to the durable outbound store of PL-14 in the same transaction as its cause. It SHALL be delivered with retries that reuse its original `message_id`, until delivery succeeds, and for `handoff.status` and `clinical_need.marker` until openPractice answers with `message.ack`. Delivery MUST NOT rely on `frappe.publish_realtime` or any other site-local event. Clock expiry SHALL NOT close, cancel or unassign an item.

#### Scenario: A reply is delivered
- **WHEN** HealthLinc accepts the clinician's reply and the owner, holding `close`, then closes the item with an outcome
- **THEN** openChart sends `responded` and then `closed`

#### Scenario: Failure: openPractice is unreachable
- **WHEN** openPractice is unreachable while openChart has acknowledgments and status messages to send
- **THEN** the messages stay in the durable store and are delivered with their original `message_id` when openPractice returns, and no item changes state because of the outage

#### Scenario: Failure: the response clock expires
- **WHEN** an item's effective response deadline passes with no reply
- **THEN** openChart sends `clock_expired` at once, and the item stays open, owned, queued and escalated under MI-09

#### Scenario: An unlinked item's messages carry no link
- **WHEN** openChart acknowledges, or reports status for, an item offered with `identity_state` `unlinked`
- **THEN** each message carries the `handoff_id` and no `link_id`, and validates against the pinned schema

### Requirement: MI-07 Every item has exactly one named owner in a physician or nurse lane
Every inbox item SHALL have exactly one owner from acceptance until it closes, except while it has no possible owner: nobody holds `own` over `clinical_inbox_item` in force for its lane, or for the lane MI-08 lets it fall back to. MI-08 governs that state, and the item SHALL take an owner as soon as anyone can own it. The owner SHALL be a named human with an openChart account who holds the `clinician` or `nurse` role and a grant over `clinical_inbox_item` with the action `own`, in force for the item's lane (AU-06). Which role may hold a grant in which lane is AU-06's lane rule. Clinical roles, the medical director and grants are those of `define-clinical-acts-foundation` (openChart-spec#5): AU-01 defines the roles and the medical director, only the medical director records a grant (AU-02), and AU-06 carries the inbox's scopes, PROPOSED pending owner decision 92. This change defines no role or grant of its own (design Decision 15). A person without the grant in force for an action and a lane SHALL take none of the inbox actions it covers (design call MD-31).

Each item SHALL sit in one of two lanes, `physician` or `nurse` (AU-06). Lane assignment SHALL come from a lane policy that the medical director approves. What the `nurse` lane may triage or answer is the nurse-lane scope that the medical director records under AU-06. Until a lane policy is approved and a nurse-lane scope is recorded, every item SHALL enter the `physician` lane (design call MD-3).

At acceptance, the owner SHALL be:
- the first person the cover roster (MI-08) lists for the item's lane and hour;
- when nobody is listed, the medical director, when they hold `own` over `clinical_inbox_item` for the item's lane (AU-06);
- otherwise, MI-08's rule for an empty roster slot.

No item SHALL close without a closing outcome recorded by a named human who holds a grant over `clinical_inbox_item` with the action `close`, in force for the item's lane (AU-06). openChart SHALL refuse a close by anyone else, and the item SHALL stay open and owned. A recorded closing outcome closes the item, including one already answered, and openChart then sends `closed` (MI-06). A return under MI-15 is not a close: it ends the item with outcome `returned_not_clinical` and needs `return`. No agent SHALL own, acknowledge, answer, re-route or close an item (design call MD-10). This matches the foundation's AU-05, under which only named humans act on clinical acts.

#### Scenario: Failure: nobody is rostered for the lane and hour
- **WHEN** an offer arrives for an hour with no one listed for its lane
- **THEN** the medical director owns the item when they hold `own` for that lane, and otherwise MI-08's rule for an empty slot applies

#### Scenario: An answered item is closed
- **WHEN** HealthLinc has accepted the owner's reply, and the owner, holding `close` for the item's lane, records a closing outcome
- **THEN** the item closes, and openChart sends `closed` after `responded` (MI-06)

#### Scenario: Failure: a close without the close action
- **WHEN** an owner whose `clinical_inbox_item` grant for the item's lane does not include `close` tries to close the item with an outcome
- **THEN** openChart refuses the close, the item stays open and owned, and openChart sends no `closed`

#### Scenario: Failure: someone closes an item with no outcome
- **WHEN** a user tries to close an item without recording an outcome
- **THEN** the close is refused and the item stays owned

#### Scenario: Failure: an agent tries to close an item
- **WHEN** an AI agent tries to close or answer an inbox item
- **THEN** the action is refused and the item is unchanged

### Requirement: MI-08 Reassignment, absence and roster cover keep every item owned
openChart SHALL keep a cover roster. It is a schedule, not a role: for every hour and lane it lists, in order, only people who hold `own` over `clinical_inbox_item` in force for that lane, the medical director included as the last fallback (AU-06; design call MD-4). The first person listed owns new items (MI-07). An item's *next rostered holder* is the person listed for its lane and hour who comes first in that order among those who are neither its current owner nor anyone who has already failed to acknowledge it (MI-09). There is no on-call designation (AU-06). AU-06 refuses a roster entry for anyone else, and removes a holder from every later slot at once when their grant lapses. openChart owns after-hours clinical cover in its own queue (ER-13 in the openPractice change).

The inbox SHALL NOT be enabled until the roster covers every hour of each lane in use, with the medical director as the fallback where nobody else is listed. While the inbox is enabled, openChart SHALL refuse a roster or account change that would leave an hour with neither.

**An empty slot after a lapse.** A grant lapse is not a roster change, so the refusal above cannot stop it. When a lapse, or anything else, leaves an hour and lane with nobody rostered, openChart SHALL keep a human reaching every item (design call MD-4):
- openChart SHALL warn the medical director, and the administrative role that AU-01 names, ahead of a scheduled end of a grant or of the attestation it rests on that would leave a slot empty. It SHALL warn the medical director at once when a narrowing they record would do so;
- when a slot becomes empty, openChart SHALL alert the medical director and that administrative role at once, with a coded cause and an opaque reference only (MI-21);
- an empty `nurse`-lane slot SHALL fall back to the `physician` lane for that hour, and its items move to that lane, whose grants AU-06's lane rule governs. An empty `physician`-lane slot SHALL fall back to the medical director, when they hold `own` for that lane (AU-06);
- when nobody can take the item, openChart SHALL alert the medical director and every holder of a `clinical_inbox_item` grant in force for the lane at once, and re-alert them at each escalation interval until one of them takes it.

While no medical director designation is in force (AU-01, AU-03), every alert that this requirement or MI-09 sends to the medical director SHALL go to the administrative role that AU-01 names, which can designate one, with a coded cause and an opaque reference only.

An offer that openChart cannot give a named owner SHALL be kept durably and unacknowledged, never accepted without an owner (MI-04) and never dropped. Its deadlines SHALL run from the offer as received. openChart SHALL answer `accepted` once an owner is assigned. Until then, openPractice's alert for a missing acknowledgment runs at `ack_by`, and for an urgent item so does its fallback (ER-07 and ER-09 in the openPractice change). **No possible owner.** An accepted item has no possible owner when nobody holds `own` over `clinical_inbox_item` in force for its lane or, for a `nurse`-lane item, for the `physician` lane. That happens when the last such grant, or the attestation it rests on, ends (AU-03), including the medical director's, whose designation then ends too. Such an item SHALL stay open, listed and re-alerted as above. For an `urgent` or `priority` item, openChart SHALL end its effective response deadline at once and send `clock_expired` in the same transaction, so that openPractice runs its fallback for an `urgent` item, or its tracked on-call alert for a `priority` one, at once (ER-07 and ER-09 in the openPractice change; design call MD-34). A `routine` item SHALL be reported `clock_expired` at its deadline; openPractice is not told sooner (tension MT-5). When anyone gains `own` for the item's lane, openChart SHALL make them its owner at once.

An owner who holds `reassign` (AU-06) MAY reassign an item to another person who holds `own` for the lane it moves to, in a lane the policy allows. The reassignment SHALL be recorded with actor, time and reason. openChart SHALL move each open item at once when its owner is marked absent, loses access, has their account disabled, or no longer holds the role or the `own` grant (MI-07). The item SHALL go to its next rostered holder, or else to the medical director when they hold `own` for that lane, or else under the rule for an empty slot above. Reassignment and cover SHALL NOT reset or extend the clock.

#### Scenario: Failure: an owner's account is disabled
- **WHEN** the account of a clinician who owns an open `urgent` item is disabled
- **THEN** the item moves at once to cover, and its deadlines are unchanged

#### Scenario: Failure: a roster change would leave an hour uncovered
- **WHEN** an administrator tries to remove the only roster entry for an hour and lane, and no medical director fallback is named
- **THEN** the change is refused

#### Scenario: Failure: a grant lapse empties a roster slot
- **WHEN** the only `physician`-lane clinician rostered for tonight's hours loses their `own` grant when its interval ends
- **THEN** AU-06 takes them off the roster, openChart alerts the medical director and the administrative role of AU-01 at once, and the medical director covers those hours when they hold `own` for the `physician` lane

#### Scenario: Failure: nobody can own an urgent offer
- **WHEN** an `urgent` offer arrives for an hour whose slot is empty, and the medical director holds no `own` grant for its lane
- **THEN** openChart keeps the offer durably and unacknowledged, alerts the medical director and every holder of a `clinical_inbox_item` grant for the lane at once and at each escalation interval, answers `accepted` only once one of them owns it, and openPractice's fallback runs at `ack_by` meanwhile

#### Scenario: Failure: the only holder's attestation lapses while they own an urgent item
- **WHEN** the medical director holds the only `own` grant for the `physician` lane and owns an open `urgent` item, and the attestation their designation and grants rest on expires
- **THEN** the designation and grants stop at once (AU-03), the item has no possible owner, openChart sends `clock_expired` at once so openPractice's fallback runs, alerts the administrative role of AU-01, and keeps the item open and listed until someone can own it

#### Scenario: Failure: a routine item loses every possible owner
- **WHEN** an accepted `routine` item has no possible owner after a grant lapse
- **THEN** it stays open, listed and re-alerted, and openChart reports `clock_expired` at its deadline, not sooner (tension MT-5)

### Requirement: MI-09 An unacknowledged urgent item escalates to the next rostered holder, then to the medical director
openChart SHALL escalate every item that has no clinician acknowledgment by its acknowledgment deadline, when the item is `urgent`, or `priority` and unfiled because of its identity (MI-18). A clinician acknowledgment is an explicit act by the item's owner under the action `acknowledge` (AU-06), recorded with its time. Delivery of a notification is not acknowledgment. The escalation steps are:
1. openChart SHALL alert the item's next rostered holder for the hour (MI-08) at once, and make them the owner. Step 1 never goes back to the owner who failed to acknowledge. When there is no next rostered holder, or it is the medical director, openChart SHALL go straight to step 2.
2. When that holder does not acknowledge within the next escalation interval, or step 1 was skipped, openChart SHALL alert the medical director (AU-01 of the foundation) and make the medical director the owner, when they hold `own` for the item's lane (AU-06), or for the `physician` lane when the item is in the `nurse` lane, which it then moves to as MI-08 provides, and are not the owner who failed to acknowledge. Otherwise openChart SHALL alert the medical director and every holder of a `clinical_inbox_item` grant in force for that lane, as MI-08 provides for an empty slot.
3. After the last step, openChart SHALL keep re-alerting the medical director, and every holder alerted at step 2, at each escalation interval until a clinician acknowledges.

Until a response policy is approved, each escalation interval SHALL equal the item's acknowledgment window (`ack_by` minus `routed_at`). An item that arrives at or after its `ack_by` SHALL escalate at once (design call MD-2). Escalation SHALL NOT drop, park or close an item, SHALL NOT depend on any agent, and SHALL run whatever the item's identity state (MI-18). Any other item that has no acknowledgment by its deadline SHALL move to its lane's cover for the hour.

An item whose clock has expired SHALL stay in the queue, open and owned, or listed and re-alerted while it has no possible owner (MI-08), until a clinician replies or a holder of `close` for its lane records a closing outcome (MI-07). openChart SHALL let a holder of a `clinical_inbox_item` grant in force for the item's lane, under AU-06's lane rule, find an open item by its routing id (`handoff_id`) and see it, and SHALL NOT show it by routing id to anyone else. That includes openPractice's on-call clinician named in its tracked alert (ER-07 and ER-09 in the openPractice change), when they hold such a grant (tension MT-7).

#### Scenario: Failure: the owner does not acknowledge an urgent item
- **WHEN** an `urgent` item's acknowledgment deadline passes with no acknowledgment by its owner
- **THEN** the item's next rostered holder, never the owner who failed to acknowledge, is alerted at once and becomes the owner

#### Scenario: Failure: the next rostered holder does not acknowledge
- **WHEN** the next rostered holder does not acknowledge within the next escalation interval
- **THEN** the medical director is alerted and becomes the owner

#### Scenario: Failure: the owner who failed is the only person listed
- **WHEN** an `urgent` item's owner, the only person listed for its lane and hour, does not acknowledge by the acknowledgment deadline
- **THEN** openChart skips step 1 and alerts the medical director at once, who becomes the owner when they hold `own` for the lane, and the owner who failed is never alerted as the next holder

#### Scenario: Failure: nobody acknowledges
- **WHEN** no clinician acknowledges an `urgent` item after the medical director is alerted
- **THEN** openChart keeps re-alerting the medical director, reports `clock_expired` at the effective response deadline, and the item stays owned

#### Scenario: Failure: openPractice's on-call alert names an expired item
- **WHEN** openPractice's on-call clinician, who holds a `clinical_inbox_item` grant for the item's lane, receives openPractice's tracked alert for an expired item and looks it up in openChart by its routing id
- **THEN** openChart shows the item, which is still queued and open

#### Scenario: Failure: a holder looks up an item in another lane
- **WHEN** a person whose only `clinical_inbox_item` grant is for the `nurse` lane looks up a `physician`-lane item by its routing id
- **THEN** openChart does not show the item

### Requirement: MI-10 openChart never lowers urgency
openChart MUST NOT lower an item's urgency by any path. No user, role, agent, policy or message may lower it.

On `handoff.urgency_raised`, openChart SHALL set the item's urgency to the higher of its current urgency and the raised one. It SHALL move each deadline only earlier, to the earlier of the current and the offered time, and SHALL answer `message.ack` `received`. A raise that would not increase urgency SHALL be recorded and SHALL change nothing. A raise for a `handoff_id` that has not yet been received SHALL be recorded and applied when its offer arrives.

A named holder of `raise` over `clinical_inbox_item` for the item's lane (AU-06) MAY raise an item's urgency inside openChart, to `priority` or to `urgent`, which tightens its deadlines. openChart SHALL report every such raise to openPractice as `handoff.clinician_urgency_raised` (design call MD-8). The message carries:
- the `handoff_id`, and the `link_id` when the item is linked;
- the new `urgency`;
- `raised_at`;
- `respond_by`, openChart's new effective response deadline;
- `raised_by`, openChart's opaque clinician reference, never derived from the clinician's name or login.

openChart SHALL write the message to the durable outbound store of PL-14 in the same transaction as the raise, and deliver it until openPractice answers with `message.ack`. What openPractice then does is the openPractice change's to define (ER-03 and design calls DC-30 and DC-42 there):
- it shadows the new `respond_by`, but never later than its current shadow deadline, so the earlier deadline stands;
- for a raise to `urgent`, it runs its urgent path, including emergency guidance for the patient if the deadline is missed;
- for a raise to `priority`, it sends a tracked on-call alert, with no emergency guidance for the patient.

openChart SHALL NOT rely on openPractice to do more than that. No agent SHALL raise urgency in openChart. A raise to `urgent` on an item already `responded` or closed SHALL reopen it inside openChart, to its last owner or to cover, under MI-09 (design call MD-9).

#### Scenario: Failure: a clinician tries to lower urgency
- **WHEN** a clinician tries to change an `urgent` item to `routine`
- **THEN** the change is refused and the item stays `urgent`

#### Scenario: Failure: a late raise would extend a deadline
- **WHEN** a raise arrives whose new `respond_by` is later than the item's current effective response deadline
- **THEN** the urgency rises and the current, earlier deadline is kept

#### Scenario: Failure: a raise arrives before its offer
- **WHEN** a `handoff.urgency_raised` arrives for a `handoff_id` openChart has not yet received
- **THEN** openChart records it, answers `message.ack` `received`, and applies the raise when the offer arrives

#### Scenario: A clinician raises an item to urgent
- **WHEN** a clinician raises a `priority` item to `urgent`
- **THEN** openChart tightens the item's deadlines, and sends `handoff.clinician_urgency_raised` with `urgent`, `raised_at`, its new `respond_by` and `raised_by` through the durable store

#### Scenario: A clinician raises a routine item to priority
- **WHEN** a clinician raises a `routine` item to `priority`
- **THEN** openChart sends `handoff.clinician_urgency_raised` with `priority` and its new `respond_by`

#### Scenario: Failure: openPractice is unreachable when a clinician raises urgency
- **WHEN** openPractice is unreachable at the moment a clinician raises an item to `urgent`
- **THEN** the message stays in the durable store and is delivered with its original `message_id` when openPractice returns, and openChart's own escalation under MI-09 runs meanwhile

### Requirement: MI-11 The clinician's reply goes to the patient through HealthLinc
openChart SHALL send the clinician's reply to the patient through HealthLinc, as `reply.deliver` under `openchart-conversation-retrieval/1.0`, against the offer's `reply_path_ref`, over openChart's own HealthLinc integration. It SHALL never send the reply through openPractice (ER-05 in the openPractice change). This holds whichever system holds the conversation, as openPractice ER-05 also states (design call MD-16). openChart SHALL send `reply.deliver` only while HealthLinc has declared `reply_delivery` (MI-03). Only a named human who holds `reply` over `clinical_communication`, in force for the item's lane under AU-06's lane rule, SHALL send a reply, and only as the item's owner or as someone the lane policy allows. Without that grant, openChart SHALL refuse the reply (design call MD-31). Each reply SHALL carry its `reply_id`, the sender's opaque `clinician_ref` and the author type `clinician` (MI-12).

openChart SHALL report `responded` only after HealthLinc answers the reply with `message.ack` `received`, which means accepted for delivery. When HealthLinc cannot be reached, or refuses with `temporarily_unavailable`, openChart SHALL keep the reply and retry with the same `message_id`. When HealthLinc refuses with any other code, or has not declared `reply_delivery`, openChart SHALL keep the reply and show the owner the coded reason, so that they can reach the patient through a permitted channel (MI-22). In every case the item SHALL stay open and owned, and the clock SHALL keep running (design call MD-26).

Once HealthLinc has declared `delivery_failure_callback`, it may report with `reply.delivery_failed` that a reply it had accepted could not be delivered. The message carries `reply_message_id`, `reply_id`, `handoff_id`, `reply_path_ref`, `failure_reason` and `failed_at`. `failure_reason` is one of `recipient_link_revoked`, `account_closed`, `conversation_unavailable`, `placement_failed`, `no_permitted_notification_channel` or `service_suspended` (design call MD-26). openChart SHALL accept the callback only from HealthLinc's authenticated integration and only for a reply it sent. Otherwise it SHALL refuse it with `unauthorized` or `reference_not_found`. On an accepted callback, openChart SHALL treat `responded` as not final (design call MD-21):
- it SHALL reopen the item if it was closed, and keep it owned by its last owner or by cover;
- for an `urgent` item, it SHALL escalate under MI-09;
- it SHALL record the failure (MI-12);
- it SHALL show the owner the coded cause, and point them to a permitted channel (MI-22).

A repeated callback for the same reply SHALL change nothing further. Under the handoff contract 1.0 no status withdraws `responded`, so openChart sends openPractice nothing for the failure (tension MT-15).

#### Scenario: A reply is accepted
- **WHEN** a clinician sends a reply and HealthLinc answers `reply.deliver` with `message.ack` `received`
- **THEN** openChart records the reply and reports `responded`

#### Scenario: Failure: HealthLinc refuses the reply
- **WHEN** HealthLinc refuses a reply with `message.ack` `rejected` and the code `reply_path_invalid`
- **THEN** the item stays open and owned, openChart does not report `responded`, and the owner sees the coded reason

#### Scenario: Failure: an accepted urgent reply is not delivered
- **WHEN** HealthLinc sends `reply.delivery_failed` with `failure_reason` `no_permitted_notification_channel` for an `urgent` reply that openChart had already reported as `responded`
- **THEN** the item reopens and stays owned, it escalates under MI-09, the owner is pointed to a permitted channel, and openChart sends openPractice nothing under the handoff contract 1.0

#### Scenario: Failure: an accepted routine reply is not delivered
- **WHEN** HealthLinc sends `reply.delivery_failed` for a `routine` reply
- **THEN** the item reopens to its owner, who sees the coded cause, and it is not escalated under MI-09

#### Scenario: Failure: HealthLinc has withdrawn reply delivery
- **WHEN** HealthLinc's latest `capabilities.result` no longer declares `reply_delivery`, and a clinician sends a reply
- **THEN** openChart sends no `reply.deliver`, keeps the reply, and keeps the item open and owned, and the owner is told to use a permitted channel

### Requirement: MI-12 A clinical communication is recorded with its author type and provenance, and is never a diagnosis or a clinical fact of record
This requirement is the single definition of the clinical communication record in openChart. Other openChart changes reference it rather than defining a second record; that includes `define-ai-authored-clinical-records` (openChart-spec#4; ruling 64). Every record SHALL carry one origin (design call MD-28):
- **`handoff`:** an inbox item. openChart SHALL record every inbox item as one clinical communication record of this origin, with the provenance stated below.
- **`ai_consult`:** a consult record that `define-ai-authored-clinical-records` keeps from a `consult.write`: an accepted consult record (its AC-01), or a quarantined one (its AC-11). That change defines this origin's provenance, among it the model identifiers and versions, the evidence references, the mode in force, the authority and the exchange's content digest (its AC-01 and AC-03), and the record holds the full exchange. Its turns carry only the author types `patient`, `representative` and `ai` (its AC-02). The handoff references below are absent for this origin. An `ai_consult` record exists whether or not the inbox is enabled, and needs no openPractice (MI-20).

**The quarantined mark.** A record of origin `ai_consult`, and only such a record, SHALL carry these fields, as that change's AC-11 names them:
- `ai_consult_state`: `accepted` or `quarantined`;
- `quarantine_cause`: present only when `quarantined`; one of the ten values that AC-11 lists: the grant-check reasons `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `approver_mismatch` and `legal_review_mismatch`, or `source_cap_suspended`, for an emergency or red-flag consult kept from a source under a cap suspension (that change's AW-13);
- `quarantine_grant_checked`: present only when `quarantined` and a grant existed; the `grant_id` and `grant_version` openChart checked.

Their meaning, and who may read a quarantined consult, are that change's AC-11. Wherever the inbox shows a quarantined consult (MI-24), it SHALL mark it visibly as quarantined, with its `quarantine_cause`. It SHALL never present it as an accepted consult or as a clinical fact.

The author types, the rule that a communication is never a fact of record, and the versioning rule below apply to both origins. The provenance list, MI-20's inertness and MI-24's no-copy rule apply to `handoff` records only.

**Author type.** Every piece of content in a clinical communication SHALL carry exactly one author type:
- `patient`, for the patient. Content from the patient's representative carries `representative`, and is treated like `patient` content under every rule in this capability. A patient's or representative's own turn SHALL never be recorded or shown as AI content, whichever system holds the conversation.
- `ai`, for any AI or agent. The provenance SHALL name the source, by the retrieval contract's source token:
  - HealthLinc's coach (`healthlinc`), which gives general health information only, with a not-medical-advice statement (rulings 51 and 54);
  - medXfactory's medical AI (`medxfactory`) (ruling 51). Its advice-only answers may reach the patient without prior sign-off (ruling 66). They are AI content, never shown as clinician-reviewed;
  - an openPractice agent's administrative answer (`openpractice_agent`). Each such turn SHALL carry either the read-only answer type and version the agent used (AH-05 exception 1 in openPractice change `define-actors-agents-and-work-inbox`; ruling 45), or the staff member who approved the agent's drafted answer. The retrieval schema refuses a turn with neither or both.
- `clinician`, for a named human who holds the `clinician` or `nurse` role of `define-clinical-acts-foundation` (AU-01), acting through an authenticated openChart session. A retrieved turn that claims `clinician` carries the `reply_id` of a reply openChart sent. openChart SHALL show it as clinician-authored only when that `reply_id` matches its own reply record, and otherwise SHALL record and show it as `unknown` (design call MD-24).
- `staff` or `system`, for content from practice staff, or from a system rather than a person.
- `unknown`, a fail-safe for content whose author type the source system does not report. `unknown` content SHALL never be treated, shown or delivered as clinician-authored.

**Urgency sources.** Every urgency change SHALL be recorded with its source and an author type. `coach_triage`, `medical_ai_triage` and `agent_proposal` are `ai` (ruling 51, amending ruling 44). `staff` is `staff`, `routing_rule` is `system`, and a clinician's raise inside openChart is `clinician`. `patient_checklist`, the patient's own answers to HealthLinc's red-flag checklist (ruling 71), is `patient` and SHALL never be recorded as `ai` (MI-02).

**Provenance of a `handoff` record.** The record SHALL hold:
- the handoff references: `handoff_id`, `link_id` when present, `identity_state`, `healthlinc_message_ref`, `conversation_source`, `conversation_ref`, `reply_path_ref`, the origin and any split-group reference;
- for an `unlinked` item, the `unlinked_identity` as received: `legal_name`, `birth_date` and `administrative_sex`. It is marked unverified, is never projected onto an `OC Patient`, and is never used to match (MI-17, MI-18);
- every urgency change with its source, every owner change, every clock event, every acknowledgment, every status sent, every clinician urgency raise and clinical-need marker sent, and every reply delivery failure reported (MI-10, MI-11, MI-25);
- for every retrieval, the `snapshot_ref`, the `consent_ref`, the urgency the holder applied, the count of withheld turns if any, `patient_told_at` and `origin_conversation_ref` where given, and the retrieval time; for a failed retrieval, its coded cause;
- for every retrieved turn, keyed by its `turn_id`: its position, author type, source token, time, whether it is a request turn, and its sharing basis; and, where present, its answer type and version, its approver or its `reply_id`;
- for an `ai` turn, where the holder gives them: the mode in force (`ai_mode`: `advice_only`, `limited_practice` or `full_practice`), the code of the disclosure shown to the patient (`disclosure_code`), the model reference (`model_ref`), the advice-statement reference (`advice_statement_ref`) (design call MD-30), and the emergency-guidance codes (`emergency_guidance`) (design call MD-33);
- for a conversation HealthLinc holds, also each turn's text as retrieved;
- for a conversation medXfactory holds, no copy of any turn's text (MI-24, design call MD-27);
- every reply, with the named clinician who sent it, its time and HealthLinc's acceptance.

**Not a fact of record.** A clinical communication SHALL NOT be a diagnosis, problem, order, prescription, encounter, intake statement or other clinical fact of record, whoever wrote it. Nothing in it SHALL become one through this capability. Only a separately governed clinical workflow may record such a fact (MI-14, MI-26).

A recorded communication MUST NOT be silently overwritten or deleted. A correction SHALL create a new version that references its predecessor, with actor, reason and time. This is consistent with the ratified rule that amendments preserve accepted history. A `handoff` record SHALL be filed to an `OC Patient` only when MI-17 resolves the patient; otherwise it stays unfiled under MI-18. How an `ai_consult` record names its patient is for `define-ai-authored-clinical-records` to define. The storage shape SHALL be decided in planning.

#### Scenario: A patient's message is recorded
- **WHEN** HealthLinc returns a conversation turn that the patient wrote
- **THEN** the record holds it with author type `patient`, HealthLinc as the source system, its reference and its times, and it is not a clinical fact of record

#### Scenario: A coach turn is recorded
- **WHEN** HealthLinc returns a conversation turn that its coach wrote
- **THEN** the record holds it with author type `ai`, and names HealthLinc's coach as the source system

#### Scenario: A medical-AI exchange is referenced
- **WHEN** medXfactory holds an item's conversation
- **THEN** the record holds the `conversation_ref`, the `snapshot_ref`, and each turn's id, author type, source and time, with medXfactory's medical AI named as the source of its AI turns, and no copy of any turn's text

#### Scenario: An openPractice agent's answer is recorded
- **WHEN** HealthLinc returns a turn with source `openpractice_agent` that carries an answer type and version
- **THEN** the record holds it with author type `ai`, names the openPractice agent as its source, and keeps the answer type and version

#### Scenario: A checklist urgency is recorded
- **WHEN** a `handoff.urgency_raised` with source `patient_checklist` arrives
- **THEN** the record holds the urgency change with author type `patient`, never `ai`

#### Scenario: A quarantined consult is shown with its cause
- **WHEN** a filed inbox item is associated with an `ai_consult` record whose `ai_consult_state` is `quarantined`, with `quarantine_cause` `grant_expired`, and a reader that AC-11 allows opens the item
- **THEN** the inbox shows the consult visibly marked as quarantined, with the cause `grant_expired`, and never as an accepted consult or a clinical fact

#### Scenario: A consult kept from a cap-suspended source is shown with its cause
- **WHEN** a filed inbox item is associated with a quarantined `ai_consult` record whose `quarantine_cause` is `source_cap_suspended`, and a reader that AC-11 allows opens the item
- **THEN** the inbox shows it visibly marked as quarantined, with that cause, and never as an accepted consult or a clinical fact

#### Scenario: Failure: an accepted consult carries a quarantine cause
- **WHEN** an `ai_consult` record whose `ai_consult_state` is `accepted` would carry a `quarantine_cause`
- **THEN** openChart refuses to record it, and no accepted consult carries a quarantine cause

#### Scenario: An AI consult record exists without the inbox
- **WHEN** `define-ai-authored-clinical-records` records an accepted `consult.write` at a site with no openPractice gateway and the inbox not enabled
- **THEN** the consult is a clinical communication record of origin `ai_consult`, holding the full exchange with that change's provenance, and the inbox's absence blocks nothing

#### Scenario: A clinician's reply is recorded
- **WHEN** a named physician sends a reply and HealthLinc accepts it
- **THEN** the record holds it with author type `clinician`, the physician's identity, the time and HealthLinc's acceptance

#### Scenario: Failure: a turn's author cannot be attributed
- **WHEN** a holder returns a conversation turn whose author it cannot attribute, as author type `unknown`
- **THEN** openChart records and shows it as `unknown`, and never as clinician-authored

#### Scenario: Failure: a clinical communication is read as a fact of record
- **WHEN** a consumer tries to read a clinician's reply, or a patient's turn, as a diagnosis of record
- **THEN** no diagnosis or other clinical fact exists for it, and it stays a clinical communication

#### Scenario: Failure: a user tries to edit a sent reply
- **WHEN** a user tries to change the text of a reply that HealthLinc has accepted
- **THEN** the edit is refused, and a correction is recorded as a new version that references the original, with both kept for audit

#### Scenario: Failure: retrieved content changes
- **WHEN** a later retrieval from HealthLinc returns content that differs from the content the clinician saw
- **THEN** openChart records the new content as a new version and keeps the version the clinician saw

### Requirement: MI-13 AI-authored and clinician-authored content are always distinguishable
openChart SHALL keep AI-authored content distinguishable from clinician-authored content wherever it records, shows or delivers that content. It SHALL do so with the author types and source systems of the clinical communication record (MI-12). AI-authored content, and content of `unknown` authorship, MUST NOT be recorded, shown or delivered as clinician-authored. Only the authenticated session of a named holder of the reply grant (MI-11) can create `clinician` content. This change grants no AI drafting of clinical replies (design call MD-10). Any AI assistance in the inbox needs a separately governed change. A patient's or representative's turn SHALL never be shown as AI content. An answer in medXfactory's advice-only class (ruling 66) SHALL be labelled AI-authored and SHALL never be shown as clinician-reviewed; the medical director's sampled review of that class happens in medXfactory, not in openChart. A retrieved turn that claims clinician authorship without a matching `reply_id` SHALL be shown as `unknown` (MI-12). With each AI turn, openChart SHALL show the clinician the mode, disclosure, model and advice statement the holder gave, and SHALL show any the holder did not give as not stated. openChart SHALL never infer them, so an AI turn with no `ai_mode` is never shown as advice-only (design call MD-30). An AI turn that carries `emergency_guidance` SHALL be shown prominently to the clinician, with its codes, wherever the turn or its item is shown. The codes never replace the turn's text, and SHALL NOT change the item's urgency, owner or clock (design call MD-33).

#### Scenario: Failure: medical-AI content could pass as a doctor's
- **WHEN** an item shows a turn written by medXfactory's medical AI
- **THEN** the turn is labelled AI-authored, with medXfactory's medical AI named as its source, and is never shown as clinician-authored

#### Scenario: Failure: an automated process tries to send a clinician reply
- **WHEN** an automated process tries to send a reply with author type `clinician`, without a named clinician's authenticated session
- **THEN** the reply is refused and nothing is sent

#### Scenario: Failure: a retrieved turn claims clinician authorship without a matching reply
- **WHEN** a holder returns a turn with author type `clinician` whose `reply_id` matches no reply openChart sent
- **THEN** openChart records and shows the turn as `unknown`, never as clinician-authored

#### Scenario: A patient's turn in a medical-AI conversation
- **WHEN** medXfactory returns a turn that the patient wrote in a conversation with its medical AI
- **THEN** openChart shows it as the patient's own turn, never as AI content

#### Scenario: An advice-only answer shows its disclosure
- **WHEN** medXfactory returns an AI turn with `ai_mode` `advice_only`, a `disclosure_code`, a `model_ref` and an `advice_statement_ref`
- **THEN** the clinician sees the turn labelled AI-authored, with the mode, the model, and the disclosure and statement under which it reached the patient

#### Scenario: Failure: an AI turn carries no provenance fields
- **WHEN** a holder returns an AI turn with none of the four AI-turn fields
- **THEN** the clinician sees the turn labelled AI-authored, with its mode, disclosure, model and statement shown as not stated, and never as advice-only

#### Scenario: An AI turn gave emergency guidance
- **WHEN** a retrieved AI turn carries `emergency_guidance` with the code `call_emergency_services`
- **THEN** the clinician sees the turn prominently, with the code and the turn's full text, and the item's urgency and deadlines are unchanged by it

### Requirement: MI-14 Patient-reported message text is never a diagnosis or a clinical fact
Under MI-12, a clinical communication is never a diagnosis or a clinical fact of record. Message text from a patient or a representative SHALL remain visibly patient-reported. It SHALL NOT become a diagnosis, problem, order, prescription, encounter, intake statement or other clinical fact. This is consistent with the ratified `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority": patient statements remain visibly patient-reported until an authorized clinical workflow records another assertion. Only a separately governed clinical workflow may record such an assertion. AI-authored content, from HealthLinc's coach or from medXfactory's medical AI, SHALL likewise not become a diagnosis or clinical fact through the inbox. A medical-AI exchange reaches the chart only under MI-24, and only as communication under MI-26.

No item, message or reply SHALL create a billable fact. Inbox records are not encounters, diagnoses or procedures, so CF-06 keeps reporting `no_billable_facts`, and CF-02 applies (design call MD-11).

#### Scenario: Failure: a message is read as a diagnosis
- **WHEN** a patient's message says "I think I have diabetes" and a consumer tries to treat it as a diagnosis
- **THEN** it stays a patient-reported message, and no condition, statement or fact is created from it

#### Scenario: Failure: billable facts are read after a reply
- **WHEN** openPractice reads clinical facts for a linked patient after a clinician has replied to a routed item
- **THEN** the read returns `no_billable_facts`

### Requirement: MI-15 Administrative items are re-routed, not answered, and openChart keeps no administrative queue
An item's owner who holds `return` (AU-06) and finds that it is administrative SHALL return it to openPractice with `handoff.status` `returned_not_clinical`, and SHALL NOT answer it (ruling 44; ER-12 in the openPractice change). After the return, openChart SHALL refuse any reply on that item. The item SHALL leave the clinical queue with outcome `returned_not_clinical`, and its record is kept under MI-12. openChart SHALL NOT keep an administrative work queue, administrative lanes or tools for answering administrative questions.

#### Scenario: A clinician returns a billing question
- **WHEN** a nurse finds that a routed item asks only about a statement balance
- **THEN** openChart sends `returned_not_clinical`, the item leaves the clinical queue, and no reply is sent

#### Scenario: Failure: someone replies to a returned item
- **WHEN** a clinician tries to reply to an item already returned as `returned_not_clinical`
- **THEN** the reply is refused

### Requirement: MI-16 Mixed questions are split, and only the clinical part is answered in openChart
When an item mixes clinical and administrative questions, the clinician SHALL answer only the clinical part. openChart SHALL ask HealthLinc, with `split.request` naming the offer's `healthlinc_message_ref` as its `request_ref`, to split the item and resubmit only the administrative part to openPractice as a new inquiry (design call MD-7; ruling 44). openChart SHALL send `split.request` only while HealthLinc has declared `split` (MI-03), and only for a named holder of `split` for the item's lane (AU-06). openChart MUST NOT send `returned_not_clinical` for a mixed item, MUST NOT send administrative text to openPractice, and MUST NOT lower urgency on a split. The item SHALL stay open and owned until HealthLinc answers the split request with `message.ack` `received`. Until then, openChart SHALL retry the request and show the owner a coded exception. While HealthLinc has not declared `split`, openChart SHALL send no `split.request` and SHALL show the owner the same coded exception.

#### Scenario: A mixed question is split
- **WHEN** a routed item asks about a symptom and about a bill, and HealthLinc acknowledges the split request
- **THEN** the clinician answers only the symptom question, openChart reports `responded` once HealthLinc accepts the reply, and the bill question reaches openPractice only through HealthLinc

#### Scenario: Failure: HealthLinc does not acknowledge the split
- **WHEN** HealthLinc does not acknowledge a split request
- **THEN** the item stays open and owned, openChart retries and shows a coded exception, and it does not send `returned_not_clinical`

#### Scenario: Failure: HealthLinc has not declared split
- **WHEN** a clinician asks to split an item while HealthLinc's latest declaration lacks `split`
- **THEN** openChart sends no `split.request`, the item stays open and owned with a coded exception, and openChart does not send `returned_not_clinical`

### Requirement: MI-17 A handoff resolves the patient only through the links that exist
openChart SHALL resolve the patient for an offer only through the links that exist, because there is no master patient identity across HealthLinc, openPractice and openChart (ruling 39). Those links are:
- the `openpractice` `OC Patient External Identifier` row whose provenance names the offer's `link_id` (PL-02), on an offer whose `identity_state` is `linked`. The row SHALL be `active` and SHALL belong to the `OC Patient` that the offer's `ehr_patient` triple names under openChart's own issuer (PL-03);
- where one exists, the openChart patient reference that the conversation's holder reports for the account behind it, as `ehr_patient` in `conversation.result` (MI-03). It SHALL name the same `OC Patient`. A holder's reference never resolves a patient on its own.

The offer's `identity_state` is an input, never a resolution. Where it and openChart's own link state differ, the more uncertain of the two governs (design call MD-5). An `unlinked` offer has no `link_id` or `ehr_patient`, so this requirement cannot resolve its patient. Its `unlinked_identity`, with `legal_name`, `birth_date` and `administrative_sex`, SHALL NOT be used to match, link or file the item, automatically or by default (ruling 39).

openChart MUST NOT match on names, dates of birth or other demographics. It MUST NOT resolve a handoff through any other namespace or system, including a Medx or medXfactory reference, even when medXfactory holds the conversation (design call MD-19). It MUST NOT create, change, merge or re-point a link or a patient while handling a handoff (PL-01, PL-05, PL-06).

#### Scenario: Every link agrees
- **WHEN** the offer's `link_id` names an `active` row for the `OC Patient` its `ehr_patient` triple names, and HealthLinc reports the same patient
- **THEN** the item is filed to that `OC Patient`

#### Scenario: Failure: HealthLinc reports a different patient
- **WHEN** HealthLinc reports an openChart patient reference that differs from the `OC Patient` the `openpractice` link names
- **THEN** the item stays unfiled, an identity review opens, and no link or patient record changes

#### Scenario: Failure: an unlinked identity resembles an existing patient
- **WHEN** an `unlinked` offer's `unlinked_identity` resembles an existing `OC Patient`
- **THEN** openChart neither matches nor files the item, and shows the subset to the clinician as unverified

### Requirement: MI-18 Unresolved or conflicting identity goes to identity review, and an urgent or priority item still reaches a clinician
When MI-17 does not resolve exactly one patient, openChart SHALL handle the item by its urgency (design call MD-5). The cases are:
- an offer whose `identity_state` is `link_in_review`, which covers identity review and a demographic hold alike;
- an offer whose `identity_state` is `unlinked`, which carries `unlinked_identity` (`legal_name`, `birth_date` and `administrative_sex`);
- an offer marked `linked` where openChart holds the link as unknown, revoked, superseded or in `identity_review` (a PL-08 hold included), or where the `ehr_patient` triple does not match the link;
- a holder's reference that disagrees, found after acceptance (MI-17).

- **`urgent` or `priority` offers.** openChart SHALL accept the offer into an unfiled item, and show the identity uncertainty to everyone who views it. It SHALL route the item under MI-07, escalate it under MI-09, and open an identity review. It MUST NOT reject, drop or park such an item because of its identity. For an `unlinked` item, openChart SHALL show the `legal_name`, `birth_date` and `administrative_sex` to the clinician as unverified, and never put them in a notification or log (MI-21). openPractice runs its own path at the same time: for an `urgent` item, its fallback with emergency guidance; for a `priority` item, a tracked on-call alert with no emergency guidance (ER-06 in the openPractice change).
- **`routine` offers.** The openPractice change's ER-06 offers only `urgent` and `priority` items on a link in review or with no link. The pinned schema refuses a `routine` offer whose `identity_state` is `link_in_review` or `unlinked`, so openChart answers it `schema_invalid` (MI-02). A `routine` offer marked `linked` whose link openChart finds uncertain SHALL be rejected with the schema's code:
  - `link_unknown` for an unknown link;
  - `link_revoked` for a revoked or superseded link;
  - `link_in_review` for a link in review;
  - `ehr_patient_mismatch` for a triple that does not match.

  openPractice then owns the exception (ER-06 and ER-07 in the openPractice change).

An unfiled item SHALL NOT be filed to any `OC Patient` until MI-17 resolves the patient (design call MD-6). Meanwhile, its content MAY be read and answered through HealthLinc's reply path. When an identity problem is found after acceptance, the item SHALL stay accepted and become unfiled, whatever its urgency. Where a link exists, identity review SHALL follow PL-06 and PL-08. It MUST NOT merge, overwrite or delete records. This matches the openPractice change's ER-06, which offers `urgent` and `priority` items on a link in review or with no link while openPractice's own path also runs (MT-1, MT-2). For an `urgent` or `priority` offer marked `linked` that openChart finds revoked, unknown or mismatched, openChart accepts it unfiled; the openPractice change's list of companion items says to refuse such an offer (tension MT-1).

#### Scenario: Failure: an urgent offer arrives on a link in review
- **WHEN** an `urgent` offer arrives with `identity_state` `link_in_review`
- **THEN** openChart accepts it into an unfiled item that shows the identity uncertainty, the escalation of MI-09 runs, and an identity review opens

#### Scenario: Failure: a priority offer arrives on a link in review
- **WHEN** a `priority` offer arrives with `identity_state` `link_in_review`
- **THEN** openChart accepts it into an unfiled item, opens an identity review and escalates it under MI-09, and never rejects it

#### Scenario: Failure: an urgent offer arrives for an unlinked patient
- **WHEN** an `urgent` offer arrives with `identity_state` `unlinked` and an `unlinked_identity`
- **THEN** openChart accepts it into an unfiled item, shows the `legal_name`, `birth_date` and `administrative_sex` to the clinician as unverified, matches nothing, opens an identity review, and escalates it under MI-09

#### Scenario: Failure: a routine offer arrives unlinked
- **WHEN** a `routine` offer arrives with `identity_state` `unlinked`
- **THEN** openChart answers `rejected` with reason `schema_invalid`, because the pinned schema allows that state only for `priority` and `urgent`, and creates no item

#### Scenario: Failure: the offer says linked but openChart holds the link in review
- **WHEN** a `priority` offer is marked `linked` but openChart holds that link in `identity_review`
- **THEN** openChart treats the link as in review, and accepts the offer into an unfiled item

#### Scenario: Failure: a routine offer arrives on a revoked link
- **WHEN** a `routine` offer names a revoked link
- **THEN** openChart answers `rejected` with reason `link_revoked` and creates no item

#### Scenario: Failure: the identity problem appears after acceptance
- **WHEN** HealthLinc reports a different patient for an accepted `priority` item
- **THEN** the item stays accepted and owned, becomes unfiled, and an identity review opens

### Requirement: MI-19 openChart receives no billing, payment-hold or financial status
openChart MUST NOT request, receive, store or show payment-hold status, balances, entitlement results or any other financial status for a routed item. A payment hold is applied at the gateway, openPractice. It blocks only non-urgent clinical messaging and new non-urgent scheduling, and never an urgent escalation (ruling 41). openChart SHALL handle every offer it receives without regard to any such status, and SHALL NOT gate, delay or reorder an item on it. This requirement adds to CF-05 and does not modify it.

#### Scenario: Failure: an offer carries a hold field
- **WHEN** an offer carries a payment-hold or balance property
- **THEN** openChart answers `rejected` with reason `schema_invalid`, because every schema object is closed, and stores nothing

#### Scenario: An urgent item for a held patient
- **WHEN** openPractice hands off an `urgent` item for a patient it holds on a payment hold
- **THEN** openChart handles it like any other `urgent` item and keeps no record that a hold exists

### Requirement: MI-20 openChart operates without openPractice, and without a gateway the inbox is inert
openChart MUST operate without MedxFactory, MedxEHR or openPractice, as the ratified `expanded-patient-intake` requirement states; PL-15 restates the openPractice part. This requirement restates that rule and does not weaken it. openChart SHALL also operate fully with no HealthLinc or medXfactory integration, and with no conversation source configured under `openchart-conversation-retrieval/1.0`. The inbox is optional. With no openPractice gateway configured, the inbox SHALL accept no handoff, and no other openChart operation SHALL depend on it. This inertness applies to the inbox only, not to the clinical communication record that MI-12 defines: an `ai_consult` record needs neither the inbox nor openPractice.

The inbox SHALL NOT be enabled until all of these are configured:
- an openPractice integration identity;
- `define-clinical-acts-foundation`'s feature (1), clinical authority (AU-01 to AU-06), built, with a medical director designated (AU-01) and AU-06's inbox scopes in force, PROPOSED pending owner decision 92 (design call MD-31);
- conversation retrieval under `openchart-conversation-retrieval/1.0` from HealthLinc, and from medXfactory where the practice uses medXfactory's medical AI (design call MD-12);
- HealthLinc's declared `reply_delivery`, `delivery_failure_callback` and `split` capabilities (design call MD-23);
- full cover under MI-08.

Disabling the inbox SHALL withdraw the integration's authorization for handoffs, so later offers are refused with `unauthorized`. Every open item SHALL stay owned until it closes. When HealthLinc withdraws one of the three capabilities while the inbox is enabled, openChart SHALL keep accepting offers, keep every item owned, send no message for the withdrawn capability, and show the coded cause to each affected owner and to the medical director (design call MD-23).

This change defines no route by which a patient's message reaches openChart except a handoff from openPractice, whose conversation openChart then retrieves from its holder. The medical AI's records reach openChart only through MedxEHR's relay (ruling 70, MI-24), which this change does not define (design call MD-12).

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no MedxFactory, MedxEHR, openPractice, HealthLinc or medXfactory
- **THEN** migrations complete, the golden-patient intake tests pass, and the inbox is not configured

#### Scenario: Failure: an offer reaches a site with no gateway
- **WHEN** a `handoff.offer` reaches an openChart site with no openPractice gateway configured
- **THEN** openChart refuses it as `unauthorized`, stores nothing, and every other operation is unaffected

#### Scenario: Failure: the inbox is enabled without cover
- **WHEN** an administrator tries to enable the inbox while an hour has nobody listed on the roster for a lane in use and no medical director fallback is named
- **THEN** the enablement is refused

#### Scenario: Failure: the inbox is enabled without HealthLinc's delivery-failure callback
- **WHEN** an administrator tries to enable the inbox while HealthLinc's latest `capabilities.result` lacks `delivery_failure_callback`
- **THEN** the enablement is refused

#### Scenario: Failure: the inbox is enabled without the foundation's inbox scopes
- **WHEN** an administrator tries to enable the inbox while the inbox scopes of AU-06 of `define-clinical-acts-foundation` are not in force
- **THEN** the enablement is refused, and offers stay refused as `unauthorized`

### Requirement: MI-21 No PHI in logs, errors, notifications, diagnostics or keys
openChart's logs, errors, diagnostics, clinician notifications and idempotency keys, and every coded reason it sends under either contract, MUST NOT contain names, dates of birth, contact details, patient identifier values, message or reply text, or other clinical content (PL-13; ER-16 in the openPractice change). Diagnostics SHALL reference items only by `handoff_id`, `message_id` and `link_id`. A clinician notification on any device SHALL say only that an item awaits, with its urgency, a coded cause and an opaque item reference. Opening the item SHALL require an authenticated openChart session.

#### Scenario: Failure: an urgent item is overdue
- **WHEN** openChart alerts an item's next rostered holder that an `urgent` item is unacknowledged
- **THEN** the notification carries only the urgency, the cause `urgent_ack_overdue` and an opaque item reference

#### Scenario: Failure: a retrieval fails
- **WHEN** a retrieval from a source system fails
- **THEN** the log entry holds the `handoff_id`, the `message_id` and a coded reason, and no content or patient detail

### Requirement: MI-22 Replies honor confidential-communication instructions
openChart SHALL apply PL-16 to every reply it sends through HealthLinc, including any notification HealthLinc sends for that reply, because the reply is a patient communication that openChart originates (ruling 27). openChart SHALL give HealthLinc the applicable restrictions as codes with the reply, in `reply.deliver`'s `channel_restrictions`, and SHALL NOT send through a channel they restrict.

An unfiled item's instructions cannot be determined. For such an item, openChart SHALL deliver the reply only within the HealthLinc conversation that carried the message, with `delivery_scope` `conversation_only`, and SHALL mark every other channel restricted (design call MD-13). When PL-16 withholds a reply, the item SHALL stay open and owned and SHALL NOT be reported `responded`. The owner SHALL be shown the coded reason, so they can reach the patient through a permitted channel. Withholding SHALL never close an item. This requirement does not weaken PL-16.

#### Scenario: Failure: the patient refuses text messages
- **WHEN** a clinician replies to a linked patient whose applied instructions carry `no_text_messages`
- **THEN** openChart gives HealthLinc that restriction with the reply, and no text message is sent for it

#### Scenario: Failure: no permitted channel remains
- **WHEN** PL-16 leaves no permitted channel for a reply
- **THEN** the reply is withheld, the item stays open and owned, openChart does not report `responded`, and the owner sees the coded reason

### Requirement: MI-23 The inbox boundary is covered by contract tests
The inbox SHALL be covered by contract tests, written first, that validate every handoff message and every retrieval message against its schema at the digest recorded in MI-02. The tests SHALL run against an openPractice double and a contract double of `openchart-conversation-retrieval/1.0` for each holder, HealthLinc and medXfactory, with synthetic data only. They SHALL cover:
- refusal of content fields and of unknown fields;
- `conversation_source` and `conversation_ref`, including a namespace that does not match the source;
- capability declaration, with `capabilities.request` and `capabilities.result`, and no message sent for an undeclared capability;
- `consent_ref`; the required request turn, with an empty result and a result without a request turn treated as failed retrievals; `request_ref` on the retrieve and on every request turn, a request turn without it or with empty or whitespace-only text refused by the schema, a result whose request turns carry no matching `request_ref` refused with `result_mismatch`, and a placeholder that the owner records treated as a failed retrieval; for `priority` and `urgent` items, request turns shared as `urgent_escalation` with `patient_told_at`; withheld turns shown as a partial view; `result_mismatch`; and a `consent_not_granted` refusal;
- the optional AI-turn fields `ai_mode`, `disclosure_code`, `model_ref` and `advice_statement_ref`, shown when given, shown as not stated when absent, and refused on non-AI turns, and a `disclosure_code` that is not a code refused;
- `origin_conversation_ref` recorded and shown, never retrieved on its own, never used to resolve a patient, and refused when its value is not an opaque token; `emergency_guidance` shown prominently on AI turns and refused on other turns;
- no inbox action, reply or marker without its AU-06 grant for the item's lane, including a close refused without `close`, and `closed` sent once a holder of `close` records the outcome; a grant lapse that empties a roster slot, with the warnings, alerts and fallbacks of MI-08; an accepted `urgent` or `priority` item with no possible owner reported `clock_expired` at once; lookups by routing id limited to holders of a grant for the item's lane; and an offer held unacknowledged until it has a named owner;
- `ai_consult` records in state `accepted` and `quarantined`, a quarantined one always marked with its cause, each of AC-11's ten causes, and `quarantine_cause` refused on an accepted one;
- an association with an `ai_consult` record shown only on a filed item on the same patient, and a patient mismatch showing nothing and opening an identity review;
- every author type of MI-12, per turn by `turn_id`, with its source token, including `unknown`, `openpractice_agent` turns with an answer type or an approver, a clinician claim without a matching `reply_id`, patient turns never shown as AI content, and medical-AI content never filed through the inbox;
- AI-authored orders, prescriptions and diagnoses in inbox items held as communication, with no clinical act created (MI-26);
- `clinical_need.marker`: mark and withdraw under one `need_id`, the `valid_until` and `origin` rules, `related_handoff_id` for `urgent_escalation`, and the handling of `origin_not_verified`;
- acknowledgment, rejection, replay and duplicate offers;
- every status code, including `clock_expired` sent the moment the clock runs out and `responded` sent as soon as HealthLinc accepts a reply;
- an expired item kept in the queue and found by its routing id;
- urgency raises, and the absence of any lowering;
- deadlines that never extend;
- every identity case in MI-18, including `identity_state` `link_in_review` and `unlinked`, the three `unlinked_identity` fields shown as unverified and never matched, `priority` offers never rejected for identity, and `routine` offers in those states refused by the schema;
- no `link_id` on any message openChart sends about an `unlinked` handoff;
- `handoff.clinician_urgency_raised` for raises to `priority` and to `urgent`, and every urgency source recorded with its author type under MI-12, with `patient_checklist` recorded as `patient`;
- `reply.delivery_failed` with each of its six `failure_reason` codes, reopening its item, and escalating it when it is `urgent`;
- escalation to the next rostered holder, never back to the owner who failed to acknowledge, and to the medical director;
- reply delivery, refusal and withholding;
- re-routing and splitting;
- the absence of financial fields;
- no PHI in logs, notifications or keys.

The standalone golden-intake tests SHALL pass with the inbox unconfigured.

#### Scenario: CI runs the inbox suite
- **WHEN** CI runs the inbox contract tests
- **THEN** they pass against the openPractice double and the retrieval-contract doubles with synthetic data only

#### Scenario: Failure: a test adds a content field
- **WHEN** a test builds a `handoff.offer` that carries message text
- **THEN** schema validation fails, and the test expects that failure

### Requirement: MI-24 A medical-AI exchange reaches the chart only through MedxEHR's relay, and the inbox keeps it by reference
The medical AI's records SHALL reach openChart only through MedxEHR, which relays them with receipts (ruling 70, refining ruling 53). medXfactory does not write to openChart directly, and the records SHALL never pass through openPractice, which holds no clinical content (ruling 53). That write path belongs to openChart-spec change `define-ai-authored-clinical-records` (openChart-spec#4). This change cites it and defines no part of it (Open Question 4).

When medXfactory holds an inbox item's conversation, openChart SHALL retrieve it with `conversation.retrieve` for the clinician (MI-03). It SHALL record in the item only what MI-12 states for a conversation medXfactory holds: per-turn metadata keyed by `turn_id`, the `snapshot_ref`, the `consent_ref` and the retrieval provenance, with no copy of any turn's text. It SHALL NOT file the exchange to an `OC Patient` through the inbox (design call MD-17). This no-copy rule applies to inbox items only. It does not apply to an `ai_consult` record, which holds the full exchange under `define-ai-authored-clinical-records` (MI-12). When an inbox item names a conversation that an `ai_consult` record also references, the item may show that association by reference, as that change's AC-01 provides, and still files no copy. It SHALL show the association only on a filed item, only when both records are on the same patient, as that change's AC-01 also provides, only to someone that change lets read the record (its AC-06 and AC-11), and SHALL never use it to resolve or file a patient (MI-17; tension MT-23). When the two records are on different patients, openChart SHALL show no association. The disagreement is an identity problem found after acceptance (MI-18): the item stays accepted and owned, becomes unfiled, and an identity review opens. openChart SHALL change neither record. openChart MUST NOT accept medical-AI content from openPractice, and nothing in this change lets medXfactory write to openChart directly.

#### Scenario: A clinician answers an escalated medical-AI conversation
- **WHEN** a clinician answers an item whose conversation medXfactory holds
- **THEN** openChart records the reply as clinician-authored, and the item records the medical-AI exchange by reference, with per-turn metadata and no text

#### Scenario: Failure: the consult is on another patient
- **WHEN** a filed inbox item and an `ai_consult` record name the same conversation, but the consult record is on a different patient from the item
- **THEN** openChart shows no association, the item stays accepted and owned and becomes unfiled, and an identity review opens

#### Scenario: Failure: medical-AI content arrives from openPractice
- **WHEN** a handoff message from openPractice carries the text of a medical-AI exchange
- **THEN** openChart answers `rejected` with reason `schema_invalid` and stores nothing

#### Scenario: Failure: someone files the medical-AI exchange from the inbox
- **WHEN** a user tries to file a medXfactory-held exchange to an `OC Patient` from an inbox item
- **THEN** the filing is refused, and the item keeps its reference

#### Scenario: Failure: medXfactory sends a medical-AI record straight to openChart
- **WHEN** medXfactory sends a medical-AI record to openChart's inbox integration
- **THEN** openChart refuses it and records nothing, because the record's only path into openChart is MedxEHR's relay (ruling 70)

### Requirement: MI-25 A clinician's clinical-need marker is recorded in openChart and sent to openPractice as `clinical_need.marker`
openChart SHALL let a named human who holds `mark` over `clinical_need_marker` in force record a clinical-need marker, and a holder of `withdraw` withdraw it, for a patient with an `active` `openpractice` link (ruling 50; ER-18 in the openPractice change). AU-06 of `define-clinical-acts-foundation` records that grant only for the `clinician` role. Without it, openChart SHALL refuse the marker with a coded reason (design call MD-31). The kinds are:
- `messaging_continuity`, which keeps the patient's clinical messaging and medical-AI consults open for continuity of care, for example after a lapsed membership or a deactivation;
- `appointment_needed`, which records that an appointment is clinically needed, so that a payment hold never blocks it.

openChart SHALL attribute each marker to the clinician and record it. It SHALL send each mark and each withdrawal to openPractice as `clinical_need.marker`, on the patient's EB-01 `link_id`, with:
- a `need_id` that openChart mints for the marker and reuses for its withdrawal;
- the `action`, `mark` or `withdraw`, and the `kind`;
- `marked_by`, openChart's opaque reference to the clinician, never derived from the clinician's name or login;
- `marked_at`;
- for `mark` only, a `valid_until` time that the clinician sets, and an `origin` (design call MD-18);
- no reason, note or other clinical content (MI-21).

The origin SHALL be `clinician_judgment`, with one exception. A clinician who records the marker from an inbox item whose urgency is `urgent` MAY give the origin `urgent_escalation`. The urgency must be as openPractice offered or raised it, or come from a clinician's raise that openPractice acknowledged with `received` (MD-18). In that case `related_handoff_id` SHALL be that item's `handoff_id`. A withdrawal SHALL carry none of `valid_until`, `origin` or `related_handoff_id`.

openChart SHALL write each marker message to the durable outbound store of PL-14, and deliver it until openPractice answers with `message.ack`. When openPractice rejects a marker, for example with `origin_not_verified`, openChart SHALL show the clinician the coded reason and that the marker allows nothing. It SHALL NOT resend the marker with a different origin on its own. No agent SHALL record or withdraw a marker. openPractice applies access and holds, and openChart does not (ruling 41). A marker SHALL NOT cause openChart to receive any financial or access status (MI-19).

#### Scenario: A clinician keeps messaging open for continuity
- **WHEN** a physician records a `messaging_continuity` marker, with a `valid_until`, for a linked patient
- **THEN** openChart records it with the physician's attribution, and sends `clinical_need.marker` with action `mark`, the kind, `marked_by`, `marked_at`, `valid_until` and origin `clinician_judgment`, and no reason text

#### Scenario: A marker arises from an urgent item
- **WHEN** a clinician records an `appointment_needed` marker from an inbox item that openPractice offered as `urgent`
- **THEN** the marker carries origin `urgent_escalation`, with that item's `handoff_id` as `related_handoff_id`

#### Scenario: A clinician withdraws a marker
- **WHEN** a clinician withdraws a marker they recorded
- **THEN** openChart sends `clinical_need.marker` with action `withdraw` and the same `need_id`, and with no `valid_until`, `origin` or `related_handoff_id`

#### Scenario: Failure: openPractice cannot verify the urgent origin
- **WHEN** openPractice answers a marker with `message.ack` `rejected` and reason `origin_not_verified`
- **THEN** openChart shows the clinician the coded reason and that the marker allows nothing, and sends nothing further on its own

#### Scenario: Failure: a mark has no end time
- **WHEN** a clinician tries to record a mark without a `valid_until` time
- **THEN** the marker is refused, and nothing is sent

#### Scenario: Failure: an agent tries to record a marker
- **WHEN** an AI agent tries to record or withdraw a clinical-need marker
- **THEN** the action is refused and nothing is recorded

#### Scenario: Failure: no marker grant is held
- **WHEN** a physician who holds no `mark` grant over `clinical_need_marker` tries to record a `messaging_continuity` marker
- **THEN** openChart refuses it with a coded reason and sends nothing

#### Scenario: Failure: the link is not active
- **WHEN** a clinician tries to record a marker for a patient whose `openpractice` link is in `identity_review`
- **THEN** the marker is refused with a coded reason, and the clinician sees that reason

### Requirement: MI-26 AI-authored content is communication only until Tier 2 of `define-ai-authored-clinical-records` is in force for its act type
openChart SHALL treat AI-authored content as communication only, and SHALL NOT record, act on or present it as an order, prescription or diagnosis of an act type, until Tier 2 of openChart-spec change `define-ai-authored-clinical-records` (openChart-spec#4, being drafted under ruling 64) is in force for that act type. Ratifying that change does not end this hold. Its AA-01 keeps Tier 2 out of force, and refuses every `act.write` with `tier2_not_in_force`, until its required prerequisite `define-clinical-acts-foundation` (openChart-spec#5) is ratified and built and a future governed amendment puts Tier 2 in force (ruling 67). This change does not cover AI-authored orders, prescriptions or diagnoses.

The practice's medical director sets medXfactory's AI to one of three modes: advice only, full practice or limited practice (ruling 59). medXfactory's change `define-patient-medical-ai-connection` owns the mode framework and its gates (rulings 56 to 58). Ruling 59 stands, so this requirement fails closed. The never-grantable rule stays, and limited and full practice stay specified but off (ruling 67). An answer in medXfactory's advice-only class, which may reach the patient without prior sign-off (ruling 66), is AI-authored communication like any other. The chart's own record of the medical director's authorization, and the check of every AI write against it, belong to `define-ai-authored-clinical-records` (ruling 65); this change defines neither.

**Paths.** On the paths this change controls, inbox retrieval and the inbox's `handoff` records, content that presents itself as an AI-authored order, prescription or diagnosis SHALL be held as AI-authored communication, marked by code as not accepted as a clinical act (design call MD-20). On the write path of `define-ai-authored-clinical-records`, by which MedxEHR relays the medical AI's records (ruling 70), this change defers to that change: an `act.write` is refused and stores no content (its AD-7), and act-like content inside an `ai_consult` record is handled by its AC-05.

Until Tier 2 is in force for an act type, these rules apply:
- openChart MUST NOT record, act on or present AI-authored content as an order, prescription or diagnosis of that type, whatever mode, configuration or authority the content claims.
- The content SHALL stay distinguishable from clinician-authored content, with its author type `ai` and its source system named (MI-12, MI-13).
- In an inbox item, content that presents itself as an AI-authored order, prescription or diagnosis SHALL be held as AI-authored communication, marked by code as not accepted as a clinical act. It SHALL NOT create an order, prescription, diagnosis or other clinical fact.
- When such content appears in an inbox item, the owner SHALL see it labelled that way.
- The limited-practice and full-practice modes SHALL NOT be built in openChart until the conditions of that change's AA-01 hold.

#### Scenario: Failure: an AI-authored prescription appears in a retrieved conversation
- **WHEN** a conversation retrieved for an inbox item holds a turn from medXfactory's medical AI that presents itself as a prescription and claims full-practice authority
- **THEN** openChart holds it as AI-authored communication, names medXfactory's medical AI as its source, marks it as not accepted as a clinical act, and creates no prescription, order or diagnosis

#### Scenario: Failure: an AI act write arrives before Tier 2 is in force
- **WHEN** an AI system sends an `act.write` for a prescription on the write path of `define-ai-authored-clinical-records` before Tier 2 is in force
- **THEN** that change refuses it with `tier2_not_in_force` and stores no content, and the inbox neither holds nor recreates the refused content

#### Scenario: Failure: the hold outlasts ratification
- **WHEN** `define-ai-authored-clinical-records` is ratified, but no governed amendment has put Tier 2 in force for prescriptions
- **THEN** AI-authored content that presents itself as a prescription is still held as communication in an inbox item, and no prescription is created

#### Scenario: Failure: an AI-authored diagnosis appears in an inbox item
- **WHEN** a retrieved conversation in an inbox item contains an AI turn stating a diagnosis
- **THEN** the owner sees the turn labelled as AI-authored communication that was not accepted as a clinical act, and no condition or diagnosis is recorded

#### Scenario: Failure: a plan proposes building a practice mode
- **WHEN** a plan proposes building limited-practice or full-practice mode in openChart before the conditions of the AA-01 requirement of `define-ai-authored-clinical-records` hold
- **THEN** the plan is out of scope, and the work waits for that change
