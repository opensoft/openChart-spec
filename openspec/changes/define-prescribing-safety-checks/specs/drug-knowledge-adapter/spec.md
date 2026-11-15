## ADDED Requirements

### Requirement: KA-01 openChart bundles no drug knowledge; each practice connects its own source
openChart SHALL bundle no drug knowledge base, interaction data, allergy cross-reference data or medication classification data (owner ruling 78). Each practice SHALL connect a source that it has licensed or verified, through the adapter contract (KA-02). openChart SHALL assert nothing about any vendor, product, public database, or its license, availability or fitness. Each MUST be verified by the practice before use (KA-03). Distributing any drug knowledge with openChart SHALL need license verification and a separately governed change.

#### Scenario: A clean installation has no source
- **WHEN** openChart is installed with no source connected
- **THEN** no drug knowledge is present, prescriptions can be drafted with every check shown as unavailable, and none can be signed (PG-01)

#### Scenario: Failure: a plan bundles a drug database
- **WHEN** a plan proposes shipping a drug interaction dataset inside openChart
- **THEN** the plan is out of scope until license verification and a separately governed change approve it

### Requirement: KA-02 A versioned adapter contract connects a source
openChart SHALL talk to a source only through contract `openchart-drug-knowledge-adapter/1.0`. Its schema is `contracts/openchart-drug-knowledge-adapter-1.0.schema.json`, `$id` `urn:openchart:contract:openchart-drug-knowledge-adapter:1.0`, identified by the SHA-256 recorded in `contracts/SHA256SUMS`. The contract SHALL provide these operations:
- **source identity:** a reference, a label, the version and the effective date;
- **capability declaration:** the operations and check kinds supported, the code systems accepted, a severity mapping onto openChart's scale, and a batch limit;
- **medication normalization:** to ingredients and classes;
- **allergy cross-reference:** by same ingredient or class cross-sensitivity;
- **interaction lookup:** for drug–drug, duplicate therapy and, where declared, drug–supplement interactions;
- **coded errors.**

Every result SHALL carry the source reference, version and effective date. A message with an unsupported MAJOR version SHALL be refused, and a breaking change SHALL need a new MAJOR version and digest.

#### Scenario: openChart reads a capability declaration
- **WHEN** a deployment connects a source
- **THEN** openChart requests and stores its capability declaration, validated against the schema at the recorded digest

#### Scenario: Failure: a result fails the schema
- **WHEN** an adapter returns a result that fails validation
- **THEN** openChart treats the source as unavailable for that check (KA-05), and stores the failure with a coded reason

### Requirement: KA-03 A source is usable only after the medical director records its verification
A connected source SHALL be usable for checks only after the medical director, as defined by `define-clinical-acts-foundation` AU-01, records a verification (design call PD-8). The verification SHALL hold:
- the source identity and version;
- the adapter identity and version;
- an opaque reference to the practice's own licence or permission evidence;
- the result of the adapter contract tests against the synthetic fixtures;
- an effective date and a review date;
- optionally, `free_text_agreement_ref`: an opaque reference to the agreement that counsel requires before free text may be sent to this source (KA-06, design call PD-20). Without it, no free text is sent.

openChart SHALL NOT judge the licence. It records the practice's attestation and shows it as practice-supplied. A new source version, a new adapter version or a passed review date SHALL need a new verification before the source is usable again.

#### Scenario: The medical director verifies a source
- **WHEN** the medical director records a verification with evidence, a passing contract test and a review date
- **THEN** the source becomes usable for checks from its effective date

#### Scenario: Failure: the source version changes
- **WHEN** the adapter reports a source version different from the verified one
- **THEN** the source is not usable until a new verification is recorded, and the gate treats it as not verified

### Requirement: KA-04 A source older than the practice's policy age counts as unavailable
The medical director SHALL set a currency policy: the maximum age of a source, measured from its declared effective date (design call PD-9). A source older than that age SHALL be treated as unavailable. Until a currency policy is set, no source SHALL be usable, so the gate is not met. openChart SHALL alert the medical director when a source becomes stale.

#### Scenario: A source goes stale
- **WHEN** a source's effective date passes the policy's maximum age
- **THEN** openChart treats it as unavailable, alerts the medical director, and every signing uses the gate's unavailable path (PG-02)

#### Scenario: Failure: no currency policy
- **WHEN** a deployment has a verified source and no currency policy
- **THEN** the source is not usable, and no prescription can be signed

### Requirement: KA-05 An adapter failure makes the source unavailable and is never read as "no alerts"
A timeout, an adapter error, a schema-invalid result, an unsupported version, or a result that omits a requested input SHALL make the source unavailable for that check, or for that input, and SHALL raise PC-02's warning for the input. openChart MUST NOT treat any of them as an empty result, and MUST NOT show "no alerts found" for a check that did not complete (design call PD-10).

#### Scenario: Failure: the adapter times out at signing
- **WHEN** the adapter does not answer the signing-time interaction lookup in time
- **THEN** the check is marked unavailable, no "no alerts" message appears, and the gate's unavailable path applies (PG-02)

#### Scenario: Failure: a result leaves out one medication
- **WHEN** an interaction result lists neither a finding for, nor a `not_checked` entry for, one input medication
- **THEN** openChart raises "could not be checked" for that medication

### Requirement: KA-06 Adapter requests carry codes only, free text only under a recorded agreement, and no patient identity
Requests to a source SHALL carry only codes, item references and a deployment reference (design calls PD-14 and PD-20). Normalized items sent back to the source SHALL carry ingredient and class codes, without labels. A free-text medication or allergen description, such as a patient's own wording, SHALL be sent only as an item's `free_text`, and only in a request that names the `free_text_agreement_ref` recorded in the source's verification (KA-03). Without that agreement, an uncoded entry SHALL NOT be sent and SHALL stay in openChart as "could not be checked" (PC-02). openChart SHALL send a coding only when its code system is one that the source's capability declaration lists (KA-02). A coding in any other system SHALL NOT be sent, and its entry SHALL stay local as "could not be checked". A coding's `version` SHALL be sent only as the version recorded for the practice-loaded code set that the coding references (`define-clinical-acts-foundation` CA-12), and a coding whose code set records no version SHALL be sent without one. A request whose coding carries any other version SHALL NOT be sent, and that entry SHALL stay local as "could not be checked". Item and allergen references SHALL be opaque identifiers that openChart mints. Requests SHALL carry no patient identifier, name, date of birth, contact detail or note text.

The schema enforces what a schema can: every object is closed; no message has a patient field; request items carry no label; a code holds no whitespace; a code system is a URI; a version is a token without spaces; and `free_text` requires the agreement reference. No schema pattern can tell a version from an identifier, so the version pattern only keeps out spaces. openChart enforces the rest at runtime: the declared-systems rule, the loaded-code-set version rule, and opaque references. The contract's fixtures and every test SHALL use clearly synthetic substance names, classes, codes and rules, and SHALL contain no real drug data.

#### Scenario: Failure: a request would carry the patient
- **WHEN** an implementation adds a patient reference to an interaction lookup request
- **THEN** the request fails the schema and is not sent

#### Scenario: Failure: patient wording would be sent without an agreement
- **WHEN** a patient-reported allergy is free text, and the source's verification records no free-text agreement
- **THEN** openChart does not send the text, a request carrying it would fail the schema, and the clinician sees "could not be checked" for that allergy

#### Scenario: Failure: patient words disguised as a coding
- **WHEN** an implementation sends a coding with system `urn:intake:patient-words` and code `Jane Roe rash pen 1980`, with no agreement reference
- **THEN** the request fails the schema, because a code may not contain whitespace, and nothing is sent

#### Scenario: Failure: a coding in an undeclared system
- **WHEN** an entry's coding uses a code system that the source's capability declaration does not list
- **THEN** openChart does not send it, and the clinician sees "could not be checked" for that entry

#### Scenario: Failure: an identifier placed in a coding's version
- **WHEN** an implementation puts a record number such as `MRN12345` into a coding's `version`, a value the schema's version pattern accepts
- **THEN** openChart does not send the request, because the value is not the version recorded for that coding's loaded code set, and the clinician sees "could not be checked" for that entry

#### Scenario: Failure: a fixture uses real drug data
- **WHEN** a contributor adds a fixture naming a real medicine or interaction
- **THEN** review rejects it, and the fixture is replaced with a synthetic one
