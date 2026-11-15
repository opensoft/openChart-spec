## ADDED Requirements

### Requirement: MI-01 openChart receives routed clinical items in a clinical message inbox
openChart SHALL provide a clinical message inbox that receives the clinical items openPractice routes under contract `openpractice-clinical-handoff/1.0`. That contract is owned by `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation` (PR #6, not yet on main; ER-04 and ER-05 there). openChart is the doctor's clinical interface (ruling 34): the clinician reads and answers routed clinical questions in openChart. HealthLinc is the patient's gateway to their doctor: the patient may connect to their human doctor, through openPractice to openChart, or to medXfactory's medical AI (ruling 51). This inbox is the human-doctor path.

openChart SHALL accept handoff messages only from an authenticated openPractice integration identity. That identity SHALL hold a dedicated openChart integration role that is narrower than `System Manager`, is named in planning, and is authorized for subject, tenant, purpose and role, as the ratified API requirement demands. openChart SHALL use only the messages the pinned contract defines: `handoff.offer`, `handoff.ack`, `handoff.urgency_raised`, `handoff.status`, `clinical_need.marker` and `message.ack`. It SHALL define no message of its own toward openPractice.

Every requirement in this capability SHALL apply in the same way on every client through which a clinician uses openChart, whether mobile or workstation (ruling 35, a current-phase decision). No requirement depends on a device.

#### Scenario: A clinician works from a phone
- **WHEN** a clinician opens a routed item on a mobile client
- **THEN** the same ownership, clock, reply and authorship rules apply as on a workstation

#### Scenario: Failure: an unauthorized caller sends an offer
- **WHEN** a caller without the integration role sends a `handoff.offer`
- **THEN** openChart answers `handoff.ack` `rejected` with reason `unauthorized` and creates no item

### Requirement: MI-02 Handoff messages are validated against openPractice's canonical schema, pinned by path and digest
openChart SHALL validate every handoff message it receives or sends against the canonical schema that change `define-patient-gateway-and-escalation` owns in `opensoft/openPractice-spec`:
- `openspec/changes/define-patient-gateway-and-escalation/contracts/openpractice-clinical-handoff-1.0.schema.json`, at revision `097278c` (PR #6, not yet on main), SHA-256 `9e33b0f2cbd8aee1ffea0ae0377cb15dd98247ba4bf11479f9947ee6d42289bb`

The digest identifies the schema even after archival moves the file. openChart SHALL NOT implement against a schema whose digest differs from the digest recorded here, until both changes record the same new digest. When that change's schema changes, this pin SHALL be updated in a governed revision of this change.

The pinned schema carries everything this capability uses. Its offer names the conversation's holder in `conversation_source` (`healthlinc` or `medxfactory`), and gives a matching `conversation_ref` (ruling 51). It also defines `clinical_need.marker` (ER-18 in the openPractice change), which MI-25 sends.

openChart SHALL accept a `1.x` message at a MINOR version it has declared. It SHALL refuse a message whose MAJOR version it does not support with reason `unsupported_major_version`, and a message that fails the schema with reason `schema_invalid`. A refusal SHALL change nothing (the PL-12 pattern; PG-01 and ER-04 in the openPractice change).

#### Scenario: Failure: an offer fails the schema
- **WHEN** an offer carries a property the schema does not define
- **THEN** openChart answers `rejected` with reason `schema_invalid` and creates no item

#### Scenario: Failure: an unsupported major version arrives
- **WHEN** a `2.0` `handoff.offer` arrives
- **THEN** openChart answers `rejected` with reason `unsupported_major_version` and creates no item

#### Scenario: Failure: the canonical schema changes before both changes record it
- **WHEN** the openPractice change publishes a schema with a new digest that this change has not recorded
- **THEN** openChart keeps validating against the recorded digest and does not implement the new schema

### Requirement: MI-03 openChart obtains the escalated conversation by reference from the system that holds it, never from openPractice
The handoff is reference-only (ER-05 in the openPractice change). openChart SHALL obtain the escalated conversation by the offer's `conversation_ref` from the system that `conversation_source` names (ruling 51), over openChart's own authorized integration with that system (ruling 39):
- **`healthlinc`:** from HealthLinc, for a conversation with HealthLinc's coach;
- **`medxfactory`:** from medXfactory, for a conversation with medXfactory's medical AI.

The offer's `healthlinc_message_ref` is HealthLinc's reference for the patient's request. openChart SHALL keep it in the record (MI-12) and use it for split requests (MI-16), but SHALL NOT use it in place of `conversation_ref`. openChart MUST NOT request, accept or store message content from openPractice.

When retrieval fails, openChart SHALL keep the item open and owned, keep retrying, and show the owner that the content is unavailable. The same applies when openChart has no retrieval configured for the source system, for example a `medxfactory` conversation at a practice that has not configured medXfactory retrieval (design call MD-12). openChart SHALL report `content_unavailable` to openPractice (MI-06): at the first failed retrieval for an `urgent` item, and when the retry policy is exhausted for any other item (design call MD-15). An item SHALL NOT close because its content is unavailable.

#### Scenario: The conversation is retrieved
- **WHEN** openChart accepts an offer with `conversation_source` `healthlinc`, and HealthLinc returns the conversation for its `conversation_ref`
- **THEN** the owner sees each turn with its author type and source system, and nothing is requested from openPractice

#### Scenario: A medical-AI conversation is retrieved
- **WHEN** openChart accepts an offer with `conversation_source` `medxfactory`, and medXfactory returns the conversation for its `conversation_ref`
- **THEN** the owner sees it labelled as medXfactory's medical AI, and the item records it by reference only (MI-24)

#### Scenario: Failure: the source system is unreachable for an urgent item
- **WHEN** openChart cannot retrieve the conversation for an accepted `urgent` item from the system that holds it
- **THEN** openChart reports `content_unavailable` at once, keeps the item open and owned, retries the retrieval, and shows the owner the urgency and the missing content

#### Scenario: Failure: openChart has no retrieval for the source system
- **WHEN** an accepted item's conversation is held by a system for which openChart has no configured retrieval
- **THEN** the item stays open and owned, openChart reports `content_unavailable`, and it does not ask openPractice for the content

### Requirement: MI-04 Every offer is acknowledged, and handling is idempotent and replay-safe
openChart SHALL answer every schema-valid, authorized `handoff.offer` with exactly one `handoff.ack`. The two results mean:
- **`accepted`:** openChart has durably created the inbox item, assigned it a named owner (MI-07) and started its clock (MI-05). This is system acceptance, not a clinician reading the item (design call MD-1).
- **`rejected`:** the acknowledgment carries a reason code from the schema.

The `message_id` of each inbound message is its idempotency key. A message whose `message_id` was already processed SHALL be answered with the original result and SHALL change nothing. openChart SHALL keep exactly one inbox item per `handoff_id`. A later offer for an existing `handoff_id` under a new `message_id` SHALL be answered with the original result and SHALL NOT alter the item. If that offer's content differs from the original, openChart SHALL also record an integration exception that holds only identifiers and a coded cause (design call MD-14). The `message_id` of every message openChart sends SHALL be a random UUID, reused on every retry. No key SHALL carry PHI (PL-13).

#### Scenario: Failure: an offer is retried
- **WHEN** the same offer arrives three times with the same `message_id`
- **THEN** openChart holds one item and answers with the same `handoff.ack` result each time

#### Scenario: Failure: a conflicting offer reuses a handoff id
- **WHEN** a second offer for an existing `handoff_id` names a different `link_id`
- **THEN** the item is unchanged, openChart answers with the original result, and it records an integration exception holding only identifiers and a coded cause

### Requirement: MI-05 openChart owns the queue and the response clock
openChart SHALL own the queue and the response clock for every routed clinical item (ruling 43). The acknowledgment window, the response window and the escalation interval SHALL come from an openChart response policy that the practice's medical director, a named human, approves. No agent SHALL approve it.

Until a policy version is approved, openChart SHALL use the offer's `ack_by` and `respond_by` (design call MD-2). The windows in the openPractice change (its design call DC-3, for example acknowledge `urgent` items within 5 minutes and respond within 60 minutes) are proposed defaults in an unratified change. They are not facts and not clinical standards, and this change adopts no window of its own.

Once a policy version is approved, each item's effective deadline SHALL be the earlier of the policy's deadline and the offer's. No event SHALL extend an item's effective deadline: not reassignment, cover, filing, an urgency raise or a policy change. Each item SHALL record the policy version, or `offered_times`, that set its deadlines. The windows are alerting thresholds, not clinical standards.

openPractice treats `clock_expired`, or silence past `respond_by`, as `clinical_response_overdue`. For an urgent item it runs its fallback, with a tracked alert to the on-call clinician (ER-07 and ER-09 in the openPractice change). An effective response deadline therefore SHALL never fall after the offer's `respond_by`. openChart SHALL report `clock_expired` the moment that deadline passes (MI-06).

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
- `clock_expired` the moment the item's effective response deadline passes with no reply;
- `returned_not_clinical` when a clinician returns the item as administrative (MI-15);
- `content_unavailable` under MI-03;
- `closed` when the item closes with a recorded outcome.

`returned_not_clinical` SHALL be the last status for its item. After `responded`, openChart SHALL send `closed` when the item closes. openChart SHALL answer each `handoff.urgency_raised` with `message.ack`. A `responded` or `clock_expired` status SHALL be written in the same transaction as HealthLinc's acceptance or the expiry, and SHALL NOT wait for any batch or schedule.

Every `handoff.ack`, `handoff.status`, `clinical_need.marker` and `message.ack` openChart sends SHALL be written to the durable outbound store of PL-14 in the same transaction as its cause. It SHALL be delivered with retries that reuse its original `message_id`, until delivery succeeds, and for `handoff.status` and `clinical_need.marker` until openPractice answers with `message.ack`. Delivery MUST NOT rely on `frappe.publish_realtime` or any other site-local event. Clock expiry SHALL NOT close, cancel or unassign an item.

#### Scenario: A reply is delivered
- **WHEN** HealthLinc accepts the clinician's reply and the owner then closes the item with an outcome
- **THEN** openChart sends `responded` and then `closed`

#### Scenario: Failure: openPractice is unreachable
- **WHEN** openPractice is unreachable while openChart has acknowledgments and status messages to send
- **THEN** the messages stay in the durable store and are delivered with their original `message_id` when openPractice returns, and no item changes state because of the outage

#### Scenario: Failure: the response clock expires
- **WHEN** an item's effective response deadline passes with no reply
- **THEN** openChart sends `clock_expired` at once, and the item stays open, owned, queued and escalated under MI-09

### Requirement: MI-07 Every item has exactly one named owner in a physician or nurse lane
Every inbox item SHALL have exactly one owner at all times, from acceptance until it closes. The owner SHALL be a named clinician or nurse with an openChart account. Each item SHALL sit in one of two lanes: physician or nurse. Lane assignment, and what each lane may answer, SHALL come from a lane policy that the medical director approves. Until one is approved, every item SHALL enter the physician lane (design call MD-3).

At acceptance, the owner SHALL be:
- the person the cover roster (MI-08) names for the item's lane and hour;
- when nobody is named, the on-call clinician for the hour;
- when no on-call clinician is rostered, the medical director.

No item SHALL close without an outcome recorded by a named human. No agent SHALL own, acknowledge, answer, re-route or close an item (design call MD-10).

#### Scenario: Failure: nobody is rostered for the lane and hour
- **WHEN** an offer is accepted for an hour with no one named for its lane
- **THEN** the on-call clinician for the hour owns the item, or the medical director when no on-call clinician is rostered

#### Scenario: Failure: someone closes an item with no outcome
- **WHEN** a user tries to close an item without recording an outcome
- **THEN** the close is refused and the item stays owned

#### Scenario: Failure: an agent tries to close an item
- **WHEN** an AI agent tries to close or answer an inbox item
- **THEN** the action is refused and the item is unchanged

### Requirement: MI-08 Reassignment, absence and on-call cover keep every item owned
openChart SHALL keep a cover roster that names the on-call clinician for every hour, and SHALL name the practice's medical director as the last fallback (design call MD-4). openChart owns after-hours clinical cover in its own queue (ER-13 in the openPractice change).

The inbox SHALL NOT be enabled until the roster covers every hour or names the medical director as the fallback. While the inbox is enabled, openChart SHALL refuse a roster or account change that would leave an hour with neither.

An owner MAY reassign an item to another named clinician or nurse, in a lane the policy allows. The reassignment SHALL be recorded with actor, time and reason. openChart SHALL move each open item at once when its owner is marked absent, loses access, or has their account disabled. The item SHALL go to the lane's cover for the hour, or else to the on-call clinician, or else to the medical director. Reassignment and cover SHALL NOT reset or extend the clock.

#### Scenario: Failure: an owner's account is disabled
- **WHEN** the account of a clinician who owns an open `urgent` item is disabled
- **THEN** the item moves at once to cover, and its deadlines are unchanged

#### Scenario: Failure: a roster change would leave an hour uncovered
- **WHEN** an administrator tries to remove the only on-call entry for an hour, and no medical director fallback is named
- **THEN** the change is refused

### Requirement: MI-09 An unacknowledged urgent item escalates to the on-call clinician, then to the medical director
openChart SHALL escalate every `urgent` item that has no clinician acknowledgment by its acknowledgment deadline. A clinician acknowledgment is an explicit act by the item's owner, recorded with its time. Delivery of a notification is not acknowledgment. The escalation steps are:
1. openChart SHALL alert the on-call clinician for the hour at once, and make that clinician the owner.
2. When the on-call clinician does not acknowledge within the next escalation interval, or no on-call clinician is rostered, openChart SHALL alert the medical director and make the medical director the owner.
3. After the last step, openChart SHALL keep re-alerting the medical director at each escalation interval until a clinician acknowledges.

Until a response policy is approved, each escalation interval SHALL equal the item's acknowledgment window (`ack_by` minus `routed_at`). An item that arrives at or after its `ack_by` SHALL escalate at once (design call MD-2). Escalation SHALL NOT drop, park or close an item, SHALL NOT depend on any agent, and SHALL run whatever the item's identity state (MI-18). A non-urgent item that has no acknowledgment by its deadline SHALL move to its lane's cover for the hour.

An item whose clock has expired SHALL stay in the queue, open and owned, until a clinician replies or records a closing outcome. openChart SHALL let any clinician authorized for the inbox find an open item by its routing id (`handoff_id`) and see it. That includes the on-call clinician named in openPractice's tracked alert (ER-07 and ER-09 in the openPractice change).

#### Scenario: Failure: the owner does not acknowledge an urgent item
- **WHEN** an `urgent` item's acknowledgment deadline passes with no acknowledgment by its owner
- **THEN** the on-call clinician is alerted at once and becomes the owner

#### Scenario: Failure: the on-call clinician does not acknowledge
- **WHEN** the on-call clinician does not acknowledge within the next escalation interval
- **THEN** the medical director is alerted and becomes the owner

#### Scenario: Failure: nobody acknowledges
- **WHEN** no clinician acknowledges an `urgent` item after the medical director is alerted
- **THEN** openChart keeps re-alerting the medical director, reports `clock_expired` at the effective response deadline, and the item stays owned

#### Scenario: Failure: openPractice's on-call alert names an expired item
- **WHEN** the on-call clinician who receives openPractice's tracked alert for an expired item looks it up in openChart by its routing id
- **THEN** openChart shows the item, which is still queued, open and owned

### Requirement: MI-10 openChart never lowers urgency
openChart MUST NOT lower an item's urgency by any path. No user, role, agent, policy or message may lower it.

On `handoff.urgency_raised`, openChart SHALL set the item's urgency to the higher of its current urgency and the raised one. It SHALL move each deadline only earlier, to the earlier of the current and the offered time, and SHALL answer `message.ack` `received`. A raise that would not increase urgency SHALL be recorded and SHALL change nothing. A raise for a `handoff_id` that has not yet been received SHALL be recorded and applied when its offer arrives.

A clinician MAY raise an item's urgency inside openChart, which tightens its deadlines. Under contract 1.0 no message reports that raise to openPractice, whose shadow deadline stays later (design call MD-8). A raise to `urgent` on an item already `responded` or closed SHALL reopen it inside openChart, to its last owner or to cover, under MI-09 (design call MD-9).

#### Scenario: Failure: a clinician tries to lower urgency
- **WHEN** a clinician tries to change an `urgent` item to `routine`
- **THEN** the change is refused and the item stays `urgent`

#### Scenario: Failure: a late raise would extend a deadline
- **WHEN** a raise arrives whose new `respond_by` is later than the item's current effective response deadline
- **THEN** the urgency rises and the current, earlier deadline is kept

#### Scenario: Failure: a raise arrives before its offer
- **WHEN** a `handoff.urgency_raised` arrives for a `handoff_id` openChart has not yet received
- **THEN** openChart records it, answers `message.ack` `received`, and applies the raise when the offer arrives

### Requirement: MI-11 The clinician's reply goes to the patient through HealthLinc
openChart SHALL send the clinician's reply to the patient through HealthLinc, against the offer's `reply_path_ref`, over openChart's own HealthLinc integration. It SHALL never send the reply through openPractice (ER-05 in the openPractice change). This holds whichever system holds the conversation, as openPractice ER-05 also states (design call MD-16). Only the item's owner, or a named clinician or nurse whom the lane policy allows, SHALL send a reply. Each reply SHALL carry the sender's identity and the author type `clinician` (MI-12).

openChart SHALL report `responded` only after HealthLinc accepts the reply for delivery. When HealthLinc refuses the reply or cannot be reached, openChart SHALL keep the reply, retry with the same message identifier, keep the item open and owned, and show the owner the failure. The clock SHALL keep running.

#### Scenario: A reply is accepted
- **WHEN** a clinician sends a reply and HealthLinc accepts it for delivery
- **THEN** openChart records the reply and reports `responded`

#### Scenario: Failure: HealthLinc refuses the reply
- **WHEN** HealthLinc refuses a reply with a coded reason
- **THEN** the item stays open and owned, openChart does not report `responded`, and the owner sees the coded reason

### Requirement: MI-12 A clinical communication is recorded with its author type and provenance, and is never a diagnosis or a clinical fact of record
openChart SHALL record every inbox item as one clinical communication record. This requirement is the single definition of that record in openChart. Other openChart changes reference it rather than defining a second record; that includes `define-ai-authored-clinical-records` (ruling 64).

**Author type.** Every piece of content in a clinical communication SHALL carry exactly one author type:
- `patient`, for the patient. Content from the patient's representative carries `representative`, and is treated like `patient` content under every rule in this capability.
- `ai`, for any AI or agent. The provenance SHALL name the source system: HealthLinc's coach, which gives general health information only, with a not-medical-advice statement (rulings 51 and 54); or medXfactory's medical AI (ruling 51). Category and urgency proposals from either are `ai` content (ruling 51, amending ruling 44).
- `clinician`, for a named physician or nurse acting through an authenticated openChart session.
- `staff` or `system`, for content from practice staff, or from a system rather than a person.
- `unknown`, a fail-safe for content whose author type the source system does not report. `unknown` content SHALL never be treated, shown or delivered as clinician-authored.

**Provenance.** The record SHALL hold:
- the handoff references: `handoff_id`, `link_id`, `healthlinc_message_ref`, `conversation_source`, `conversation_ref`, `reply_path_ref`, the origin and any split-group reference;
- every urgency change with its source, every owner change, every clock event, every acknowledgment, every status sent and every clinical-need marker sent (MI-25);
- for a conversation HealthLinc holds, the escalated exchange as retrieved, each turn with its author type, source system, time, reference and retrieval time;
- for a conversation medXfactory holds, only the `conversation_ref`, the author type `ai` with medXfactory's medical AI named as the source, and the retrieval provenance, with no copy of the exchange (MI-24);
- every reply, with the named clinician who sent it, its time and HealthLinc's acceptance.

**Not a fact of record.** A clinical communication SHALL NOT be a diagnosis, problem, order, prescription, encounter, intake statement or other clinical fact of record, whoever wrote it. Nothing in it SHALL become one through this capability. Only a separately governed clinical workflow may record such a fact (MI-14, MI-26).

A recorded communication MUST NOT be silently overwritten or deleted. A correction SHALL create a new version that references its predecessor, with actor, reason and time. This is consistent with the ratified rule that amendments preserve accepted history. The record SHALL be filed to an `OC Patient` only when MI-17 resolves the patient; otherwise it stays unfiled under MI-18. The storage shape SHALL be decided in planning.

#### Scenario: A patient's message is recorded
- **WHEN** HealthLinc returns a conversation turn that the patient wrote
- **THEN** the record holds it with author type `patient`, HealthLinc as the source system, its reference and its times, and it is not a clinical fact of record

#### Scenario: A coach turn is recorded
- **WHEN** HealthLinc returns a conversation turn that its coach wrote
- **THEN** the record holds it with author type `ai`, and names HealthLinc's coach as the source system

#### Scenario: A medical-AI exchange is referenced
- **WHEN** medXfactory holds an item's conversation
- **THEN** the record holds the `conversation_ref`, the author type `ai` with medXfactory's medical AI named as the source, and the retrieval provenance, with no copy of the exchange

#### Scenario: A clinician's reply is recorded
- **WHEN** a named physician sends a reply and HealthLinc accepts it
- **THEN** the record holds it with author type `clinician`, the physician's identity, the time and HealthLinc's acceptance

#### Scenario: Failure: a turn arrives with no author type
- **WHEN** a source system returns a conversation turn without an author type
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
openChart SHALL keep AI-authored content distinguishable from clinician-authored content wherever it records, shows or delivers that content. It SHALL do so with the author types and source systems of the clinical communication record (MI-12). AI-authored content, and content of `unknown` authorship, MUST NOT be recorded, shown or delivered as clinician-authored. Only a named clinician's authenticated session can create `clinician` content. This change grants no AI drafting of clinical replies (design call MD-10). Any AI assistance in the inbox needs a separately governed change.

#### Scenario: Failure: medical-AI content could pass as a doctor's
- **WHEN** an item shows a turn written by medXfactory's medical AI
- **THEN** the turn is labelled AI-authored, with medXfactory's medical AI named as its source, and is never shown as clinician-authored

#### Scenario: Failure: an automated process tries to send a clinician reply
- **WHEN** an automated process tries to send a reply with author type `clinician`, without a named clinician's authenticated session
- **THEN** the reply is refused and nothing is sent

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
A clinician or nurse who finds that an item is administrative SHALL return it to openPractice with `handoff.status` `returned_not_clinical`, and SHALL NOT answer it (ruling 44; ER-12 in the openPractice change). After the return, openChart SHALL refuse any reply on that item. The item SHALL leave the clinical queue with outcome `returned_not_clinical`, and its record is kept under MI-12. openChart SHALL NOT keep an administrative work queue, administrative lanes or tools for answering administrative questions.

#### Scenario: A clinician returns a billing question
- **WHEN** a nurse finds that a routed item asks only about a statement balance
- **THEN** openChart sends `returned_not_clinical`, the item leaves the clinical queue, and no reply is sent

#### Scenario: Failure: someone replies to a returned item
- **WHEN** a clinician tries to reply to an item already returned as `returned_not_clinical`
- **THEN** the reply is refused

### Requirement: MI-16 Mixed questions are split, and only the clinical part is answered in openChart
When an item mixes clinical and administrative questions, the clinician SHALL answer only the clinical part. openChart SHALL ask HealthLinc to split the item and resubmit only the administrative part to openPractice as a new inquiry (design call MD-7; ruling 44). openChart MUST NOT send `returned_not_clinical` for a mixed item, MUST NOT send administrative text to openPractice, and MUST NOT lower urgency on a split. The item SHALL stay open and owned until HealthLinc acknowledges the split request. Until then, openChart SHALL retry the request and show the owner a coded exception.

#### Scenario: A mixed question is split
- **WHEN** a routed item asks about a symptom and about a bill, and HealthLinc acknowledges the split request
- **THEN** the clinician answers only the symptom question, openChart reports `responded` once HealthLinc accepts the reply, and the bill question reaches openPractice only through HealthLinc

#### Scenario: Failure: HealthLinc does not acknowledge the split
- **WHEN** HealthLinc does not acknowledge a split request
- **THEN** the item stays open and owned, openChart retries and shows a coded exception, and it does not send `returned_not_clinical`

### Requirement: MI-17 A handoff resolves the patient only through the links that exist
openChart SHALL resolve the patient for an offer only through the links that exist, because there is no master patient identity across HealthLinc, openPractice and openChart (ruling 39). Those links are:
- the `openpractice` `OC Patient External Identifier` row whose provenance names the offer's `link_id` (PL-02). The row SHALL be `active` and SHALL belong to the `OC Patient` that the offer's `ehr_patient` triple names under openChart's own issuer (PL-03);
- where one exists, the openChart patient reference that HealthLinc reports for the account behind the message (MI-03). It SHALL name the same `OC Patient`.

openChart MUST NOT match on names, dates of birth or other demographics. It MUST NOT resolve a handoff through any other namespace or system, including a Medx or medXfactory reference, even when medXfactory holds the conversation (design call MD-19). It MUST NOT create, change, merge or re-point a link or a patient while handling a handoff (PL-01, PL-05, PL-06).

#### Scenario: Every link agrees
- **WHEN** the offer's `link_id` names an `active` row for the `OC Patient` its `ehr_patient` triple names, and HealthLinc reports the same patient
- **THEN** the item is filed to that `OC Patient`

#### Scenario: Failure: HealthLinc reports a different patient
- **WHEN** HealthLinc reports an openChart patient reference that differs from the `OC Patient` the `openpractice` link names
- **THEN** the item stays unfiled, an identity review opens, and no link or patient record changes

### Requirement: MI-18 Unresolved or conflicting identity goes to identity review, and an urgent item still reaches a clinician
When MI-17 does not resolve exactly one patient, openChart SHALL handle the item by its urgency. The cases are: an unknown link; a revoked or superseded link; a link in `identity_review`, including a date-of-birth hold under PL-08; an `ehr_patient` triple that does not match the link; or a HealthLinc reference that disagrees.

- **`routine` or `priority` offers.** openChart SHALL reject the offer with the schema's code, as the openPractice change expects: `link_unknown` for an unknown link; `link_revoked` for a revoked or superseded link; `link_in_review` for a link in review; and `ehr_patient_mismatch` for a triple that does not match. openPractice then owns the exception (ER-06 and ER-07 in the openPractice change).
- **`urgent` offers.** openChart SHALL accept the offer into an unfiled item, show the identity uncertainty to everyone who views it, route it under MI-07 and MI-09, and open an identity review (design call MD-5). An urgent item MUST NOT be rejected, dropped or parked because of its identity.

An unfiled item SHALL NOT be filed to any `OC Patient` until MI-17 resolves the patient (design call MD-6). Meanwhile, its content MAY be read and answered through HealthLinc's reply path. When an identity problem is found after acceptance, the item SHALL stay accepted and become unfiled, whatever its urgency. Identity review SHALL follow PL-06 and PL-08, and MUST NOT merge, overwrite or delete records. For urgent offers only, this departs from the list of companion items in the openPractice change; tension MT-1 records the departure.

#### Scenario: Failure: an urgent offer arrives on a link in review
- **WHEN** an `urgent` offer names a link that openChart holds in `identity_review`
- **THEN** openChart accepts it into an unfiled item that shows the identity uncertainty, the escalation of MI-09 runs, and an identity review opens

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
openChart SHALL operate fully with no openPractice deployment and no HealthLinc integration, as the ratified `expanded-patient-intake` rule and PL-15 require. This requirement restates those rules and does not weaken them. The inbox is optional. With no openPractice gateway configured, the inbox SHALL accept no handoff, and no other openChart operation SHALL depend on it.

The inbox SHALL NOT be enabled until all of these are configured:
- an openPractice integration identity;
- conversation retrieval from HealthLinc, and from medXfactory where the practice uses medXfactory's medical AI (design call MD-12);
- HealthLinc reply delivery and split requests;
- full cover under MI-08.

Disabling the inbox SHALL withdraw the integration's authorization for handoffs, so later offers are refused with `unauthorized`. Every open item SHALL stay owned until it closes. Apart from medXfactory's governed chart path for medical-AI exchanges (ruling 53, MI-24), this change defines no route by which a patient's message reaches openChart without passing through openPractice (design call MD-12).

#### Scenario: Standalone installation
- **WHEN** openChart is installed on a clean supported site with no openPractice and no HealthLinc
- **THEN** migrations complete, the golden-patient intake tests pass, and the inbox is not configured

#### Scenario: Failure: an offer reaches a site with no gateway
- **WHEN** a `handoff.offer` reaches an openChart site with no openPractice gateway configured
- **THEN** openChart refuses it as `unauthorized`, stores nothing, and every other operation is unaffected

#### Scenario: Failure: the inbox is enabled without cover
- **WHEN** an administrator tries to enable the inbox while an hour has no on-call clinician and no medical director fallback is named
- **THEN** the enablement is refused

### Requirement: MI-21 No PHI in logs, errors, notifications, diagnostics or keys
openChart's logs, errors, diagnostics, clinician notifications and idempotency keys, and every coded reason it sends, MUST NOT contain names, dates of birth, contact details, patient identifier values, message or reply text, or other clinical content (PL-13; ER-16 in the openPractice change). Diagnostics SHALL reference items only by `handoff_id`, `message_id` and `link_id`. A clinician notification on any device SHALL say only that an item awaits, with its urgency, a coded cause and an opaque item reference. Opening the item SHALL require an authenticated openChart session.

#### Scenario: Failure: an urgent item is overdue
- **WHEN** openChart alerts the on-call clinician that an `urgent` item is unacknowledged
- **THEN** the notification carries only the urgency, the cause `urgent_ack_overdue` and an opaque item reference

#### Scenario: Failure: a retrieval fails
- **WHEN** a retrieval from a source system fails
- **THEN** the log entry holds the `handoff_id`, the `message_id` and a coded reason, and no content or patient detail

### Requirement: MI-22 Replies honor confidential-communication instructions
openChart SHALL apply PL-16 to every reply it sends through HealthLinc, including any notification HealthLinc sends for that reply, because the reply is a patient communication that openChart originates (ruling 27). openChart SHALL give HealthLinc the applicable restrictions as codes with the reply, and SHALL NOT send through a channel they restrict.

An unfiled item's instructions cannot be determined. For such an item, openChart SHALL deliver the reply only within the HealthLinc conversation that carried the message, and SHALL mark every other channel restricted (design call MD-13). When PL-16 withholds a reply, the item SHALL stay open and owned and SHALL NOT be reported `responded`. The owner SHALL be shown the coded reason, so they can reach the patient through a permitted channel. Withholding SHALL never close an item. This requirement does not weaken PL-16.

#### Scenario: Failure: the patient refuses text messages
- **WHEN** a clinician replies to a linked patient whose applied instructions carry `no_text_messages`
- **THEN** openChart gives HealthLinc that restriction with the reply, and no text message is sent for it

#### Scenario: Failure: no permitted channel remains
- **WHEN** PL-16 leaves no permitted channel for a reply
- **THEN** the reply is withheld, the item stays open and owned, openChart does not report `responded`, and the owner sees the coded reason

### Requirement: MI-23 The inbox boundary is covered by contract tests
The inbox SHALL be covered by contract tests, written first, that validate every handoff message against the schema at the digest recorded in MI-02. The tests SHALL run against an openPractice double and a double for each conversation source system, HealthLinc and medXfactory, with synthetic data only. They SHALL cover:
- refusal of content fields and of unknown fields;
- `conversation_source` and `conversation_ref`, including a namespace that does not match the source;
- every author type of MI-12 and its source-system provenance, including `unknown`, and medical-AI content never filed through the inbox;
- AI-authored orders, prescriptions and diagnoses held as communication, with no clinical act created (MI-26);
- `clinical_need.marker`: mark and withdraw under one `need_id`, the `valid_until` and `origin` rules, `related_handoff_id` for `urgent_escalation`, and the handling of `origin_not_verified`;
- acknowledgment, rejection, replay and duplicate offers;
- every status code, including `clock_expired` sent the moment the clock runs out and `responded` sent as soon as HealthLinc accepts a reply;
- an expired item kept in the queue and found by its routing id;
- urgency raises, and the absence of any lowering;
- deadlines that never extend;
- every identity case in MI-18;
- escalation to the on-call clinician and to the medical director;
- reply delivery, refusal and withholding;
- re-routing and splitting;
- the absence of financial fields;
- no PHI in logs, notifications or keys.

The standalone golden-intake tests SHALL pass with the inbox unconfigured.

#### Scenario: CI runs the inbox suite
- **WHEN** CI runs the inbox contract tests
- **THEN** they pass against the openPractice and source-system doubles with synthetic data only

#### Scenario: Failure: a test adds a content field
- **WHEN** a test builds a `handoff.offer` that carries message text
- **THEN** schema validation fails, and the test expects that failure

### Requirement: MI-24 A medical-AI exchange reaches the chart only through medXfactory's own governed path
medXfactory's medical-AI exchanges with a patient SHALL be recorded in the chart only through medXfactory's own governed path into MedxEHR and openChart. They SHALL never pass through openPractice, which holds no clinical content (ruling 53).

When medXfactory holds an inbox item's conversation, openChart SHALL retrieve it by its `conversation_ref` for the clinician (MI-03). It SHALL record in the item only what MI-12 states for a conversation medXfactory holds: the reference, the author type and source, and the retrieval provenance. It SHALL NOT file a copy of the exchange to an `OC Patient` through the inbox (design call MD-17). openChart MUST NOT accept medical-AI content from openPractice. This change does not define openChart's receiving side of medXfactory's governed path (Open Question 4).

#### Scenario: A clinician answers an escalated medical-AI conversation
- **WHEN** a clinician answers an item whose conversation medXfactory holds
- **THEN** openChart records the reply as clinician-authored, and the item records the medical-AI exchange by reference and source only

#### Scenario: Failure: medical-AI content arrives from openPractice
- **WHEN** a handoff message from openPractice carries the text of a medical-AI exchange
- **THEN** openChart answers `rejected` with reason `schema_invalid` and stores nothing

#### Scenario: Failure: someone files the medical-AI exchange from the inbox
- **WHEN** a user tries to file a medXfactory-held exchange to an `OC Patient` from an inbox item
- **THEN** the filing is refused, and the item keeps its reference

### Requirement: MI-25 A clinician's clinical-need marker is recorded in openChart and sent to openPractice as `clinical_need.marker`
openChart SHALL let a named clinician record, and later withdraw, a clinical-need marker for a patient with an `active` `openpractice` link (ruling 50; ER-18 in the openPractice change). The kinds are:
- `messaging_continuity`, which keeps the patient's clinical messaging and medical-AI consults open for continuity of care, for example after a lapsed membership or a deactivation;
- `appointment_needed`, which records that an appointment is clinically needed, so that a payment hold never blocks it.

openChart SHALL attribute each marker to the clinician and record it. It SHALL send each mark and each withdrawal to openPractice as `clinical_need.marker`, on the patient's EB-01 `link_id`, with:
- a `need_id` that openChart mints for the marker and reuses for its withdrawal;
- the `action`, `mark` or `withdraw`, and the `kind`;
- `marked_by`, openChart's opaque reference to the clinician, never derived from the clinician's name or login;
- `marked_at`;
- for `mark` only, a `valid_until` time that the clinician sets, and an `origin` (design call MD-18);
- no reason, note or other clinical content (MI-21).

The origin SHALL be `clinician_judgment`, with one exception. A clinician who records the marker from an inbox item whose urgency is `urgent`, as openPractice offered or raised it, MAY give the origin `urgent_escalation`. In that case `related_handoff_id` SHALL be that item's `handoff_id`. A withdrawal SHALL carry none of `valid_until`, `origin` or `related_handoff_id`.

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

#### Scenario: Failure: the link is not active
- **WHEN** a clinician tries to record a marker for a patient whose `openpractice` link is in `identity_review`
- **THEN** the marker is refused with a coded reason, and the clinician sees that reason

### Requirement: MI-26 AI-authored content is communication only until `define-ai-authored-clinical-records` is ratified
openChart SHALL treat all AI-authored content that reaches the chart as communication only, by any path, until openChart-spec change `define-ai-authored-clinical-records` is ratified. That change is being drafted (ruling 64). The paths include inbox retrieval and medXfactory's governed chart path (ruling 53). This change does not cover AI-authored orders, prescriptions or diagnoses.

The practice's medical director sets medXfactory's AI to one of three modes: advice only, full practice or limited practice (ruling 59). medXfactory's change `define-patient-medical-ai-connection` owns the mode framework and its gates (rulings 56 to 58). Ruling 59 stands, so this requirement fails closed.

Until `define-ai-authored-clinical-records` is ratified, these rules apply:
- openChart MUST NOT record, act on or present AI-authored content as an order, prescription or diagnosis, whatever mode, configuration or authority the content claims.
- The content SHALL stay distinguishable from clinician-authored content, with its author type `ai` and its source system named (MI-12, MI-13).
- Content that presents itself as an AI-authored order, prescription or diagnosis SHALL be held as AI-authored communication, marked by code as not accepted as a clinical act (design call MD-20). It SHALL NOT create an order, prescription, diagnosis or other clinical fact.
- When such content appears in an inbox item, the owner SHALL see it labelled that way.
- The limited-practice and full-practice modes SHALL NOT be built in openChart.

#### Scenario: Failure: an AI-authored prescription reaches openChart
- **WHEN** content from medXfactory's medical AI that presents itself as a prescription, and claims full-practice authority, reaches openChart
- **THEN** openChart holds it as AI-authored communication, names medXfactory's medical AI as its source, marks it as not accepted as a clinical act, and creates no prescription, order or diagnosis

#### Scenario: Failure: an AI-authored diagnosis appears in an inbox item
- **WHEN** a retrieved conversation in an inbox item contains an AI turn stating a diagnosis
- **THEN** the owner sees the turn labelled as AI-authored communication that was not accepted as a clinical act, and no condition or diagnosis is recorded

#### Scenario: Failure: a plan proposes building a practice mode
- **WHEN** a plan proposes building limited-practice or full-practice mode in openChart before `define-ai-authored-clinical-records` is ratified
- **THEN** the plan is out of scope, and the work waits for that change
