## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

These facts about what is built were checked at `opensoft/openChart-code` revision `30b9645`:
- openChart holds patient-reported allergy, medication and supplement statements (`OC Allergy Statement`, `OC Medication Statement`, `OC Supplement Statement`). Each has `assertion_kind` patient-reported and a `verification_state` (`patient_reported` by default, or `clinician_verified`).
- Statements may carry a code system, code and display.
- There is no clinician-confirmed allergy list, no medication list, no prescription, no drug knowledge and no check.

**Related drafts, none on main:**
- `define-clinical-acts-foundation` (openChart-spec#5, head `e497b03`, content schema digest `d10cb6ddd8c5b2f93a7179d7d4ba00061c4b87461a22bc4fb71983468a9483b2`) specifies the prescription record (RX-01 to RX-04), its signing gate (RX-02), the act model (CA-01 to CA-15) and authority (AU-01 to AU-07). It names this change as required before any prescription is signed, with minimum contents (checked below). At `e497b03` it also holds the general rule for additions to the chart under owner ruling 80 (`chart-additions` AN-01 to AN-14), including the recommendation record (AN-09), and the practitioner's sign-off of owner ruling 151 (CA-04), which at `e497b03` follows the unratified openWallet and openSig drafts, PROPOSED there, and sorts a failed sign-off into four kinds (its AN-14).
- `define-ai-authored-clinical-records` (openChart-spec#4, read at `dbb1fc5` and in part at `6989780`) has a Tier 2 that would accept AI-authored prescriptions. PG-01 covers that acceptance, and it needs `open`.
- `define-openpractice-boundary` (openChart-spec#2, `e7c3090`) has CF-03.

openPractice FD-11 (`opensoft/openPractice-spec`, `ideation/review/openpractice-framing-decisions.md`) governs openPractice's licensed code sets. This change applies the same principle to drug knowledge, by ruling 78.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template at revision `d20de75`. **Planning is blocked until a constitution is adopted.**

## Owner rulings

Every row is a ruling by **Brett Heap**. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

| # | Date | Ruling | Governs |
|---|---|---|---|
| 34 | 2026-11-14 | openPractice is the administrative gateway and holds no clinical content. | BD-02 |
| 35 | 2026-11-14 | The physician uses openChart on mobile or workstation. | SL-05; no requirement depends on a device |
| 67 | 2026-11-15 | No AI is granted clinical authority now. | PG-02 (no AI uses the outage path) |
| 73 | 2026-11-15 | The foundation's scope excludes clinical decision support. This change is the narrow, required exception that ruling 74 names. | Scope |
| 74 | 2026-11-15 | The prescription record is specified in `define-clinical-acts-foundation`, but the prescription feature is not buildable until allergy and interaction checking is specified. A prescription cannot be signed in any deployment where that gate is not met. | PG-01, PG-05; the foundation's RX-02 |
| 75 | 2026-11-15 | "Draft the allergy and interaction checking change too." | This change |
| 76 | 2026-11-15 | When the knowledge source is unavailable at signing, a clinician may sign only with a recorded statement that checks were unavailable and that a manual review was done. The prescription is flagged and re-checked when the source returns. A non-clinician author, including any future AI author, can never use that path. | PG-02 |
| 77 | 2026-11-15 | The first checks are allergy, drug–drug interaction and duplicate therapy. Drug–supplement interaction is included only where the knowledge source declares that it supports it. Later changes: dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, paediatric and geriatric rules. | PC-03 |
| 78 | 2026-11-15 | openChart bundles no drug knowledge. Each practice connects a licensed or verified source through the adapter contract, and no prescription can be signed without one. | KA-01 to KA-03, PG-01 |
| 80 | 2026-11-15 | "The rule in one line: anyone or anything the chart can identify may add to it, the chart records exactly where each addition came from, and only a decision by someone authorized to make it counts as a decision." The owner's statement and the wording he approved are reproduced in `define-clinical-acts-foundation` `design.md`, section "Ruling 80", in the wording for public repositories, with ruling 151 beside it. That change owns the general rule. | PG-01 (a recommendation gets no gate decision, is never a signature, co-signature, release or acceptance, and never counts as a prescription); PC-01 (a pending allergy or medication-list recommendation may only raise a labelled alert, PD-23); PG-02 (what a non-clinician author submits is a recommendation, never refused for missing authority) |
| 82 | 2026-11-15 | "A verified source that is stale or down uses the outage path, with the medical director alerted. Signing stops after a staleness limit set by policy. A practice that never had a verified source cannot sign." | KA-03, KA-04, KA-05, PG-01, PG-02; PT-2, settled |
| 83 | 2026-11-15 | Asked whether prescriptions for controlled substances, or with an unknown classification, should be refused in this change: "Yes. Controlled-substance prescribing goes into a later change alongside electronic prescribing, where its regulatory requirements can be handled properly." | PG-01 (with the foundation's reason code `controlled_classification_not_permitted`); Non-Goals; the foundation's RX-03 |
| 84 | 2026-11-15 | Asked: "openChart's ratified text says no 'API response' shall create a prescription, diagnosis or order. Read broadly, that would block a clinician signing through the API, and block patient-reported allergies from triggering safety alerts." Accepted: "Read it narrowly: it bars automatic creation from intake, and an alert to the clinician isn't a treatment recommendation. Add a small clarifying amendment to the ratified text, so it can't be misread later." | PT-1, settled; the amendment's wording is proposed in `define-clinical-acts-foundation` (its CT-1) |
| 189 | 2026-11-15 | Asked: "An allergy the chart holds only as unconfirmed information or as a recommendation, for example from a nurse, an AI consult or another organization's record: should the prescribing check use it?" Accepted: "Yes, to raise an alert only, labelled as resting on an unconfirmed entry. It never counts as confirmed and never removes a warning." | PC-01; PD-23 (allergies) |

Rulings 79 to 98 were made together on 2026-11-15, when Brett Heap accepted the recommended form of every numbered decision except 80; his words were "accept recomendations. on all but 80". He ruled decision 80 later that day, as ruling 80, recorded in `define-clinical-acts-foundation`. Each row quotes the recommendation he accepted, and the words outside the quotation marks name the question it answered. Later on 2026-11-15 he answered decisions 152 to 194 with the words "accept your recs for 152-194"; row 189 quotes the question and the accepted words. The others that touch openChart's clinical record are recorded in `define-clinical-acts-foundation`. The rows above are the ones that touch this change.

## Goals / Non-Goals

**Goals:**

- Meet ruling 74's gate. No prescription is signed unless checks have run, with the clinician answering every alert, or unless a clinician uses the recorded outage path.
- Make every check failure visible. A check that cannot run is never silent.
- Keep patient-reported content patient-reported, and still use it to protect the patient.
- Bundle no drug knowledge, assert nothing about any source, and keep adapter traffic free of patient identity.
- Reuse the foundation's act model and authority without a second signing model.

**Non-Goals:**

| Out of scope | Pointer |
|---|---|
| Dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, paediatric and geriatric rules | Later governed changes (ruling 77) |
| Other clinical decision support | Later governed changes (ruling 73) |
| Re-checking released prescriptions when the lists change, except outage-flagged ones | A later governed change (PD-15) |
| Any bundled drug knowledge, or any statement about a vendor, product, database or licence | Ruling 78; each practice verifies its own source |
| Electronic prescription transmission | `define-clinical-acts-foundation` RX-04; a later governed change |
| Controlled-substance prescribing | A later change alongside electronic prescribing (ruling 83). Until then PG-01 refuses it. |
| Any change to ratified text, or adopting the constitution | Separate governance |

## Decisions

### 1. Two lists on the foundation's act model

- **New act classes.** Two new classes, `allergy_intolerance` and `medication_list_entry`, follow every rule of the foundation's act model and authority (SL-03).
- **How the classes are added.** They enter `openchart-clinical-act-content` in a MINOR version, together with the prescription content flag `checks_unavailable_at_signing` that the outage path sets (PG-02). That version is published by a governed revision of `define-clinical-acts-foundation` once both changes are ratified, so this change never edits the foundation's files (PD-1; tension PT-3).
- **Allergy entries.** An entry carries a substance, category, criticality, clinical status and verification status, and optional reactions and onset. A separate act type records "no known drug allergies", so an empty list never means "none" (PD-3).
- **The active medication list.** It is the clinician-confirmed entries plus the foundation's `released` prescriptions, included by reference, so nothing is listed twice (PD-2).
- **Reconciliation.** Reconciliation from intake follows the foundation's CA-11: an explicit, attributed action, with the statement unchanged. A "reviewed, not added" record leaves the statement in the check inputs (SL-04, PD-17).

### 2. Inputs, and what cannot be checked

A check reads (PC-01, PD-4):
- the prescription version;
- the confirmed entries;
- the other `pending_release` and `released` prescriptions, so a duplicate between two prescriptions not yet released is caught;
- the latest accepted version of every active patient-reported allergy, medication and supplement statement, including those marked `clinician_verified`, because they remain patient-reported.

A `draft` or `refuted` entry never hides a report of the same substance. An entry is for the same substance when it was reconciled from the statement or carries the same code system and code.

Only codes go to the source. An uncoded or free-text entry is sent only when the source's verification records the agreement that counsel requires (PD-20); otherwise it stays local. Each of these raises an explicit warning that needs its own response (PC-02, PC-06):
- uncoded or unresolvable input, including free text kept local;
- an item the source reports as not recognized, ambiguous, of an unsupported kind or outside its scope;
- a requested check kind that the source did not run;
- a missing allergy status.

### 3. Checks, severities and responses

- **Check kinds.** Allergy (ingredient and class), drug–drug and duplicate therapy, plus drug–supplement only where declared (PC-03, ruling 77).
- **When checks run.** At drafting, after each change, at signing, at co-signature and at release, including at a deferred release time (PC-04, PD-7, PD-21).
  - Each step check runs against the exact content digest, and anything older is stale.
  - The co-signer sees every earlier alert and override.
  - A new finding at release holds the prescription in `pending_release` and opens a work item; no timer releases it.
- **Severity.** The scale is `critical`, `high`, `moderate`, `low` and `info`. Source severities map through the adapter's declared mapping, and an unmapped one counts as `critical`. A same-ingredient allergy match is always `critical` (PC-05, PD-5).
- **Responses.** Each `critical` and each `high` alert, each "could not be checked" warning (above all on allergy inputs) and the "allergy status not recorded" warning need their own explicit response, with a reason. Only `moderate`, `low` and `info` alerts may share one recorded reason. Changing or cancelling the prescription also answers an alert (PC-06, PD-6).
- **The record.** Each check is stored as an immutable record attached to the prescription version (PC-07). It holds the inputs with their kinds, the source, version and effective date, the adapter and its capability declaration, the alerts as shown, the responses and the outcome. Alert text is stored as shown (PD-18; Open Question 5).
- **Labels.** Alerts are labelled as advice from the named source. The clinician is named as the decision-maker, and nothing is ever labelled "safe" (PC-08).

### 4. The adapter contract

`openchart-drug-knowledge-adapter/1.0` is owned by this change (KA-02). It follows the convention of the sibling contracts:
- JSON Schema draft 2020-12, with a URN `$id`;
- closed objects;
- dispatch on `message_type`;
- `contracts/SHA256SUMS`.

| Message | Direction | Use |
|---|---|---|
| `source.identify.request` / `source.identity` | openChart → adapter → openChart | Source reference, label, version, effective date; adapter reference and version |
| `capability.request` / `capability.declaration` | both ways | Operations, check kinds (drug–supplement only if listed), accepted code systems, severity mapping, batch limit |
| `medication.normalize.request` / `.result` | both ways | Ingredients and classes per item, or a coded `not_checked` reason |
| `allergy.cross_reference.request` / `.result` | both ways | `same_ingredient` or `class_cross_sensitivity` matches, graded |
| `interaction.lookup.request` / `.result` | both ways | `drug_drug`, `duplicate_therapy`, `drug_supplement` findings, graded; `kinds_checked` says what actually ran |
| `adapter.error` | adapter → openChart | A coded error, never "no alerts" |

Every result carries the source stamp (reference, version, effective date). Requests carry codes only, and normalized items go back as codes without labels. A code holds no whitespace, a code system is a URI, and openChart sends a coding only in a system the source declares, with only the version recorded for its loaded code set (KA-06). An item's `free_text` is allowed only in a request that names the `free_text_agreement_ref` from the source's verification (PD-20). No message has a patient field, so patient identity cannot cross (KA-06, PD-14). `contracts/examples/` holds 25 synthetic fixtures, 11 that must validate and 14 that must fail. Among the failing ones is the reviewer's probe, patient words sent as a coding, each for one reason stated in `examples/expected-failures.json`. Every substance, class, code system and rule in them is synthetic.

A practice's medication codings come from its own code sets (foundation CA-12). A source accepts the code systems it declares. A mismatch makes items uncheckable, and each such item raises PC-02's warning. Contract tests during verification (KA-03) expose a mismatch before go-live.

### 5. Verification, currency and failures

- **Verification.** A source is usable only after the medical director records a verification (KA-03, PD-8). It holds the source and adapter identities and versions, the practice's evidence reference, a passing contract test, an effective date and a review date. openChart does not judge the licence. A new version or a passed review date needs a new verification.
- **Currency (ruling 82).** The medical director sets a maximum source age and a longer staleness limit. A source past the maximum age is stale: it is handled as the outage path, and the medical director is alerted. Past the staleness limit, signing stops and no outage path is offered. With no policy set, no source is usable (KA-04, PD-9, PD-12).
- **Failures.** A timeout, an error, an invalid result or an omitted input never reads as "no alerts" (KA-05, PD-10). A verified source that goes down alerts the medical director, as a stale one does, once per period of unavailability: after a policy threshold, or at the first outage-path step, whichever comes first (KA-05; the bound is PROPOSED in PD-12).

### 6. The gate (rulings 74, 76, 78, 82 and 83)

One decision is made per signature, co-signature and release attempt (PG-01, PD-19):

| Decision | When |
|---|---|
| `open` | Capability enabled; legal review in force; source verified and current; that step's check complete for the exact digest; every alert and warning answered under PC-06 |
| `outage_path` | Everything else holds, but the verified source is unavailable at that step (unreachable, failing, or stale but within the staleness limit) |
| `refused` | `controlled_classification_not_permitted`, `capability_disabled`, `legal_review_missing`, `no_verified_source`, `currency_policy_missing`, `source_stale_beyond_limit`, `check_not_completed`, `check_stale` or `alerts_unanswered` |

**The outage path** (PG-02, ruling 76; mechanics PD-11 and PD-22):
- only an author whose type is `clinician`, holding prescription `sign` scope (or `cosign` scope for a co-signature), may use it;
- **local review, entry by entry:** the review list is PC-01's input list, taken by reference and never narrowed, less the prescription itself. So every active patient-reported statement appears, whether or not it was reconciled, reviewed or marked `clinician_verified`. The list adds every `draft` or `refuted` entry for the same substance as a statement on it, and the "allergy status not recorded" warning. openChart shows one entry at a time. The clinician responds to each entry on its own, never one response for several, and the responses are stored as that step's outage-review check record;
- the clinician records the statement that the checks were unavailable and that a manual review was done, with code `prescribing.checks_unavailable_manual_review`, on that step's check record. It is also the attestation of a signature or co-signature; a release has no signature;
- only at signing is the prescription content's `checks_unavailable_at_signing` flag set, before the signature. At co-signature and release, the outage is recorded on the check record alone, and signed content never changes (foundation CA-05). The prescription is listed for the acting clinician and the medical director;
- a deferred release with the source unavailable, and no clinician taking this path, stays `pending_release` with a work item (foundation RX-02);
- it is re-checked automatically when the source is available and current;
- an alert from the re-check opens a work item that no timer closes.

A future AI author always needs `open`.

**Controlled and unknown classifications** (ruling 83). A prescription classified `controlled` or `unknown` under the foundation's RX-03 is refused at every step with `controlled_classification_not_permitted`, the foundation's own reason code, whatever the source's state. It never takes the outage path. Controlled-substance prescribing goes into a later change alongside electronic prescribing (ruling 83).

**How rulings 76, 78 and 82 fit together** (tension PT-2, settled by ruling 82; PD-12). Ruling 78 ("no prescription can be signed without one") governs configuration: with no verified source connected, the decision is `refused` and no outage path exists, and ruling 82 confirms that a practice that never had a verified source cannot sign. Ruling 76 governs a connected, verified source that is unavailable at signing. Ruling 82 puts staleness under ruling 76: a verified source that is stale or down uses the outage path, with the medical director alerted, and signing stops after a staleness limit set by policy. A source whose verification has lapsed (KA-03) is not a verified source, so it stays refused, as before.

**Go-live** needs a recorded legal and regulatory review (PG-04, PD-13). Its topics are listed in the requirement. No rule is asserted about medical-device or other regulation.

**No bypass.** Disabling the capability refuses every signature (PG-03).

### 7. Order of building

This change is one Spec Kit feature, the protocol's default (PD-16):
1. It builds on foundation feature (1), clinical authority, and feature (2), encounter, note and signing, which carries the act model.
2. Foundation feature (5), prescriptions, may start only after this change is ratified (ruling 74).
3. This change's checks and gate are enabled before, or together with, foundation feature (5) in any deployment. Until then, RX-02 refuses every signature, co-signature and release (PG-05).

### 8. FHIR R4-compatible mapping (contract level, no conformance claim)

| Item | Resource | Key mappings |
|---|---|---|
| Allergy entry | AllergyIntolerance | code; category; criticality (`low`, `high`, `unable-to-assess`); clinicalStatus; verificationStatus; reaction; onset. "No known drug allergies" as its own coded entry |
| Medication list entry | MedicationStatement | medication; status (`active`, `on-hold`, `stopped`); dosage text; effective period |
| openChart prescription | MedicationRequest | As in `define-clinical-acts-foundation` |
| Alert and response | DetectedIssue | code from check kind; severity (`critical` and `high` → `high`, `moderate` → `moderate`, `low` and `info` → `low`); implicated items; evidence; mitigation = override with clinician, time and reason |
| Check record | Provenance | agent (signing clinician); entity (inputs, source version) |

The value sets are to be checked in planning against the FHIR R4 specification (BD-03). openChart claims no certification and no profile or implementation-guide conformance.

## Minimum contents listed by `define-clinical-acts-foundation`

| # | Foundation item | Where this change meets it |
|---|---|---|
| 1 | Clinician-confirmed allergy and active medication lists on the act model, with no second signing model | SL-01 to SL-03, PD-1 |
| 2 | Reconciliation from intake only by an explicit, attributed action | SL-04 |
| 3 | Inputs include patient-reported statements; uncheckable entries warn explicitly | PC-01, PC-02 |
| 4 | The first checks (ruling 77) | PC-03 |
| 5 | Checks at drafting, at each change and at signing; severities; overrides with reasons; individual critical overrides; a record of each check; labels as advice | PC-04 to PC-08 |
| 6 | No bundled knowledge; a versioned adapter contract with schema and SHA256SUMS; nothing asserted about vendors; synthetic fixtures | KA-01, KA-02, KA-06 |
| 7 | Gates: a verified source, and none for a practice that never had one; a verified source that is stale or down on the outage path, until a staleness limit set by policy stops signing (ruling 82); the outage path for clinicians only; a recorded legal and regulatory review; controlled and unknown classifications refused (ruling 83) | KA-03, KA-04, PG-01, PG-02, PG-04 |
| 8 | One gate decision per signing attempt that RX-02 relies on; an attempt entered as a recommendation, or stopped before the gate by a sign-off failure that leaves the draft open, gets none | PG-01 |
| 9 | Boundaries: no source needed except for signing; nothing to openPractice; FHIR mapping | BD-01 to BD-03 |

All nine are met.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone application, which must operate without MedxFactory, MedxEHR or openPractice | BD-01. Nothing needs an external system except prescription signing, which needs a practice-connected source. |
| External identifiers never replace the openChart identifier | Unaffected. Adapter traffic carries no patient identity (KA-06). |
| Submissions versioned and idempotent; statements preserve reported detail | Untouched. Checks read statements and never change them. |
| Amendments preserve accepted history | SL-03 (the foundation's CA-05 and CA-06), PC-07 (immutable check records). |
| APIs and hooks authorized and versioned | Lists follow the foundation's CA-10. The adapter contract is versioned by MAJOR version and digest. |
| Intake does not confer clinician or autonomous authority | SL-04. Nothing is promoted automatically, and statements stay patient-reported. Alerts advise and create nothing. **Tension PT-1, read narrowly under ruling 84.** |

One possible conflict with ratified text is recorded, as PT-1, and ruling 84 settles it. No other conflict with ratified text was found.

## Design calls for owner review

Each item goes beyond the rulings and is proposed, not ruled. Where an item implements a ruling, it cites the ruling, and its mechanics stay a proposed design call. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| PD-1 | The two act classes, and the prescription flag `checks_unavailable_at_signing`, are added to `openchart-clinical-act-content` in a MINOR version, published by a governed revision of the foundation after both changes are ratified. Their fields are fixed here at requirement level. | SL-01 to SL-03, PG-02 |
| PD-2 | The active medication list is confirmed entries plus `released` prescriptions, included by reference. | SL-02 |
| PD-3 | An explicit "no known drug allergies" act type. With neither entries nor that assertion, the status is "not recorded", and every check warns. | SL-01, PC-02 |
| PD-4 | Inputs include the latest accepted patient-reported statements, whether reconciled, reviewed or marked `clinician_verified`, and every other `pending_release` and `released` prescription. A draft or refuted entry never hides a report. | PC-01 |
| PD-5 | The closed severity scale. An unmapped source severity counts as `critical`, and a same-ingredient allergy match is always `critical`. | PC-05 |
| PD-6 | Responses are coded reasons with optional text. Each `critical` and `high` alert and every warning gets its own response. Only `moderate`, `low` and `info` alerts may share one reason. | PC-06 |
| PD-7 | The signing-time check runs against the exact content digest being signed. Any change to the prescription or an input makes a result stale. | PC-04 |
| PD-8 | The medical director records the source verification, with the practice's evidence reference and a passing contract test. A new version or a passed review date needs a new verification. | KA-03 |
| PD-9 | The medical director sets the currency policy: a maximum age and a longer staleness limit, both measured from the source's effective date. This change sets neither value. With either missing, no source is usable. A stale source alerts the medical director. | KA-04 |
| PD-10 | Every adapter failure, and every omitted input, is "unavailable" or "could not be checked", never "no alerts". | KA-05 |
| PD-11 | Outage-path mechanics beyond ruling 76: listing for the signer and the medical director, automatic re-check on return, and a work item that no timer closes. | PG-02 |
| PD-12 | **Under ruling 82.** A stale source counts as unavailable, so the outage path applies, and the medical director is alerted. Past the staleness limit, the decision is `refused` with `source_stale_beyond_limit` at every step, and no outage path is offered. A verified source that goes down also alerts the medical director (KA-05), once per period of unavailability: when it has stayed unavailable longer than an alert threshold, or at the first outage-path step, whichever comes first. **PROPOSED:** this bound. The threshold is a policy value that the medical director sets, and until it is set every unavailability alerts at once. | KA-04, KA-05, PG-01, PG-02 |
| PD-13 | The medical director records the legal and regulatory review, with the topics in PG-04. A lapse refuses every signature. | PG-04 |
| PD-14 | Adapter requests carry codes only and no patient identity. The schema enforces closed objects, no label or patient fields, a code without whitespace, a URI code system and a token version. openChart enforces at runtime that a coding is sent only in a system the source declares, and only with the version recorded for its loaded code set, because no schema pattern can tell a version from an identifier. | KA-06 |
| PD-15 | Released prescriptions are not re-checked when the lists change, except outage-flagged prescriptions. That waits for a later change. | Non-Goals |
| PD-16 | One Spec Kit feature, built after foundation features (1) and (2) and enabled before, or together with, foundation feature (5). | PG-05 |
| PD-17 | A "reviewed, not added" record leaves the statement unchanged and still in the check inputs. | SL-04 |
| PD-18 | Alert text is stored in the check record as shown, so the record shows what the clinician saw. Whether the source's licence permits this is Open Question 5. | PC-07 |
| PD-19 | The gate decision codes and their order are as tabulated in Decision 6. Under ruling 83, a `controlled` or `unknown` classification is refused first, whatever the source's state, with the foundation's reason code `controlled_classification_not_permitted`, and never takes the outage path. Controlled-substance prescribing goes into a later change alongside electronic prescribing. | PG-01 |
| PD-20 | Free text (a patient's own wording, or any uncoded description) goes to a source only when the source's verification records `free_text_agreement_ref`, the agreement counsel requires (Open Question 9). Otherwise uncoded entries stay local as "could not be checked". | KA-03, KA-06, PC-02 |
| PD-21 | Checks also run at co-signature and at release, each against the exact digest. The co-signer sees every earlier alert and override and answers new findings. A finding at release that was not answered before holds the prescription in `pending_release` and opens a work item; no timer releases it. A finding counts as already answered only for the same inputs and source version. | PC-04, PG-01; foundation RX-02 |
| PD-22 | At an outage step, the review list is PC-01's input list by reference, less the prescription itself, so every active patient-reported statement appears, reconciled or not. It adds every `draft` or `refuted` entry for the same substance and any missing allergy status. openChart shows one entry at a time, and the clinician answers each entry on its own. The statement uses code `prescribing.checks_unavailable_manual_review` and is recorded on that step's check record; it is also the attestation of a signature or co-signature. Only the signing step sets the signed content flag `checks_unavailable_at_signing`; co-signature and release change no signed content. | PG-02, SL-03 |
| PD-23 | **Ruled by 189 for allergies; the rest PROPOSED, listed for the owner under ruling 80.** Owner ruling 189: an allergy the chart holds only as unconfirmed information or as a recommendation, for example from a nurse, an AI consult or another organization's record, is used by the check "to raise an alert only, labelled as resting on an unconfirmed entry. It never counts as confirmed and never removes a warning." PROPOSED beyond its words: where that entry is a recommendation, the label also says it is not an authorized decision (ruling 80); and PC-01 also takes, under the same rule, every pending recommendation record (`define-clinical-acts-foundation` AN-09) that proposes a medication list entry, labelled as resting on an entry that is not an authorized decision. None of these inputs is ever treated as confirmed, suppresses an alert or warning, or satisfies anything, so an allergy recorded through a path without the authority still reaches the check. Through PD-22 they also appear, marked, in the outage-review list. | PC-01, PG-01, PG-02 |

## Conflicts and tensions

Five are recorded. PT-1 and PT-2 are settled by owner rulings 84 and 82. Each of the other three needs the owner's disposition before ratification. None is resolved by this draft on its own authority.

| # | Tension | Status |
|---|---|---|
| PT-1 | **Ratified text.** `expanded-patient-intake`, "Intake does not confer clinician or autonomous authority": "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action." A patient-reported allergy or supplement statement becomes an input that can raise an alert about a clinician's draft. | **Settled by ruling 84:** "an alert to the clinician isn't a treatment recommendation", and the sentence "bars automatic creation from intake". An alert advises on the clinician's own draft and creates no record of care and no action, and the statement stays patient-reported. No MODIFIED delta is needed. The clarifying amendment that ruling 84 directs says this in so many words. It is proposed in `define-clinical-acts-foundation` (its CT-1), for the owner to apply to the ratified requirement at ratification. |
| PT-2 | **Rulings 76 and 78 read together.** Ruling 78 says "no prescription can be signed without one" (a connected, licensed or verified source). Ruling 76 lets a clinician sign when the source is unavailable at signing. The brief also counts a stale source as unavailable. | **Settled by ruling 82:** "A verified source that is stale or down uses the outage path, with the medical director alerted. Signing stops after a staleness limit set by policy. A practice that never had a verified source cannot sign." Ruling 78 governs configuration, so with no verified source connected there is no outage path (PD-12, KA-04, PG-01). |
| PT-3 | `define-clinical-acts-foundation` (draft) CA-01 records "exactly six act classes" and refuses any other. This change adds `allergy_intolerance` and `medication_list_entry`. | That change needs a governed revision: CA-01 wording and a MINOR version of `openchart-clinical-act-content` that adds both classes (PD-1). This change does not edit it. |
| PT-4 | `define-ai-authored-clinical-records` (draft) accepts a Tier 2 act at receipt (AA-03) and does not mention prescribing-safety checks. Under ruling 76, an AI-authored prescription always needs a completed check and never uses the outage path. | That change should state that acceptance of an AI-authored prescription calls PG-01 and needs `open`. Meanwhile PG-02 refuses the outage path to any non-clinician author, and foundation RX-02 refuses any prescription signature without the gate. |
| PT-5 | openChart `AGENTS.md`: "Do not enable autonomous clinical actions by default." Some steps here are automatic: checks at drafting, re-checks when the source returns, and work items. | Not a conflict by its letter. Each step informs a clinician and decides nothing; signing stays a clinician's act. Recorded for the owner's confirmation. |

## Risks / Trade-offs

- **[Alert fatigue]** → Severity scale; shared acknowledgement below `critical`; individual overrides for `critical` only.
- **[A silent gap in checking]** → Explicit warnings for every uncheckable input and every check kind not run; failures never read as "no alerts".
- **[Outage abuse]** → Clinician only, a recorded statement, a flag, listing for the medical director, and an automatic re-check.
- **[A stale or unverified source]** → Verification and a currency policy recorded by the medical director, with a stale source counted as unavailable and signing stopped past the staleness limit (ruling 82).
- **[Controlled-substance prescribing]** → Refused at every step, and never through the outage path (ruling 83).
- **[Licensing of drug knowledge]** → Nothing bundled; practice-supplied sources; the practice's evidence recorded; Open Question 5 on stored alert text.
- **[Regulatory status of decision support]** → A recorded legal and regulatory review before go-live; no rule asserted.
- **[PHI leaving through the adapter]** → Closed schema with no patient fields.
- **[No constitution]** → Planning is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly, check the schema digest and run the self-test. Brett Heap disposes PT-3 to PT-5 and PD-1 to PD-23, including the design calls made under rulings 82 and 83 (PD-9, PD-12, PD-19) and the parts of PD-23 beyond ruling 189, stamps `Ratified by` and sets `Status: ratified`.
2. Adopt openChart's constitution through separate governance.
3. After foundation features (1) and (2) land, create this change's single feature: the lists, checks, adapter client, check record, verification, currency and legal-review records, and the gate. Contract tests run against an adapter double.
4. A governed revision of `define-clinical-acts-foundation` publishes the MINOR content-schema version with the two act classes (PT-3).
5. Enable the gate before, or together with, foundation feature (5) in each deployment, after the medical director records the verification, the currency policy (maximum age and staleness limit) and the legal review.
6. Rollback: disable the capability, which refuses every prescription signature. Records stay; nothing is deleted.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** This blocks planning.
2. **Owner dispositions** of PT-3 to PT-5 and PD-1 to PD-23 (PT-1 and PT-2 are settled by rulings 84 and 82). These block ratification. PD-23 is ruled by 189 for allergies; its medication-list part, and the added label for a recommendation, are listed for the owner under ruling 80.
3. **The legal and regulatory review.** Counsel decides its content for each jurisdiction, including whether this capability is regulated as a medical device or otherwise. This change asserts no rule. It blocks go-live in each deployment, not the build.
4. **Which sources a practice may connect.** Each practice verifies its own source and licence; openChart names none. This blocks go-live in each deployment.
5. **Storing alert text.** May a check record keep a source's alert text as shown, under that source's licence? The practice and counsel decide. Meanwhile, PD-18 stores it, and a practice whose licence forbids that must not go live until a governed revision stores a reference instead.
6. **Retention** of check records, overrides and work items. The owner and counsel decide. Meanwhile, nothing is deleted.
7. **Retrospective re-checks** when the lists change. This needs a later governed change. Meanwhile, PD-15 applies.
8. **Sensitive record categories and minors' records** (the foundation's Open Question 3). The foundation's restricted mark applies to list entries too. Counsel decides.
9. **Free text to a knowledge source.** What agreement must be in place before a patient's own wording may be sent to a source? Counsel decides. Meanwhile, no free text is sent (PD-20).
