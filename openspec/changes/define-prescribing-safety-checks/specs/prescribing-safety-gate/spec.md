## ADDED Requirements

### Requirement: PG-01 One gate decision governs every prescription signature, co-signature and release
openChart SHALL decide exactly one gate decision, with a coded reason, for each attempt to sign a prescription or a new version of one, to co-sign it, or to release it from `pending_release`. Once a governed amendment puts `define-ai-authored-clinical-records` Tier 2 in force, it SHALL also decide one for each acceptance of an AI-authored prescription, which SHALL need `open` (PG-02; tension PT-4). `define-clinical-acts-foundation` RX-02 (not yet on main) SHALL rely on this decision (owner rulings 74 and 78). The decision SHALL be `open` only when all of these hold:
- this capability is built and enabled in the deployment;
- a recorded legal and regulatory review is in force (PG-04);
- a source is connected, verified (KA-03) and current (KA-04);
- a check for that step has completed against the exact content digest (PC-04);
- every alert and warning from that check has a response that meets PC-06.

When the source is connected and verified but unavailable at signing (KA-04, KA-05), the decision SHALL be `outage_path`, governed by PG-02. In every other case it SHALL be `refused`, with one of these reasons: `capability_disabled`, `legal_review_missing`, `no_verified_source`, `currency_policy_missing`, `check_not_completed`, `check_stale` or `alerts_unanswered`.

#### Scenario: Every condition holds
- **WHEN** a clinician signs a prescription after a completed signing-time check, with every alert answered, in a deployment with a verified, current source and a recorded review
- **THEN** the gate decision is `open`, and RX-02 lets the signature complete

#### Scenario: Failure: no verified source is connected
- **WHEN** a clinician tries to sign a prescription in a deployment with no verified source
- **THEN** the gate decision is `refused` with reason `no_verified_source`, the prescription stays `draft`, and no outage path is offered

#### Scenario: Failure: an alert is unanswered
- **WHEN** a clinician tries to sign with a `high` alert unanswered
- **THEN** the gate decision is `refused` with reason `alerts_unanswered`

### Requirement: PG-02 When the source is unavailable at signing, only a clinician may sign, with a recorded statement, and the prescription is flagged and re-checked
When the gate decision is `outage_path`, openChart SHALL let the step (signature, co-signature or release) complete only when all four of these hold (owner ruling 76; design call PD-22):
- the acting clinician's author type is `clinician`;
- the acting clinician holds prescription `sign` scope, or `cosign` scope for a co-signature;
- **the local review is done.** openChart SHALL show every input that needs no knowledge source: the clinician-confirmed allergy list, every unreconciled patient-reported allergy, medication and supplement statement, the other `pending_release` and `released` prescriptions, and the "allergy status not recorded" warning where it applies. The clinician SHALL respond to each one under PC-06's individual-response rule, and the inputs and responses SHALL be stored as an outage-review check record (PC-07);
- **the statement is recorded.** The clinician records, as the attestation of that signature, the statement that the checks were unavailable and that a manual review was done, using the attestation code `prescribing.checks_unavailable_manual_review`.

openChart SHALL then:
- set the prescription content's `checks_unavailable_at_signing` flag (SL-03, PD-1), which the signature covers;
- list it for the signer and for the medical director;
- re-check it automatically as soon as the source is available and current again;
- route any alert from that re-check to the signer, or to the medical director where the signer cannot act, as an open work item.

The work item SHALL stay open until a named clinician responds under PC-06. No timer or default SHALL close it. A non-clinician author SHALL never use this path. That includes any future AI author under `define-ai-authored-clinical-records` (not yet on main), which always needs an `open` decision.

#### Scenario: A clinician signs during an outage
- **WHEN** the verified source is unreachable at signing, and a clinician records the statement and signs
- **THEN** the prescription is signed and flagged, both the signer and the medical director see it, and it is re-checked when the source returns

#### Scenario: Failure: the statement is missing
- **WHEN** a clinician tries to sign during an outage without recording the statement
- **THEN** openChart refuses the signature and the prescription stays `draft`

#### Scenario: Failure: a patient-reported allergy is skipped at outage signing
- **WHEN** a clinician signs during an outage, and the patient has an unreconciled patient-reported allergy
- **THEN** openChart shows that allergy, and refuses the signature until the clinician gives it its own response, which is stored in the outage-review check record

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

### Requirement: PG-05 Foundation feature (4) depends on this change's ratification, and this change builds on foundation feature (1)
`define-clinical-acts-foundation`'s feature (4), prescriptions, SHALL NOT start before this change is ratified (owner ruling 74). This change's feature SHALL build on that change's feature (1), the act model and authority. Its checks and gate SHALL be enabled in a deployment before, or together with, foundation feature (4). Until they are, RX-02 SHALL refuse every prescription signature in that deployment.

#### Scenario: Prescriptions are built after ratification
- **WHEN** this change is ratified and foundation feature (1) has landed
- **THEN** foundation feature (4) may start, and its signing path calls PG-01

#### Scenario: Failure: prescriptions are enabled before the checks
- **WHEN** a deployment enables foundation feature (4) without this change's capability
- **THEN** every prescription signature is refused, because the gate decision is `refused` with `capability_disabled`
