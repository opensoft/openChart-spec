## ADDED Requirements

### Requirement: OR-01 One generic order record covers laboratory, imaging, referral, procedure and other orders
openChart SHALL record a clinician's order as an act of class `order` with an order category (`laboratory`, `imaging`, `referral`, `procedure` or `other`; design call CD-18), a description of what is ordered, an optional coding from a practice-supplied code set, a priority (`routine`, `urgent`, `asap` or `stat`), and optionally an encounter, reason references to diagnoses of record, a reason text, an intended performer reference, instructions and a deferred release time. One record shape SHALL serve every category; a category outside the list SHALL be refused.

#### Scenario: A clinician orders a laboratory panel
- **WHEN** a clinician with order `sign` scope records and signs a routine laboratory order linked to a diagnosis
- **THEN** openChart stores one order with category `laboratory`, priority `routine` and the diagnosis reference, and it is `released`

#### Scenario: Failure: an unknown category
- **WHEN** a client submits an order with category `pharmacy`
- **THEN** openChart refuses it with a coded reason

### Requirement: OR-02 An order is released when signed unless a co-signature or a deferred release time holds it
When an order is signed, openChart SHALL set it to `released` at once, unless a `before_effect` co-signature requirement applies (CA-07) or its release time is in the future; then it SHALL be `pending_release` until the co-signature is recorded and the release time is reached. `released` SHALL mean the order is in force in openChart and may be acted on; `pending_release` SHALL mean it is signed and not yet in force. A `pending_release` order MAY be cancelled by its author or a clinician with order `sign` scope. A `released` order SHALL move only to `completed`, recorded by a person with order `complete` scope; to `discontinued`, recorded as a signed lifecycle record with a reason by a clinician with order `discontinue` scope; or to `entered_in_error` (CA-06).

#### Scenario: A deferred order releases on time
- **WHEN** a clinician signs an imaging order with a release time tomorrow
- **THEN** the order is `pending_release` until that time, and then `released`

#### Scenario: A released order is discontinued
- **WHEN** a clinician with `discontinue` scope discontinues a released referral, with a reason
- **THEN** the order becomes `discontinued`, with a signed lifecycle record naming the clinician, the time and the reason

#### Scenario: Failure: an unsigned order would be acted on
- **WHEN** a user tries to mark a `draft` or `pending_release` order `completed`
- **THEN** openChart refuses it and the order is unchanged

### Requirement: OR-03 A released order is never amended; a change is a discontinuation and a new order
openChart SHALL allow an amendment (a new signed version) of an order only while it is `pending_release` (design call CD-6). A change to a `released` order SHALL be recorded as a discontinuation of that order and a new order that references it; the two SHALL be linked both ways in provenance.

#### Scenario: A pending order is corrected
- **WHEN** a clinician amends the instructions of a `pending_release` order
- **THEN** version 2 is signed, references version 1, and stays `pending_release` or becomes `released` under OR-02

#### Scenario: Failure: a released order is amended
- **WHEN** a clinician tries to amend a `released` order
- **THEN** openChart refuses the amendment and offers to discontinue it and record a new order that references it

### Requirement: OR-04 openChart transmits no order and ingests no result in this change
In this change openChart SHALL NOT transmit an order to any laboratory, imaging service, referral recipient or other external performer, and SHALL NOT ingest results (design call CD-19). `released` SHALL mean in force within openChart only. Completion SHALL be an explicit act by a named person, never inferred from an external message. Order transmission and results ingestion each need a separately governed change.

#### Scenario: Failure: a plan adds order transmission
- **WHEN** a plan proposes sending released orders to an external laboratory
- **THEN** the plan is out of scope for this change, and the work waits for a separately governed change

#### Scenario: Failure: an external message would complete an order
- **WHEN** an external system sends a message claiming a released order is complete
- **THEN** openChart does not change the order, and completion waits for a named person's explicit act
