## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Feature `001-expanded-patient-intake` built it under the archived change `add-expanded-patient-intake-foundation`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

This change touches these pieces of what is already built:

- **`OC Patient`** has `patient_name` (one required string), `date_of_birth` (optional), and `sex_recorded`. Records are named `OC-PAT-#####`, a sequence per site, so the same name can recur on two sites.
- **`OC Patient External Identifier`** has `patient`, `issuer_or_endpoint`, `namespace`, `value`, `status` (`active`, `superseded`, `revoked` or `identity_review`), an effective interval, `provenance` and `identifier_version`.
- **`open_chart.api.v1.register_external_identifier`** is gated to `System Manager`. Its decision, `open_chart.intake.core.identity_decision`, compares issuer and value only. It ignores `namespace` and does not detect a second active value on the same patient.
- **`emit_submission_event`** uses `frappe.publish_realtime`, which never leaves the site. It cannot carry contract messages.
- **No clinician-authored encounters, diagnoses or procedures exist.** Every statement in openChart is patient-reported.

The openPractice side is `opensoft/openPractice-spec` change `define-mvp-practice-foundation`, capability `ehr-boundary` (EB-01 to EB-20). That change owns the canonical schemas this change references by digest (PL-04).

Brett Heap ruled on 33 questions on 2026-11-14; they are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main`. There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. The plan phase waits on adopting a constitution.

## Owner rulings (2026-11-14 and 2026-11-15)

Rows 1 to 33 have the same source: **Brett Heap, 2026-11-14, authoring session.** Rows 87, 88, 89 and 93 come from **Brett Heap, 2026-11-15**, who answered decisions 79 to 98 with "accept recomendations. on all but 80. for 80 explain that more". Each of those rows records the recommended form he accepted. Rows that govern only openPractice point to the companion change. Rulings are not ratification.

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
| 10 | Confidential-communication instructions are in the MVP registry and carried in the link snapshot. | PL-09 (stored in the applied-version record) |
| 11 | Preferred language added; sex assigned at birth and sexual orientation stay out, being clinical facts owned by openChart | PL-09; CF-05 (openChart keeps the clinical attributes) |
| 12 | Tier 4 only for hard delete and `customer-detail` enablement; `link_existing` and review resolution at tier 2 | openPractice only (openChart has no governance tiers) |
| 13 | Coverage is not in link contract 1.0 | CF-05 |
| 14 | The date-of-birth hold is accepted, as a link-level suspension | PL-08 |
| 15 | The "agree" check is made deterministic against the built DocType | PL-05 |
| 16 | Applied name and date of birth are projected onto `OC Patient` with history; `sex_recorded` is never overwritten | PL-09 |
| 17 | openChart refuses direct edits to a linked patient's projected fields and routes them to openPractice as correction requests, intake flows included | PL-10, for a patient with an established link (⚑ design call 1) |
| 18 | The integration role is named and scoped in planning, narrower than System Manager | PL-05 |
| 19 | Namespace tokens `openpractice` and `openchart` are confirmed | PL-02, PL-03 |
| 20 | Zero or more coverages | openPractice only |
| 21 | Manual charge entry is allowed for a linked patient while the EHR reports no billable-facts capability | CF-06 |
| 22 | Accrual valuation with an expected contractual adjustment | openPractice only |
| 23 | Full bank numbers are encrypted and role-restricted | openPractice only |
| 24 | Membership, subscription and retail invoicing are out of the MVP accounting contract's scope | openPractice only |
| 25 | Medical-billing customers may carry name and billing contact in the accounting destination after its BAA gate, in `customer-detail` mode only (supersedes ruling 3) | openPractice only |
| 26 | Posting mechanics belong to `define-mvp-practice-foundation`; customer roles, offering routes and obligation ownership belong to openPractice change `define-customer-financial-data-boundaries` | openPractice only |
| 27 | Confidential-communication instructions stay in the link snapshot. openChart, and anything it drives (for example HealthLinc), must honor them for every patient communication it originates. This settles re-review finding N6. | PL-16, with instructions taken from an established link only (⚑ design call 2) |
| 28 | The accounting default is `summary-journal`; `customer-detail` is a per-destination opt-in behind the BAA gate | openPractice only |
| 29 | openPractice is the source for administrative demographics and publishes them to a linked EHR; each system owns its own record | Boundary: PL-07, PL-09 (unchanged) |
| 30 | Net revenue is the constrained expected entitlement, estimated at the date of service and re-estimated at each close (supersedes ruling 22) | openPractice only |
| 31 | openPractice is the system of record for the administrative appointment; the EHR owns the encounter and keeps an appointment reference if needed. The 1.0 contracts carry no appointment operations; appointment events are a future MINOR version. This closes R-7. | Boundary: Non-goals, Open Question 3 |
| 32 | One Party with roles; "customer" is a party role only for membership and retail buyers, and a medical-billing accounting customer is derived from the guarantor or payer role | openPractice only |
| 33 | FD-5 governs sign-offs; where a tier calls for an approval, release decision or attestation, a named human or an opted-in named AI agent with an openWallet ID may sign; tier 4 stays human-only | openPractice only. openChart's identity-review resolution stays with its authorized user. |
| 87 | (2026-11-15) Which diagnoses openChart publishes to openPractice: "Only confirmed ones. If a published diagnosis is later refuted, a retraction is sent." | CF-01 (only `confirmed` encounter diagnoses are published), CF-04 (a refuted published diagnosis is retracted). The mechanism is `define-clinical-acts-foundation`'s publication capability. |
| 88 | (2026-11-15) Whether retractions are delivered after a patient link is revoked or superseded: "Yes. Retractions of facts already published under that link are delivered, as pointers only. No new facts and no reads are served. Otherwise openPractice keeps billing withdrawn facts." | CF-01's one exception to its active-link limit, and CF-04. No new fact is published and no read is served on such a link. This is consistent with `define-clinical-acts-foundation`, which recorded the exception as its tension CT-15. |
| 89 | (2026-11-15) "Add a retraction reason code to the contract now, while 1.0 is still unratified. That is a small follow-up PR in openPractice-spec…" The rest of the ruling concerns an erratum elsewhere and does not touch this change. | CF-04. The code is added to `openpractice-ehr-clinical-facts/1.0` itself, not to a later MINOR version, and the follow-up change of ruling 93 carries it. The PL-04 pin of `openpractice-ehr-clinical-facts/1.0` stays at its recorded digest until that follow-up lands. This change then re-pins (task 1.4). |
| 93 | (2026-11-15) Whether one follow-up pull request to `opensoft/openPractice-spec` should update the merged, unratified openPractice drafts: "Yes, one draft PR carrying: the agent operations Hermes lacks and the consent check; a verifiable entitlement; a clinician-acknowledged status; the representative's relationship and authority; the retraction reason code…" | Here, only for the retraction reason code of ruling 89. The follow-up is being drafted by another author (`opensoft/openPractice-spec` PR #7). This change's own position until it lands: a retraction is sent as today, without a reason code, and the PL-04 pins stand. |

The accounting posting modes are named `summary-journal` and `customer-detail` in all three changes. None of rulings 24 to 33, 87, 88 or 93 alters either EHR contract or its schema digest, and the PL-04 pins are unchanged. Ruling 89 will alter `openpractice-ehr-clinical-facts` through the ruling-93 follow-up, not through this change. Ruling 27 adds PL-16, and ruling 31 settles appointment authority without adding any operation.

## Goals / Non-Goals

**Goals:**

- Implement openChart's half of `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0` against openPractice's canonical schemas, verified by digest.
- Keep every ratified `expanded-patient-intake` requirement intact, and keep `OC Patient` as the clinical anchor.
- Make wrong-patient propagation hard. The safeguards are:
  - a deterministic "agree" check;
  - a link-level suspension when the date of birth changes;
  - a single resolver for each review;
  - refusal to edit projected fields locally, with corrections routed to openPractice;
  - nothing applied, projected or routed through a link that has never been confirmed.
- Keep openChart free of billing, accounting, coverage and guarantor data.

**Non-Goals:**

- Building clinician encounters.
- Appointment operations under the 1.0 contracts. Ruling 31 makes openPractice the appointment's system of record; openChart owns the encounter and may keep an appointment reference.
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
- case 2 can never resolve as `confirmed`;
- `revoked` and `superseded` are terminal. No confirmation, hold resolution or link request makes such a link `active` again, and a revocation or supersession cancels an open hold (⚑ design call 4).

**Established links (⚑ design call 1).** A link in `identity_review` is in one of two positions. An established link, one that has been `active` at least once, is in review while a date-of-birth change is held (PL-08). A link in review since its request, after a failed agree check (PL-05) or a conflict (PL-06), has never been established. Only an established link carries anything (PL-02):
- edit refusals and correction requests (PL-10);
- applied and projected demographics (PL-07 to PL-09);
- confidential-communication instructions (PL-16).

A link that has never been established refuses no edit, receives updates without applying or holding them, projects nothing and routes nothing.

**Confirming a link that has never been established (⚑ design call 3).**
- The link becomes established at the moment of confirmation, and only then do snapshots apply.
- The reviewer confirms against the latest snapshot received on the link, read side by side with the `OC Patient`. openChart applies exactly that snapshot, never one received before the confirmation that the reviewer did not read.
- `link.review_resolved` carries its version as `applied_version`. A later snapshot waits for openPractice's next publication (PL-06).

### 4. Applying demographics and projecting them

- Each applied version is stored immutably.
- Name and date of birth are projected onto `OC Patient`, with history kept.
- The other administrative attributes live in the version record, including preferred language and confidential-communication instructions (rulings 10, 11 and 16).
- `sex_recorded` is never overwritten.
- The storage shape (a new DocType or child rows) is decided in planning.

### 5. The date-of-birth suspension

This replaces the earlier hold on single updates (PL-08, ruling 14, review B2). A hold starts whenever an incoming snapshot's date of birth differs from the date of birth currently applied. It does not depend on the previous version, so no later full snapshot can bypass it. While a hold is open, the link status is `identity_review` and every later version is held. A hold arises only on an established link, which has a date of birth applied.

| Outcome | Effect |
|---|---|
| Confirm | Apply the latest held snapshot and send `link.review_resolved` with outcome `confirmed` |
| Reject | Apply nothing, return the link to `active`, and send `demographics.hold_rejected` |

Both outcomes first re-check the link. A link that is revoked or superseded keeps that status, because its hold was cancelled when it ended, and nothing is applied or sent (⚑ design call 4).

openPractice suspends its own delivery for the link until the hold is confirmed, or until its staff correct or re-assert the value. There is no deadlock: confirmation applies the newest held version, and resuming after a rejection needs a deliberate human act.

### 6. Refusing local edits and routing corrections

This closes the former Open Question 3 (ruling 17, PL-10). Direct edits to the `patient_name` or `date_of_birth` of a patient with an established link are refused, whether they come from openChart staff or from intake flows such as HealthLinc. Each refused edit is sent to openPractice as a `demographics.correction_requested` message through the established link. A link in review since its request has never been confirmed as the same person, and a request aimed at the wrong patient sits in exactly that state. Such a link refuses no edit and carries no correction request, so this patient's demographic changes never reach an unrelated openPractice record (⚑ design call 1). openPractice acknowledges it (`correction.ack`) and later reports the outcome (`correction.resolved`); an applied correction comes back as a new demographic version.

An intake submission is still accepted and persisted under the ratified intake requirements. Only the change to the projected fields is withheld.

### 7. Durable outbound delivery

This removes the reliance on `oc_intake_submission_update` (review m10, PL-14). Every message openChart sends goes through a durable store that commits in the same transaction as its cause, with retries that reuse the `message_id`. The mechanism is decided in planning. `frappe.publish_realtime` cannot carry contract messages, because it is site-local.

### 8. Clinical-fact publication

- **Contents:** pointer-only notifications, a capability result, and reads of the billing subset, with codings carrying a system and code only (CF-01 to CF-04).
- **Billable-facts support:** until a clinical-encounter capability exists, the capability result is false and reads return `no_billable_facts` (CF-06). openPractice then enters charges manually, marked manual (ruling 21).
- **No billing data:** openChart produces no billing data (CF-05), and holds no coverage (ruling 13).
- **Diagnoses and retractions:** only `confirmed` encounter diagnoses are published, and a published diagnosis that is later refuted is retracted (ruling 87). Publication is limited to an `active` link, with one exception: pointer-only retractions of facts already published are still delivered after the link ends `revoked` or `superseded` (ruling 88; CF-01, CF-04). A retraction reason code is added to `openpractice-ehr-clinical-facts/1.0` while 1.0 is unratified, through the ruling-93 follow-up (ruling 89).

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

**No conflict with ratified openChart text was found.** PL-10 refuses local edits to `patient_name` and `date_of_birth` only for patients with an established link. The ratified text does not require openChart to accept such edits, so no ratified text is changed.

## Design calls for owner review

Items marked ⚑ are design calls this change makes beyond Brett Heap's rulings. Each is proposed, not ruled, and each is an owner item (`tasks.md` 1.5).

1. ⚑ **Established links** (PL-02, PL-07 to PL-10, PL-16). This change tells the two kinds of `identity_review` apart by whether the link has ever been `active`. A link becomes established when openChart answers `linked` or a review of it resolves `confirmed`, and planning decides how the row records it.
   - An established link in review stands confirmed as the same person, with one field in question.
   - A link in review since its request does not. Its openPractice record may be someone else, so it must not receive this patient's corrections, and its snapshots must not change this patient's record.
   - Ruling 17 covers edits to "a linked patient's projected fields". This call reads a patient whose only link was never confirmed as not yet linked.
   - The alternative was to refuse edits during any review but send no correction. That would freeze a patient's name and date of birth in openChart because of a request that may name another person.

   Recommendation: confirm.
2. ⚑ **No instructions from a link that has never been established** (PL-16). openChart takes neither restriction flags nor alternate addresses or channels from such a link's snapshots.
   - An alternate address or channel from a record not confirmed as this patient's could send this patient's communications to another person.
   - Honoring that record's restriction flags alone would disclose nothing, but could withhold this patient's communications because of another person's instructions.
   - The other reading is to honor the flags and never the channels. The open corrections to `opensoft/openPractice-spec` `define-mvp-practice-foundation` take that reading for a same-person group (its PR-15, proposed there).

   Recommendation: take nothing until the link is confirmed, and treat the patient meanwhile as a patient with no link.
3. ⚑ **Confirming a link that has never been established** (PL-06). The link becomes established at the moment of confirmation, and openChart applies snapshots only from then on.
   - **What is applied.** The reviewer confirms against the latest snapshot received on the link, read side by side with the `OC Patient`. openChart applies exactly that snapshot in the same transaction, never a snapshot received before the confirmation that the reviewer did not read.
   - **`applied_version`.** `link.review_resolved` carries that snapshot's `demographic_version` as `applied_version`. Each link request carries a snapshot, so a confirmation always has one to read.
   - **A later snapshot.** One that arrives after the reviewer's reading is not applied by the confirmation. openChart applies the next snapshot openPractice publishes on the link.
   - **What the contract fixes.** `openpractice-ehr-patient-link/1.0` leaves `applied_version` optional and gives it no further meaning. It has a provenance reason, `republish_after_review`, but no rule says when it is used. The resume rule of `define-mvp-practice-foundation` EB-08, "publishing the current snapshot if it is newer than the applied version", covers held updates only. So openPractice may learn of an older `applied_version` and still publish nothing until its next change.
   - **Why.** A snapshot that arrived while nothing confirmed the two records as one person was never checked against this patient. Applying it unread would let a confirmation carry demographics that nobody compared.
   - **The other reading** was to apply the latest snapshot received, read or not. That is simpler, but it applies data no human compared with the patient.

   Recommendation: confirm. The companion change should extend EB-08's resume rule to every `confirmed` resolution: openPractice republishes its current snapshot, with reason `republish_after_review`, when `applied_version` is lower than its current version.

4. ⚑ **`revoked` and `superseded` are terminal** (PL-02, PL-06, PL-08, PL-11, PL-16).
   - **The finding.** PL-08's rejection set a link "back to `active`" unconditionally. A hold rejected after the link was revoked would have reactivated it, and with it demographic application and clinical-fact reads. PL-06 and PL-11 gave revocation precedence over confirmation only, and nothing gave supersession precedence at all.
   - **The rule.** No transition leaves `revoked` or `superseded`. Every confirmation and every hold resolution re-checks the link's status first.
   - **Cancelled holds.** A revocation or supersession cancels every open hold on the link, with the reason recorded, and nothing is sent for it.
   - **Reused link ids.** A `link.request` that names a revoked or superseded `link_id` is refused with `link_revoked` or `link_superseded`. The contract's `link_id` names one link for its whole life.
   - **Restrictions.** Restrictions of versions held when the link ended stay honored, because openChart was honoring them a moment before.
   - **Where else this was checked.** Three other transitions set a link `active`: PL-05's `linked`, PL-06's confirmation and PL-08's confirmation. Each was covered only by "revocation wins over confirmation", which said nothing of supersession or of a reused `link_id`. They now share the one rule.

   Recommendation: confirm.
5. ⚑ **What openChart expects back for a correction request** (PL-10, PL-11). This follows `opensoft/openPractice-spec` `define-mvp-practice-foundation` EB-09 (its design call F-22, PROPOSED there).
   - openPractice answers every correction request `received`, even through a link it holds in identity review. That includes a review it raised on a link openChart holds `active`.
   - It decides nothing on such a request while the review is open.
   - It sends no `correction.resolved` for a request whose link ends `revoked`.
   - openChart therefore records `received` as received only, waits without error, and treats the link's revocation as closing its open correction requests on that link, with the reason recorded.
   - A `link.review_resolved` `revoked` from openPractice for a review it raised is handled as a revocation, since it is the only way openChart learns that such a review ended the link.
   - The patient-link contract is unchanged: no reject reason was added, so PL-04 still pins `76f465e144893000de4bd2240adb9f547899e2e8100315f698c3cc6cb885b802`.

   Recommendation: confirm.

## Risks / Trade-offs

- **[Wrong-patient propagation]** → Mitigated by the deterministic "agree" check, the date-of-birth suspension, single-resolver review, and the edit refusal. A link that has never been confirmed carries nothing in either direction (⚑ design call 1).
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
3. **Appointment authority (R-7).** Closed by ruling 31: openPractice owns the administrative appointment, and openChart owns the encounter and may keep an appointment reference. The 1.0 contracts carry no appointment operations; appointment events wait for a later MINOR version.
