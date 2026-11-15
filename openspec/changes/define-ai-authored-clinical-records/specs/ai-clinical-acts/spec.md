## ADDED Requirements

### Requirement: AA-01 Tier 2 is not buildable until the clinical-acts foundation is ratified, and until then no AI-authored act is created
openChart has no clinician-authored encounters, orders, prescriptions, diagnoses or treatment plans. This capability specifies the authorship, authority, co-review and reversal layer for AI-authored clinical acts, and SHALL NOT be built until the required prerequisite change, the clinical-acts foundation (proposed id `define-clinical-acts-foundation`), is ratified, and its acts are built. A MINOR version of the contract SHALL then pin the foundation's content schemas for `act_content` (design call AD-17).

Until then, openChart SHALL refuse every `act.write` with reason `tier2_not_in_force`, ahead of every grant, mode and act check (AW-06 precedence), and SHALL create no order, prescription, diagnosis, treatment-plan change or other clinical act from AI-authored content, whatever mode, grant or authority it claims. This keeps `define-clinical-message-inbox` MI-26's hold in force in substance, even after this change is ratified (tension AT-5). Once the foundation exists, an act class or act type that it does not define SHALL be refused with reason `act_type_unsupported`.

#### Scenario: Failure: an act write arrives before the foundation exists
- **WHEN** an AI system sends a schema-valid `act.write` claiming `full_practice` before the clinical-acts foundation is built
- **THEN** openChart refuses it with reason `tier2_not_in_force` and creates no clinical act

#### Scenario: Failure: a plan proposes building Tier 2 early
- **WHEN** a plan proposes building AI-authored acts before the clinical-acts foundation is ratified
- **THEN** the plan is out of scope, and the work waits for the foundation

### Requirement: AA-02 The authorship layer applies to every clinical act type and keeps AI authorship distinguishable
Every clinical act that openChart records SHALL carry an author kind: `clinician` for a named clinician's act, or `ai` for an act an external clinical AI system wrote under this capability. The layer SHALL apply in the same way to every act class the foundation defines (orders, prescriptions, diagnoses of record and treatment-plan changes) and SHALL NOT depend on the act's clinical content. An AI-authored act SHALL carry its source system, its model identifiers and versions, its evidence references and, where the source system states it, its knowledge basis, the consult it came from where there is one, and the authority it rested on (AA-12). It SHALL be shown as AI-authored on every surface (AW-09).

#### Scenario: Failure: an AI act would be listed with clinician acts
- **WHEN** a patient's medication list shows an accepted AI-authored prescription beside clinician-authored ones
- **THEN** the AI-authored prescription is labelled AI-authored with its source system and co-review status, and is never shown as clinician-authored

### Requirement: AA-03 An AI-authored act is accepted only under a current practice-mode grant
openChart SHALL accept an `act.write` only when the grant in force at receipt is `active`, is a `limited_practice` or `full_practice` grant, and names the practice, the mode, the configuration version, the allowlist entry (limited practice) or the full-practice grant (full practice), the approving medical director and the recorded legal review for that mode; and when the write matches every one of them (AG-06). An act made before a pause, narrowing or expiry but received after it SHALL be refused (design call AD-5); the AI system routes the patient to a human clinician.

#### Scenario: Failure: an act arrives after the grant was narrowed
- **WHEN** the medical director removes allowlist entry `SYN-ALLOW-0007`, and an act naming that entry arrives afterwards
- **THEN** openChart refuses it with reason `grant_mismatch`, or `allowlist_entry_unknown` when it names the new grant version, and creates no act

#### Scenario: Failure: the act names a different legal review
- **WHEN** an act write names a legal review other than the one the grant records
- **THEN** openChart refuses it with reason `legal_review_mismatch`

### Requirement: AA-04 A limited-practice act must match its allowlist entry, protocol and checkable conditions
For a `limited_practice` act, openChart SHALL require that the write names an allowlist entry of the current grant version; that the act's class and type equal the entry's; that the protocol reference equals the entry's standing order or protocol; and that every condition the entry marks as checkable from chart data holds in openChart at receipt (design call AD-16). Conditions the entry does not mark as checkable SHALL be accepted as the AI system's statement with its evidence, recorded with the act, and examined in co-review (AA-07).

#### Scenario: Failure: the act type differs from the entry
- **WHEN** an act names allowlist entry `SYN-ALLOW-0007`, whose act type is a lab order, but carries a prescription
- **THEN** openChart refuses it with reason `allowlist_entry_mismatch`

#### Scenario: Failure: a checkable condition does not hold
- **WHEN** an entry's checkable condition requires a recorded result that openChart does not hold for the patient
- **THEN** openChart refuses the act with reason `conditions_unverified`

### Requirement: AA-05 The reserved list is refused for AI authors whatever mode is claimed, unless the recorded legal review cleared it
These acts are reserved to a human clinician (ruling 61): controlled-substance prescribing, and any act that the grant's recorded legal review finds must be a licensed clinician's own act. openChart SHALL refuse a reserved act from an AI author with reason `reserved_act_refused`, in every mode, unless the grant version in force records that its legal review cleared that act for that mode. An act SHALL be treated as reserved when openChart's own classification marks it reserved, or when the write declares it reserved, whichever is stricter (design call AD-15).

#### Scenario: Failure: a full-practice AI prescribes a controlled substance
- **WHEN** an AI system under a `full_practice` grant writes a prescription that openChart classifies as a controlled substance, and the grant's legal review does not clear it
- **THEN** openChart refuses it with reason `reserved_act_refused`, creates no prescription, and the patient's doctor sees the refused attempt (AA-12)

#### Scenario: Failure: the AI system marks an act reserved that openChart does not
- **WHEN** an act write declares itself reserved, and openChart's classification does not
- **THEN** openChart treats it as reserved and refuses it unless the legal review cleared it

### Requirement: AA-06 Emergency management by an AI is always refused
An AI never manages an emergency, in any mode (ruling 61). openChart SHALL refuse every `act.write` whose emergency indicator is set, or whose act type openChart classifies as emergency management, with reason `emergency_management_refused`, whatever mode, grant or clearance applies. No legal review and no grant SHALL clear it. The refusal SHALL be listed urgently for the patient's responsible clinician and the medical director.

#### Scenario: Failure: an AI orders an emergency intervention
- **WHEN** an AI system under a `full_practice` grant whose legal review clears every listed act writes an act with the emergency indicator set
- **THEN** openChart refuses it with reason `emergency_management_refused` and lists the refusal urgently for the responsible clinician and the medical director

### Requirement: AA-07 Every accepted AI-authored act enters clinician co-review within the medical director's window
Every AI-authored act that openChart accepts SHALL enter a co-review queue in openChart at once, with a due time equal to its acceptance time plus the co-review window the grant sets for its act class (ruling 62). openChart SHALL return the due time in the receipt. A named clinician whose role the medical director authorizes for that act class SHALL co-review it (design call AD-20), and SHALL record one outcome:
- **confirm:** the act stands, attributed to the AI under its authority, with the co-review recorded;
- **amend:** the clinician records a new, dated, clinician-authored act that visibly supersedes the AI act;
- **void:** the AI act is marked voided, with a reason, and stops having effect (AA-09).

No AI system and no agent SHALL co-review, and the AI that wrote the act SHALL NOT confirm it. openChart SHALL report each outcome to the AI system as an `act.status`.

#### Scenario: A clinician confirms an AI order
- **WHEN** a named clinician authorized for orders confirms an accepted AI-authored lab order within its window
- **THEN** openChart records the confirmation with the clinician, the time and the outcome, and sends `act.status` `co_review_confirmed`

#### Scenario: Failure: an agent tries to confirm an AI act
- **WHEN** an AI agent tries to confirm an act in the co-review queue
- **THEN** the action is refused and the act stays in the queue

### Requirement: AA-08 An overdue co-review escalates to the medical director and is never closed by default
When an AI-authored act's co-review is not recorded by its due time, openChart SHALL escalate it to the medical director at once, SHALL make the medical director its co-reviewer, SHALL keep re-alerting until a clinician records an outcome, and SHALL send `act.status` `co_review_overdue_escalated`. An overdue act SHALL NOT be confirmed, voided, dropped or closed by any timer or default.

#### Scenario: Failure: nobody co-reviews an AI prescription in time
- **WHEN** an accepted AI-authored prescription's co-review window passes with no outcome
- **THEN** openChart escalates it to the medical director, keeps re-alerting, and the act stays in the queue unconfirmed

### Requirement: AA-09 A clinician can void or countermand an AI act, and corrections are new dated records
A named clinician SHALL be able to void an AI-authored act, which marks it voided with actor, reason and time, or countermand it, which records a new, dated, clinician-authored act that stops it from then on. No AI-authored act or its history SHALL be deleted or edited in place. Every correction SHALL be a new dated record that references what it corrects. The patient-facing display SHALL show the voided or countermanded state (AW-09). openChart SHALL send the matching `act.status`.

#### Scenario: Failure: someone tries to delete an AI act
- **WHEN** a user tries to delete an accepted AI-authored order
- **THEN** the deletion is refused, and only a void or a countermand, each recorded as a new dated record, can stop it

### Requirement: AA-10 An AI act never overwrites or supersedes clinician-authored content
openChart SHALL refuse an `act.write` that would modify, discontinue, replace or supersede a clinician-authored record, with reason `targets_clinician_record`, and SHALL route it to the patient's doctor as a refused attempt (AA-12). This is stricter than barring a silent supersession: in contract version 1.0 an AI act may not supersede clinician-authored content at all (design call AD-8). An AI act MAY supersede only an earlier AI-authored act by the same source system, and only visibly, as a new dated record that references it. A treatment-plan change by an AI SHALL be a new dated record that references the plan it changes, and SHALL NOT alter a clinician-authored plan.

#### Scenario: Failure: an AI tries to discontinue a clinician's prescription
- **WHEN** an AI act names a clinician-authored prescription as its target record
- **THEN** openChart refuses it with reason `targets_clinician_record`, the clinician's prescription is unchanged, and the patient's doctor sees the refused attempt

### Requirement: AA-11 On narrowing or pause, pending AI acts are held for a clinician or cancelled, never executed
When the medical director narrows or pauses a grant, or a reduction applies under AG-08, openChart SHALL at once stop every pending AI-authored act whose basis the grant no longer covers. A pending act is one the foundation's lifecycle shows as accepted but not yet released or executed. Each such act SHALL be held and handed to a named clinician, who adopts it as a new clinician-authored act or cancels it (design call AD-9). The medical director MAY cancel it instead. It SHALL NOT be executed on the AI's authority. openChart SHALL send `act.status` `handed_to_clinician` or `cancelled_on_narrowing`. Acts already executed SHALL stay in co-review (AA-07).

#### Scenario: Failure: a pause arrives while an AI prescription awaits transmission
- **WHEN** the medical director pauses a grant while an accepted AI-authored prescription has not yet been released for transmission
- **THEN** the prescription is not released, is handed to a named clinician, and openChart sends `act.status` `handed_to_clinician`

### Requirement: AA-12 Every AI act states the authority it rested on, and refused attempts are visible to the patient's doctor
Every accepted AI-authored act SHALL store, and show to clinicians, the authority it rested on: the grant and its version, the mode, the configuration version, the allowlist entry and its protocol (limited practice) or the full-practice grant (full practice), the approving medical director, the legal review reference, any reserved-act clearance relied on, and the co-review status. The patient-facing display SHALL state, in plain words, that an AI system made the act under the practice's authority and whether a clinician has co-reviewed it (AW-09).

Every refused `act.write` SHALL be listed for the patient's responsible clinician, or the medical director where none is recorded, as a refused AI act attempt: its act class, its reason code, the time and any linked consult. It SHALL hold no act content (AW-06). This is how "anything not listed goes to the human doctor" (ruling 60) reaches openChart; the AI system also routes the patient to a human clinician by its own path (tension AT-9).

#### Scenario: Failure: an act would be stored without its authority
- **WHEN** an implementation tries to store an accepted AI-authored act without its grant version or legal review reference
- **THEN** the store is refused, and the act is not accepted

#### Scenario: Failure: an act outside the allowlist is refused
- **WHEN** openChart refuses an AI act with reason `allowlist_entry_unknown`
- **THEN** the patient's responsible clinician sees the refused attempt with its act class, reason and time, and no act content
