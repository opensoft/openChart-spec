## ADDED Requirements

### Requirement: AC-01 openChart records each AI consult on the clinical-communication record, with the full exchange
openChart SHALL record each accepted `consult.write` as a consult record. The consult record SHALL be the clinical communication record that MI-12 of `define-clinical-message-inbox` (openChart-spec#3, not yet on main) defines as the single definition of that record in openChart, with origin `ai_consult`, and SHALL keep MI-13's distinction of AI-authored content. This change cites MI-12 by requirement ID, adds the fields below to that record for this origin, and defines no second clinical communication record (design call AD-3). The handoff references of MI-12 are absent for this origin. This change defines no conversation retrieval; openChart's neutral `openchart-conversation-retrieval/1.0` belongs to `define-clinical-message-inbox` (ruling 69). Writing a consult record SHALL NOT require the inbox to be enabled, and SHALL NOT require openPractice.

The consult record SHALL hold the full exchange as written: every turn with its author type, time, text and attachment references, and the exchange's content digest. An AI-written summary MAY accompany it, labelled AI-authored, and SHALL never replace the exchange (design call AD-2). The record SHALL also hold the source system's conversation reference, so that an inbox item that names the same conversation can be associated with the consult record by reference. The inbox still files no copy (MI-24).

Tier 1 SHALL be buildable without any orders, prescriptions or diagnoses model in openChart. From `define-clinical-acts-foundation` (openChart-spec#5) it needs only the clinical roles and authority of AU-01 to AU-05, which that change's feature (1) builds (AG-02, AG-11). A recorded consult MUST NOT be silently overwritten or deleted. A continuation or correction SHALL be a new consult version that references its predecessor.

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
- the consent reference the write carried (design call AD-14);
- the consult's start and end times;
- the review flags the source system declared, the emergency indicator, and where the source system routed the patient.

openChart SHALL NOT fetch, store or re-host the evidence itself. An AI turn whose knowledge basis is `model_knowledge` SHALL be shown as resting on the model's own knowledge with no cited source. A consult with no evidence reference, neither for the whole consult nor for any AI turn, SHALL be recorded, shown as "no evidence references", and selected for review (AC-07).

#### Scenario: Failure: a patient turn claims a knowledge basis
- **WHEN** a `consult.write` gives a patient turn a knowledge basis or evidence references
- **THEN** openChart refuses it with reason `schema_invalid` and stores no clinical content

#### Scenario: Failure: the mode in force differs from the grant
- **WHEN** a `consult.write` states `limited_practice` as its mode in force while openChart's current grant is `advice_only`
- **THEN** openChart refuses it with reason `mode_mismatch`

#### Scenario: Failure: a consult cites no evidence
- **WHEN** an accepted consult carries no evidence reference for the whole consult or for any AI turn
- **THEN** the record shows "no evidence references", and the consult is selected for review whatever the sample

### Requirement: AC-04 A consult record is AI-generated communication, never a diagnosis or a clinical fact of record
openChart SHALL classify every consult record, and every AI turn and summary in it, as AI-generated communication. A consult record SHALL NOT become, create or update a diagnosis, problem, condition, order, prescription, treatment plan, encounter, intake statement, billable fact or any other clinical fact of record. An AI assessment or next step in a consult SHALL be shown as the AI's, and not as a clinician's or the chart's finding. In `advice_only` mode the AI content gives information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66). Whatever its text says, a consult record is never a diagnosis or a clinical fact of record.

**Label.** Every display of a consult record, to a clinician or to the patient, SHALL carry a label that states at least: that an AI system wrote it, naming the source system; that it gives information, an assessment and next steps only; that it is not a diagnosis and not a treatment instruction; that it was given without a clinician's prior sign-off; and its review status. The reference wording, which the recorded legal review confirms (`design.md`, review topic 6), is: "AI consult record from <source system>. Information, assessment and next steps only; not a diagnosis or a treatment instruction. Given without a clinician's prior sign-off. Review: <status>."

This is consistent with the ratified `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority": patient turns stay patient-reported, and AI output is a third class that records no assertion over them (tensions AT-1 and AT-2 record the reading this relies on). A consult record is not an encounter, a diagnosis or a procedure, so CF-02 and CF-06 of `define-openpractice-boundary` keep reporting `no_billable_facts`.

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
Under an `advice_only` grant, the AI system gives information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66), and may not prescribe, order, change a treatment plan or record a diagnosis of record (ruling 56). Once Tier 2 is in force, openChart SHALL refuse every `act.write` under an `advice_only` grant with reason `mode_not_permitted`; until then it refuses every `act.write` with `tier2_not_in_force`, which the precedence of AW-06 reports first (AA-01). When a consult's exchange contains content that presents itself as an order, a prescription, a treatment-plan change or a diagnosis of record, openChart SHALL keep it in the consult record as AI-generated communication, shown as not accepted as a clinical act, and SHALL create no clinical act from it. This matches `define-clinical-message-inbox` MI-26 and its design call MD-20.

openChart SHALL NOT parse, classify or rewrite consult text to enforce ruling 66 (design call AD-31). It SHALL select for review every consult that the source system declares with the built-in code `advice_scope_breach` (AC-07). A reviewer who finds diagnosis language or a treatment directive in advice-only content SHALL record the finding `advice_scope_breach` (AC-08). Either way, the content stays in the consult record as AI-generated communication and creates no fact of record.

#### Scenario: Failure: an advice consult tells the patient a prescription was issued
- **WHEN** an AI turn in an advice-only consult says that a medicine has been prescribed
- **THEN** the turn stays in the consult record, labelled AI-generated and not accepted as a clinical act, no prescription is created, and the consult is selected for review as a linked refused act (AC-07)

#### Scenario: Failure: the source system declares an advice-scope breach
- **WHEN** a `consult.write` carries the review flag `advice_scope_breach` and the review sample would not have selected it
- **THEN** openChart records the consult, selects it for review with `advice_scope_breach` as the cause, and creates no fact of record

#### Scenario: Failure: a reviewer finds a treatment directive
- **WHEN** a clinician reviewing a sampled advice-only consult finds that an AI turn told the patient to take a medicine at a stated dose
- **THEN** the clinician records the finding `advice_scope_breach`, the medical director is alerted at once, and the consult stays AI-generated communication

### Requirement: AC-06 Every consult is visible to the patient's doctor
Every accepted consult record SHALL be visible to every clinician authorized for that patient's chart, on mobile or workstation (ruling 35). openChart SHALL list each new consult for the patient's responsible clinician where openChart records one. Where it records none, it SHALL list it for the medical director (design call AD-12). Consults selected for review, and refused AI act attempts linked to a consult, SHALL be listed with a distinct marker. Refused consult writes SHALL be visible to the medical director as integration exceptions holding only identifiers and coded causes. A consult refused at the grant checks SHALL also be kept as quarantined AI communication and listed for the responsible clinician (AC-11). A refused consult that declared the emergency indicator or `red_flag` SHALL also be listed urgently, without content, as AW-06 states, so that a clinician knows to contact the patient.

#### Scenario: Failure: the patient has no responsible clinician recorded
- **WHEN** a consult is recorded for a patient for whom openChart records no responsible clinician
- **THEN** the consult is listed for the medical director and is visible to every clinician authorized for the chart

#### Scenario: Failure: a consult write is refused for an expired grant
- **WHEN** openChart refuses a consult write with reason `grant_expired`
- **THEN** the medical director sees an integration exception holding only the identifiers and the coded cause, and the consult itself is kept as quarantined AI communication and listed for the responsible clinician (AC-11)

### Requirement: AC-07 openChart selects consults for review by the medical director's sample and always-review categories
openChart, not the AI system, SHALL select consults for clinician review (ruling 57). It SHALL select:
- every consult that matches an always-review category in the grant's review policy, including any category the source system declared in `review_flags`;
- every consult that matches a built-in always-review trigger, which the medical director cannot remove (design call AD-11): the emergency indicator is set; the consult has no evidence reference at all; the consult is linked to a refused act attempt, or contains content held under AC-05; the source system declared the built-in code `red_flag` or `advice_scope_breach` in `review_flags`; or the consult is quarantined (AC-11);
- a sample of the remaining consults, at the rate the review policy sets, by a selection the AI system cannot predict or influence.

openChart SHALL record, for each consult, whether it was selected, why, and the review policy version that applied.

#### Scenario: Failure: the AI system declares a high-risk category
- **WHEN** a consult carries a review flag that the review policy lists as always-review
- **THEN** openChart selects it for review whatever the sample rate, and records the category as the cause

#### Scenario: Failure: the sample rate is zero
- **WHEN** the review policy's sample rate is zero and a consult carries the emergency indicator
- **THEN** openChart still selects the consult for review under the built-in trigger

### Requirement: AC-08 Review status, reviewer and outcome are recorded by a named clinician, and an overdue review escalates
Each consult record SHALL carry a review status: `not_selected`, `selected`, `in_review` or `reviewed`. A review SHALL be recorded only by a named clinician holding a consult review grant in force (AG-11), with the grant version relied on, the outcome (`concur`, `concur_with_note`, `follow_up_required` or `unsafe`), an optional note, and the time (design call AD-25). No AI system and no agent SHALL record, change or close a review. A review SHALL be immutable; a later view SHALL be a new review event.

A selected consult that is not reviewed within the review policy's window SHALL escalate to the medical director, who keeps being alerted until it is reviewed (design call AD-13). A quarantined consult uses AC-11's fixed window and fallback recipients instead, because it may have no grant and no medical director. An `unsafe` outcome SHALL alert the medical director at once and mark a clinician follow-up as owed to the patient. openChart SHALL report each outcome to the AI system as a `consult.reviewed` code only (design call AD-21), except for a quarantined consult (AC-11), whose review is never reported. With any outcome, the reviewer MAY record the finding `advice_scope_breach` (ruling 66), which SHALL alert the medical director at once. In contract 1.0 the finding stays in openChart, and `consult.reviewed` carries the outcome code only (design call AD-31).

#### Scenario: Failure: an agent tries to record a review
- **WHEN** an AI agent tries to record a review outcome on a consult
- **THEN** the action is refused and the review status is unchanged

#### Scenario: Failure: a selected consult is not reviewed in time
- **WHEN** a selected consult's review window passes with no review
- **THEN** openChart escalates it to the medical director and keeps re-alerting until a clinician records a review

#### Scenario: Failure: a reviewer finds the advice unsafe
- **WHEN** a clinician records the outcome `unsafe`
- **THEN** the medical director is alerted at once, a follow-up is marked owed, and the AI system receives `consult.reviewed` with outcome `unsafe` and no text

### Requirement: AC-09 openChart records consults after delivery and is never a prior sign-off
AI answers reach the patient without a prior clinician sign-off (rulings 57 and 66). openChart SHALL NOT sit in the delivery path of an AI answer and SHALL NOT approve, hold or release delivery. Each consult record SHALL say that the answer was delivered without a prior clinician sign-off.

openChart SHALL check a consult write against the grant version that was in force when the consult ended (design call AD-5). A consult that ended while the grant was active SHALL be recorded even if the grant was paused, narrowed or expired before the write arrived. A consult that ended while no grant was active SHALL be refused, with reason `no_current_grant`, `grant_paused`, `grant_expired` or `grant_revoked`, shown to the medical director as an integration exception under AC-06, and kept as quarantined AI communication under AC-11.

#### Scenario: Failure: a consult arrives after a pause
- **WHEN** a consult ended at 10:00, the medical director paused the grant at 10:05, and the write arrives at 10:10
- **THEN** openChart records the consult under the grant version in force at 10:00, and the record shows that the grant has since been paused

#### Scenario: Failure: a consult happened while the grant was paused
- **WHEN** a consult ended at 10:20, after the 10:05 pause
- **THEN** openChart refuses it with reason `grant_paused`, the medical director sees the integration exception, and the consult is kept as quarantined AI communication (AC-11)

### Requirement: AC-10 A consult with an emergency indicator is recorded, always reviewed and shown urgently, and is never AI emergency management
An AI never manages an emergency in any mode (ruling 61). When a consult write carries the emergency indicator, openChart SHALL record it, select it for review (AC-07), list it for the patient's responsible clinician and the medical director with an urgent marker, and show where the source system routed the patient. openChart SHALL NOT treat any part of the consult as emergency management by the AI, and SHALL NOT record it as a clinical act (design call AD-22).

#### Scenario: Failure: an emergency consult arrives
- **WHEN** a consult write carries the emergency indicator and records that the patient was directed to emergency care
- **THEN** openChart records the consult, selects it for review, lists it urgently for the responsible clinician and the medical director, and creates no clinical act

### Requirement: AC-11 A consult refused at the grant checks is kept as quarantined AI communication, always reviewed and never accepted
When openChart refuses a `consult.write` at step 8 of AW-06's precedence, after the write has passed steps 1 to 6, openChart SHALL keep the consult as quarantined AI communication (design call AD-33). Step 8 is any grant check of AG-06: `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `approver_mismatch` or `legal_review_mismatch`. The AI's answer has already reached the patient (rulings 57 and 66), and the patient's doctor must be able to see what was said. Only such a write qualifies, because its source is authenticated, its content is intact, its context is operational and its patient is resolved through an existing link.

A quarantined consult SHALL:
- hold what an accepted consult record holds under AC-01 to AC-03, on MI-12's clinical communication record with origin `ai_consult`, carrying the quarantined mark below;
- carry, on every display, the label of AC-04 and a quarantine label that states its coded cause: for `no_current_grant`, `grant_paused`, `grant_expired` or `grant_revoked`, "Not accepted: delivered without a current grant (<code>)"; for `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `approver_mismatch` or `legal_review_mismatch`, "Not accepted: delivered under an authority that does not match the practice's grant (<code>)"; for `source_cap_suspended`, "Not accepted: delivered by a source suspended after repeated quarantines (source_cap_suspended)";
- be readable by every clinician authorized for that patient's chart and by the medical director, through an authenticated openChart session on mobile or workstation, as AC-06 provides for accepted consults, and by nobody else: not by the source system, openPractice or the administrative role that the foundation's AU-01 names;
- be selected for review whatever the sample (AC-07), with a review window fixed in openChart that depends on no grant: 24 hours, or 1 hour when its emergency indicator is set or its `review_flags` carry `red_flag` (design call AD-36). A review policy MAY shorten these windows and SHALL NOT lengthen them;
- be listed for the patient's responsible clinician and for the medical director. Where openChart records no responsible clinician, or no AU-01 designation is in force, it SHALL be listed for every clinician authorized for that patient's chart, and the administrative role that the foundation's AU-01 names SHALL receive an alert that carries only an opaque reference and a coded cause (design call AD-39);
- be listed urgently for those recipients when its emergency indicator is set or its `review_flags` carry `red_flag`;
- escalate when its window passes with no review: to the medical director and, where none is designated, to every clinician authorized for the chart and to the administrative role that the foundation's AU-01 names, re-alerting until a review is recorded. No timer or default SHALL close it;
- never be a diagnosis or a clinical fact of record (AC-04), and never become an accepted consult record through a later grant, approval or edit.

A quarantined consult SHALL NOT count as an accepted record for the AI system. Its receipt is `refused`, with the grant reason and no `record_ref`. Its reference is never sent to the source system, a readback that names it is answered `not_found` (AW-12), and no `consult.reviewed` is sent for it. A repeat of the same `consult_id` and `consult_version` with identical content SHALL be refused the same way and add no second copy. A repeat with different content SHALL be refused with `conflicting_duplicate`; the first quarantined copy SHALL stay unchanged, and an integration exception SHALL hold only identifiers and the coded cause (AW-05). openChart SHALL also quarantine a consult with the emergency indicator or `red_flag` from a cap-suspended source that has passed steps 1 and 3 to 6 and whose grant checks pass, with the cause `source_cap_suspended` (AW-13). A consult refused at any other step, every write refused at step 2 under a suspension or deregistration (AW-13), and every refused `act.write` SHALL store no clinical content (AW-06).

**Who reviews it.** A quarantined consult is reviewed under AC-08 by a holder of the AG-11 grant. When no person in the practice holds an AG-11 grant in force, because no AU-01 designation is in force or none has been recorded, any named person holding the `clinician` role under the foundation's AU-01 and authorized for that patient's chart MAY record the review, and the review SHALL be marked as made without a review grant (design call AD-39; tension AT-13). The rule fails towards a clinician seeing and reviewing the consult.

**The quarantined mark.** MI-12's record carries three fields, present only for origin `ai_consult` (design call AD-38):
- `ai_consult_state`: `accepted` (an AC-01 consult record) or `quarantined`;
- `quarantine_cause`: present only when `quarantined`; one of the nine step-8 reason codes above, or `source_cap_suspended` (AW-13);
- `quarantine_grant_checked`: present only when `quarantined` and a grant existed; the `grant_id` and `grant_version` openChart checked.

#### Scenario: Failure: a consult arrives with no current grant
- **WHEN** a `consult.write` for a linked patient passes every check before the grant checks, and the practice has no current grant
- **THEN** openChart answers `refused` with reason `no_current_grant` and no `record_ref`, keeps the consult as quarantined AI communication labelled "Not accepted: delivered without a current grant (no_current_grant)", selects it for review, and lists it for the responsible clinician

#### Scenario: Failure: an emergency consult arrives after the grant expired
- **WHEN** a consult with the emergency indicator set ended after the practice's grant expired
- **THEN** openChart refuses it with reason `grant_expired`, keeps it as quarantined AI communication, and lists it urgently for the responsible clinician and the medical director

#### Scenario: Failure: a red-flag consult names a configuration the grant does not record
- **WHEN** a consult whose `review_flags` carry `red_flag` names a configuration version that the grant in force does not record
- **THEN** openChart refuses it with reason `grant_mismatch`, keeps it as quarantined AI communication, and lists it urgently for the responsible clinician and the medical director

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
- **THEN** openChart refuses it with reason `conflicting_duplicate`, keeps the first quarantined copy unchanged, and records an integration exception holding only identifiers and the coded cause

#### Scenario: Failure: a consult is quarantined for a mismatch, not for want of a grant
- **WHEN** a consult is quarantined with reason `grant_mismatch` while a grant is in force
- **THEN** its label reads "Not accepted: delivered under an authority that does not match the practice's grant (grant_mismatch)", never "delivered without a current grant"

#### Scenario: Failure: the administrative role follows a quarantine alert
- **WHEN** a holder of the administrative role that the foundation's AU-01 names opens a quarantine alert
- **THEN** openChart shows only the opaque reference and the coded cause, and no consult content

#### Scenario: Failure: the grant is restored and the consult is re-sent
- **WHEN** the medical director approves a new grant version after a consult was quarantined, and the AI system re-sends the same consult
- **THEN** openChart checks it against the grant in force when the consult ended (AC-09), refuses it again, keeps the one quarantined copy, and never turns it into an accepted record
