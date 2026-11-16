## ADDED Requirements

### Requirement: AU-01 openChart defines clinical roles and one independently attested medical director per practice
openChart SHALL define two clinical roles, `clinician` and `nurse`, and a medical director designation (design calls CD-12 and CD-34). Each practice (tenant) SHALL have at most one medical director at a time. A designation SHALL be recorded by an account that holds the administrative designation role named in planning, and SHALL be refused unless all of these hold:
- the designee is a named human with their own openChart account;
- the designating account is not the designee's account;
- the designee holds the `clinician` role, resting on a licensure attestation in force that was recorded by a named human other than the designee (AU-03).

**The first medical director.** While a practice has no medical director, nobody can record a grant, so the first designee gets a clinical role in one audited bootstrap act by the designating account. That act records three things: the designee's licensure attestation (AU-03, so recorded by a named human other than the designee); the `clinician` role resting on it; and the designation. The role confers no act-class authority. The medical director then needs a grant for each act class, under AU-02's self-grant rule.

**Confirming the first designation (owner ruling 98; design call CD-38).** The first medical director's designation SHALL take effect only once it is confirmed by a second named human who is neither the designating account nor the designee. A practice with only one administrator SHALL instead record, with the designation, a licence verification against the licensing board's public record, naming who performed it, when, and a reference to the record consulted. openChart SHALL store that verification, SHALL NOT perform or judge it, and SHALL assert no rule about it. A designation is configuration, not an addition to a patient's chart (AN-01). The medical director's own sign-offs follow CA-04, and how this ruling-98 check relates to the licence verification in the medical director's openWallet (owner ruling 151) is tension CT-18, recorded, not resolved.

Every designation, bootstrap act, confirmation and end of a designation SHALL be recorded with actor, time and effective interval. It SHALL be listed for the administrative role and, once a medical director is designated, for the medical director. When no medical director is designated, no role grant (AU-02) and no act-type registry entry (CA-09) SHALL be recorded, so nothing can be signed. This is the medical director designation that `define-ai-authored-clinical-records` AG-02 and `define-clinical-message-inbox` (both not yet on main) need (tension CT-9).

#### Scenario: The first medical director is designated
- **WHEN** an administrator designates a named physician as the practice's first medical director, recording a licensure attestation the physician did not record
- **THEN** openChart records the attestation, the `clinician` role and the designation in one audited act, and the physician has no act-class authority until a grant is recorded

#### Scenario: Failure: a sole administrator designates without confirmation or licence verification
- **WHEN** a practice with one administrator designates its first medical director with neither a second person's confirmation nor a recorded licence verification
- **THEN** the designation does not take effect, and no grant can be recorded

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
Who may draft, sign, co-sign, complete or discontinue each act class, and who may review AI consult records, SHALL be decided only by role grants recorded inside openChart (design calls CD-12 and CD-37). For a sign-off, a grant confers authority only together with the licence verification in the practitioner's openWallet (CA-04; owner ruling 151). openChart builds no scope-of-practice table: the scope a licence covers is the medical director's grant (owner ruling 92; owner ruling 80, clause 11). A licence the grant does not name covers nothing, and an entry signed off on it is a recommendation. The jurisdiction a grant names SHALL be one the practice has recorded as a place it practises (design call CD-78, PROPOSED). A grant SHALL name:
- the person and the clinical role;
- its scope: an act class with the permitted actions (`draft`, `sign`, `cosign`, `complete`, `discontinue`), optionally limited to a subset of act types; or the record class `ai_consult_record` with the single action `review`; or one of the inbox scopes of AU-06;
- an effective interval;
- the practice-supplied attestation it rests on (AU-03), and the licence the grant was made against: the licensing authority, the jurisdiction and the licence class that attestation records (design call CD-78, PROPOSED);
- any co-signature requirement on the holder's acts (mode and window, CA-07);
- the medical director who recorded it;
- a version.

**The consult review scope.** The scope `review` over `ai_consult_record` lets its holder record a review of an AI consult record under `define-ai-authored-clinical-records` AG-11 and AC-08 (not yet on main). `ai_consult_record` is not an act class: a review creates no act, and the scope confers no authority over any act. It SHALL be recorded only for a person holding the `clinician` role, and it follows every other rule of this requirement and of AU-03 to AU-05. PROPOSED, the same scope also covers the review of an AI's information record, a note or a document, that came through the AI write path, since every such record is selected for clinician review there (design call CD-37). A review of an AI consult needs the practitioner's sign-off under CA-04 (owner ruling 158). The sign-off statement is the one CA-04 defines, over the review record that `define-ai-authored-clinical-records` defines: its identifier and version, the patient, the record class, the action `review`, the signer, the attestation, the digests of its content and provenance, the time and the challenge (design call CD-50, PROPOSED).

Only the medical director SHALL record, widen or renew a grant. A grant the medical director records for themselves SHALL be flagged `self_granted` (design call CD-34). It SHALL rest on an attestation recorded by a named human other than the medical director, SHALL be audited, and SHALL be shown as self-granted wherever the grant is shown and wherever an act signed under it shows its authority. Every self-grant SHALL be listed for the administrative role and for the medical director. A person with no grant in force for an act class SHALL have no authority for it. Nothing SHALL be granted by default, by role name alone, or by the `System Manager` role.

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
- **THEN** the review takes no effect. It is recorded as a recommendation marked not an authorized decision, in the record `define-ai-authored-clinical-records` defines, and the consult record's review status is unchanged

#### Scenario: Failure: a System Manager tries to sign an order
- **WHEN** a user holding only `System Manager` tries to sign an order
- **THEN** no order takes effect, and openChart enters it as a recommendation marked not an authorized decision, with `no_grant_in_force`

#### Scenario: Failure: a nurse signs outside the grant
- **WHEN** a nurse whose grant permits only `draft` for orders tries to sign one
- **THEN** no order takes effect. openChart enters the order as a recommendation with `no_grant_in_force`, tied to the draft, holds the draft without cancelling it, and puts the recommendation before a clinician with order `sign` scope (AN-14)

### Requirement: AU-03 Licensure and prescriber facts are practice-supplied attestations, recorded by someone other than their subject, and not verified by openChart
openChart SHALL record licensure, scope and prescriber facts only as attestations supplied by the practice (design calls CD-13 and CD-34). Each attestation SHALL hold:
- its subject;
- the named human who recorded it;
- the time;
- the fact attested, as a code, and for a licence, the licensing authority, the jurisdiction, the licence identifier and the licence class, so that openChart can compare them with the wallet's licence verification under owner ruling 160 (design call CD-78, PROPOSED);
- an expiry date;
- an opaque reference to the practice's own evidence.

The recorder SHALL hold the attestation-recording permission that planning names, and SHALL NOT be the attestation's subject. openChart SHALL refuse any attestation that a person records about themselves. Every attestation SHALL be listed for the administrative role and, once one is designated, for the medical director. openChart SHALL NOT verify attestations against any registry, and SHALL NOT state or imply that it has. It SHALL show each attestation as practice-supplied, naming its recorder. A decision's sign-off also relies on the licence verification held in the practitioner's openWallet (owner ruling 151; CA-04). These attestations still underpin every grant and designation, and both SHALL hold for a sign-off to take effect. openChart SHALL show which licence verification a sign-off relied on and that it came from the practitioner's openWallet. It SHALL NOT state that it verified the licence itself (tension CT-18). Owner ruling 160 settles which licence record counts: "Both must hold, and ruling 98's check stays." When the practice's attestation and the wallet's licence verification disagree, about any of those four facts or about whether the licence is in force, neither governs alone: the sign-off SHALL NOT count, and openChart SHALL enter the entry as a recommendation whose `missing_authority` names the record that does not support it, `practice_attestation_not_in_force` or `licence_verification_missing`, or both when they differ about the licence itself.

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
- **THEN** every prescription-signing grant resting on it stops conferring authority, and a later signing attempt takes no effect and is entered as a recommendation with `practice_attestation_not_in_force` and `no_grant_in_force`, never refused for that reason

#### Scenario: Failure: the practice's attestation and the wallet's verification disagree
- **WHEN** a clinician whose openWallet holds a current licence verification signs off an order after the practice's licensure attestation for them has expired
- **THEN** the sign-off does not count, and openChart enters the order as a recommendation with `practice_attestation_not_in_force` and `no_grant_in_force`

### Requirement: AU-04 Every action is checked against its decision maker's authority in force at that moment, whatever kind of decision maker it is, and reductions apply at once
openChart SHALL check every action below against its decision maker's authority in force at that moment, whatever kind of decision maker it is (owner ruling 80, clause 11):
- every draft;
- every sign-off: a signature, a new signed version, a co-signature, a discontinuation, an entered-in-error mark, or the cancellation of a pending-release order or prescription;
- every completion of an order, which is a record of work done and not a decision: it needs the `complete` scope and no sign-off. A prescription is never completed in this version (RX-01; design call CD-58, PROPOSED);
- every AI consult review;
- every inbox action under AU-06.

The authority checked is:
- for a human, their grants in force (AU-02) and, for a sign-off, the licence verification in their openWallet and the openSig attestation (CA-04; owner ruling 151);
- for an AI, the mode and scope the medical director has approved. Advice only is the only mode that could be switched on, it confers no decision authority, and owner ruling 207 keeps it off for patients until a clinician's review of an AI consult can be signed off (AN-12);
- a device or a plain integration holds none.

openChart SHALL record the authority relied on: the grant version, and for a sign-off the evidence of CA-04. For a decision added on someone's behalf, openChart SHALL judge the decision maker and SHALL confirm that they made it by their own sign-off (AN-08).

An action without that authority SHALL take no effect, and SHALL NOT be refused for that reason (clause 18). openChart SHALL enter it as a recommendation (AN-09), except a completion, which is not a decision: one attempted without the `complete` scope changes nothing and is kept in the act's trail as a report attributed to its writer (OR-02). For an AI consult review or an inbox action, the recommendation is held in the record its own change defines, and nothing is sent and no status or item changes (design call CD-50, PROPOSED). A narrowing, suspension or end of a grant SHALL apply at once to every later action. Acts already signed SHALL keep their signatures, and SHALL show the grant version in force when signed. Grant history SHALL be kept; no grant version SHALL be deleted.

#### Scenario: A grant is narrowed mid-session
- **WHEN** the medical director removes prescription signing from a clinician's grant while the clinician has a draft prescription open
- **THEN** the clinician's next signing attempt takes no effect. openChart enters the prescription as a recommendation with `no_grant_in_force`, tied to the draft, holds the draft without cancelling it, and tells the clinician at once

#### Scenario: Failure: a stale grant is relied on
- **WHEN** a client submits a signature citing a grant version that has been superseded
- **THEN** openChart checks the grant in force and records the grant it checked. Where that grant does not permit the action, it enters the content as a recommendation instead of applying the signature

#### Scenario: Failure: an AI attempts a decision
- **WHEN** a registered relay submits a prescription on behalf of an AI
- **THEN** openChart checks the AI's authority, finds none in force, and enters the prescription as a recommendation with `no_decision_authority`

### Requirement: AU-05 Only a named human practitioner signs off a decision; an AI, agent, device or plain integration holds no decision authority, and what it adds is information or a recommendation
Every decision SHALL be signed off by a named human practitioner under CA-04 (owner ruling 151). Every author of an act, signer and co-signer SHALL be a named human holding a grant in force. In this change, no AI system, agent, device, integration identity, scheduled job or other automated process holds decision authority (owner ruling 80, clauses 11 and 19; owner ruling 67, second sentence). None of them SHALL sign off a decision, co-sign, complete, discontinue or mark an act entered in error, record an AI consult review, or hold a grant, including an inbox scope of AU-06. Each MAY add to the chart as an identified writer, registered where AN-03 requires (AN-01 to AN-03). What it adds is information, or, where it is a decision, a recommendation marked not an authorized decision (AN-09), never refused for that reason. Limited and full practice stay specified, and off, in `define-ai-authored-clinical-records` (not yet on main). An AI never manages an emergency, and the urgent hand-off to a human stays as it is (clause 20).

#### Scenario: Failure: an agent tries to co-sign
- **WHEN** an AI agent's relay submits a co-signature of a pending order
- **THEN** the co-signature takes no effect. openChart enters it as a recommendation marked not an authorized decision, with `no_decision_authority`, and the co-signature requirement stays pending

#### Scenario: Failure: a scheduled job tries to complete orders
- **WHEN** a registered scheduled job submits completions for released orders
- **THEN** the orders are unchanged, because only a named person with the `complete` scope records a completion, and each report is kept in its order's trail, attributed to the job

### Requirement: AU-06 The single grant model carries the clinical message inbox's scopes, and none of them reaches an act
Owner ruling 92 places inbox authority in this single grant model, set by the medical director. For `define-clinical-message-inbox` (not yet on main), an AU-02 grant MAY carry one of the scopes below (design calls CD-39 and CD-40). None of them is an act class or creates an act, and none gives authority over any act. No AI system, agent or integration identity SHALL hold one (AU-05). Every other rule of AU-02 to AU-05 applies, including the medical director's recording, the self-grant rule, attestations, and checks at the moment of action. This change defines only these grants; the inbox's behaviour stays in that change. An inbox action or patient reply attempted without the grant SHALL take no effect, and SHALL NOT be refused for that reason (owner ruling 80, clause 18). It SHALL be recorded as a recommendation marked not an authorized decision, in the record `define-clinical-message-inbox` defines for it: nothing is sent, and no item changes. Owner ruling 158 decides which of them need the practitioner's sign-off: a clinician's replies to patients "Yes", and "No for inbox housekeeping such as taking or reassigning an item." A patient reply is therefore signed off under CA-04, over the reply record `define-clinical-message-inbox` defines, in the same form as a consult review's sign-off (design call CD-50, PROPOSED). Where the item's patient is not yet matched, the statement names the handoff (`handoff_id`) and its `identity_state` in place of the patient (design call CD-50, PROPOSED). Where a close or an early marker withdrawal needs the sign-off, below, it is signed over a statement of the same form, with the action `close` or `withdraw` (design call CD-50, PROPOSED). Taking and reassigning an item are what the ruling names: `own` and `reassign` need no sign-off. PROPOSED beyond its words, `acknowledge`, `raise`, `return` and `split` are housekeeping too, and need none (design call CD-50); the ruling does not name `acknowledge`, and acknowledging stops an escalation, so it is listed for the owner. `close` is put to the owner, with this recommendation, which this change takes, PROPOSED: a close that follows a signed-off reply or a re-route is housekeeping; a close that ends an item with no reply records a clinical judgment and needs the sign-off. The ruling does not name the clinical-need marker. Recording a marker needs no sign-off, because it only widens access to care. Withdrawing it before its `valid_until` narrows access, so, PROPOSED and put to the owner, an early withdrawal needs the sign-off; otherwise the marker ends on its `valid_until` (design call CD-50; Open Question 13, closed).
- **Inbox ownership:** the record class `clinical_inbox_item`, with one or more of the actions `own`, `acknowledge`, `reassign`, `raise`, `return`, `split` and `close`, and exactly one lane, `physician` or `nurse`. A `nurse`-lane grant SHALL name the nurse-lane scope that the medical director records, which sets what may be triaged or answered in that lane. A person with no ownership grant in force owns no inbox item. `close` covers recording the closing outcome that the inbox requires (#3 MT-24).
- **Lanes follow roles:** a `physician`-lane grant, for any `clinical_inbox_item` action or for `reply` over `clinical_communication`, SHALL be recorded only for a person holding the `clinician` role. A person holding only the `nurse` role SHALL receive `clinical_inbox_item` and `reply` grants only in the `nurse` lane, bounded by the medical director's nurse-lane scope. openChart SHALL refuse any other grant.
- **Patient reply:** the record class `clinical_communication`, with the action `reply`, for one clinical role and one lane, resting on an AU-03 attestation in force.
- **Clinical-need marker:** the record class `clinical_need_marker`, with the actions `mark` and `withdraw`, recorded only for a person holding the `clinician` role.
- **On-call cover:** openChart SHALL define no on-call designation. The inbox's cover roster is a schedule. For each hour and lane it SHALL name only people holding an ownership grant in force for that lane, the medical director included as the last fallback. A roster entry for anyone else SHALL be refused, and a grant that lapses SHALL remove its holder from every later roster slot at once.

#### Scenario: The medical director grants nurse-lane ownership
- **WHEN** the medical director records a `clinical_inbox_item` grant with `own` and `acknowledge` in the `nurse` lane for a nurse, naming the nurse-lane scope the medical director recorded
- **THEN** openChart records the grant, and the nurse gains no authority over any act

#### Scenario: Failure: a nurse is given a physician-lane grant
- **WHEN** the medical director tries to record a `physician`-lane `clinical_inbox_item` grant with `own`, or a `physician`-lane `reply` grant, for a person who holds only the `nurse` role
- **THEN** openChart refuses the grant

#### Scenario: Failure: closing without the close action
- **WHEN** an owner whose `clinical_inbox_item` grant for the item's lane does not include `close` tries to close the item with an outcome
- **THEN** the close takes no effect. It is recorded as a recommendation marked not an authorized decision, and the item stays open and owned

#### Scenario: Failure: a reply without a reply grant
- **WHEN** a clinician who owns an inbox item, but holds no `reply` grant over `clinical_communication` for that lane, tries to send a patient reply
- **THEN** the reply is not sent. It is recorded as a recommendation marked not an authorized decision, for a holder of the reply grant

#### Scenario: Failure: the roster names someone without an ownership grant
- **WHEN** a roster change names a clinician with no `clinical_inbox_item` ownership grant in force for that lane and hour
- **THEN** openChart refuses the roster entry

#### Scenario: Failure: a marker grant for a nurse
- **WHEN** the medical director tries to record a `clinical_need_marker` grant for a person who holds only the `nurse` role
- **THEN** openChart refuses the grant

### Requirement: AU-07 A practitioner's account is bound to their wallet only in their own session, with proof of possession
The binding that CA-04's first check reads SHALL be made for each signing key individually, only in the practitioner's own re-authenticated openChart session, by that key's own proof of possession over a challenge that openChart issues, which openChart verifies by openWallet's verification for the profile the proof names, from a key that openChart accepts for a sign-off (CA-04; owner rulings 208 and 209; design call CD-54, PROPOSED, against openWallet-spec change `add-practitioner-profile-and-licence-verification` (draft pull request #10, read at `484dd16`) and openSig-spec change `add-wallet-bound-attestation` (draft pull request #4, read at `9100b3c`). Both are unratified drafts, and openChart re-checks their field names when they settle). Owner ruling 208 has a practitioner sign with a passkey or a security key, under the proof profile `wallet-webauthn-proof`, drafted in openWallet-spec change `add-webauthn-proof-profile` (draft pull request #11, read at `4d32fa1`), unratified; until it is ratified, no binding can be made and no practitioner can sign. Under it a key is bound only from a registration followed, in the same session, by a proof over a challenge openChart issued (CA-04; design call CD-85, PROPOSED). Each bound key has its own binding, whose public key is one that a licence verification names. openChart SHALL take its held copy of the practitioner's wallet record only from the practitioner, in their own session, and SHALL accept a key added to it only with that key's own proof made in that session. No administrator SHALL add a key to it; an administrator or the medical director MAY suspend a binding. Replacing a key is a new binding, and a sign-off with the new key is supported only by a licence verification that names it. CD-10's re-authentication may stay WebAuthn: it is not the proof. Whether the wallet's holder, and the subject of its licence verification, is the person of the account is answered, PROPOSED, by the three-leg match of openWallet's draft: the verifier's own record, this binding, and the practice's licence record of AU-03 (Open Question 9). Under openWallet, a wallet is a key or a declared set of keys held by its holder, and use requires proof of possession. openChart SHALL bind one wallet to at most one account. Every binding, suspension and unbinding SHALL be audited, recorded with actor and time, and listed for the medical director and the administrative role. The practitioner MAY unbind their wallet, and unbinding SHALL apply at once to every later sign-off. An administrator or the medical director MAY suspend a binding, which applies at once, but SHALL NOT create one or bind a wallet to another person's account. A binding is configuration, not an addition to a patient's chart (AN-01), and a wallet identifier never becomes the person's identifier (AN-02). Whoever runs the deployment can alter a binding outside these paths, so the account is not evidence of who signed: CA-04 shows the signer from the sealed licence verification (design call CD-84, PROPOSED).

**Enrolling a device for signing (owner ruling 209; design call CD-83, PROPOSED).** Owner ruling 209: a passkey that syncs through the practitioner's Apple or Google account counts "only on a device the practitioner has enrolled, as ruling 134 allows for approvals. A security key always counts. Controlled substances stay out (ruling 83) and would need stronger keys." In this change's terms, PROPOSED and put to the owner (Open Question 31):
- a device is enrolled for signing only by the practitioner, in their own re-authenticated openChart session on that device, with a proof made in that session by a key bound to their account. openChart then holds a credential for that device that stays on it, and a session that re-authenticates with it is a session on an enrolled device; planning chooses the credential;
- no administrator, medical director or other person SHALL enrol a device for a practitioner. The practitioner MAY remove their own enrolment; an administrator or the medical director MAY suspend or remove one, but SHALL NOT create one. Each applies at once to every later sign-off and changes nothing signed before;
- every enrolment, suspension and removal SHALL be audited, recorded with actor and time, listed for the medical director and the administrative role, and told to the practitioner. An enrolment is configuration, not an addition (AN-01);
- a key whose backup eligibility is set, a passkey that syncs, counts only when the session that re-authenticated for the sign-off is on a device the practitioner has enrolled; otherwise it fails in the kind only the practitioner's own enrolment cures (`signing_device_not_enrolled`, AN-14). Beyond the ruling's words, which name a security key, a key whose backup eligibility is clear needs no enrolled device: the flag does not show that a key is a security key, and a passkey that cannot sync is treated like one;
- openChart reads the backup eligibility the proof profile records at registration and returns with every proof, as the authenticator reports it; the profile says it cannot be proved truthful, and openChart relies on it as reported. A passkey that syncs does not reveal which device signed, so openChart evidences enrolment by its own means, the re-authenticated session on an enrolled device. Each sign-off records the backup eligibility and backup state, and, where the eligibility is set, the enrolled device (`enrolled_device_ref`);
- every bound key declares a custody model of openWallet's registry, so until the registry has one that fits a passkey that syncs, no such passkey can be bound, and owner ruling 209's yes for it waits on that (CA-04; Open Question 33). A security key with no PIN or biometric set cannot make the proof with user verification that a binding and a sign-off need (CA-04; Open Question 34);
- nothing here admits a controlled-substance prescription; RX-03's refusal stands (owner ruling 83).

#### Scenario: A practitioner binds their wallet
- **WHEN** a clinician, re-authenticated in their own session, presents a signature over openChart's challenge from a key their openWallet declares
- **THEN** openChart binds that wallet to the clinician's account, records the binding, and lists it for the medical director

#### Scenario: Failure: an administrator binds a wallet to someone else's account
- **WHEN** an administrator tries to bind clinician A's wallet to clinician B's account
- **THEN** openChart refuses the binding, and B's sign-offs with A's wallet fail CA-04's first check with `wallet_not_bound`

#### Scenario: Failure: an administrator adds a key to a practitioner's wallet record
- **WHEN** an administrator adds a key to the held copy of a clinician's wallet record
- **THEN** openChart does not add it, no binding rests on it, and a sign-off with it fails CA-04's first check

#### Scenario: A practitioner enrols their phone for signing
- **WHEN** a clinician, re-authenticated in their own session on their phone, enrols it with a proof made there by a key bound to their account
- **THEN** openChart records the enrolment with actor and time, lists it for the medical director and the administrative role, and tells the clinician

#### Scenario: Failure: a passkey that syncs is used from a device not enrolled
- **WHEN**, once the proof profile for passkeys and security keys is ratified, a clinician signs off an order with a passkey that syncs through their Apple account, from a laptop they have not enrolled
- **THEN** the sign-off does not count, the draft stays a draft, the attempt is recorded with `signing_device_not_enrolled`, and the clinician is told to enrol that device or sign with a security key

#### Scenario: A key whose backup eligibility is clear signs from a device that is not enrolled
- **WHEN**, once the proof profile for passkeys and security keys is ratified, a clinician signs off with a key whose backup eligibility is clear, from a laptop they have not enrolled
- **THEN** the enrolment rule does not stop the sign-off, every other check of CA-04 applies, and the sign-off records the backup eligibility clear and no enrolled device

#### Scenario: Failure: an administrator enrols a device for a clinician
- **WHEN** an administrator tries to enrol a device for signing on a clinician's behalf
- **THEN** openChart refuses the enrolment, and a sign-off from that device with a passkey that syncs does not count

#### Scenario: Failure: a second account claims a bound wallet
- **WHEN** a second account tries to bind a wallet that is already bound to another account
- **THEN** openChart refuses the binding until the first is unbound
