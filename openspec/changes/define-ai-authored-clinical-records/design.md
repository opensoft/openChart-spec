## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

What is built today, and what is not:

- **Built:** `OC Patient`, `OC Patient External Identifier` (namespaced, versioned, with an `identity_review` status), `OC Intake Submission` and eight patient-reported statement families, behind the versioned API `open_chart.api.v1`. Every statement is `patient_reported`.
- **Roles:** every built DocType grants permissions to `System Manager` only. No clinician, nurse or medical-director role exists.
- **Not built:** there are no clinician encounters, orders, prescriptions, diagnoses of record or treatment plans in openChart, and nothing records AI-authored content. This change does not write as if they exist. Tier 2 waits for a prerequisite change that builds them.

**Two draft openChart changes are related, and neither is on main.**
- `define-clinical-message-inbox` (branch `change/define-clinical-message-inbox`, head `26bf411`) defines routed patient questions for the human doctor and a clinical-communication record (MI-12, MI-13). Its MI-26 holds every AI-authored order, prescription or diagnosis as communication "until a later openChart change for practice modes is ratified", and its Open Question 4 leaves openChart's receiving side of the AI system's governed chart path to a separate change. This change answers both (tensions AT-5 to AT-7).
- `define-openpractice-boundary` (branch `change/define-openpractice-boundary`, head `e7c3090`) provides the patterns reused here: digest-pinned schemas (PL-04), a durable outbound store (PL-14), no PHI in diagnostics (PL-13), and standalone operation (PL-15). Its Open Question 2 asks which change introduces clinician-authored encounters, diagnoses and procedures; the prerequisite named here is that change.

**Cross-references, not dependencies of the text.** `MedxSoft/medXfactory` change `define-patient-medical-ai-connection` is drafted and not yet on main. It owns the medical-AI mode framework and its patient connection, and lists this change as a required companion. `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay` is the Medx-specific overlay on this contract. Nothing in this change depends on either system's internals.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main` (checked at revision `d20de75`). There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. Planning is blocked until a constitution is adopted.

Brett Heap's rulings are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

## Owner rulings (2026-11-14)

Every row has the same source: **Brett Heap, 2026-11-14, authoring session.** The numbering is shared with the openPractice and inbox changes. The rulings name medXfactory as the system that holds the clinical medical AI. This change's requirements are neutral: they speak of "an external clinical AI system", and name medXfactory only as a cross-reference.

| # | Ruling | Governs |
|---|---|---|
| 35 | For now the physician uses openChart, on mobile or workstation. | AW-09, AC-06 (no requirement depends on a device) |
| 51 | The clinical medical AI lives in medXfactory, not in HealthLinc. | Context; the external clinical AI system of this change |
| 53 | The medical AI's exchanges with a patient are recorded in the chart through medXfactory's own governed path (MedxEHR and openChart). They never pass through openPractice. | AW-01, AW-02, AC-01; the write path is that path's openChart end |
| 56 | In advice mode the medical AI may inform, assess and recommend next steps. It may not prescribe, order, change a treatment plan, or record a diagnosis of record. | AG-03, AC-04, AC-05 |
| 57 | Answers reach the patient without prior clinician sign-off. Every consult is in the chart for the patient's doctor. The medical director sets a review sample. Flagged or high-risk categories are always reviewed. | AC-06 to AC-09, AG-10 |
| 58 | Nothing is switched on for patients until the medical director approves the scope and red-flag rules, and a legal and regulatory review is on record. | AG-04, AG-05 |
| 59 | The medical director sets the medical AI's mode for the practice: advice only (the default), limited practice (limited authority), or full practice (full practice authority). Only the medical director, a named human, sets or changes it. He can narrow or pause at once. | AG-01 to AG-03, AG-08 |
| 60 | Limited practice is an allowlist the medical director approves. Each entry is an act type with its conditions and the standing order or protocol behind it. Anything not listed goes to the human doctor. | AG-07, AA-04, AA-12 |
| 61 | In full practice a reserved list stays with a human clinician unless the recorded legal review clears it: controlled-substance prescribing, and any act that review finds must be a licensed clinician's own act. The AI never manages an emergency in any mode. | AA-05, AA-06, AC-10 |
| 62 | In the practice modes every AI order, prescription or diagnosis is queued for clinician co-review after the fact, within a window the medical director sets. | AA-07, AA-08, AG-10 |
| 63 | Build order: advice only, then limited practice, then full practice. | AG-03; tasks §4 |
| 64 | These two changes are drafted now ("draft the openChart and MedxEHR AI write path changes too"). | This change |

**The gates (same session).** Each mode stays off until (a) the medical director has approved that mode's scope, (b) a legal and regulatory review covering that mode is recorded, and (c) for limited and full practice, the chart can accept an AI-authored order, prescription or diagnosis recorded with the authority it acted under. Item (c) is what this change specifies. AG-04 encodes all three.

**Proposed decision 65 (not ruled).** openChart holds its own record of the medical director's authorization and checks each write against it, rather than trusting the AI system's claim. This is design call AD-1, proposed pending the owner's decision 65.

## Terms used in both changes

These names are used identically in this change and in `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay`.

| Term | Meaning |
|---|---|
| `openchart-ai-clinical-record-write/1.0` | The write-path contract this change owns. Schema `contracts/openchart-ai-clinical-record-write-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-ai-clinical-record-write:1.0`, SHA-256 `e6bf6b3f2fb7912f7d79d5f9d39936866332458406d9bf5465038af3fdee067d`. |
| external clinical AI system | The system that writes AI-authored records. It is identified by `source_system` (issuer and namespace). |
| authority grant | openChart's own record of the medical director's authorization, identified by `grant_id` and `grant_version` (AG-01). |
| mode | `advice_only` (the default), `limited_practice` or `full_practice`. |
| configuration version | The AI system's configuration that the medical director approved, as `configuration_version`. |
| allowlist entry | One limited-practice entry, `allowlist_entry_id`, with its act type, conditions and `protocol_ref`. |
| recorded legal and regulatory review | The review covering a mode, referenced by `legal_review_ref` (AG-05). |
| medical director | The practice's named human who approves grants, referenced by `approver_ref` (AG-02). |
| consult record | Tier 1: one AI consult, written by `consult.write` (AC-01). |
| AI-authored clinical act | Tier 2: an `order`, `prescription`, `diagnosis_of_record` or `treatment_plan_change`, written by `act.write` (AA-01). |
| review policy | The medical director's review sample rate, always-review categories and review window (AG-10, AC-07). |
| co-review queue, co-review window | Clinician co-review of AI acts after the fact, within the window the medical director sets (AA-07). |
| reserved act | An act reserved to a human clinician unless the recorded legal review clears it (AA-05). |
| write receipt | `write.receipt`: `accepted`, `duplicate` or `refused` with a reason code (AW-06). |
| readback | `record.readback_request` and `record.readback`: the writing system confirms what openChart stored, by digest and code only (AW-12). |
| authority notice | `authority.notice`: a change in authority, from either side (AG-08). |
| context | `operational`, `scenario` or `simulation`; only `operational` is recorded (AW-04). |
| knowledge basis | What an AI turn's or act's statements rest on: `cited_sources`, `model_knowledge` or `mixed` (AC-03, AD-27). |
| source authority reference | The AI system's own reference to the configuration it acted under, `source_authority_ref` (AG-01). |
| clinical-acts foundation | The required prerequisite change, proposed id `define-clinical-acts-foundation`. |

## Goals / Non-Goals

**Goals:**

- Give openChart a neutral, versioned write path for records from an external clinical AI system operating under a declared authority.
- Make Tier 1, the AI consult record, buildable now, without any orders model, so that advice-only mode can be switched on once its gates are met.
- Specify Tier 2's authorship, authority, co-review and reversal layer now, so the clinical-acts foundation can be built to receive it.
- Make the chart, not the AI system, the judge of what authority a write rests on, and fail closed.
- Keep every ratified `expanded-patient-intake` requirement intact and keep openChart usable with no AI system at all.

**Non-Goals:**

- Building clinician encounters, orders, prescriptions, diagnoses or treatment plans. That is the prerequisite change.
- The AI system's internals, its models, its vendors or its patient-facing behaviour.
- Stating any legal or regulatory rule. This change states what the recorded review must cover.
- Billing. CF-02, CF-05 and CF-06 of `define-openpractice-boundary` are unchanged.
- Changing any ratified text, or adopting the constitution inside this change.

## Decisions

### 1. Two tiers

| Tier | What | Modes | Buildable |
|---|---|---|---|
| 1 | AI consult records: the exchange, its provenance and its review | `advice_only` and above | Now, after ratification, the constitution and the inbox's ratification (AD-3) |
| 2 | AI-authored clinical acts: authorship, authority, co-review, reversal | `limited_practice`, `full_practice` | Not until the clinical-acts foundation is ratified and built (AA-01) |

### 2. The contract

`openchart-ai-clinical-record-write/1.0` is owned by this change (AW-01). The schema follows the convention of the openPractice-spec contracts that `define-openpractice-boundary` and `define-clinical-message-inbox` pin: JSON Schema draft 2020-12, a URN `$id`, `oneOf` over the messages, every object closed, and `contracts/SHA256SUMS`. The one open object is `act_content.content`, reserved for the foundation's content schemas (AD-17).

| Message | Direction | Use |
|---|---|---|
| `consult.write` | AI system → openChart | Tier 1 consult record (AC-01) |
| `act.write` | AI system → openChart | Tier 2 act; refused with `tier2_not_in_force` until the foundation exists (AA-01) |
| `authority.notice` | both | A change in authority; from the AI system only a reduction is accepted (AG-08) |
| `write.receipt` | openChart → AI system | The answer to every write and notice (AW-06) |
| `act.status` | openChart → AI system | Co-review outcome, reversal, hand-off, cancellation, escalation (AA-07 to AA-11) |
| `consult.reviewed` | openChart → AI system | Review outcome as a code (AC-08) |
| `record.readback_request` | AI system or its relay → openChart | Asks what openChart stored for a record it wrote (AW-12) |
| `record.readback` | openChart → AI system or its relay | The stored record's identifiers, content digest, grant version, state and review status; no content (AW-12) |
| `message.ack` | both | Acknowledges a status or notice |

The refusal reasons are closed: `schema_invalid`, `unsupported_major_version`, `unauthorized`, `non_operational_context`, `patient_link_unknown`, `patient_link_mismatch`, `patient_link_in_review`, `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `allowlist_entry_unknown`, `allowlist_entry_mismatch`, `conditions_unverified`, `reserved_act_refused`, `emergency_management_refused`, `approver_mismatch`, `legal_review_mismatch`, `targets_clinician_record`, `act_type_unsupported`, `tier2_not_in_force`, `conflicting_duplicate`, `content_digest_mismatch` and `notice_would_widen`.

`contracts/examples/` holds 35 synthetic fixtures: 13 that must validate and 22 that must fail, each for one stated reason. They are part of the contract-test suite (AW-11).

### 3. openChart's own record of authority (proposed decision 65)

The chart keeps its own grant record and checks every write against it (AG-01, AD-1). The AI system's claim is compared with the chart's record and never substitutes for it. The alternative, accepting the AI system's signed statement of its mode, was rejected: a defect or compromise in the AI system would then create clinical acts in the chart with no independent check, and the chart could not show a clinician what authority a record rested on.

Only the medical director, a named human, approves, widens or resumes a grant (AG-02). A reduction applies at once from any source, the AI system's own notice included; a widening is only ever the medical director's act in openChart (AG-08, AD-6). Grants and legal reviews expire and never renew themselves (AG-09, AD-10).

### 4. Modes and gates

`advice_only` is the default (AG-03). A grant is activated only when the three gates of the 2026-11-14 session are met for its mode (AG-04): the medical director's approval of the mode's scope, a recorded legal and regulatory review covering that mode, and, for the practice modes, Tier 2 in force over the foundation. Ruling 63 is a build order: the modes are built advice, limited, full; enablement need not step through them, but a mode cannot be enabled before its build exists (AD-19).

### 5. How AI output is classified

| Content | Class | Becomes a clinical fact of record? |
|---|---|---|
| A patient's or representative's turn in a consult | Patient-reported, as the ratified intake requirement keeps it | No |
| An AI turn or summary in a consult | AI-generated communication (AC-04) | No, in any mode |
| Consult content that presents itself as an act | AI-generated communication, shown as not accepted as a clinical act (AC-05) | No |
| An AI-authored act accepted under a current practice-mode grant | An act of record with author kind `ai`, its authority stated, pending co-review (AA-02, AA-12) | Yes, as an AI-authored act, only in Tier 2 and only under a grant |
| A refused AI act | A refusal record with identifiers and codes only (AW-06, AA-12) | No |
| A clinician's amendment or countermand | A clinician-authored act | Yes |

### 6. The Tier 1 consult record and the inbox

The consult record is the inbox's clinical-communication record (MI-12, MI-13) with origin `ai_consult` (AC-01, AD-3). It holds the full exchange, each turn with its author kind, plus an optional AI summary labelled as such (AD-2). The alternative, a reference into the AI system plus a summary, was rejected for now: ruling 57 puts every consult "in the chart", a summary written by the same AI would be the doctor's only view of its own advice, and a reference fails when the AI system is unreachable or its store changes.

An inbox item that names the same conversation is associated with the consult record by the conversation reference. The inbox still files no copy (MI-24). Writing a consult record needs neither the inbox enabled nor openPractice, because ruling 53 keeps the AI's exchanges away from openPractice (tension AT-6).

### 7. Review (ruling 57)

openChart selects consults for review, not the AI system (AC-07). The review policy, set by the medical director as part of the grant, has a sample rate, always-review categories and a review window (AG-10). Four built-in triggers cannot be removed: the emergency indicator, no evidence reference at all, a linked refused act or held act content, and a declared red flag (AD-11). A named clinician records the review status, reviewer and outcome (AC-08). An overdue review escalates to the medical director (AD-13). An `unsafe` outcome alerts the medical director at once.

### 8. Tier 2: acceptance, reserved acts and emergencies

An act is accepted only under a current practice-mode grant that it matches in every field (AA-03). A limited-practice act must match its allowlist entry, protocol and checkable conditions (AA-04, AD-16). A reserved act is refused in every mode unless the grant's legal review cleared it; reservedness is the stricter of openChart's classification and the AI system's declaration (AA-05, AD-15). An act marked as emergency management is always refused, and no clearance can change that (AA-06). A consult with an emergency indicator, by contrast, is recorded and shown urgently, because the record of what the patient was told matters (AC-10, AD-22).

### 9. Co-review and reversal (ruling 62)

Every accepted act enters the co-review queue at once with a due time from the grant's window (AA-07). A named clinician authorized for the act class confirms, amends or voids it (AD-20). An overdue item escalates to the medical director and is never closed by a timer (AA-08). A clinician can void or countermand an AI act; nothing is deleted, and corrections are new dated records (AA-09). An AI act never modifies, discontinues or supersedes clinician-authored content (AA-10, AD-8).

### 10. Narrowing and pause

A narrowing or pause applies at once (AG-08). Pending AI acts that the grant no longer covers are held and handed to a named clinician, or cancelled by the medical director, and never executed on the AI's authority (AA-11, AD-9). "Pending" is defined by the foundation's act lifecycle.

### 11. Identity, context and standalone operation

A write resolves the patient only through an existing `OC Patient External Identifier` row in the AI system's namespace (AW-03, AD-23). There is no demographic matching, no merge and no master identity. Only `operational` writes are recorded; `scenario` and `simulation` are refused with an explicit code (AW-04, AD-18). Every component is optional, and with no AI system registered the write path accepts nothing (AW-10).

### 12. Labels

Every display of an AI-authored record, to a clinician or a patient, labels it AI-authored and states its review or co-review status without implying a prior sign-off (AW-09). Every act shows the authority it rested on (AA-12).

## What the recorded legal and regulatory review must cover

This change states no legal or regulatory rule. For each mode, the review that the medical director records (AG-05) must address at least these topics. Whether each topic is satisfied, and how, is for counsel and the medical director, not for this change.

1. The mode, and the act classes and act types in its scope.
2. The jurisdictions where the practice and its patients are located, and which rules apply in each.
3. For each act type, whether it may be the AI system's own act, under what conditions, and on whose licence or authority it is made.
4. Which acts must remain a licensed clinician's own act (the reserved list), including an explicit finding on controlled-substance prescribing.
5. Supervision, delegation, standing-order and protocol requirements, and whether after-the-fact co-review and the proposed window are acceptable.
6. Disclosure to patients and their consent for AI consults and AI acts, and the wording of the patient-facing labels.
7. Identification of the author of an AI act on any record or transmission that leaves the practice, such as a prescription or an order.
8. Record-keeping, attribution and retention of AI-authored records.
9. Accountability: who is the responsible clinician of record for an AI-authored act.
10. Emergency handling and escalation duties.
11. Privacy and security requirements for the write path.
12. The review's expiry, and the events that require re-review (a new act type, a new jurisdiction, a model change, a widening).

## Required prerequisite change: the clinical-acts foundation

**Proposed id `define-clinical-acts-foundation`. Required, not drafted.** Tier 2 is not buildable, and neither practice mode can be enabled, until it is ratified and built. It is also the clinical-encounter capability that `define-openpractice-boundary` Open Question 2 waits for. Its minimum contents:

1. **Clinician encounters**, with participants, period and status.
2. **Orders** (for example laboratory, imaging, referral and procedure), with a lifecycle that distinguishes draft, signed, pending release, released or executed, completed, discontinued or countermanded, and voided.
3. **Prescriptions**, with the same lifecycle plus dispense or transmission states, and a medication classification that marks controlled substances.
4. **Diagnoses of record** (problem list and encounter diagnoses), with verification status, kept distinct from patient-reported conditions.
5. **Treatment plans**, versioned, where each change is a new dated record.
6. **Authorship on every act:** an author kind (`clinician` or `ai`) and an authority-basis reference that this change's Tier 2 fills, plus clinician signing or attestation.
7. **An act-type registry:** act classes and act types as data, with flags for reserved acts and emergency management, which allowlist entries and AA-05 and AA-06 use.
8. **Roles:** clinician, nurse and medical director, with scope per act class.
9. **Amendment, void and countermand** as new dated records; nothing edited in place or deleted.
10. **Content schemas** for each act class, published so that a MINOR version of `openchart-ai-clinical-record-write` can pin them for `act_content`.
11. **Reconciliation with the ratified intake text** that tension AT-1 records, because clinician orders created through an API meet the same sentence.
12. **Billing interplay** with CF-02 and CF-06 of `define-openpractice-boundary`.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which must operate without MedxFactory, MedxEHR or openPractice | AW-10 restates it. Every component is optional; with no AI system the write path accepts nothing. Nothing needs openPractice (ruling 53). |
| Patient identity: an external identifier must not replace the openChart identifier or silently merge patients | AW-03. The write names the openChart triple; the AI system's reference is a namespaced external identifier; nothing is matched, merged or re-pointed. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Consult and act writes are idempotent too (AW-05). |
| Statements preserve reported detail | Untouched. Patient turns in a consult stay patient-reported (AC-02). |
| Amendments preserve accepted history | AC-01, AG-01, AA-09: nothing is overwritten; corrections are new versions or new dated records. |
| APIs and hooks are authorized and versioned | AW-01, AW-02: a dedicated role narrower than `System Manager`, authorized for subject, tenant, purpose and role; MAJOR versioning by digest. |
| Intake confers no clinician or autonomous authority | Tier 1 never creates an act (AC-04, AC-05). Tier 2 does create AI-authored acts through an API. **Tensions AT-1 and AT-2.** |

**Two possible conflicts with ratified openChart text are recorded, as AT-1 and AT-2.** No other conflict with ratified text was found.

## Consistency with `define-clinical-message-inbox` and `define-openpractice-boundary`

| Requirement | Relation |
|---|---|
| MI-12, MI-13 | Reused for the consult record (AC-01, AC-02). No second record is defined. **Tension AT-6.** |
| MI-24, MD-17 | Kept: the inbox files no copy; the consult record is the chart's copy, associated by conversation reference. |
| MI-26, MD-20 | Kept in substance until Tier 2 is in force for an act type (AA-01, AC-05). **Tensions AT-5 and AT-7.** |
| Open Question 4 | Answered: this change is openChart's receiving side of the AI system's governed chart path. |
| P-1, P-2 (its required later change) | Provided: P-1 by AA-02, AA-03 and AA-12; P-2 by AA-07 and AA-08. |
| PL-04, PL-12 | Pattern reused for this change's own contract (AW-01). |
| PL-13 | Extended to the write path (AW-07). |
| PL-14 | Pattern reused (AW-08). |
| PL-15 | Restated (AW-10). |
| CF-02, CF-05, CF-06 | Unchanged. Consult records are never billable (AC-04). **Tension AT-8** for AI acts. |

## Design calls for owner review

Each item goes beyond the rulings and is proposed, not ruled. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| AD-1 | **Proposed decision 65.** openChart keeps its own record of the medical director's authority grant and checks every write against it. It never accepts a write on the AI system's claim. | AG-01 |
| AD-2 | The consult record holds the full exchange, with an optional AI summary labelled as such. The alternative, a reference into the AI system plus a summary, is rejected for now (Decision 6). | AC-01 |
| AD-3 | The consult record is `define-clinical-message-inbox`'s clinical-communication record with origin `ai_consult`. Writing one needs neither the inbox enabled nor openPractice. Tier 1 therefore needs the inbox change ratified first or together; the alternative is to move the record into its own capability. | AC-01 |
| AD-4 | A consult write is accepted only under a current grant of `advice_only` or above. Without one it is refused, and the medical director sees an integration exception with identifiers only. | AG-06, AC-06 |
| AD-5 | A consult is checked against the grant version in force when it ended, so a consult that happened before a pause is still recorded. An act is checked at receipt, so an act made before a pause but received after it is refused. | AC-09, AA-03 |
| AD-6 | Authority signals are asymmetric. A reduction from any source, the AI system's own notice included, applies at once. A widening or resumption is only ever the medical director's act in openChart. | AG-08 |
| AD-7 | A refused write stores no clinical content. A refusal record holds identifiers and codes and is visible to the patient's doctor and the medical director. What the patient was told is in the consult record. | AW-06, AA-12 |
| AD-8 | In contract version 1.0 an AI act may not modify, discontinue or supersede clinician-authored content at all, which is stricter than the ruling's "never silently". It may supersede only its own source system's earlier AI act, visibly. | AA-10 |
| AD-9 | On a narrowing or pause, pending AI acts are held and handed to a named clinician by default; only the medical director or that clinician cancels one. | AA-11 |
| AD-10 | Every grant version and every recorded legal review carries an expiry or re-review date; nothing renews itself. | AG-09 |
| AD-11 | Four built-in always-review triggers that the medical director cannot remove: emergency indicator, no evidence reference for the consult or any AI turn, a linked refused act or held act content, and a declared red flag. | AC-07 |
| AD-12 | A consult is visible to every clinician authorized for the chart, and is listed for the responsible clinician, or for the medical director where openChart records none. | AC-06 |
| AD-13 | A consult selected for review has a review window set by the medical director; when it passes, the consult escalates to the medical director. | AC-08 |
| AD-14 | Every write carries a consent reference. openChart records it and does not evaluate it. | AC-03 |
| AD-15 | An act is reserved when openChart's classification or the AI system's declaration says so, whichever is stricter. | AA-05 |
| AD-16 | A limited-practice act's conditions that can be checked from chart data are re-checked by openChart; the others are recorded as the AI system's statement with evidence and examined in co-review. | AG-07, AA-04 |
| AD-17 | `act_content.content` is the contract's one open object until a MINOR version pins the foundation's content schemas. Every 1.x receiver refuses `act.write` until then. | AA-01 |
| AD-18 | `context` is an enum (`operational`, `scenario`, `simulation`) so that a non-operational write is refused with an explicit code rather than a schema error. | AW-04 |
| AD-19 | Ruling 63 is read as a build order. Enablement need not step through the modes, but a mode cannot be enabled before its build exists. | AG-03 |
| AD-20 | A co-reviewer is a named clinician whose role the medical director authorizes for the act class. The AI and agents never co-review. | AA-07 |
| AD-21 | openChart reports each consult review outcome to the AI system as a code, for its quality process. No text crosses. | AC-08 |
| AD-22 | A consult with an emergency indicator is recorded and shown urgently; an act with an emergency indicator is refused. | AC-10, AA-06 |
| AD-23 | The AI system's patient link is an `OC Patient External Identifier` row in its own namespace, registered through the ratified path or a later governed link contract. Its value may be minted for that link alone and need not be the AI system's internal patient identifier. No demographic matching. | AW-03 |
| AD-24 | The medical director is designated per practice by an audited act of a role decided in planning. With no medical director recorded, no grant can be approved. | AG-02 |
| AD-25 | Review outcomes are `concur`, `concur_with_note`, `follow_up_required` and `unsafe`; `unsafe` alerts the medical director at once and marks a follow-up owed. | AC-08 |
| AD-26 | A refused write for a patient-link mismatch or a conflicting duplicate records an integration exception with identifiers and a coded cause only. | AW-03, AW-05 |
| AD-27 | An AI turn, and an act, may carry its own evidence references and a neutral knowledge basis (`cited_sources`, `model_knowledge`, `mixed`), so that a reviewer can see which statements rest on cited sources and which on the model's own knowledge. Only AI turns may carry them. | AC-03, AA-02 |
| AD-28 | The contract carries a digest-only readback, answered only to the source system that wrote the record, so that a writer or its relay can confirm what the chart stored without any clinical content crossing back. | AW-12 |

## Conflicts and tensions

Nine are recorded. Each needs the owner's disposition before ratification. None is resolved by this draft on its own authority.

| # | Tension | Status |
|---|---|---|
| AT-1 | **Ratified text.** `expanded-patient-intake`, requirement "Intake does not confer clinician or autonomous authority": "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action." Tier 2 creates AI-authored prescriptions, orders and diagnoses through an API. Tier 1 records an AI's recommendations of next steps. | Reading proposed: the sentence sits in a requirement about intake and governs intake surfaces. A consult record keeps an external AI's advice as AI-generated communication and creates no treatment recommendation of record. If the owner reads the sentence as governing every openChart API, Tier 2, and the clinical-acts foundation's own clinician orders, need a MODIFIED delta to that requirement. Tier 2 is blocked until this is disposed. |
| AT-2 | **Ratified text.** The same requirement: "Patient statements SHALL remain visibly patient-reported until an authorized clinical workflow records another assertion." Does an AI act under a grant count as an "authorized clinical workflow"? | Reading proposed: Tier 1 never records another assertion over a patient statement. A Tier 2 diagnosis of record, accepted under a grant and co-reviewed, is a separate AI-authored record that may reference a patient statement and never alters it. Owner confirms at ratification. |
| AT-3 | openChart `AGENTS.md`: "Do not enable autonomous clinical actions by default." Tier 2 is autonomous clinical action. | Not a conflict by its letter: every mode is off by default and stays off until the medical director's grant and all three gates (AG-04). Recorded because Tier 2 is the first design that can enable such actions at all. |
| AT-4 | `contracts/p4-compatibility-declaration.yaml` publishes this guarantee: "every statement assertion_kind=patient_reported; no prescription, diagnosis, order, administration, or autonomous action is ever emitted". Downstream consumers vendor that declaration by digest. | The guarantee is scoped to component p4, the intake foundation, and stays true for it. The write path must publish its own compatibility declaration, and consumers must not read p4's as covering it. Owner confirms. |
| AT-5 | `define-clinical-message-inbox` (draft) MI-26 holds AI-authored acts as communication "until a later openChart change for practice modes is ratified". By its letter, ratifying this change would end that hold, though Tier 2 cannot be built yet. | AA-01 keeps the hold in substance until Tier 2 is in force for the act type. The inbox change should amend MI-26's wording to say so. |
| AT-6 | `define-clinical-message-inbox` (draft) defines the clinical-communication record inside the inbox capability, and MI-20 makes the inbox inert without an openPractice gateway. Ruling 53 keeps the AI's exchanges away from openPractice. | AD-3: the record's shape and rules are reused for origin `ai_consult`; its enablement is not. The owner may prefer to move the record into its own capability, which both changes would then cite. |
| AT-7 | `define-clinical-message-inbox` (draft) MD-20 holds content that presents itself as an AI-authored act as communication "by any path". This change refuses an `act.write` and stores no content (AD-7), and holds act-like content only inside a consult (AC-05). | Reading proposed: the consult record carries what the patient was told; a refused act write is a refusal record. Owner confirms, or directs that refused act content be held as communication. |
| AT-8 | `define-openpractice-boundary` (draft) CF-02 marks a fact billable only when it comes from clinician-authored documentation that is final and signed. An AI-authored diagnosis of record would therefore never be billable. | No conflict: nothing here is billable, and CF-06 is unchanged. Whether a co-reviewed AI act can ever be billable is for the clinical-acts foundation and the owner. |
| AT-9 | Ruling 60: "Anything not listed goes to the human doctor." openChart can show the refused attempt to the patient's doctor (AA-12), but the patient's need reaches the doctor only if the AI system routes the patient to the human-doctor path (HealthLinc, openPractice, the inbox). | Owner item. The AI system's change should own that routing; this change owns only the chart's view of the refusal. |

## Risks / Trade-offs

- **[An AI act rests on authority the chart cannot verify]** → The chart's own grant record (AD-1), checked field by field; refusal on any mismatch.
- **[The AI system keeps acting after a pause]** → A pause in either system applies at once in openChart (AD-6); later writes are refused, and consults that happened after the pause become integration exceptions for the medical director.
- **[AI text is mistaken for a clinician's]** → An author kind on every turn and act, labels on every surface, the patient's included.
- **[An unsafe answer reaches a patient]** → Ruling 57 accepts delivery without sign-off; the review sample, the built-in triggers and the `unsafe` alert are the safety net.
- **[Co-review backlog]** → Escalation to the medical director, who can narrow or pause.
- **[Two records of authority drift]** → The configuration version must match exactly; drift refuses writes rather than accepting them.
- **[Tier 1 waits on the inbox]** → AD-3; the alternative is a standalone record capability.
- **[A large consult record]** → Attachments by reference and digest; size limits in the schema.
- **[No constitution]** → Planning is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly. Brett Heap disposes AT-1 to AT-9 and AD-1 to AD-28, stamps `Ratified by` and sets `Status: ratified`. `define-clinical-message-inbox` is ratified first or together (AD-3).
2. Adopt openChart's constitution through separate governance.
3. Create the single Spec Kit feature from the assembly root, starting with Tier 1: the write-path role, the grant record for `advice_only`, the legal-review record, the review policy, the consult record and its review, and refusal of every `act.write` with `tier2_not_in_force`. Contract tests run against an AI-system double alongside the standalone regression suite.
4. Enable advice-only for a practice only when its gates are recorded (AG-04).
5. After `define-clinical-acts-foundation` is ratified and built: a governed revision of this change pins the foundation's content schemas in a MINOR contract version, then Tier 2 is built for limited practice, then for full practice (ruling 63).
6. Rollback: the medical director pauses the grant; the write path is disabled; open co-review items stay owned until they close; no record is deleted.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks planning.
2. **Owner dispositions** of AT-1 to AT-9 and AD-1 to AD-28, including proposed decision 65. These block ratification.
3. **The clinical-acts foundation.** Who drafts `define-clinical-acts-foundation`, and when? This blocks Tier 2.
4. **The responsible clinician.** openChart records no care team today. Which change defines a patient's responsible clinician? Meanwhile, AD-12's fallback to the medical director applies.
5. **The AI system's patient link.** Is it registered through the ratified external-identifier path, or through a governed link contract like PL-02's? Meanwhile, AD-23 applies.
6. **Retention** of consult records, refusal records and integration exceptions. The owner and counsel decide. Meanwhile, nothing is deleted.
7. **Who routes a refused act's patient to the human doctor** (AT-9). The AI system's change decides. Meanwhile, the refusal is shown to the doctor.
