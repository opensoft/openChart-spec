## ADDED Requirements

### Requirement: AU-01 openChart defines clinical roles and one independently attested medical director per practice
openChart SHALL define two clinical roles, `clinician` and `nurse`, and a medical director designation (design calls CD-12 and CD-34). Each practice (tenant) SHALL have at most one medical director at a time. A designation SHALL be recorded by an account that holds the administrative designation role named in planning, and SHALL be refused unless all of these hold:
- the designee is a named human with their own openChart account;
- the designating account is not the designee's account;
- the designee holds the `clinician` role, resting on a licensure attestation in force that was recorded by a named human other than the designee (AU-03).

**The first medical director.** While a practice has no medical director, nobody can record a grant, so the first designee gets a clinical role in one audited bootstrap act by the designating account. That act records three things: the designee's licensure attestation (AU-03, so recorded by a named human other than the designee); the `clinician` role resting on it; and the designation. The role confers no act-class authority. The medical director then needs a grant for each act class, under AU-02's self-grant rule.

Every designation, bootstrap act and end of a designation SHALL be recorded with actor, time and effective interval, and SHALL be listed for the administrative role. When no medical director is designated, no role grant (AU-02) and no act-type registry entry (CA-09) SHALL be recorded, so nothing can be signed. This is the medical director designation that `define-ai-authored-clinical-records` AG-02 and `define-clinical-message-inbox` (both not yet on main) need (tension CT-9).

#### Scenario: The first medical director is designated
- **WHEN** an administrator designates a named physician as the practice's first medical director, recording a licensure attestation the physician did not record
- **THEN** openChart records the attestation, the `clinician` role and the designation in one audited act, and the physician has no act-class authority until a grant is recorded

#### Scenario: Failure: an administrator designates their own account
- **WHEN** the account holding the designation role tries to designate itself as medical director
- **THEN** openChart refuses the designation

#### Scenario: Failure: the designee's licensure attestation is self-recorded
- **WHEN** a designee's only licensure attestation was recorded by the designee
- **THEN** openChart refuses the designation

#### Scenario: Failure: no medical director is designated
- **WHEN** a practice with no medical director tries to record a role grant
- **THEN** openChart refuses it, and no clinician can sign an act

#### Scenario: Failure: a second medical director
- **WHEN** someone designates a second medical director while one is in force
- **THEN** openChart refuses the designation until the first one ends

### Requirement: AU-02 Authority to author, sign and co-sign is a role grant recorded in openChart, and a self-grant is shown and independently attested
Who may draft, sign, co-sign, complete or discontinue each act class, and who may review AI consult records, SHALL be decided only by role grants recorded inside openChart (design calls CD-12 and CD-37). A grant SHALL name:
- the person and the clinical role;
- its scope: either an act class with the permitted actions (`draft`, `sign`, `cosign`, `complete`, `discontinue`), optionally limited to a subset of act types; or the record class `ai_consult_record` with the single action `review`;
- an effective interval;
- the practice-supplied attestation it rests on (AU-03);
- any co-signature requirement on the holder's acts (mode and window, CA-07);
- the medical director who recorded it;
- a version.

**The consult review scope.** The scope `review` over `ai_consult_record` lets its holder record a review of an AI consult record under `define-ai-authored-clinical-records` AG-11 and AC-08 (not yet on main). `ai_consult_record` is not an act class: a review creates no act, and the scope confers no authority over any act. It SHALL be recorded only for a person holding the `clinician` role, and it follows every other rule of this requirement and of AU-03 to AU-05.

Only the medical director SHALL record, widen or renew a grant. A grant the medical director records for themselves SHALL be flagged `self_granted` (design call CD-34). It SHALL rest on an attestation recorded by a named human other than the medical director, SHALL be audited, and SHALL be shown as self-granted wherever the grant is shown and wherever an act signed under it shows its authority. Every self-grant SHALL be listed for the administrative role. A person with no grant in force for an act class SHALL have no authority for it. Nothing SHALL be granted by default, by role name alone, or by the `System Manager` role.

#### Scenario: The medical director grants order authority
- **WHEN** the medical director grants a clinician `draft` and `sign` for orders for one year
- **THEN** openChart records the grant with its version, interval, attestation reference and the medical director

#### Scenario: The medical director grants themselves diagnosis authority
- **WHEN** the medical director records a diagnosis grant for themselves, resting on a licensure attestation recorded by an administrator
- **THEN** the grant is recorded, flagged `self_granted`, listed for the administrative role, and every diagnosis signed under it shows that its authority was self-granted

#### Scenario: Failure: the medical director self-grants prescribing on their own attestation
- **WHEN** the medical director tries to grant themselves prescription `sign` scope, resting on a prescriber attestation they recorded themselves
- **THEN** openChart refuses the grant

#### Scenario: The medical director grants consult review
- **WHEN** the medical director records a grant of `review` over `ai_consult_record` for a named clinician, resting on an attestation in force
- **THEN** openChart records the grant, and the clinician can record AI consult reviews but gains no authority over any act

#### Scenario: Failure: a consult review without the grant
- **WHEN** a clinician who holds sign scope for diagnoses, but no `review` grant over `ai_consult_record`, tries to record a review of an AI consult record
- **THEN** openChart refuses the review, and the consult record's review status is unchanged

#### Scenario: Failure: a System Manager tries to sign an order
- **WHEN** a user holding only `System Manager` tries to sign an order
- **THEN** openChart refuses the signature

#### Scenario: Failure: a nurse signs outside the grant
- **WHEN** a nurse whose grant permits only `draft` for orders tries to sign one
- **THEN** openChart refuses the signature and the order stays `draft`

### Requirement: AU-03 Licensure and prescriber facts are practice-supplied attestations, recorded by someone other than their subject, and not verified by openChart
openChart SHALL record licensure, scope and prescriber facts only as attestations supplied by the practice (design calls CD-13 and CD-34). Each attestation SHALL hold:
- its subject;
- the named human who recorded it;
- the time;
- the fact attested, as a code;
- an expiry date;
- an opaque reference to the practice's own evidence.

The recorder SHALL hold the attestation-recording permission that planning names, and SHALL NOT be the attestation's subject. openChart SHALL refuse any attestation that a person records about themselves. openChart SHALL NOT verify attestations against any registry, and SHALL NOT state or imply that it has. It SHALL show each attestation as practice-supplied, naming its recorder.

A grant that includes `sign` for prescriptions SHALL require a prescriber attestation in force; without one, the grant SHALL be refused. When an attestation expires or is withdrawn, every grant and designation that rests on it SHALL stop conferring authority at once.

#### Scenario: A prescriber attestation is recorded
- **WHEN** an authorized administrator records that a clinician is a prescriber, with an expiry date
- **THEN** openChart stores the attestation as practice-supplied, names the administrator as its recorder, and shows it as not verified by openChart

#### Scenario: Failure: a clinician records their own attestation
- **WHEN** a clinician tries to record a licensure or prescriber attestation about themselves
- **THEN** openChart refuses it and stores nothing

#### Scenario: Failure: a prescription grant without a prescriber attestation
- **WHEN** the medical director tries to grant `sign` for prescriptions to a clinician with no prescriber attestation in force
- **THEN** openChart refuses the grant

#### Scenario: Failure: an attestation expires
- **WHEN** a clinician's prescriber attestation expires
- **THEN** every prescription-signing grant resting on it stops conferring authority, and a later signing attempt is refused

### Requirement: AU-04 Every action is checked against the grant in force at that moment, and reductions apply at once
openChart SHALL check every draft, signature, co-signature, completion, discontinuation, entered-in-error mark and AI consult review against the actor's grants in force at that moment, and SHALL record the grant version relied on. A narrowing, suspension or end of a grant SHALL apply at once to every later action. Acts already signed SHALL keep their signatures, and SHALL show the grant version in force when signed. Grant history SHALL be kept; no grant version SHALL be deleted.

#### Scenario: A grant is narrowed mid-session
- **WHEN** the medical director removes prescription signing from a clinician's grant while the clinician has a draft prescription open
- **THEN** the clinician's next signing attempt is refused, and the draft stays `draft`

#### Scenario: Failure: a stale grant is relied on
- **WHEN** a client submits a signature citing a grant version that has been superseded
- **THEN** openChart checks the grant in force, refuses if it does not permit the action, and records the grant it checked

### Requirement: AU-05 Only named humans author, sign or co-sign; no agent does
Every author, signer and co-signer SHALL be a named human holding a grant in force. No AI system, agent, integration identity, scheduled job or other automated process SHALL author, sign, co-sign, complete, discontinue or mark an act entered in error, or record an AI consult review, in any role, in this change. Owner ruling 67 grants no AI clinical authority now; AI-authored acts remain specified, and off, in `define-ai-authored-clinical-records` (not yet on main).

#### Scenario: Failure: an agent tries to co-sign
- **WHEN** an AI agent tries to co-sign a pending order
- **THEN** openChart refuses it and the co-signature requirement stays pending

#### Scenario: Failure: a scheduled job tries to complete orders
- **WHEN** a scheduled job tries to mark released orders `completed`
- **THEN** openChart refuses it and the orders are unchanged
