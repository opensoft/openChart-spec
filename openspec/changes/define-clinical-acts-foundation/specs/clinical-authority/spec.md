## ADDED Requirements

### Requirement: AU-01 openChart defines clinical roles and one medical director per practice
openChart SHALL define two clinical roles, `clinician` and `nurse`, and a medical director designation (design call CD-12). Each practice (tenant) SHALL have at most one medical director at a time: a named human with an openChart account and a clinical role, designated by an audited act of an administrative role that planning names. Every designation and its end SHALL be recorded with actor, time and effective interval. When no medical director is designated, no role grant (AU-02) and no act-type registry entry (CA-09) SHALL be recorded, so nothing can be signed. The medical director designation is the one that `define-ai-authored-clinical-records` AG-02 and `define-clinical-message-inbox` (both not yet on main) need (tension CT-9).

#### Scenario: A practice designates its medical director
- **WHEN** the administrative role designates a named clinician as medical director
- **THEN** openChart records the designation with actor, time and effective interval

#### Scenario: Failure: no medical director is designated
- **WHEN** a practice with no medical director tries to record a role grant
- **THEN** openChart refuses it, and no clinician can sign an act

#### Scenario: Failure: a second medical director
- **WHEN** someone designates a second medical director while one is in force
- **THEN** openChart refuses the designation until the first one ends

### Requirement: AU-02 Authority to author, sign and co-sign is a role grant recorded in openChart
Who may draft, sign, co-sign, complete or discontinue each act class SHALL be decided only by role grants recorded inside openChart (design call CD-12). A grant SHALL name the person, the clinical role, the act class, the permitted actions (`draft`, `sign`, `cosign`, `complete`, `discontinue`), optionally a subset of act types, an effective interval, the practice-supplied credential attestation it rests on (AU-03), any co-signature requirement on the holder's acts (mode and window, CA-07), the medical director who recorded it, and a version. Only the medical director SHALL record, widen or renew a grant. A person with no grant in force for an act class SHALL have no authority for it; nothing SHALL be granted by default, by role name alone, or by the `System Manager` role.

#### Scenario: The medical director grants order authority
- **WHEN** the medical director grants a clinician `draft` and `sign` for orders for one year
- **THEN** openChart records the grant with its version, interval, attestation reference and the medical director

#### Scenario: Failure: a System Manager tries to sign an order
- **WHEN** a user holding only `System Manager` tries to sign an order
- **THEN** openChart refuses the signature

#### Scenario: Failure: a nurse signs outside the grant
- **WHEN** a nurse whose grant permits only `draft` for orders tries to sign one
- **THEN** openChart refuses the signature and the order stays `draft`

### Requirement: AU-03 Licensure and prescriber facts are supplied by the practice and are not verified by openChart
openChart SHALL record licensure, scope and prescriber facts only as attestations supplied by the practice: the attesting person, the time, the fact attested as a code, an expiry date and an opaque reference to the practice's own evidence (design call CD-13). openChart SHALL NOT verify them against any registry and SHALL NOT state or imply that it has. A grant that includes `sign` for prescriptions SHALL require a prescriber attestation in force; without one it SHALL be refused. When an attestation expires or is withdrawn, every grant that rests on it SHALL stop conferring authority at once.

#### Scenario: A prescriber attestation is recorded
- **WHEN** the practice records that a clinician is a prescriber, with an expiry date
- **THEN** openChart stores the attestation as practice-supplied, and shows it as not verified by openChart

#### Scenario: Failure: a prescription grant without a prescriber attestation
- **WHEN** the medical director tries to grant `sign` for prescriptions to a clinician with no prescriber attestation in force
- **THEN** openChart refuses the grant

#### Scenario: Failure: an attestation expires
- **WHEN** a clinician's prescriber attestation expires
- **THEN** every prescription-signing grant resting on it stops conferring authority, and a later signing attempt is refused

### Requirement: AU-04 Every action is checked against the grant in force at that moment, and reductions apply at once
openChart SHALL check every draft, signature, co-signature, completion, discontinuation and entered-in-error mark against the actor's grants in force at that moment, and SHALL record the grant version relied on. A narrowing, suspension or end of a grant SHALL apply at once to every later action. Acts already signed SHALL keep their signatures, and SHALL show the grant version in force when signed. Grant history SHALL be kept; no grant version SHALL be deleted.

#### Scenario: A grant is narrowed mid-session
- **WHEN** the medical director removes prescription signing from a clinician's grant while the clinician has a draft prescription open
- **THEN** the clinician's next signing attempt is refused, and the draft stays `draft`

#### Scenario: Failure: a stale grant is relied on
- **WHEN** a client submits a signature citing a grant version that has been superseded
- **THEN** openChart checks the grant in force, refuses if it does not permit the action, and records the grant it checked

### Requirement: AU-05 Only named humans author, sign or co-sign; no agent does
Every author, signer and co-signer SHALL be a named human holding a grant in force. No AI system, agent, integration identity, scheduled job or other automated process SHALL author, sign, co-sign, complete, discontinue or mark an act entered in error, in any role, in this change. Owner ruling 67 grants no AI clinical authority now; AI-authored acts remain specified, and off, in `define-ai-authored-clinical-records` (not yet on main).

#### Scenario: Failure: an agent tries to co-sign
- **WHEN** an AI agent tries to co-sign a pending order
- **THEN** openChart refuses it and the co-signature requirement stays pending

#### Scenario: Failure: a scheduled job tries to complete orders
- **WHEN** a scheduled job tries to mark released orders `completed`
- **THEN** openChart refuses it and the orders are unchanged
