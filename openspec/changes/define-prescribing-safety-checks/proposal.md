code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: a clinician-confirmed allergy and intolerance list and an active medication list, both on `define-clinical-acts-foundation`'s act model, reconciled from patient-reported intake only by an explicit, attributed clinician action; prescribing-safety checks whose inputs are clinician-confirmed entries and patient-reported statements, with an explicit "could not be checked" warning for anything that cannot be checked; the first checks (allergy by ingredient and class, drug–drug interaction and duplicate therapy, plus drug–supplement interaction where the source declares support); severities, individual overrides with recorded reasons, and an immutable check record; a versioned adapter contract, `openchart-drug-knowledge-adapter/1.0`, through which each practice connects a drug knowledge source it has licensed or verified; and the prescribing-safety gate that `define-clinical-acts-foundation` RX-02 relies on, with its clinician-only outage path and a recorded legal and regulatory review before go-live. Out of scope: any bundled drug knowledge; dose-range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, and paediatric and geriatric rules; other clinical decision support; re-checking released prescriptions when the lists change (except outage-flagged prescriptions); electronic prescription transmission; controlled-substance prescribing (ruling 83: a later change alongside electronic prescribing); and any change to the ratified `expanded-patient-intake` requirements.
target_release: Prescribing safety v1, one Spec Kit feature, built after `define-clinical-acts-foundation` features (1) and (2) and enabled before, or together with, its feature (5). The change archives when a landed, validator-green open_chart revision meets these conditions. It passes contract tests against an adapter double at the recorded schema digest. It still passes the standalone golden-intake round trip with no source connected. Every prescription signature is refused when there is no verified source, a source past its staleness limit, a controlled or unknown classification, no recorded legal and regulatory review, no completed signing-time check, or an unanswered alert. And the outage path, which a stale source within its staleness limit also takes, is open only to a clinician who records the statement.
Status: draft
Ratified by: pending. The decisions encoded here rest on rulings Brett Heap made on 2026-11-15: ruling 74 (no prescription is signed until allergy and interaction checking is specified), ruling 75 ("draft the allergy and interaction checking change too"), rulings 76 to 78 (the outage path, the first checks, and no bundled drug knowledge), and, from the second batch of 2026-11-15, rulings 82 to 84 (a stale source and the staleness limit, controlled and unknown classifications, and the narrow reading of the ratified intake sentence). They are recorded in `design.md` under "Owner rulings". Rulings are not ratification. The design calls in `design.md`, including those that implement a ruling, are proposed, not ruled. Ratification requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

`define-clinical-acts-foundation` (openChart-spec#5, not yet on main) specifies the prescription record. Under owner ruling 74, its prescription feature is not buildable until allergy and interaction checking is specified, and no prescription can be signed in a deployment where that gate is not met (its RX-02). This change is that checking.

The foundation's scope (ruling 73) has no clinician-confirmed allergy list or medication list, and checking needs both. openChart today holds only patient-reported allergy, medication and supplement statements, which the ratified `expanded-patient-intake` capability keeps patient-reported.

## What Changes

- **Lists** (SL-01 to SL-05). openChart gains a clinician-confirmed allergy and intolerance list, with an explicit "no known drug allergies" assertion, so that an empty list never means "none". It also gains an active medication list: clinician-confirmed entries plus openChart's released prescriptions, by reference. Both reuse the foundation's act model, and no second signing model is defined. Patient-reported statements reach the lists only by an explicit, attributed clinician action. The chart always shows unreconciled reports beside confirmed entries, each labelled.
- **Checks** (PC-01 to PC-08).
  - **Inputs:** clinician-confirmed entries and patient-reported statements alike. A report is never ignored because nobody has confirmed it.
  - **What cannot be checked:** anything the source cannot check gets an explicit "could not be checked" warning, never silence. Free text stays local unless a counsel-required agreement is recorded for the source.
  - **First checks (ruling 77):** allergy by ingredient and class, drug–drug interaction and duplicate therapy, plus drug–supplement interaction only where the source declares support.
  - **When they run:** at drafting, after each change, at signing, at co-signature (the co-signer sees every earlier alert and override) and at release. A new finding at release holds the prescription. Pending prescriptions are inputs too.
  - **Severity:** a closed severity scale. A same-ingredient allergy match is always critical, and an unmapped severity counts as critical.
  - **Responses:** every alert gets a response. Critical and high alerts and every warning each need their own response with a reason; only lower-severity alerts may be acknowledged together.
  - **Record:** an immutable check record holds the inputs, the source and its version, the alerts and the responses.
  - **Labels:** alerts are labelled as advice, and the record names the clinician as the decision-maker.
- **Knowledge source** (KA-01 to KA-06).
  - openChart bundles no drug knowledge (ruling 78). Each practice connects a source it has licensed or verified, through `openchart-drug-knowledge-adapter/1.0`, a canonical JSON schema pinned by SHA-256 in `contracts/SHA256SUMS`, with synthetic fixtures and a self-test.
  - The operations are: source identity, capability declaration, normalization to ingredients and classes, allergy cross-reference, interaction lookup, and coded errors.
  - A source is usable only after the medical director records its verification and a currency policy; a practice that never had a verified source cannot sign. A verified source that is stale or down uses the outage path, with the medical director alerted, and signing stops after a staleness limit set by policy (ruling 82).
  - Adapter failures are never read as "no alerts".
  - Requests carry codes only, in the source's declared systems, and no patient identity. Free text is sent only under an agreement recorded in the source's verification.
  - Nothing is asserted about any vendor, product, database or licence.
- **Gate** (PG-01 to PG-05).
  - One gate decision per prescription signature, co-signature and release, which the foundation's RX-02 relies on.
  - **No verified source, no signing** (ruling 78).
  - **Controlled and unknown classifications are refused** (ruling 83) at every step, and never through the outage path. Controlled-substance prescribing goes into a later change alongside electronic prescribing.
  - **Outage path (ruling 76):** when the source is unavailable at a step (signature, co-signature or release), only a clinician may complete it. The clinician first answers every local input that needs no source, one entry at a time, then records the statement (code `prescribing.checks_unavailable_manual_review`) on that step's check record. Only signing sets the signed flag `checks_unavailable_at_signing`. The prescription is re-checked when the source returns. A non-clinician author, including any future AI author, can never use this path.
  - **Go-live** needs a recorded legal and regulatory review, whose topics are listed. No legal rule is asserted.
  - No role or setting bypasses the gate.
  - Foundation feature (5), prescriptions, depends on this change's ratification.
- **Boundaries** (BD-01 to BD-04):
  - everything except prescription signing works with no source;
  - no list, check or alert content goes to openPractice;
  - a FHIR R4-compatible mapping (AllergyIntolerance, MedicationStatement, MedicationRequest, DetectedIssue, Provenance), with no conformance claim;
  - no PHI in logs;
  - a check that cannot run is always visible.

## Capabilities

### New Capabilities

- `clinical-safety-lists` (SL-01 to SL-05)
- `prescribing-safety-checks` (PC-01 to PC-08)
- `drug-knowledge-adapter` (KA-01 to KA-06)
- `prescribing-safety-gate` (PG-01 to PG-05)
- `prescribing-safety-boundaries` (BD-01 to BD-04)

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged. One possible conflict with them is recorded as tension PT-1 in `design.md`; ruling 84 settles it by reading the ratified sentence narrowly.

## Dependencies

- **`define-clinical-acts-foundation`** (openChart-spec#5, not yet on main):
  - Its act model (CA-01 to CA-15) and authority (AU-01 to AU-05) are reused.
  - Its RX-02 relies on this change's gate decision (PG-01).
  - Its RX-03 refuses controlled and unknown classifications, and PG-01 refuses them too under ruling 83, with the same reason code.
  - Its feature (5), prescriptions, may start only after this change is ratified (ruling 74).
  - Its content schema needs a MINOR version that adds this change's two act classes (tension PT-3).
- **`define-ai-authored-clinical-records`** (openChart-spec#4, not yet on main): a future AI-authored prescription always needs an `open` gate decision and never the outage path (ruling 76; tension PT-4).
- **`define-openpractice-boundary`** (openChart-spec#2, not yet on main): CF-03 is kept, and nothing from this change is published.
- **Cross-references only:** medXfactory and MedxEHR. This change defines no interface to either.

## Impact

- **openChart:**
  - two new act classes on the foundation's act model;
  - list views that label each item's source;
  - a check engine over the adapter contract;
  - an immutable check record;
  - a source verification record, a currency policy (maximum age and staleness limit), an unavailability alert threshold and a legal-review record, all kept by the medical director;
  - the gate decision;
  - outage-path flags and re-check work items.
- **Governance:** openChart's constitution is still the unfilled template. A Constitution Check, and with it the plan phase, needs a constitution adopted through separate governance first.
- **Safety:**
  - no prescription without a completed check, or a clinician's recorded statement during an outage;
  - no controlled or unknown classification signed (ruling 83);
  - every unchecked input visible;
  - critical alerts overridden one at a time, with reasons;
  - no bundled drug data;
  - synthetic fixtures only;
  - no patient identity in adapter traffic;
  - no PHI in logs.
- **Tensions:** five are recorded in `design.md` as PT-1 to PT-5. PT-1, on ratified openChart text, is settled by ruling 84, and PT-2, on reading rulings 76 and 78 together, by ruling 82. The other three need the owner's disposition.
