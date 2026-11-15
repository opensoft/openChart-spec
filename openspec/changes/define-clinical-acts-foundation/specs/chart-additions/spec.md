## ADDED Requirements

### Requirement: AN-01 Any identified human or system may add to a patient's chart, and an addition the chart cannot identify is refused with nothing stored
Any human or system SHALL be able to add to a patient's chart: a clinician, other staff, the patient, an AI, a device or another system (owner ruling 80, clause 1). An addition is anything written into a patient's chart through any path: an act, a note, a message, a consult record, a reading, an imported record or a recommendation. openChart SHALL add nothing unless it can identify the writer, the human or system that writes the addition into the chart, as AN-02 states. An addition whose writer it cannot identify SHALL be refused, and nothing SHALL be stored (clause 2). Every addition SHALL arrive through the versioned service boundary (CA-10).

Practice configuration is not an addition to a patient's chart: grants, attestations, designations, act-type registry entries and system and device registrations. Their own refusals stay (design call CD-49, PROPOSED).

#### Scenario: A registered system adds a summary
- **WHEN** a registered integration identity adds a document summary for a patient, naming itself and its operator
- **THEN** openChart stores the summary as information, with the integration identity as its writer

#### Scenario: Failure: an unidentified caller adds to the chart
- **WHEN** a caller that the chart cannot identify as a named account, a verified patient link, a registered system or a registered device submits a note for a patient
- **THEN** openChart refuses it, and nothing is stored

### Requirement: AN-02 Each kind of writer is identified in its own recorded way
Every party an addition names, its writer and every party on whose behalf it was written, SHALL be identified by `kind` as below (owner ruling 80, part B and clause 2; owner ruling 151):

| `kind` | Identified by |
|---|---|
| `human` | the person's own named account in the chart (`account_ref`). For a clinician, also their clinical role and the licence attestation on record (AU-03). A practitioner who signs off a decision is also identified by their `openwallet_id` (CA-04) |
| `patient` | the verified link the patient or their representative comes through (`patient_link_ref`). A representative is named as such (`acting_as`) |
| `ai` | its `openwallet_id`, plus the `model` and `model_version` that produced the content |
| `device` | its `make`, `model` and `serial`, or a `device_id` the chart can resolve to them, with its `device_id_kind`: `udi` or `asset_tag` |
| `system` | its registered integration identity (`system_id`) and who operates it (`operator_ref`) |

Each party SHALL also carry its `identity_basis` (design call CD-42, PROPOSED). It is `verified_by_chart` when openChart itself authenticated the identity. It is `asserted_by` when an identified system vouched for it, and then names that system. The writer's identity SHALL always be `verified_by_chart`.

When a system delivers an AI's addition, the system is the writer and the AI is named as the party on whose behalf it wrote. The AI's `openwallet_id` SHALL be carried on every addition it makes, and openChart SHALL check it against the registration of the system that delivers it (AN-03). A wallet identifier SHALL NOT become the identifier of a person or a patient: openChart resolves people by their own account and patients by the openChart patient triple. This keeps openWallet's ratified rule that a wallet reference is attestation, not identity.

#### Scenario: A relay delivers an AI's consult record
- **WHEN** a registered relay delivers a consult record written by an AI that carries its openWallet ID, model and model version
- **THEN** openChart records the relay as the writer, verified by the chart, and the AI as the party on whose behalf it wrote, asserted by the relay. It also checks the AI's openWallet ID against the relay's registration

#### Scenario: Failure: an AI addition without its openWallet ID
- **WHEN** a relay delivers an AI's addition that names no openWallet ID for the AI
- **THEN** openChart cannot identify the AI, refuses the addition, and stores nothing

### Requirement: AN-03 Every system and device is registered with the practice before it adds, and the practice can suspend any of them at once
openChart SHALL let a system or device add to a chart only after it is registered with the practice (owner ruling 80, clause 3). A registration SHALL record the writer's `kind` and identity (AN-02), its operator, the practice user who registered it and when, and for a system that delivers an AI's additions, the AI `openwallet_id` values it may deliver for. The practice SHALL be able to suspend any registered system or device at once. Every later addition by a suspended writer SHALL be refused and nothing stored, until the suspension is lifted (clause 18). Registrations and suspensions SHALL be audited, and no registration SHALL be deleted. The administrative role named in planning SHALL register systems and devices. The same role or the medical director SHALL suspend them (design call CD-43, PROPOSED). A registration confers no decision authority (AN-07).

#### Scenario: A device is registered
- **WHEN** an administrator registers a home monitor by its make, model and serial number, naming its operator
- **THEN** openChart records the registration with the administrator and the time, and the monitor gains no decision authority

#### Scenario: Failure: a suspended system adds to a chart
- **WHEN** the medical director suspends an integration identity, and a minute later it submits an observation for a patient
- **THEN** openChart refuses the observation and stores nothing

### Requirement: AN-04 Every addition records when it was received, when the information arose, where it came from, what added it and on whose behalf
Every addition SHALL carry its provenance (owner ruling 80, clauses 4 to 7):
- `received_at`: the chart's own clock when it received the addition;
- `occurred_at`: when the information itself arose, where that differs, such as when a reading was taken or a conversation held;
- `source`: where the information came from, as a `kind` (`patient_statement`, `device_reading`, `ai_consult`, `clinician_observation`, `external_record` or `chart_entry`) and a reference to it;
- `added_by`: the writer, identified as AN-02 states;
- `on_behalf_of`: when a system adds something for another system or a human, every party it was added for and every hand it passed through, in order from the originator to the writer.

openChart SHALL set `received_at` itself and SHALL NOT take it from the writer.

#### Scenario: An integration forwards another organization's record
- **WHEN** a registered integration delivers a discharge summary that another organization's system produced for a clinician there
- **THEN** the addition records the integration as writer, the other organization's system and its clinician on whose behalf it was added, source kind `external_record` with its reference, `received_at` from openChart's clock and `occurred_at` from the record

#### Scenario: Failure: a writer supplies its own receipt time
- **WHEN** a writer submits an addition carrying a `received_at` in the past
- **THEN** openChart records its own receipt time as `received_at`, and keeps the writer's time only as `occurred_at` where the source supports it

### Requirement: AN-05 The record of an addition is permanent and readable by anyone who can read the chart; a correction is a new addition that points to the old one
The provenance and content of every addition SHALL be permanent and visible to anyone who can read the patient's chart (owner ruling 80, clause 8). Nothing in it SHALL be edited or deleted through any supported path. A correction SHALL be a new, dated addition that points to the addition it corrects (`corrects`), and the corrected addition SHALL stay readable. For an act, CA-05 and CA-06 are how a correction is made.

#### Scenario: A wrong reading is corrected
- **WHEN** a registered system corrects a reading it added an hour earlier
- **THEN** openChart stores the correction as a new addition pointing to the first, and both stay readable

#### Scenario: Failure: someone edits an addition's provenance
- **WHEN** a user or extension tries to change the `added_by` of a stored addition
- **THEN** openChart refuses the change, and the addition is unchanged

### Requirement: AN-06 Every addition is information or a decision; the act-type registry is the list of decisions, and the class a writer claims never decides whether an addition takes effect
Every addition SHALL be either information or a decision (owner ruling 80, clause 9). Information is an observation, a reading, a statement, a message, a summary or a recommendation. A decision changes the patient's care or what the chart holds as established. The chart's list of what counts as a decision SHALL be the act-type registry (CA-09). An addition is a decision when it holds act content of an act type in that registry, or when it signs off an act: a signature, a new signed version, a co-signature, a completion, a discontinuation or an entered-in-error mark. Everything else is information. A draft revision is not a decision (design call CD-44, PROPOSED).

A writer MAY declare a class on an addition. openChart SHALL determine the class itself from the registry, SHALL record the class it determined, and SHALL keep a declared class that differs as the writer's declaration only. The class a writer claims SHALL never decide whether an addition takes effect. Act content declared as information is still a decision, so it takes effect only under AN-07. A declared decision that is not in the registry is information. Information needs only the identification of AN-01 to AN-04 (clause 10).

#### Scenario: A clinician's observation is information
- **WHEN** a nurse adds a free-text observation to a patient's chart
- **THEN** openChart stores it as information, identified and with its provenance, and no authority is checked

#### Scenario: Failure: an order is declared as information
- **WHEN** a registered system submits order content and declares it `information`
- **THEN** openChart determines that it is a decision, keeps the declaration as the writer's only, and applies AN-07, so the order does not take effect

### Requirement: AN-07 A decision counts as a decision only when its decision maker held the authority at that moment and a practitioner signed it off; the authority relied on is recorded
A decision SHALL count as a decision only when its decision maker held the practice authority for that kind of decision at that moment (owner ruling 80, clause 11), and a practitioner signed it off in their own logged-in session with their openWallet and openSig (owner ruling 151; CA-04). openChart SHALL check that authority at the moment of the action (AU-04) and SHALL record the authority each decision rested on:
- for a human, their licence and what the medical director has granted them: the licence verification in their openWallet relied on at sign-off (CA-04), the practice-supplied attestations under the grant (AU-03) and the grant version (AU-02);
- for an AI, the mode and scope the medical director has approved for it, of which none can be switched on today (AN-12);
- a device or a plain integration holds none.

A decision without that authority SHALL be entered as a recommendation (AN-09). It SHALL NOT be refused for that reason (clause 18).

#### Scenario: An authorized clinician signs a diagnosis
- **WHEN** a clinician with a diagnosis grant in force signs off a diagnosis in their own session, and every check of CA-04 passes
- **THEN** the diagnosis counts as a decision, and the record names the grant version and the sign-off evidence it rested on

#### Scenario: Failure: a device submits a diagnosis
- **WHEN** a registered device submits content shaped as a diagnosis of record
- **THEN** openChart enters it as a recommendation marked not an authorized decision, because a device holds no decision authority, and no diagnosis exists

### Requirement: AN-08 A decision added on someone's behalf counts as theirs only with their own sign-off in the chart; otherwise it is the carrying system's recommendation
When a system adds a decision on someone's behalf, openChart SHALL judge authority on the decision maker, never on the system that carried it (owner ruling 80, clause 12). The decision SHALL count as the decision maker's only when it carries that practitioner's own sign-off, made in the chart as CA-04 states (owner ruling 151). Under ruling 151, nothing else is "an approval of theirs it can check". Otherwise openChart SHALL enter it as the carrying system's recommendation (AN-09). The recommendation names the carrying system as its decision maker, keeps the party it claimed as the claimed decision maker, and records `decision_maker_not_confirmed`.

#### Scenario: A clinician later signs off a carried order
- **WHEN** an integration delivers an order on a clinician's behalf, and the clinician then adopts it in their own session with their openWallet and openSig
- **THEN** a new order of the clinician's own takes effect, pointing back to the recommendation that the delivery created

#### Scenario: Failure: a system claims a clinician ordered something
- **WHEN** an integration delivers an order stating that a named clinician made it, with no sign-off by that clinician in the chart
- **THEN** openChart enters it as the integration's recommendation marked not an authorized decision, with `decision_maker_not_confirmed`, names the clinician only as the claimed decision maker, and no order takes effect

### Requirement: AN-09 A decision made without authority is entered in full as a recommendation, marked not an authorized decision, with no effect
A decision made without authority SHALL still be entered in the chart, in full, as a recommendation and not a decision (owner ruling 80, clause 13). The recommendation record SHALL hold:
- the proposed act's class, type and action;
- its content, in one of three forms: validated under `openchart-clinical-act-content` (CA-01); or exactly as given, when the writing path declared it under another schema, such as the AI write contract's own, with `content_schema` naming the schema it was declared under (its identifier, version and SHA-256); or, for an action on an existing act, that act's version and the action;
- the same identification and provenance (AN-02, AN-04);
- the marker `not_authorized_decision`;
- each coded `missing_authority` reason, from this closed list that every reader uses (design call CD-45, PROPOSED). Several may apply at once:
  - `no_grant_in_force`: the decision maker holds no grant in force for this action, act class and act type. For a human that is AU-02; for an AI it is the mode and scope the medical director approved, with their conditions;
  - `no_decision_authority`: no decision maker of this kind can hold authority for this decision now. That covers an AI today (AN-12), a patient, a device or a plain integration, an act reserved to a human clinician, the management of an emergency, an AI's action on a clinician-authored record, and an act class or type this chart does not define;
  - `decision_maker_not_confirmed`: it was added on someone's behalf without that person's own confirmed sign-off (AN-08);
  - `no_practitioner_sign_off`: no practitioner signed it off under CA-04;
  - `wallet_not_bound`: the signer's account is not bound to the `openwallet_id` that signed;
  - `licence_verification_missing`: the wallet holds no current licence verification that covers this decision;
  - `attestation_not_verified`: the openSig attestation did not verify against the wallet over the content and provenance digests;
  - `signing_service_unavailable`: openWallet or openSig could not be reached;
  - `practice_attestation_not_in_force`: the practice-supplied licensure or prescriber attestation that the grant rests on is not in force (AU-03);
- optionally, the writing path's own coded reason, `path_reason`: the scheme that defines the code, the scheme's version and the code (design call CD-51, PROPOSED). A path that fails on finer reasons of its own maps each of its codes to one or more codes of the closed list, records those in `missing_authority`, and keeps its own code in `path_reason` for the source and the reviewer. `path_reason` never replaces `missing_authority`. It is shown to the reviewer beside it, and it decides nothing.

A safety gate is never a missing-authority reason: the list names only which authority was missing (owner ruling 80, clauses 13 and 14). A recommendation is not gated. The prescribing-safety gate applies to the practitioner's own decision when they adopt the recommendation (AN-11, RX-02). A writing path that stops at a gate check of its own SHALL record in `missing_authority` the authority codes that are true of the entry, such as `no_practitioner_sign_off`, and SHALL keep its gate code in `path_reason` only.

Content stored as given is kept for the source and the reviewer. This contract does not validate it, and nothing reads it as an act's content. An act class this contract does not define is kept, as declared, only with such content. A clinician who adopts the recommendation creates a new act whose content is validated under CA-01 (AN-11).

Wherever a recommendation is shown, to a clinician or a patient, it SHALL be clearly marked "not an authorized decision" and SHALL say which authority was missing.

A recommendation SHALL have no effect (clause 14). It is never an act of record. It has no act status and cannot be signed, released, transmitted or published. It is never a billable fact. It never counts as an active diagnosis, procedure, order or prescription, or as a signature, co-signature or release, and it never satisfies a check or removes a warning that a decision would. Nothing is ordered, prescribed, sent, billed or treated as established because of it. The same SHALL apply to a human as to a system (clause 17).

#### Scenario: A nurse's unauthorized order is kept
- **WHEN** a nurse without order `sign` scope submits a laboratory order as final
- **THEN** openChart enters it in full as a recommendation marked "not an authorized decision", with `no_grant_in_force`, and no order exists or is released

#### Scenario: An AI's act content is kept as given, with the path's own reason
- **WHEN** a relay delivers an AI's order whose content was declared under the AI write contract's own schema, and the AI write path records it with a code of its own for the check that failed
- **THEN** openChart enters it as a recommendation with `missing_authority` `no_decision_authority`, keeps the content exactly as given with `content_schema` naming the declared schema, and keeps the path's scheme and code in `path_reason`

#### Scenario: Failure: a recommendation would be published or counted
- **WHEN** a recommendation holds a confirmed encounter diagnosis, and openPractice reads that encounter's facts, or a duplicate-therapy check lists active prescriptions
- **THEN** the recommendation appears in neither, because it is never an act of record

### Requirement: AN-10 Whoever submitted a recommendation is told at once
Whoever or whatever submitted an addition that is entered as a recommendation SHALL be told at once that it was entered as a recommendation (owner ruling 80, clause 15). The response or receipt SHALL say `recorded_as_recommendation`, with each `missing_authority` code and the recommendation's identifier. A human in an openChart session SHALL see it before they leave the screen where they submitted it.

#### Scenario: A system receives its receipt
- **WHEN** an integration submits an order that is entered as a recommendation
- **THEN** its API response says `recorded_as_recommendation` with the codes and the recommendation's identifier

#### Scenario: Failure: a submission would look like a success
- **WHEN** a clinician whose grant lapsed submits a prescription for signing
- **THEN** openChart does not show it as signed, and tells the clinician at once that it was entered as a recommendation and why

### Requirement: AN-11 A recommendation goes before a clinician who holds the authority, who may adopt or decline it; it stays as written
openChart SHALL put every recommendation in front of a clinician who holds the authority it lacked (owner ruling 80, clause 16; design call CD-47, PROPOSED). It SHALL use the review path that already exists for the writer's path where one does, such as the clinical message inbox or the AI co-review queue in their own changes. Otherwise it SHALL open a review item for the encounter's primary performer, or for the medical director where there is none. A review item SHALL stay open until a named clinician adopts or declines the recommendation. Its due time and escalation SHALL work as a co-signature requirement's do (CA-07), and no timer, default or agent SHALL close it.

The clinician MAY adopt it. Adoption creates a new decision of the clinician's own, through the normal path (CA-10): a draft that the clinician may change, then a sign-off under CA-04 (owner ruling 151). The new act records `adopted_from`, naming the recommendation. The clinician MAY instead decline it, with the clinician, the time and a coded reason recorded. Either way the recommendation SHALL stay in the chart as written.

#### Scenario: A clinician adopts an AI's recommendation
- **WHEN** a clinician with order `sign` scope opens an AI's recommended laboratory order, changes its priority and signs it off with their openWallet and openSig
- **THEN** a new order of the clinician's own takes effect with `adopted_from` naming the recommendation, and the recommendation stays as written

#### Scenario: Failure: a recommendation would be closed by default
- **WHEN** a recommendation's review item passes its due time with no clinician's adoption or decline
- **THEN** openChart escalates it to the medical director and keeps it open

### Requirement: AN-12 Missing authority never refuses an addition, and an AI holds no decision authority today
Missing authority SHALL never be a reason to refuse an addition (owner ruling 80, clause 18). These still are, and openChart SHALL refuse the addition and store nothing when:
- it cannot identify the writer (AN-01);
- it cannot match the patient;
- the content is malformed or test data;
- the practice has suspended the writer (AN-03).

The existing rules that keep what an AI already told a patient in front of the doctor stand.

An AI holds no decision authority today (clause 19). Advice only is the only mode that can be switched on, and limited and full practice stay specified and off (owner ruling 67, second sentence), so everything an AI adds now is information or a recommendation. An AI never manages an emergency, and the urgent hand-off to a human stays as it is (clause 20). Consent, the patient's link, the medical director's pause and narrowing, and clinician review of what an AI told a patient all still apply (clause 21).

#### Scenario: An AI's addition is kept as information
- **WHEN** a registered relay delivers an AI's consult summary for a matched patient
- **THEN** openChart stores it as information, identified and with its provenance

#### Scenario: Failure: an addition for a patient the chart cannot match
- **WHEN** an identified system submits an observation whose patient reference matches no openChart patient
- **THEN** openChart refuses it and stores nothing

### Requirement: AN-13 A device is identified by make, model and serial or a resolvable device ID, and a reading records when it was taken; no path for device data exists yet
A device SHALL be identified by its `make`, `model` and `serial`, or by a `device_id` with its `device_id_kind` (`udi` or `asset_tag`) that the chart can resolve to them through the device's registration (AN-03; owner ruling 80, part B). A device reading SHALL record the device's identity, the `occurred_at` when the reading was taken and the `received_at` when the chart received it, source kind `device_reading` with a reference to the reading, and its writer. When an app relays a device's reading, the app is the writer, and the device is named on whose behalf it wrote, `asserted_by` that app (design call CD-42, PROPOSED). A device holds no decision authority (AN-07).

This change defines no path by which device data enters the chart: its service boundary has no operation for device readings (Open Question 8). A later governed change would define one.

#### Scenario: How a relayed reading would be recorded
- **WHEN** a later change defines a device path, and a registered app relays a reading from a registered monitor
- **THEN** the reading records the app as writer, the monitor by make, model and serial asserted by the app, the time it was taken and the time it was received

#### Scenario: Failure: a device reading arrives before a path exists
- **WHEN** a registered device submits a reading in this change
- **THEN** no operation of this change accepts it, and nothing is stored

### Requirement: AN-14 A draft is its author's work in progress, and act content submitted without the authority becomes one recommendation
Drafts, co-signatures and recommendations SHALL relate as follows, so that a nurse's unsigned draft and a nurse's unauthorized order are stages of one path, not two different things (design call CD-46, PROPOSED):
- **A draft** is an act in status `draft` (or `in_progress` for an encounter), created only by a human who holds `draft` scope for its class (AU-02). It is its author's work in progress: not a decision, and not a recommendation. Only its author signs it off (CA-04). No other clinician signs another person's draft.
- **Submitting act content as final**, by signing off a draft or by submitting act content in one step, is a sign-off attempt. When every check of CA-04 and AU-04 passes, it is a decision. Otherwise openChart SHALL enter the content as one recommendation (AN-09). A draft it came from SHALL be closed as `cancelled`, with a lifecycle event that has reason `recorded_as_recommendation` and names the recommendation. The content then lives only in the recommendation.
- **Act content from a writer without `draft` scope for its class**, whether a human without it, a patient, an AI, a device or a system, SHALL be entered as a recommendation at once. No draft is created for it.
- **A decision made with authority and subject to a co-signature requirement** (CA-07) is a decision, never a recommendation. Until it is co-signed it is held (`before_effect`) or takes effect and is co-reviewed (`after_the_fact`), as CA-07 states. A co-signature attempted without authority SHALL be entered as a recommendation, and the requirement SHALL stay open.

A clinician who wants a decision of their own from another person's work does it only by adopting the recommendation (AN-11).

#### Scenario: A nurse's draft goes to a clinician
- **WHEN** a nurse with order `draft` scope but no `sign` scope submits her draft order as final
- **THEN** openChart closes the draft as `cancelled`, naming the recommendation it created, and the recommendation goes to a clinician who holds order `sign` scope

#### Scenario: Failure: a clinician signs someone else's draft
- **WHEN** a clinician tries to sign a draft order whose author is a nurse
- **THEN** the clinician's signature does not apply to the nurse's draft, and the clinician is directed to adopt the recommendation instead, if the nurse has submitted one
