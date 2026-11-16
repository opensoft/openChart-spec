## ADDED Requirements

### Requirement: AN-01 Any identified human or system may add to a patient's chart, and an addition whose writer the chart cannot identify is refused with nothing stored
Any human or system SHALL be able to add to a patient's chart: a clinician, other staff, the patient, an AI, a device or another system (owner ruling 80, clause 1). An addition is anything written into a patient's chart through any path: a signed act, a note, a message, a consult record, a reading, an imported record, information or a recommendation. The addition is the record openChart creates: a signed act version, a recommendation record, an information record, or another record of information. A draft is not yet an addition, and a draft that stays open after a failed sign-off is still not one (AN-05, AN-14). Every addition SHALL arrive through the versioned service boundary (CA-10).

openChart SHALL add nothing unless it can identify the writer, the human or system that writes the addition into the chart, as AN-02 states. An addition SHALL be refused, and nothing SHALL be stored, only for a reason that concerns its writer: the chart cannot identify the writer (clause 2), the writer is a system or device that is not registered (clause 3; AN-03), or the practice has suspended the writer (clause 18). AN-12 lists the reasons that concern the content and the patient. Any other party the addition names that the chart cannot identify SHALL be recorded as such, with `identity_basis` `not_identified`, and SHALL never cause a refusal (design call CD-66, PROPOSED). An AI is never recorded as `not_identified`: an AI that is not identified is held, as below.

**Two kinds of quarantine.** This change and `define-ai-authored-clinical-records` use the word in two senses, defined once here:
- **quarantined in the chart**: recorded on the patient's record, marked not accepted, and reviewed. Owner ruling 90 puts there an AI consult that fails a grant check. Owner ruling 199 puts there an AI consult that reaches the chart without the reference to the patient's consent: "Keep it, marked not accepted, in front of a clinician and flagged to the medical director. The practice's AI has already spoken to the patient, so the practice needs the record. The missing consent is an incident to look into." PROPOSED beyond those cases, a writing path may put there, as the AI write path does, any other write that carries no consent reference, an AI's note or document among them, and an AI's information write that fails that path's consent check or a grant check; the cause and flag names, and how the missing-consent incident is recorded, are the writing path's (design call CD-61). It is an addition, permanent like any other (AN-05), and the minimum for a held item below does not apply to it;
- **held in quarantine outside the chart**: an addition held outside the chart because of a party it names, and no part of the chart until it is released. Owner ruling 194 decides an AI whose `openwallet_id` is missing (`openwallet_id_missing`) or is not covered by the registration of the identified, registered writer that delivers it (`openwallet_id_not_covered`). PROPOSED beyond its words: an AI that is not identified in the form the writing path reads (`ai_not_identified`, design call CD-70), and a party whose coverage the writing path's registration defines and does not give, such as an uncovered source system (`source_system_not_covered`, design call CD-71). The minimum below applies to every such hold, and every writing path uses these four names for its causes.

**An AI that the writer's registration does not cover (owner ruling 194; design call CD-61; Open Question 22, closed).** An identified, registered writer may deliver an addition for an AI whose `openwallet_id` is missing, or is not covered by that writer's registration. For an AI consult, owner ruling 194 decides it: "Keep it in quarantine, outside the chart, in front of a clinician, and alert the practice to fix the registration. The patient has already been told something, and the doctor should see it. Refuse only when the relay itself cannot be identified." openChart SHALL apply the same to every addition for such an AI, an act included (CD-61, PROPOSED, beyond the ruling's words, which name a consult). It SHALL NOT add it to the chart: it holds it in quarantine outside the chart. Where the writing path has its own hold, such as the AI write path's, the addition is held there; otherwise it is put in front of a clinician by the routing of AN-11, and stays held, not an addition. openChart SHALL alert the practice's administrative role to fix the registration. The hold applies only when the writer is identified, registered and not suspended, and only the AI it speaks for is missing or not covered; it never reaches a writer that is unidentified, unregistered or suspended. By ruling 194's last words, nothing but the writer causes a refusal: a source system or any other party the writer names that the registration does not cover is never refused. It is recorded as AN-02 states, or held where its writing path's registration defines its coverage (design call CD-71, PROPOSED).

**An AI that is not identified (design call CD-70, PROPOSED, beyond ruling 194's words, which decide an AI that is not registered).** openChart SHALL hold in the same way, and SHALL never refuse or record as `not_identified`, an addition that does not identify, in the form its writing path reads, the AI it speaks for and the hands it passed through. That covers an addition that names no AI where its path requires one; one that names an AI without its `openwallet_id`, `model` or `model_version`; one that gives any of them in a form the chart does not accept, such as a `model` outside `^[A-Za-z0-9._:/@+-]{1,128}$` or an `openwallet_id` that is not an openWallet ID; and one whose chain of parties (`on_behalf_of`) the path cannot read. Ruling 80, clause 7 makes the order of hands meaningful, so openChart never reorders the chain and never guesses at it. The cause is `ai_not_identified`, kept apart from ruling 194's own `openwallet_id_missing`. A malformed value is kept as AN-12 keeps a value openChart could not read: never used or displayed in place of its field, readable on request, marked as such, and never in an alert, a notification, a log line, a diagnostic or an acknowledgement. Such a hold is never released, and neither is one for `openwallet_id_missing`: a held item is never edited, and nothing the practice registers can repair it. Its content reaches the chart only through a corrected write or a clinician's own record. A later write that corrects the identification of a held write is checked as a new write, and the record it becomes names the held item (`corrects_held_item_ref`). The held item is then flagged, so that a clinician can dismiss it as `duplicate_of_existing_record`, naming the new record. The record schema stays strict: only a well-formed identification is ever recorded, and an AI named in a stored record has all three.

**A party a writing path's registration does not cover (design call CD-71, PROPOSED, beyond ruling 194).** A writing path whose registration defines coverage for a party other than the AI, such as the source systems a relay may deliver from, MAY hold a write for a party it does not cover, in the same way, with the cause `source_system_not_covered`. The hold ends by release once every party whose lack of coverage caused it is covered, with every check applied as of release, or by a clinician's own record or a dismissal.

**What a held item is (design call CD-61, PROPOSED).** The AI write path defines its own hold in detail. Every hold outside the chart SHALL meet at least this:
- the held item is kept as it arrived, with its writer, its time of arrival and why it is held. It is never edited and never deleted. Clinicians who can read the patient's chart can read it, marked held in quarantine. The administrative role is alerted as the rule below says, and does not read the held item's content. PROPOSED and put to the owner (Open Question 36): so that it can learn which AI or source to register, the administrative role may open the held item and see only the AI's `openwallet_id`, the source system and a relay's system party, each only where it is in its form, marked as given and unverified; any other part of the identification, such as a `model`, which can spell anything even when it is well formed, is shown only as missing or malformed; that view is audited, and nothing of it is pushed in an alert;
- the writer SHALL be told at once that it is held and why (`held_in_quarantine`);
- while it is held it is not an addition: it is not in the chart, it has no effect, it is not published or exposed through any interoperability read, and nothing counts it;
- it ends once, in one of three ways, each recorded on the held item with who, when, and the reference of any record it led to. An ending is final: a held item that has ended cannot end again, so a dismissed item is never released later, and no two additions carry the same held item's reference, which the verifier of CA-08 checks:
  - **released into the chart**: only an item that itself carries a complete, well-formed identification of every party whose lack of coverage caused the hold, which the writer's registration now covers, can be released (for an AI, its `openwallet_id`, `model` and `model_version`), and only while the writer is identified, registered and not suspended. The administrative role or a clinician releases it; owner ruling 201 decides this for an AI consult: "The administrative role or a clinician. Either way it stays on the clinician's review list until a clinician has read it." Every check of the general rule applies as of the release (design call CD-61, PROPOSED). The addition takes as `received_at` the time the chart added it, never its first arrival, and its provenance gains `released_from_quarantine`: the held item's reference, its first time of arrival, who released it and when. It is usually a recommendation, because an AI holds no decision authority today (AN-12). Whoever released it, a released item stays on the clinician's review list until a clinician has read it (owner ruling 201);
  - **recorded by a clinician**: a clinician writes a record of their own that states what the patient was told, naming the held item as its source. That record is the clinician's addition, so the AI's content enters the chart under an identified human writer;
  - **dismissed**: a clinician dismisses it, with a recorded reason about its content, from the closed list its writing path states (owner ruling 202 for an AI consult). It stays held, kept and readable, marked held, which keeps it in front of a clinician;
- an item that can never be released, one held as `openwallet_id_missing` or `ai_not_identified`, ends only by being recorded by a clinician or by dismissal, including dismissal as `duplicate_of_existing_record` once a corrected write has become a record of its own.

**What an alert about a held or quarantined item carries (design call CD-61, PROPOSED).** A value taken from a write can carry whatever its sender put there, including a patient's details, even when it passes a form check. So every alert about an item held in quarantine outside the chart, or quarantined in the chart, SHALL carry the writer or holder as the practice registered it, the coded cause and a count, and nothing taken from the write; where an identification must be shown to the administrative role, it SHALL come from the practice's own registration data. That holds for ruling 194's alert to fix a registration, for ruling 199's flag to the medical director, and for a misdirected-delivery report. An alert for `ai_not_identified` MAY say whether a value was missing or malformed, and nothing of the value. Alerts are grouped and counted by writer or holder and by cause. An alert MAY carry openChart's own references to the held or quarantined items, which ruling 199's flag needs so that the medical director can look into the incident; such a reference is openChart's own, never a value taken from the write. openChart's own alerts and log lines follow it, and writing paths cite it.

**Dismissal (owner ruling 202; design call CD-61, PROPOSED beyond its words).** Owner ruling 202 decides it for an AI consult: "Only a clinician, with a recorded reason about its content. Deciding not to register that AI does not dismiss what it already told a patient." Every writing path's list of dismissal reasons SHALL meet these rules for every kind of held item, and openChart's own list, for items it holds itself, is the one given here:
- a dismissal is made by a clinician, never by the administrative role, with a recorded reason about the item's content;
- a decision not to register an AI is the administrative role's, and does not dismiss what the AI already told a patient: it is never by itself a reason to dismiss. The item stays in front of a clinician, flagged as one that can no longer be released, and ends by the clinician's own record or by a dismissal for a reason about its content;
- `duplicate_of_existing_record` names the record it duplicates, which may be the record a corrected write became (CD-70);
- `not_for_this_patient` restricts the item from ordinary reading in this patient's context, raises a misdirected-delivery report to the administrative role carrying only what the rule above allows, and tells the writer, so the source can send it for the right patient. openChart moves no content between charts by itself;
- `no_clinical_content` is for an item with no clinical content at all.

Practice configuration is not an addition to a patient's chart: grants, attestations, designations, act-type registry entries, system and device registrations, and the binding of a practitioner's account to their wallet (AU-07). Their own refusals stay (design call CD-49, PROPOSED).

#### Scenario: A registered system adds a summary
- **WHEN** a registered integration identity adds a discharge summary declared a document, whose content validates as the document shape (a title, a date, text and a PDF attachment by reference and digest), naming itself and its operator
- **THEN** openChart stores the summary as information, with the integration identity as its writer

#### Scenario: Failure: an unidentified caller adds to the chart
- **WHEN** a caller that the chart cannot identify as a named account, a verified patient link, a registered system or a registered device submits a note for a patient
- **THEN** openChart refuses it, and nothing is stored

#### Scenario: An AI consult arrives without the reference to the patient's consent
- **WHEN** a registered relay delivers a consult from an AI its registration covers, with no reference to the patient's consent
- **THEN** openChart does not refuse it: it keeps it in the chart, marked not accepted, in front of a clinician, and flags it to the medical director as a missing-consent incident to look into

#### Scenario: Failure: an AI named with a malformed model
- **WHEN** a registered relay delivers a consult whose AI's openWallet ID the relay's registration covers, but whose `model` is `syn medical model`
- **THEN** openChart does not refuse it and does not add it: it holds it in quarantine outside the chart with the cause `ai_not_identified`, never releases it, and alerts the administrative role with the relay as the practice registered it, the cause and a count, and nothing taken from the write

#### Scenario: A corrected write follows a held one
- **WHEN** the relay later sends the same consult again with the AI's identification complete and well formed
- **THEN** openChart checks it as a new write, the record it becomes names the held item in `corrects_held_item_ref`, and the held item is flagged so that a clinician can dismiss it as `duplicate_of_existing_record`, naming that record

#### Scenario: Failure: the administrative role dismisses a held AI consult
- **WHEN** the practice decides not to register the AI of a consult held in quarantine outside the chart, and an administrator tries to dismiss the held consult
- **THEN** the dismissal takes no effect; the consult stays held, in front of a clinician, flagged as one that can no longer be released, until a clinician records it or dismisses it with a reason about its content

#### Scenario: A writing path holds a write from a source system it does not cover
- **WHEN** a registered relay delivers an AI's consult from a source system its registration does not cover
- **THEN** openChart does not refuse it: it holds it with the cause `source_system_not_covered`, and releases it only once that source system is covered

### Requirement: AN-02 Each kind of party is identified in its own recorded way
Every party an addition names, its writer and every party on whose behalf it was written, SHALL be identified by `kind` as below (owner ruling 80, part B and clause 2):

| `kind` | Identified by |
|---|---|
| `human` | their own named account in the chart (`account_ref`) |
| `patient` | the verified link the patient or their representative comes through (`patient_link_ref`). A representative is named as such (`acting_as`) |
| `ai` | its `openwallet_id`, plus the `model` and `model_version` that produced the content |
| `device` | its `make`, `model` and `serial`, or a `device_id` the chart can resolve to them, with its `device_id_kind`: `udi` or `asset_tag` |
| `system` | its registered integration identity (`system_id`) and who operates it (`operator_ref`) |

For a human, openChart SHALL also record, where they apply, their clinical role, the licence attestation on record (AU-03) and, for a practitioner who signs off a decision, their `openwallet_id` (CA-04, AU-07). These are never part of the identity, and their absence SHALL never make a writer unidentified: a sign-off without them fails as CA-04 states (design call CD-55, PROPOSED).

A human or system that has no account or registration in this chart, such as another organization's clinician or system named in the record it produced, SHALL be named by its `external_ref` (issuer, namespace and value), with its identity `asserted_by` the identified system that delivered it. Such a party SHALL never be the writer, and such a human SHALL carry no openChart clinical role (design call CD-57, PROPOSED).

Each party SHALL also carry its `identity_basis` (design call CD-42, PROPOSED). It is `verified_by_chart` when openChart itself authenticated the identity. It is `asserted_by` when an identified system vouched for it, and then names that system. The writer's identity SHALL always be `verified_by_chart`.

When a system delivers an AI's addition, the system is the writer and the AI is named as the party on whose behalf it wrote. The AI's `openwallet_id` SHALL be carried on every addition it makes, and openChart SHALL check it against the registration of the system that delivers it (AN-03). An AI named with no `openwallet_id`, or with one that the delivering system's registration does not cover, is held in quarantine outside the chart and not added, as owner ruling 194 decides (AN-01; Open Question 22, closed). So is an AI that is not identified in the form the writing path reads (design call CD-70, PROPOSED). So an AI in the chart is always identified by its `openwallet_id`, `model` and `model_version`, its `model` in the form `^[A-Za-z0-9._:/@+-]{1,128}$` that the AI write path and the inbox use.

A party other than the writer that the chart cannot identify, such as the author of an outside letter who is named but not identified, or a speaker other than an AI that a writing path cannot read, SHALL be recorded with `identity_basis` `not_identified`, and SHALL never cause a refusal (design call CD-66, PROPOSED). Such a party SHALL carry `described_as`, what is known of it as the record gave it, and SHALL carry no account, clinical role, licence attestation or wallet ID, since each would claim an identity the chart does not hold. For a speaker a writing path could not read, the party is the system the item came through, a hand in the chain and never the author, and its `described_as` SHALL be fixed neutral text, such as "a source system openChart could not read", never the value given (design call CD-66, PROPOSED). It is never a recommendation's decision maker: where the claimed maker of a carried decision cannot be identified, the carrying writer is the decision maker and the claim is kept as the claimed decision maker (AN-08). A writer, an AI and a patient are never recorded as `not_identified`: an AI whose identification a path cannot read is held as `ai_not_identified` (AN-01), and no writing path adds a hold cause of its own beyond AN-01's four. A wallet identifier SHALL NOT become the identifier of a person or a patient: openChart resolves people by their own account and patients by the openChart patient triple. Owner ruling 183: "a wallet ID may name an AI as the author of a record. It still never identifies a patient or a person, and nothing needs the wallet to be reachable to read the chart." The clarifying change to openWallet's specification is in openWallet-spec change `add-practitioner-profile-and-licence-verification` (draft pull request #10, unratified) (Open Question 24, closed). A `walletId` has the identifier form of openWallet's wallet record contract (`opensoft/openWallet-code` at `bb0e9da`: 1 to 200 characters, `^[A-Za-z0-9][A-Za-z0-9._:/-]*$`); openWallet's ratified specification text states no form of its own for a wallet identifier.

#### Scenario: A relay delivers an AI's consult record
- **WHEN** a registered relay delivers a consult record written by an AI that carries its openWallet ID, model and model version, and the relay's registration covers that openWallet ID
- **THEN** openChart records the relay as the writer, verified by the chart, and the AI as the party on whose behalf it wrote, asserted by the relay

#### Scenario: A clinician whose attestation has lapsed is still identified
- **WHEN** a clinician whose licensure attestation has expired submits an order from their own session
- **THEN** openChart identifies the clinician by their named account, and the order is entered as a recommendation with `practice_attestation_not_in_force` and `no_grant_in_force`, never refused

#### Scenario: An outside letter's author who cannot be identified is recorded as such
- **WHEN** a registered integration delivers a letter whose signing clinician is named but cannot be identified by any account or outside identifier
- **THEN** openChart records that clinician as a party with `identity_basis` `not_identified` and `described_as` giving the name and role as the letter states them, with no account or role in this chart, and the addition is not refused for it

#### Scenario: Failure: an AI addition the relay's registration does not cover
- **WHEN** a registered relay delivers an AI's addition that names no openWallet ID, or one that the relay's registration does not list
- **THEN** openChart does not add it to the chart. It holds the addition in quarantine in front of a clinician, and alerts the administrative role to fix the relay's registration (AN-01)

### Requirement: AN-03 Every system and device is registered with the practice before it adds, and the practice can suspend any of them at once
openChart SHALL let a system or device add to a chart only after it is registered with the practice (owner ruling 80, clause 3). An addition whose writer is a system or device that is not registered SHALL be refused, and nothing stored. A registration SHALL record the writer's `kind` and identity (AN-02), its operator, the practice user who registered it and when, and for a system that delivers an AI's additions, the AI `openwallet_id` values it may deliver for. The practice SHALL be able to suspend any registered system or device at once. Every later addition by a suspended writer SHALL be refused and nothing stored, until the suspension is lifted (clause 18). Registrations and suspensions SHALL be audited, and no registration SHALL be deleted. The practice's administrative role SHALL register systems and devices, and that role or the medical director SHALL be able to suspend them (owner ruling 159). Which permission names that role is decided in planning (design call CD-43, PROPOSED). A registration confers no decision authority (AN-07).

#### Scenario: A device is registered
- **WHEN** an administrator registers a home monitor by its make, model and serial number, naming its operator
- **THEN** openChart records the registration with the administrator and the time, and the monitor gains no decision authority

#### Scenario: Failure: a suspended system adds to a chart
- **WHEN** the medical director suspends an integration identity, and a minute later it submits an observation for a patient
- **THEN** openChart refuses the observation and stores nothing

### Requirement: AN-04 Every addition records when it was received, when the information arose, where it came from, what added it and on whose behalf
Every addition SHALL carry its provenance (owner ruling 80, clauses 4 to 7):
- `received_at`: the chart's own clock when it received the addition. For an item released from quarantine it is the time the chart added it, and `released_from_quarantine` keeps the held item's reference, its first arrival, who released it and when (AN-01);
- `occurred_at`: when the information itself arose, where that differs, such as when a reading was taken or a conversation held;
- `retrieved_at`: where a path retrieves items, as the inbox does, the time it retrieved this one. A retrieving path SHALL set it on every addition it makes from a retrieval, and it is never later than `received_at` (design call CD-73, PROPOSED);
- `source`: where the information came from, as a `kind` (`patient_statement`, `device_reading`, `ai_consult`, `clinician_observation`, `clinician_reply` for a clinician's reply to a patient, `external_record` or `chart_entry`) and a reference to it (design call CD-73, PROPOSED, for `clinician_reply`). Where a source is named by several values, the reference MAY be their digest: `sha256:` and the hex SHA-256 of the RFC 8785 canonical JSON of those values, which the writing path keeps beside it, as the inbox does for a turn's three reference values;
- `added_by`: the writer, identified as AN-02 states;
- `on_behalf_of`: when a system adds something for another system or a human, every party it was added for and every hand it passed through. They are listed in order from the originator to the writer, an order that is design call CD-42, PROPOSED.

openChart SHALL set `received_at` itself and SHALL NOT take it from the writer.

**What a writing path may supply (design call CD-73, PROPOSED).** Nothing is refused for a missing source or a missing time (owner ruling 188; clause 4 asks for the time the information arose only where it differs). Where a write names no `source`, its writing path MAY supply the kind its path implies, marked `defaulted`, with no reference unless the path has one, so that a path never invents one; the AI write path supplies `ai_consult`. Where a write gives no time the information arose, gives one that cannot be read, or declares one later than its receipt beyond a small clock skew that planning sets, the path MAY set `occurred_at` to the time the path received the item, marked `occurred_at_defaulted`: `retrieved_at` where the path recorded it; otherwise, for an item released from quarantine, its first arrival (`released_from_quarantine.first_received_at`), since its `received_at` is its release; otherwise `received_at`. It keeps a declared time as `occurred_at_as_declared` only where it is later than that time and is a well-formed timestamp, so an inverted interval's given end, which is earlier, is never kept there; a declared time that cannot be read is kept as AN-12 keeps a value openChart could not read. A missing time or source never makes an addition's envelope unreadable (AN-12).

Until a later governed change aligns it (tension CT-17; Open Question 15), an intake submission under the ratified `expanded-patient-intake` capability SHALL record the identity and audit that capability defines, in place of these fields. No intake addition is a decision.

#### Scenario: An item retrieved before it is filed
- **WHEN** the inbox retrieves at 10:00 a turn that gives no time, and files it into the chart at 17:30
- **THEN** the addition records `retrieved_at` 10:00, `received_at` 17:30 and `occurred_at` 10:00, marked `occurred_at_defaulted`

#### Scenario: A released write whose time was defaulted
- **WHEN** a write that gives no time first arrives at 08:00, is held in quarantine outside the chart, and is released into the chart at 14:00
- **THEN** the addition records `received_at` 14:00, `released_from_quarantine` with its first arrival at 08:00, and `occurred_at` 08:00, marked `occurred_at_defaulted`

#### Scenario: An integration forwards another organization's record
- **WHEN** a registered integration delivers a discharge summary that another organization's system produced for a clinician there
- **THEN** the addition records the integration as writer, and the other organization's clinician and system, each named by its `external_ref` and asserted by the integration, as the parties on whose behalf it was added. It records source kind `external_record` with its reference, `received_at` from openChart's clock and `occurred_at` from the record

#### Scenario: A writing path supplies what a write left out
- **WHEN** a registered relay delivers an AI's note that names no source and gives no time the information arose
- **THEN** openChart does not refuse it: the provenance carries source kind `ai_consult` marked `defaulted`, with no reference, and `occurred_at` equal to `received_at`, marked `occurred_at_defaulted`

#### Scenario: Failure: a writer supplies its own receipt time
- **WHEN** a writer submits an addition carrying a `received_at` in the past
- **THEN** openChart records its own receipt time as `received_at`, and keeps the writer's time only as `occurred_at` where the source supports it

### Requirement: AN-05 The record of an addition is permanent from submission; a correction is a new addition that points to the old one
From the moment an addition is submitted, its provenance and content SHALL be permanent and visible to anyone who can read the patient's chart in openChart (owner ruling 80, clause 8). Nothing in it SHALL be edited or deleted through any supported path. A draft is its author's work in progress and not yet an addition, so revising a draft before it is submitted is not an edit of an addition (CA-05; design call CD-60, PROPOSED). A correction SHALL be a new, dated addition that points to the addition it corrects (`corrects`), and the corrected addition SHALL stay readable. For an act, CA-05 and CA-06 are how a correction is made. What an interoperability read returns is CA-13's rule.

#### Scenario: A wrong reading is corrected
- **WHEN** a registered system corrects a reading it added an hour earlier
- **THEN** openChart stores the correction as a new addition pointing to the first, and both stay readable

#### Scenario: Failure: someone edits an addition's provenance
- **WHEN** a user or extension tries to change the `added_by` of a stored addition
- **THEN** openChart refuses the change, and the addition is unchanged

### Requirement: AN-06 Every addition is information or a decision; decision content whose class or type the chart does not hold in force becomes a recommendation, and the class a writer claims never decides whether an addition takes effect
Every addition SHALL be either information or a decision (owner ruling 80, clause 9). Information is an observation, a reading, a statement, a message, a summary or a recommendation. A decision changes the patient's care or what the chart holds as established. Decision content is (design call CD-44, PROPOSED):
- act content of the classes `encounter`, `diagnosis_of_record`, `procedure_performed`, `order` and `prescription`, whatever its act type;
- content submitted as an act of a class this chart does not define, and content of a kind clause 9 names as a decision: a diagnosis, an order, a prescription, a referral or a treatment plan;
- a sign-off of an act: a signature, a clinical note's and an encounter's included; a new signed version; a co-signature; a discontinuation; an entered-in-error mark; or the cancellation of a pending-release order or prescription.

A clinical note's content is information, an observation or a summary; the practitioner's signature on it is a sign-off, which is a decision. Owner ruling 187: "A note is information and only records who wrote it. Recording that an order was carried out is a record of work done. Signing a note or an encounter, and stopping or correcting a decision, are decisions and need the sign-off." (design call CD-63; Open Question 20). Recording that an order was carried out (a completion) is a record of work done, not a decision (design call CD-58, PROPOSED; Open Question 21). A draft revision is not a decision.

The chart keeps the list of what counts as a decision in this requirement and in the act-type registry (CA-09). Decision content whose class and act type are in force in the registry can take effect, under AN-07. Decision content whose class or act type the chart does not define, or that is not in force in the registry, including while the registry is empty, SHALL be entered as a recommendation with `no_decision_authority` when it arrives without a draft (AN-09). A sign-off of a draft whose act type was retired or is not defined is refused instead, and the draft stays a draft (CA-09, AN-14). It SHALL NOT be refused for that reason, and SHALL NOT be kept as unmarked information.

**How openChart tells information from decision content (design call CD-65, PROPOSED).** openChart SHALL determine the class from the content, never from the declaration alone. Every kind of record of information SHALL have a closed content shape: this change's note shape (`clinicalNoteContent`), or a closed shape published, pinned by digest, by the change that owns the writing path, for messages, consult records, summaries, readings and imported records:
- content declared as a kind of record of information is information only when it validates against that kind's published shape;
- content declared as a kind that has no published shape, or that does not validate against its kind's shape, SHALL be entered as a recommendation, with `no_decision_authority` (AN-09). openChart SHALL NOT look at its field names to decide whether it is decision content, and SHALL NOT keep it as information;
- this change publishes two shapes: the note shape, and the document shape (`documentContent`) for summaries, letters and imported records. Owner ruling 204 sets the document shape: until richer formats are defined, outside records and summaries are kept "As information, in one simple format: a title, a date, text, and attached PDFs or pictures that are only displayed. Anything structured still becomes a recommendation." Attachments are by reference and digest, and opaque: openChart never parses them for clinical structure and never executes them, and accepts only `application/pdf`, `image/png` and `image/jpeg`; a document needs its text or at least one attachment (design call CD-65, PROPOSED for the media types, limits and field names). Anything structured fails the document shape and becomes a recommendation; a structured clinical format needs a shape published by its own path;
- until the change that owns any other path publishes its kind's shape, content of that kind is entered as a recommendation. The AI write contract's consult record is closed in that change's own contract.

So a writer cannot keep decision content out of the "not an authorized decision" marking by declaring it a note, a summary or any other kind, whatever it names its fields. Text inside any record of information SHALL never create, count as or authorize a decision: a note or a summary that says "start amoxicillin" is documentation, and an order exists only as an order signed off under CA-04. What the chart cannot police is free text inside a valid record of information (Open Question 20).

A writer MAY declare a class on an addition. openChart SHALL determine the class itself, SHALL record the class it determined, and SHALL keep a declared class that differs as the writer's declaration only. The class a writer claims SHALL never decide whether an addition takes effect. Act content declared as information is still decision content, so it takes effect only under AN-07. Content that is not act content, and is not of a kind clause 9 names as a decision, is information even when its writer declares it a decision. Information needs only the identification of AN-01 to AN-04 to be added (clause 10). That says what information needs in order to be added; it does not exempt what an AI adds from the controls of ruling 80, clause 21 (AN-12; design call CD-74, PROPOSED).

#### Scenario: A clinician's observation is information
- **WHEN** a nurse adds a free-text observation that validates as note content to a patient's chart
- **THEN** openChart stores it as information, identified and with its provenance, and no authority is checked

#### Scenario: Failure: an order under other field names is declared a summary
- **WHEN** a registered integration submits content `{order_kind, panel_text, urgency}` declared a document
- **THEN** the content does not validate as the document shape, so openChart enters it as a recommendation with `no_decision_authority`, marked not an authorized decision, routed to a clinician, with the integration told at once

#### Scenario: Failure: a document attaches a plain-text file
- **WHEN** a registered system adds a letter declared a document whose attachment has the media type `text/plain`
- **THEN** its content does not validate as the document shape, whose attachments are PDFs or pictures, and openChart enters it as a recommendation with `no_decision_authority`

#### Scenario: A treatment plan the chart does not define is kept as a recommendation
- **WHEN** a clinician submits a treatment plan change through openChart's own boundary, a class this chart does not define, with no declared schema
- **THEN** openChart enters it as a recommendation marked not an authorized decision, with `no_decision_authority`, keeping the class as given

#### Scenario: Failure: an order arrives before any act type is registered
- **WHEN** a registered system submits an order while the practice's registry has no act type in force
- **THEN** openChart enters it as a recommendation with `no_decision_authority`, neither refusing it nor keeping it as unmarked information

#### Scenario: Failure: an order is declared as information
- **WHEN** a registered system submits order content and declares it `information`
- **THEN** openChart determines that it is decision content, keeps the declaration as the writer's only, and applies AN-07, so the order does not take effect

#### Scenario: Failure: an order under other field names is declared a note
- **WHEN** a registered system submits content `{order_kind, panel_text, urgency}` declared a clinical note
- **THEN** the content does not validate as note content, so openChart enters it as a recommendation with `no_decision_authority`, marked not an authorized decision, routed to a clinician, with the system told at once

### Requirement: AN-07 A decision counts as a decision only when its decision maker held the authority at that moment and a practitioner signed it off; the authority relied on is recorded
A decision SHALL count as a decision only when its decision maker held the practice authority for that kind of decision at that moment (owner ruling 80, clause 11), and a practitioner signed it off in their own logged-in session with their openWallet and openSig (owner ruling 151; CA-04). openChart SHALL check that authority at the moment of the action (AU-04) and SHALL record the authority each decision rested on:
- for a human, their licence and what the medical director has granted them: the licence verification in their openWallet relied on at sign-off (CA-04), the practice-supplied attestations under the grant (AU-03) and the grant version (AU-02);
- for an AI, the mode and scope the medical director has approved for it. Under owner ruling 157, ruling 151 governs over clause 11: "An AI only ever makes recommendations until a practitioner signs. Limited and full practice as designed would need a new ruling." Advice only is the only mode that could be switched on, it confers no decision authority, and owner ruling 207 keeps it off for patients until a clinician's review of an AI consult can be signed off (AN-12);
- a device or a plain integration holds none.

A decision without that authority SHALL be entered as a recommendation (AN-09). It SHALL NOT be refused for that reason (clause 18).

#### Scenario: An authorized clinician signs a diagnosis
- **WHEN** a clinician with a diagnosis grant in force signs off a diagnosis in their own session, and every check of CA-04 passes
- **THEN** the diagnosis counts as a decision, and the record names the grant version and the sign-off evidence it rested on

#### Scenario: Failure: a device submits a diagnosis
- **WHEN** a registered device submits content shaped as a diagnosis of record
- **THEN** openChart enters it as a recommendation marked not an authorized decision, because a device holds no decision authority, and no diagnosis exists

### Requirement: AN-08 A decision added on someone's behalf counts as theirs only with their own sign-off; otherwise it is a recommendation whose decision maker is said here
When a system adds a decision on someone's behalf, openChart SHALL judge authority on the decision maker, never on the system that carried it (owner ruling 80, clause 12). The decision SHALL count as the decision maker's only when the chart can confirm they made it, by their own sign-off made as ruling 151 states (owner ruling 151).

In version 1, openChart SHALL accept as that sign-off only one made in openChart, in the practitioner's own openChart session as CA-04 states. Owner ruling 186: "In openChart only, in version 1, as ruling 35 has physicians working there. A sign-off made in another system counts later, once openWallet and openSig can prove it to the chart." How such a proof would work is left to a later change (design call CD-52; Open Question 17, closed).

Otherwise openChart SHALL enter it as a recommendation (AN-09), and its decision maker SHALL be named as follows:
- **a decision claimed for a person**, such as a clinician named in another system's order: the carrying system is the decision maker. The recommendation keeps the claimed person as `claimed_decision_maker`, recorded `not_identified` with `described_as` where the chart cannot identify them, and records `decision_maker_not_confirmed`;
- **an AI's decision content delivered by a relay whose registration covers the AI's `openwallet_id`**: the AI is the decision maker, its identity asserted by the relay. The relay is the writer (`added_by`) and the AI the party on whose behalf it wrote. There is no claimed decision maker and no `decision_maker_not_confirmed`, because the relay's registration is what confirms that the AI's content is the AI's. While an AI holds no decision authority, the codes are `no_decision_authority` and `no_practitioner_sign_off`, with the path's own code in `path_reason` (design call CD-61, PROPOSED);
- **an AI the relay's registration does not cover**: the addition is held in quarantine, not entered (AN-01).

A recommendation whose decision maker is not a human SHALL carry `no_practitioner_sign_off`, since only a human practitioner signs off a decision (owner ruling 151).

`attestation_not_verified` and `signing_service_unavailable` appear in a recommendation's `missing_authority` only for an entry that reached the chart with nobody present to try again: a decision a system added on a practitioner's behalf whose carried sign-off evidence does not verify, or could not be checked. In version 1 such a decision does not count in any case (owner ruling 186); the code records why its carried evidence also failed. A sign-off attempted in openChart that fails either way is on the attempt trail only (AN-14; design call CD-79, PROPOSED).

#### Scenario: A clinician later signs off a carried order
- **WHEN** an integration delivers an order on a clinician's behalf, and the clinician then adopts it in their own session with their openWallet and openSig
- **THEN** an order of the clinician's own takes effect, pointing back to the recommendation that the delivery created

#### Scenario: A relay delivers an AI's order
- **WHEN** a registered relay whose registration covers the AI's openWallet ID delivers an order the AI produced
- **THEN** openChart enters a recommendation whose decision maker is the AI, asserted by the relay, with the relay as writer, `missing_authority` `no_decision_authority` and `no_practitioner_sign_off`, and no claimed decision maker

#### Scenario: Failure: a system claims a clinician ordered something
- **WHEN** an integration delivers an order stating that a named clinician made it, with no sign-off by that clinician that the chart can confirm
- **THEN** openChart enters it as the integration's recommendation marked not an authorized decision, with `decision_maker_not_confirmed`, names the clinician only as the claimed decision maker, and no order takes effect

### Requirement: AN-09 Decision content entered without authority is kept in full as a recommendation, marked not an authorized decision, with no effect
A decision made without authority SHALL still be entered in the chart, in full, as a recommendation and not a decision (owner ruling 80, clause 13). The recommendation record SHALL hold:
- the proposed action, and the act class and act type as the writer gave them. The class is kept as given, whether or not this chart defines it, and the act type is kept where the writer gave one (design call CD-51, PROPOSED);
- the content exactly as given. openChart SHALL check it only for being well formed: an object the chart can read, within the record's own closed envelope. Where the writing path declared it under another schema, `content_schema` names that schema (its identifier, version and SHA-256), with any action but a co-signature (design call CD-56, PROPOSED);
- for an action on an existing record, the form below (design call CD-51, PROPOSED):
  - a discontinuation, an entered-in-error mark or a cancellation is that action, with the act version it is on as `target`, any coded reason as `reason_code`, and any content the writing path gave with it kept as given, with its `content_schema`;
  - a correction or replacement of an existing act is `new_version`, with the act version it would replace as `target` and the new content as given;
  - the writing path's own reference to the record, such as the AI write contract's `target_record_ref`, is kept as given in `target_as_given`. Where openChart cannot resolve it to an act version of this patient's chart, `target` is absent and the reviewer sees the reference as given;
  - a `sign` names no existing record;
  - a change proposed to a record that is not an act, such as an earlier recommendation or an information record, is a new addition that `corrects` it (AN-05), so a superseding AI act is a new recommendation that corrects the earlier one;
  - an AI's action on a clinician-authored record is `no_decision_authority`, as below;
- the same identification and provenance (AN-02, AN-04);
- the marker `not_authorized_decision`;
- each coded `missing_authority` reason, from this closed list that every reader uses (design call CD-45, PROPOSED). Several may apply at once:
  - `no_grant_in_force`: the decision maker holds no grant in force for this action, act class and act type. For a human that is AU-02; for an AI it is the mode and scope the medical director approved, with their conditions;
  - `no_decision_authority`: no decision maker of this kind can hold authority for this decision now. That covers an AI today (AN-12), a patient, a device or a plain integration, an act reserved to a human clinician, the management of an emergency, an AI's action on a clinician-authored record, an author co-signing their own act (CA-07), content declared a note that is not note content (AN-06), and decision content whose class or act type the chart does not define or hold in force, submitted without a draft (AN-06). A sign-off of a draft of such a type is refused instead, and the draft stays a draft (CA-09; Open Question 23);
  - `decision_maker_not_confirmed`: it was added on someone's behalf without that person's own confirmed sign-off (AN-08);
  - `no_practitioner_sign_off`: no practitioner signed it off under CA-04. A recommendation whose decision maker is not a human always carries it (AN-08);
  - `wallet_not_bound`: the signer's account is not bound to the `openwallet_id` that signed (AU-07);
  - `licence_verification_missing`: the wallet holds no current licence verification that covers this decision;
  - `attestation_not_verified`: the openSig attestation did not verify against the wallet over the sign-off statement (CA-04);
  - `signing_service_unavailable`: openWallet or openSig could not be reached;
  - `practice_attestation_not_in_force`: the practice-supplied licensure or prescriber attestation that the grant rests on is not in force (AU-03);
- optionally, the writing path's own coded reason, `path_reason`: the scheme that defines the code, the scheme's version and the code (design call CD-51, PROPOSED). A path that fails on finer reasons of its own maps each of its codes to one or more codes of the closed list, records those in `missing_authority`, and keeps its own code in `path_reason` for the source and the reviewer. `path_reason` never replaces `missing_authority`. It is shown to the reviewer beside it, and it decides nothing.

A safety gate is never a missing-authority reason: the list names only which authority was missing (owner ruling 80, clauses 13 and 14). Authority is checked before any gate, and a recommendation is not gated. The prescribing-safety gate applies to the practitioner's own decision when they adopt the recommendation (AN-11, RX-02). A writing path that stops at a gate check of its own SHALL record in `missing_authority` the authority codes that are true of the entry, such as `no_practitioner_sign_off`, and SHALL keep its gate code in `path_reason` only.

A recommendation's content is kept for the source and the reviewer. Nothing reads it as an act's content. A recommendation never holds note content: content that validates as note content is information (AN-06, AN-14). The act-validity rules (CA-01's class content, CA-09's act types, CA-12's code sets and the class rules of DX-01, DX-03, OR-01 and RX-01) apply only when a clinician adopts it, and a failure is recorded on the recommendation (AN-11).

Wherever a recommendation is shown, to a clinician or a patient, it SHALL be clearly marked "not an authorized decision" and SHALL say which authority was missing.

A recommendation SHALL have no effect (clause 14). It is never an act of record. It has no act status and cannot be signed, released, transmitted or published. It is never a billable fact. It never counts as an active diagnosis, procedure, order or prescription, or as a signature, co-signature or release, and it never satisfies a check or removes a warning that a decision would. Nothing is ordered, prescribed, sent, billed or treated as established because of it. The same SHALL apply to a human as to a system (clause 17).

#### Scenario: A nurse's unauthorized order is kept
- **WHEN** a nurse without order `sign` scope submits a laboratory order as final
- **THEN** openChart enters it in full as a recommendation marked "not an authorized decision", with `no_grant_in_force`, and no order exists or is released

#### Scenario: A nurse's uncoded diagnosis is kept as given
- **WHEN** a nurse without diagnosis `sign` scope submits a provisional encounter diagnosis that carries free text and no coding
- **THEN** openChart keeps it as given in a recommendation with `no_grant_in_force`. The coding rule applies when a clinician adopts it

#### Scenario: An AI's act content is kept as given, with the path's own reason
- **WHEN** a relay delivers an AI's order whose content was declared under the AI write contract's own schema, and the AI write path records it with a code of its own for the check that failed
- **THEN** openChart enters it as a recommendation with `missing_authority` `no_decision_authority`, keeps the content exactly as given with `content_schema` naming the declared schema, and keeps the path's scheme and code in `path_reason`

#### Scenario: Failure: a recommendation would be published or counted
- **WHEN** a recommendation holds a confirmed encounter diagnosis, and openPractice reads that encounter's facts, or a duplicate-therapy check lists active prescriptions
- **THEN** the recommendation appears in neither, because it is never an act of record

### Requirement: AN-10 Whoever submitted a recommendation is told at once, a repeat is answered with the first result, and a conflicting repeat is kept and flagged
Whoever or whatever submitted an addition that is entered as a recommendation SHALL be told at once that it was entered as a recommendation (owner ruling 80, clause 15). The response or receipt SHALL say `recorded_as_recommendation`, with each `missing_authority` code and the recommendation's identifier. A human in an openChart session SHALL see it before they leave the screen where they submitted it; that timing is design call CD-47, PROPOSED.

A submission that repeats an earlier one, from the same writer with the same `submission_ref` and the same content digest, SHALL be answered with the first submission's result, and SHALL create no second recommendation or other addition. A submission that reuses a `submission_ref` with a different content digest SHALL NOT be refused. openChart SHALL store it as a new addition, flagged `submission_ref_conflict` with the first addition and its content digest, and SHALL tell the writer at once: a recommendation's or an information record's writer in its receipt (`submission_ref_conflict`); the writer of an act version, who is a human in their own openChart session (CD-52), on screen before they leave the screen where they submitted, with that notice recorded in the act's audit trail (CA-08). Both additions stay; nothing is lost (design call CD-64, PROPOSED).

#### Scenario: A system receives its receipt
- **WHEN** an integration submits an order that is entered as a recommendation
- **THEN** its API response says `recorded_as_recommendation` with the codes and the recommendation's identifier

#### Scenario: Failure: a reused submission reference carries different content
- **WHEN** an integration sends a second order with the same `submission_ref` as an earlier one but different content
- **THEN** openChart stores the second as a new recommendation flagged `submission_ref_conflict`, naming the first, tells the integration at once, and neither content is dropped

#### Scenario: Failure: a retry would create a second recommendation
- **WHEN** an integration resends the same order with the same `submission_ref` after a network timeout
- **THEN** openChart answers with the first receipt and the same recommendation's identifier, and stores nothing new

#### Scenario: Failure: a submission would look like a success
- **WHEN** a clinician whose grant lapsed submits a prescription for signing
- **THEN** openChart does not show it as signed, and tells the clinician at once that it was entered as a recommendation and why

### Requirement: AN-11 A recommendation goes before a clinician who holds the authority, who may adopt or decline it; it stays as written
openChart SHALL put every recommendation in front of a clinician who holds the authority it lacked (owner ruling 80, clause 16; design call CD-47, PROPOSED). It SHALL use the review path that already exists for the writer's path where one does, such as the clinical message inbox or the AI co-review queue in their own changes. Otherwise it SHALL open a review item for the encounter's primary performer, or for the medical director where there is none. A review item SHALL stay open until a named clinician adopts or declines the recommendation. Its due time and escalation SHALL work as a co-signature requirement's do (CA-07), and no timer, default or agent SHALL close it.

The clinician MAY adopt it, which makes a decision of the clinician's own, signed off under CA-04 (owner ruling 151), whose record names the recommendation in `adopted_from`:
- for proposed new content with no draft, a draft of the clinician's own that the clinician may change, then signs off;
- for content tied to a draft (AN-14), a sign-off made on that draft, so nothing attached to it is left pointing at a closed record. An adoption without any change signs the content as written: the draft keeps its identifier and version and becomes the clinician's act, with the clinician as author and the drafter kept as its writer (AN-04). An adoption that changes anything is a new version of the clinician's own, which the clinician writes and signs off. It keeps the draft's identifier, supersedes the held draft and points back to the recommendation (design call CD-47, PROPOSED);
- for a proposed action on an existing act (a co-signature, a discontinuation, an entered-in-error mark or a cancellation), the clinician's own sign-off of that action, whose lifecycle event names the recommendation;
- for a proposed `new_version` of an existing act, the clinician's own new version, carrying `adopted_from`, made as the act's class allows (design call CD-47, PROPOSED): an amendment of a final note, diagnosis or procedure (CA-05), inside an encounter amendment where its encounter is final (EN-05); an encounter amendment for an encounter; a new signed version of an order or prescription that is still `pending_release`; and for one already `released`, which is never amended (OR-03), a discontinuation of the target and a new act, each signed off by the clinician and each carrying `adopted_from`. Where the target did not resolve (`target_as_given` only), the clinician adopts by choosing the act it means, or by a new draft;
- every targeted action a recommendation can propose has one of these forms. No recommendation proposes a completion: recording that an order was carried out is a record of work done, not a decision (owner ruling 187), so one attempted without the `complete` scope is kept in the order's trail as a report attributed to its writer and shown to the order's signer (design call CD-58, PROPOSED).

A decline SHALL carry a coded reason. The reason `not_a_decision_kept_for_reference` records that the content was never a decision and stays in the chart for reference, and is shown that way, never as a clinician rejecting the facts it holds (design call CD-65, PROPOSED). It is allowed only where the proposed class is outside the five decision classes, which the contract enforces: content of a decision class is declined for what it proposes, never as never a decision.

Adoption applies the act-validity rules to the content the clinician signs off (AN-09). Adopting an encounter signs off the manifest of every record its signing view showed, as every encounter sign-off does (CA-04, EN-04), so the clinician attests only what the sign-off binds. An adoption made on a held draft releases the hold with `hold_released` `adopted` (AN-14). An adoption that does not complete, because the content fails such a rule, the clinician lacks the authority, or the sign-off fails, SHALL be recorded on the recommendation with the clinician, the time and the reasons. It SHALL create no second recommendation, and the recommendation SHALL stay open (design call CD-46, PROPOSED). The clinician MAY instead decline it, with the clinician, the time and a coded reason recorded. Either way the recommendation SHALL stay in the chart as written.

#### Scenario: A clinician adopts an AI's recommendation
- **WHEN** a clinician with order `sign` scope opens an AI's recommended laboratory order, changes its priority and signs it off with their openWallet and openSig
- **THEN** an order of the clinician's own takes effect with `adopted_from` naming the recommendation, and the recommendation stays as written

#### Scenario: A clinician adopts a nurse's held draft with a change
- **WHEN** a clinician adopts the recommendation that a nurse's draft order is held for, and raises its priority before signing it off
- **THEN** the clinician's new version of the order, with the draft's identifier, supersedes the held draft, names the clinician as its writer and author, states the change as its amendment reason, and carries `adopted_from` naming the recommendation; the nurse's draft stays readable as the version before it

#### Scenario: A failed adoption is recorded on the recommendation
- **WHEN** a clinician tries to adopt a recommended order while openSig cannot be reached
- **THEN** openChart records the attempt on the recommendation with `signing_service_unavailable`, creates no second recommendation, and the recommendation stays open for the clinician to try again

#### Scenario: Failure: a recommendation would be closed by default
- **WHEN** a recommendation's review item passes its due time with no clinician's adoption or decline
- **THEN** openChart escalates it to the medical director and keeps it open

### Requirement: AN-12 Missing authority never refuses an addition, and an AI holds no decision authority today
Missing authority SHALL never be a reason to refuse an addition (owner ruling 80, clause 18). These still are, and openChart SHALL refuse the addition and store nothing when:
- it cannot identify the writer (AN-01);
- the writer is a system or device that is not registered (AN-03, clause 3);
- it cannot match the patient, except as below;
- the content cannot be read at all (malformed, owner ruling 188), which, PROPOSED (Open Question 37), includes content whose digest does not recompute, or is test data;
- the whole message is beyond the size limit its writing path's contract names (PROPOSED);
- the practice has suspended the writer (AN-03).

A party other than the writer that cannot be identified never causes a refusal (AN-02). An AI that the writer's registration does not cover is held in quarantine outside the chart, not refused (AN-01, owner ruling 194), and so is an AI that is not identified (design call CD-70, PROPOSED).

**An item whose patient cannot be matched, kept outside every chart (design call CD-72, PROPOSED).** Where a safety rule of the writing path requires a human to see an item, such as the clinical message inbox's rule for urgent and priority items, openChart MAY keep an item whose patient it cannot match outside every chart instead of refusing it. It is modelled on AN-01's held item: nothing of it enters any patient's chart; it is kept as it arrived, never edited or deleted; it is in front of a named human; the writer is told; and it ends once, either matched to a patient and filed through the normal path, with the hold recorded on what it became, or closed with a coded reason. Every other addition whose patient cannot be matched is refused, and nothing is stored.

Owner ruling 188: content is "Kept, as entered, as a recommendation. Only content the chart cannot read at all is refused. The clinician who adopts it completes the missing parts." So content is malformed only when the chart cannot read it at all. An addition's envelope is not its content: a writer the chart cannot identify, or a patient it cannot match, is refused for that reason, and an addition that carries no readable content object or provenance at all is unreadable and refused as malformed (design call CD-56, PROPOSED for the envelope). A missing time or source never makes it unreadable (AN-04). A reused `submission_ref` is not malformed: it is kept and flagged (AN-10). Content that is readable but breaks an act-validity rule, such as a nurse's order that lacks a required code, is kept as entered as a recommendation, and the clinician who adopts it completes the missing parts (AN-11; Open Question 18, closed). openChart SHALL recognize test data only by a context its writer declares, on the submission or in its registration (`test`, `scenario` or `simulation`), or by a patient record the practice has marked as a test patient. It SHALL never infer test data from content (design call CD-62, PROPOSED).

**A value that fails its form (design call CD-56, PROPOSED as a reading of owner rulings 188 and 194).** Apart from the writer, the patient, the declared context, the record identifiers and the content object, no value SHALL refuse a write. A value that fails its form takes the outcome its absence would take, failing closed: an unreadable time is a missing time (AN-04), an unreadable source a missing source, an unreadable identification of an AI an AI that is not identified (AN-01), an unreadable speaker other than an AI a party recorded as `not_identified` (AN-02), and an unreadable authority claim no authority (AN-09). Ruling 188 refuses only content the chart cannot read at all, and ruling 194 refuses only when the relay itself cannot be identified. Writing paths cite this rule.

**Where a value openChart could not read is kept, and who can read it (design call CD-56, PROPOSED as a reading of owner ruling 80, clause 8, and put to the owner, Open Question 35).** Clause 8: "This record is permanent and visible to anyone who can read the chart." A value openChart could not read is kept as given with the addition's record. It is never used or displayed in place of the field it was given for. Anyone who can read the chart can read it on request, marked as a value openChart could not read. It never appears in an alert, a notification, a log line, a diagnostic or an acknowledgement. Writing paths cite this rule.

**Content whose digest does not recompute, and size (design call CD-56, PROPOSED).** Content whose digest does not recompute is content openChart cannot read: it cannot be read back by its digest, and nothing shows that it arrived as it was sent. A writing path MAY refuse it. That is a reading of owner ruling 188's "only content the chart cannot read at all", put to the owner (Open Question 37); the other reading keeps such content, marked as failing its digest. A single declaration beyond its bound, inside a write openChart can read, is a value that fails its form: it is set aside, and only its SHA-256 and its length are kept, never the value itself. Only a whole message beyond a stated limit MAY be refused, and the writing path's contract names that limit. Writing paths cite this rule.

The existing rules that keep what an AI already told a patient in front of the doctor stand (AN-01).

An AI holds no decision authority today (clause 19). Advice only is the only mode that could be switched on, and limited and full practice stay specified and off (owner ruling 67, second sentence), so everything an AI adds now is information or a recommendation. Owner ruling 207 keeps even advice only off for patients until a clinician's review of an AI consult can be signed off: "Every AI consult is meant to be reviewed by a clinician; if that review cannot be completed, the AI should not be talking to patients. It can still be built and tested against stand-ins." A review can be signed off only once CA-04's checks can be made in a live deployment (owner ruling 152; design call CD-69, PROPOSED). An AI never manages an emergency, and the urgent hand-off to a human stays as it is (clause 20). Consent, the patient's link, the medical director's pause and narrowing, and clinician review of what an AI told a patient all still apply (clause 21). openChart reads clause 21 as reaching everything an AI adds through a writing path, information included: that path's consent check, the medical director's pause and narrowing, and clinician review (design call CD-74, PROPOSED). Clause 10 says what information needs in order to be added; it does not exempt it from those controls. The other reading, that clause 10 alone governs information and clause 21 reaches only what an AI told a patient, is put to the owner.

#### Scenario: An AI's addition is kept as information
- **WHEN** a registered relay delivers an AI's consult summary that validates as consult record content, under the AI write contract's published shape, for a matched patient
- **THEN** openChart stores it as information, identified and with its provenance, and no text in it creates, counts as or authorizes a decision

#### Scenario: Failure: an addition for a patient the chart cannot match
- **WHEN** an identified system submits an observation whose patient reference matches no openChart patient
- **THEN** openChart refuses it and stores nothing

#### Scenario: Failure: a submission declared as a simulation
- **WHEN** a registered system submits an order in a submission it declares as `simulation`
- **THEN** openChart refuses it as test data and stores nothing

### Requirement: AN-13 A device is identified by make, model and serial or a resolvable device ID, and a reading records when it was taken; no path for device data exists yet
A device SHALL be identified by its `make`, `model` and `serial`, or by a `device_id` with its `device_id_kind` (`udi` or `asset_tag`) that the chart can resolve to them through the device's registration (AN-03; owner ruling 80, part B). A device reading SHALL record the device's identity, the `occurred_at` when the reading was taken and the `received_at` when the chart received it, source kind `device_reading` with a reference to the reading, and its writer. When an app relays a device's reading, the app is the writer, and the device is named on whose behalf it wrote, `asserted_by` that app (design call CD-42, PROPOSED). A device holds no decision authority (AN-07).

This change defines no path by which device data enters the chart: its service boundary has no operation for device readings (Open Question 8). A later governed change would define one.

#### Scenario: How a relayed reading would be recorded
- **WHEN** a later change defines a device path, and a registered app relays a reading from a registered monitor
- **THEN** the reading records the app as writer, the monitor by make, model and serial asserted by the app, the time it was taken and the time it was received

#### Scenario: Failure: a device reading arrives before a path exists
- **WHEN** a registered device submits a reading in this change
- **THEN** no operation of this change accepts it, and nothing is stored

### Requirement: AN-14 A draft is its author's work in progress, and a failed sign-off never loses what the author wrote
Drafts, sign-off attempts, co-signatures and recommendations SHALL relate as follows (design call CD-46, PROPOSED):
- **A draft** is an act in status `draft`, or `in_progress` for an encounter, created only by a human who holds `draft` scope for its class (AU-02). It carries `entry_class` `draft` and no signature. It is its author's work in progress: not a decision, not a recommendation, and not yet an addition (AN-05). Only its author signs it off, except by adoption (AN-11).
- **Submitting as final**, by signing off a draft or by submitting act content in one step, is a sign-off attempt. For a draft, openChart SHALL check first that its act type is in force (CA-09), then authority (AU-04 and CA-04's grant check), then the rest of CA-04, then any gate (RX-02, RX-03). When every check passes, it is a decision. A sign-off of a draft whose act type was retired or is not defined is refused at the first check, whoever wrote the draft, so it never becomes a recommendation (Open Question 23).
- **A failed sign-off is one of four kinds**, and each leaves a different thing behind (design call CD-79, PROPOSED). In every kind, nothing counts as a decision unless every check passed:
  1. **The author can cure it by trying again**: openSig is unavailable, an attestation came back not verified for a reason a retry cures (CA-04), re-authentication failed or lapsed, or the statement's digest changed. The draft stays the author's draft, and the failure is on the attempt trail only, with any `not_verified` attestation kept as openSig issued it (CA-08). openChart tells the author at once and creates no recommendation.
  2. **Only the deployment can cure it**: openWallet's check of the licence verification is `not_checkable`, because the deployment holds nothing to check it with, or the attestation key or the attester in the deployment is at fault, or the attester does not accept the proof's profile, or openSig refused openChart's own request or credential. The draft stays a draft, and the failure is on the attempt trail. The practice's administrative role is alerted, because no practitioner can sign until it is fixed.
  3. **Only the practitioner's own new binding or device enrolment can cure it**: the bound key's custody is not one openChart accepts, openSig found the key's binding missing, not current, not declared or retired, its custody reference mismatched or its backup eligibility changed, or a passkey that syncs is used from a device the practitioner has not enrolled (owner ruling 209; AU-07). It is never cured by trying again. The author is told to bind a key of accepted custody, with a licence verification that names it, or to enrol the device or sign with a security key (AU-07). The draft stays a draft, and the failure is on the attempt trail.
  4. **The authority is missing**: every openWallet refusal of the verification relied on, and openSig's `wallet_not_active`, each mapped to `licence_verification_missing` with the reason in `path_reason`; no grant in force; or licence records that do not match under owner ruling 160. This is a failure of authority, below.

  A one-step submission that fails in kind 1, 2 or 3 SHALL be kept as its author's draft. A check that openWallet or openSig does not yet specify cannot be made: the attempt is recorded, and the draft stays a draft as in kind 1. So while openWallet and openSig specify nothing, a practitioner's drafts stay drafts.
- **A failure of authority**, kind 4, meaning any missing-authority reason, SHALL enter the content as one recommendation (AN-09), tied to the draft by `draft_ref`, as owner ruling 80, clause 13 says, for a human as for a system. The draft SHALL NOT be cancelled. It is held while the recommendation is open: it carries `held_for`, naming that recommendation, and a `held` lifecycle event records the hold, so that anyone reading the draft sees it is held and for what. Its author cannot revise, resubmit or cancel it while it is held. The hold ends only with a `hold_released` event, by adoption (`adopted`) or by decline (`declined`), and an act signed after a hold carries `adopted_from` or follows a release by decline, which the verifier of CA-08 checks. A held draft cannot be cancelled while held, so its recommendation is never left pointing at a closed draft. The addition is the recommendation; the held draft is still not an addition. An encounter is never cancelled by a failed sign-off, so every note, diagnosis and procedure attached to it stays attached. When a clinician adopts the recommendation, the adoption is made on the draft (AN-11). When the recommendation is declined, the draft returns to its author, who may revise and resubmit it or abandon it as `cancelled`. Owner ruling 203 decides who may close another clinician's unfinished draft that blocks signing the visit: the medical director, "but only after it has been listed and escalated. Its content stays readable, and its author is told." A draft that returns this way, like any draft that blocks an encounter's signature (EN-04) and is not held, SHALL NOT block it indefinitely: it is listed for its author and for the encounter's primary performer with a due time set by practice policy, and when that time passes it escalates to the medical director, who may close it as `cancelled` with the reason `closed_to_finalize_encounter`. The author and the primary performer are told when it is closed. Its content stays readable, and a declined recommendation keeps it too, so nothing is lost. No timer closes it. This does not reach a held draft, which cannot be cancelled while held; its recommendation's review item escalates instead (AN-11) (design call CD-68, PROPOSED for the listing, the times, the notices and the reason).
- **A refusal that loses nothing** leaves the draft a draft, with no recommendation: a sign-off of a draft whose act type was retired or is not defined, refused at the first check (CA-09), since nothing is lost and such a recommendation could never be adopted; and a gate refusal after the authority checks pass (RX-02, RX-03). A one-step submission that the gate refuses SHALL be kept as its author's draft. What becomes a recommendation is never gated (AN-09).
- **A clinical note** submitted as final without the authority to sign it is not a recommendation. Where its content validates as note content (AN-06), openChart SHALL keep it as information under its writer's name (record kind `information`, marked not signed off), and SHALL tell the writer at once, recording the receipt `kept_as_information`. Where it came from a draft, openChart SHALL close the draft as `cancelled` with reason `kept_as_information`, naming that record. Nothing is lost, because the content now lives in that record. Such a note never counts as a final note (EN-04) and is never published (design call CD-63, PROPOSED; Open Question 20). Content declared a note that does not validate as note content follows AN-06: it is always a recommendation with `no_decision_authority`. Such content never comes from a note draft, whose content is always note content (CA-01).
- **Decision content from a writer without `draft` scope** for its class, whether a human without it, a patient, an AI, a device or a system, SHALL be entered as a recommendation at once. No draft is created for it.
- **A decision made with authority and subject to a co-signature requirement** (CA-07) is a decision, never a recommendation. Until it is co-signed it is held (`before_effect`) or takes effect and is co-reviewed (`after_the_fact`), as CA-07 states. A co-signature attempted without authority SHALL be entered as a recommendation, and the requirement SHALL stay open.

A clinician who wants a decision of their own from another person's work does it only by adopting the recommendation (AN-11).

#### Scenario: A nurse's draft goes to a clinician
- **WHEN** a nurse with order `draft` scope but no `sign` scope submits her draft order as final
- **THEN** openChart enters the content as a recommendation tied to the draft, holds the draft without cancelling it, and puts the recommendation before a clinician who holds order `sign` scope

#### Scenario: A signing service outage leaves the draft open
- **WHEN** a clinician with sign scope signs off a draft note while openSig cannot be reached
- **THEN** the note stays a draft, the attempt is recorded in its trail, the clinician is told at once, and no recommendation is created

#### Scenario: Failure: the deployment holds nothing to check a licence verification with
- **WHEN** a clinician signs off a draft order while the deployment holds no revocation list from the verifier of the clinician's licence verification
- **THEN** the order stays a draft, the attempt is recorded, no recommendation is created, and the administrative role is alerted that the deployment must obtain the list

#### Scenario: Failure: the bound key's custody is not accepted
- **WHEN** a clinician signs off with a bound key whose declared custody is not one openChart accepts
- **THEN** the draft stays a draft, the attempt is recorded, and the clinician is told to bind a key of accepted custody with a licence verification that names it; trying again with the same key fails the same way

#### Scenario: Failure: an encounter would be cancelled by a failed sign-off
- **WHEN** a nurse without encounter `sign` scope submits an in-progress encounter with notes and a diagnosis attached
- **THEN** the encounter stays `in_progress` with everything attached, and the content is entered as a recommendation tied to it, which a clinician may adopt on the encounter itself

#### Scenario: Failure: a held draft would be abandoned while held
- **WHEN** a nurse tries to cancel her draft order while it is held for its recommendation
- **THEN** openChart refuses, and the draft stays held until a clinician adopts or declines the recommendation

#### Scenario: Failure: a clinician signs someone else's draft
- **WHEN** a clinician tries to sign a draft order whose author is a nurse
- **THEN** the clinician's signature does not apply to the nurse's draft, and the clinician is directed to adopt the recommendation instead, if the nurse has submitted one
