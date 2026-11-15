## ADDED Requirements

### Requirement: SL-01 openChart keeps a clinician-confirmed allergy and intolerance list
openChart SHALL keep, for each patient, a clinician-confirmed allergy and intolerance list. Each entry SHALL be an act of a new act class, `allergy_intolerance`, with:
- the substance, as text and, where available, a coding from a practice-supplied code set;
- a category (`medication`, `food`, `environment`, `biologic` or `unknown`);
- a criticality (`low`, `high` or `unable_to_assess`);
- a clinical status (`active`, `inactive` or `resolved`);
- a verification status (`unconfirmed`, `confirmed` or `refuted`);
- optionally, reactions as text and coding, and an onset date.

A clinician MAY also record an explicit "no known drug allergies" assertion, as a separate act type of the same class (design call PD-3). An empty list SHALL NOT mean "no known allergies": a patient with neither an entry nor that assertion SHALL be shown as "allergy status not recorded".

#### Scenario: A clinician confirms an allergy
- **WHEN** a clinician records and signs an active, confirmed allergy to a coded substance
- **THEN** the allergy list shows the entry as clinician-confirmed, with its signer, criticality and status

#### Scenario: Failure: an empty list would read as no allergies
- **WHEN** a patient has no allergy entry and no "no known drug allergies" assertion
- **THEN** the chart shows "allergy status not recorded", and every check warns of it (PC-02)

### Requirement: SL-02 openChart keeps a clinician-confirmed active medication list
openChart SHALL keep, for each patient, an active medication list made of two parts (design call PD-2):
- **List entries:** acts of a new act class, `medication_list_entry`, each with the medication as text and, where available, a coding; a kind (`prescription_from_elsewhere`, `over_the_counter`, `supplement` or `other`); dose and frequency as text; a status (`active`, `on_hold` or `stopped`); and optionally a start date and an end date;
- **openChart's own prescriptions:** every prescription under `define-clinical-acts-foundation` (not yet on main) whose status is `released`, included by reference and never copied into an entry.

A stopped or entered-in-error entry, and a prescription that is `completed` (not reachable in version 1; `define-clinical-acts-foundation` RX-01), `discontinued`, `cancelled` or `entered_in_error`, SHALL NOT be shown as active.

#### Scenario: The active list combines entries and prescriptions
- **WHEN** a patient has one active over-the-counter entry and one released openChart prescription
- **THEN** the active medication list shows both, the prescription by reference, each labelled with its source

#### Scenario: Failure: a discontinued prescription would stay on the list
- **WHEN** a clinician discontinues a released prescription
- **THEN** it leaves the active medication list at once

### Requirement: SL-03 The lists reuse the foundation's act model and define no second signing model
Allergy entries and medication list entries SHALL follow every rule of `define-clinical-acts-foundation`'s `clinical-act-record` and `clinical-authority` capabilities, including:
- an author type that accepts only `clinician` (CA-02);
- the documentation lifecycle `draft`, `final`, `amended`, `cancelled` and `entered_in_error` (CA-03);
- attested signing (CA-04);
- amendment as a new version (CA-05);
- entered-in-error handling (CA-06);
- provenance and audit (CA-08);
- role grants per act class (AU-02).

This change SHALL NOT define a second signing, amendment or authorship model. A new MINOR version of `openchart-clinical-act-content` SHALL add the two act classes, together with a boolean `checks_unavailable_at_signing` on prescription content (PG-02). It SHALL be published by a governed revision of `define-clinical-acts-foundation` once both changes are ratified (design call PD-1; tension PT-3).

#### Scenario: An allergy entry is amended
- **WHEN** a clinician changes a confirmed allergy's criticality
- **THEN** a new signed version supersedes the old one under CA-05, and the old version stays readable

#### Scenario: Failure: an unsigned allergy entry would count as confirmed
- **WHEN** an allergy entry is still `draft`
- **THEN** it is not shown as clinician-confirmed, and a check treats it as unconfirmed (PC-01)

### Requirement: SL-04 Patient-reported statements reach the lists only by an explicit, attributed clinician action
A clinician MAY reconcile a patient-reported medication, supplement or allergy statement into a list entry only by an explicit action, recorded as derivation provenance naming the statement and its version, under `define-clinical-acts-foundation` CA-11. Nothing SHALL be promoted automatically. The statement SHALL stay unchanged and patient-reported, as the ratified `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority" requires. A clinician MAY also record that a statement was reviewed and not added, with a reason. That record SHALL leave the statement unchanged, and SHALL NOT remove it from the inputs of a check (PC-01).

#### Scenario: A clinician reconciles a reported supplement
- **WHEN** a clinician reviews a patient-reported supplement statement and adds it to the medication list
- **THEN** a signed `medication_list_entry` of kind `supplement` names the statement and version as its source, and the statement stays patient-reported

#### Scenario: Failure: an intake submission would update the list
- **WHEN** an intake submission with a new allergy statement is accepted
- **THEN** no allergy entry is created or changed, and the statement appears as patient-reported until a clinician acts

### Requirement: SL-05 The chart shows confirmed entries and unreconciled reports together, each labelled
Wherever openChart shows the allergy list or the active medication list, it SHALL also show every active patient-reported allergy, medication and supplement statement that has not been reconciled into an entry. Each item SHALL be visibly labelled as clinician-confirmed, openChart prescription or patient-reported. The view SHALL hold on every client, mobile or workstation.

#### Scenario: A reported allergy appears beside confirmed ones
- **WHEN** a patient has one confirmed allergy and one unreconciled patient-reported allergy
- **THEN** both appear, labelled clinician-confirmed and patient-reported

#### Scenario: Failure: a report would be hidden
- **WHEN** a view would list only clinician-confirmed allergies
- **THEN** openChart also shows the unreconciled patient-reported allergies, labelled as such
