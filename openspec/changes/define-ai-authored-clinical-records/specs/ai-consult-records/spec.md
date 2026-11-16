## ADDED Requirements

### Requirement: AC-01 openChart records each AI consult on the clinical-communication record, with the full exchange
openChart SHALL record each accepted `consult.write` as a consult record. The consult record SHALL be the clinical communication record that MI-12 of `define-clinical-message-inbox` (openChart-spec#3, not yet on main) defines as the single definition of that record in openChart, with origin `ai_consult`, and SHALL keep MI-13's distinction of AI-authored content. This change cites MI-12 by requirement ID, adds the fields below to that record for this origin, and defines no second clinical communication record (design call AD-3). The handoff references of MI-12 are absent for this origin. This change defines no conversation retrieval; openChart's neutral `openchart-conversation-retrieval/1.0` belongs to `define-clinical-message-inbox` (ruling 69). Writing a consult record SHALL NOT require the inbox to be enabled, and SHALL NOT require openPractice. A consult record is information (ruling 80, clause 9). It needs the identification of AW-02 (clause 10) and carries the provenance of AW-15; the medical director's grant, with its pause and narrowing, and its consent reference decide whether it is accepted or quarantined in the chart (clause 21; AC-11; design call AD-62), and never refuse it.

The consult record SHALL hold the full exchange as written: every turn with its author type, time, text and attachment references, and the exchange's content digest. An AI-written summary MAY accompany it, labelled AI-authored, and SHALL never replace the exchange (design call AD-2). The record SHALL also hold the source system's conversation reference, so that an inbox item that names the same conversation can be associated with the consult record by reference. The inbox still files no copy (MI-24).

Tier 1 SHALL be buildable without any orders, prescriptions or diagnoses model in openChart. From `define-clinical-acts-foundation` (openChart-spec#5) it needs the clinical roles and authority of AU-01 to AU-05, and the general rule for additions with its recommendation record (AN-01 to AN-14), which that change's feature (1) builds (AG-02, AG-11, AW-16). A recorded consult MUST NOT be silently overwritten or deleted. A continuation or correction SHALL be a new consult version that references its predecessor.

#### Scenario: An advice consult is recorded
- **WHEN** an AI system sends a schema-valid, authorized `consult.write` under an active `advice_only` grant for a linked patient
- **THEN** openChart records the full exchange and its digest on a clinical-communication record with origin `ai_consult`, and answers `accepted` with the `record_ref`

#### Scenario: Failure: the exchange does not match its digest
- **WHEN** a `consult.write` carries a `content_sha256` that does not equal the digest of its turns
- **THEN** openChart refuses it with reason `content_digest_mismatch` and stores no clinical content

#### Scenario: Failure: a user tries to file the consult again from an inbox item
- **WHEN** an inbox item names the same conversation and a user tries to file a copy of the exchange from it
- **THEN** the filing is refused, and, where both records are on the same patient, the inbox item shows the association with the existing consult record (MI-24)

### Requirement: AC-02 AI authorship is always distinguishable from clinician-authored and patient-reported content
Every turn of a consult record SHALL carry one of MI-12's author types: `patient`, `representative` or `ai`, in the field `author_type`. A consult write SHALL NOT carry content of MI-12's other author types: `clinician`, `staff`, `system` or `unknown`. AI turns and the AI summary SHALL be recorded and shown as AI-authored, naming the source system, using MI-12's author type `ai`. Patient and representative turns SHALL remain visibly patient-reported. A consult SHALL contain at least one AI turn. Nothing in a consult record SHALL be recorded, shown or delivered as clinician-authored.

#### Scenario: Failure: a turn claims clinician authorship
- **WHEN** a `consult.write` carries a turn with author type `clinician`
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: an AI summary could pass as a doctor's note
- **WHEN** a clinician views a consult record that carries an AI summary
- **THEN** the summary is labelled AI-authored with the source system named, and is never shown as a clinician's note

### Requirement: AC-03 A consult record carries its models, evidence, mode in force and authority
Every consult record SHALL carry:
- the model identifiers and versions the source system used;
- the evidence references, each by namespace, reference, and where given version and digest, for the consult as a whole and, where the source system gives them, for each AI turn;
- for each AI turn where the source system states it, its knowledge basis: `cited_sources`, `model_knowledge` or `mixed` (design call AD-27);
- the mode in force and the grant identifier, grant version and configuration version the write claimed, and the grant version openChart checked;
- the consent reference the write carried, the source system's own reference to the patient's consent, which the source system holds and openChart neither resolves nor verifies, or that it carried none (AW-06; ruling 199; design calls AD-14 and AD-62);
- the consult's start and end times as the write gives them, or that its start was not stated and its end was taken from its receipt (AW-15; design call AD-70);
- the review flags the source system declared, the emergency indicator, and where the source system routed the patient;
- the AI's openWallet ID, model and model version, the writer and every party on whose behalf it was written, and its source (AW-02, AW-15).

A declaration the write leaves out is recorded as absent and never refuses it (ruling 188; design call AD-63): with no `models`, the record shows the AI's model and model version from `on_behalf_of` only; with no `review_flags`, none was declared; with no `escalation`, the routing was not stated; with no `authority`, the grant checks answer as AG-06 states; and with no `emergency_indicated`, the consult counts as an emergency, failing closed, so it is listed urgently and always reviewed, and the record shows that the value was defaulted.

openChart SHALL NOT fetch, store or re-host the evidence itself. An AI turn whose knowledge basis is `model_knowledge` SHALL be shown as resting on the model's own knowledge with no cited source. A consult with no evidence reference, neither for the whole consult nor for any AI turn, SHALL be recorded, shown as "no evidence references", and selected for review (AC-07).

#### Scenario: Failure: a patient turn claims a knowledge basis
- **WHEN** a `consult.write` gives a patient turn a knowledge basis or evidence references
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: the mode in force differs from the grant
- **WHEN** a `consult.write` states `limited_practice` as its mode in force while openChart's current grant is `advice_only`
- **THEN** openChart keeps it as a quarantined consult with `quarantine_cause` `mode_mismatch` and answers `quarantined` (AC-11)

#### Scenario: Failure: a consult cites no evidence
- **WHEN** an accepted consult carries no evidence reference for the whole consult or for any AI turn
- **THEN** the record shows "no evidence references", and the consult is selected for review whatever the sample

### Requirement: AC-04 A consult record is AI-generated communication, never a diagnosis or a clinical fact of record
openChart SHALL classify every consult record, and every AI turn and summary in it, as AI-generated communication. A consult record SHALL NOT become, create or update a diagnosis, problem, condition, order, prescription, treatment plan, encounter, intake statement, billable fact or any other clinical fact of record. An AI assessment or next step in a consult SHALL be shown as the AI's, and not as a clinician's or the chart's finding. In `advice_only` mode the AI content gives information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66). Its next steps mean how to get care and general self-care information, such as "see your doctor", "book a visit" or "go to urgent care", and never a treatment instruction for the patient's own condition (ruling 81). Whatever its text says, a consult record is never a diagnosis or a clinical fact of record.

**Label.** Every display of a consult record, to a clinician or to the patient, SHALL carry a label that states at least: that an AI system wrote it, naming the source system; that it gives information, an assessment and next steps only; that it is not a diagnosis and not a treatment instruction; that it was given without a clinician's prior sign-off; and its review status. The reference wording, which the recorded legal review confirms (`design.md`, review topic 6), is: "AI consult record from <source system>. Information, assessment and next steps only; not a diagnosis or a treatment instruction. Given without a clinician's prior sign-off. Review: <status>."

This is consistent with the ratified `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority": patient turns stay patient-reported, and AI output is a third class that records no assertion over them (tensions AT-1 and AT-2 record the reading this relies on). A consult record is not an encounter, a diagnosis or a procedure, so CF-02 and CF-06 of `define-openpractice-boundary` keep reporting `no_billable_facts`.

**Ruling 80.** A consult record is information (ruling 80, clause 9), never a decision. Whatever its text says, it is not an attempted decision recorded as a recommendation under AW-16, and it carries no `not_authorized_decision` marker: the label above already says that it is not a diagnosis or a treatment instruction (design call AD-53). It is kept on MI-12's clinical communication record, not as the foundation's `information` record kind. That kind holds only a clinical note's content (`clinicalNoteContent`) or a document (`documentContent`) from a writer without the authority to sign it, marked not signed off (its AN-06 and AN-14, and its design calls CD-63 and CD-65). A consult record is neither, was never submitted for signing, and its AC-04 label says what it is; the foundation's AN-06 leaves the consult record closed in this change's own contract. Its published shape is this contract's `consultWrite.exchange` and `summary`, closed and pinned by this contract's digest, as the foundation's AN-06 requires of every kind of record of information: turns of text with display-only attachments, and a summary of text, with no structured field that could carry an order (design call AD-53). Text in a consult never creates, counts as or authorizes a decision. Attachments are opaque: openChart never parses or imports them and only displays them, and their media types are `text/plain`, `application/pdf`, `image/png` and `image/jpeg`, the foundation's `documentAttachment` list (its AN-06 and design call CD-65). The only writes on this path that become the foundation's information record are an `act.write` declared `clinical_note` whose content is note content and one declared `document` whose content is the foundation's document shape (AW-16), once it passes the consent and grant checks (AW-06).

#### Scenario: Failure: an AI turn uses diagnosis language and a consumer reads it as a diagnosis
- **WHEN** a consult's AI turn names a condition, contrary to ruling 66, and a consumer tries to treat it as a diagnosis of record
- **THEN** no condition, problem or statement is created, and the text stays labelled AI-generated communication

#### Scenario: Failure: a consult record would be shown without its label
- **WHEN** a clinician or patient view would show a consult record without the label this requirement states
- **THEN** openChart does not show the record without the label

#### Scenario: Failure: billable facts are read after a consult
- **WHEN** openPractice reads clinical facts for a linked patient after an AI consult was recorded
- **THEN** the read returns `no_billable_facts`

### Requirement: AC-05 In advice-only mode, diagnosis language, treatment directives and act-like content create nothing, and a declared advice-scope breach is always reviewed
Under an `advice_only` grant, the AI system gives information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66). Its next steps mean how to get care and general self-care information, such as "see your doctor", "book a visit" or "go to urgent care", and never a treatment instruction for the patient's own condition (ruling 81). It may not prescribe, order, change a treatment plan or record a diagnosis of record (ruling 56). Once Tier 2 is in force, openChart SHALL record every `act.write` under an `advice_only` grant as a recommendation with `path_reason` `mode_not_permitted`; until then it records every `act.write` as a recommendation with `tier2_not_in_force`, which the precedence of AW-06 reports first (AA-01, AW-16). When a consult's exchange contains content that presents itself as an order, a prescription, a treatment-plan change or a diagnosis of record, openChart SHALL keep it in the consult record as AI-generated communication, shown as not accepted as a clinical act, and SHALL create no clinical act from it. This matches `define-clinical-message-inbox` MI-26 and its design call MD-20. Such content is not additionally marked `not_authorized_decision`, and it is not a recommendation record: openChart does not parse consult text (AD-31), and the consult's label and the `advice_scope_breach` review put it in front of a clinician (design call AD-53). A clinician who wants to act on it makes a decision of their own, signed off as ruling 151 requires.

openChart SHALL NOT parse, classify or rewrite consult text to enforce rulings 66 and 81 (design call AD-31). It SHALL select for review every consult that the source system declares with the built-in code `advice_scope_breach` (AC-07). A reviewer who finds diagnosis language, a treatment directive, or a next step that is not how to get care or general self-care information, in advice-only content SHALL record the finding `advice_scope_breach` (AC-08). Either way, the content stays in the consult record as AI-generated communication and creates no fact of record.

#### Scenario: Failure: an advice consult tells the patient a prescription was issued
- **WHEN** an AI turn in an advice-only consult says that a medicine has been prescribed
- **THEN** the turn stays in the consult record, labelled AI-generated and not accepted as a clinical act, no prescription is created, and the consult is selected for review as content held under AC-05 (AC-07)

#### Scenario: Failure: the source system declares an advice-scope breach
- **WHEN** a `consult.write` carries the review flag `advice_scope_breach` and the review sample would not have selected it
- **THEN** openChart records the consult, selects it for review with `advice_scope_breach` as the cause, and creates no fact of record

#### Scenario: Failure: a reviewer finds a treatment directive
- **WHEN** a clinician reviewing a sampled advice-only consult finds that an AI turn told the patient to take a medicine at a stated dose
- **THEN** the clinician records the finding `advice_scope_breach`, the medical director is alerted at once, and the consult stays AI-generated communication

### Requirement: AC-06 Every consult is visible to the patient's doctor
Every accepted consult record SHALL be visible to every clinician authorized for that patient's chart, on mobile or workstation (ruling 35). openChart SHALL list each new consult for the patient's responsible clinician where openChart records one. Where it records none, it SHALL list it for the medical director (design call AD-12). Consults selected for review, and AI act attempts linked to a consult, whether refused or recorded as recommendations, SHALL be listed with a distinct marker. Refused consult writes SHALL be visible to the medical director as integration exceptions holding only identifiers and coded causes. A consult that fails a grant check is not refused: it is kept as a quarantined consult and listed for the responsible clinician (AC-11), and the medical director also sees an integration exception holding only identifiers and the coded cause. A refused consult that declared the emergency indicator or `red_flag` SHALL also be listed urgently, without content, as AW-06 states, so that a clinician knows to contact the patient.

#### Scenario: Failure: the patient has no responsible clinician recorded
- **WHEN** a consult is recorded for a patient for whom openChart records no responsible clinician
- **THEN** the consult is listed for the medical director and is visible to every clinician authorized for the chart

#### Scenario: Failure: a consult write fails the grant check for an expired grant
- **WHEN** a consult write fails the grant checks with `grant_expired`
- **THEN** it is kept as quarantined AI communication and listed for the responsible clinician, its receipt says `quarantined` (AC-11), and the medical director sees an integration exception holding only the identifiers and the coded cause

### Requirement: AC-07 openChart selects consults for review by the medical director's sample and always-review categories
openChart, not the AI system, SHALL select consults for clinician review (ruling 57). It SHALL select:
- every consult that matches an always-review category in the grant's review policy, including any category the source system declared in `review_flags`;
- every consult that matches a built-in always-review trigger, which the medical director cannot remove (design call AD-11): the emergency indicator is set, or absent and so counted as set (design call AD-63); the consult has no evidence reference at all; the consult is linked to an act attempt that was refused or recorded as a recommendation, or contains content held under AC-05; the source system declared the built-in code `red_flag` or `advice_scope_breach` in `review_flags`; the consult is quarantined in the chart (AC-11); or it was released from the hold, whoever released it, and it stays on the clinician's review list until a clinician has read it (ruling 201), which this change records as a review under AC-08 (design call AD-65);
- a sample of the remaining consults, at the rate the review policy sets, by a selection the AI system cannot predict or influence.

openChart SHALL also select, always, every information record that an AI adds through this path and every information write quarantined in the chart (AW-16; design call AD-69, PROPOSED). openChart SHALL record, for each consult, whether it was selected, why, and the review policy version that applied.

#### Scenario: Failure: the AI system declares a high-risk category
- **WHEN** a consult carries a review flag that the review policy lists as always-review
- **THEN** openChart selects it for review whatever the sample rate, and records the category as the cause

#### Scenario: Failure: the sample rate is zero
- **WHEN** the review policy's sample rate is zero and a consult carries the emergency indicator
- **THEN** openChart still selects the consult for review under the built-in trigger

### Requirement: AC-08 Review status, reviewer and outcome are recorded by a named clinician, and an overdue review escalates
Each consult record SHALL carry a review status: `not_selected`, `selected`, `in_review` or `reviewed`. A review SHALL be recorded only by a named clinician holding a consult review grant in force (AG-11), signed off as below, with the grant version relied on, the outcome (`concur`, `concur_with_note`, `follow_up_required` or `unsafe`), an optional note, and the time (design call AD-25). A review attempted without that grant takes no effect, is kept as a review attempt and is never refused (AG-11; design call AD-59). No AI system and no agent SHALL record, change or close a review. A review SHALL be immutable; a later view SHALL be a new review event. The same review applies to an information record that an AI adds through this path (AW-16; design call AD-69, PROPOSED). One review MAY cover a consult and the AI notes and documents of the same patient that name it in `consult_ref`: the reviewer names each record the review covers, its sign-off statement carries the content digest of each, and each record so named counts as reviewed by it, each keeping its own rule for what the source is told (design call AD-69, PROPOSED).

A selected consult that is not reviewed within the review policy's window SHALL escalate to the medical director, who keeps being alerted until it is reviewed (design call AD-13). A quarantined consult uses AC-11's fixed window and fallback recipients instead, because it may have no grant and no medical director. An `unsafe` outcome SHALL alert the medical director at once and mark a clinician follow-up as owed to the patient. openChart SHALL report each outcome to the AI system as a `consult.reviewed` code only (design call AD-21), except for a quarantined consult (AC-11), whose review is never reported. With any outcome, the reviewer MAY record the finding `advice_scope_breach` (ruling 66), which SHALL alert the medical director at once. In contract 1.0 the finding stays in openChart, and `consult.reviewed` carries the outcome code only (design call AD-31).

**Ruling 158.** A clinician's review of an AI consult needs the practitioner's sign-off: "Yes for both. No for inbox housekeeping such as taking or reassigning an item." It is made as the foundation's CA-04 states, in openChart, in the reviewer's own logged-in session, with their openWallet and openSig, over the sign-off statement with a single-use challenge (rulings 151 and 186), under the AG-11 grant, and both records of the reviewer's licence must hold (ruling 160; the foundation's AU-03; design call AD-54). The sign-off statement is the one CA-04 defines, over the review record this requirement defines: its identifier and version, the patient, the record class `ai_consult_record`, the action `review`, the signer, the attestation, the digests of its content and provenance, the time and the challenge (the foundation's AU-02 and its design call CD-50, PROPOSED). Housekeeping needs no sign-off: taking a consult into review, reassigning it, and acknowledging a listing or an alert. A review still creates no act and never turns the consult into a decision (AC-04). Until openWallet and openSig can do their part, no review can be made as a real decision (ruling 152). A review recorded before then follows the foundation's rule for a sign-off that fails in a way its author can cure (its AN-14 and CA-04): it is kept as the reviewer's draft review, readable with the consult; the attempt is recorded in its trail and the reviewer is told at once; the consult's review status does not change; the draft counts as no review for selection, escalation and the window; and it is never reported to the source. The reviewer signs it off once the sign-off can be made (design call AD-67, PROPOSED). A draft review's safety findings do not wait for the sign-off: an `unsafe` outcome or an `advice_scope_breach` finding recorded in a draft alerts the medical director at once, and an `unsafe` outcome marks a clinician follow-up as owed to the patient, as a signed review's would (design call AD-67, PROPOSED). Meanwhile, because a draft counts as no review, every selected consult and every consult quarantined in the chart escalates to the medical director when its window passes, and keeps re-alerting until a review is signed off. With gate (e) no mode is switched on for patients before then (AG-04; ruling 207), so what arrives meanwhile is test traffic, in a deployment that the foundation's design call CD-69 keeps to synthetic patients; anything else is quarantined for want of a grant in force and escalates the same way. A review attempted without the AG-11 grant is a failure of authority, kept as AG-11 states (design call AD-59).

#### Scenario: Failure: an agent tries to record a review
- **WHEN** an AI agent tries to record a review outcome on a consult
- **THEN** the attempt takes no effect: openChart keeps it as a review attempt marked not an authorized decision, with `no_decision_authority`, and the review status is unchanged (AG-11)

#### Scenario: Failure: a review is recorded before openWallet and openSig can do their part
- **WHEN** a clinician holding the AG-11 grant records a review outcome while openWallet and openSig cannot yet support a sign-off
- **THEN** openChart keeps it as the reviewer's draft review, records the attempt in its trail and tells the reviewer at once, leaves the consult's review status unchanged, keeps the consult in its window and escalation, and reports nothing to the source

#### Scenario: Failure: a draft review finds the advice unsafe
- **WHEN** a clinician holding the AG-11 grant records a review with outcome `unsafe` while openWallet and openSig cannot yet support a sign-off
- **THEN** the medical director is alerted at once and a follow-up is marked owed to the patient, while the review stays a draft, the consult's review status is unchanged, and nothing is reported to the source

#### Scenario: A clinician takes a consult into review
- **WHEN** a clinician takes a selected consult into review, or reassigns it to another clinician
- **THEN** openChart records it as housekeeping, with no sign-off, and the consult's review status becomes `in_review`

#### Scenario: Failure: a selected consult is not reviewed in time
- **WHEN** a selected consult's review window passes with no review
- **THEN** openChart escalates it to the medical director and keeps re-alerting until a clinician records a review

#### Scenario: Failure: a reviewer finds the advice unsafe
- **WHEN** a clinician records the outcome `unsafe`
- **THEN** the medical director is alerted at once, a follow-up is marked owed, and the AI system receives `consult.reviewed` with outcome `unsafe` and no text

### Requirement: AC-09 openChart records consults after delivery and is never a prior sign-off
AI answers reach the patient without a prior clinician sign-off (rulings 57 and 66). openChart SHALL NOT sit in the delivery path of an AI answer and SHALL NOT approve, hold or release delivery. Each consult record SHALL say that the answer was delivered without a prior clinician sign-off.

openChart SHALL check a consult write against the grant version that was in force when the consult ended, and that version's state then (design call AD-5). It SHALL read both at the consult's `ended_at` from the grant's versions and their state history (AG-01), never from the grant's current state. A consult that ended while the grant was active SHALL be recorded even if the grant was paused, narrowed or expired before the write arrived. A consult that ended while no grant was active SHALL NOT be accepted: it is kept as quarantined AI communication under AC-11, with `quarantine_cause` `no_current_grant`, `grant_paused`, `grant_expired` or `grant_revoked`, answered `quarantined`, and shown to the medical director as an integration exception under AC-06. It is never refused for this (ruling 80, clause 18). Where the write gives no `ended_at` that AW-15 uses, the consult is judged at its `received_at` (design call AD-70). An AI's note or document is also judged at its receipt, because the AI adds it when it sends it (AW-06; design call AD-69).

#### Scenario: Failure: a consult arrives after a pause
- **WHEN** a consult ended at 10:00, the medical director paused the grant at 10:05, and the write arrives at 10:10
- **THEN** openChart records the consult under the grant version in force at 10:00, whose state history shows it `active` then, and the record shows that the grant has since been paused

#### Scenario: Failure: a consult happened while the grant was paused
- **WHEN** a consult ended at 10:20, after the 10:05 pause
- **THEN** openChart keeps it as quarantined AI communication with `quarantine_cause` `grant_paused` and answers `quarantined` (AC-11), and the medical director sees the integration exception

#### Scenario: Failure: a consult ended during a pause that has since been lifted
- **WHEN** the grant was paused at 10:05 and resumed at 10:30, a consult ended at 10:20, and its write arrives at 10:40
- **THEN** openChart reads from the state history that the grant was `paused` at 10:20 and keeps the consult as quarantined AI communication with `quarantine_cause` `grant_paused` (AC-11), although the grant is `active` when the write arrives

### Requirement: AC-10 A consult with an emergency indicator is recorded, always reviewed and shown urgently, and is never AI emergency management
An AI never manages an emergency in any mode (ruling 61). When a consult write carries the emergency indicator, openChart SHALL record it, select it for review (AC-07), list it for the patient's responsible clinician and the medical director with an urgent marker, and show where the source system routed the patient. openChart SHALL NOT treat any part of the consult as emergency management by the AI, and SHALL NOT record it as a clinical act (design call AD-22).

#### Scenario: Failure: an emergency consult arrives
- **WHEN** a consult write carries the emergency indicator and records that the patient was directed to emergency care
- **THEN** openChart records the consult, selects it for review, lists it urgently for the responsible clinician and the medical director, and creates no clinical act

### Requirement: AC-11 A consult or an AI's information that fails a grant or consent check is quarantined in the chart, always reviewed and never accepted, and a write whose AI is not identified, or whose parties the writer's registration does not cover, is held outside the chart
**Two kinds of quarantine.** openChart SHALL keep two kinds of quarantine apart. A consult, or an AI's note or document kept as information (AW-06), that fails a grant check or carries no consent reference is quarantined in the chart: recorded on the patient's record, marked not accepted, and reviewed (ruling 90, and ruling 199 for a consult with no consent reference; for information, design call AD-69, PROPOSED). A write whose AI cannot be identified, or whose source system the writer's registration does not cover (tension AT-20), is held in quarantine outside the chart and is no part of the chart until it is released (ruling 194). These are the two senses that the foundation's AN-01 defines, and its minimum for a held item applies only to the second.

When a `consult.write` passes steps 1 to 6 of AW-06's precedence and its AI check, and fails a check at step 8, openChart SHALL NOT refuse it (ruling 80, clause 18), and SHALL keep the consult in full as quarantined AI communication, in the chart (ruling 90; design call AD-33). Step 8 is the consent step, `consent_ref_missing` (design call AD-62, PROPOSED), or any grant check of AG-06: `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `approver_mismatch` or `legal_review_mismatch`. The AI's answer has already reached the patient (rulings 57 and 66), and the patient's doctor must be able to see what was said. Only such a write qualifies, because its writer and its AI are identified, its content is intact, its context is operational and its patient is resolved through an existing link.

A quarantined consult SHALL:
- hold what an accepted consult record holds under AC-01 to AC-03, on MI-12's clinical communication record with origin `ai_consult`, carrying the quarantined mark below;
- carry, on every display, the label of AC-04 and a quarantine label that states its coded cause: for `no_current_grant`, `grant_paused`, `grant_expired` or `grant_revoked`, "Not accepted: delivered without a current grant (<code>)"; for `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `approver_mismatch` or `legal_review_mismatch`, "Not accepted: delivered under an authority that does not match the practice's grant (<code>)"; for `consent_ref_missing`, "Not accepted: delivered with no consent reference (consent_ref_missing)";
- be readable by every clinician authorized for that patient's chart and by the medical director, through an authenticated openChart session on mobile or workstation, as AC-06 provides for accepted consults, and by nobody else: not by the source system, openPractice or the administrative role that the foundation's AU-01 names. A receipt or readback tells the source its state and codes only (AW-12);
- be selected for review whatever the sample (AC-07), with a review window fixed in openChart that depends on no grant: 24 hours, or 1 hour when its emergency indicator is set or its `review_flags` carry `red_flag` (design call AD-36). A review policy MAY shorten these windows and SHALL NOT lengthen them;
- be listed for the patient's responsible clinician and for the medical director. Where openChart records no responsible clinician, or no AU-01 designation is in force, it SHALL be listed for every clinician authorized for that patient's chart, and the administrative role that the foundation's AU-01 names SHALL receive an alert that carries only an opaque reference and a coded cause (design call AD-39);
- be listed urgently for those recipients when its emergency indicator is set or its `review_flags` carry `red_flag`;
- escalate when its window passes with no review: to the medical director and, where none is designated, to every clinician authorized for the chart and to the administrative role that the foundation's AU-01 names, re-alerting until a review is recorded. No timer or default SHALL close it;
- never be a diagnosis or a clinical fact of record (AC-04), and never become an accepted consult record through a later grant, approval or edit.

**An AI's information quarantined in the chart (design call AD-69, PROPOSED).** An `act.write` whose content is information under AW-06 and that fails a check at step 8 is quarantined in the chart in the same way. It is kept in full on this change's record of the write, on the patient's record, marked quarantined with its cause. It is an addition, a record of information that this change keeps, and never the foundation's information record, nor one later through a grant, approval or edit. Every point of the list above applies to it as to a quarantined consult, with AW-09's labels of AI authorship in place of AC-04's: its quarantine label, who may read it, its selection for review with the fixed window, its listing and fallback recipients, its urgent listing, its escalation, and its review under AC-08. Its receipt is `quarantined` with its `quarantine_cause` and `record_ref`, and a readback answers `found` with `record_state` `quarantined`.

A quarantined consult SHALL NOT count as an accepted record for the AI system. Its receipt is `quarantined`, with its `quarantine_cause` and its `record_ref`, so that the writer is told at once that the consult was kept and not accepted (design call AD-52). A readback that names it is answered `found` with `record_state` `quarantined`, by codes and digests only (AW-12), and no `consult.reviewed` is sent for it. A repeat of the same `consult_id` and `consult_version` with identical content SHALL be answered `duplicate`, with the original `record_ref` and `quarantine_cause`, and add no second copy (AW-05). A repeat with a different content digest SHALL NOT be refused: it is checked as a new write and kept, flagged `submission_ref_conflict`; the first quarantined copy SHALL stay unchanged, and an integration exception SHALL hold only identifiers and the coded cause (AW-05). A consult quarantined with `consent_ref_missing` is also flagged to the medical director with identifiers and the coded cause only, as an incident to look into (ruling 199; design call AD-62). A consult refused at steps 1 to 6, and every write refused at step 2 under a manual suspension or a deregistration (AW-13), SHALL store no clinical content (AW-06). An `act.write` whose content is not information and that fails a check at steps 7 to 9 is a recommendation under AW-16, not quarantined in the chart.

**A write held outside the chart (ruling 194; design calls AD-60 and AD-65).** A `consult.write` or an `act.write` that passes steps 1 to 6 of AW-06 and whose `on_behalf_of` is missing or cannot be read in the form AW-02 gives, or that names its AI without an `openwallet_id`, `model` or `model_version`, or with a value outside its form, or with an `openwallet_id` that the writer's registration does not cover, or names a source system that registration does not cover, SHALL be held in quarantine outside the chart, with the `quarantine_cause` of AW-06's AI check: `ai_not_identified`, `openwallet_id_missing`, `source_system_not_covered` or `openwallet_id_not_covered`. Ruling 194 rules this for a consult whose AI's openWallet ID is missing or not covered, ruling 201 who may release a held consult, and ruling 202 who may dismiss one; the rest is PROPOSED. A held write SHALL meet every point of the foundation's AN-01 minimum for a held item:
- **kept:** it is kept as it arrived, with its writer, its time of arrival and why it is held, in this change's record of held writes, and is never edited or deleted; an act is never written as a recommendation while it is held;
- **the writer told at once:** its receipt is `quarantined` with the `record_ref` and the cause, this path's `held_in_quarantine`;
- **not an addition while held:** it is no part of the chart, has no effect, is never published or exposed through an interoperability read, and nothing counts it: no clinical check, list or bill, and not AW-13's cap;
- **in front of a clinician:** it is readable, marked held because a party it names is not covered, by every clinician authorized for the patient's chart and by the medical director, and is listed, selected for review and escalated as this requirement provides for a quarantined consult, with its fixed window;
- **the administrative role told, not reading:** the practice's administrative role receives an alert carrying the AI's identification, its `openwallet_id`, `model` and `model_version` where given in their form, the writer (`added_by`) and the source system, and the cause, so that it can fix the registration or, for `openwallet_id_missing` and `ai_not_identified`, take the write up with the writer's operator so that the source resends it corrected (AW-05), and no patient and no clinical content. A value given as `openwallet_id`, `model` or `model_version` outside its form is not shown, nor is any party of an `on_behalf_of` this path cannot read: the alert says only which value is malformed, or that the parties could not be read (AW-07). It does not read the held write (the foundation's AN-01, which answers tension AT-19);
- **ended once, in one of three ways,** each recorded on the held write with who, when and the reference of any record it led to. An ending is final: a held write ends once, an ended write is not released, recorded or dismissed again, and no two additions carry the same `held_item_ref`, which the foundation's verifier checks (its AN-01 and CA-08). Until it ends, its listing stays open and escalates:
  - **released into the chart:** only a held write whose `openwallet_id` the writer's registration now covers, and whose source system it covers, can be released, and only while the writer is identified, registered for the practice and not suspended. The administrative role or a clinician releases it, as ruling 201 rules for a consult once the registration is fixed: "The administrative role or a clinician. Either way it stays on the clinician's review list until a clinician has read it." For a held act, the same is PROPOSED. **Every check as of the release, each judging the fact it records** (the foundation's AN-01; AC-09): every check of AW-06 from step 2 on is made at the release. The writer's identification, registration and suspension, the AI check, the context and the patient link are judged as they stand at the release, and the addition is dated by the release: its `received_at` is the time openChart added it, and a time AW-15 supplies is the held write's first arrival. The grant is judged at the time the grant check records: for a consult, the grant version in force when the consult ended and that version's state then, read at its `ended_at` as AC-09 provides, because that is when the AI answered the patient under it; for an AI's note or document, the grant at its `occurred_at` and the grant's state at the release, which is its receipt (AW-06); for any other act, the grant in force at its receipt (AA-03), which for a released act is its release. Where a check would refuse the write, the release does not happen and the write stays held. The addition carries `released_from_quarantine`, with `held_item_ref`, `first_received_at`, `released_by` and `released_at` (AW-15). A consult is then accepted, or quarantined in the chart, by its grant checks; an act becomes a recommendation, or information, or, as information that fails step 8, is quarantined in the chart (AW-06, AW-16). A released consult stays on the clinician's review list until a clinician has read it, whoever released it (ruling 201), which this change records as a clinician's review under AC-08 (AC-07; design call AD-65), and a released act stays listed until a clinician adopts or declines it, or, where it became information, until a clinician has reviewed it (AW-16);
  - **recorded by a clinician:** a clinician writes a record of their own that states what the patient was told, naming the held write as its source, so that the content enters the chart under an identified human writer. That record is information, which records who wrote it (ruling 187);
  - **dismissed:** a clinician, never the administrative role, dismisses it, with a recorded reason about its content, as ruling 202 requires for a consult: "Only a clinician, with a recorded reason about its content. Deciding not to register that AI does not dismiss what it already told a patient." The reason is one from this path's closed list, PROPOSED: `duplicate_of_existing_record`, naming the record it duplicates, a corrected write among them (AW-05); `not_for_this_patient`, which restricts it from ordinary reading in this patient's context, raises a misdirected-delivery report to the administrative role with no clinical content, and tells the writer, so that the source can send it for the right patient; or `no_clinical_content`, for content with no clinical content at all. A dismissed write stays held, kept, and readable by those allowed to read it, marked held, which keeps it in front of a clinician (the foundation's AN-01);
- **when it cannot be released:** a held write with `openwallet_id_missing` or `ai_not_identified` can never be released, because nothing the practice registers can identify its AI (the foundation's AN-02), and the schema refuses a `held.ended` or a readback that reports one released; it ends only by a clinician's own record or by a dismissal. **How a correction gets in (design call AD-71, PROPOSED).** The source corrects the AI's identification and resends the write: AW-05 does not answer such a resend `duplicate`, but checks it as a new write, keeps it as whatever that makes it, and links it to the held write, which is flagged as having a corrected write, so that a clinician can dismiss the held write as `duplicate_of_existing_record`, naming the new record. This is how a correction gets in; the held write itself is never edited or released. A write whose AI the administrative role decides not to register ends the same two ways: that decision is the administrative role's and is never by itself a reason to dismiss, because it does not dismiss what the AI already told a patient (ruling 202); the write stays in front of a clinician, flagged as one that can no longer be released, and ends by a clinician's own record or by a dismissal for a reason about its content.

**What the source learns.** openChart SHALL tell the writing source how a held write ended, once, with a `held.ended` message, delivered durably under AW-08: `released`, with the reference and state of the record it became; `recorded_by_clinician`; or `dismissed`, with the reason. A readback of the held write reports `held` while it is held, and its ending after (AW-12). A resend of the held write's identifiers with the same content digest is answered `duplicate` with `first_result` `quarantined`, the held cause and the held write's `record_ref`, before and after its ending alike, and changes nothing: it neither reopens an ended hold nor starts another. The one exception is a corrected resend of a write held with `openwallet_id_missing` or `ai_not_identified`, whose `on_behalf_of` differs, which is checked as a new write (AW-05). The source reads the ending from `held.ended` or a readback. A resend with a different content digest is a new write, flagged `submission_ref_conflict` (AW-05).

**The quarantine in the chart is not a hold.** A consult quarantined in the chart for a grant check, or for want of a consent reference, is a marked addition on MI-12's record, not a held item, and the foundation's AN-01 minimum for a held item does not apply to it. It is kept, its writer is told, it has no effect, it is never published or exposed through an interoperability read, it never counts as an accepted record, and it ends by its review under AC-08, as ruling 90 and design call AD-33 keep it. It is never released into the chart as an accepted record.

**Who reviews it.** Every item that openChart always selects for review is reviewed under AC-08 by a holder of the AG-11 grant: a consult selected by an always-review category or a built-in trigger (AC-07), a consult or an AI's note or document quarantined in the chart, a held write, and every information record an AI adds through this path (AW-16). When no person in the practice holds an AG-11 grant in force, because no AU-01 designation is in force, none has been recorded or every one has lapsed, each such item SHALL also be listed for the medical director, where one is designated, and any named person holding the `clinician` role under the foundation's AU-01 and authorized for that patient's chart MAY record its review, signed off as AC-08 states, and the review SHALL be marked as made without a review grant (design calls AD-39 and AD-73; tension AT-13). The rule fails towards a clinician seeing and reviewing the item. AG-04 switches no mode on while nobody holds the grant (its gate (f)), so the fallback serves a practice whose last grant has lapsed.

**The quarantined mark.** MI-12's record carries three fields, present only for origin `ai_consult` (design call AD-38):
- `ai_consult_state`: `accepted` (an AC-01 consult record) or `quarantined`;
- `quarantine_cause`: present only when `quarantined`; one of the nine grant-check codes above, or `consent_ref_missing`. A held write's cause, `ai_not_identified`, `openwallet_id_missing`, `openwallet_id_not_covered` or `source_system_not_covered`, is kept on this change's record of held writes, not on MI-12's record, because a held write is not in the chart;
- `quarantine_grant_checked`: present only when `quarantined` and a grant existed; the `grant_id` and `grant_version` openChart checked.

#### Scenario: Failure: a consult arrives with no current grant
- **WHEN** a `consult.write` for a linked patient passes every check before the grant checks, and the practice has no current grant
- **THEN** openChart answers `quarantined` with `quarantine_cause` `no_current_grant` and the `record_ref`, keeps the consult as quarantined AI communication labelled "Not accepted: delivered without a current grant (no_current_grant)", selects it for review, and lists it for the responsible clinician

#### Scenario: Failure: an emergency consult arrives after the grant expired
- **WHEN** a consult with the emergency indicator set ended after the practice's grant expired
- **THEN** openChart keeps it as quarantined AI communication with `quarantine_cause` `grant_expired`, answers `quarantined`, and lists it urgently for the responsible clinician and the medical director

#### Scenario: Failure: a red-flag consult names a configuration the grant does not record
- **WHEN** a consult whose `review_flags` carry `red_flag` names a configuration version that the grant in force does not record
- **THEN** openChart keeps it as quarantined AI communication with `quarantine_cause` `grant_mismatch`, answers `quarantined`, and lists it urgently for the responsible clinician and the medical director

#### Scenario: Failure: a consult refused before the grant checks stores nothing
- **WHEN** a `consult.write` is refused with reason `patient_link_unknown`
- **THEN** openChart stores no clinical content and keeps only the refusal record, because the consult cannot be tied to a patient

#### Scenario: Failure: an emergency consult is quarantined with no medical director and no responsible clinician
- **WHEN** no AU-01 designation is in force, openChart records no responsible clinician, and a consult with the emergency indicator set is quarantined
- **THEN** it is listed urgently for every clinician authorized for the patient's chart, its review is due within 1 hour, and the administrative role that the foundation's AU-01 names receives an alert carrying only an opaque reference and a coded cause

#### Scenario: Failure: a quarantined consult is not reviewed in time
- **WHEN** a quarantined consult's fixed window passes with no review
- **THEN** openChart escalates it to the medical director, or, where none is designated, to every clinician authorized for the chart and to the administrative role that the foundation's AU-01 names, and keeps re-alerting until a review is recorded

#### Scenario: Failure: no review grant can exist
- **WHEN** nobody in the practice holds an AG-11 grant, and a named person holding the `clinician` role and authorized for the patient's chart reviews a quarantined consult
- **THEN** openChart records the review, marked as made without a review grant

#### Scenario: Failure: a repeat of a quarantined consult carries different content
- **WHEN** a second write for a quarantined consult's `consult_id` and `consult_version` carries a different exchange
- **THEN** openChart does not refuse it: it checks the second write as a new write, keeps it flagged `submission_ref_conflict` with the first record and its digest, keeps the first quarantined copy unchanged, and records an integration exception holding only identifiers and the coded cause

#### Scenario: Failure: a consult is quarantined for a mismatch, not for want of a grant
- **WHEN** a consult is quarantined with reason `grant_mismatch` while a grant is in force
- **THEN** its label reads "Not accepted: delivered under an authority that does not match the practice's grant (grant_mismatch)", never "delivered without a current grant"

#### Scenario: Failure: the administrative role follows a quarantine alert
- **WHEN** a holder of the administrative role that the foundation's AU-01 names opens a quarantine alert
- **THEN** openChart shows only the opaque reference and the coded cause, and no consult content

#### Scenario: Failure: the grant is restored and the consult is re-sent
- **WHEN** the medical director approves a new grant version after a consult was quarantined, and the AI system re-sends the same consult
- **THEN** openChart answers `duplicate` with `first_result` `quarantined`, the original `record_ref` and `quarantine_cause` (AW-05), keeps the one quarantined copy, and never turns it into an accepted record

#### Scenario: Failure: a held consult is released once the registration covers its AI
- **WHEN** a consult was held with `openwallet_id_not_covered`, the named human then adds that openWallet ID to the relay's registration, and the administrative role releases the held consult
- **THEN** openChart records the release on the held write, applies every check as of the release, dates the consult record by its release with `released_from_quarantine` (`held_item_ref`, `first_received_at`, `released_by`, `released_at`), accepts or quarantines it by its grant checks read at the consult's `ended_at`, keeps it selected for review until a clinician reviews it, and sends `held.ended` `released`; the held write stays kept

#### Scenario: Failure: a clinician dismisses a held act sent for the wrong patient
- **WHEN** a clinician dismisses an `act.write` held with `openwallet_id_missing`, with the reason `not_for_this_patient`
- **THEN** openChart records the dismissal, who made it and when, restricts the act from ordinary reading in that patient's context, reports a misdirected delivery to the administrative role without content, sends `held.ended` `dismissed` with that reason, and the act stays held and kept, with no recommendation and no effect

#### Scenario: Failure: a held write with no openWallet ID is released
- **WHEN** the administrative role tries to release a consult held with `openwallet_id_missing`
- **THEN** the release is refused, and the consult stays held, in front of a clinician, until a clinician records it in a record of their own or dismisses it

#### Scenario: Failure: an AI's document arrives under a revoked grant
- **WHEN** an AI system whose grant was revoked before the document's `occurred_at` sends an `act.write` declared `document` whose content validates as the foundation's document shape
- **THEN** openChart keeps it in full, quarantined in the chart on this change's record with `quarantine_cause` `grant_revoked`, labelled "Not accepted: delivered without a current grant (grant_revoked)", selects it for review with the fixed window, lists it for the responsible clinician, answers `quarantined`, and never keeps it as the foundation's information record

#### Scenario: Failure: a write held because its AI was not identified would be released
- **WHEN** the administrative role tries to release a consult held with `ai_not_identified` because its AI carried no model version
- **THEN** the release is refused, and the consult stays held in front of a clinician until a clinician records it in a record of their own or dismisses it

#### Scenario: Failure: an ended held write would end again
- **WHEN** a clinician tries to dismiss a held write that was already released into the chart
- **THEN** the dismissal is refused, because an ending is final, and the released record is unchanged

#### Scenario: Failure: the administrative role tries to dismiss a held write
- **WHEN** a holder of the administrative role, who is not a clinician, tries to dismiss a held write
- **THEN** the dismissal is refused; only a clinician dismisses, and the write stays held

#### Scenario: Failure: the administrative role decides not to register the AI
- **WHEN** the administrative role records that it will not register the AI of a held consult
- **THEN** the consult stays held in front of a clinician, flagged as one that can no longer be released, until a clinician records it in a record of their own or dismisses it for a reason about its content

#### Scenario: Failure: the administrative role opens a held-write alert
- **WHEN** a holder of the administrative role opens the alert for a held write
- **THEN** openChart shows the AI's `openwallet_id`, model and model version where the write gave them in their form, the writer, the source system and the cause, and no patient and no clinical content

#### Scenario: Failure: a source resends a consult after it was released
- **WHEN** the source resends a held consult's identifiers with the same content after the consult was released
- **THEN** openChart answers `duplicate` with `first_result` `quarantined`, the held cause and the held write's `record_ref`, changes nothing, and a readback of that `record_ref` answers `released` with the new record's reference and state

#### Scenario: Failure: a source corrects the AI's identification and resends
- **WHEN** a consult was held with `ai_not_identified` because its AI's model was `syn model 2`, and the source resends the same `consult_id`, `consult_version` and exchange with the model in its form
- **THEN** openChart does not answer `duplicate`: it checks the resend as a new write, records it, links it to the held write and flags the held write as corrected, and the held write stays held, in front of a clinician, until a clinician dismisses it as `duplicate_of_existing_record`, naming the new record

#### Scenario: Failure: nobody holds the review grant when an AI's note is kept
- **WHEN** every AG-11 grant in the practice has lapsed, and an AI's note is kept as information
- **THEN** openChart lists it for the medical director as well as the responsible clinician, and a named clinician authorized for the chart may review it, marked as made without a review grant
