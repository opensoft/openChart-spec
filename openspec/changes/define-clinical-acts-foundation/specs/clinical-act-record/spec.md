## ADDED Requirements

### Requirement: CA-01 One clinical act model covers six act classes under a published content schema
openChart SHALL record clinical acts of exactly six act classes: `encounter`, `clinical_note`, `diagnosis_of_record`, `procedure_performed`, `order` and `prescription`. Every act SHALL share one envelope: act identifier and version, act class, act type, the openChart patient, status, author, recording time, signatures, amendment links, co-signature, derivation provenance, lifecycle events, the class openChart determined (`decision` for a signed act, `draft` for a draft; AN-06), the addition provenance of AN-04 and, for an act adopted from a recommendation, `adopted_from` (design call CD-1). Each act SHALL reference exactly one `OC Patient` through the openChart triple (openChart issuer, `openchart`, `OC Patient` identifier). An external identifier MUST NOT replace it.

The canonical representation of one act version SHALL be contract `openchart-clinical-act-content/1.0`, schema `contracts/openchart-clinical-act-content-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-clinical-act-content:1.0`, identified by the SHA-256 recorded in `contracts/SHA256SUMS`. The same contract SHALL represent one recommendation record (AN-09) and one information record (AN-14), told apart by `record_kind`. An information record's content SHALL validate as note content (`$defs/clinicalNoteContent`), with no other schema (AN-06). Each class's clinical content SHALL be addressable as `$defs/<class>Content`, so that another governed contract can pin it by digest (design call CD-28). A breaking change SHALL need a new MAJOR version and a new digest. Decision content of a class not in this list, or of an act type not in force in the registry (CA-09), never becomes an act and is never refused for that reason: it is entered as a recommendation with `no_decision_authority` (AN-06).

#### Scenario: An act is stored and read back
- **WHEN** a clinician signs a clinical note for a patient
- **THEN** openChart stores one act of class `clinical_note` linked to that patient's `OC Patient`, and its read representation validates against the schema at the recorded digest

#### Scenario: Failure: an act of a class this chart does not define is submitted
- **WHEN** a client submits decision content of class `treatment_plan_change` or `immunization`
- **THEN** no act is created, and openChart enters it as a recommendation with `no_decision_authority`, keeping the class as given

### Requirement: CA-02 Every act has a practitioner author; act content from any other author is entered as a recommendation, never refused for that reason
Every act version SHALL carry an author: an author type, the named author's reference, the author's clinical role and the reference of the role grant the author acted under (the authority basis). Like every addition, it SHALL also carry its writer and provenance (AN-04). An act exists only as a practitioner's draft or as a decision the practitioner signed off (CA-04, AN-14), and every act version is written by a human, in the chart (design call CD-52, PROPOSED). So its author type SHALL be `clinician`: a named human who holds an openChart clinical role grant, `clinician` or `nurse` (AU-02), acting through their own authenticated openChart session (design calls CD-2 and CD-3). Act content whose author is anyone else SHALL NOT become an act, and SHALL NOT be refused for that reason (owner ruling 80, clauses 13, 17 and 18). That covers a patient, an AI, a device, a system, and a human without the scope for it. openChart SHALL enter such content as a recommendation (AN-09) that names its author by `kind` (AN-02), or, for a clinical note's content, keep it as information under its writer's name (AN-14). Content whose writer cannot be identified SHALL be refused, and nothing stored (AN-01). Only a later governed change may add an author type for acts, once the owner answers Open Question 12. This field is the hook that `define-ai-authored-clinical-records` (not yet on main) builds on.

#### Scenario: A clinician authors a diagnosis
- **WHEN** a named clinician with a diagnosis grant records a diagnosis of record
- **THEN** the act carries author type `clinician`, the clinician's reference, the role `clinician`, the grant version and its provenance

#### Scenario: Failure: act content arrives from an AI
- **WHEN** a registered relay submits an order whose author is an AI, whatever authority or grant the request claims
- **THEN** openChart creates no act. It enters the order as a recommendation marked not an authorized decision, naming the AI by its openWallet ID, model and model version, with `no_decision_authority`

#### Scenario: Failure: an unregistered integration tries to author an act
- **WHEN** an integration identity that is not registered with the practice submits an order
- **THEN** openChart refuses it and stores nothing, because it cannot identify the writer

### Requirement: CA-03 Each act class has a closed status lifecycle
Every act SHALL have exactly one status from its class's closed list, and SHALL move only by the transitions below (design call CD-4). Each transition SHALL be recorded as an attributed, dated lifecycle event. openChart MUST refuse any other transition.

| Act class | Statuses | Transitions |
|---|---|---|
| `encounter` | `in_progress`, `final`, `amended`, `cancelled`, `entered_in_error` | `in_progress` → `final` (signed) or `cancelled`; `final` or `amended` → `amended` (new signed version) or `entered_in_error` |
| `clinical_note`, `diagnosis_of_record`, `procedure_performed` | `draft`, `final`, `amended`, `cancelled`, `entered_in_error` | `draft` → `final` (signed) or `cancelled`; `final` or `amended` → `amended` (new signed version) or `entered_in_error` |
| `order` | `draft`, `pending_release`, `released`, `completed`, `discontinued`, `cancelled`, `entered_in_error` | `draft` → `pending_release` or `released` (signed) or `cancelled`; `pending_release` → `released`, `pending_release` (new signed version), `cancelled` or `entered_in_error`; `released` → `completed`, `discontinued` or `entered_in_error` |
| `prescription` | `draft`, `pending_release`, `released`, `discontinued`, `cancelled`, `entered_in_error` | `draft` → `pending_release` or `released` (signed) or `cancelled`; `pending_release` → `released`, `pending_release` (new signed version), `cancelled` or `entered_in_error`; `released` → `discontinued` or `entered_in_error` |

`amended` SHALL apply only to a version after the first. `cancelled` SHALL mean the act never took effect. A failed sign-off SHALL never cancel a draft or an encounter, with one exception: a note draft whose content was kept as information is closed as `cancelled`, with reason `kept_as_information`, naming the record that now holds its content, so nothing is lost (AN-14). Cancelling a `pending_release` order or prescription is a sign-off, and its event carries the evidence of CA-04 (OR-02). A discontinuation, an entered-in-error mark and a co-signature are sign-offs too, and their events carry that evidence. For an order, `completed` records work done, not a decision: owner ruling 187, "Recording that an order was carried out is a record of work done." (design call CD-58). A prescription is never `completed` in this version: it ends only by a signed-off discontinuation or an entered-in-error mark (RX-01). `entered_in_error` SHALL mean the act was recorded in error (CA-06).

#### Scenario: A draft note is signed
- **WHEN** the author signs a draft clinical note
- **THEN** its status becomes `final`, with a `signed` lifecycle event naming the signer and time

#### Scenario: Failure: an illegal transition is attempted
- **WHEN** a user tries to move a `completed` order back to `released`, or a `cancelled` note to `final`
- **THEN** openChart refuses the transition and the act is unchanged

### Requirement: CA-04 A decision takes effect only by the practitioner's own sign-off, made with their openWallet and openSig in their logged-in session
Every medical decision SHALL need the practitioner's sign-off (owner ruling 151). An act SHALL take a signed status, and any other decision of AN-06 SHALL take effect, only when the practitioner signs it off as a logged-in user, with their openWallet and openSig signing and validating the entry. The practitioner MUST act through their own authenticated openChart session. Under ruling 151, the openWallet holds the verification of the practitioner's licence, and the openSig attests that the signature is from that wallet. openChart SHALL require re-authentication at the moment of signing; the mechanism is decided in planning (design call CD-10).

Before it accepts a sign-off, openChart SHALL check all four of these at that moment, all inside the practice's deployment (design calls CD-48 and CD-75, PROPOSED, against openWallet-spec change `add-practitioner-profile-and-licence-verification` (draft pull request #10, read at `4cfef0a`) and openSig-spec change `add-wallet-bound-attestation` (draft pull request #4, read at `b7d37a5`). Both are unratified drafts, and openChart re-checks their field names when they settle):
- the signer's account is bound to the key that signs, by a binding made as AU-07 states, and that key is declared by the `openwallet_id` that signs;
- the licence verification relied on passes openWallet's whole check of a verification, each part named: the verifier's signature verifies under a verifier key the deployment holds as active and not compromised; every proof of possession it records verifies under its recorded public key, names the recorded key reference and the wallet the verification is bound to, and has the recorded fingerprint; it names the key that signs; it is before its reliance bound; it is not superseded, by the supersession index below; it is not revoked in the newest revocation list the deployment holds from its verifier, whose age, and any freshness flag, the reliance records; the held record of the bound wallet is active; and its status is one openChart accepts, `active` only in version 1. It is for the licence the grant relied on was made against (AU-02; design call CD-78, PROPOSED);
- the sign-off is accepted, by four checks openChart makes itself: the openSig attestation verifies under openSig's attestation key held in the deployment, with result `verified`; openChart verifies the sealed proof, openWallet's `wallet-challenge-proof`, under the sealed public key, over `sha256:` and its own recomputed `statement_sha256`; the sealed key fingerprint is a key bound to the signer's account (AU-07) and named by the licence verification relied on; and the sealed challenge reference is the statement's. A forged attestation never stands in for the proof;
- the signer holds a grant in force with the action's scope for the act class and act type (AU-02, AU-04), resting on a practice attestation in force (AU-03).

**Supersession (design call CD-75, PROPOSED).** Supersession needs no revocation, so nothing else the deployment holds shows that a later verification replaced the one presented. openChart SHALL keep every licence verification it receives, not only the one a sign-off relied on, and a supersession index of them, and SHALL refuse an earlier verification presented after its successor (`superseded`), though nothing else it holds has changed. An entry is never removed. The verifications are kept as long as the records they support.

openSig receives only the challenge reference, the statement's SHA-256 and the proof, never the statement, the patient or any content. openChart owns exact-request consent: the signing view and its refusal of a signature over a digest that differs from what was shown, re-authentication at signing (design call CD-10), and acceptance only of a key whose each use is authorized by the practitioner on the device that holds it. That last is openChart's own acceptance rule for a sign-off, not something openWallet's custody registry states; nothing can check it until openWallet has a custody-acceptance record, or a successor proof profile that reports how each use was authorized. Neither the proof nor the attestation is consent. openChart authenticates to the attester with a credential internal to the deployment, such as mutual TLS with a pinned client certificate, decided in planning. After a lost answer, openChart resends the identical request, the same challenge reference, digest and proof, and issues no new challenge; openSig answers it with the stored attestation, comparing the proof in its canonical form (design call CD-75, PROPOSED).

The signer named in the statement SHALL be the account whose session re-authenticated for this sign-off. A signature's `signer_ref`, and a lifecycle event's `by_ref`, SHALL be that account (design call CD-53, PROPOSED).

**The sign-off statement (design call CD-53, PROPOSED).** At re-authentication openChart SHALL issue a single-use challenge for that one sign-off. The statement the practitioner signs off is the RFC 8785 canonical JSON of: the act identifier and version; the patient triple; the act class and act type; the action (`sign`, `cosign`, `discontinue`, `enter_in_error` or `cancel`); the signature role (`author` for `sign`, `cosigner` for `cosign`, and `actor` for any other action on an existing act); the signer; the attestation code and version; the SHA-256 of the canonical content and of its provenance; the signing time; the challenge; and, for an encounter's signature, the SHA-256 of the manifest of the records its signing view showed (EN-04). The signing view SHALL show every act and information record that references the encounter at signing: the latest version of each act, except a cancelled one, and each information record. It never shows a recommendation as part of the encounter. The manifest lists exactly those records, each as its record kind, identifier, version (for an act) and content digest, sorted. Only an encounter's signature, and the copy on its `cosigned` event, carries a manifest digest. The practitioner's proof, and openSig's attestation of it, SHALL be over that statement's SHA-256 only, which openChart SHALL record as `statement_sha256` with the challenge. The challenge is 32 random bytes in unpadded base64url and carries no meaning, the form openSig's draft accepts; the statement's own fields keep sign-offs of different purposes apart (design call CD-53, PROPOSED). A challenge SHALL be used once and only for the sign-off it was issued for. So an attestation captured for one action cannot stand in for another action, another act or another time.

openChart SHALL also accept a sign-off only from a wallet key whose declared custody is `isolated_per_use_authorized`, and SHALL record it with `custody_basis` `declared`: until openWallet defines a record of the evidence on which a key's custody is accepted, what openChart holds is the custody the key declares, and a wallet that declares such a key must itself declare that model. That each use is authorized on the device is openChart's own acceptance rule, which nothing checks until openWallet has a custody-acceptance record or a successor proof profile that reports how each use was authorized (design call CD-76, PROPOSED). That is the one model in openWallet's ratified closed custody registry (`opensoft/openWallet-code` at `bb0e9da`, `contracts/openxwallet/openxwallet-custody.registry.yaml`, version 1) whose signature evidences that the holder acted. `holder_readable` and `isolated_invocable` evidence only the holder's environment.

The licence verification that the second check reads, and the attestation that the third check reads, are now drafted in openWallet-spec change `add-practitioner-profile-and-licence-verification` (draft pull request #10, read at `4cfef0a`) and openSig-spec change `add-wallet-bound-attestation` (draft pull request #4, read at `b7d37a5`). Both are unratified drafts, and openChart re-checks their field names when they settle (tension CT-20; Open Questions 9 and 11). Owner ruling 153 has both drafted as changes in their own repositories: "a practitioner profile carrying a licence verification in openWallet, and a wallet-bound attestation in openSig". The checks above follow those drafts, PROPOSED (design calls CD-75 to CD-79). Owner ruling 154 amends openWallet's rule that a wallet is never a prerequisite for operating a domain "with one named exception: a practitioner's sign-off of a medical decision. The rest of the chart still works without a wallet." Owner ruling 155: "openChart decides whether a sign-off counts; openSig only attests that the signature came from that wallet." Owner ruling 156: a sign-off is checkable "Inside the practice's own deployment, so the chart never waits on an outside service to accept a decision."

Until each check is specified through its own project's governed change, and the owner accepts it for this check, that check cannot be made. Owner ruling 152: "No real decision until both exist. It can still be built and tested against stand-ins." The attempt SHALL then fail in the way the author can cure by trying again (AN-14): the draft stays open and nothing takes effect. openChart SHALL NOT substitute a check of its own for either. A stand-in for openWallet or openSig is for tests only: a deployment configured with a stand-in is a test deployment that holds only synthetic patients, and a sign-off checked against a stand-in never makes a decision in a live chart (design call CD-69, PROPOSED).

A signature SHALL bind:
- the signer, the signer's role and the role grant and its version;
- an attestation statement code and version (design call CD-9);
- the signing time;
- the SHA-256 of the canonical content signed;
- the sign-off evidence (design call CD-76, PROPOSED): the action; the `openwallet_id`; the key that made the proof, by `key_ref` and `key_fingerprint`; the licence verification relied on, kept once beside the records and named by its reference and SHA-256, with its verifier, when the licence was checked, its reliance bound, the licensing authority, jurisdiction, licence identifier and licence class, what the grant relied on was made against (`covers`), the revocation list used (its verifier, sequence, issue time and age, flagged when stale) and the provenance of the verifier key; the challenge; the statement's SHA-256; the openSig attestation itself, exactly as openSig issued it; the SHA-256 of the provenance; the custody model, with `custody_basis` `declared`; and the result of the check.

An author signature SHALL be a sign-off with action `sign`, and a co-signer's signature one with action `cosign`, whose signature role is `cosigner`. A co-signature's evidence is on the co-signer's signature, and the `cosigned` lifecycle event SHALL carry an identical copy of it. A sign-off of any other action on an existing act (a discontinuation, an entered-in-error mark, or the cancellation of a pending-release order or prescription) SHALL carry the same evidence, with signature role `actor` and its attestation code and version, on that action's lifecycle event (CA-03).

A failed sign-off SHALL NOT take effect and SHALL NOT be refused for missing authority (AN-12). What follows depends on which of AN-14's four kinds of failure it is (design call CD-79, PROPOSED): one the author can cure by trying again, one only the deployment can cure, and one only a new binding can cure each leave a draft open, or an existing act unchanged, with the failure on the attempt trail and no recommendation; a failure of authority enters the content, or the proposed action, as a recommendation (AN-09) whose `missing_authority` names each failed check, and a draft it came from is held, never cancelled. The results of the two drafts map as follows:
- openWallet's refusals of the verification relied on (`reliance_bound_passed`, `superseded`, `revoked`, `wallet_mismatch`, `key_not_covered`, `verifier_not_held`, `verifier_not_active`, `verifier_compromised`, `signature_invalid`, `wallet_not_active`, `status_not_accepted`) map to `licence_verification_missing`, with openWallet's reason in `path_reason`: a failure of authority. Its `not_checkable` (`licence_verification_not_checkable`) is one only the deployment can cure;
- openSig's `unavailable` maps to `signing_service_unavailable`: with reason `binding_registry_unreachable` the author can cure it by trying again; with `wallet_record_unavailable`, `attester_key_unavailable` or `clock_untrusted` only the deployment can cure it;
- openSig's `not_verified` maps to `attestation_not_verified`, which the author can cure by trying again. Where its reason names the binding or the key, the author is also told that the key may need binding again (AU-07). A `not_verified` with reason `signature_invalid` or `digest_mismatch` is raised to the medical director as a possible forgery or replay, never to the signer alone;
- openSig's `refused` with reason `caller_not_authenticated`, `request_shape_invalid` or `unexpected_field` (`attestation_request_refused`) means openChart's own credential or request is at fault, which only the deployment can cure; with `challenge_already_attested` or `digest_already_attested` (`attestation_replay_refused`), openChart issues a new challenge and the author signs again, and the attempt is raised to the medical director as a possible replay, never to the signer alone;
- the bound key's custody not being one openChart accepts (`custody_not_holder_evidencing`) is cured only by a new binding.

A sign-off attempted by a writer that holds no decision authority, or in another person's name, SHALL be entered as a recommendation (AN-07, AN-08). openChart MUST refuse a signature on content whose digest differs from the content shown to the signer, because the signer did not see that content.

#### Scenario: A clinician signs an encounter
- **WHEN** a clinician with encounter sign scope re-authenticates and signs an encounter with their openWallet and openSig, and all four checks pass
- **THEN** the signature records the clinician, role, grant version, attestation code and version, time, content digest, openWallet ID, licence verification relied on, openSig attestation and the check's result

#### Scenario: Failure: a signer's grant has lapsed
- **WHEN** a clinician whose diagnosis grant ended yesterday tries to sign their draft diagnosis
- **THEN** no diagnosis takes effect. openChart enters the content as a recommendation marked not an authorized decision, with `no_grant_in_force`, tied to the draft, holds the draft without cancelling it, and tells the clinician at once

#### Scenario: Failure: the wallet holds no current licence verification
- **WHEN** openWallet's licence verification is specified, and a clinician with a grant in force signs off an order while their openWallet holds no current licence verification covering it
- **THEN** no order takes effect, and openChart enters the order as a recommendation with `licence_verification_missing`, tied to the held draft

#### Scenario: Failure: the signature service cannot be reached
- **WHEN** a clinician signs off a draft note while openSig cannot be reached
- **THEN** the note stays a draft, the attempt is recorded, the clinician is told at once, and no recommendation is created

#### Scenario: Failure: openWallet and openSig do not yet specify the checks
- **WHEN** a clinician signs off an encounter before openWallet specifies a licence verification and openSig an attestation
- **THEN** the encounter stays `in_progress` with everything attached, the attempt is recorded, and no recommendation is created

#### Scenario: Failure: a captured attestation is replayed for another action
- **WHEN** a client presents the openSig attestation from a clinician's earlier signature of an order as that clinician's sign-off of the order's discontinuation
- **THEN** the attestation does not verify over the discontinuation's statement and challenge, the order is unchanged, and the attempt is recorded

#### Scenario: Failure: an attestation stands in for the proof
- **WHEN** an attestation with result `verified` is presented for a sign-off whose sealed proof does not verify under the sealed public key over openChart's own recomputed statement digest
- **THEN** the sign-off is not accepted, nothing takes effect, the attempt is recorded, and it is raised to the medical director as a possible forgery

#### Scenario: Failure: the licence the grant names is not the licence verified
- **WHEN** a clinician's grant was made against a licence in one jurisdiction, and the only licence verification their wallet holds is for a licence in another
- **THEN** that licence covers nothing for this grant, and openChart enters the entry as a recommendation with `licence_verification_missing`

#### Scenario: Failure: content changed after it was shown
- **WHEN** the content digest at signing differs from the digest of the content displayed to the signer
- **THEN** openChart refuses the signature and asks the signer to review the current content

### Requirement: CA-05 Signed content is never edited; an amendment is a new version
The content of a signed act version MUST NOT be edited in place or deleted. A change to signed content SHALL be recorded as a new version of the same act that references the version it supersedes, states an amendment reason, and carries its own author and signature (design call CD-5). Every prior version SHALL remain stored and readable by authorized users, with the current version marked. A new version MAY be authored by any clinician who holds sign scope for that act class, and the original author SHALL be shown as the author of the superseded version. A new version is a decision. Its sign-off follows CA-04, and one attempted without the authority SHALL be entered as a recommendation (AN-09), leaving the current version unchanged. Before it is submitted, a draft MAY be revised: a draft is not yet an addition, so revising it is not an edit of an addition (AN-05). Every revision SHALL be audited, and an abandoned draft SHALL be closed as `cancelled`, never deleted (design call CD-8).

#### Scenario: A clinician corrects a signed diagnosis code
- **WHEN** a clinician amends a final diagnosis to a different code with a reason
- **THEN** version 2 records the new code, references version 1, carries the clinician's signature and status `amended`, and version 1 stays readable

#### Scenario: Failure: someone edits signed content in place
- **WHEN** a user or extension tries to change the text of a final clinical note in place
- **THEN** openChart refuses the edit, and the note is unchanged

#### Scenario: Failure: someone deletes a signed act
- **WHEN** a user tries to delete a signed order
- **THEN** openChart refuses the deletion; only an entered-in-error mark, a discontinuation or an amendment can change its effect

### Requirement: CA-06 An act recorded in error is marked entered in error, never deleted
openChart SHALL let the act's author, a clinician with sign scope for the act class, or the medical director mark a signed act `entered_in_error`, with actor, time and a coded reason, as an attributed lifecycle event (design call CD-7). The mark is a decision. It is signed off under CA-04, and its lifecycle event carries the sign-off evidence and attestation. A mark attempted without the authority SHALL be entered as a recommended action on that act (AN-09), leaving the act unchanged. The act's content and history SHALL stay stored for audit. An entered-in-error act SHALL stop having clinical effect, SHALL be shown labelled as entered in error wherever it appears, and SHALL NOT count as an active diagnosis, procedure, order or prescription. This mark is the void that `define-ai-authored-clinical-records` (not yet on main) names. A draft SHALL be cancelled instead.

#### Scenario: An order on the wrong patient is voided
- **WHEN** a clinician marks a released order `entered_in_error` with reason `wrong_patient`
- **THEN** the order stops having effect, is shown labelled entered in error, and its content and history remain for audit

#### Scenario: Failure: an entered-in-error mark without a reason
- **WHEN** a user tries to mark an act entered in error without a coded reason
- **THEN** openChart refuses the mark and the act is unchanged

### Requirement: CA-07 A co-signature requirement can attach to any act version
openChart SHALL support a co-signature requirement on any act version, without changing the act model, with these parts (design call CD-11):
- **source:** in this change, the author's role grant (AU-02); the requirement names the grant and its version;
- **mode:** `before_effect`, where the act does not take effect until co-signed (in this change, only orders and prescriptions, which stay `pending_release`), or `after_the_fact`, where the act takes effect and is co-reviewed within a window;
- **due time:** the signing time plus the window the source sets;
- **co-signer:** a named clinician, other than the author, holding co-sign scope for the act class;
- **outcome:** `cosigned` (the co-signer's signature is added, signed off under CA-04); an amendment by the co-signer, which supersedes the version (CA-05); or an entered-in-error mark (CA-06).

A requirement whose due time passes with no outcome SHALL escalate to the medical director at once, who becomes a co-signer, and SHALL keep alerting until a named clinician records an outcome. No timer, default or agent SHALL record an outcome or close the requirement. A co-signature SHALL add the co-signer's signature, with signature role `cosigner` and action `cosign`, and a `cosigned` lifecycle event carrying an identical copy of its sign-off evidence (CA-04). While a `before_effect` requirement is pending or escalated, the act SHALL NOT be `released`, `completed` or `discontinued`. A co-signature attempted without the authority SHALL be entered as a recommendation (AN-09), and the requirement SHALL stay open (AN-14). A co-signature of a prescription SHALL also need the prescribing-safety gate (RX-02). A later governed change MAY add another source in a new MINOR version; `define-ai-authored-clinical-records` (not yet on main) intends its authority grant to be that source for owner ruling 62's co-review.

#### Scenario: A nurse's order waits for co-signature
- **WHEN** a nurse whose grant requires `before_effect` co-signature for orders signs a laboratory order
- **THEN** the order is `pending_release` until a clinician with co-sign scope co-signs it, and is then `released`

#### Scenario: Failure: a co-signature window passes
- **WHEN** an `after_the_fact` co-signature requirement passes its due time with no outcome
- **THEN** openChart escalates it to the medical director, keeps alerting, and the requirement stays open

#### Scenario: Failure: the author tries to co-sign their own act
- **WHEN** the author of an act tries to record its co-signature
- **THEN** the co-signature does not count and the requirement stays pending; openChart enters the attempt as a recommendation with `no_decision_authority`, because an author never co-signs their own act, whatever grant they hold

### Requirement: CA-08 Every act and every recommendation carries full provenance and an audit trail
openChart SHALL record the provenance of AN-04 for every act and every recommendation record. For every act it SHALL also record an append-only trail of every creation, draft revision, signature, co-signature, release, completion, discontinuation, cancellation, entered-in-error mark, amendment and co-signature escalation, and of every failed sign-off attempt with its reasons (AN-14). Each entry SHALL carry the actor, the time and the coded reason where one applies. Every sign-off in the trail SHALL carry the evidence of CA-04: the action, the signer's `openwallet_id`, the licence verification relied on, the challenge, the statement's digest, the openSig attestation and the result of the check. For a recommendation, the trail SHALL record the receipt sent to its submitter (AN-10), every failed adoption (AN-11) and its adoption or decline. An information record (AN-14) carries the provenance of AN-04 and the receipt sent to its writer. It SHALL record every read of an act or recommendation by an integration identity, with the identity, time and purpose. The trail MUST NOT be edited or deleted through any supported path. The provenance of an act or recommendation SHALL be readable by anyone who can read the patient's chart (owner ruling 80, clause 8).

**Integrity verification (design call CD-53, PROPOSED).** openChart SHALL provide an audit verifier. It SHALL run over the stored record on demand, whenever a record is exported, before an encounter is published to openPractice (PB-02), and before a record is returned by an interoperability read (CA-13). For every sign-off the verifier SHALL recompute, from the record's own fields:
- the content digest;
- the provenance digest;
- the sign-off statement's digest, whose signer is the signature's `signer_ref` or the event's `by_ref`;
- for an encounter's signature, the manifest digest, from every act and information record that referenced the encounter at `signed_at` (CA-04): the version of each act received by then and its status at that time, worked out from its lifecycle events, so an order cancelled after the signature still counts as shown.

It SHALL also check:
- that every signature is recorded as a `signed` lifecycle event (CA-03), reporting a missing one as an integrity failure;
- that an item released from quarantine is dated by its release: its first arrival, then its release, then its `received_at` (AN-01);
- that the author signature is by the act's author;
- that a `cosigned` event's copy equals the co-signer's signature;
- that no challenge serves two sign-offs, anywhere in the store;
- that every time is a real calendar time, since the contract's pattern checks ranges only;
- that an act signed after a hold carries `adopted_from`, or follows a `hold_released` by decline, and that a draft carries `held_for` exactly while its last hold event is `held` (AN-14).

**Re-verification (design call CD-77, PROPOSED, against openWallet-spec change `add-practitioner-profile-and-licence-verification` (draft pull request #10, read at `4cfef0a`) and openSig-spec change `add-wallet-bound-attestation` (draft pull request #4, read at `b7d37a5`). Both are unratified drafts, and openChart re-checks their field names when they settle).** For every sign-off the verifier SHALL also re-verify, from the record and what the deployment holds:
- openSig's signature over the attestation, under the attestation public keys the deployment holds, retired ones included;
- for a `verified` attestation only, the sealed proof, under the sealed public key, over the statement digest it recomputes;
- the licence verification, under the held verifier key, with every proof of possession it records, and that it named the sealed key fingerprint;
- revocation, against the revocation list recorded on that reliance, never today's, and supersession, against an index it rebuilds from the kept verifications rather than the stored one;
- that the attestation's challenge reference and digest are the statement's, and that the licence the grant names is the licence verified.

It never claims that a binding is still current. Verifying an attestation is checking openSig's signature: the audit, and the trail of failed attempts, verify a `not_verified` attestation by its signature alone, and never fail because its sealed proof does not verify. Such an attestation may carry no binding, or only the SHA-256 of a proof that did not decode, and lists what openSig did not resolve; the references inside its proof are only what the proof claims, and the trail stores it as it is. A decision's sign-off only ever carries a `verified` attestation. It SHALL also have a mode that takes verifier keys only from a release of openChart and runs on an exported copy of the records, so that someone outside the deployment can check the aim that the openWallet draft's threat model states. openChart SHALL keep, for that audit, every licence verification it received, the held verifier keys with their provenance and state, the revocation lists, and openSig's attestation public keys, retired ones included.

A mismatch SHALL be treated as an integrity failure. It is reported to the medical director and the administrative role, and is never repaired silently. A record that fails SHALL NOT be published or returned by an interoperability read until the failure is resolved. The contract's self-test runs every one of these checks that needs no signature over every valid fixture, checking that each sign-off's evidence agrees with itself, since its synthetic fixtures carry placeholder signatures, recomputing the manifest from the fixture set and checking challenges within each record and across the valid fixture set, which stands in for one store, and over integrity fixtures that pass the schema and must fail the verifier.

#### Scenario: An auditor reviews an amended note
- **WHEN** an authorized user opens the history of a note amended twice
- **THEN** every version, author, signature, reason and time is shown in order

#### Scenario: Failure: someone tries to edit the audit trail
- **WHEN** an extension or user tries to change or delete a lifecycle event
- **THEN** openChart refuses it and the trail is unchanged

#### Scenario: Failure: stored sign-off evidence no longer matches its record
- **WHEN** the audit verifier finds a discontinuation whose `by_ref`, act or patient differs from the statement its `statement_sha256` was made over, or a `cosigned` event whose copy differs from the co-signer's signature
- **THEN** it reports an integrity failure to the medical director and the administrative role, and changes nothing in the record

### Requirement: CA-09 Act types are data in a registry with reserved and emergency flags
openChart SHALL keep an act-type registry: for each act class, the act types a practice uses, each with a stable code, a display name, an effective interval, a version and two flags that SHALL be set explicitly on registration: `reserved` (an act reserved to a human clinician) and `emergency_management` (design call CD-14). Only the medical director SHALL add, change or retire an entry, and every change SHALL be a new registry version. Every act SHALL name an act type that is in force in the registry for its class. Together with AN-06, the registry is the chart's list of what counts as a decision (owner ruling 80, clause 9): decision content can take effect only when its class and act type are in force in it. A sign-off of a draft whose act type was retired or is not defined in the registry SHALL be refused with the coded reason `act_type_not_in_force`, whoever wrote the draft. This is the first check of a sign-off, before authority (AN-14). The draft stays a draft, with no recommendation, so nothing is lost and nothing is made that nobody could adopt. The draft is not an addition, so the refusal refuses no addition (design call CD-51, PROPOSED). Whether this departs from clause 13, under which a decision without authority is still entered in the chart, is put to the owner (Open Question 23). Decision content that arrives without a draft, whose class or act type is not in force, including while the registry is empty, SHALL be entered as a recommendation with `no_decision_authority` (AN-06, AN-09). A recommendation's act type is checked against the registry only when a clinician adopts it (AN-09). This change gives the two flags no effect on clinician-authored acts; they exist for `define-ai-authored-clinical-records` (not yet on main) and its allowlist, reserved-act and emergency rules.

#### Scenario: The medical director registers an act type
- **WHEN** the medical director registers a laboratory order type with `reserved` false and `emergency_management` false
- **THEN** a new registry version records the entry, both flags and the medical director

#### Scenario: Failure: an act type is registered without its flags
- **WHEN** someone tries to register an act type without setting both flags
- **THEN** openChart refuses the entry

#### Scenario: Failure: an act names an unregistered type
- **WHEN** a clinician tries to sign their own draft order whose act type was retired from the registry after the draft was created
- **THEN** openChart refuses the signature with `act_type_not_in_force`, creates no recommendation, and the draft stays a draft

### Requirement: CA-10 Additions arrive only through the versioned service boundary, and an act takes a signed status only by a practitioner's authorized sign-off
openChart SHALL accept additions, and create and change acts, only through its authenticated, versioned service boundary, authorized for subject, tenant, purpose and role as the ratified API requirement demands. Every client, mobile or workstation, and every system writer SHALL use that boundary as an identified writer (AN-01 to AN-03). Direct table writes SHALL be refused, as they are for intake today. A draft act SHALL be created only on the command of a human with `draft` scope (AN-14), and every act version SHALL be written by a human, in the chart (design call CD-52, PROPOSED). An act SHALL be moved to a signed status only by a practitioner's authorized sign-off (CA-04, AU-04). No intake submission, patient-reported statement, clinical communication, API response, extension event, notification, timer or other automated process SHALL create an act or move it to a signed status.

Decision content that an identified writer adds without the authority SHALL be entered as a recommendation (AN-09), and a clinical note's content from a writer without the authority to sign it is kept as information (AN-14). A recommendation is not a prescription, diagnosis, order, administration or autonomous action, and it creates none of them. Extensions MAY read acts and receive pointer-only events through supported hooks. An extension that adds anything SHALL do so as a registered system writer through the boundary, and MUST NOT create or sign an act. An extension event adds nothing by itself.

This is how this change honours the ratified rule that "no intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order…" (tension CT-1, read narrowly under owner ruling 84). That sentence also names a "treatment recommendation", and how its words read on the recommendation record is recorded as tension CT-22, not resolved here.

#### Scenario: Failure: an extension writes a diagnosis directly
- **WHEN** an extension inserts a diagnosis row directly, outside the service boundary
- **THEN** the write is refused and no diagnosis exists

#### Scenario: Failure: an extension event tries to create an order
- **WHEN** an extension event carries a payload shaped like an order
- **THEN** no order is created, drafted or signed, and nothing is added from the event

#### Scenario: Failure: a registered system submits an order
- **WHEN** a registered integration submits an order through the boundary
- **THEN** no order exists. openChart enters the content as the integration's recommendation marked not an authorized decision, and tells it so at once

### Requirement: CA-11 A clinician creates a record from patient-reported content only by an explicit, attributed action
A clinician MAY create a draft act from a patient-reported intake statement only by an explicit action, recorded with the clinician, the time and the source statement's identifier and version as derivation provenance (design call CD-22). The same SHALL hold for a clinical communication record under `define-clinical-message-inbox` (not yet on main), once it lands. The created act SHALL be a separate, clinician-authored act that follows every rule of this capability, including signing; nothing SHALL be created, drafted, signed or entered as a recommendation automatically from a statement or a communication. The source statement SHALL stay unchanged and visibly patient-reported, keeping its assertion kind; openChart SHALL NOT set its `verification_state` to `clinician_verified` or change any of its fields (tension CT-3). This is the "authorized clinical workflow" that "records another assertion", in the words of the ratified requirement "Intake does not confer clinician or autonomous authority" (tension CT-2).

#### Scenario: A clinician confirms a reported condition as a diagnosis
- **WHEN** a clinician reviews a patient-reported condition and chooses to record it as an encounter diagnosis
- **THEN** a draft diagnosis is created with derivation provenance naming the statement and its version, the clinician signs it, and the statement stays patient-reported and unchanged

#### Scenario: Failure: a statement would become a diagnosis without a clinician
- **WHEN** an intake submission containing a patient-reported condition is accepted
- **THEN** no diagnosis, draft or problem-list entry is created from it

#### Scenario: Failure: a reported medication is read as a prescription
- **WHEN** a consumer reads a patient-reported medication statement
- **THEN** it is not a prescription, and no prescription exists unless a clinician recorded and signed one

### Requirement: CA-12 Codes come from practice-supplied code sets; openChart bundles none
A coding on an act SHALL store the code system, the code, the code-system version where the practice-supplied code set declares one, the display text, and a reference to the practice-supplied code-set import it came from (design call CD-23). openChart SHALL bundle no code set and SHALL assert no license status for any code system. Before any code set is bundled with or distributed by openChart, its license status MUST be verified and a separately governed change MUST approve it. A practice SHALL load code sets under its own rights, and each load SHALL be recorded with its identity, version, effective date and the loading user. A code that is not in a loaded code set in force SHALL be refused on any coded field of an act. A recommendation's codings are kept as given and checked only when a clinician adopts it (AN-09, AN-11).

#### Scenario: A practice loads a code set
- **WHEN** a practice loads a code set it supplies
- **THEN** openChart records the set's identity, version, effective date and the loading user, and codings reference that load

#### Scenario: Failure: a code set is proposed for bundling
- **WHEN** a plan proposes shipping a code set inside openChart
- **THEN** the plan is out of scope until license verification and a separately governed change approve it

#### Scenario: Failure: a code is not in any loaded set
- **WHEN** a clinician enters a diagnosis code that is not in a loaded code set in force
- **THEN** openChart refuses the coding with a coded reason

### Requirement: CA-13 Acts map to FHIR R4-compatible resources at contract level, with no conformance claim
openChart SHALL define a FHIR R4-compatible mapping for acts at contract level: `encounter` to Encounter; `diagnosis_of_record` to Condition; `procedure_performed` to Procedure; `order` to ServiceRequest; `prescription` to MedicationRequest; `clinical_note` to DocumentReference; and authorship, signatures, co-signatures and derivation to Provenance (design `design.md`, "FHIR R4-compatible mapping"; design call CD-26). openChart MUST NOT claim FHIR certification, profile conformance or validation against any implementation guide. A draft, cancelled or restricted act SHALL NOT be exposed through any interoperability read. A recommendation record (AN-09) and an information record (AN-14) SHALL NOT be exposed through one either in this version (design call CD-59, PROPOSED). Open Question 19 names the FHIR fields that could carry their "not an authorized decision" or "not signed off" marker in a later version. They stay readable, with that marker, to anyone who can read the chart in openChart (AN-05). A record that fails the integrity verifier of CA-08 SHALL NOT be returned by any interoperability read until the failure is resolved. Provenance SHALL carry the writer, every party on whose behalf it wrote (AN-04) and the sign-off evidence (CA-04).

#### Scenario: A FHIR-compatible read of a final diagnosis
- **WHEN** an authorized consumer reads a final encounter diagnosis through an interoperability surface
- **THEN** it receives a Condition-compatible representation with category, code, clinical and verification status, encounter reference and Provenance

#### Scenario: Failure: a draft would be exposed
- **WHEN** an interoperability read would include a draft order
- **THEN** the draft is omitted

### Requirement: CA-14 Acts work without any external system, and no PHI enters logs
Every capability in this change SHALL operate with no openPractice, MedxFactory, MedxEHR, HealthLinc, medXfactory, external AI system or drug knowledge source configured, with three exceptions. A decision's sign-off needs the practitioner's openWallet and openSig (CA-04; owner ruling 151), the one named exception to openWallet's rule that a wallet is never a prerequisite (owner ruling 154). The sign-off SHALL be checkable inside the practice's own deployment, so the chart never waits on an outside service to accept a decision (owner ruling 156; Open Question 10 and tension CT-19, settled). Where a check cannot be made, a sign-off attempt leaves its draft open and is recorded (AN-14); it is never refused. Nothing but a sign-off needs a wallet: the chart is read, and patients resolved, with no wallet (owner rulings 154 and 183). Signing a prescription also needs the gate of RX-02. Third, openChart fetches each verifier's revocation list when the deployment can reach it. That fetch never blocks a sign-off (owner ruling 156): a reliance on the newest list held stands even when that list is older than the deployment's freshness bound, and is then flagged and raised to a human other than the signer. openChart sets that bound, 72 hours unless the practice sets another (design call CD-81, PROPOSED). A raised item never goes only to the signer: where the signer is the medical director, the practice names a second recipient when it configures its escalation path. A reliance later found to rest on a compromised verifier key since its compromise time, or on a verification revoked as issued in error or withdrawn by its verifier, is flagged and raised the same way; nothing is voided automatically, and the record stays as written. If no newer list arrives, the verification's reliance bound is the only hard stop. The ratified standalone golden-intake tests SHALL keep passing. openChart's logs, error messages, diagnostics and coded reasons MUST NOT contain names, dates of birth, contact details, identifier values or clinical content; they SHALL reference acts by identifier and version only.

#### Scenario: Standalone deployment
- **WHEN** openChart runs with no external system configured
- **THEN** a clinician can open and document an encounter and record diagnoses, procedures and orders. Every addition is identified and recorded, a sign-off takes effect where its checks can be made inside the deployment, and the golden-intake tests pass

#### Scenario: Failure: no newer revocation list arrives
- **WHEN** the newest revocation list the deployment holds from a verifier is older than the freshness bound, and a clinician signs off an order
- **THEN** the sign-off is not blocked; the reliance records the list used and its age, is flagged as stale, and is raised to the medical director, and to the practice's second recipient where the signer is the medical director

#### Scenario: Failure: a refusal would log clinical content
- **WHEN** openChart refuses to sign a diagnosis
- **THEN** its log entry carries the act identifier, version and a coded reason, and no code display, note text or patient detail

### Requirement: CA-15 A restricted act never leaves the chart until counsel's rules are encoded
Pending counsel's answer on sensitive record categories and minors' records (Open Question 3), openChart SHALL let a clinician mark an act `restricted` (design call CD-27). A restricted act, and any encounter that carries one, SHALL NOT be published to openPractice, exposed through any interoperability read, or sent to any external system. It SHALL stay visible in openChart's chart view to users authorized for the patient's chart. openChart SHALL assert no legal rule about which records are sensitive; a later governed change SHALL encode counsel's answer.

#### Scenario: A restricted diagnosis on a final encounter
- **WHEN** a final encounter for a linked patient carries a diagnosis marked `restricted`
- **THEN** openChart publishes nothing for that encounter to openPractice, and the encounter stays visible in the chart

#### Scenario: Failure: an interoperability read asks for a restricted act
- **WHEN** an integration identity reads an act marked `restricted`
- **THEN** openChart returns no content for it and records the read with a coded reason
