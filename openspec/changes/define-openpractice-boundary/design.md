## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Feature `001-expanded-patient-intake` built it under the archived change `add-expanded-patient-intake-foundation`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

This change touches these pieces of what is already built:

- **`OC Patient`** has `patient_name` (one required string), `date_of_birth` (optional), and `sex_recorded`. Records are named `OC-PAT-#####`, a sequence per site, so the same name can recur on two sites.
- **`OC Patient External Identifier`** has `patient`, `issuer_or_endpoint`, `namespace`, `value`, `status` (`active`, `superseded`, `revoked` or `identity_review`), an effective interval, `provenance` and `identifier_version`.
- **`open_chart.api.v1.register_external_identifier`** is gated to `System Manager`. Its decision, `open_chart.intake.core.identity_decision`, compares issuer and value only. It ignores `namespace` and does not detect a second active value on the same patient.
- **`emit_submission_event`** uses `frappe.publish_realtime`, which never leaves the site. It cannot carry contract messages.
- **No clinician-authored encounters, diagnoses or procedures exist.** Every statement in openChart is patient-reported.

The openPractice side is `opensoft/openPractice-spec` change `define-mvp-practice-foundation`, capability `ehr-boundary` (EB-01 to EB-20). That change owns the canonical schemas this change references by digest (PL-04).

Brett Heap ruled on 26 questions on 2026-11-14; they are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main`. There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. The plan phase waits on adopting a constitution.

## Owner rulings (2026-11-14)

Every row has the same source: **Brett Heap, 2026-11-14, authoring session.** Rows that govern only openPractice point to the companion change.

| # | Ruling | Governs |
|---|---|---|
| 1 | Handoff shape A (ordered multi-feature exception) | openPractice only |
| 2 | Accounting customers are the guarantor account and each payer | openPractice only |
| 3 | Customers are identified by account number only, never by name. **Superseded by ruling 25.** | openPractice only |
| 4 | Accounting dates (date of service, finalization date, statement terms, late charges) | openPractice only |
| 5 | Bank register, payer deposit links, deposit-only reconciliation | openPractice only |
| 6 | BAA attestation for a practice-operated destination | openPractice only |
| 7 | Posting mode is fixed before the first released batch | openPractice only |
| 8 | ERPNext is reached through its REST API only | openPractice only |
| 9 | Hard delete for records created in error | openPractice only |
| 10 | Confidential-communication instructions are in the registry and carried in the link snapshot | PL-09 (stored in the applied-version record) |
| 11 | Preferred language added; sex assigned at birth and sexual orientation stay out, being clinical facts owned by openChart | PL-09; CF-05 (openChart keeps the clinical attributes) |
| 12 | Tier 4 only for hard delete and `customer-detail` enablement; `link_existing` and review resolution at tier 2 | openPractice only (openChart has no governance tiers) |
| 13 | Coverage is not in link contract 1.0 | CF-05 |
| 14 | The date-of-birth hold is accepted, as a link-level suspension | PL-08 |
| 15 | The "agree" check is made deterministic against the built DocType | PL-05 |
| 16 | Applied name and date of birth are projected onto `OC Patient` with history; `sex_recorded` is never overwritten | PL-09 |
| 17 | openChart refuses direct edits to a linked patient's projected fields and routes them to openPractice as correction requests, intake flows included | PL-10 |
| 18 | The integration role is named and scoped in planning, narrower than System Manager | PL-05 |
| 19 | Namespace tokens `openpractice` and `openchart` are confirmed | PL-02, PL-03 |
| 20 | Zero or more coverages | openPractice only |
| 21 | Manual charge entry is allowed for a linked patient while the EHR reports no billable-facts capability | CF-06 |
| 22 | Accrual valuation with an expected contractual adjustment | openPractice only |
| 23 | Full bank numbers are encrypted and role-restricted | openPractice only |
| 24 | Membership, subscription and retail invoicing are out of the MVP accounting contract's scope | openPractice only |
| 25 | Medical-billing customers may carry name and billing contact in the accounting destination after its BAA gate, in `customer-detail` mode only (supersedes ruling 3) | openPractice only |
| 26 | Posting mechanics belong to `define-mvp-practice-foundation`; customer roles, offering routes and obligation ownership belong to openPractice change `define-customer-financial-data-boundaries` | openPractice only |

The accounting posting modes are named `summary-journal` and `customer-detail` in all three changes. None of rulings 24 to 26 alters either EHR contract or its schema digest.

## Goals / Non-Goals

**Goals:**

- Implement openChart's half of `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0` against openPractice's canonical schemas, verified by digest.
- Keep every ratified `expanded-patient-intake` requirement intact, and keep `OC Patient` as the clinical anchor.
- Make wrong-patient propagation hard. The safeguards are:
  - a deterministic "agree" check;
  - a link-level suspension when the date of birth changes;
  - a single resolver for each review;
  - refusal to edit projected fields locally, with corrections routed to openPractice.
- Keep openChart free of billing, accounting, coverage and guarantor data.

**Non-Goals:**

- Building clinician encounters.
- Synchronizing appointments (R-7).
- Sending demographic updates to openPractice.
- Changing any ratified text.
- Adopting the constitution inside this change.

## Decisions

### 1. Link identity

- **The openPractice reference** is stored as (openPractice issuer, `openpractice`, openPractice patient identifier) (PL-02).
- **openChart's own identity** is (openChart issuer, `openchart`, `OC-PAT-#####`) (PL-03). Each openChart deployment configures a stable issuer that is unique across deployments, so the per-site sequence never collides.
- **Every message carries the `link_id`** that openPractice minted. Versions are compared per `link_id`.

### 2. The integration role and link requests

A dedicated integration role, narrower than `System Manager`, is named and scoped in planning (ruling 18). Planning also chooses whether `register_external_identifier` is extended or wrapped.

**The deterministic "agree" check** (PL-05):

1. Project the snapshot's structured legal name using the canonical schema's projection: given names, then the family name, then the suffix, joined by single spaces.
2. Normalize both the projected name and `OC Patient.patient_name`: Unicode NFKC, case folding, trimming, and collapsing internal whitespace to one space.
3. Compare the two strings, and compare the dates of birth for exact equality.

An empty `date_of_birth` sends the link to identity review.

### 3. Identity review

There are two conflict cases (PL-06). The second, a second active value from the same issuer on one patient, extends today's `identity_decision`, which planning must make namespace-aware. Under ruling-aligned EB-05 and PL-06:

- the side that raised a review is its only resolver;
- revocation wins over confirmation;
- case 2 can never resolve as `confirmed`.

### 4. Applying demographics and projecting them

- Each applied version is stored immutably.
- Name and date of birth are projected onto `OC Patient`, with history kept.
- The other administrative attributes live in the version record, including preferred language and confidential-communication instructions (rulings 10, 11 and 16).
- `sex_recorded` is never overwritten.
- The storage shape (a new DocType or child rows) is decided in planning.

### 5. The date-of-birth suspension

This replaces the earlier hold on single updates (PL-08, ruling 14, review B2). A hold starts whenever an incoming snapshot's date of birth differs from the date of birth currently applied. It does not depend on the previous version, so no later full snapshot can bypass it. While a hold is open, the link status is `identity_review` and every later version is held.

| Outcome | Effect |
|---|---|
| Confirm | Apply the latest held snapshot and send `link.review_resolved` with outcome `confirmed` |
| Reject | Apply nothing, return the link to `active`, and send `demographics.hold_rejected` |

openPractice suspends its own delivery for the link until the hold is confirmed, or until its staff correct or re-assert the value. There is no deadlock: confirmation applies the newest held version, and resuming after a rejection needs a deliberate human act.

### 6. Refusing local edits and routing corrections

This closes the former Open Question 3 (ruling 17, PL-10). Direct edits to a linked patient's `patient_name` or `date_of_birth` are refused, whether they come from openChart staff or from intake flows such as HealthLinc. Each refused edit is sent to openPractice as a `demographics.correction_requested` message. openPractice acknowledges it (`correction.ack`) and later reports the outcome (`correction.resolved`); an applied correction comes back as a new demographic version.

An intake submission is still accepted and persisted under the ratified intake requirements. Only the change to the projected fields is withheld.

### 7. Durable outbound delivery

This removes the reliance on `oc_intake_submission_update` (review m10, PL-14). Every message openChart sends goes through a durable store that commits in the same transaction as its cause, with retries that reuse the `message_id`. The mechanism is decided in planning. `frappe.publish_realtime` cannot carry contract messages, because it is site-local.

### 8. Clinical-fact publication

- **Contents:** pointer-only notifications, a capability result, and reads of the billing subset, with codings carrying a system and code only (CF-01 to CF-04).
- **Billable-facts support:** until a clinical-encounter capability exists, the capability result is false and reads return `no_billable_facts` (CF-06). openPractice then enters charges manually, marked manual (ruling 21).
- **No billing data:** openChart produces no billing data (CF-05), and holds no coverage (ruling 13).

### 9. Standalone operation

Every new component is optional (PL-15). The standalone golden-intake tests remain the regression gate.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which must operate without openPractice | PL-15 restates it. Every boundary component is optional. |
| External identifiers must not replace the openChart identifier or merge patients | PL-01, PL-02 and PL-06. Conflicts go to review, never to a merge. |
| Intake submissions are versioned, auditable and idempotent | PL-10 keeps every intake submission accepted. Only projected-field changes are routed to openPractice. |
| Statements preserve reported detail | Untouched (PL-09). |
| Amendments preserve accepted history | Applied versions are immutable, and prior values are kept. |
| APIs and hooks are authorized and versioned | The dedicated integration role is scoped by subject, tenant, purpose and role (PL-05). Contracts are versioned by MAJOR version and schema digest (PL-04, PL-12). |
| Intake confers no clinician or autonomous authority | CF-02. Demographic updates are human-authored administrative changes made in openPractice. |

**No conflict with ratified openChart text was found.** PL-10 refuses local edits to `patient_name` and `date_of_birth` for linked patients only. The ratified text does not require openChart to accept such edits, so no ratified text is changed.

## Risks / Trade-offs

- **[Wrong-patient propagation]** → Mitigated by the deterministic "agree" check, the date-of-birth suspension, single-resolver review, and the edit refusal.
- **[Staff frustration at refused edits]** → The correction path is explicit, and each request is acknowledged and resolved by openPractice.
- **[Over-privileged integration]** → A dedicated role, narrower than `System Manager`.
- **[Contract drift]** → Schemas are compared by digest (PL-04). Both changes' task 1.3 checks them.
- **[Lost outbound messages]** → Durable outbound store (PL-14).
- **[Publication before encounters exist]** → A false capability result and `no_billable_facts`; patient-reported statements are never substituted.
- **[No constitution]** → The plan phase is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly. Brett Heap stamps `Ratified by` and sets `Status: ratified`.
2. Adopt openChart's constitution through separate governance.
3. Create the single Spec Kit feature from the assembly root.
4. Implement:
   - issuer configuration;
   - schema validation pinned to the recorded digests;
   - the integration role and link commands;
   - the namespace-aware identity decision;
   - the version store and projection;
   - the date-of-birth suspension;
   - edit refusal and correction requests;
   - durable outbound delivery;
   - a publication surface that reports no billable facts.

   Contract tests run against an openPractice double, alongside the standalone regression suite.
5. Land the leg pull requests and the root pin bump, then archive.
6. Rollback: revoke links and disable the role. Never delete identifier rows or demographic history.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks the plan phase.
2. **Clinical-encounter capability.** Which governed change introduces clinician-authored encounters, diagnoses and procedures? This blocks billable publication (CF-06) and openPractice Feature 4's live interoperation.
3. **Appointment authority (R-7).** Still open in openPractice. No openChart requirement depends on it, because the 1.0 contracts carry no appointment operations.
