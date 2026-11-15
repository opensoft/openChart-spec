## ADDED Requirements

### Requirement: AG-01 openChart keeps its own record of the medical director's authority grant and checks every write against it
openChart SHALL keep its own record of each authority grant the practice's medical director approves for an external clinical AI system, and SHALL check every write against that record (proposed decision 65, design call AD-1). openChart MUST NOT accept a write on the strength of the authority the write claims, or of any configuration held only by the AI system.

Each grant version SHALL record:
- the practice and the source system it applies to;
- the mode: `advice_only`, `limited_practice` or `full_practice`;
- the AI system's configuration version that the medical director approved, and the AI system's own reference to that configuration where it has one;
- for `limited_practice`, the allowlist entries (AG-07); for `full_practice`, the full-practice grant and the reserved acts its legal review cleared (AA-05);
- the approving medical director (AG-02) and the approval time;
- the recorded legal and regulatory review for that mode (AG-05);
- the review policy and, for the practice modes, the co-review window (AG-10);
- the effective time, the expiry (AG-09) and the state: `active`, `paused`, `expired`, `revoked` or `superseded`;
- a grant identifier and a version number.

A grant version, once approved, SHALL NOT be edited. Every change SHALL create a new version that references its predecessor, with actor, reason and time.

#### Scenario: Failure: a write claims more authority than the chart's record
- **WHEN** a `consult.write` claims `full_practice` under a grant whose current version in openChart records `advice_only`
- **THEN** openChart refuses it with reason `mode_mismatch` and stores no clinical content

#### Scenario: Failure: someone edits an approved grant in place
- **WHEN** a user tries to change the configuration version of an approved grant version
- **THEN** the edit is refused, and only a new version approved by the medical director can carry the change

### Requirement: AG-02 Only the practice's medical director, a named human, approves or changes a grant
openChart SHALL record one medical director for each practice: a named human with an openChart account, designated by an audited act of a role decided in planning (design call AD-24). Only that person SHALL approve a grant version, widen it, resume it, record its legal review reference, or set its review policy and co-review window. The medical director, and any reduction under AG-08, MAY narrow or pause it. No AI system, agent, integration identity or other role SHALL approve, widen or resume a grant. Where no medical director is recorded, no grant SHALL be approved and the write path SHALL accept nothing.

#### Scenario: Failure: an AI agent tries to approve a grant
- **WHEN** an AI agent, or the AI system's integration identity, tries to approve or widen a grant
- **THEN** the action is refused and the grant is unchanged

#### Scenario: Failure: the practice has no medical director recorded
- **WHEN** an administrator tries to activate a grant for a practice with no medical director recorded
- **THEN** activation is refused

### Requirement: AG-03 There are three modes, advice only is the default, and they are built in order
A grant SHALL carry exactly one mode: `advice_only`, `limited_practice` or `full_practice` (ruling 59). A new grant SHALL default to `advice_only`. In `advice_only`, the AI system may inform, assess and recommend next steps; it may not prescribe, order, change a treatment plan or record a diagnosis of record (ruling 56). The modes SHALL be built in this order: `advice_only` first (Tier 1), then `limited_practice`, then `full_practice` (ruling 63). openChart SHALL NOT let a grant for a mode be approved on a deployment whose openChart lacks the build for that mode (design call AD-19).

#### Scenario: Failure: full practice is requested before it is built
- **WHEN** a medical director tries to approve a `full_practice` grant on an openChart deployment that has only the advice-only build
- **THEN** the approval is refused with a coded reason

### Requirement: AG-04 Each mode stays off until its three gates are met
openChart SHALL NOT activate a grant for a mode until all of the following are recorded for that mode (ruling 58 and the gates the owner set on 2026-11-14):
- **(a)** the medical director's approval of that mode's scope: for `advice_only`, the scope and the red-flag rules; for `limited_practice`, the allowlist; for `full_practice`, the full-practice grant;
- **(b)** a legal and regulatory review covering that mode (AG-05);
- **(c)** for `limited_practice` and `full_practice`, that openChart can accept an AI-authored order, prescription or diagnosis recorded with the authority it acted under: the clinical-acts foundation is ratified and built, and this change's Tier 2 is built for every act class in the grant's scope (AA-01).

A legal review covering one mode SHALL NOT satisfy gate (b) for another.

#### Scenario: Failure: limited practice without a legal review covering it
- **WHEN** a medical director tries to approve a `limited_practice` grant while the only recorded legal review covers `advice_only`
- **THEN** the approval is refused, and the grant stays at its prior mode

#### Scenario: Failure: a practice mode before the foundation exists
- **WHEN** a medical director tries to approve a `limited_practice` grant before the clinical-acts foundation is built
- **THEN** the approval is refused for gate (c)

### Requirement: AG-05 openChart records a reference to the legal and regulatory review for each mode, and states no legal rule itself
openChart SHALL record, for each mode it may activate, a reference to a legal and regulatory review: an opaque locator and SHA-256 digest of the review document, the mode or modes it covers, the act classes and act types it addresses, the reviewer named in it, the person who recorded the reference (the medical director), the recording time, and its expiry or re-review date. For `full_practice` and `limited_practice` it SHALL also record which reserved acts the review cleared, if any (AA-05).

openChart SHALL NOT encode any legal or regulatory rule as fact. The topics the recorded review must address are listed in `design.md` under "What the recorded legal and regulatory review must cover". openChart checks that a review is recorded, that it covers the mode, and that it is current. It does not judge the review's content.

#### Scenario: Failure: the review reference lacks a digest
- **WHEN** a medical director records a legal review reference with no document digest
- **THEN** the record is refused, and no grant may rely on it

#### Scenario: Failure: the legal review has expired
- **WHEN** the legal review a grant relies on passes its expiry
- **THEN** the grant stops accepting writes with reason `grant_expired` until a current review is recorded and the medical director approves a new version

### Requirement: AG-06 Every write is checked against the current grant, and anything missing, expired, paused, narrowed or mismatched fails closed
For every `consult.write` and `act.write`, openChart SHALL find the grant for the write's practice and source system, and SHALL refuse the write when any of these holds:

| Condition | Reason |
|---|---|
| No grant exists, or none is `active` for the time AC-09 or AA-03 sets | `no_current_grant` |
| The grant is `paused` | `grant_paused` |
| The grant, or the legal review it relies on, has expired | `grant_expired` |
| The grant is `revoked` | `grant_revoked` |
| The write names a grant version other than the one in force, or a configuration version or source authority reference other than the one that version records | `grant_mismatch` |
| The write's mode differs from the grant's mode | `mode_mismatch` |
| The write is not permitted in the grant's mode | `mode_not_permitted` |
| A named approver or legal review differs from the grant's | `approver_mismatch`, `legal_review_mismatch` |

A narrowing (AG-08) SHALL count: a write that relies on scope removed by a narrowing is refused. openChart SHALL record which grant version it checked in the receipt.

#### Scenario: Failure: the configuration version does not match
- **WHEN** a write names the current grant version but a configuration version the grant does not record
- **THEN** openChart refuses it with reason `grant_mismatch` and stores no clinical content

#### Scenario: Failure: an advice-only grant receives an act
- **WHEN** an `act.write` arrives for a practice whose grant is `advice_only`
- **THEN** openChart refuses it with reason `mode_not_permitted`

### Requirement: AG-07 Limited practice is an allowlist the medical director approves, and anything not listed goes to the human doctor
A `limited_practice` grant SHALL carry an allowlist (ruling 60). Each entry SHALL record an entry identifier, one act type with its act class, its conditions, and the standing order or protocol behind it, by reference. An entry MAY mark conditions that openChart can check from chart data; those are re-checked on each write (AA-04, design call AD-16). The medical director approves the allowlist as part of the grant version.

Anything not on the allowlist SHALL be refused with reason `allowlist_entry_unknown`, and the refusal SHALL be shown to the patient's doctor as an act that the AI system was not allowed to make (AA-12). A reserved act (AA-05) SHALL NOT be bound to an allowlist entry unless the grant's legal review cleared it.

#### Scenario: Failure: an act type not on the allowlist
- **WHEN** an AI system writes an act whose act type matches no entry on the current allowlist
- **THEN** openChart refuses it with reason `allowlist_entry_unknown`, and the patient's doctor sees the refused attempt

#### Scenario: Failure: an entry names a reserved act without clearance
- **WHEN** a medical director tries to add controlled-substance prescribing to an allowlist whose legal review does not clear it
- **THEN** the entry is refused

### Requirement: AG-08 The medical director can narrow or pause at once, and any reduction from any source applies at once
The medical director SHALL be able to narrow a grant (remove allowlist entries, lower the mode, shorten windows or add reserved acts) or pause it, in openChart, effective at once (ruling 59). A narrowing SHALL create a new grant version; a pause SHALL set the grant to `paused`. openChart SHALL send an `authority.notice` with `direction` `from_openchart` for every change to a grant, through AW-08.

openChart SHALL also apply at once an `authority.notice` from the AI system whose `change` is `paused` or `narrowed`, and SHALL record it as a reduction pending the medical director's review (design call AD-6). A notice can only reduce authority. Only the medical director's act in openChart SHALL widen or resume a grant. Pending AI acts on a narrowing or pause SHALL be handled under AA-11.

#### Scenario: Failure: a pause arrives from the AI system
- **WHEN** the AI system sends an `authority.notice` with `change` `paused` for an active grant
- **THEN** openChart pauses the grant at once, refuses later writes with reason `grant_paused`, and shows the medical director the pending reduction

#### Scenario: Failure: a notice tries to widen authority
- **WHEN** a notice from the AI system would add an allowlist entry or raise the mode
- **THEN** openChart refuses it with reason `notice_would_widen` and the grant is unchanged

### Requirement: AG-09 Grants and legal reviews expire, and nothing renews itself
Every grant version and every recorded legal review SHALL carry an expiry or re-review date set by the medical director (design call AD-10). On expiry the grant SHALL stop accepting writes. No grant, review or allowlist entry SHALL renew, extend or reactivate itself. Only a new version approved by the medical director SHALL restore it.

#### Scenario: Failure: a grant reaches its expiry
- **WHEN** an active grant reaches its expiry with no new version approved
- **THEN** openChart refuses later writes with reason `grant_expired` and sends an `authority.notice` with `change` `expired`

### Requirement: AG-10 A grant carries its review policy and, for the practice modes, its co-review window
A grant version SHALL NOT be approved without a review policy version that the medical director sets: the review sample rate and the always-review categories for consults (AC-07), and the review window for consults selected for review (AC-08). A grant version for `limited_practice` or `full_practice` SHALL NOT be approved without a co-review window for every act class in its scope (AA-07). No agent SHALL set or change either.

#### Scenario: Failure: an advice-only grant without a review policy
- **WHEN** a medical director tries to approve an `advice_only` grant with no review sample rate or always-review categories
- **THEN** the approval is refused

#### Scenario: Failure: a practice-mode grant without a co-review window
- **WHEN** a medical director tries to approve a `limited_practice` grant with no co-review window for one of its act classes
- **THEN** the approval is refused
