## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

What is built today, and what is not:

- **Built:** `OC Patient`, `OC Patient External Identifier` (namespaced, versioned, with an `identity_review` status), `OC Intake Submission` and eight patient-reported statement families, behind the versioned API `open_chart.api.v1`. Every statement is `patient_reported`.
- **Roles:** every built DocType grants permissions to `System Manager` only. No clinician, nurse or medical-director role exists. openChart-spec#5 (`define-clinical-acts-foundation`) defines them in AU-01 and AU-02, and Tier 1 waits for that part of it, its feature (1).
- **Not built:** there are no clinician encounters, orders, prescriptions, diagnoses of record or treatment plans in openChart, and nothing records AI-authored content. This change does not write as if they exist. Tier 2 waits for a prerequisite change that builds them, now drafted as openChart-spec#5 (ruling 72), and for a future governed amendment (ruling 67).

**Two draft openChart changes are related, and neither is on main.**
- `define-clinical-message-inbox` (openChart-spec#3, branch `change/define-clinical-message-inbox`) defines routed patient questions for the human doctor and the clinical communication record. Its MI-12 is the single definition of that record in openChart and names this change as one that references it; its MI-13 keeps AI-authored content distinguishable. Its MI-26 holds all AI-authored content as communication only "until `define-ai-authored-clinical-records` is ratified", and its Open Question 4 leaves openChart's receiving side of the AI system's governed chart path to a separate change. This change answers both (tensions AT-5 to AT-7). Under ruling 69 that change also owns openChart's one neutral conversation-retrieval contract, `openchart-conversation-retrieval/1.0`; this change defines no conversation retrieval.
- `define-openpractice-boundary` (openChart-spec#2, branch `change/define-openpractice-boundary`) provides the patterns reused here: digest-pinned schemas (PL-04), a durable outbound store (PL-14), no PHI in diagnostics (PL-13), and standalone operation (PL-15). Its Open Question 2 asks which change introduces clinician-authored encounters, diagnoses and procedures; the prerequisite named here is that change.

**Cross-references, not dependencies of the text.** `MedxSoft/medXfactory` change `define-patient-medical-ai-connection` is drafted and not yet on main. It owns the medical-AI mode framework and its patient connection, and lists this change as a required companion. `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay` is the Medx-specific overlay on this contract. Nothing in this change depends on either system's internals. Under ruling 70 the medical AI's records reach openChart through MedxEHR, which relays them with receipts, and medXfactory does not write to openChart directly; the write path admits such a relay without naming it (AW-02, AD-30).

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main` (checked at revision `d20de75`). There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. Planning is blocked until a constitution is adopted.

Brett Heap's rulings are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

## Owner rulings (2026-11-14 and 2026-11-15)

Rows 35 to 64 have the source **Brett Heap, 2026-11-14, authoring session.** Rows 65 to 72 have the source **Brett Heap, 2026-11-15, decisions accepted in the alignment round.** The numbering is shared with the openPractice and inbox changes; a number absent here was not relayed to this change. Rows 73, 74 and 76 have the same date and source and are recorded in openChart-spec#5 (`define-clinical-acts-foundation`); this change cites them from there. The rulings name medXfactory as the system that holds the clinical medical AI. This change's requirements are neutral: they speak of "an external clinical AI system", and name medXfactory only as a cross-reference.

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
| 65 | The chart keeps its own record of the medical director's authorization and checks every AI write against it. Design call AD-1 is binding. | AG-01, AG-06; AD-1 |
| 66 | Advice-only mode is a patient-consult class: information, assessment and next steps, with no diagnosis language and no treatment directives. Answers reach the patient without prior sign-off, and the medical director's sampled review applies. | AG-03, AC-04, AC-05, AC-07, AC-08, AW-09; AD-31 |
| 67 | The ratified texts stand, among them openChart intake's bar on any prescription, diagnosis or order created by an intake, API response or extension event, together with the companion systems' own bars that the ruling names. Limited and full practice stay specified but off. They are revisited only through a future governed amendment, after advice-only has run and counsel's review is in. | AG-03, AG-04, AA-01; AT-1, AT-2, AT-4 |
| 69 | openChart owns one neutral conversation-retrieval contract, `openchart-conversation-retrieval/1.0`, published by `define-clinical-message-inbox` (openChart-spec#3). | AC-01: this change defines no conversation retrieval |
| 70 | The medical AI's records reach openChart through MedxEHR, which relays them with receipts. medXfactory does not write to openChart directly. | AW-02, AW-12; AD-30 |
| 72 | The clinical-acts foundation is being drafted now by another author, as `define-clinical-acts-foundation` (branch `change/define-clinical-acts-foundation`, base `main`). It accepts only `clinician` as author type and provides the signing and co-signature model that Tier 2 builds on. | AA-01, AA-02; required prerequisite; AT-10 |
| 73 | The foundation's scope is encounters, clinical notes, diagnoses, procedures, orders, prescriptions, and authorship, signing and amendment. Left for later changes: results ingestion, care plans and treatment-plan records, immunizations, clinical decision support, and electronic transmission of prescriptions to pharmacies. | AA-01 (`treatment_plan_change`); prerequisite items 3 and 5 |
| 74 | The prescription record is specified in the foundation, but the prescription feature is not buildable until allergy and interaction checking is specified. A prescription cannot be signed in any deployment where that gate is not met. | AA-03 |
| 76 | For `define-prescribing-safety-checks`: when the knowledge source is unavailable at signing, a clinician may sign only with a recorded statement that checks were unavailable and that a manual review was done. The prescription is flagged and re-checked when the source returns. A non-clinician author, including any future AI author, can never use that path. | AA-03 |

**The gates (same session).** Each mode stays off until (a) the medical director has approved that mode's scope, (b) a legal and regulatory review covering that mode is recorded, and (c) for limited and full practice, the chart can accept an AI-authored order, prescription or diagnosis recorded with the authority it acted under. Item (c) is what this change specifies. Ruling 67 adds (d) for the two practice modes: a future governed amendment, made after advice-only has run and counsel's review is in, that puts the mode in force. AG-04 encodes all four.

**What the 2026-11-15 rulings change.** Ruling 65 makes design call AD-1 binding: openChart holds its own record of the medical director's authorization and checks every AI write against it, rather than trusting the AI system's claim. Ruling 66 defines advice-only content: information, an assessment and next steps, with no diagnosis language and no treatment directives, delivered without prior sign-off under the medical director's sampled review (AC-04, AC-05, AC-07). Ruling 67 keeps the ratified texts and leaves the practice modes specified but off. Tier 1 is therefore the only tier in scope to build, and Tier 2 stays refused with `tier2_not_in_force` until both the clinical-acts foundation exists and a future governed amendment puts Tier 2 in force (AA-01, AG-04). Ruling 72 records that the foundation is being drafted; it is now openChart-spec#5, whose clinical roles and authority (AU-01 to AU-05) Tier 1 also relies on.

## Terms used in both changes

These names are used identically in this change and in `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay`.

| Term | Meaning |
|---|---|
| `openchart-ai-clinical-record-write/1.0` | The write-path contract this change owns. Schema `contracts/openchart-ai-clinical-record-write-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-ai-clinical-record-write:1.0`, SHA-256 `69a1420daa7e130614046a413bd31f15a4ea24bab810594bdd74013d7338ae5b`. |
| external clinical AI system | The system that writes AI-authored records. It is identified by `source_system` (issuer and namespace). |
| source token | A write's `source_system.namespace`: the token MI-12 uses for the source system where it defines one (for example `medxfactory`). `healthlinc`, `openpractice_agent` and `openchart` are refused (AW-02, AD-30). |
| relay | A system that holds the integration identity and delivers one source system's writes and receipts; the write still names the source system (ruling 70, AW-02). |
| author type | MI-12's author types. A consult turn carries `patient`, `representative` or `ai`, in the schema field `author_type` (AC-02). |
| authority grant | openChart's own record of the medical director's authorization, identified by `grant_id` and `grant_version` (AG-01). |
| mode | `advice_only` (the default), `limited_practice` or `full_practice`. The two practice modes are specified but off (ruling 67). |
| advice-only content | Information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66, AC-05). |
| configuration version | The AI system's configuration that the medical director approved, as `configuration_version`. |
| allowlist entry | One limited-practice entry, `allowlist_entry_id`, with its act type, conditions and `protocol_ref`. |
| recorded legal and regulatory review | The review covering a mode, referenced by `legal_review_ref` (AG-05). |
| medical director | The practice's medical director as openChart-spec#5 AU-01 designates it, the single definition in openChart; referenced by `approver_ref` (AG-02). |
| consult review grant | The openChart-spec#5 AU-02 grant of action `review` over record class `ai_consult_record`; a named clinician must hold it to record a consult review (AG-11). |
| consult record | Tier 1: one AI consult, written by `consult.write`, on MI-12's clinical communication record with origin `ai_consult` (AC-01). Never a diagnosis or a clinical fact of record, and labelled as AC-04 states. |
| quarantined consult | A consult refused at the grant checks and kept as AI communication labelled with its coded cause, carrying `ai_consult_state` `quarantined`: always reviewed within a fixed window, never accepted, never a clinical fact (AC-11). |
| AI-authored clinical act | Tier 2: an `order`, `prescription`, `diagnosis_of_record` or `treatment_plan_change`, written by `act.write` (AA-01). |
| review policy | The medical director's review sample rate, always-review categories and review window (AG-10, AC-07). |
| built-in review codes | `red_flag` and `advice_scope_breach` in `review_flags`; each always selects a consult for review (AC-07). |
| co-review queue, co-review window | Clinician co-review of AI acts after the fact, within the window the medical director sets (AA-07). |
| reserved act | An act reserved to a human clinician unless the recorded legal review clears it (AA-05). |
| write receipt | `write.receipt`: `accepted`, `duplicate` or `refused` with a reason code (AW-06). |
| readback | `record.readback_request` and `record.readback`: the writing system confirms what openChart stored, by digest and code only (AW-12). |
| authority notice | `authority.notice`: a change in authority, from either side (AG-08). |
| context | `operational`, `scenario` or `simulation`; only `operational` is recorded (AW-04). |
| knowledge basis | What an AI turn's or act's statements rest on: `cited_sources`, `model_knowledge` or `mixed` (AC-03, AD-27). |
| source authority reference | The AI system's own reference to the configuration it acted under, `source_authority_ref` (AG-01). |
| clinical-acts foundation | The required prerequisite change `define-clinical-acts-foundation`, drafted by another author as openChart-spec#5 (ruling 72). Its feature (1) carries the clinical roles and authority Tier 1 needs. |

## Goals / Non-Goals

**Goals:**

- Give openChart a neutral, versioned write path for records from an external clinical AI system operating under a declared authority.
- Make Tier 1, the AI consult record, buildable without any orders model, on the foundation's clinical roles and authority (openChart-spec#5 feature (1)), so that advice-only mode can be switched on once its gates are met.
- Specify Tier 2's authorship, authority, co-review and reversal layer now, so the clinical-acts foundation can be built to receive it, while Tier 2 stays refused (ruling 67).
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
| 1 | AI consult records: the exchange, its provenance and its review | `advice_only` and above | After ratification, the constitution, the inbox's ratification (AD-3), and openChart-spec#5's feature (1), clinical authority (AU-01 to AU-06), which carries the clinical roles and authority Tier 1 relies on (AU-01 to AU-05; AG-02, AG-11) |
| 2 | AI-authored clinical acts: authorship, authority, co-review, reversal | `limited_practice`, `full_practice` (specified, off) | No, and not in scope to build: it needs the clinical-acts foundation ratified and built and a future governed amendment (ruling 67, AA-01) |

Tier 1 is the only tier in scope to build (rulings 66 and 67).

### 2. The contract

`openchart-ai-clinical-record-write/1.0` is owned by this change (AW-01). The schema follows the convention of the openPractice-spec contracts that `define-openpractice-boundary` and `define-clinical-message-inbox` pin: JSON Schema draft 2020-12, a URN `$id`, `oneOf` over the messages, every object closed, and `contracts/SHA256SUMS`. The one open object is `act_content.content`, reserved for the foundation's content schemas (AD-17).

| Message | Direction | Use |
|---|---|---|
| `consult.write` | AI system → openChart | Tier 1 consult record (AC-01) |
| `act.write` | AI system → openChart | Tier 2 act; refused with `tier2_not_in_force` until the foundation exists and a future governed amendment puts Tier 2 in force (AA-01) |
| `authority.notice` | both | A change in authority; from the AI system only a reduction is accepted (AG-08) |
| `write.receipt` | openChart → AI system | The answer to every write and notice (AW-06) |
| `act.status` | openChart → AI system | Co-review outcome, reversal, hand-off, cancellation, escalation (AA-07 to AA-11) |
| `consult.reviewed` | openChart → AI system | Review outcome as a code (AC-08) |
| `record.readback_request` | AI system or its relay → openChart | Asks what openChart stored for a record it wrote (AW-12) |
| `record.readback` | openChart → AI system or its relay | The stored record's identifiers, content digest, grant version, state and review status; no content (AW-12) |
| `message.ack` | both | Acknowledges a status or notice |

The refusal reasons are closed, and AW-06 fixes the order in which they are checked: `schema_invalid`, `unsupported_major_version`, `unauthorized`, `non_operational_context`, `patient_link_unknown`, `patient_link_mismatch`, `patient_link_in_review`, `no_current_grant`, `grant_paused`, `grant_expired`, `grant_revoked`, `grant_mismatch`, `mode_mismatch`, `mode_not_permitted`, `allowlist_entry_unknown`, `allowlist_entry_mismatch`, `conditions_unverified`, `reserved_act_refused`, `emergency_management_refused`, `approver_mismatch`, `legal_review_mismatch`, `targets_clinician_record`, `act_type_unsupported`, `tier2_not_in_force`, `conflicting_duplicate`, `content_digest_mismatch` and `notice_would_widen`.

`contracts/examples/` holds 37 synthetic fixtures: 13 that must validate and 24 that must fail, each for one stated reason. They are part of the contract-test suite (AW-11).

### 3. openChart's own record of authority (ruling 65)

The chart keeps its own grant record and checks every write against it (AG-01, AD-1). The AI system's claim is compared with the chart's record and never substitutes for it. The alternative, accepting the AI system's signed statement of its mode, was rejected: a defect or compromise in the AI system would then create clinical acts in the chart with no independent check, and the chart could not show a clinician what authority a record rested on.

Only the medical director, as openChart-spec#5 AU-01 designates, approves, widens or resumes a grant (AG-02), and only that person records consult review grants (AG-11). A reduction applies at once from any source, the AI system's own notice included; a widening is only ever the medical director's act in openChart (AG-08, AD-6). Grants and legal reviews expire and never renew themselves (AG-09, AD-10).

### 4. Modes and gates

`advice_only` is the default (AG-03). A grant is activated only when the gates are met for its mode (AG-04): the medical director's approval of the mode's scope, a recorded legal and regulatory review covering that mode, and, for the practice modes, Tier 2 built over the foundation and a future governed amendment that puts the mode in force (ruling 67). No such amendment exists, so only `advice_only` can be approved. Ruling 63 is a build order: the modes are built advice, limited, full; enablement need not step through them, but a mode cannot be enabled before its build exists (AD-19).

### 5. How AI output is classified

| Content | Class | Becomes a clinical fact of record? |
|---|---|---|
| A patient's or representative's turn in a consult | Patient-reported, as the ratified intake requirement keeps it | No |
| An AI turn or summary in a consult | AI-generated communication (AC-04) | No, in any mode |
| Consult content that presents itself as an act | AI-generated communication, shown as not accepted as a clinical act (AC-05) | No |
| Diagnosis language or a treatment directive in advice-only content | AI-generated communication; always reviewed when declared `advice_scope_breach`, and a reviewer's breach finding alerts the medical director (AC-05) | No |
| An AI-authored act accepted under a current practice-mode grant | An act of record with author type `ai`, its authority stated, pending co-review (AA-02, AA-12) | Only once Tier 2 is in force, which ruling 67 defers to a future governed amendment |
| A refused AI act | A refusal record with identifiers and codes only (AW-06, AA-12) | No |
| A consult refused at the grant checks | Quarantined AI communication, labelled with its coded cause, always reviewed within a fixed window, with fallback recipients (AC-11) | No |
| A clinician's amendment, or a countermand to `discontinued` or `cancelled` | A clinician-authored record | Yes |

### 6. The Tier 1 consult record and the inbox

The consult record is the clinical communication record that MI-12 defines, cited by requirement ID, with origin `ai_consult` (AC-01, AD-3). It holds the full exchange, each turn with its MI-12 author type, plus an optional AI summary labelled as such (AD-2). The alternative, a reference into the AI system plus a summary, was rejected for now: ruling 57 puts every consult "in the chart", a summary written by the same AI would be the doctor's only view of its own advice, and a reference fails when the AI system is unreachable or its store changes.

An inbox item that names the same conversation is associated with the consult record by the conversation reference. The inbox still files no copy (MI-24). Writing a consult record needs neither the inbox enabled nor openPractice, because ruling 53 keeps the AI's exchanges away from openPractice (tension AT-6). This change defines no conversation retrieval: that is `openchart-conversation-retrieval/1.0`, which ruling 69 assigns to `define-clinical-message-inbox`.

### 7. Review (ruling 57)

openChart selects consults for review, not the AI system (AC-07). The review policy, set by the medical director as part of the grant, has a sample rate, always-review categories and a review window (AG-10). Six built-in triggers cannot be removed: the emergency indicator, no evidence reference at all, a linked refused act or held act content, the declared codes `red_flag` and `advice_scope_breach`, and quarantine (AD-11). A consult refused at the grant checks is quarantined, not dropped: its answer already reached the patient, so it stays visible to the patient's doctor (AC-11, AD-33). openChart does not parse consult text to enforce ruling 66. A reviewer who finds diagnosis language or a treatment directive records the finding `advice_scope_breach`, which alerts the medical director at once (AC-08, AD-31). A named clinician holding a consult review grant (AG-11) records the review status, reviewer and outcome (AC-08). An overdue review escalates to the medical director (AD-13). An `unsafe` outcome alerts the medical director at once.

### 8. Tier 2 (specified, refused under ruling 67): acceptance, reserved acts and emergencies

An act is accepted only under a current practice-mode grant that it matches in every field (AA-03). A limited-practice act must match its allowlist entry, protocol and checkable conditions (AA-04, AD-16). A reserved act is refused in every mode unless the grant's legal review cleared it; reservedness is the stricter of openChart's classification and the AI system's declaration (AA-05, AD-15). An act marked as emergency management is always refused, and no clearance can change that (AA-06). A consult with an emergency indicator, by contrast, is recorded and shown urgently, because the record of what the patient was told matters (AC-10, AD-22).

### 9. Co-review and reversal (ruling 62)

Every accepted act enters the co-review queue at once with a due time from the grant's window (AA-07). A named clinician holding `cosign` scope for the act class under openChart-spec#5 AU-02 confirms, amends or voids it (AD-20). openChart-spec#5 CA-07 defines a co-signature model of its own, and the two converge on CA-07 at the Tier 2 amendment (tension AT-11). A void is the foundation's `entered_in_error` and a countermand its `discontinued` (or `cancelled` while `pending_release`). An AI prescription is accepted only on an `open` prescribing-safety gate decision for its exact content, never on the outage path (AA-03; openChart-spec#6 PG-01, ruling 76). An overdue item escalates to the medical director and is never closed by a timer (AA-08). A clinician can void or countermand an AI act; nothing is deleted, and corrections are new dated records (AA-09). An AI act never modifies, discontinues or supersedes clinician-authored content (AA-10, AD-8). Co-review would build on the foundation's signing and co-signature model (ruling 72); that mapping belongs to the future governed amendment.

### 10. Narrowing and pause

A narrowing or pause applies at once (AG-08). Pending AI acts that the grant no longer covers are held and handed to a named clinician, or cancelled by the medical director, and never released on the AI's authority (AA-11, AD-9). "Pending" is the foundation's `pending_release`: signed but not yet in force (its CT-7).

### 11. Identity, context and standalone operation

A write resolves the patient only through an existing `OC Patient External Identifier` row in the AI system's namespace (AW-03, AD-23). There is no demographic matching, no merge and no master identity. Only `operational` writes are recorded; `scenario` and `simulation` are refused with an explicit code (AW-04, AD-18). Every component is optional, and with no AI system registered the write path accepts nothing (AW-10).

### 12. Labels

Every display of an AI-authored record, to a clinician or a patient, labels it AI-authored and states its review or co-review status without implying a prior sign-off (AW-09). Every act shows the authority it rested on (AA-12). A consult record also carries the ruling-66 label: information, assessment and next steps only, not a diagnosis and not a treatment instruction (AC-04).

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

**`define-clinical-acts-foundation`. Required; drafted (ruling 72)** by another author as openChart-spec#5, branch `change/define-clinical-acts-foundation`, not yet ratified. This change does not edit it. Its feature (1), clinical authority (AU-01 to AU-06), is also a prerequisite of Tier 1, for the clinical roles and authority of AU-01 to AU-05 (AG-02, AG-11). Tier 2 is not buildable, and neither practice mode can be enabled, until it is ratified and built and a future governed amendment puts Tier 2 in force (ruling 67). It is also the clinical-encounter capability that `define-openpractice-boundary` Open Question 2 waits for. Ruling 72 says it accepts only `clinician` as author type and provides the signing and co-signature model that Tier 2 builds on. What this change needs of it:

1. **Clinician encounters**, with participants, period and status.
2. **Orders** (for example laboratory, imaging, referral and procedure), with the foundation's closed lifecycle `draft`, `pending_release`, `released`, `completed`, `discontinued`, `cancelled` and `entered_in_error` (CA-03, OR-02). Signing is an event and a signature (CA-04), not a status (its CT-7).
3. **Prescriptions**, with the same lifecycle and a classification that marks controlled substances (RX-01, RX-03). This change asks for no dispense or transmission state: the foundation reserves `transmission_status`, fixed at `none_recorded` in 1.x (RX-04), and dispense and transmission wait for a later e-prescribing change (its CT-8).
4. **Diagnoses of record** (problem list and encounter diagnoses), with verification status, kept distinct from patient-reported conditions.
5. **Treatment plans**, versioned, where each change is a new dated record. Not in the foundation: ruling 73 leaves treatment-plan records to a later change, which is a prerequisite of the `treatment_plan_change` act class (its CT-6; AA-01).
6. **Authorship on every act:** an author type, and clinician signing and co-signature (ruling 72). The foundation accepts only `clinician`; author type `ai`, and the authority-basis reference that Tier 2 fills, wait for the future governed amendment (tension AT-10).
7. **An act-type registry:** act classes and act types as data, with flags for reserved acts and emergency management, which allowlist entries and AA-05 and AA-06 use.
8. **Roles:** clinician, nurse and medical director, with scope per act class. openChart-spec#5 provides them in AU-01 and AU-02, which this change cites as the single definition (AG-02, AG-11).
9. **Amendment, entered-in-error marks and discontinuation** as new dated records (CA-05, CA-06, OR-02); nothing edited in place or deleted.
10. **Content schemas** for each act class, published so that a MINOR version of `openchart-ai-clinical-record-write` can pin them for `act_content`.
11. **Reconciliation with the ratified intake text** that tension AT-1 records, because clinician orders created through an API meet the same sentence.
12. **Billing interplay** with CF-02 and CF-06 of `define-openpractice-boundary`.

openChart-spec#5 maps each item in its own minimum-contents table: item 3 is provided in part (its CT-8) and item 5 is not provided (its CT-6). **Further prerequisites for parts of Tier 2:** a later treatment-plan change for `treatment_plan_change` (ruling 73), and `define-prescribing-safety-checks` (openChart-spec#6), with its gate `open`, for any AI prescription (ruling 74; AA-03).

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which must operate without MedxFactory, MedxEHR or openPractice | AW-10 restates it. Every component is optional; with no AI system the write path accepts nothing. Nothing needs openPractice (ruling 53). |
| Patient identity: an external identifier must not replace the openChart identifier or silently merge patients | AW-03. The write names the openChart triple; the AI system's reference is a namespaced external identifier; nothing is matched, merged or re-pointed. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Consult and act writes are idempotent too (AW-05). |
| Statements preserve reported detail | Untouched. Patient turns in a consult stay patient-reported (AC-02). |
| Amendments preserve accepted history | AC-01, AG-01, AA-09: nothing is overwritten; corrections are new versions or new dated records. |
| APIs and hooks are authorized and versioned | AW-01, AW-02: a dedicated role narrower than `System Manager`, authorized for subject, tenant, purpose and role; MAJOR versioning by digest. |
| Intake confers no clinician or autonomous authority | Tier 1 never creates an act (AC-04, AC-05). Tier 2 would create AI-authored acts through an API; under ruling 67 the text stands and Tier 2 stays refused. **Tensions AT-1 and AT-2, disposed by ruling 67.** |

**Two conflicts with ratified openChart text are recorded, as AT-1 and AT-2. Ruling 67 disposes both: the ratified text stands, and Tier 2 stays refused.** No other conflict with ratified text was found.

## Consistency with `define-clinical-acts-foundation` and `define-prescribing-safety-checks`

| Their item | Relation |
|---|---|
| openChart-spec#5 AU-01, AU-02 | The single definitions of the medical director and of role grants; AG-02 and AG-11 cite them (its CT-9) |
| #5 CT-6 (treatment plans) | AA-01: `treatment_plan_change` is refused with `act_type_unsupported`, and the later treatment-plan change is a prerequisite of that act class |
| #5 CT-7 (status names) | Prerequisite items 2 and 9, AA-07, AA-09 and AA-11 use `pending_release`, `released`, `discontinued`, `cancelled` and `entered_in_error`, with signing as an event. The contract's Tier 2-only codes are mapped in AD-34 |
| #5 CT-8 (dispense and transmission) | Item 3 asks for no such state; `transmission_status` stays `none_recorded` in 1.x (RX-04) until the later e-prescribing change |
| #5 CA-07 | Tension AT-11 |
| openChart-spec#6 PG-01, PG-02 (its PT-4) | AA-03: an AI prescription is accepted only on an `open` gate decision for its exact content, never on the outage path (ruling 76) |

## Consistency with `define-clinical-message-inbox` and `define-openpractice-boundary`

| Requirement | Relation |
|---|---|
| MI-12, MI-13 | Cited by requirement ID for the consult record (AC-01, AC-02). MI-12 is the single definition, and no second record is defined. Consult author types are MI-12's. **Tension AT-6, partly resolved.** |
| MI-24, MD-17 | Kept: the inbox files no copy; the consult record is the chart's copy, associated by conversation reference. |
| MI-26, MD-20 | Kept in substance until Tier 2 is in force for an act type (AA-01, AC-05). **Tensions AT-5 and AT-7.** |
| Open Question 4 | Answered: this change is openChart's receiving side of the AI system's governed chart path. |
| `openchart-conversation-retrieval/1.0` (ruling 69) | Owned by `define-clinical-message-inbox`. This change defines no conversation retrieval. |
| P-1, P-2 (its required later change) | Provided: P-1 by AA-02, AA-03 and AA-12; P-2 by AA-07 and AA-08. |
| PL-04, PL-12 | Pattern reused for this change's own contract (AW-01). |
| PL-13 | Extended to the write path (AW-07). |
| PL-14 | Pattern reused (AW-08). |
| PL-15 | Restated (AW-10). |
| CF-02, CF-05, CF-06 | Unchanged. Consult records are never billable (AC-04). **Tension AT-8** for AI acts. |

## Design calls for owner review

Each item goes beyond the rulings and is proposed, not ruled, except AD-1, which ruling 65 made binding. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| AD-1 | **Ruled: ruling 65 makes this binding.** openChart keeps its own record of the medical director's authority grant and checks every write against it. It never accepts a write on the AI system's claim. | AG-01 |
| AD-2 | The consult record holds the full exchange, with an optional AI summary labelled as such. The alternative, a reference into the AI system plus a summary, is rejected for now (Decision 6). | AC-01 |
| AD-3 | The consult record is `define-clinical-message-inbox`'s clinical-communication record with origin `ai_consult`. Writing one needs neither the inbox enabled nor openPractice. Tier 1 therefore needs the inbox change ratified first or together; the alternative is to move the record into its own capability. | AC-01 |
| AD-4 | A consult write is accepted only under a current grant, which under ruling 67 can only be `advice_only`. Without one it is refused, and the medical director sees an integration exception with identifiers only. | AG-06, AC-06 |
| AD-5 | A consult is checked against the grant version in force when it ended, so a consult that happened before a pause is still recorded. An act is checked at receipt, so an act made before a pause but received after it is refused. | AC-09, AA-03 |
| AD-6 | Authority signals are asymmetric. A reduction from any source, the AI system's own notice included, applies at once. A widening or resumption is only ever the medical director's act in openChart. | AG-08 |
| AD-7 | A refused write stores no clinical content, except a consult refused at the grant checks, which AC-11 keeps as quarantined AI communication (AD-33). A refusal record holds identifiers and codes and is visible to the patient's doctor and the medical director. What the patient was told is in the consult record or the quarantined consult. | AW-06, AA-12, AC-11 |
| AD-8 | In contract version 1.0 an AI act may not modify, discontinue or supersede clinician-authored content at all, which is stricter than the ruling's "never silently". It may supersede only its own source system's earlier AI act, visibly. | AA-10 |
| AD-9 | On a narrowing or pause, pending AI acts are held and handed to a named clinician by default; only the medical director or that clinician cancels one. | AA-11 |
| AD-10 | Every grant version and every recorded legal review carries an expiry or re-review date; nothing renews itself. | AG-09 |
| AD-11 | Six built-in always-review triggers that the medical director cannot remove: emergency indicator, no evidence reference for the consult or any AI turn, a linked refused act or held act content, the declared codes `red_flag` and `advice_scope_breach`, and quarantine (AC-11). | AC-07 |
| AD-12 | A consult is visible to every clinician authorized for the chart, and is listed for the responsible clinician, or for the medical director where openChart records none. | AC-06 |
| AD-13 | A consult selected for review has a review window set by the medical director; when it passes, the consult escalates to the medical director. | AC-08 |
| AD-14 | Every write carries a consent reference. openChart records it and does not evaluate it. | AC-03 |
| AD-15 | An act is reserved when openChart's classification or the AI system's declaration says so, whichever is stricter. | AA-05 |
| AD-16 | A limited-practice act's conditions that can be checked from chart data are re-checked by openChart; the others are recorded as the AI system's statement with evidence and examined in co-review. | AG-07, AA-04 |
| AD-17 | `act_content.content` is the contract's one open object until a MINOR version pins the foundation's content schemas. Every 1.x receiver refuses `act.write` until then, and until a future governed amendment puts Tier 2 in force (ruling 67). | AA-01 |
| AD-18 | `context` is an enum (`operational`, `scenario`, `simulation`) so that a non-operational write is refused with an explicit code rather than a schema error. | AW-04 |
| AD-19 | Ruling 63 is read as a build order. Enablement need not step through the modes, but a mode cannot be enabled before its build exists. | AG-03 |
| AD-20 | A co-reviewer is a named clinician holding `cosign` scope for the act class under openChart-spec#5 AU-02. The AI and agents never co-review (its AU-05). | AA-07 |
| AD-21 | openChart reports each consult review outcome to the AI system as a code, for its quality process. No text crosses. | AC-08 |
| AD-22 | A consult with an emergency indicator is recorded and shown urgently; an act with an emergency indicator is refused. | AC-10, AA-06 |
| AD-23 | The AI system's patient link is an `OC Patient External Identifier` row in its own namespace, registered through the ratified path or a later governed link contract. Its value may be minted for that link alone and need not be the AI system's internal patient identifier. No demographic matching. | AW-03 |
| AD-24 | The medical director is the one openChart-spec#5 AU-01 designates, the single definition in openChart; this change defines no designation of its own. With no designation in force, no grant can be approved and no consult review grant recorded. | AG-02, AG-11 |
| AD-25 | Review outcomes are `concur`, `concur_with_note`, `follow_up_required` and `unsafe`; `unsafe` alerts the medical director at once and marks a follow-up owed. | AC-08 |
| AD-26 | A refused write for a patient-link mismatch or a conflicting duplicate records an integration exception with identifiers and a coded cause only. | AW-03, AW-05 |
| AD-27 | An AI turn, and an act, may carry its own evidence references and a neutral knowledge basis (`cited_sources`, `model_knowledge`, `mixed`), so that a reviewer can see which statements rest on cited sources and which on the model's own knowledge. Only AI turns may carry them. | AC-03, AA-02 |
| AD-28 | The contract carries a digest-only readback, answered only to the source system that wrote the record, so that a writer or its relay can confirm what the chart stored without any clinical content crossing back. | AW-12 |
| AD-29 | When several refusal reasons apply, openChart reports the first in a fixed precedence (AW-06): `tier2_not_in_force` comes before every grant, mode and act check, so a Tier 1 deployment answers every act write the same way. Idempotency is scoped to the authenticated practice and source system (AW-05). A set emergency indicator makes any refused act's record urgent, whatever its reason. | AW-05, AW-06 |
| AD-30 | A source system's namespace is the source token MI-12 uses for it where MI-12 defines one (for example `medxfactory`). `healthlinc` and `openpractice_agent` are never write-path sources, and `openchart` is never a source namespace; the schema refuses all three. MI-12 records that HealthLinc's coach gives general health information only (rulings 51 and 54), and ruling 53 keeps the medical AI's exchanges away from openPractice. A relay may hold the integration identity for one source system (ruling 70); the write names the source system, not the relay. A source whose owner has ruled that it writes only through a relay is registered relay-only: openChart registers only its relay's identity and refuses a direct one. Ruling 70 is such a ruling. | AW-02 |
| AD-31 | openChart enforces ruling 66 without parsing, classifying or rewriting consult text. It relies on the source system's own advice-scope control and its `advice_scope_breach` declaration, on the built-in triggers and the sample, and on the reviewer's breach finding, which alerts the medical director at once. In contract 1.0 the finding stays in openChart, and `consult.reviewed` carries only the outcome code. Whatever the text says, a consult record is never a diagnosis or a clinical fact of record. | AC-04, AC-05, AC-08 |
| AD-32 | The consult review grant is the openChart-spec#5 AU-02 grant of action `review` over record class `ai_consult_record`, which is not an act class and creates no act; AU-02 carries it as of head `317beda` (AT-12). Only a holder with the `clinician` role may review; nurses may not review AI consults until the owner says otherwise. | AG-11, AC-08 |
| AD-33 | Quarantine covers a consult refused at any grant check (AW-06 step 8), mismatches included, because in every such case the answer reached the patient. A consult refused earlier (schema, identity, replay, context, digest or patient link) is not quarantined, because its source, content or patient cannot be relied on. The receipt stays `refused` with no `record_ref`, so the AI system never counts the consult as accepted, and no readback or `consult.reviewed` discloses it. | AC-11, AW-06 |
| AD-34 | The 1.0 contract's Tier 2-only codes keep their names: `act.status` `voided`, `countermanded` and `co_review_voided`, and readback `record_state` `voided` and `countermanded`. They are never sent while Tier 2 is refused. They correspond to the foundation's `entered_in_error`, and to `discontinued` (or `cancelled` for an act still `pending_release`), as its CT-7 maps them. The MINOR version that puts Tier 2 in force adds the foundation's names. Changing 1.0 now would change a digest that two companions pin. | AA-07, AA-09 |
| AD-35 | An AI prescription that the prescribing-safety gate does not open is refused with `prescribing_gate_not_open`, a reason the Tier 2 MINOR version adds. An `outage_path` decision counts as refused for an AI author (ruling 76). | AA-03, AW-06 |
| AD-36 | A quarantined consult's review window is fixed in openChart and needs no grant: 24 hours, or 1 hour with the emergency indicator or `red_flag`. A review policy may shorten it, never lengthen it. The values are proposed for the owner and the medical director to confirm. | AC-11 |
| AD-37 | Two suspensions and a deregistration, audited and effective at once. A manual suspension or deregistration (a human judged the source unsafe) refuses every write at step 2 and stores nothing; only the medical director lifts a manual suspension. A cap suspension, triggered by a per-source quarantine cap of at most 20 non-urgent quarantines in a rolling 24 hours, stops only non-urgent consults: emergency and `red_flag` consults never count and are still quarantined and listed urgently. While no medical director is designated, the administrative role may lift a cap suspension, never a manual one, and lifting grants nothing. The ceiling is proposed for the owner to confirm. | AW-13 |
| AD-38 | The quarantined mark is three fields on MI-12's record, only for origin `ai_consult`: `ai_consult_state` (`accepted` or `quarantined`), `quarantine_cause` (one of the nine step-8 codes) and `quarantine_grant_checked` (grant id and version, when a grant existed). `quarantine_cause` may also be `source_cap_suspended` (AW-13). `define-clinical-message-inbox` defines the record; this change asks that change to accept these fields. | AC-11 |
| AD-39 | With no responsible clinician or no medical director, a quarantined consult is listed for every clinician authorized for the chart, and the administrative role gets an alert with no clinical content. When nobody holds an AG-11 grant, any named holder of the `clinician` role authorized for the chart may review a quarantined consult, marked as made without a grant (AT-13). | AC-11 |
| AD-40 | What the source receives, using existing codes only: a write refused under a manual suspension, a deregistration, or a cap suspension (non-urgent) gets `refused` `unauthorized`; an emergency or `red_flag` consult from a cap-suspended source gets `refused` with its step-8 reason, or `unauthorized` when every grant check passes. No existing code says "quarantined because the source is cap-suspended", so `unauthorized` is used and the internal cause is `source_cap_suspended`. Every case tells the source the consult was not recorded. A refused write that declared the emergency indicator or `red_flag` keeps them on its refusal record and is listed urgently without content. | AW-06, AW-13, AC-11 |

## Conflicts and tensions

Thirteen are recorded. The Disposition column gives the owner's disposition where a 2026-11-15 ruling made one, and otherwise the status. None is resolved by this draft on its own authority.

| # | Tension | Disposition |
|---|---|---|
| AT-1 | **Ratified text.** `expanded-patient-intake`, requirement "Intake does not confer clinician or autonomous authority": "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action." Tier 2 creates AI-authored prescriptions, orders and diagnoses through an API. Tier 1 records an AI's recommendations of next steps. | **Disposed by ruling 67: the ratified text stands.** Tier 2 stays specified and refused with `tier2_not_in_force`. Putting it in force needs both the clinical-acts foundation and a future governed amendment, which must address this sentence, as the foundation must for clinician orders created through an API. For Tier 1 the reading stands: a consult record keeps an external AI's advice as AI-generated communication and creates no treatment recommendation of record. **Residual, for the owner:** the sentence also names a "treatment recommendation", and ruling 66 allows next steps while forbidding treatment directives. This change reads next steps such as "seek emergency care" or "book an appointment" as not a treatment recommendation, and treats anything that directs treatment as an advice-scope breach (AC-05, AD-31). The owner confirms or rejects this reading. |
| AT-2 | **Ratified text.** The same requirement: "Patient statements SHALL remain visibly patient-reported until an authorized clinical workflow records another assertion." Does an AI act under a grant count as an "authorized clinical workflow"? | **Disposed by ruling 67: the ratified text stands.** Tier 1 records no assertion over a patient statement. Tier 2, which could, stays refused, and the future governed amendment must address this sentence. |
| AT-3 | openChart `AGENTS.md`: "Do not enable autonomous clinical actions by default." Tier 2 is autonomous clinical action. | **Consistent; no action.** Every mode is off by default, and under ruling 67 neither practice mode can be approved at all. |
| AT-4 | `contracts/p4-compatibility-declaration.yaml` publishes this guarantee: "every statement assertion_kind=patient_reported; no prescription, diagnosis, order, administration, or autonomous action is ever emitted". Downstream consumers vendor that declaration by digest. | **Stands (ruling 67); consistent while Tier 2 is refused.** p4's guarantee stays true for p4, and Tier 1 emits no prescription, diagnosis, order, administration or autonomous action. The write path publishes its own compatibility declaration (task 5.1), and consumers must not read p4's as covering it. |
| AT-5 | `define-clinical-message-inbox` (draft) MI-26 holds all AI-authored content as communication only "until `define-ai-authored-clinical-records` is ratified". By its letter, ratifying this change would end that hold, though Tier 2 stays refused under ruling 67. | **Open, cross-change.** AA-01 keeps the hold in substance until Tier 2 is in force for an act type. The inbox change should amend MI-26's wording to say so. |
| AT-6 | `define-clinical-message-inbox` (draft) MI-12 is the single definition of the clinical communication record, but its provenance list is written for handoff items: handoff references and, for a conversation medXfactory holds, no copy of the exchange. Its MI-20 makes the inbox inert without an openPractice gateway, and ruling 53 keeps the AI's exchanges away from openPractice. | **Partly resolved.** MI-12 now names this change as one that references the record, and this change cites MI-12 by requirement ID and defines no second record. Residual: AD-3 adds the `ai_consult` fields, including the full exchange, which MI-12's provenance list does not mention. The inbox change should name origin `ai_consult` in MI-12, or the owner moves the record into its own capability. |
| AT-7 | `define-clinical-message-inbox` (draft) MD-20 holds content that presents itself as an AI-authored act as communication "by any path". This change refuses an `act.write` and stores no content (AD-7), and holds act-like content only inside a consult (AC-05). | **Open.** The owner confirms the reading, or directs that refused act content be held as communication. It arises only for act writes, all of which are refused while Tier 2 is not in force. |
| AT-8 | `define-openpractice-boundary` (draft) CF-02 marks a fact billable only when it comes from clinician-authored documentation that is final and signed. An AI-authored diagnosis of record would therefore never be billable. | **Open, deferred with Tier 2.** Nothing in Tier 1 is billable, and CF-06 is unchanged. |
| AT-9 | Ruling 60: "Anything not listed goes to the human doctor." openChart can show the refused attempt to the patient's doctor (AA-12), but the patient's need reaches the doctor only if the AI system routes the patient to the human-doctor path (HealthLinc, openPractice, the inbox). | **Deferred with the practice modes (ruling 67).** It arises only for practice-mode acts. The AI system's change still owns the routing. |
| AT-10 | Ruling 72: the clinical-acts foundation accepts only `clinician` as author type. Tier 2 (AA-02, AA-12) records acts with author type `ai` and an authority basis. | **Open, deferred with Tier 2.** No conflict while Tier 2 is refused. The future governed amendment that would put Tier 2 in force must also amend the foundation to admit `ai` acts, or withdraw Tier 2. This change does not edit the foundation. |
| AT-11 | Two co-review models. This change's AA-07 and AA-08 queue AI acts for co-review with the outcomes confirm, amend and void. openChart-spec#5 CA-07 defines a co-signature requirement on any act version: modes `before_effect` and `after_the_fact`, a co-signer with `cosign` scope, and the outcomes `cosigned`, an amendment or an entered-in-error mark. It names this change's authority grant as the source it intends for ruling 62's co-review. | **Open, deferred with Tier 2.** No conflict while Tier 2 is refused. The Tier 2 amendment converges on openChart-spec#5's CA-07 co-signature model: the grant becomes a CA-07 source, AA-07's confirm and amend map to `cosigned` and a CA-05 amendment, and AA-08's escalation is CA-07's. AA-07's void is CA-06's `entered_in_error`, as the foundation's CT-7 mapping proposes. |
| AT-12 | openChart-spec#5 AU-02 granted authority only per act class. A consult review is not an act, yet Tier 1 needs a grant for it (AG-11). | **Resolved.** As of openChart-spec#5 head `317beda`, AU-02 carries the scope action `review` over record class `ai_consult_record`, which is not an act class and creates no act, recorded only for a `clinician`. AG-11 is that grant and defines no grant model of its own. |
| AT-13 | openChart-spec#5 AU-02: "Nothing SHALL be granted by default, by role name alone, or by the `System Manager` role." AC-11's fail-safe lets a named holder of the `clinician` role authorized for the chart review a quarantined consult without a review grant when nobody in the practice holds one. | **Open, for the owner and openChart-spec#5.** The fail-safe is kept as the default, because a clinician reviewing a quarantined consult is safer than nobody. The owner confirms it, or the foundation provides a default reviewer. |

## Risks / Trade-offs

- **[An AI act rests on authority the chart cannot verify]** → The chart's own grant record (AD-1), checked field by field; refusal on any mismatch.
- **[The AI system keeps acting after a pause]** → A pause in either system applies at once in openChart (AD-6); later writes are refused, and consults that happened after the pause are kept as quarantined AI communication, always reviewed and listed for the responsible clinician (AC-11).
- **[AI text is mistaken for a clinician's]** → An author type on every turn and act, labels on every surface, the patient's included.
- **[An unsafe answer reaches a patient]** → Ruling 57 accepts delivery without sign-off; the review sample, the built-in triggers and the `unsafe` alert are the safety net.
- **[Advice content strays into diagnosis or treatment]** → The source system's own control and declaration, the built-in triggers, the sample and the reviewer's breach finding (AD-31). Whatever the text says, the record is never a fact of record.
- **[Co-review backlog]** → Escalation to the medical director, who can narrow or pause.
- **[Two records of authority drift]** → The configuration version must match exactly; drift refuses writes rather than accepting them.
- **[Tier 1 waits on the inbox]** → AD-3; the alternative is a standalone record capability.
- **[A large consult record]** → Attachments by reference and digest; size limits in the schema.
- **[No constitution]** → Planning is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly. Brett Heap disposes the open tensions (AT-5 to AT-8, AT-10 to AT-13 and the residual reading under AT-1) and AD-2 to AD-40, stamps `Ratified by` and sets `Status: ratified`. `define-clinical-message-inbox` is ratified first or together (AD-3).
2. Adopt openChart's constitution through separate governance.
3. After openChart-spec#5's feature (1), with its clinical roles and authority, has landed, create the single Spec Kit feature from the assembly root, starting with Tier 1: the write-path role, the consult review grant, the quarantine of consults refused at the grant checks, the grant record for `advice_only`, the legal-review record, the review policy, the consult record and its review, and refusal of every `act.write` with `tier2_not_in_force`. Contract tests run against an AI-system double alongside the standalone regression suite.
4. Enable advice-only for a practice only when its gates are recorded (AG-04).
5. Only after `define-clinical-acts-foundation` is ratified and built, and a future governed amendment under ruling 67 puts Tier 2 in force (with, for prescriptions, `define-prescribing-safety-checks` ratified and its gate built, and, for treatment-plan changes, the later treatment-plan change): a governed revision of this change pins the foundation's content schemas in a MINOR contract version, then Tier 2 is built for limited practice, then for full practice (ruling 63).
6. Rollback: the medical director pauses the grant; the write path is disabled; open co-review items stay owned until they close; no record is deleted.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks planning.
2. **Owner dispositions** of the open tensions (AT-5 to AT-8, AT-10 to AT-13 and the residual reading under AT-1) and of AD-2 to AD-40. AD-1 is ruled (ruling 65). These block ratification.
3. **The clinical-acts foundation.** Answered by ruling 72: another author drafted it as openChart-spec#5. Tier 1 needs its feature (1); Tier 2 also needs a future governed amendment (ruling 67).
4. **The responsible clinician.** openChart records no care team today. Which change defines a patient's responsible clinician? Meanwhile, AD-12's fallback to the medical director applies.
5. **The AI system's patient link.** Is it registered through the ratified external-identifier path, or through a governed link contract like PL-02's? Meanwhile, AD-23 applies.
6. **Retention** of consult records, refusal records and integration exceptions. The owner and counsel decide. Meanwhile, nothing is deleted.
7. **Who routes a refused act's patient to the human doctor** (AT-9). The AI system's change decides. Meanwhile, the refusal is shown to the doctor. Deferred with the practice modes.
