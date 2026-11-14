code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: a namespaced openPractice link carried as `OC Patient External Identifier` rows; link-request and demographic-update endpoints under the versioned contract `openpractice-ehr-patient-link/1.0`; an extension of identity review; an immutable store of applied administrative demographic versions; and a publication surface for `openpractice-ehr-clinical-facts/1.0`. Out of scope: billing, claims, receivables, accounting, coverage or guarantor data, appointment synchronization, and any change to the ratified `expanded-patient-intake` requirements.
target_release: openPractice boundary v1. Archives when a landed, validator-green open_chart revision passes contract tests for both contracts against an openPractice contract double, still passes the standalone golden intake round trip with no openPractice installed, and publishes no billable clinical fact until a governed clinical-encounter capability exists.
Status: draft
Ratified by: pending. The decisions encoded here were made by Brett Heap on 2026-11-14 for the openPractice MVP (companion change `opensoft/openPractice-spec` `define-mvp-practice-foundation`). This artifact is agent-drafted and is not ratified until Brett Heap stamps this line and changes `Status` to `ratified`.

## Why

openPractice is defining its MVP boundary with the electronic health record (EHR): each system owns its own patient record, and the two records are linked. openPractice is the source of administrative demographics. Clinical facts for charge capture come from the EHR through versioned FHIR R4-compatible contracts.

openChart is the first EHR on the other side of that boundary. Its ratified `expanded-patient-intake` capability already holds the pieces this needs:
- `OC Patient` as the local patient anchor;
- versioned, namespaced `OC Patient External Identifier` records;
- an identity-review state instead of merging;
- a versioned, authorized API;
- the rule that openChart operates without openPractice.

What openChart lacks is a governed statement of how it accepts an openPractice link and openPractice's demographic updates, and what it publishes back. Without one, openPractice and openChart would each define half of the same contract. This change specifies openChart's half, using the same contract names, versions and namespaces as the openPractice change.

## What Changes

- **The openPractice link.** openChart stores the openPractice patient reference as an `OC Patient External Identifier` row with namespace **`openpractice`**, the openPractice deployment's issuer identifier as `issuer_or_endpoint`, and the openPractice patient identifier as `value`. Statuses use the existing vocabulary (`active`, `superseded`, `revoked`, `identity_review`). `OC Patient` stays the clinical anchor.
- **Link requests.** openChart accepts `link.request` messages (`create_new` or `link_existing`) under **`openpractice-ehr-patient-link/1.0`**, only from an integration identity authorized for subject, tenant, purpose and role. It answers each with `linked`, `identity_review` or `refused`, and never links by its own matching.
- **Identity review.** A conflicting link enters identity review and is never merged. Review covers two cases: the openPractice reference is already active on another patient, or the target patient already holds a different active openPractice reference from the same issuer. The second case extends today's identity decision, which compares issuer and value only.
- **Demographic updates.** openChart applies openPractice's demographic updates only on an active link and only through the contract. It stores each applied version immutably with provenance and keeps prior values. It answers each update with `applied`, `duplicate`, `stale`, `rejected` or `identity_review`, and holds any change of date of birth for review.
- **What updates touch.** Administrative demographics never overwrite intake submissions, patient-reported statements or clinical records, and never overwrite `OC Patient.sex_recorded`.
- **Clinical facts.** openChart publishes billing-relevant clinical facts under **`openpractice-ehr-clinical-facts/1.0`**: pointer-only notifications plus authorized FHIR R4-compatible reads of Encounter, encounter-diagnosis Condition and Procedure, with a documentation-final indicator. Patient-reported statements are never published as diagnoses or procedures.
- **No billing.** openChart owns no billing or accounting and receives no guarantor, coverage or financial data.
- **Standalone operation.** openChart continues to operate without openPractice.

## Capabilities

### New Capabilities

- `openpractice-patient-linkage`: openChart's side of `openpractice-ehr-patient-link/1.0`. It covers the namespaced link, link requests, identity review without merge, applying demographic versions with provenance, the date-of-birth hold, protection of clinical and patient-reported content, one-way demographics in 1.0, contract versioning, and standalone operation.
- `openpractice-clinical-fact-publication`: openChart's side of `openpractice-ehr-clinical-facts/1.0`. It covers the billing-relevant fact publication surface, final-only billability, minimum necessary data with no database access, forward corrections, no billing ownership, and an explicit no-billable-facts result until a governed clinical-encounter capability exists.

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and kept unchanged. This change adds requirements beside them and modifies none of their text.

## Impact

- **openChart:** a new namespace convention for `openpractice`; new versioned API commands for link requests, link-review resolution and demographic updates; an extension of the identity decision; a store of administrative demographic versions; a publication surface; and a scoped integration role in place of the `System Manager` gate that `register_external_identifier` uses today.
- **Dependencies:** openPractice is a consumer, never a prerequisite. Billable clinical-fact publication depends on a future, separately governed openChart clinical-encounter capability.
- **Governance:** openChart's `.specify/memory/constitution.md` in the assembly root is still the unfilled template. A meaningful Constitution Check, and therefore this change's Speckit plan phase, needs a constitution adopted through separate governance first.
- **Safety:** synthetic fixtures only (`SYN-` discipline), no real PHI, no clinical or autonomous authority, and no billing data.
- **Cross-reference:** companion change `opensoft/openPractice-spec`, change `define-mvp-practice-foundation`. That change's `ehr-boundary` capability states openPractice's side, with the identical contract identifiers `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0` and the identical namespaces `openpractice` and `openchart`.
