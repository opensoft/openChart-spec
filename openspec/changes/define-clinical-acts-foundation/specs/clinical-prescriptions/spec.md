## ADDED Requirements

### Requirement: RX-01 A prescription records the clinician's prescribing decision
openChart SHALL record a prescription as an act of class `prescription`: the clinician's prescribing decision, with the medication as text and, optionally, a coding from a practice-supplied code set; a controlled-substance classification and its source (RX-03); dosage instructions as text and, optionally, a structured dose, route and frequency; and optionally a dispense quantity, refills, days of supply, whether substitution is allowed, an encounter, reason references to diagnoses of record and a deferred release time. Its lifecycle, release, amendment and discontinuation SHALL follow OR-02 and OR-03. Signing SHALL need prescription `sign` scope resting on a prescriber attestation in force (AU-03), and the prescribing-safety gate (RX-02).

#### Scenario: A clinician drafts a prescription
- **WHEN** a clinician with prescription `draft` scope records a prescription with medication text, classification and dosage instructions
- **THEN** openChart stores a `draft` prescription with those fields

#### Scenario: Failure: a prescription without dosage instructions
- **WHEN** a client submits a prescription with no dosage instructions
- **THEN** openChart refuses it with a coded reason

### Requirement: RX-02 No prescription is signed in a deployment where the prescribing-safety gate is not met
openChart SHALL refuse to sign a prescription, and SHALL refuse to sign a new version of one, in any deployment where the prescribing-safety gate is not met (owner ruling 74; design call CD-30). The gate SHALL be met only when all three of these hold:
- `define-prescribing-safety-checks` (not yet on main) is ratified;
- its checking capability is built and enabled in that deployment;
- the signing satisfies that change's signing-time conditions. Under its owner rulings 76 to 78 these include a connected, licensed or verified knowledge source and a completed check, with a recorded clinician-only path when the source is unavailable at signing.

Until `define-prescribing-safety-checks` is ratified, the gate SHALL NOT be met in any deployment. No setting, role, grant, co-signature or override in this change SHALL bypass the gate, and a refused signature SHALL leave the prescription `draft`, with the refusal recorded with a coded reason.

#### Scenario: Failure: a clinician signs a prescription before checking exists
- **WHEN** a clinician with prescription `sign` scope and a prescriber attestation in force tries to sign a prescription in a deployment where `define-prescribing-safety-checks` is not ratified, built and enabled
- **THEN** openChart refuses the signature with reason `prescribing_safety_gate_not_met`, the prescription stays `draft`, and nothing takes effect

#### Scenario: Failure: an administrator tries to switch the gate off
- **WHEN** a user with `System Manager` tries to disable the gate in a deployment
- **THEN** openChart refuses the change, and the gate still applies to every signature

### Requirement: RX-03 Every prescription carries a controlled-substance classification, and unknown counts as controlled
Every prescription SHALL carry a controlled-substance classification (`controlled`, `not_controlled` or `unknown`) and its source (`practice_code_set` or `clinician_entry`). openChart SHALL NOT determine a classification itself, and SHALL treat `unknown` as `controlled` under every rule that reads the classification. Until the owner decides through a governed change, openChart SHALL refuse to sign a prescription classified `controlled` or `unknown` (design call CD-20). openChart asserts no rule about controlled-substance prescribing.

#### Scenario: A practice code set supplies the classification
- **WHEN** a clinician selects a medication whose practice-supplied code-set entry marks it not controlled
- **THEN** the prescription records `not_controlled` with source `practice_code_set`

#### Scenario: Failure: a controlled or unknown prescription is signed
- **WHEN** a clinician tries to sign a prescription classified `unknown`
- **THEN** openChart refuses the signature with reason `controlled_classification_not_permitted`, and the prescription stays `draft`

### Requirement: RX-04 openChart transmits no prescription and records no dispense in this change
In this change openChart SHALL NOT transmit a prescription to a pharmacy or intermediary, SHALL NOT perform controlled-substance electronic prescribing, SHALL NOT produce any document or message intended for a pharmacy to dispense from, and SHALL NOT record dispensing (design call CD-21). Every prescription's transmission status SHALL be `none_recorded`. Electronic transmission, controlled-substance electronic prescribing and dispense states need a later governed change, which needs vendor and regulatory verification before it is drafted as buildable. openChart asserts no rule about them.

#### Scenario: Failure: a plan adds pharmacy transmission
- **WHEN** a plan proposes sending signed prescriptions to a pharmacy network
- **THEN** the plan is out of scope for this change, and the work waits for a later governed change with vendor and regulatory verification

#### Scenario: Failure: a client sets a transmission state
- **WHEN** a client submits a prescription with transmission status `transmitted`
- **THEN** openChart refuses it with a coded reason
