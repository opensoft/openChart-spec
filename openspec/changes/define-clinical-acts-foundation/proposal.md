code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: openChart's core clinician-authored clinical record. It has one act model for six act classes: encounter, clinical note, diagnosis of record (encounter diagnosis and problem-list condition), procedure or service performed, a generic order, and the prescription record. The model covers authorship with an author type that accepts only `clinician`, status lifecycles, signing with attestation, amendment by new versions, entered-in-error handling, a co-signature hook, provenance and audit, and an act-type registry. It also covers clinical roles, the medical director designation and role grants recorded in openChart, with practice-supplied, unverified licensure and prescriber facts; explicit, attributed creation of clinician records from patient-reported intake; codings from practice-supplied code sets; the canonical content schema `openchart-clinical-act-content/1.0`; a FHIR R4-compatible mapping at contract level; and publication of signed, final encounters, their diagnoses and procedures to openPractice under `openpractice-ehr-clinical-facts/1.0`, by reference, with forward-only corrections. Out of scope: results ingestion; care plans and treatment-plan records; immunizations; clinical decision support; allergy and interaction checking (the required later change `define-prescribing-safety-checks`); electronic transmission of prescriptions to pharmacies and controlled-substance electronic prescribing; order transmission; AI authorship (`define-ai-authored-clinical-records`); billing and coding validation (openPractice); and any change to the ratified `expanded-patient-intake` requirements.
target_release: Clinical-acts foundation v1, delivered as five ordered Spec Kit features, each gated on ratification (owner ruling 85): (1) clinical authority; (2) encounter, note and signing; (3) diagnoses, procedures and publication to openPractice; (4) orders; (5) prescriptions, which also waits for `define-prescribing-safety-checks` to be ratified (owner ruling 74). The change archives when landed, validator-green open_chart revisions for all five features meet four conditions. They pass contract tests against `openchart-clinical-act-content/1.0` at the recorded digest, and against an openPractice double for publication. They still pass the standalone golden-intake round trip with no external system. They refuse every act whose author type is not `clinician`. And they refuse every prescription signature where the prescribing-safety gate is not met.
Status: draft
Ratified by: pending. The decisions encoded here rest on rulings Brett Heap made on 2026-11-14 and 2026-11-15, including ruling 72 ("draft the openChart clinical-acts foundation change too"), ruling 73 (the scope) and ruling 74 (the prescription gate), and on rulings 82 to 85, 87 to 89, 92, 93 and 98 from the second batch of 2026-11-15. They are recorded in `design.md` under "Owner rulings". Rulings are not ratification. The design calls in `design.md`, including those that implement a ruling, are proposed, not ruled. Ratification requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

openChart is the public, neutral clinical chart, and the doctor's clinical interface on mobile or workstation (rulings 34 and 35). Its built scope is patient intake only:
- `OC Patient` and `OC Patient External Identifier`;
- `OC Intake Submission`;
- eight patient-reported statement families.

There are no clinician encounters, notes, diagnoses, procedures, orders or prescriptions. Every statement is patient-reported, and the ratified `expanded-patient-intake` capability keeps it so.

Three draft changes, none yet on main, wait for this foundation:
- **`define-ai-authored-clinical-records`** (openChart-spec#4) lists it as its required prerequisite, with twelve minimum contents. Its Tier 2 adds AI authorship, an authority grant, clinician co-review and reversal on top of the acts defined here. This change defines no AI authorship.
- **`define-openpractice-boundary`** (openChart-spec#2): its `openpractice-clinical-fact-publication` capability reports "no billable facts" until a clinical-encounter capability exists (CF-06, Open Question 2). openPractice needs final, signed encounter documentation, diagnoses and procedures, with forward-only corrections and references rather than copies (`opensoft/openPractice-spec` `define-mvp-practice-foundation`, EB-13 to EB-16).
- **`define-clinical-message-inbox`** (openChart-spec#3) records clinician replies as clinical communications (MI-12). It says that only a separately governed clinical workflow may record a clinical fact of record.

This change is that workflow: openChart's core clinician-authored clinical record.

## What Changes

The scope below is ruled (owner ruling 73).

- **One act model** (CA-01 to CA-15). Six act classes share one envelope and one canonical content schema, `openchart-clinical-act-content/1.0`, pinned by SHA-256 in `contracts/SHA256SUMS`, with synthetic fixtures and a self-test. Every act has:
  - a named clinician author, with an author type that accepts only `clinician` and refuses every other value;
  - a closed status lifecycle;
  - a signature with attestation, bound to the content digest, with re-authentication at signing;
  - amendments as new versions, never destructive edits;
  - entered-in-error handling;
  - a co-signature hook (before effect, or after the fact within a window, escalating to the medical director);
  - full provenance and audit;
  - an act type from a registry that carries reserved and emergency-management flags.

  Acts are created only by a named clinician through the versioned service boundary. Nothing is created from intake automatically. Codes come from practice-supplied code sets; openChart bundles none and asserts no license status. Acts have a FHIR R4-compatible mapping at contract level, with no conformance claim.
- **Authority** (AU-01 to AU-06). openChart defines clinical roles (`clinician`, `nurse`) and one medical director per practice. The designating account is never the designee, and the designee's role rests on a licensure attestation recorded by another named human. The first medical director is set up by one audited bootstrap act. Grants per act class and action, plus a `review` scope over `ai_consult_record` for AI consult reviews, are recorded by the medical director, and a self-grant is flagged, independently attested and shown. Licensure and prescriber facts are attestations supplied by the practice, never recorded by their own subject, and not verified by openChart. Under ruling 98, a second person confirms the first designation, or a sole administrator records a licence verification against the licensing board's public record, and these acts are listed for the medical director too. Under ruling 92, inbox authority lives in this grant model: AU-06 adds the clinical message inbox's ownership, reply and clinical-need marker scopes, none of which reaches an act. Every action is checked against the grant in force, and reductions apply at once. No agent or automated process authors, signs or co-signs (ruling 67).
- **Encounters and notes** (EN-01 to EN-06):
  - an encounter lifecycle (in progress, final, amended);
  - an optional appointment reference only, since openPractice owns the appointment (ruling 31);
  - signed notes and addenda;
  - finalization only when documentation is complete;
  - a signed encounter amendment for every later change;
  - no requirement depends on form factor (ruling 35).
- **Diagnoses and procedures** (DX-01 to DX-03): coded, clinician-asserted encounter diagnoses and problem-list conditions, kept distinct from patient-reported conditions, and coded procedures performed.
- **Publication to openPractice** (PB-01 to PB-05). This change is the capability that CF-06 waits for. A signed, final encounter, with its coded diagnoses and procedures, is published under `openpractice-ehr-clinical-facts/1.0`:
  - by reference;
  - with codings carrying the system and code only;
  - with encounter diagnoses only when `confirmed`, and a retraction if a published one is later refuted (ruling 87);
  - with forward-only corrections and retractions, queued whatever the link state and delivered when the link returns to `active`. Retractions still reach openPractice, as pointers only, after a link is revoked or superseded (ruling 88). A fact whose latest version could no longer be published is retracted, and every withdrawn encounter reads the same.

  openChart still works with no openPractice.
- **Orders** (OR-01 to OR-04). One generic order record covers laboratory, imaging, referral, procedure and other orders. Its lifecycle is draft, pending release, released, completed, discontinued, cancelled and entered in error. A released order is never amended. openChart transmits no order and ingests no result.
- **Prescriptions** (RX-01 to RX-04). The record of the prescribing decision carries a controlled-substance classification in which unknown counts as controlled.
  - **Binding gate (ruling 74):** no prescription is signed, co-signed or released in any deployment where the prescribing-safety gate of `define-prescribing-safety-checks` is not met.
  - Controlled or unknown prescriptions are refused (ruling 83).
  - There is no pharmacy transmission, no controlled-substance electronic prescribing and no dispense record.

## Capabilities

### New Capabilities

- `clinical-act-record` (CA-01 to CA-15): the shared act model, the content schema, intake derivation, coding, the FHIR mapping, standalone operation and restricted acts.
- `clinical-authority` (AU-01 to AU-06): roles, the medical director, grants and practice-supplied attestations, and the grant scopes for AI consult review and the clinical message inbox.
- `clinical-encounters` (EN-01 to EN-06): encounters, notes, finalization and encounter amendments.
- `clinical-diagnoses-and-procedures` (DX-01 to DX-03).
- `clinical-acts-publication` (PB-01 to PB-05): the source of billable facts under `openpractice-ehr-clinical-facts/1.0`.
- `clinical-orders` (OR-01 to OR-04).
- `clinical-prescriptions` (RX-01 to RX-04).

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged. Possible conflicts with ratified openChart text (CT-1 to CT-3) and with the published p4 compatibility declaration (CT-4) are recorded as tensions in `design.md`. Ruling 84 reads CT-1's sentence narrowly. The clarifying amendment it calls for is proposed in `design.md`, for the owner to apply to the ratified feature text at ratification; this change does not edit that text.

## Required later changes

- **`define-prescribing-safety-checks`** (REQUIRED before any prescription can be signed; ruling 74; being drafted under ruling 75). Its minimum contents are listed in `design.md` under "Required later change: prescribing-safety checks". Feature (5), prescriptions, depends on its ratification.
- Electronic transmission of prescriptions and controlled-substance electronic prescribing, as a later governed change that needs vendor and regulatory verification (ruling 73).
- Results ingestion; care plans and treatment-plan records; immunizations; clinical decision support beyond the prescribing-safety checks; order transmission (ruling 73; `design.md` "Non-Goals").

## What is buildable, in order

| Feature | Contents | Gated on |
|---|---|---|
| (1) Clinical authority | AU-01 to AU-06 | Ratification of this change; openChart's constitution. Going live also needs the confirmation path of ruling 98 (tasks §2.6) |
| (2) Encounter, note and signing | CA-01 to CA-15, EN-01 to EN-06 | Feature (1) |
| (3) Diagnoses, procedures and publication | DX-01 to DX-03, PB-01 to PB-05 | Feature (2). Publication also needs `define-openpractice-boundary` ratified and its publication surface built |
| (4) Orders | OR-01 to OR-04 | Feature (2) |
| (5) Prescriptions | RX-01 to RX-04 | Feature (2) and **ratification of `define-prescribing-safety-checks`** (ruling 74) |

## Impact

- **openChart:**
  - act storage for six classes, with versions, signatures, lifecycle events and audit;
  - a role, grant and attestation store, and a medical director designation;
  - an act-type registry and a code-set import record;
  - an extension of the versioned service boundary;
  - the content schema contract;
  - publication through the PL-14 durable outbound store.

  Every component works with no external system, except that prescription signing needs the prescribing-safety gate.
- **Dependents:**
  - `define-ai-authored-clinical-records` gets its prerequisite. Eleven of its twelve minimum contents are met. Treatment plans are not, by ruling 73, and that change now records them as a later prerequisite (CT-6 to CT-8 resolved). Its consult review grant lives in AU-02.
  - `define-openpractice-boundary` gets the capability that CF-06 and Open Question 2 wait for, without any edit to it.
  - `define-clinical-message-inbox` gets the clinical workflow that MI-12 and MI-14 defer to, the roles and grant scopes it cites (AU-01 to AU-06; AU-06 under ruling 92), clinical authority as feature (1) (ruling 92), and a proposed answer to its Open Question 11.
- **Governance:** openChart's constitution (`.specify/memory/constitution.md` in `opensoft/openChart`) is still the unfilled Spec Kit template. A Constitution Check, and with it the plan phase of every feature, needs a constitution adopted through separate governance first.
- **Safety:**
  - every act is a named human's;
  - no AI clinical authority (ruling 67);
  - signed content is never edited;
  - prescriptions are gated (ruling 74);
  - synthetic fixtures only;
  - no PHI in logs;
  - sensitive categories are an open question for counsel, with a fail-closed restricted mark meanwhile.
- **Tensions:** sixteen are recorded in `design.md` as CT-1 to CT-16. CT-6 to CT-10 are resolved; CT-1, CT-14 and CT-15 are settled by rulings 84, 85 and 88; and CT-16 is ruled (ruling 89) and stays recorded until the follow-up of ruling 93 lands. Four of them (CT-1 to CT-4) concern ratified openChart text or published openChart contracts. Each other open tension needs the owner's disposition.
