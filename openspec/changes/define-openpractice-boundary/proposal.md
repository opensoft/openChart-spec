code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: a configured openChart issuer; validation against openPractice's canonical schemas, pinned by digest; `OC Patient External Identifier` rows in namespace `openpractice`; a dedicated integration role narrower than System Manager; link, review, revocation, demographic-update and correction-request handling under `openpractice-ehr-patient-link/1.0`; a namespace-aware identity decision; an immutable store of applied administrative demographic versions, projected onto `OC Patient`; a link-level suspension on date-of-birth changes; honoring confidential-communication instructions in every patient communication openChart or a system it drives originates (PL-16); durable outbound delivery; and a publication surface for `openpractice-ehr-clinical-facts/1.0`. Out of scope: billing, claims, receivables, accounting, coverage or guarantor data, appointment operations (openPractice owns the administrative appointment under ruling 31; appointment events are a later MINOR version), and any change to the ratified `expanded-patient-intake` requirements.
target_release: openPractice boundary v1. The change archives when a landed, validator-green open_chart revision meets three conditions: it passes contract tests for both contracts against an openPractice double at the recorded schema digests; it still passes the standalone golden-intake round trip with no openPractice installed; and it reports no billable facts until a governed clinical-encounter capability exists.
Status: draft
Ratified by: pending. The boundary decisions encoded here were made by Brett Heap on 2026-11-14 for the openPractice MVP (companion change `opensoft/openPractice-spec` `define-mvp-practice-foundation`). The ⚑ design calls of the first draft were ruled by Brett Heap on 2026-11-14, and rulings 87, 88, 89 and 93 on 2026-11-15. Two ⚑ design calls added on 2026-11-15, on established links, are not ruled (`design.md`, "Design calls for owner review"). All are recorded in `design.md` under "Owner rulings". Ratification still requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

openPractice is defining its MVP boundary with the EHR. Each system owns its own patient record, and the two records are linked. openPractice is the source of administrative demographics. Clinical facts for charge capture come from the EHR through versioned FHIR R4-compatible contracts.

openChart is the first EHR on the other side of that boundary. Its ratified `expanded-patient-intake` capability already provides:
- `OC Patient` as the local anchor;
- namespaced, versioned `OC Patient External Identifier` records;
- an identity-review state instead of merging;
- a versioned, authorized API;
- the rule that openChart operates without openPractice.

This change specifies openChart's half of both contracts. It uses the contract identifiers, versions, namespaces and issuer rules of the openPractice change, and validates against openPractice's canonical schemas, pinned by digest.

## What Changes

- **Link identity.** openChart configures a stable issuer and identifies its patients as (openChart issuer, `openchart`, `OC Patient` identifier). It stores openPractice's reference as (openPractice issuer, `openpractice`, value) in an `OC Patient External Identifier` row. Every message carries a `link_id`, and version counters are tracked per link. `OC Patient` stays the clinical anchor.
- **Canonical schemas.** openChart validates every message against openPractice's canonical schemas, pinned by SHA-256 digest (PL-04).
- **Link requests.** openChart accepts link requests only from a dedicated integration role, narrower than System Manager, that is named in planning. `link_existing` requests are checked deterministically against the built DocType: the projected name is normalized and compared, the date of birth must be equal, and an empty date of birth goes to review.
- **Identity review.** Conflicts go to identity review with a single resolver. Revocation wins. A second active `openpractice` link on one patient can never resolve as `confirmed`. Nothing is ever merged.
- **Demographic updates.** openChart applies them only on an active link. It acknowledges each update with one of `applied`, `duplicate`, `stale`, `rejected` or `identity_review`, and stores every applied version immutably. It projects the legal name and date of birth onto `OC Patient`, never overwrites `sex_recorded`, and never alters clinical or patient-reported content.
- **Date-of-birth changes.** A change to the date of birth suspends the link. Later versions are held. Confirming applies the latest held snapshot; rejecting sends `demographics.hold_rejected`.
- **Local edits.** Direct edits to the projected fields of a patient with an established link, one that has been active at least once, are refused, whether made by staff or by intake flows such as HealthLinc. They are routed to openPractice as `demographics.correction_requested` through that link. Intake submissions are still accepted. A link in identity review since its request has never been confirmed as the same person: it refuses no edit, carries no correction request, applies and projects nothing, and gives no communication instructions (⚑ design calls 1 and 2).
- **Revocations.** openChart accepts and sends `link.revoked`.
- **Outbound delivery and diagnostics.** Every outbound contract message uses a durable delivery mechanism, not site-local realtime events. Diagnostics carry no PHI.
- **Clinical facts.** openChart publishes billing-relevant facts with a capability result. Until a clinical-encounter capability exists, the capability result reports no billable facts. Patient-reported statements are never published as diagnoses. openChart owns no billing or accounting, and it still operates without openPractice.

## Capabilities

### New Capabilities

- `openpractice-patient-linkage` (PL-01 to PL-16): openChart's side of `openpractice-ehr-patient-link/1.0`.
- `openpractice-clinical-fact-publication` (CF-01 to CF-06): openChart's side of `openpractice-ehr-clinical-facts/1.0`.

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged.

## Impact

- **openChart:** issuer configuration; schema validation pinned by digest; versioned commands; a dedicated role; an extended identity decision; a demographic version store and projection; refusal of edits to projected fields for patients with an established link; durable outbound delivery; and a publication surface.
- **Dependencies:** openPractice is a consumer, never a prerequisite. Billable publication depends on a future openChart clinical-encounter capability.
- **Governance:** openChart's constitution is still the unfilled template. A Constitution Check, and with it the plan phase, needs a constitution adopted through separate governance first.
- **Safety:** synthetic fixtures only, no PHI in diagnostics, no clinical or autonomous authority, and no billing data.
- **Cross-reference:** companion change `opensoft/openPractice-spec` `define-mvp-practice-foundation` (EB-01 to EB-20), with identical contract identifiers, namespaces, issuer rules and schema digests.
