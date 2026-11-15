## ADDED Requirements

### Requirement: AC-01 openChart records each AI consult on the clinical-communication record, with the full exchange
openChart SHALL record each accepted `consult.write` as a consult record. The consult record SHALL be a clinical-communication record as `define-clinical-message-inbox` (not yet on main) defines it in MI-12 and MI-13, with origin `ai_consult`. This change adds the fields below to that record for this origin, and defines no second clinical-communication record (design call AD-3). The handoff references of MI-12 are absent for this origin. Writing a consult record SHALL NOT require the inbox to be enabled, and SHALL NOT require openPractice.

The consult record SHALL hold the full exchange as written: every turn with its author kind, time, text and attachment references, and the exchange's content digest. An AI-written summary MAY accompany it, labelled AI-authored, and SHALL never replace the exchange (design call AD-2). The record SHALL also hold the source system's conversation reference, so that an inbox item that names the same conversation can be associated with the consult record by reference. The inbox still files no copy (MI-24).

Tier 1 SHALL be buildable without any orders, prescriptions or diagnoses model in openChart. A recorded consult MUST NOT be silently overwritten or deleted. A continuation or correction SHALL be a new consult version that references its predecessor.

#### Scenario: An advice consult is recorded
- **WHEN** an AI system sends a schema-valid, authorized `consult.write` under an active `advice_only` grant for a linked patient
- **THEN** openChart records the full exchange and its digest on a clinical-communication record with origin `ai_consult`, and answers `accepted` with the `record_ref`

#### Scenario: Failure: the exchange does not match its digest
- **WHEN** a `consult.write` carries a `content_sha256` that does not equal the digest of its turns
- **THEN** openChart refuses it with reason `content_digest_mismatch` and stores no clinical content

#### Scenario: Failure: a user tries to file the consult again from an inbox item
- **WHEN** an inbox item names the same conversation and a user tries to file a copy of the exchange from it
- **THEN** the filing is refused, and the inbox item shows the association with the existing consult record

### Requirement: AC-02 AI authorship is always distinguishable from clinician-authored and patient-reported content
Every turn of a consult record SHALL carry an author kind: `patient`, `representative` or `ai`. A consult write SHALL NOT carry clinician-authored content. AI turns and the AI summary SHALL be recorded and shown as AI-authored, naming the source system, using MI-13's author kind `ai`. Patient and representative turns SHALL remain visibly patient-reported. A consult SHALL contain at least one AI turn. Nothing in a consult record SHALL be recorded, shown or delivered as clinician-authored.

#### Scenario: Failure: a turn claims clinician authorship
- **WHEN** a `consult.write` carries a turn with author kind `clinician`
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
openChart SHALL classify every consult record, and every AI turn and summary in it, as AI-generated communication. A consult record SHALL NOT become, create or update a diagnosis, problem, condition, order, prescription, treatment plan, encounter, intake statement, billable fact or any other clinical fact of record. An AI assessment, impression or recommendation in a consult SHALL be shown as the AI's, and not as a clinician's or the chart's finding.

This is consistent with the ratified `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority": patient turns stay patient-reported, and AI output is a third class that records no assertion over them (tensions AT-1 and AT-2 record the reading this relies on). A consult record is not an encounter, a diagnosis or a procedure, so CF-02 and CF-06 of `define-openpractice-boundary` keep reporting `no_billable_facts`.

#### Scenario: Failure: a consumer reads an AI assessment as a diagnosis
- **WHEN** a consult's AI turn says "this sounds like a tension-type headache" and a consumer tries to treat it as a diagnosis of record
- **THEN** no condition, problem or statement is created, and the text stays labelled AI-generated communication

#### Scenario: Failure: billable facts are read after a consult
- **WHEN** openPractice reads clinical facts for a linked patient after an AI consult was recorded
- **THEN** the read returns `no_billable_facts`

### Requirement: AC-05 In advice-only mode, content that presents itself as a clinical act is held as communication and creates no act
Under an `advice_only` grant, the AI system may inform, assess and recommend next steps, and may not prescribe, order, change a treatment plan or record a diagnosis of record (ruling 56). Once Tier 2 is in force, openChart SHALL refuse every `act.write` under an `advice_only` grant with reason `mode_not_permitted`; until then it refuses every `act.write` with `tier2_not_in_force`, which the precedence of AW-06 reports first (AA-01). When a consult's exchange contains content that presents itself as an order, a prescription, a treatment-plan change or a diagnosis of record, openChart SHALL keep it in the consult record as AI-generated communication, shown as not accepted as a clinical act, and SHALL create no clinical act from it. This matches `define-clinical-message-inbox` MI-26 and its design call MD-20.

#### Scenario: Failure: an advice consult tells the patient a prescription was issued
- **WHEN** an AI turn in an advice-only consult says that a medicine has been prescribed
- **THEN** the turn stays in the consult record, labelled AI-generated and not accepted as a clinical act, no prescription is created, and the consult is selected for review as a linked refused act (AC-07)

### Requirement: AC-06 Every consult is visible to the patient's doctor
Every accepted consult record SHALL be visible to every clinician authorized for that patient's chart, on mobile or workstation (ruling 35). openChart SHALL list each new consult for the patient's responsible clinician where openChart records one. Where it records none, it SHALL list it for the medical director (design call AD-12). Consults selected for review, and refused AI act attempts linked to a consult, SHALL be listed with a distinct marker. Refused consult writes SHALL be visible to the medical director as integration exceptions holding only identifiers and coded causes.

#### Scenario: Failure: the patient has no responsible clinician recorded
- **WHEN** a consult is recorded for a patient for whom openChart records no responsible clinician
- **THEN** the consult is listed for the medical director and is visible to every clinician authorized for the chart

#### Scenario: Failure: a consult write is refused for an expired grant
- **WHEN** openChart refuses a consult write with reason `grant_expired`
- **THEN** the medical director sees an integration exception with the identifiers and the coded cause, and no consult content

### Requirement: AC-07 openChart selects consults for review by the medical director's sample and always-review categories
openChart, not the AI system, SHALL select consults for clinician review (ruling 57). It SHALL select:
- every consult that matches an always-review category in the grant's review policy, including any category the source system declared in `review_flags`;
- every consult that matches a built-in always-review trigger, which the medical director cannot remove (design call AD-11): the emergency indicator is set; the consult has no evidence reference at all; the consult is linked to a refused act attempt, or contains content held under AC-05; or the source system declared a red flag;
- a sample of the remaining consults, at the rate the review policy sets, by a selection the AI system cannot predict or influence.

openChart SHALL record, for each consult, whether it was selected, why, and the review policy version that applied.

#### Scenario: Failure: the AI system declares a high-risk category
- **WHEN** a consult carries a review flag that the review policy lists as always-review
- **THEN** openChart selects it for review whatever the sample rate, and records the category as the cause

#### Scenario: Failure: the sample rate is zero
- **WHEN** the review policy's sample rate is zero and a consult carries the emergency indicator
- **THEN** openChart still selects the consult for review under the built-in trigger

### Requirement: AC-08 Review status, reviewer and outcome are recorded by a named clinician, and an overdue review escalates
Each consult record SHALL carry a review status: `not_selected`, `selected`, `in_review` or `reviewed`. A review SHALL be recorded only by a named clinician with an openChart account, with the outcome (`concur`, `concur_with_note`, `follow_up_required` or `unsafe`), an optional note, and the time (design call AD-25). No AI system and no agent SHALL record, change or close a review. A review SHALL be immutable; a later view SHALL be a new review event.

A selected consult that is not reviewed within the review policy's window SHALL escalate to the medical director, who keeps being alerted until it is reviewed (design call AD-13). An `unsafe` outcome SHALL alert the medical director at once and mark a clinician follow-up as owed to the patient. openChart SHALL report each outcome to the AI system as a `consult.reviewed` code only (design call AD-21).

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
AI answers reach the patient without a prior clinician sign-off (ruling 57). openChart SHALL NOT sit in the delivery path of an AI answer and SHALL NOT approve, hold or release delivery. Each consult record SHALL say that the answer was delivered without a prior clinician sign-off.

openChart SHALL check a consult write against the grant version that was in force when the consult ended (design call AD-5). A consult that ended while the grant was active SHALL be recorded even if the grant was paused, narrowed or expired before the write arrived. A consult that ended while no grant was active SHALL be refused, with reason `no_current_grant`, `grant_paused`, `grant_expired` or `grant_revoked`, and shown to the medical director as an integration exception under AC-06.

#### Scenario: Failure: a consult arrives after a pause
- **WHEN** a consult ended at 10:00, the medical director paused the grant at 10:05, and the write arrives at 10:10
- **THEN** openChart records the consult under the grant version in force at 10:00, and the record shows that the grant has since been paused

#### Scenario: Failure: a consult happened while the grant was paused
- **WHEN** a consult ended at 10:20, after the 10:05 pause
- **THEN** openChart refuses it with reason `grant_paused`, and the medical director sees the integration exception

### Requirement: AC-10 A consult with an emergency indicator is recorded, always reviewed and shown urgently, and is never AI emergency management
An AI never manages an emergency in any mode (ruling 61). When a consult write carries the emergency indicator, openChart SHALL record it, select it for review (AC-07), list it for the patient's responsible clinician and the medical director with an urgent marker, and show where the source system routed the patient. openChart SHALL NOT treat any part of the consult as emergency management by the AI, and SHALL NOT record it as a clinical act (design call AD-22).

#### Scenario: Failure: an emergency consult arrives
- **WHEN** a consult write carries the emergency indicator and records that the patient was directed to emergency care
- **THEN** openChart records the consult, selects it for review, lists it urgently for the responsible clinician and the medical director, and creates no clinical act
