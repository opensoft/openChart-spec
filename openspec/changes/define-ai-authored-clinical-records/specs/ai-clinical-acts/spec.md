## ADDED Requirements

### Requirement: AA-01 Tier 2 is specified but not in force: it needs the clinical-acts foundation and a future governed amendment, and until both no AI-authored act is created
openChart has no clinician-authored encounters, orders, prescriptions, diagnoses or treatment plans. This capability specifies the authorship, authority, co-review and reversal layer for AI-authored clinical acts, and SHALL NOT be built or put in force until both of these hold: (a) the required prerequisite change, the clinical-acts foundation (`define-clinical-acts-foundation`, openChart-spec#5, drafted under ruling 72), is ratified and its acts are built; and (b) a future governed amendment, made after advice-only has run and counsel's review is in, puts Tier 2 in force (ruling 67). Under ruling 67 the ratified texts that bar an AI-authored prescription, diagnosis or order stand, and that amendment must address them (tensions AT-1 and AT-2). A MINOR version of the contract SHALL then pin the foundation's content schemas for `act_content`. Until then a recommendation keeps an act's content as given, on the foundation's recommendation record in `openchart-clinical-act-content/1.0` at SHA-256 `9fef87204574038450f88374b71e1f878b1b218993a0b2813b69d01707cc9dd8`, as of its head `de2109f` (AW-16; design call AD-17). Ruling 157 says how Tier 2 meets ruling 151: "151. An AI only ever makes recommendations until a practitioner signs. Limited and full practice as designed would need a new ruling." So the governed amendment of ruling 67 cannot put Tier 2 in force as this capability specifies it, an AI act accepted under a practice-mode grant and co-reviewed afterwards, without a new ruling (AG-04 gate (d)). Until then, an AI's act is a recommendation until a practitioner signs it off.

Until then, openChart SHALL record every `act.write` that passes steps 1 to 6 of AW-06 and its AI check as a recommendation under AW-16, with `path_reason` `tier2_not_in_force`, which step 7 reports ahead of every grant, mode and act check. It SHALL create no order, prescription, diagnosis, treatment-plan change or other clinical act from AI-authored content, whatever mode, grant or authority the content claims. An AI holds no decision authority today: advice only is the only mode that can be switched on, so everything an AI adds is information or a recommendation (ruling 80, clause 19; ruling 67, second sentence). This keeps `define-clinical-message-inbox` MI-26's hold in force in substance, even after this change is ratified (tension AT-5). Once Tier 2 is in force, an act class this capability does not cover, an act type the foundation does not define, and an act with no act type SHALL be recorded as a recommendation with `act_type_unsupported`; until then every act takes `tier2_not_in_force` (ruling 188; design call AD-63). The foundation defines no treatment-plan record (ruling 73; its tension CT-6), so a `treatment_plan_change` SHALL be recorded as a recommendation with `act_type_unsupported` until a later treatment-plan change, a prerequisite of that act class, is ratified and built and the Tier 2 amendment covers it.

#### Scenario: Failure: an act write arrives before the foundation exists
- **WHEN** an identified AI system sends a schema-valid `act.write` claiming `full_practice`, for a linked patient, before the clinical-acts foundation is built
- **THEN** openChart records it as a recommendation with `path_reason` `tier2_not_in_force`, answers `recorded_as_recommendation`, and creates no clinical act

#### Scenario: Failure: the foundation is built but no governed amendment exists
- **WHEN** the clinical-acts foundation is ratified and built, no governed amendment has put Tier 2 in force, and an AI system sends a schema-valid `act.write` under a grant it claims
- **THEN** openChart records it as a recommendation with `path_reason` `tier2_not_in_force` and creates no clinical act

#### Scenario: Failure: a treatment-plan change arrives with no treatment-plan record
- **WHEN** Tier 2 is in force over the foundation, no treatment-plan change has been ratified, and an AI system writes a `treatment_plan_change` act
- **THEN** openChart records it as a recommendation with `path_reason` `act_type_unsupported` and creates no act

#### Scenario: Failure: a plan proposes building Tier 2 early
- **WHEN** a plan proposes building AI-authored acts before the clinical-acts foundation is ratified and a governed amendment puts Tier 2 in force
- **THEN** the plan is out of scope, and the work waits for both

### Requirement: AA-02 The authorship layer applies to every clinical act type and keeps AI authorship distinguishable
Once Tier 2 is in force, every clinical act that openChart records SHALL carry an author type: `clinician` for a named clinician's act, or `ai` for an act an external clinical AI system wrote under this capability, an author type that only the governed amendment putting Tier 2 in force, under the new ruling that ruling 157 requires, can add to the foundation's (its CA-02). The layer SHALL apply in the same way to every act class the foundation defines (orders, prescriptions, diagnoses of record and treatment-plan changes) and SHALL NOT depend on the act's clinical content. An AI-authored act SHALL carry the AI's openWallet ID, model and model version, its writer and every party on whose behalf it was written (AW-02, AW-15), its source system, its model identifiers and versions, its evidence references and, where the source system states it, its knowledge basis, the consult it came from where there is one, and the authority it rested on (AA-12). It SHALL be shown as AI-authored on every surface (AW-09). The foundation keeps an act's author type `clinician` and enters act content from any other author as a recommendation, never refusing it for that reason (its CA-02). Ruling 80 lets any identified writer add to the chart, and the foundation carries that rule: who may add and how each writer is identified (its AN-01 to AN-03), and every addition being information or a decision, the act-type registry deciding which (its AN-06). So while Tier 2 is not in force no act with author type `ai` exists: every act an AI sends is a recommendation that names the AI as its decision maker, created at once with no draft, because an AI holds no `draft` scope (the foundation's AN-09 and AN-14; AW-16; tension AT-10).

#### Scenario: Failure: an AI act would be listed with clinician acts
- **WHEN** a patient's medication list shows an accepted AI-authored prescription beside clinician-authored ones
- **THEN** the AI-authored prescription is labelled AI-authored with its source system and co-review status, and is never shown as clinician-authored

### Requirement: AA-03 An AI-authored act is accepted only under a current practice-mode grant
Under ruling 157 no AI act is accepted until a new ruling allows it; this requirement specifies what such a ruling would build on. openChart SHALL accept an `act.write` only when the grant in force at receipt is `active`, is a `limited_practice` or `full_practice` grant, and names the practice, the mode, the configuration version, the allowlist entry (limited practice) or the full-practice grant (full practice), the approving medical director and the recorded legal review for that mode; and when the write matches every one of them (AG-06). Otherwise openChart SHALL record the act as a recommendation whose `path_reason` is the first check it fails, mapped to the foundation's codes as AW-06 states (AW-16). An act made before a pause, narrowing or expiry but received after it SHALL be recorded as a recommendation (design call AD-5); the AI system routes the patient to a human clinician.

For a `prescription` act, openChart SHALL also call the prescribing-safety gate of `define-prescribing-safety-checks` (openChart-spec#6, not yet on main), its PG-01, for the exact content being accepted, and SHALL accept the act only when the decision is `open`, which needs a check completed against the digest of that content. A decision of `outage_path` SHALL be treated as not open: an AI author never uses the outage path (ruling 76; that change's PG-02). The co-review and the release of an accepted AI prescription are prescription steps under the foundation's RX-02, and call the gate again. A gate decision that is not `open` SHALL leave the act a recommendation with `path_reason` `prescribing_gate_not_open`, a code which the MINOR version that puts Tier 2 in force adds to the contract, and with `missing_authority` `no_practitioner_sign_off`, and `no_decision_authority` while an AI holds none. The gate code goes in `path_reason` only, because a safety gate is never a missing authority, and the recommendation itself is never gated: the gate applies again when a clinician adopts it (the foundation's AN-09 and RX-02; design call AD-35). No 1.x receiver accepts an act before then (AA-01).

#### Scenario: Failure: an act arrives after the grant was narrowed
- **WHEN** the medical director removes allowlist entry `SYN-ALLOW-0007`, and an act naming that entry arrives afterwards
- **THEN** openChart records it as a recommendation with `path_reason` `grant_mismatch`, or `allowlist_entry_unknown` when it names the new grant version, and creates no act

#### Scenario: Failure: an AI prescription meets the outage path
- **WHEN** Tier 2 is in force, an AI system writes a prescription under a grant it matches in every field, and the prescribing-safety gate decision for it is `outage_path` because the knowledge source is unavailable
- **THEN** openChart records it as a recommendation with `path_reason` `prescribing_gate_not_open`, creates no prescription, and lists it with its content for the patient's doctor (AA-12)

#### Scenario: Failure: the gate's check covered different content
- **WHEN** an AI prescription arrives whose content digest differs from the digest that the completed prescribing-safety check covered
- **THEN** the gate decision is not `open`, and openChart records the act as a recommendation with `path_reason` `prescribing_gate_not_open`

#### Scenario: Failure: the act names a different legal review
- **WHEN** an act write names a legal review other than the one the grant records
- **THEN** openChart records it as a recommendation with `path_reason` `legal_review_mismatch`

### Requirement: AA-04 A limited-practice act must match its allowlist entry, protocol and checkable conditions
For a `limited_practice` act, openChart SHALL require that the write names an allowlist entry of the current grant version; that the act's class and type equal the entry's; that the protocol reference equals the entry's standing order or protocol; and that every condition the entry marks as checkable from chart data holds in openChart at receipt (design call AD-16). An act that fails any of these SHALL be recorded as a recommendation (AW-16). Conditions the entry does not mark as checkable SHALL be accepted as the AI system's statement with its evidence, recorded with the act, and examined in co-review (AA-07).

#### Scenario: Failure: the act type differs from the entry
- **WHEN** an act names allowlist entry `SYN-ALLOW-0007`, whose act type is a lab order, but carries a prescription
- **THEN** openChart records it as a recommendation with `path_reason` `allowlist_entry_mismatch`

#### Scenario: Failure: a checkable condition does not hold
- **WHEN** an entry's checkable condition requires a recorded result that openChart does not hold for the patient
- **THEN** openChart records the act as a recommendation with `path_reason` `conditions_unverified`

### Requirement: AA-05 The reserved list is never accepted from an AI author, whatever mode is claimed, unless the recorded legal review cleared it
These acts are reserved to a human clinician (ruling 61): controlled-substance prescribing, and any act that the grant's recorded legal review finds must be a licensed clinician's own act. openChart SHALL NOT accept a reserved act from an AI author, in any mode, unless the grant version in force records that its legal review cleared that act for that mode. It SHALL record such an act as a recommendation with `path_reason` `reserved_act_refused`, unless an earlier check of AW-06 fails first (AW-16). An act SHALL be treated as reserved when openChart's own classification marks it reserved, or when the write declares it reserved, whichever is stricter (design call AD-15).

#### Scenario: Failure: a full-practice AI prescribes a controlled substance
- **WHEN** an AI system under a `full_practice` grant writes a prescription that openChart classifies as a controlled substance, and the grant's legal review does not clear it
- **THEN** openChart records it as a recommendation with `path_reason` `reserved_act_refused`, creates no prescription, and lists it with its content for the patient's doctor (AA-12)

#### Scenario: Failure: the AI system marks an act reserved that openChart does not
- **WHEN** an act write declares itself reserved, and openChart's classification does not
- **THEN** openChart treats it as reserved and records it as a recommendation unless the legal review cleared it

### Requirement: AA-06 An AI never manages an emergency: an emergency act is recorded as a recommendation and listed urgently, and the urgent hand-off stands
An AI never manages an emergency, in any mode (ruling 61; ruling 80, clause 20). openChart SHALL NOT accept an `act.write` whose emergency indicator is set, or whose act type openChart classifies as emergency management, whatever mode, grant or clearance applies. No legal review and no grant SHALL clear it. openChart SHALL record it as a recommendation under AW-16, with `path_reason` `emergency_management_refused` unless an earlier check fails first, and SHALL list it urgently, with its content, for the patient's responsible clinician and the medical director. A set emergency indicator makes the listing urgent whatever its codes (design call AD-29). The urgent hand-off to a human stays as it is: the AI system directs the patient to emergency care or a human clinician by its own path, and openChart's urgent listing puts what the AI attempted in front of a clinician.

#### Scenario: Failure: an AI orders an emergency intervention
- **WHEN** an AI system under a `full_practice` grant whose legal review clears every listed act writes an act with the emergency indicator set
- **THEN** openChart records it as a recommendation with `path_reason` `emergency_management_refused`, creates no act, and lists it urgently, with its content, for the responsible clinician and the medical director

#### Scenario: Failure: an emergency act arrives before Tier 2 is in force
- **WHEN** an AI system under an `advice_only` grant sends an `act.write` with the emergency indicator set, for a linked patient
- **THEN** openChart records it as a recommendation with `path_reason` `tier2_not_in_force`, creates no act, and lists it urgently, with its content, for the responsible clinician and the medical director

### Requirement: AA-07 Every accepted AI-authored act enters clinician co-review within the medical director's window
Every AI-authored act that openChart accepts SHALL enter a co-review queue in openChart at once, with a due time equal to its acceptance time plus the co-review window the grant sets for its act class (ruling 62). openChart SHALL return the due time in the receipt. A named clinician holding `cosign` scope for that act class under `define-clinical-acts-foundation` AU-02 SHALL co-review it (design call AD-20), and SHALL record one outcome. These outcomes converge on that change's CA-07 co-signature model at the Tier 2 amendment (tension AT-11):
- **confirm:** the act stands, attributed to the AI under its authority, with the co-review recorded;
- **amend:** the clinician records a new, dated, clinician-authored act that visibly supersedes the AI act;
- **void:** the AI act is marked `entered_in_error` (foundation CA-06), with a reason, and stops having effect (AA-09).

No AI system and no agent SHALL co-review, and the AI that wrote the act SHALL NOT confirm it. openChart SHALL report each outcome to the AI system as an `act.status`. Under rulings 151 and 187 each of these outcomes is a practitioner's sign-off of a medical decision, made in the co-reviewer's own logged-in session with their openWallet and openSig, as the foundation's CA-04 provides, with the authority it rested on recorded as its AN-07 states (design call AD-54). Each is made over the foundation's sign-off statement, with a single-use challenge and the attestation over the statement's SHA-256 (`challenge_ref`, `statement_sha256`), and names its action: confirm is a co-signature (`cosign`, signature role `cosigner`); amend is a new version the clinician signs (`sign`); void is an entered-in-error mark (`enter_in_error`, signature role `actor`). The Tier 2 amendment maps these onto the foundation's co-signature model (tension AT-11). Under ruling 157 an AI act cannot take effect before a practitioner signs it off, so this after-the-fact queue would stand only under a new ruling (AA-01). A recommendation (AW-16) never enters this queue.

#### Scenario: A clinician confirms an AI order
- **WHEN** a named clinician authorized for orders confirms an accepted AI-authored lab order within its window
- **THEN** openChart records the confirmation with the clinician, the time and the outcome, and sends `act.status` `co_review_confirmed`

#### Scenario: Failure: an agent tries to confirm an AI act
- **WHEN** an AI agent tries to confirm an act in the co-review queue
- **THEN** the confirmation takes no effect, and the act stays in the queue unconfirmed; openChart enters the attempt as a recommendation marked not an authorized decision, with `no_decision_authority`, as the foundation's AU-05 provides

### Requirement: AA-08 An overdue co-review escalates to the medical director and is never closed by default
When an AI-authored act's co-review is not recorded by its due time, openChart SHALL escalate it to the medical director at once, SHALL make the medical director its co-reviewer, SHALL keep re-alerting until a clinician records an outcome, and SHALL send `act.status` `co_review_overdue_escalated`. An overdue act SHALL NOT be confirmed, marked `entered_in_error`, dropped or closed by any timer or default.

#### Scenario: Failure: nobody co-reviews an AI prescription in time
- **WHEN** an accepted AI-authored prescription's co-review window passes with no outcome
- **THEN** openChart escalates it to the medical director, keeps re-alerting, and the act stays in the queue unconfirmed

### Requirement: AA-09 A clinician can void or countermand an AI act, and corrections are new dated records
A named clinician SHALL be able to void an AI-authored act, which marks it `entered_in_error` with actor, reason and time (foundation CA-06), or countermand it. A countermand moves a `released` act to `discontinued` by a signed discontinuation, and a `pending_release` act to `cancelled` (foundation CA-03, OR-02); either way it stops the act from then on. Under rulings 151 and 187 a void and a countermand, which stop or correct a decision, are each a practitioner's sign-off of a medical decision (design call AD-54), made as the foundation's CA-04 states, over its sign-off statement with a single-use challenge, and naming its action: a void is `enter_in_error`; a countermand is `discontinue` for a `released` act and `cancel` for a `pending_release` act, each with signature role `actor`. A prescription is never `completed`: it ends only by a signed-off discontinuation or an entered-in-error mark (the foundation's RX-01 and CA-03), and `act.status` and the readback have no completion value for any act. No AI-authored act or its history SHALL be deleted or edited in place. Every correction SHALL be a new dated record that references what it corrects (ruling 80, clause 8). The patient-facing display SHALL show the `entered_in_error`, `discontinued` or `cancelled` status (AW-09). openChart SHALL send the matching `act.status`.

#### Scenario: Failure: someone tries to delete an AI act
- **WHEN** a user tries to delete an accepted AI-authored order
- **THEN** the deletion is refused, and only an `entered_in_error` mark or a countermand to `discontinued` or `cancelled`, each a new dated record, can stop it

### Requirement: AA-10 An AI act never overwrites or supersedes clinician-authored content
openChart SHALL NOT let an `act.write` modify, discontinue, replace or supersede a clinician-authored record. It SHALL record such a write as a recommendation with `path_reason` `targets_clinician_record`, unless an earlier check of AW-06 fails first, and list it, with its content, for the patient's doctor (AW-16, AA-12); the clinician's record is unchanged. This is stricter than barring a silent supersession: in contract version 1.0 an AI act may not supersede clinician-authored content at all (design call AD-8). An AI act MAY supersede only an earlier AI-authored act by the same source system, and only visibly, as a new dated record that references it. A treatment-plan change by an AI SHALL be a new dated record that references the plan it changes, and SHALL NOT alter a clinician-authored plan.

#### Scenario: Failure: an AI tries to discontinue a clinician's prescription
- **WHEN** an AI act names a clinician-authored prescription as its target record
- **THEN** openChart records it as a recommendation with `path_reason` `targets_clinician_record`, the clinician's prescription is unchanged, and the patient's doctor sees the recommendation with its content

### Requirement: AA-11 On narrowing or pause, pending AI acts are held for a clinician or cancelled, never released
When the medical director narrows or pauses a grant, or a reduction applies under AG-08, openChart SHALL at once stop every pending AI-authored act whose basis the grant no longer covers. A pending act is one in the foundation's `pending_release` status: signed but not yet in force (CA-03, OR-02; its tension CT-7). Each such act SHALL be held and handed to a named clinician, who adopts it as a new clinician-authored act, a sign-off under ruling 151 with action `sign`, or cancels it, a sign-off with action `cancel` (design call AD-9). The medical director MAY cancel it instead. Each is made over the foundation's sign-off statement with a single-use challenge (its CA-04). It SHALL NOT be released on the AI's authority. openChart SHALL send `act.status` `handed_to_clinician` or `cancelled_on_narrowing`. Acts already `released` SHALL stay in co-review (AA-07).

#### Scenario: Failure: a pause arrives while an AI prescription is `pending_release`
- **WHEN** the medical director pauses a grant while an accepted AI-authored prescription is still `pending_release`
- **THEN** the prescription is not released, stays `pending_release` until a named clinician adopts or cancels it, is handed to that clinician, and openChart sends `act.status` `handed_to_clinician`

### Requirement: AA-12 Every AI act states the authority it rested on, and every recommendation is in front of the patient's doctor
Every accepted AI-authored act SHALL store, and show to clinicians, the authority it rested on: the grant and its version, the mode, the configuration version, the allowlist entry and its protocol (limited practice) or the full-practice grant (full practice), the approving medical director, the legal review reference, any reserved-act clearance relied on, and the co-review status. The patient-facing display SHALL state, in plain words, that an AI system made the act under the practice's authority and whether a clinician has co-reviewed it (AW-09).

Every `act.write` recorded as a recommendation (AW-16) SHALL be listed, with its content, for the patient's responsible clinician when that clinician holds `sign` scope for its act class, and otherwise for the medical director, and SHALL stay listed until a named clinician adopts or declines it (AW-16; the foundation's AN-11). Its writer and AI are identified, its context is operational and its patient is linked, because it passed steps 1 to 6 of AW-06 and its AI check. The listing shows the act class, the `missing_authority` codes beside the `path_reason` code and, in plain words, the authority that was missing, the time, any linked consult and the content, marked "not an authorized decision" (ruling 80, clause 13). These listings fall under AW-13's per-source ceiling and digest, as urgent listings do (design call AD-46). An `act.write` with no evidence reference is listed marked so (design call AD-63). An `act.write` held by the AI check (AC-11) is listed the same way, with its content, marked held because a party it names is not covered, and never shown as a recommendation while it is held. An `act.write` refused at steps 1, 2 or 4 to 6 keeps its refusal record, with identifiers and a coded cause, holds no content, and is listed only where AW-06 lists a refusal. This is how "anything not listed goes to the human doctor" (ruling 60) reaches openChart: the recommendation itself goes in front of a clinician who holds the authority, who may adopt or decline it (ruling 80, clause 16). The AI system also routes the patient to a human clinician by its own path (tension AT-9).

#### Scenario: Failure: an act would be stored without its authority
- **WHEN** an implementation tries to store an accepted AI-authored act without its grant version or legal review reference
- **THEN** the store is refused, and the act is not accepted

#### Scenario: Failure: a scenario act and a deregistered source's act are refused
- **WHEN** openChart refuses a `scenario` `act.write`, and an `act.write` from a deregistered identity
- **THEN** each keeps its refusal record, with identifiers and a coded cause, and neither is listed for any clinician

#### Scenario: Failure: a source floods recommendations
- **WHEN** a source's eleventh act recorded as a recommendation in 60 minutes arrives, with no lower ceiling set
- **THEN** it is recorded in full, and its listing goes into that source's digest under AW-13, not listed one by one

#### Scenario: Failure: an act outside the allowlist is recorded as a recommendation
- **WHEN** openChart records an AI act as a recommendation with `path_reason` `allowlist_entry_unknown`
- **THEN** the patient's responsible clinician sees it with its act class, the missing authority, the time and its content, marked "not an authorized decision"
