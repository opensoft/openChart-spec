## Context

openChart is an original Frappe v15 application (`open_chart`, in `opensoft/openChart-code`). Feature `001-expanded-patient-intake` built it under the archived change `add-expanded-patient-intake-foundation`. Its canonical capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md), which was ratified. These are the built pieces this change touches:

- `OC Patient` has `patient_name`, `date_of_birth` and `sex_recorded`, and is named `OC-PAT-#####`.
- `OC Patient External Identifier` has `patient`, `issuer_or_endpoint`, `namespace`, `value`, `status` (`active`, `superseded`, `revoked`, `identity_review`), `effective_start`, `effective_end`, `provenance` and `identifier_version`.
- `open_chart.api.v1.register_external_identifier` writes identifier rows. It is gated to `System Manager`. Its decision, `open_chart.intake.core.identity_decision`, sends a row to `identity_review` when an active row with the same `issuer_or_endpoint` and `value` belongs to another patient. It does not consider `namespace`, and it does not detect a second active value for the same patient.
- The vendored identity binding in the code leg's `tests/fixtures/medx/` uses the product-name token convention `identifier_namespace: openchart`.
- openChart has no clinician-authored encounter, diagnosis or procedure records. Its statements are patient-reported only.

On 2026-11-14 Brett Heap decided the openPractice MVP boundary. These are the parts that bind openChart:
- each system owns its own patient record, and the records are linked;
- openChart stores the openPractice reference as an `OC Patient External Identifier` with a defined namespace;
- openPractice is the source of administrative demographic changes and publishes them through a versioned contract;
- neither system merges the other's records;
- a link conflict goes to identity review;
- the clinical facts openPractice needs come from the EHR through versioned FHIR R4-compatible contracts;
- openChart works without openPractice.

The openPractice side is governed by `opensoft/openPractice-spec`, change `define-mvp-practice-foundation`, capability `ehr-boundary`. That change's `design.md` (Decisions 4 and 5) holds the full message catalogue that this design implements.

**Constitution status.** openChart's `.specify/memory/constitution.md` in the assembly root `opensoft/openChart` is the unfilled Spec Kit template on `main`. There is no ratified constitution to check against. This design therefore checks consistency against openChart's `AGENTS.md` (repository role, safety and data rules) and the ratified `expanded-patient-intake` requirements. A meaningful Constitution Check, and so this change's Speckit plan phase, waits on a constitution adopted through separate governance.

## Goals / Non-Goals

**Goals:**

- Implement openChart's half of `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0`, with identifiers, versions and namespaces identical to the openPractice change.
- Keep every ratified `expanded-patient-intake` requirement intact, and keep `OC Patient` as the clinical anchor.
- Make wrong-patient propagation hard: human confirmation happens on the openPractice side, demographic agreement is checked here, a date-of-birth change is held, and a conflict never merges.
- Keep openChart free of billing, accounting, coverage and guarantor data.

**Non-Goals:**

- Building clinician encounters, diagnoses or procedures. That needs a separate governed capability.
- Synchronizing appointments. Authority over appointments is open as R-7 in the openPractice change.
- Sending demographics from openChart to openPractice under 1.0.
- Changing the text of any ratified requirement.
- Adopting openChart's constitution inside this change.

## Decisions

### 1. The link is an `OC Patient External Identifier` in namespace `openpractice`

The openPractice patient reference is stored as `namespace = openpractice`, `issuer_or_endpoint = <openPractice deployment issuer>` and `value = <openPractice patient identifier>`. This follows the existing product-name token convention (`openchart` in the vendored binding). openPractice stores the reverse reference under namespace `openchart`, with the `OC Patient` identifier as the value.

The issuer is a stable identifier that each openPractice deployment configures. It keeps two deployments from colliding on the same value. Provenance names the contract and the message identifier.

*Design call for owner review:* the tokens `openpractice` and `openchart`. They are identical in both changes.

### 2. Link requests, authorization and the integration role

Link requests arrive through new versioned commands in `open_chart.api.v1`. Exact names are chosen in planning.
- `create_new` creates an `OC Patient` from the snapshot.
- `link_existing` links the named patient only when name and date of birth agree. "Agree" is proposed as an exact match of date of birth and of the legal name parts present (family name and first given name, or a single name), after case and whitespace normalization. Anything else goes to identity review. openChart never links on its own matching.

The ratified API requirement demands authorization by subject, tenant, purpose and role. The `System Manager` gate on today's `register_external_identifier` is too broad for a standing integration identity, so planning must introduce a scoped integration role. *Design call:* the role, its permissions, and whether `register_external_identifier` is extended or wrapped.

### 3. Identity review beyond today's decision

Two conditions put a link in review:
1. the openPractice issuer and value are already active on another `OC Patient`. Today's `identity_decision` already covers this;
2. the target `OC Patient` already holds an active `openpractice` identifier from the same issuer with a different value. This is new, and it catches duplicate patients on the openPractice side.

Planning extends the decision so that it is namespace-aware. Review resolution is `confirmed` or `revoked`, is recorded, and is reported to openPractice. Nothing merges.

### 4. Applied demographic versions and their projection

openChart stores each applied `demographics.updated` version immutably. Each record carries the full administrative snapshot, `demographic_version`, the message identifier, issuer, actor reference, source and reason. The acknowledgement semantics are identical to the openPractice change: `applied`, `duplicate`, `stale`, `rejected` and `identity_review`.

The applied legal name and date of birth are projected onto `OC Patient.patient_name` and `OC Patient.date_of_birth`, with history kept in the version records. Gender identity, pronouns, telecom and addresses live in the administrative version record.

*Design calls:*
- projecting onto `OC Patient` rather than keeping the administrative demographics wholly separate;
- the storage shape (a new DocType versus child rows), decided in planning.

### 5. Date-of-birth changes are held

A date-of-birth change is the strongest signature of a link to the wrong patient. openChart holds such an update in identity review until an authorized openChart user confirms it, and acknowledges it as `identity_review`. Name, sex, gender, pronoun and contact changes apply directly, with provenance. *Design call for owner review:* this hold goes beyond the decision that openPractice is the source. It confirms the link rather than overriding the source.

### 6. `sex_recorded` is left alone

`OC Patient.sex_recorded` has no documented semantics in openChart's specs or contracts, and it may carry the intake's recorded value. Administrative sex from openPractice is therefore stored in the administrative version record and does not overwrite `sex_recorded`. Whether the two should be mapped is open.

### 7. Clinical-fact publication

The publication surface has two parts:
- pointer-only notifications, following the pattern of today's pointer-only `oc_intake_submission_update` event, which carries no clinical content;
- authorized FHIR R4-compatible reads of Encounter, encounter-diagnosis Condition and Procedure, with a documentation-final indicator. Notes, medications, results and orders are excluded.

Codes are published as code-system identifiers and values only. Fixtures use synthetic or license-free codes, so no licensed descriptor text enters the repository.

Until a governed clinical-encounter capability exists, reads return an explicit no-billable-facts result. Patient-reported statements are never substituted: the ratified intake spec forbids treating them as diagnoses.

### 8. No billing, accounting, coverage or guarantor data

openChart produces no ChargeItem or Claim resources under this contract. It holds no receivables and integrates with no accounting system. The openPractice link carries no guarantor, coverage or financial data.

### 9. Standalone operation is preserved

Every new command and store is optional. A site with no openPractice link behaves exactly as today, and the standalone golden-intake tests remain the regression gate.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| openChart provides an original standalone Frappe application, and MUST operate without MedxFactory, MedxEHR or openPractice | Requirement "openChart operates without openPractice" restates it. Every boundary component is optional. |
| Patient identity records retain external namespaces. An external identifier MUST NOT replace the openChart patient identifier or silently merge patients | The openPractice reference is exactly such an identifier. Conflicts go to `identity_review`, never to a merge. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Demographic updates never alter submissions. |
| Medication, supplement and other statements preserve reported detail | Untouched. Administrative updates never alter statements. |
| Amendments preserve accepted history | Applied demographic versions are immutable, and prior values stay retrievable. |
| APIs and extension hooks are authorized and versioned | New commands are versioned and gated by subject, tenant, purpose and role, through a scoped integration role. |
| Intake does not confer clinician or autonomous authority | Patient-reported statements are never published as diagnoses or procedures. Demographic updates are human-authored administrative changes from openPractice, not clinical acts. |

**No conflict between Brett Heap's 2026-11-14 decisions and ratified openChart text was found.** The tensions below are recorded instead, and no ratified text is changed.

## Risks / Trade-offs

- **[A wrong-patient link propagates demographics]** → `link_existing` is confirmed by a human in openPractice and checked for demographic agreement here. Date-of-birth changes are held. Conflicts go to review.
- **[openPractice-sourced demographics diverge from a value an openChart user or an intake flow sets locally]** → The local-edit policy for linked patients is open (Open Question 3). Applied versions keep full history either way.
- **[The integration identity is over-privileged]** → Planning replaces the `System Manager` gate with a scoped role.
- **[The contracts drift between the two repositories]** → Identical identifiers in both changes, contract tests on both sides, and rejection of unsupported MAJOR versions.
- **[The publication contract ships before encounters exist]** → An explicit no-billable-facts result, and never substitution from intake.
- **[Planning starts without a constitution]** → The tasks block the plan phase until openChart's constitution is adopted.

## Migration Plan

1. Strictly validate this change. Brett Heap ratifies it by stamping `Ratified by` and setting `Status: ratified` in `proposal.md`.
2. Adopt openChart's constitution through separate governance.
3. Create the single openChart Spec Kit feature for this change, from the assembly root.
4. Implement: the namespace convention; the link commands and scoped role; the namespace-aware identity decision; the demographic version store and projection; the date-of-birth hold; and the publication surface returning no billable facts. Contract tests run against an openPractice double, and the standalone golden-intake regression tests run alongside.
5. Land the code and spec leg PRs and the assembly pin bump. Archive this change, and promote the two capabilities, only after landing.
6. Roll back by revoking links and disabling the integration role. Identifier rows, applied versions and audit history stay. Never roll back by deleting identifiers or demographic history.

## Open Questions

Items marked ⚑ are design calls this change made beyond Brett Heap's decisions.

1. **Constitution.** openChart's constitution is the unfilled template. Who adopts it, and when? This blocks the plan phase.
2. ⚑ **Date-of-birth review hold** (Decision 5). Confirm.
3. **Local edits for linked patients.** If an openChart user, or an intake flow such as HealthLinc, changes the name of a patient linked to openPractice, does openChart refuse the edit, record it as a local divergence, or let the next openPractice version overwrite it? The ratified intake text does not address this. Brett Heap's decision makes openPractice the source of administrative changes.
4. ⚑ **`sex_recorded`** (Decision 6). Should administrative sex ever map onto it?
5. ⚑ **Projection onto `OC Patient`** (Decision 4). Confirm, or keep the administrative demographics wholly separate.
6. ⚑ **Integration role** (Decision 2). Its name and permissions, and whether `register_external_identifier` is extended or wrapped.
7. **Clinical-encounter capability.** Which governed openChart change introduces clinician-authored encounters, diagnoses and procedures? Billable publication waits on it.
8. **Appointment authority** (openPractice R-7). Open; this change carries no appointment operations.
9. ⚑ **Namespace tokens** `openpractice` and `openchart`. Confirm.
10. ⚑ **Definition of "agree"** for `link_existing` (Decision 2). Confirm.
