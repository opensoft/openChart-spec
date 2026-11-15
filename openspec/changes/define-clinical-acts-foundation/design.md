## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

These facts about what is built were checked at `opensoft/openChart-code` revision `30b9645`. Nothing else is assumed to exist.

- **DocTypes:**
  - `OC Patient` (`patient_name`, `date_of_birth`, `sex_recorded`; named `OC-PAT-#####`);
  - `OC Patient External Identifier`;
  - `OC Intake Submission`;
  - eight statement DocTypes: allergy, condition, document reference, goal, medication, observation, supplement and symptom.

  Every statement row carries `assertion_kind` (set to patient-reported by `open_chart.intake.core`), and a `verification_state` select whose options are `patient_reported` (the default) and `clinician_verified`. No code path sets `clinician_verified` (tension CT-3).
- **API:** `open_chart.api.v1` exposes `submit`, `amend`, `read_submission` and `register_external_identifier`. Every write is gated to `System Manager`. Controllers derived from `GuardedDocument` reject writes made without the API's guard flag (`OC-DIRECT-WRITE`).
- **Roles:** no clinician, nurse or medical-director role exists.
- **Not built:** encounters, notes, diagnoses of record, procedures, orders and prescriptions. There is no practice or tenant record, and no code-set store.

**Related drafts, none on main**, read at these heads:
- `define-ai-authored-clinical-records` (openChart-spec#4, `dbb1fc5`) lists this change as its required prerequisite, with twelve minimum contents (checked below).
- `define-openpractice-boundary` (openChart-spec#2, `e7c3090`) has CF-01 to CF-06 and Open Question 2.
- `define-clinical-message-inbox` (openChart-spec#3, `eda4b08`) has MI-12, MI-14 and Open Question 11.
- In `opensoft/openPractice-spec`, `define-mvp-practice-foundation` (PR #2, `fecc81e`) has `ehr-boundary` EB-13 to EB-20 and owns the schema `openpractice-ehr-clinical-facts-1.0.schema.json`. That schema's SHA-256 is `6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec`, which matches its `contracts/SHA256SUMS` and PL-04.
- `ideation/review/openpractice-framing-decisions.md` FD-11 is read from that repository's `main`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template at revision `d20de75`. There is nothing ratified to check against. This design checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements instead. **Planning for every feature of this change is blocked until a constitution is adopted.**

## Owner rulings

Every row is a ruling by **Brett Heap**. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`. The numbering is shared with the other openChart and openPractice changes.

| # | Date | Ruling | Governs |
|---|---|---|---|
| 31 | 2026-11-14 | openPractice is the system of record for the administrative appointment. The EHR owns the encounter and keeps an appointment reference if needed. The 1.0 contracts carry no appointment operations. (Recorded in `define-openpractice-boundary`.) | EN-02 |
| 34 | 2026-11-14 | openChart is the doctor's clinical interface. openPractice is the administrative gateway and holds no clinical content. | PB-02 (references only), PB-04 |
| 35 | 2026-11-14 | For now the physician uses openChart, on mobile or workstation. | EN-06; no requirement depends on a device |
| 62 | 2026-11-14 | When the AI practice modes are someday enabled, every AI order, prescription or diagnosis gets clinician co-review. | CA-07: the co-signature hook takes a later source without redesign |
| 67 | Not stated in this change's brief | No AI is granted clinical authority now. AI-authored orders, prescriptions and diagnoses stay specified, and off, in `define-ai-authored-clinical-records`. | CA-02, AU-05 |
| 72 | 2026-11-15 | "Draft the openChart clinical-acts foundation change too." | This change |
| 73 | 2026-11-15 | The foundation's scope is encounters, clinical notes, diagnoses, procedures, orders, prescriptions, and authorship, signing and amendment. Left for later changes: results ingestion, care plans and treatment-plan records, immunizations, clinical decision support, and electronic transmission of prescriptions to pharmacies. | The scope; Non-Goals; CT-6, CT-8 |
| 74 | 2026-11-15 | The prescription record is specified in this change, but the prescription feature is not buildable until allergy and interaction checking is specified. A prescription cannot be signed in any deployment where that gate is not met. | RX-02; tasks §2.4 and §3.1; "Required later change" |
| 75 | 2026-11-15 | "Draft the allergy and interaction checking change too." | `define-prescribing-safety-checks`, being drafted |
| 76 | 2026-11-15 | For `define-prescribing-safety-checks`: when the knowledge source is unavailable at signing, a clinician may sign only with a recorded statement that checks were unavailable and that a manual review was done. The prescription is flagged and re-checked when the source returns. A non-clinician author, including any future AI author, can never use that path. | RX-02 (through that change) |
| 77 | 2026-11-15 | For `define-prescribing-safety-checks`: the first checks are allergy, drug–drug interaction and duplicate therapy, plus drug–supplement interaction only where the knowledge source declares support. Later: dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, paediatric and geriatric rules. | "Required later change" |
| 78 | 2026-11-15 | For `define-prescribing-safety-checks`: openChart bundles no drug knowledge. Each practice connects a licensed or verified source through the adapter contract, and no prescription can be signed without one. | RX-02 (through that change); CA-12 (same principle for code sets) |

Rulings 76 to 78 belong to `define-prescribing-safety-checks`. They are listed here because RX-02 defers to that change's signing-time conditions.

## Goals / Non-Goals

**Goals:**

- Give openChart a clinician-authored clinical record whose authorship, signing, amendment, entered-in-error, co-signature and audit rules are the same for every act class.
- Make the record the base that `define-ai-authored-clinical-records` Tier 2 builds on, without redesign: an author type field, an authority-basis reference, an act-type registry with its flags, a co-signature hook and published content schemas.
- Replace the "no billable facts" placeholder of `define-openpractice-boundary` CF-06 with signed, final encounter facts, published by reference with forward-only corrections, without editing that change.
- Honor the ratified rule that intake confers no clinician authority. Clinician records come from patient-reported content only by an explicit, attributed clinician action.
- Fail closed wherever a ruling is silent and the consequence is clinical.

**Non-Goals (ruling 73 and the brief):**

| Out of scope | Pointer |
|---|---|
| Results ingestion | A later governed change (ruling 73). OR-04 refuses completion from external messages. |
| Care plans and treatment-plan records | A later governed change (ruling 73). Tier 2's `treatment_plan_change` stays unsupported (CT-6). |
| Immunizations | A later governed change (ruling 73). |
| Clinical decision support | A later governed change (ruling 73). The narrow prescribing-safety checks are the required change `define-prescribing-safety-checks` (rulings 74 and 75). |
| Electronic transmission of prescriptions and controlled-substance electronic prescribing | A later governed change that needs vendor and regulatory verification (ruling 73; RX-04). |
| Order transmission to external performers | A later governed change (OR-04, CD-19). |
| AI authorship | `define-ai-authored-clinical-records` Tier 2 (ruling 67). |
| Billing, charge capture and coding validation | openPractice (`define-mvp-practice-foundation`; `define-openpractice-boundary` CF-05). openChart validates only that a code exists in a loaded code set (CA-12). |
| Adopting the constitution, or changing any ratified text | Separate governance |

## Decisions

### 1. One act model, one content schema

Six act classes share one envelope (CA-01, CD-1).

| Act class | Content | FHIR R4-compatible resource |
|---|---|---|
| `encounter` | types, period, participants, location, optional appointment reference, reasons | Encounter |
| `clinical_note` | encounter, note kind and type, text, addendum link, attachments by digest | DocumentReference (CD-26) |
| `diagnosis_of_record` | role (`encounter_diagnosis` or `problem_list`), coding, verification and clinical status, rank, dates | Condition |
| `procedure_performed` | encounter, coding, time, performer, quantity, body site | Procedure |
| `order` | category, text, optional coding, priority, reasons, intended performer, release time | ServiceRequest |
| `prescription` | medication, controlled-substance classification, dosage, quantity, refills, release time, transmission status | MedicationRequest |

The envelope holds:
- act identifier and version, class and type, and the openChart patient triple;
- status, author and recording time;
- signatures, amendment links and the co-signature requirement;
- derivation provenance, the restricted mark and lifecycle events.

`contracts/openchart-clinical-act-content-1.0.schema.json` is the canonical representation of one act version. It follows the convention of the sibling contracts: JSON Schema draft 2020-12, a URN `$id`, closed objects and `contracts/SHA256SUMS`. It is pinned by digest. `contracts/examples/` holds 24 synthetic fixtures, 9 that must validate and 15 that must fail, each for one reason stated in `examples/expected-failures.json`. `contracts/selftest.py` checks them (task 1.2).

Each class's content is a named definition (`$defs/encounterContent` and so on), so a MINOR version of `openchart-ai-clinical-record-write` can pin it for `act_content` (CD-28).

### 2. Author type, and the hook for Tier 2

Every act version carries an author type, the author's reference, role and authority basis (CA-02). In 1.x the author type accepts only `clinician`: a named human with an openChart clinical role grant, which covers the `clinician` and `nurse` roles, as MI-12 does (CD-3). Every other value is refused by the schema and at runtime. The authority basis is the role grant and its version.

`define-ai-authored-clinical-records` Tier 2 would add the author type `ai` and an authority basis pointing at its own grant, in a new MINOR version of both contracts and through its own governed change. Nothing in this change's act model needs to change for that.

### 3. Lifecycles

`signed` is an event, not a resting status (CD-4). It moves a draft to `final` (documentation classes), or to `pending_release` or `released` (orders and prescriptions).

| Class | Resting statuses | FHIR status mapping (contract level; to be checked in planning against the FHIR R4 specification) |
|---|---|---|
| `encounter` | `in_progress`, `final`, `amended`, `cancelled`, `entered_in_error` | Encounter.status: `in-progress`; `finished`; `finished`; `cancelled`; `entered-in-error` |
| `clinical_note` | `draft`, `final`, `amended`, `cancelled`, `entered_in_error` | DocumentReference.docStatus: `preliminary`; `final`; `amended`; not exposed; `entered-in-error` |
| `diagnosis_of_record` | as for notes | Condition.verificationStatus from content; `entered-in-error` when entered in error |
| `procedure_performed` | as for notes | Procedure.status: not exposed while draft; `completed`; `completed`; not exposed; `entered-in-error` |
| `order` | `draft`, `pending_release`, `released`, `completed`, `discontinued`, `cancelled`, `entered_in_error` | ServiceRequest.status: `draft`; `on-hold`; `active`; `completed`; `revoked`; `revoked`; `entered-in-error` |
| `prescription` | as for orders | MedicationRequest.status: `draft`; `on-hold`; `active`; `completed`; `stopped`; `cancelled`; `entered-in-error` |

A lifecycle change appends an attributed, dated event. Content changes only by a new version (CA-05).

### 4. Signing and attestation

A signature binds these items (CA-04, CD-9):
- the signer and the signer's role;
- the role grant and its version;
- a coded attestation statement and its version, whose wording the medical director maintains per act class;
- the time;
- the SHA-256 of the RFC 8785 canonical JSON of the content signed.

openChart requires re-authentication at the moment of signing; the mechanism is decided in planning (CD-10). Nobody signs on another person's behalf.

### 5. Amendment, entered in error and drafts

- **Amendment.** A new version references its predecessor, states a reason and carries its own author and signature. Any clinician with sign scope for the class may amend. Every prior version stays readable (CA-05, CD-5).
- **Released orders and prescriptions** are never amended. A change is a discontinuation plus a new act (OR-03, CD-6).
- **Entered in error** is the void. It is marked by the author, a clinician with sign scope, or the medical director, with a coded reason. Content stays for audit (CA-06, CD-7).
- **Drafts** may be revised before signing, with every revision audited. An abandoned draft is `cancelled`, never deleted (CD-8).

### 6. The co-signature hook (ruling 62)

A co-signature requirement attaches to one act version (CA-07, CD-11). It records:
- its source;
- its mode: `before_effect`, where the act is held as `pending_release` (orders and prescriptions only in this change), or `after_the_fact`;
- a due time;
- a co-signer, who is a named clinician other than the author with co-sign scope;
- one outcome: co-signed, amended by the co-signer, or entered in error.

When the due time passes, the requirement escalates to the medical director and keeps alerting. It is never closed by a timer, a default or an agent.

In this change the only source is the author's role grant, for example a supervised clinician or a nurse. This maps onto `define-ai-authored-clinical-records` AA-07 and AA-08 one for one:

| AA-07 / AA-08 | This hook |
|---|---|
| Queue at once, with a due time from the grant's window | Requirement with mode `after_the_fact` and due time = signing time + window |
| Confirm | Outcome `cosigned` |
| Amend: a new, dated, clinician-authored act that visibly supersedes the AI act | Outcome: an amendment by the co-signer (CA-05). A new version may have a different author. |
| Void | Outcome: entered in error (CA-06) |
| Overdue escalates to the medical director, re-alerts, never closed by default | Escalation rule of CA-07 |
| No AI or agent co-reviews | AU-05 |

Tier 2 adds its authority grant as a second `source` value in a MINOR version. An encounter whose signature has an open co-signature requirement is not published until it is co-signed (PB-04).

### 7. Authority

- **Roles.** openChart defines two roles, `clinician` and `nurse`, plus a medical director designation: one per practice, designated by an audited act of an administrative role named in planning (AU-01, CD-12).
- **No medical director, nothing signable.** With no medical director, no grant can be recorded, so nothing can be signed.
- **Grants.** Grants are per person, per act class and per action (`draft`, `sign`, `cosign`, `complete`, `discontinue`), optionally limited to act types. Each grant has an interval, rests on a practice-supplied attestation and may carry a co-signature requirement. Only the medical director records them (AU-02). `System Manager` confers no clinical authority.
- **Attestations.** Licensure and prescriber facts are attestations supplied by the practice, with an expiry. openChart does not verify them and says so (AU-03, CD-13).
- **Prescriptions fail closed.** A prescription-signing grant needs a prescriber attestation in force. Without one it is refused, and an expired attestation stops the grant at once.
- **Checks at the moment of action.** Every action is checked against the grant in force at that moment. Reductions apply at once (AU-04).

### 8. Act-type registry

The registry lists, per class, the act types a practice uses (CA-09, CD-14). Each type has a code, a display name, an interval, a version and two explicit flags, `reserved` and `emergency_management`. The medical director maintains it. The flags do nothing for clinician acts in this change. They are the data that `define-ai-authored-clinical-records` AA-04 to AA-06 read.

### 9. Patient-reported content stays patient-reported

A clinician may create a draft act from an intake statement only by an explicit action, recorded as derivation provenance (`derived_from`: kind, reference, version, who and when) (CA-11, CD-22). The same applies to a clinical communication record under MI-12, once `define-clinical-message-inbox` lands.

Nothing is created automatically. The source statement is never changed, keeps `assertion_kind` patient-reported, and its `verification_state` is never set by this change. The clinician's record is a separate, signed act. This is how the ratified "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order…" is honored: an act is created only by a named clinician's authenticated, signed command through the versioned boundary, and never by intake, a statement, an API response or an extension event (CA-10; tension CT-1).

### 10. Encounters and notes

- **The encounter.** It is opened `in_progress` with one primary performer (EN-01).
- **The appointment.** openPractice owns the appointment (ruling 31). The encounter may hold an opaque appointment reference, and nothing more (EN-02, CD-17). The 1.0 contracts carry no appointment events, so the reference is entered by an authorized user or left absent until a later MINOR version of the link contract adds events. A walk-in has none (openPractice EB-19).
- **Signing the encounter.** It needs all of these: the signer is a participant with encounter sign scope, at least one final note, no attached drafts, and an end time (EN-04, CD-15). The encounter signature is the documentation-final signature.
- **After finalization.** Every change to attached acts goes through a signed encounter amendment, which publication treats as a forward-only correction (EN-05, CD-16).
- **Notes and replies.** Notes are signed by their author, and addenda are separate notes. Clinician replies to patients stay MI-12 communications (EN-03).

### 11. Diagnoses and procedures

- **Diagnoses.** A diagnosis of record is either an encounter diagnosis (with an encounter and an optional rank) or a problem-list condition (with a clinical status). It is always coded and carries a verification status. An uncoded diagnosis cannot be signed (DX-01, CD-25).
- **Kept apart from reports.** Diagnoses stay distinct from patient-reported conditions in storage, display and reads (DX-02).
- **Procedures.** Procedures are coded, attached to an encounter and performed by a participant (DX-03).

### 12. Publication to openPractice: how CF-06's placeholder is replaced

CF-06 reads: "Until a separately governed openChart capability records clinician-authored encounters, diagnoses and procedures, openChart SHALL report `billable_facts_supported: false`…" This change is that capability (PB-01). It replaces the placeholder by meeting CF-06's own condition, not by editing `define-openpractice-boundary`:

1. In a deployment where features (1) and (2) are enabled and the boundary change's publication surface is built, `capability.result` reports `true` (CD-24).
2. In every other deployment CF-06 still governs: the result is `false` and reads return `no_billable_facts`.
3. Disabling feature (2) returns the result to `false` at once.

What is published, field by field, against the canonical schema at `6b2071fe…` (PB-02):

| Contract field | Source in this change |
|---|---|
| `encounter.documentation_final` notification | The encounter becomes `final` for a patient with an `active` `openpractice` link. Resource references only, sent through PL-14's durable store. |
| `encounter.id`, `version` | Encounter act identifier and act version |
| `encounter.status` | `in_progress` → `in-progress`, `final`/`amended` → `finished`, `cancelled` → `cancelled`, `entered_in_error` → `entered-in-error` |
| `encounter.type`, `period`, `location_ref`, `participants` | Encounter content. Codings as system and code; practitioner references opaque. |
| `conditions[]` | Each `final`/`amended` `encounter_diagnosis` on the encounter: category `encounter-diagnosis`, coding (system, code), rank, encounter reference |
| `procedures[]` | Each `final`/`amended` procedure: coding, quantity, `performed`, `performer_ref`, encounter reference |
| `documentation_final` | `final: true`, `signer_ref` and `signed_at` from the encounter version's author signature |
| `clinical_fact.corrected` | An encounter amendment: new versions in `resource_refs`, replaced versions in `supersedes` (PB-03) |
| `clinical_fact.entered_in_error` | A published diagnosis, procedure or encounter marked entered in error (PB-03) |

What is never published (PB-04):
- patient-reported statements and communications;
- the problem list, which the contract has no category for;
- notes, orders and prescriptions;
- drafts;
- restricted acts;
- encounters awaiting co-signature;
- anything the schema cannot represent. In that case nothing is published for the encounter, and an integration exception is recorded.

A read of a non-final encounter returns `no_billable_facts` (CD-24). Codings drop the version and display, because CF-01 and FD-11 allow a system and a code only (tension CT-11).

openChart still works with no openPractice, and a delivery failure never blocks a clinical act (PB-05).

### 13. Orders

There is one generic record, with five categories (OR-01, CD-18):
- `laboratory`, `imaging`, `referral` and `other`, from the brief;
- `procedure`, from `define-ai-authored-clinical-records`' minimum list.

Release follows signing unless a `before_effect` co-signature or a future release time holds the order in `pending_release` (OR-02). `released` means in force inside openChart. openChart transmits nothing and ingests no result; completion is a named person's explicit act (OR-04, CD-19).

### 14. Prescriptions and the prescribing-safety gate (ruling 74)

The prescription records the prescribing decision (RX-01).

**Gate.** RX-02 makes ruling 74 binding. No prescription, and no new version of one, is signed in a deployment where the prescribing-safety gate is not met. The gate is met only when three conditions hold:
1. `define-prescribing-safety-checks` is ratified;
2. its capability is built and enabled in that deployment;
3. the signing meets that change's signing-time conditions. Under rulings 76 to 78 these are a connected, licensed or verified knowledge source and a completed check, or the clinician-only outage path with a recorded statement.

Ruling 74 says "specified". This design reads that as ratified, and it adds the runtime conditions so that a deployment cannot sign in the gap between ratification and a working check (CD-30). Feature (4) is not buildable before that change is ratified (tasks §2.4).

**Controlled-substance classification.** The classification is required. `unknown` counts as `controlled`. Signing a prescription classified `controlled` or `unknown` is refused until the owner decides through a governed change (RX-03, CD-20). No rule about controlled substances is asserted.

**No transmission.** There is no transmission, no controlled-substance electronic prescribing, no pharmacy-facing document and no dispense record, and the transmission status is fixed at `none_recorded` (RX-04, CD-21).

### 15. Coding and licensed intellectual property

A coding stores the system, the code, the code-system version (where the practice's code set declares one), the display and the reference of the practice-supplied code-set import (CA-12, CD-23). openChart bundles no code set and asserts no license status for any code system. Bundling anything needs license verification and a governed change. This is consistent with openPractice FD-11's "never licensed content in the repo". openChart goes further than FD-11 in one respect: it does not adopt FD-11's list of license-free sets, because FD-11 governs openPractice (tension CT-12). Synthetic fixtures use synthetic code systems only.

### 16. FHIR R4-compatible mapping (contract level, no conformance claim)

| Act | Resource | Key mappings |
|---|---|---|
| Encounter | Encounter | status (§3); type; period; participant.individual = practitioner reference, participant.type from participation; location; appointment reference only as an identifier |
| Clinical note | DocumentReference (CD-26; Composition is the alternative) | docStatus (§3); type from note type; context.encounter; content as attachment with hash; relatesTo for addenda (`appends`) and amendments (`replaces`) |
| Diagnosis of record | Condition | category `encounter-diagnosis` or `problem-list-item`; code; clinicalStatus; verificationStatus; encounter; onset/abatement dates |
| Procedure performed | Procedure | status (§3); code; performed; performer; encounter; bodySite |
| Order | ServiceRequest | status (§3); intent `order`; category from order category; code; priority; reasonReference; encounter; performer |
| Prescription | MedicationRequest | status (§3); intent `order`; medication; dosageInstruction text; dispenseRequest quantity and refills; substitution; reasonReference |
| Authorship, signatures, co-signatures, derivation | Provenance | agent (author, verifier for co-signer); signature with the content digest; entity `source` for `derived_from` |

Drafts, cancelled acts and restricted acts are never exposed (CA-13). openChart claims no FHIR certification and no profile or implementation-guide conformance.

### 17. Standalone operation, logs and restricted acts

- **Standalone.** Every capability works with no external system, except prescription signing, which needs the gate (CA-14). The golden-intake tests stay the regression gate.
- **Logs.** Logs and coded reasons carry identifiers only.
- **Restricted acts.** Sensitive categories and minors' records are an open question for counsel (Open Question 3). Meanwhile, a clinician may mark an act `restricted`. A restricted act, and any encounter carrying one, never leaves the chart (CA-15, CD-27). No legal rule is asserted.

### 18. Handoff shape

The brief asks for four ordered features, each gated on ratification. The shared workflow protocol's default is exactly one Spec Kit feature per OpenSpec change. Ruling 1 approved an ordered multi-feature exception for openPractice only. This change therefore asks the owner for the same exception, for openChart (CD-31, tension CT-14).

## Minimum contents required by `define-ai-authored-clinical-records`

That change's design, section "Required prerequisite change: the clinical-acts foundation", lists twelve items.

| # | Item | Where this change meets it | Met |
|---|---|---|---|
| 1 | Clinician encounters, with participants, period and status | EN-01, EN-04, CA-03 | Yes |
| 2 | Orders (laboratory, imaging, referral, procedure) with a lifecycle that distinguishes draft, signed, pending release, released or executed, completed, discontinued or countermanded, and voided | OR-01, OR-02, CA-03, CD-18. `signed` is the signing event and the signature (§3); voided is `entered_in_error`; countermanded is `discontinued`; released or executed is `released` | Yes, with a terminology mapping (CT-7) |
| 3 | Prescriptions with the same lifecycle plus dispense or transmission states, and a classification that marks controlled substances | RX-01, RX-03, RX-04. The lifecycle and classification are provided. Dispense and transmission states are reserved: `transmission_status` is `none_recorded` in 1.x (ruling 73) | Partly (CT-8) |
| 4 | Diagnoses of record (problem list and encounter diagnoses), with verification status, distinct from patient-reported conditions | DX-01, DX-02 | Yes |
| 5 | Treatment plans, versioned, each change a new dated record | Not provided: ruling 73 leaves care plans and treatment-plan records for a later change. The versioning rule a later change would inherit is CA-05. Tier 2's `treatment_plan_change` is refused with `act_type_unsupported` under its own AA-01 | No (CT-6) |
| 6 | Authorship on every act: author kind (`clinician` or `ai`) and an authority-basis reference that Tier 2 fills, plus clinician signing or attestation | CA-02 (author type, `clinician` only; Tier 2 adds `ai`), `authority_basis_ref`, CA-04 | Yes (CT-10 on the field's name) |
| 7 | An act-type registry with reserved and emergency-management flags | CA-09 | Yes |
| 8 | Roles: clinician, nurse and medical director, with scope per act class | AU-01, AU-02 | Yes (CT-9 on the overlap with AG-02) |
| 9 | Amendment, void and countermand as new dated records; nothing edited in place or deleted | CA-05, CA-06, OR-02 (discontinuation as a signed lifecycle record), OR-03 | Yes |
| 10 | Content schemas per act class, published so that a MINOR version of `openchart-ai-clinical-record-write` can pin them | `openchart-clinical-act-content/1.0`, `$defs/<class>Content`, SHA-256 in `contracts/SHA256SUMS` (CA-01, CD-28) | Yes |
| 11 | Reconciliation with the ratified intake text that AT-1 records | CA-10, CA-11, §9; tensions CT-1 and CT-2 | Yes, pending the owner's disposition of CT-1 |
| 12 | Billing interplay with CF-02 and CF-06 | PB-01 to PB-05, §12. AI-authored acts are not published, because only `clinician` authors exist in 1.x and CF-02 requires clinician-authored documentation | Yes |

## Required later change: prescribing-safety checks

**`define-prescribing-safety-checks`.** It is required before any prescription can be signed (ruling 74), and is being drafted under ruling 75. Feature (4) of this change depends on its ratification. RX-02 refuses every prescription signature until its gate is met. Its minimum contents:

1. **Clinician-confirmed lists.** A clinician-confirmed allergy and intolerance list and an active medication list. Each reuses this change's act model (author type, signing, amendment, entered in error, provenance) through new act classes in a MINOR version of `openchart-clinical-act-content`. It defines no second signing model.
2. **Reconciliation from intake.** The lists are reconciled from patient-reported medication, supplement and allergy statements only by an explicit, attributed clinician action (CA-11). Nothing is promoted automatically.
3. **Inputs.** A check reads both clinician-confirmed entries and patient-reported statements. A patient-reported entry is shown as patient-reported and is never ignored because it is unconfirmed. An uncoded or free-text entry that cannot be checked produces an explicit "could not be checked" warning and is never skipped silently.
4. **The checks (ruling 77):**
   - allergy (ingredient and class);
   - drug–drug interaction;
   - duplicate therapy;
   - drug–supplement interaction, only where the source declares support.

   Later changes will add dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, and paediatric and geriatric rules.
5. **Behaviour.**
   - Checks run when a prescription is drafted or changed, and again at signing.
   - Each alert has a severity.
   - An override needs a recorded reason, and the most severe class needs an explicit override for each alert, never in bulk.
   - Each check records its inputs, the source and its version, the alerts raised and the clinician's response.
   - Alerts are labelled as advice, and the record shows the clinician as responsible.
6. **The knowledge source (ruling 78).**
   - openChart bundles no drug knowledge.
   - A versioned adapter contract, with a canonical schema and SHA256SUMS, covers normalization to ingredients, allergy cross-reference, interaction lookup, a capability declaration and source identity with version and effective date.
   - Nothing is asserted about any vendor, product, database or license; each must be verified before use.
   - Fixtures are synthetic.
7. **Gates, failing closed.**
   - No prescription is signed without a connected, verified and current source (ruling 78). A source older than a policy-set age counts as unavailable.
   - The outage path is for a clinician only: a recorded statement, a flag, and a re-check when the source returns. A non-clinician author, including any future AI author, never uses it (ruling 76).
   - Go-live needs a recorded legal and regulatory review, which states what it covers and asserts no rule.
8. **The interface RX-02 calls.** One gate decision per signing attempt, with a coded reason, that this change's signing path can rely on.
9. **Boundaries.**
   - Everything except prescription signing works with no source.
   - No clinical content goes to openPractice.
   - A FHIR R4-compatible mapping at contract level (AllergyIntolerance, MedicationStatement or MedicationRequest, DetectedIssue), with no conformance claim.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which "MUST operate without MedxFactory, MedxEHR or openPractice" | CA-14 and PB-05. Every component works with no external system. Only prescription signing needs the safety gate, which is part of openChart. |
| External identifiers must not replace the openChart identifier or merge patients | CA-01. Every act names the openChart triple; the schema refuses any other namespace. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Acts never alter submissions. |
| Statements preserve reported detail | Untouched. Derivation reads a statement and never changes it (CA-11). |
| Amendments preserve accepted history | CA-05, CA-06, CA-08. Nothing is overwritten or deleted. |
| APIs and hooks are authorized and versioned | CA-10. One versioned, authorized boundary; direct writes refused; extensions read only. |
| Intake does not confer clinician or autonomous authority | CA-10, CA-11, DX-02, PB-04. **Tensions CT-1, CT-2 and CT-3.** |

Four possible conflicts with ratified or published openChart text are recorded: CT-1 to CT-3 against the ratified requirement, and CT-4 against the published p4 declaration. No other conflict with ratified text was found.

## Consistency with the draft changes

| Draft requirement | Relation |
|---|---|
| `define-openpractice-boundary` CF-01, CF-03, CF-04 | Followed: PB-02 publishes exactly CF-01's fields, by reference and minimum necessary; PB-03 is CF-04's forward-only correction. |
| CF-02 | Followed: only final, clinician-signed encounter facts (PB-04). |
| CF-05 | Followed: this change creates no billing data. |
| CF-06 and Open Question 2 | This change is the capability named; CF-06 stops requiring `false` only where this change is enabled (PB-01). **CT-13.** |
| PL-01, PL-03 | Followed: the patient triple. |
| PL-13, PL-14, PL-15 | Reused for logs, delivery and standalone operation (CA-14, PB-02, PB-05). |
| `define-clinical-message-inbox` MI-12, MI-14 | This change is the "separately governed clinical workflow" those requirements defer to. Replies stay communications (EN-03), and a communication becomes a source only by explicit derivation (CA-11). |
| MI-07, task 3.2 (roles) | AU-01 gives the roles and the medical director. **CT-9.** |
| MI Open Question 11 (billability of replies) | Proposed answer (CD-29): a communication is never billable. A clinician who judges an exchange to be a documented service records an encounter, with a note that may derive from the communication. |
| `define-ai-authored-clinical-records` (12 minimum contents) | Table above. **CT-6 to CT-10.** |
| AA-01 | Unchanged: `tier2_not_in_force` stays until Tier 2 is built over this foundation; unsupported classes are refused with `act_type_unsupported`. |
| AA-07, AA-08, AA-09, AA-11 | The hook (§6) and lifecycles (§3) carry them; "pending" for AA-11 is `pending_release`. |
| openPractice EB-13 to EB-16, EB-19 | Followed: final signed documentation, diagnoses and procedures, forward-only corrections, references only, and an appointment reference only. |

## Design calls for owner review

Each item goes beyond the rulings and is proposed, not ruled. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| CD-1 | One envelope for six act classes; the storage shape is decided in planning. | CA-01 |
| CD-2 | The author type accepts only `clinician`. Any other value, `ai` included, is refused. Only a later governed change may add a value, in a new MINOR version. | CA-02 |
| CD-3 | The `clinician` author type covers anyone with an openChart clinical role grant, `clinician` or `nurse`, matching MI-12's definition. | CA-02 |
| CD-4 | The status lists and transitions of CA-03. `signed` is an event, not a resting status. | CA-03 |
| CD-5 | Any clinician with sign scope for the class may amend. Each version has its own author and signature. | CA-05 |
| CD-6 | Orders and prescriptions are amended only while `pending_release`. After release, a change is a discontinuation plus a new act. | OR-03 |
| CD-7 | Entered in error may be marked by the author, a clinician with sign scope, or the medical director, with a coded reason. It is the void of AA-09. | CA-06 |
| CD-8 | Draft revisions are audited, and abandoned drafts are cancelled, never deleted. | CA-05 |
| CD-9 | Attestation statements are coded and versioned per act class, with wording maintained by the medical director. A signature binds the RFC 8785 content digest. | CA-04 |
| CD-10 | Re-authentication at every signature. **Proposed fail-closed default**: required; planning chooses the mechanism. | CA-04, EN-06 |
| CD-11 | The co-signature hook: `before_effect` only for orders and prescriptions; `after_the_fact` for all classes; escalation to the medical director; never closed by default. An encounter awaiting co-signature is not published. | CA-07, PB-04 |
| CD-12 | Roles `clinician` and `nurse`, plus a medical director designation. Designation is by an administrative role named in planning. Grants are recorded by the medical director only. With no medical director, nothing is signable. `System Manager` confers nothing. | AU-01, AU-02 |
| CD-13 | Licensure and prescriber facts are practice-supplied attestations that openChart does not verify. **Fail-closed default for prescriptions**: a prescription-signing grant needs a prescriber attestation in force, and expiry stops it at once. | AU-03 |
| CD-14 | The registry is maintained by the medical director. Both flags must be set explicitly. They have no effect on clinician acts. | CA-09 |
| CD-15 | Encounter finalization needs a signer who is a participant, at least one final note, no attached drafts, and an end time. | EN-04 |
| CD-16 | After finalization, every change to attached acts goes through a signed encounter amendment. | EN-05 |
| CD-17 | The appointment reference is optional and opaque, entered by an authorized user or absent, until a MINOR version of the link contract adds appointment events. Its absence never blocks anything. | EN-02 |
| CD-18 | The order categories add `procedure` (from the AI change's minimum list) to the brief's laboratory, imaging, referral and other. | OR-01 |
| CD-19 | No order transmission and no results ingestion. Completion is a named person's explicit act. | OR-04 |
| CD-20 | **Fail-closed default**: signing a prescription classified `controlled` or `unknown` is refused until the owner decides through a governed change. `unknown` counts as controlled. | RX-03 |
| CD-21 | No pharmacy-facing document or message. `transmission_status` is fixed at `none_recorded`. | RX-04 |
| CD-22 | Derivation from intake statements and clinical communications only by explicit action, with provenance. The statement is never changed, and its `verification_state` is never set. | CA-11 |
| CD-23 | A coding carries `code_set_ref` to the practice's import. A code must be in a loaded code set in force. | CA-12 |
| CD-24 | The capability is `true` only where features (1) and (2) are enabled and the boundary surface is built. A non-final encounter read returns `no_billable_facts`. An entered-in-error encounter read returns status `entered-in-error` with no facts. | PB-01, PB-02, PB-03 |
| CD-25 | An uncoded diagnosis or procedure cannot be signed. Uncoded reasoning goes in a note. | DX-01, DX-03 |
| CD-26 | Notes map to DocumentReference (the alternative is Composition). `pending_release` maps to `on-hold`. Drafts are never exposed. | CA-13 |
| CD-27 | **Fail-closed default pending counsel** on sensitive categories and minors' records: a clinician may mark an act `restricted`, and a restricted act, or an encounter carrying one, never leaves the chart. No legal rule is asserted. | CA-15, PB-04 |
| CD-28 | The content schema is published now, with each class's content addressable for a MINOR version of `openchart-ai-clinical-record-write`. | CA-01 |
| CD-29 | Answers inbox Open Question 11: a communication is never billable. A clinician who judges an exchange to be a documented service records an encounter whose note may derive from it. | EN-03, CA-11 |
| CD-30 | Reading of ruling 74: "specified" means ratified. The gate also needs the capability built and enabled in the deployment, and the signing-time conditions of `define-prescribing-safety-checks` (rulings 76 to 78). | RX-02 |
| CD-31 | An ordered four-feature handoff, as an exception to the protocol's one-feature default. Ruling 1 gave openPractice the same exception; this change asks for it for openChart. | tasks §3 |
| CD-32 | Every read by an integration identity is audited. How reads by chart users are audited is decided in planning. | CA-08 |

## Conflicts and tensions

Fourteen are recorded. Each needs the owner's disposition before ratification. None is resolved by this draft on its own authority. **This change does not claim to be free of conflicts.**

| # | Tension | Status |
|---|---|---|
| CT-1 | **Ratified text.** `expanded-patient-intake`, "Intake does not confer clinician or autonomous authority": "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action." Clinician acts are created through openChart's versioned API. This is the same sentence as `define-ai-authored-clinical-records` AT-1, which that change routes to this foundation (its minimum item 11). | Reading proposed: the sentence sits in a requirement about intake and governs intake-derived artefacts. A clinician's authenticated, signed command creates the act, and no intake, statement, API response or extension event does (CA-10, CA-11). If the owner reads the sentence as governing every openChart API, this change needs a MODIFIED delta to that requirement before ratification. |
| CT-2 | **Ratified text.** The same requirement: "Patient statements SHALL remain visibly patient-reported until an authorized clinical workflow records another assertion." "Until" could be read as letting a statement stop being patient-reported. | Reading proposed: this change is that authorized workflow. It records a separate, signed assertion, and the statement stays patient-reported for good (CA-11, DX-02). This is stricter than the text, not a conflict. Owner confirms. |
| CT-3 | **Ratified text and built code.** The ratified requirements give statements a "verification state". The built field `verification_state` offers `clinician_verified`, which could be read as a clinician assertion made on a patient statement. | This change never sets it (CA-11, CD-22). Owner decides whether `clinician_verified` is retired, defined by a governed change, or left unused. Meanwhile, a statement marked `clinician_verified` by any path is still patient-reported and never a diagnosis. |
| CT-4 | **Published openChart contract.** `contracts/p4-compatibility-declaration.yaml` guarantees "every statement assertion_kind=patient_reported; no prescription, diagnosis, order, administration, or autonomous action is ever emitted". This change's reads and publication emit clinician-authored diagnoses, procedures and, in the chart, orders and prescriptions. | The guarantee is scoped to component p4, the intake API, and stays true for it. This change must publish its own compatibility declaration (task 5.1), and consumers must not read p4's as covering acts. Owner confirms. Same reading as AT-4 of `define-ai-authored-clinical-records`. |
| CT-5 | openChart `AGENTS.md`: "Do not enable autonomous clinical actions by default." Some steps happen automatically: publication notifications, co-signature escalation, and an order's release at the time its signer chose. | Not a conflict by its letter. Each step carries out a named clinician's signed decision, or alerts a human, and decides nothing clinical. Recorded for the owner's confirmation. |
| CT-6 | `define-ai-authored-clinical-records` minimum item 5 (treatment plans) is not provided, because ruling 73 leaves treatment-plan records for later. | That change's own AA-01 refuses an unsupported act class with `act_type_unsupported`, so Tier 2's `treatment_plan_change` stays refused. That change should name the later treatment-plan change as a prerequisite for that act class. |
| CT-7 | That change's item 2 names the order states "signed, … released or executed, … discontinued or countermanded, and voided". This change uses `pending_release`/`released`, `discontinued` and `entered_in_error`, with `signed` as an event. Its AA-11 scenario says "released for transmission", but this change has no transmission. | Mapping proposed in the minimum-contents table. "Pending" for AA-11 means `pending_release`. That change should adopt these status names in its MINOR version. |
| CT-8 | That change's item 3 asks for dispense or transmission states. Ruling 73 leaves pharmacy transmission for later. | `transmission_status` is reserved, fixed at `none_recorded` in 1.x (RX-04). Dispense and transmission values wait for the later e-prescribing change. |
| CT-9 | `define-ai-authored-clinical-records` AG-02 records the practice's medical director itself. `define-clinical-message-inbox` leaves the clinician, nurse and medical-director roles to planning (its task 3.2). This change defines both (AU-01). | Proposed: this change holds the single definition, and both drafts cite it. AG-02's rule "with no medical director recorded, no grant can be approved" agrees with AU-01. Owner confirms. Those drafts would need amending. |
| CT-10 | Field name. That change calls the field "author kind" (AA-02). MI-12 and this change call it "author type". | Proposed: one field, `author_type`. AA-02 reads it as its author kind. |
| CT-11 | `openpractice-ehr-clinical-facts/1.0` (digest `6b2071fe…`) carries a coding as system and code only, with a code of at most 32 characters. openPractice cannot tell which code-system version a code came from, and this change stores codes of up to 64 characters. | This change publishes system and code only (PB-02). A code that does not fit blocks publication of its encounter, with an integration exception (PB-04). Carrying the version needs a MINOR version of the openPractice contract, owned by `define-mvp-practice-foundation`. Owner item. |
| CT-12 | openPractice FD-11 lets the open-source core ship ICD-10, HCPCS Level II and other sets it calls license-free. openChart bundles no code set and asserts no license status (CA-12). The two systems may therefore load different code-set versions. | Not a conflict: FD-11 governs openPractice, and openChart is stricter. Combined with CT-11, a version mismatch between the two systems is not detectable under 1.0. Owner item. |
| CT-13 | `define-openpractice-boundary`'s design says "No clinician-authored encounters, diagnoses or procedures exist" and "Every statement in openChart is patient-reported". CF-06 holds `false` "until" a capability exists. | Not a conflict with its requirement text: PB-01 meets CF-06's condition without editing it. Those design statements become stale once this change lands, and its Open Question 2 is answered by this change. |
| CT-14 | The shared workflow protocol hands an OpenSpec change to exactly one Spec Kit feature. This change hands off to four ordered features (the brief; ruling 74 orders feature (4) last). | CD-31 asks for the exception that ruling 1 gave openPractice. If refused, the four features become four successive revisions of one feature, in the same order and with the same gates. |

## Risks / Trade-offs

- **[A wrong-patient or wrong-content signature]** → Re-authentication at signing; a content digest bound to the signature; entered-in-error handling; nothing deleted.
- **[Patient-reported content mistaken for a clinician's]** → Separate records, explicit derivation, the statement never changed, and labels on every surface.
- **[Prescribing without safety checks]** → RX-02 refuses every signature until `define-prescribing-safety-checks` is ratified, built and satisfied (ruling 74). Controlled and unknown classifications are refused (CD-20).
- **[Over-privileged users]** → Grants per class and action, recorded by the medical director. `System Manager` confers nothing. Reductions apply at once.
- **[Billing from unfinished documentation]** → Only final, clinician-signed encounter facts are published, after any co-signature, by reference, with forward-only corrections.
- **[Code-set licensing]** → Nothing bundled; practice-supplied sets; verification before any bundling.
- **[Co-signature backlog]** → Escalation to the medical director, who can narrow grants.
- **[A large first build]** → Four ordered features, each gated.
- **[No constitution]** → Planning is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly, check the schema digest and run the self-test. Brett Heap disposes CT-1 to CT-14 and CD-1 to CD-32, stamps `Ratified by` and sets `Status: ratified`.
2. Adopt openChart's constitution through separate governance.
3. Feature (1): acts, signing, authority, encounters and notes, contract tests against the content schema, and the standalone regression suite.
4. Feature (2): diagnoses, procedures and publication, against an openPractice double at the PL-04 digest. Live publication waits for `define-openpractice-boundary` to be ratified and built.
5. Feature (3): orders.
6. Feature (4): prescriptions, only after `define-prescribing-safety-checks` is ratified (ruling 74). The signing path calls that change's gate decision.
7. Land the leg pull requests and the root pin bump for each feature. Archive after the last.
8. Rollback: disable a feature's capability. Signed acts stay readable; nothing is deleted. Disabling feature (2) returns the capability result to `false`.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks planning for every feature.
2. **Owner dispositions** of CT-1 to CT-14 and CD-1 to CD-32. These block ratification.
3. **Sensitive record categories and minors' records.** Do some categories, or records of minors, need segmentation, special consent handling or restricted disclosure, and under which rules? This is a question for counsel; this change asserts no legal rule. Meanwhile, CD-27's restricted mark applies, and nothing marked restricted leaves the chart.
4. **Retention** of acts, versions, drafts, audit trails and grants. The owner and counsel decide. Meanwhile, nothing is deleted.
5. **The administrative role that designates the medical director**, and how a practice (tenant) is represented. Planning decides, within AU-01.
6. **Appointment references.** When a MINOR version of the link contract adds appointment events, how is the reference filled? `define-openpractice-boundary` and openPractice decide. Meanwhile, CD-17 applies.
7. **Controlled-substance prescriptions.** When, and under which governed change, may a prescription classified `controlled` be signed? The owner decides. Meanwhile, CD-20 refuses it.
