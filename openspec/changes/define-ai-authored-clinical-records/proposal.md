code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: a versioned write path, `openchart-ai-clinical-record-write/1.0`, owned by this change, for records from an external clinical AI system operating under a declared authority; openChart's own record of the medical director's authority grant, with the recorded legal and regulatory review for each mode, checked on every write; Tier 1, the AI consult record (buildable now, for advice-only mode), with model, evidence and mode provenance, visibility to the patient's doctor, the medical director's review sample and always-review categories; Tier 2, the authorship, authority, co-review and reversal layer for AI-authored clinical acts (orders, prescriptions, diagnoses of record, treatment-plan changes) under limited practice and full practice, specified now and not buildable until the clinical-acts foundation is ratified; receipts for every write; scenario isolation; and patient-facing labels of AI authorship. Out of scope: building clinician encounters, orders, prescriptions or diagnoses (the required prerequisite change `define-clinical-acts-foundation`); the AI system's internals, models or vendors; billing (CF-05 and CF-06 unchanged); and any change to the ratified `expanded-patient-intake` requirements.
target_release: AI write path v1. Tier 1 archives when a landed, validator-green open_chart revision passes contract tests for `consult.write`, `authority.notice`, `write.receipt` and `consult.reviewed` against an AI-system double at the recorded schema digest, still passes the standalone golden-intake round trip with no AI system configured, and refuses every `act.write` with `tier2_not_in_force`. Tier 2 is realized by a later governed revision after the clinical-acts foundation is ratified, and this change archives only when both tiers have landed or Tier 2 is explicitly split out.
Status: draft
Ratified by: pending. The decisions encoded here rest on rulings Brett Heap made on 2026-11-14 (rulings 35, 51, 53 and 56 to 64; ruling 64: "draft the openChart and MedxEHR AI write path changes too"). They are recorded in `design.md` under "Owner rulings (2026-11-14)". Rulings are not ratification. The design calls in `design.md`, including proposed decision 65, are proposed, not ruled. Ratification requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

The practice's medical director will set an external clinical AI system to one of three modes: advice only (the default), limited practice, or full practice (ruling 59). Its exchanges with patients are recorded in the chart through that system's own governed path, never through openPractice (ruling 53). Every consult must be in the chart for the patient's doctor (ruling 57). And each mode stays off until the medical director has approved its scope, a legal and regulatory review covering that mode is on record, and, for the two practice modes, the chart can accept an AI-authored order, prescription or diagnosis recorded with the authority it acted under (rulings 58 to 62).

That last condition is this change. openChart is the doctor's clinical interface, on mobile or workstation (ruling 35). Its built code holds patient intake only: `OC Patient`, `OC Patient External Identifier`, `OC Intake Submission` and eight patient-reported statement families. There are no clinician encounters, orders, prescriptions or diagnoses in openChart yet, and nothing records AI-authored content.

Two draft openChart changes need this one. `define-clinical-message-inbox` (not yet on main) holds every AI-authored order, prescription or diagnosis as communication until "a later openChart change for practice modes" is ratified (its MI-26), and leaves openChart's receiving side of the AI system's governed chart path to a separate change (its Open Question 4). `define-openpractice-boundary` (not yet on main) waits for a clinical-encounter capability (its Open Question 2).

This change is neutral. It speaks of "an external clinical AI system operating under a declared authority". openChart must still operate with no such system present. The Medx-specific binding is a separate private companion.

## What Changes

- **A versioned write path.** openChart accepts AI-authored records only through `openchart-ai-clinical-record-write/1.0`, a canonical JSON schema owned by this change and pinned by SHA-256 in `contracts/SHA256SUMS`. Writes are idempotent, every write gets a receipt, the writing system can read back what the chart stored by digest, and no PHI appears in errors, logs or notifications (AW-01 to AW-12).
- **openChart's own record of authority (proposed decision 65).** The chart keeps its own record of the medical director's authority grant: practice, mode, configuration version, allowlist entries or the full-practice grant, the approving medical director, the recorded legal and regulatory review for that mode, expiry, review policy and co-review window. It checks every write against that record and never trusts the AI system's claim. It fails closed on anything missing, expired, paused, narrowed or mismatched. Only the medical director, a named human, approves, narrows, pauses or resumes. A reduction of authority from any source applies at once; a widening is only ever the medical director's act in openChart (AG-01 to AG-10).
- **Tier 1: AI consult records (buildable now).** The chart records each consult as the full exchange with an optional, labelled AI summary (design call AD-2). The record carries the model and version identifiers, the evidence references, the mode in force and the authority. AI authorship is always distinguishable from clinician-authored and patient-reported content. A consult record is AI-generated communication: never a diagnosis and never a clinical fact of record. It is visible to the patient's doctor, and it supports the medical director's review sample and always-review categories, with review status, reviewer and outcome. It reuses `define-clinical-message-inbox`'s clinical-communication record and defines no second one (AC-01 to AC-10).
- **Tier 2: AI-authored clinical acts (specified, not buildable yet).** For orders, prescriptions, diagnoses of record and treatment-plan changes under limited or full practice, this change specifies the authorship, authority, co-review and reversal layer that applies to any act type. An act is accepted only under a current grant. The reserved list is refused whatever mode is claimed, unless the grant's recorded legal review cleared that act. Emergency management by an AI is always refused. Every accepted act enters a clinician co-review queue with a window the medical director sets; the clinician confirms, amends or voids it, and an overdue item escalates to the medical director. A clinician can void or countermand an AI act. An AI act never overwrites or supersedes clinician-authored content. On narrowing or pause, pending AI acts are held and handed to a clinician, or cancelled, and never executed (AA-01 to AA-12).
- **Tier 2 is blocked.** Tier 2 is not buildable until the required prerequisite change, the clinical-acts foundation, is ratified. Until then every `act.write` is refused with `tier2_not_in_force`, and `define-clinical-message-inbox`'s MI-26 hold continues in substance.
- **Isolation and labels.** Only operational writes are recorded; a scenario or simulation write is refused and stores nothing. Every AI-authored record states the authority it rested on, and every display of it, the patient's included, labels AI authorship.

## Capabilities

### New Capabilities

- `ai-write-path` (AW-01 to AW-12): the contract, integration identity, patient resolution, context isolation, idempotency, receipts, no-PHI rule, durable notification delivery, AI-authorship labels, standalone operation, contract tests and readback by digest.
- `ai-authority-grants` (AG-01 to AG-10): openChart's own record of the medical director's authority grant and its gates.
- `ai-consult-records` (AC-01 to AC-10): Tier 1.
- `ai-clinical-acts` (AA-01 to AA-12): Tier 2. Not buildable until the clinical-acts foundation is ratified.

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged. Two possible conflicts with them are recorded as tensions AT-1 and AT-2 in `design.md`.

## Required prerequisite change (not drafted)

**`define-clinical-acts-foundation`** (proposed id). It must give openChart clinician encounters, orders, prescriptions, diagnoses of record and treatment plans, with the minimum contents listed in `design.md` under "Required prerequisite change". Tier 2 is not buildable, and neither practice mode can be enabled, until it is ratified and built.

## What is buildable now

| Part | Buildable | Blocked by |
|---|---|---|
| Tier 1 (advice-only consult records, grants for `advice_only`, review sample) | After this change and `define-clinical-message-inbox` are ratified, and openChart's constitution is adopted | Constitution (plan phase); inbox ratification (AD-3) |
| Tier 2 (AI-authored acts, practice-mode grants, co-review, reversal) | No | `define-clinical-acts-foundation`; owner disposition of AT-1 and AT-2 |

## Impact

- **openChart:** a write-path integration role per AI system; an authority-grant record, a legal-review record and a review policy, all approved by a named medical director; consult records on the clinical-communication record; review workflow; and, later, the Tier 2 layer over the foundation's acts. Every new component is optional.
- **Dependencies:**
  - `define-clinical-message-inbox` (not yet on main): its clinical-communication record (MI-12, MI-13) is reused by Tier 1. Its MI-26 and Open Question 4 are answered here (tensions AT-5 and AT-6).
  - `define-openpractice-boundary` (not yet on main): its durable outbound pattern (PL-14) and no-PHI rule (PL-13) are reused; CF-02, CF-05 and CF-06 are unchanged.
  - `define-clinical-acts-foundation` (required, not drafted): Tier 2 waits for it.
  - Cross-references: `MedxSoft/medXfactory` change `define-patient-medical-ai-connection` (drafted, not yet on main) owns the medical-AI mode framework and lists this change as a required companion; `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay` is the Medx-specific overlay on this contract.
- **Governance:** openChart's constitution is still the unfilled template. A Constitution Check, and with it the plan phase, needs a constitution adopted through separate governance first.
- **Safety:** every mode off by default; synthetic fixtures only; no PHI in logs, errors, receipts or notifications; no AI act without a current grant, a recorded legal review and clinician co-review; no emergency management by an AI.
- **Tensions:** nine are recorded in `design.md` as AT-1 to AT-9, including two possible conflicts with ratified openChart text (AT-1, AT-2). Each needs the owner's disposition.
