## ADDED Requirements

### Requirement: DX-01 A diagnosis of record is clinician-asserted, coded and signed
openChart SHALL record a diagnosis of record as an act of class `diagnosis_of_record` with one of two roles:
- `encounter_diagnosis`: references one encounter and MAY carry a rank, where rank 1 is the primary diagnosis for that encounter;
- `problem_list`: a condition on the patient's problem list, which persists across encounters and carries a clinical status (`active`, `recurrence`, `relapse`, `inactive`, `remission` or `resolved`).

Every diagnosis of record SHALL carry a coding from a practice-supplied code set (CA-12) and a verification status (`unconfirmed`, `provisional`, `differential`, `confirmed` or `refuted`), and MAY carry onset and abatement dates and a note. It SHALL be `final` only when signed by a clinician with diagnosis `sign` scope. A diagnosis without a coding SHALL NOT be signed; uncoded diagnostic reasoning belongs in a clinical note (design call CD-25). A change of clinical status, such as `active` to `resolved`, or of verification status, SHALL be an amendment (CA-05). Only an encounter diagnosis whose verification status is `confirmed` SHALL be published as a billable fact. An amendment that refutes a published diagnosis, or otherwise moves it away from `confirmed`, SHALL be retracted (PB-02, PB-03). This rule is owner ruling 87 (design call CD-33).

#### Scenario: A clinician resolves a problem-list condition
- **WHEN** a clinician amends an active problem-list condition to `resolved`, with a reason
- **THEN** version 2 carries `resolved` and the clinician's signature, and version 1 stays readable

#### Scenario: Failure: an uncoded diagnosis is signed
- **WHEN** a clinician tries to sign a diagnosis that has free text and no coding
- **THEN** openChart refuses the signature and the diagnosis stays `draft`

#### Scenario: Failure: an encounter diagnosis without an encounter
- **WHEN** a client submits an `encounter_diagnosis` that references no encounter
- **THEN** openChart refuses it with a coded reason

### Requirement: DX-02 Diagnoses of record stay distinct from patient-reported conditions
openChart SHALL keep every diagnosis of record distinct from every patient-reported condition statement, in storage, display and every read. A patient-reported condition SHALL NOT be shown, counted, published or exported as a diagnosis of record, and a diagnosis of record SHALL NOT be shown as patient-reported. A diagnosis created from a statement SHALL name it as derivation provenance (CA-11), and the statement SHALL stay patient-reported and unchanged.

#### Scenario: The chart shows both
- **WHEN** a patient has a patient-reported condition and a clinician-signed diagnosis with the same code
- **THEN** the chart shows two items, one labelled patient-reported and one labelled clinician diagnosis with its signer

#### Scenario: Failure: a statement is listed on the problem list
- **WHEN** a view would list a patient-reported condition among problem-list diagnoses
- **THEN** openChart omits it from that list and shows it only as patient-reported

### Requirement: DX-03 A procedure or service performed is coded, attributed and attached to an encounter
openChart SHALL record a procedure or service performed as an act of class `procedure_performed` that references one encounter and carries a coding from a practice-supplied code set, the time performed, the performer (a participant on the encounter), and optionally a quantity, a coded body site and a note. It SHALL be `final` only when signed by a clinician with procedure `sign` scope, and SHALL NOT be signed without a coding.

#### Scenario: A procedure is documented
- **WHEN** a clinician records and signs a procedure performed during an encounter
- **THEN** openChart stores it with its coding, time, performer and encounter, as `final`

#### Scenario: Failure: the performer is not on the encounter
- **WHEN** a client names a performer who is not a participant on the encounter
- **THEN** openChart refuses the procedure with a coded reason
