## ADDED Requirements

### Requirement: PG-01 One gate decision governs every prescription signature, co-signature and release
openChart SHALL decide exactly one gate decision, with a coded reason, for each attempt to sign a prescription or a new version of one, to co-sign it, or to release it from `pending_release`. Once a governed amendment puts `define-ai-authored-clinical-records` Tier 2 in force, it SHALL also decide one for each acceptance of an AI-authored prescription, which SHALL need `open` (PG-02; tension PT-4). `define-clinical-acts-foundation` RX-02 (not yet on main) SHALL rely on this decision (owner rulings 74 and 78). The decision SHALL be `open` only when all of these hold:
- this capability is built and enabled in the deployment;
- the prescription's controlled-substance classification (`define-clinical-acts-foundation` RX-03) is neither `controlled` nor `unknown` (owner ruling 83);
- a recorded legal and regulatory review is in force (PG-04);
- a source is connected, verified (KA-03) and current (KA-04);
- a check for that step has completed against the exact content digest (PC-04);
- every alert and warning from that check has a response that meets PC-06.

A prescription classified `controlled` or `unknown` SHALL get `refused` with reason `controlled_classification_not_permitted`, the foundation's own reason code, at every step and whatever the source's state. It SHALL never get `outage_path` (owner ruling 83). When the source is connected and verified but unavailable at that step (KA-04, KA-05), and not past its staleness limit (KA-04), the decision SHALL be `outage_path`, governed by PG-02. In every other case it SHALL be `refused`, with one of these reasons: `controlled_classification_not_permitted`, `capability_disabled`, `legal_review_missing`, `no_verified_source`, `currency_policy_missing`, `source_stale_beyond_limit`, `check_not_completed`, `check_stale` or `alerts_unanswered`.

#### Scenario: Every condition holds
- **WHEN** a clinician signs a prescription after a completed signing-time check, with every alert answered, in a deployment with a verified, current source and a recorded review
- **THEN** the gate decision is `open`, and RX-02 lets the signature complete

#### Scenario: Failure: no verified source is connected
- **WHEN** a clinician tries to sign a prescription in a deployment with no verified source
- **THEN** the gate decision is `refused` with reason `no_verified_source`, the prescription stays `draft`, and no outage path is offered

#### Scenario: Failure: an alert is unanswered
- **WHEN** a clinician tries to sign with a `high` alert unanswered
- **THEN** the gate decision is `refused` with reason `alerts_unanswered`

#### Scenario: Failure: a controlled or unknown classification
- **WHEN** a clinician tries to sign a prescription classified `unknown`, whether the source is verified and current with a completed check, or unavailable
- **THEN** the gate decision is `refused` with reason `controlled_classification_not_permitted`, no outage path is offered, and the prescription stays `draft`

### Requirement: PG-02 When the source is unavailable at a step, only a clinician may complete it, after an entry-by-entry local review and a recorded statement, and the prescription is re-checked
When the gate decision is `outage_path`, openChart SHALL let the step (signature, co-signature or release) complete only when all four of these hold (owner rulings 76 and 82; design call PD-22):
- the acting clinician's author type is `clinician`;
- the acting clinician holds prescription `sign` scope, or `cosign` scope for a co-signature;
- **the local review is done, entry by entry.** The review list SHALL be PC-01's input list, taken by reference, so that a change to PC-01 changes this list with it. It SHALL NOT be narrowed. openChart SHALL show, one entry at a time:
  - every input that PC-01 lists for that step's check, except the prescription version being checked. So every active patient-reported allergy, medication and supplement statement appears, whether or not a clinician has reconciled it, reviewed it or marked it `clinician_verified`;
  - every `draft` allergy entry or medication list entry, and every `refuted` allergy entry, for the same substance as a patient-reported statement on the list (PC-01), whatever its clinical status;
  - the "allergy status not recorded" warning, where it applies (PC-02).

  The clinician SHALL respond to each entry on its own. No response SHALL cover more than one entry, and no entry SHALL be skipped. The entries and responses SHALL be stored as that step's outage-review check record (PC-07);
- **the statement is recorded on that step's check record.** The clinician records the statement that the checks were unavailable and that a manual review was done, with the code `prescribing.checks_unavailable_manual_review`, on that step's outage-review check record. For a signature or co-signature, the same code SHALL also be that signature's attestation. A release has no signature, so for a release the check record names the acting clinician.

openChart SHALL then:
- at the signing step only, set the prescription content's `checks_unavailable_at_signing` flag (SL-03, PD-1) before the signature is applied, so that the signature covers it. At co-signature and at release, the outage SHALL be recorded only on that step's check record, and signed content SHALL NOT change (`define-clinical-acts-foundation` CA-05);
- list the prescription for the acting clinician and for the medical director;
- re-check it automatically as soon as the source is available and current again;
- route any alert from that re-check to the signer, or to the medical director where the signer cannot act, as an open work item.

When the source is unavailable at a deferred release time and no clinician completes this path, the prescription SHALL stay `pending_release` with a work item for its signer, as `define-clinical-acts-foundation` RX-02 requires. No timer SHALL release it.

The work item SHALL stay open until a named clinician responds under PC-06. No timer or default SHALL close it. A non-clinician author SHALL never use this path. That includes any future AI author under `define-ai-authored-clinical-records` (not yet on main), which always needs an `open` decision.

#### Scenario: A clinician signs during an outage
- **WHEN** the verified source is unreachable at signing, and a clinician responds to each local entry and records the statement
- **THEN** the prescription is signed with its `checks_unavailable_at_signing` flag, both the signer and the medical director see it, and it is re-checked when the source returns

#### Scenario: Failure: the statement is missing
- **WHEN** a clinician tries to sign during an outage without recording the statement
- **THEN** openChart refuses the signature and the prescription stays `draft`

#### Scenario: Failure: a clinician-confirmed medication entry is skipped at outage signing
- **WHEN** a clinician signs during an outage, and the medication list holds a clinician-confirmed entry for a drug prescribed elsewhere
- **THEN** openChart shows that entry on its own, and refuses the signature until the clinician gives it its own response, which is stored in the outage-review check record

#### Scenario: Failure: one response would cover the whole allergy list
- **WHEN** a clinician tries to answer the patient's three confirmed allergy entries with a single response during an outage
- **THEN** openChart refuses it, and asks for a response to each entry

#### Scenario: Failure: a patient-reported allergy is skipped at outage signing
- **WHEN** a clinician signs during an outage, and the patient has an unreconciled patient-reported allergy
- **THEN** openChart shows that allergy, and refuses the signature until the clinician gives it its own response, which is stored in the outage-review check record

#### Scenario: Failure: a reconciled penicillin report and its refuted entry are left out at outage signing
- **WHEN** a patient reported a penicillin allergy at intake, a clinician reconciled that statement into an allergy entry that is `refuted` and `inactive`, and a clinician signs a prescription for amoxicillin during an outage
- **THEN** openChart shows the patient's penicillin statement and the refuted entry, each as its own entry, and refuses the signature until the clinician gives each its own response, which is stored in the outage-review check record

#### Scenario: Failure: the source is unavailable at a deferred release
- **WHEN** a signed prescription reaches its release time while the source is unavailable, and no clinician completes the outage path
- **THEN** the prescription stays `pending_release`, a work item goes to its signer, and its signed content does not change

#### Scenario: Failure: an AI author meets an outage
- **WHEN** an AI-authored prescription arrives under a future Tier 2 while the source is unavailable
- **THEN** it is refused, because only a clinician may use the outage path

#### Scenario: Failure: the re-check finds a critical alert
- **WHEN** the re-check of a flagged prescription finds a `critical` allergy alert
- **THEN** openChart opens a work item for the signer that stays open until a named clinician responds with an explicit override or acts on the prescription

### Requirement: PG-03 The gate cannot be bypassed or switched off
No setting, role (including `System Manager`), grant, co-signature, override reason, extension or client SHALL bypass the gate or change its decision. Disabling this capability SHALL make every decision `refused` with reason `capability_disabled`. It SHALL NOT open signing.

#### Scenario: Failure: an administrator disables the checks
- **WHEN** a `System Manager` disables this capability in a deployment
- **THEN** every later prescription signature is refused with `capability_disabled`

#### Scenario: Failure: a client skips the check
- **WHEN** a client submits a prescription signature without a signing-time check
- **THEN** the gate decision is `refused` with reason `check_not_completed`

### Requirement: PG-04 Go-live needs a recorded legal and regulatory review
The gate SHALL NOT be `open` or `outage_path` in a deployment until the medical director records a legal and regulatory review covering this capability, with its scope, an opaque reference to the review, an effective date and a re-review date (design call PD-13). Clinical decision support may fall under medical-device or other rules. This change asserts no such rule. The review SHALL address at least these topics:
- whether and how the capability is regulated in each jurisdiction where the practice and its patients are located;
- the knowledge source's licence terms and permitted use;
- the labelling of alerts as advice and the record of the clinician's decision (PC-08);
- the outage path and its statement (PG-02);
- record-keeping and retention of check records;
- privacy of adapter traffic (KA-06);
- the events that require re-review: a new source, a new adapter, a new check kind or a widened scope.

A passed re-review date SHALL make the decision `refused` with reason `legal_review_missing`.

#### Scenario: The review is recorded
- **WHEN** the medical director records a review with its scope, reference and dates
- **THEN** the gate can open once its other conditions hold

#### Scenario: Failure: the review lapses
- **WHEN** the review's re-review date passes
- **THEN** every prescription signature is refused with `legal_review_missing` until a new review is recorded

### Requirement: PG-05 Foundation feature (5) depends on this change's ratification, and this change builds on foundation features (1) and (2)
`define-clinical-acts-foundation`'s feature (5), prescriptions, SHALL NOT start before this change is ratified (owner ruling 74). This change's feature SHALL build on that change's feature (1), clinical authority, and feature (2), encounter, note and signing, which carries the act model. Its checks and gate SHALL be enabled in a deployment before, or together with, foundation feature (5). Until they are, RX-02 SHALL refuse every prescription signature in that deployment.

#### Scenario: Prescriptions are built after ratification
- **WHEN** this change is ratified and foundation features (1) and (2) have landed
- **THEN** foundation feature (5) may start, and its signature, co-signature and release paths call PG-01

#### Scenario: Failure: prescriptions are enabled before the checks
- **WHEN** a deployment enables foundation feature (5) without this change's capability
- **THEN** every prescription signature is refused, because the gate decision is `refused` with `capability_disabled`
