## ADDED Requirements

### Requirement: AG-01 openChart keeps its own record of the medical director's authority grant and checks every write against it
openChart SHALL keep its own record of each authority grant the practice's medical director approves for an external clinical AI system, and SHALL check every write against that record (ruling 65, design call AD-1, binding). openChart MUST NOT accept a write on the strength of the authority the write claims, or of any configuration held only by the AI system.

Each grant version SHALL record:
- the practice and the source system it applies to;
- the mode: `advice_only`, `limited_practice` or `full_practice`;
- the AI system's configuration version that the medical director approved, and the AI system's own reference to that configuration where it has one;
- for `limited_practice`, the allowlist entries (AG-07); for `full_practice`, the full-practice grant and the reserved acts its legal review cleared (AA-05);
- the approving medical director (AG-02) and the approval time;
- the recorded legal and regulatory review for that mode (AG-05);
- the review policy and, for the practice modes, the co-review window (AG-10);
- its information scope: whether the AI's notes and documents kept as information (AW-06) are in scope; on in every mode unless a narrowing removes it (AG-08; design call AD-72, PROPOSED);
- the effective time and the expiry (AG-09);
- a grant identifier and a version number. The versions of one grant SHALL be consecutive integers starting at 1: each new version takes its predecessor's number plus one, and no number is skipped or reused (design call AD-47).

A grant version, once approved, SHALL NOT be edited. Every change to what a version records SHALL create a new version that references its predecessor, with actor, reason and time: a narrowing (AG-08) and a superseding approval (AG-09) each do.

**State history.** A version's state, `active`, `paused`, `expired`, `revoked` or `superseded`, SHALL be kept as an append-only history of dated state events on that version, and never by editing the version: its approval (`active`), a pause, a resumption, an expiry of the version or of the legal review it relies on, a revocation, and its supersession by a new version. Each state event SHALL record the new state, the time it takes effect, the actor (a named person; the AI system's notice, for a reduction under AG-08; or openChart, for an expiry, or for a pause when the last review grant lapses, AG-08) and the reason. A state event creates no version. A version's state at any time is the state set by its latest event at or before that time. No state event SHALL be changed or removed; a mistaken one is corrected by a later event, with its own actor and reason.

#### Scenario: Failure: a write claims more authority than the chart's record
- **WHEN** a `consult.write` claims `full_practice` under a grant whose current version in openChart records `advice_only`
- **THEN** openChart does not accept it: it keeps the consult as quarantined AI communication with `quarantine_cause` `mode_mismatch` and answers `quarantined` (AC-11)

#### Scenario: Grant versions are consecutive
- **WHEN** the medical director approves a grant, pauses and resumes it, narrows it, and later approves a superseding version
- **THEN** the versions are numbered 1, 2 and 3: the pause and the resumption create no version but are two dated state events on version 1, with actor and reason, the narrowing creates version 2, and the superseding approval creates version 3

#### Scenario: Failure: someone rewrites a grant's state history
- **WHEN** a user tries to change the time of a recorded pause, or to delete it
- **THEN** the change is refused, the state event stays as recorded, and a correction can only be a later state event with its own actor and reason

#### Scenario: Failure: a version number would be skipped
- **WHEN** an implementation tries to record version 4 of a grant whose latest version is 2
- **THEN** the record is refused, and the next version of that grant can only be 3

#### Scenario: Failure: someone edits an approved grant in place
- **WHEN** a user tries to change the configuration version of an approved grant version
- **THEN** the edit is refused, and only a new version approved by the medical director can carry the change

### Requirement: AG-02 Only the practice's medical director, as the clinical-acts foundation designates, approves or changes a grant
The medical director SHALL be the one that `define-clinical-acts-foundation` (openChart-spec#5, not yet on main) designates under its AU-01, which is the single definition of the practice's medical director in openChart, including the clinical role and any attestation AU-01 requires. This change defines no designation of its own (design call AD-24). Only that person, while the AU-01 designation is in force, SHALL approve a grant version, widen it, resume it, record its legal review reference, set its review policy and co-review window, or record a consult review grant (AG-11). The medical director, and any reduction under AG-08, MAY narrow or pause it. No AI system, agent, integration identity or other role, `System Manager` included, SHALL approve, widen or resume a grant. Where no AU-01 designation is in force, no grant SHALL be approved and the write path SHALL accept nothing: no grant counts as current, and every write that reaches the grant checks fails them with `no_current_grant`: a consult is quarantined under AC-11, with AC-11's fallback recipients, and an act is recorded as a recommendation under AW-16. When the AU-01 designation lapses or ends, openChart SHALL send every registered source of the practice an `authority.notice` with `change` `no_medical_director` (AW-13).

#### Scenario: Failure: an AI agent tries to approve a grant
- **WHEN** an AI agent, or the AI system's integration identity, tries to approve or widen a grant
- **THEN** the action is refused and the grant is unchanged

#### Scenario: Failure: a System Manager tries to approve a grant
- **WHEN** a user who holds `System Manager` but no AU-01 designation tries to approve an `advice_only` grant
- **THEN** the approval is refused and no grant is recorded

#### Scenario: Failure: the medical director's designation lapses
- **WHEN** the AU-01 designation ends because its licensure attestation lapses
- **THEN** every registered source of the practice receives an `authority.notice` with `change` `no_medical_director`, and its later consults are quarantined with `quarantine_cause` `no_current_grant`

#### Scenario: Failure: the practice has no medical director recorded
- **WHEN** an administrator tries to activate a grant for a practice with no medical director recorded
- **THEN** activation is refused

### Requirement: AG-03 There are three modes, advice only is the default, and they are built in order
A grant SHALL carry exactly one mode: `advice_only`, `limited_practice` or `full_practice` (ruling 59). A new grant SHALL default to `advice_only`. In `advice_only`, the AI system gives a patient information, an assessment and next steps, with no diagnosis language and no treatment directives (ruling 66). Its next steps mean how to get care and general self-care information, such as "see your doctor", "book a visit" or "go to urgent care", and never a treatment instruction for the patient's own condition (ruling 81). It may not prescribe, order, change a treatment plan or record a diagnosis of record (ruling 56). `limited_practice` and `full_practice` stay specified but off: openChart SHALL NOT approve a grant for either until a future governed amendment puts that mode in force (ruling 67, AG-04 gate (d)). The modes SHALL be built in this order: `advice_only` first (Tier 1), then `limited_practice`, then `full_practice` (ruling 63). openChart SHALL NOT let a grant for a mode be approved on a deployment whose openChart lacks the build for that mode (design call AD-19).

#### Scenario: Failure: full practice is requested before it is built
- **WHEN** a medical director tries to approve a `full_practice` grant on an openChart deployment that has only the advice-only build
- **THEN** the approval is refused with a coded reason

### Requirement: AG-04 Each mode stays off until its gates are met
openChart SHALL NOT activate a grant for a mode until all of the following are recorded for that mode (ruling 58, the gates the owner set on 2026-11-14, ruling 67 and ruling 207):
- **(a)** the medical director's approval of that mode's scope: for `advice_only`, the scope and the red-flag rules; for `limited_practice`, the allowlist; for `full_practice`, the full-practice grant;
- **(b)** a legal and regulatory review covering that mode (AG-05);
- **(c)** for `limited_practice` and `full_practice`, that openChart can accept an AI-authored order, prescription or diagnosis recorded with the authority it acted under: the clinical-acts foundation is ratified and built, and this change's Tier 2 is built for every act class in the grant's scope (AA-01);
- **(d)** for `limited_practice` and `full_practice`, a future governed amendment, made after advice-only has run and counsel's review is in, that puts that mode in force (ruling 67), and, because an AI only ever makes recommendations until a practitioner signs, a new ruling that allows limited or full practice as designed (ruling 157). Neither exists; until both do, neither practice mode can be approved;
- **(e)** for every mode, `advice_only` included, that a consult review can be signed off as ruling 158 requires, because ruling 57 has flagged and high-risk consults always reviewed: openWallet and openSig can do their part (ruling 152). Ruling 207: "Yes. Every AI consult is meant to be reviewed by a clinician; if that review cannot be completed, the AI should not be talking to patients. It can still be built and tested against stand-ins." Until then a grant can be recorded and tested against stand-ins, but not activated for patients; how a stand-in is marked, and what a test deployment may publish, are design call AD-67, PROPOSED;
- **(f)** for every mode, that at least one person holding the `clinician` role holds an AG-11 review grant in force in the practice, so that what openChart selects for review has a reviewer (design call AD-73, PROPOSED). Should the last such grant lapse later, openChart pauses the grant at once (AG-08), and AC-11's fallback applies to every item selected for review, by the sample as well as always (AG-11; design call AD-76, PROPOSED, citing ruling 207).

A legal review covering one mode SHALL NOT satisfy gate (b) for another.

#### Scenario: Failure: advice only before a consult review can be signed off
- **WHEN** a medical director tries to activate an `advice_only` grant while openWallet and openSig cannot yet support a practitioner's sign-off
- **THEN** activation is refused for gate (e), and the grant can still be recorded and tested against stand-ins

#### Scenario: Failure: advice only while nobody holds the review grant
- **WHEN** a medical director tries to activate an `advice_only` grant while no clinician in the practice holds an AG-11 review grant in force
- **THEN** activation is refused for gate (f), because nothing selected for review would have a reviewer

#### Scenario: Failure: limited practice without a legal review covering it
- **WHEN** a medical director tries to approve a `limited_practice` grant while the only recorded legal review covers `advice_only`
- **THEN** the approval is refused, and the grant stays at its prior mode

#### Scenario: Failure: a practice mode before the foundation exists
- **WHEN** a medical director tries to approve a `limited_practice` grant before the clinical-acts foundation is built
- **THEN** the approval is refused for gate (c)

#### Scenario: Failure: a practice mode before the governed amendment
- **WHEN** a medical director tries to approve a `limited_practice` grant on a deployment where the foundation and Tier 2 are built and a legal review covering limited practice is recorded, but no governed amendment has put limited practice in force
- **THEN** the approval is refused for gate (d)

### Requirement: AG-05 openChart records a reference to the legal and regulatory review for each mode, and states no legal rule itself
openChart SHALL record, for each mode it may activate, a reference to a legal and regulatory review: an opaque locator and SHA-256 digest of the review document, the mode or modes it covers, the act classes and act types it addresses, the reviewer named in it, the person who recorded the reference (the medical director), the recording time, and its expiry or re-review date. For `full_practice` and `limited_practice` it SHALL also record which reserved acts the review cleared, if any (AA-05).

openChart SHALL NOT encode any legal or regulatory rule as fact. The topics the recorded review must address are listed in `design.md` under "What the recorded legal and regulatory review must cover". openChart checks that a review is recorded, that it covers the mode, and that it is current. It does not judge the review's content.

#### Scenario: Failure: the review reference lacks a digest
- **WHEN** a medical director records a legal review reference with no document digest
- **THEN** the record is refused, and no grant may rely on it

#### Scenario: Failure: the legal review has expired
- **WHEN** the legal review a grant relies on passes its expiry
- **THEN** openChart appends an `expired` state event to the grant version, accepts no write, quarantining consults and recording acts as recommendations with `grant_expired`, sends an `authority.notice` with `change` `expired`, and answers a grant readback `grant_not_current` with `grant_expired`, until a current review is recorded and the medical director approves a new version (AG-09)

### Requirement: AG-06 Every write is checked against the current grant, and anything missing, expired, paused, narrowed or mismatched fails closed
For every `consult.write` and `act.write`, openChart SHALL find the grant for the write's practice and source system, and SHALL NOT accept the write when any of these holds, checking in the order of this table after the earlier steps of AW-06's precedence (for an `act.write`, `tier2_not_in_force` comes first, and for every write the consent step of AW-06 step 8 comes before this table). A consult, or an `act.write` whose content is information (AW-06), is then kept as quarantined AI communication in the chart (AC-11), and any other act is recorded as a recommendation (AW-16), each carrying the table's code. Failing closed means that such a write is never accepted; it never means that the write is refused, because missing authority is never a reason to refuse an addition (ruling 80, clause 18).

| Condition | Code |
|---|---|
| No grant exists, or none is `active` for the time AC-09, AW-06 or AA-03 sets | `no_current_grant` |
| The grant is `paused` | `grant_paused` |
| The grant, or the legal review it relies on, has expired | `grant_expired` |
| The grant is `revoked` | `grant_revoked` |
| The write names a grant version other than the one in force, or a configuration version or source authority reference other than the one that version records | `grant_mismatch` |
| The write's mode differs from the grant's mode | `mode_mismatch` |
| The write is not permitted in the grant's mode, or is an AI's note or document while the grant version's information scope is removed (AG-08) | `mode_not_permitted` |
| A named approver or legal review differs from the grant's | `approver_mismatch`, `legal_review_mismatch` |

A write that names no grant version or configuration version fails `grant_mismatch`, one that names no mode fails `mode_mismatch`, and one that names no approver or legal review where the grant records one fails `approver_mismatch` or `legal_review_mismatch`: a missing claim is answered by the check it would have answered, never refused (ruling 188; design call AD-63). A narrowing (AG-08) SHALL count: a write that relies on scope removed by a narrowing is not accepted. openChart SHALL record which grant version it checked in the receipt. Every check in this table that does not depend on what a write contains is also what the grant readback reports (AW-14; design call AD-44). An AI's note or document kept as information is permitted in every mode, advice only included, because it is information, while the grant version's information scope is on, as it is unless a narrowing removed it (AG-01, AG-08); one whose scope was removed fails `mode_not_permitted` and is quarantined in the chart, never refused (design calls AD-69 and AD-72, PROPOSED). Its grant's state at its receipt is checked too (AW-06).

#### Scenario: Failure: the configuration version does not match
- **WHEN** a write names the current grant version but a configuration version the grant does not record
- **THEN** openChart does not accept it: a consult is kept as quarantined AI communication, and an act recorded as a recommendation, each with `grant_mismatch`

#### Scenario: Failure: an advice-only grant receives an act
- **WHEN** an `act.write` arrives for a practice whose grant is `advice_only`, on a deployment where Tier 2 is in force
- **THEN** openChart records it as a recommendation with `path_reason` `mode_not_permitted`

### Requirement: AG-07 Limited practice is an allowlist the medical director approves, and anything not listed goes to the human doctor
A `limited_practice` grant SHALL carry an allowlist (ruling 60). Each entry SHALL record an entry identifier, one act type with its act class, its conditions, and the standing order or protocol behind it, by reference. An entry MAY mark conditions that openChart can check from chart data; those are re-checked on each write (AA-04, design call AD-16). The medical director approves the allowlist as part of the grant version.

Anything not on the allowlist SHALL NOT be accepted: it is recorded as a recommendation with `path_reason` `allowlist_entry_unknown`, and listed, with its content, for the patient's doctor as an act that the AI system was not allowed to make (AA-12, AW-16). A reserved act (AA-05) SHALL NOT be bound to an allowlist entry unless the grant's legal review cleared it.

#### Scenario: Failure: an act type not on the allowlist
- **WHEN** an AI system writes an act whose act type matches no entry on the current allowlist
- **THEN** openChart records it as a recommendation with `path_reason` `allowlist_entry_unknown`, and the patient's doctor sees it with its content

#### Scenario: Failure: an entry names a reserved act without clearance
- **WHEN** a medical director tries to add controlled-substance prescribing to an allowlist whose legal review does not clear it
- **THEN** the entry is refused

### Requirement: AG-08 The medical director can narrow or pause at once, and any reduction from any source applies at once
The medical director SHALL be able to narrow a grant (remove allowlist entries, lower the mode, shorten windows, add reserved acts, or remove its information scope, so that the AI's notes and documents are quarantined in the chart while its consults are checked as before; design call AD-72, PROPOSED) or pause it, in openChart, effective at once (ruling 59). A narrowing SHALL create a new grant version; a pause SHALL append a `paused` state event to the version in force (AG-01). openChart SHALL send an `authority.notice` with `direction` `from_openchart` for every change to a grant, through AW-08, whose `effective_at` is the time that change takes effect in the grant's history.

openChart SHALL also apply at once an `authority.notice` from the AI system whose `change` is `paused` or `narrowed`, and SHALL record it as a reduction pending the medical director's review (design call AD-6). A notice can only reduce authority. Only the medical director's act in openChart SHALL widen or resume a grant. Pending AI acts on a narrowing or pause SHALL be handled under AA-11.

**When the last review grant lapses (design call AD-76, PROPOSED, citing ruling 207).** Ruling 207: "Yes. Every AI consult is meant to be reviewed by a clinician; if that review cannot be completed, the AI should not be talking to patients. It can still be built and tested against stand-ins." When the last AG-11 grant in force in the practice lapses, ends or is revoked, so that no clinician can complete a consult review under the grant, openChart SHALL at once append a `paused` state event to every active AI grant version of the practice, with openChart as the actor and that lapse as the reason (AG-01), send each source an `authority.notice` with `change` `paused` (AW-08), and alert the medical director and the administrative role that the foundation's AU-01 names, with the coded cause only (AW-07). Only the medical director resumes the grant, and AG-04's gate (f) must hold again first. A consult that ended before the pause is recorded as before, and one that ended after it is quarantined in the chart with `grant_paused` (AC-09, AC-11).

#### Scenario: Failure: a pause arrives from the AI system
- **WHEN** the AI system sends an `authority.notice` with `change` `paused` for an active grant
- **THEN** openChart pauses the grant at once, accepts no later write, quarantining consults and recording acts as recommendations with `grant_paused`, and shows the medical director the pending reduction

#### Scenario: Failure: a notice tries to widen authority
- **WHEN** a notice from the AI system would add an allowlist entry or raise the mode
- **THEN** openChart refuses it with reason `notice_would_widen` and the grant is unchanged

#### Scenario: Failure: the medical director narrows notes and documents out of the grant
- **WHEN** the medical director narrows an active grant by removing its information scope, and an AI's note whose content validates as note content then arrives
- **THEN** openChart records a new grant version, sends an `authority.notice` with `change` `narrowed`, and quarantines the note in the chart with `mode_not_permitted`, never refusing it, while consults under the new version are checked as before

#### Scenario: Failure: the last review grant lapses
- **WHEN** the only AG-11 grant in force in the practice reaches its end while an `advice_only` grant is active
- **THEN** openChart appends a `paused` state event to the grant with openChart as the actor, sends the source an `authority.notice` with `change` `paused`, alerts the medical director and the administrative role with the coded cause only, and quarantines with `grant_paused` every consult that ended after the pause

### Requirement: AG-09 Grants and legal reviews expire, and nothing renews itself
Every grant version and every recorded legal review SHALL carry an expiry or re-review date set by the medical director (design call AD-10). When a grant version, or the legal review it relies on, reaches its expiry, the grant SHALL stop accepting writes, openChart SHALL append an `expired` state event to it (AG-01), and SHALL send an `authority.notice` with `change` `expired` (AW-08) and answer the grant readback `grant_not_current` with `grant_expired` (AW-14; design call AD-44). No grant, review or allowlist entry SHALL renew, extend or reactivate itself, and recording a current legal review does not restore an expired version. Only a new version approved by the medical director, relying on a current legal review, SHALL restore it; openChart then sends `superseded` naming that version, and the readback answers `grant_current`.

#### Scenario: Failure: a grant reaches its expiry
- **WHEN** an active grant reaches its expiry with no new version approved
- **THEN** openChart accepts no later write, quarantining consults and recording acts as recommendations with `grant_expired`, and sends an `authority.notice` with `change` `expired`

#### Scenario: Failure: the legal review reaches its re-review date
- **WHEN** the legal review an active grant relies on reaches its re-review date, while the grant's own expiry is months away
- **THEN** openChart appends an `expired` state event to the grant version, sends an `authority.notice` with `change` `expired`, accepts no later write, quarantining consults and recording acts as recommendations with `grant_expired`, and answers a grant readback `grant_not_current` with `grant_expired`

#### Scenario: The medical director restores a grant after its legal review lapsed
- **WHEN** a current legal review is recorded, and the medical director approves a new grant version that relies on it
- **THEN** openChart sends an `authority.notice` with `change` `superseded` naming the new version, and a grant readback answers `grant_current` with that version

### Requirement: AG-10 A grant carries its review policy and, for the practice modes, its co-review window
A grant version SHALL NOT be approved without a review policy version that the medical director sets: the review sample rate and the always-review categories for consults (AC-07), and the review window for consults selected for review (AC-08). A grant version for `limited_practice` or `full_practice` SHALL NOT be approved without a co-review window for every act class in its scope (AA-07). No agent SHALL set or change either.

#### Scenario: Failure: an advice-only grant without a review policy
- **WHEN** a medical director tries to approve an `advice_only` grant with no review sample rate or always-review categories
- **THEN** the approval is refused

#### Scenario: Failure: a practice-mode grant without a co-review window
- **WHEN** a medical director tries to approve a `limited_practice` grant with no co-review window for one of its act classes
- **THEN** the approval is refused

### Requirement: AG-11 A consult review is recorded only by a named clinician holding the AU-02 review grant
The consult review grant SHALL be the role grant of `define-clinical-acts-foundation` AU-02 whose scope is the action `review` over the record class `ai_consult_record`. That record class is not an act class, and a review under the grant creates no act. This change defines no grant model of its own (design call AD-32; tension AT-12, resolved). openChart SHALL let a person record a consult review (AC-08) only while that person holds such a grant in force and holds the `clinician` role under AU-01. The grant carries what AU-02 requires of every grant: the person and clinical role, the effective interval, the attestation it rests on (AU-03), the medical director who recorded it (AG-02), a version, and the `self_granted` flag where the medical director holds it. As AU-02 provides, only the medical director records, widens or renews it, and nothing is granted by default, by role name alone or by the `System Manager` role. No AI system or agent holds one (AU-05). openChart SHALL check every review against the grants in force at that moment, and SHALL record the grant version relied on (AU-04). AU-02 carries this scope and restricts it to holders of the `clinician` role. Where nobody holds the grant, AC-11's fallback applies to every item openChart selects for review, by the sample as well as by a category or a trigger, not only to what is quarantined in the chart, so that each reaches the medical director and every clinician authorized for the chart, any of whom may record a review attempt that does not clear it (design calls AD-59, AD-73 and AD-76, PROPOSED, citing ruling 207); AG-04's gate (f) switches no mode on while nobody holds it, and when the last grant lapses openChart pauses the AI's grant (AG-08). The same grant covers the review of an information record that an AI adds through this path (AW-16): the foundation's AU-02 at `9408e11` extends the scope `review` over `ai_consult_record` to such a record, PROPOSED there (its CD-37; design call AD-69, PROPOSED). A consult review under this grant also needs the practitioner's sign-off (ruling 158; AC-08; design call AD-54): it rests on this grant and the attestation behind it (AU-03), and on the licence verification held in the practitioner's openWallet (ruling 151; the foundation's CA-04). Both records of a licence must hold (ruling 160); when the practice's attestation and the wallet's licence verification disagree, neither governs alone, the sign-off does not count, and the entry is a recommendation naming the record that does not support it (the foundation's AU-03; tension AT-17, answered).

**A review attempted without the grant.** A consult review attempted by a person with no AG-11 grant in force, including one whose grant rests on an attestation no longer in force, SHALL take no effect and SHALL NOT be refused for that reason (ruling 80, clause 18). openChart SHALL keep the attempt, as written, as a review attempt marked not an authorized decision, with the foundation's codes: `no_grant_in_force`, and also `practice_attestation_not_in_force` when the attestation lapsed. The consult's review status SHALL NOT change, the attempt SHALL count as no review, and it SHALL never be reported to the source (the foundation's AU-02, AU-04 and design call CD-50; design call AD-59). An attempt by an AI or an agent is kept the same way, with `no_decision_authority` (the foundation's AU-05). AC-11's fallback, where nobody holds the grant, is such an attempt: any clinician authorized for the chart may record one, and the item stays listed until a holder of the grant reviews it (design call AD-59, PROPOSED; tension AT-13, resolved).

#### Scenario: The medical director grants consult review
- **WHEN** the medical director records an AU-02 grant of `review` over `ai_consult_record`, for one year, for a named clinician with an attestation in force
- **THEN** openChart records the grant with its version, interval, attestation reference and the medical director, and the clinician can record consult reviews

#### Scenario: Failure: a user with no review grant records a review
- **WHEN** a clinician account with no consult review grant in force tries to record a review outcome on a selected consult
- **THEN** the review takes no effect: openChart keeps it as a review attempt marked not an authorized decision, with `no_grant_in_force`, the consult's review status is unchanged, and nothing is reported to the source

#### Scenario: Failure: the attestation behind a review grant lapses
- **WHEN** the attestation a consult review grant rests on expires, and the holder then tries to record a review
- **THEN** the review takes no effect: openChart keeps it as a review attempt with `no_grant_in_force` and `practice_attestation_not_in_force`, and the consult stays selected for review
