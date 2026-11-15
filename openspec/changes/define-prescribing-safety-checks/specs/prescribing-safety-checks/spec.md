## ADDED Requirements

### Requirement: PC-01 A check considers clinician-confirmed entries and patient-reported statements alike
Every prescribing-safety check SHALL take as inputs, for the patient:
- the prescription version being checked;
- every active clinician-confirmed allergy entry and medication list entry (SL-01, SL-02);
- every `released` openChart prescription;
- the latest accepted version of every active patient-reported allergy, medication and supplement statement, whether or not a clinician has reconciled it, reviewed it or marked it `clinician_verified` (design call PD-4).

A patient-reported entry MUST NOT be ignored because no clinician has confirmed it. Every alert that arises from a patient-reported or unconfirmed input SHALL say so. A `draft` or `refuted` entry SHALL NOT suppress a patient-reported statement of the same substance.

#### Scenario: A patient-reported allergy raises an alert
- **WHEN** a clinician drafts a prescription whose ingredient matches an allergy that the patient reported at intake and no clinician has confirmed
- **THEN** the check raises an allergy alert labelled as resting on a patient-reported allergy

#### Scenario: Failure: an unconfirmed report would be skipped
- **WHEN** a check would run only against clinician-confirmed entries
- **THEN** openChart includes the patient-reported statements, and the check record lists them as inputs

### Requirement: PC-02 An input that cannot be checked produces an explicit warning, never silence
For every input the source cannot recognize, resolve or check — uncoded or free-text entries, items the adapter reports as `not_recognized`, `ambiguous`, `uncoded_not_resolvable`, `kind_not_supported` or `outside_source_scope`, and every requested check kind the source did not run — openChart SHALL raise an explicit "could not be checked" warning that names the input or the check kind. A patient whose allergy status is not recorded (SL-01) SHALL raise an "allergy status not recorded" warning. These warnings SHALL be shown with the alerts, SHALL need the clinician's response under PC-06, and SHALL be stored in the check record. openChart MUST NOT skip any input silently, and MUST NOT present a check with such warnings as complete.

#### Scenario: A free-text medication cannot be normalized
- **WHEN** a patient-reported medication is free text that the source reports as `uncoded_not_resolvable`
- **THEN** the clinician sees "could not be checked" for that medication, and must respond to it before signing

#### Scenario: Failure: drug–supplement checking is not supported
- **WHEN** the source's capability declaration does not include `drug_supplement`, and the patient reports a supplement
- **THEN** the clinician sees that drug–supplement interactions were not checked for that supplement

### Requirement: PC-03 The first set of checks is allergy, drug–drug interaction and duplicate therapy
openChart SHALL run these checks (owner ruling 77):
- **allergy,** by ingredient and by class (`allergy_ingredient`, `allergy_class`), against every allergy input;
- **drug–drug interaction** (`drug_drug`), between the prescription and every medication input;
- **duplicate therapy** (`duplicate_therapy`), between the prescription and every medication input;
- **drug–supplement interaction** (`drug_supplement`), only where the connected source's capability declaration includes it. Otherwise PC-02's warning applies.

Dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, and paediatric and geriatric rules are out of scope. Each needs a later governed change. openChart SHALL NOT present any of them as checked.

#### Scenario: A drug–drug interaction is found
- **WHEN** a clinician drafts a prescription that the source finds interacts with a released prescription
- **THEN** openChart raises a `drug_drug` alert naming both items, with its severity and the source's text

#### Scenario: Failure: a later check kind would be implied
- **WHEN** the check finds no alerts
- **THEN** openChart states which check kinds ran and that dose range, drug–condition, pregnancy and lactation, renal and hepatic, and paediatric and geriatric rules were not checked

### Requirement: PC-04 Checks run when a prescription is drafted or changed, and again at signing
openChart SHALL run the checks when a prescription draft is created, after every change to it, and again at the moment of signing. The signing-time check SHALL be the one the gate relies on (PG-01). It SHALL be run against the exact content digest of the version being signed and against the inputs as they stand at that moment. A check result from before the latest change to the prescription or to any input SHALL be stale and SHALL NOT satisfy the gate.

#### Scenario: A check is re-run at signing
- **WHEN** a clinician signs a prescription an hour after drafting it, and an allergy was added in between
- **THEN** openChart re-runs the checks at signing, and the new allergy is considered

#### Scenario: Failure: a stale check would be relied on
- **WHEN** a prescription's dose text changed after its last check
- **THEN** the earlier check does not satisfy the gate, and a new check runs before the signature can complete

### Requirement: PC-05 Each alert has a severity on openChart's closed scale
openChart SHALL give each alert one severity on the closed scale `critical`, `high`, `moderate`, `low` or `info`. It SHALL map each source severity through the severity mapping in the adapter's capability declaration (KA-02). A source severity with no mapping SHALL be treated as `critical` (design call PD-5). An allergy match on the same ingredient against any active allergy input, whether clinician-confirmed or patient-reported, SHALL always be `critical`, whatever the source's severity.

#### Scenario: A same-ingredient allergy match
- **WHEN** the source reports a `same_ingredient` match with a severity it maps to `moderate`
- **THEN** openChart raises the alert as `critical`

#### Scenario: Failure: an unmapped severity
- **WHEN** a finding carries a source severity that the capability declaration does not map
- **THEN** openChart treats the alert as `critical`

### Requirement: PC-06 The clinician responds to every alert, and a critical alert needs its own explicit override
Before a prescription can be signed, the signing clinician SHALL respond to every alert and every "could not be checked" warning from the signing-time check. A response is one of these: change the prescription, which runs a new check; cancel it; or override with a recorded reason, given as a code with optional text (design call PD-6). Each `critical` alert SHALL need its own explicit override, with its own reason, and SHALL NOT be dismissed in bulk or by a default. Alerts below `critical`, and warnings, MAY be acknowledged together with one recorded reason. Every response SHALL record the clinician, the time and the reason.

#### Scenario: A clinician overrides a high alert with a reason
- **WHEN** a clinician overrides a `high` drug–drug alert with reason code `benefit_outweighs_risk`
- **THEN** the override is recorded with the clinician, time and reason, and signing may proceed if nothing else is unanswered

#### Scenario: Failure: a critical alert is dismissed in bulk
- **WHEN** a clinician selects "acknowledge all" while a `critical` allergy alert is open
- **THEN** the critical alert stays open, and signing is refused until it gets its own override with a reason

### Requirement: PC-07 Every check is recorded with its inputs, source, alerts and the clinician's response
openChart SHALL store each check as an immutable record attached to the prescription version's provenance. The record SHALL hold:
- the prescription act and version, and the content digest checked;
- every input, by reference and version, with its kind (clinician-confirmed, openChart prescription or patient-reported);
- the source reference, version and effective date, the adapter reference and version, and the capability declaration in force;
- the check kinds requested and run;
- every alert and warning, with severity and source text as shown;
- every response, with clinician, time and reason;
- the outcome, and whether it was a signing-time check.

The record MUST NOT be edited or deleted.

#### Scenario: An auditor reviews a signed prescription
- **WHEN** an authorized user opens a signed prescription's history
- **THEN** the signing-time check record shows its inputs, source and version, alerts, responses and outcome

#### Scenario: Failure: someone edits a check record
- **WHEN** a user or extension tries to change an override reason in a check record
- **THEN** openChart refuses it and the record is unchanged

### Requirement: PC-08 Alerts are labelled as advice, and the record names the clinician as the decision-maker
Every alert, warning and check result SHALL be labelled as decision support from the named source and version, advising the clinician. The prescription's record SHALL name the signing clinician as the person who made the prescribing decision. openChart SHALL NOT label a prescription as safe, approved or verified because of a check. A check with no alerts SHALL be shown as "no alerts found by <source> for the checks run", followed by the check kinds not run. This requirement is about records and labelling. It makes no legal claim about responsibility.

#### Scenario: No alerts are found
- **WHEN** a signing-time check finds no alerts or warnings
- **THEN** openChart shows "no alerts found" with the source, its version, the check kinds run and those not run, and does not call the prescription safe

#### Scenario: Failure: a display calls a prescription verified
- **WHEN** a view would label a checked prescription as verified or approved
- **THEN** openChart shows it as checked by the named source, with the signing clinician as the decision-maker
