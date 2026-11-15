## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

These facts about what is built were checked at `opensoft/openChart-code` revision `30b9645`. Nothing else is assumed to exist.

- **DocTypes:**
  - `OC Patient` (`patient_name`, `date_of_birth`, `sex_recorded`; named `OC-PAT-#####`);
  - `OC Patient External Identifier`;
  - `OC Intake Submission`;
  - eight statement DocTypes: allergy, condition, document reference, goal, medication, observation, supplement and symptom.

  Every statement row carries `assertion_kind` (set to patient-reported by `open_chart.intake.core`), and a `verification_state` select whose options are `patient_reported` (the default) and `clinician_verified`. No code path sets `clinician_verified` (tension CT-3).
- **API:** `open_chart.api.v1` exposes `submit`, `amend`, `read_submission` and `register_external_identifier`. Every write is gated to `System Manager`. Controllers derived from `GuardedDocument` reject writes made without the API's guard flag (`OC-DIRECT-WRITE`).
- **Roles:** no clinician, nurse or medical-director role exists.
- **Not built:** encounters, notes, diagnoses of record, procedures, orders and prescriptions. There is no practice or tenant record, and no code-set store.

**Related drafts, none on main**, read at these heads:
- `define-ai-authored-clinical-records` (openChart-spec#4) lists this change as its required prerequisite, with twelve minimum contents (checked below). It was first read at `dbb1fc5`. Its rulings, prerequisite list and status names were last re-read at `079dd36`.
- `define-openpractice-boundary` (openChart-spec#2, `e7c3090`) has CF-01 to CF-06 and Open Question 2.
- `define-clinical-message-inbox` (openChart-spec#3) has MI-12, MI-14 and Open Question 11. It was first read at `eda4b08`; its Decision 15, MT-17 to MT-22 and MD-31 were read at `e644fb3`.
- In `opensoft/openPractice-spec`, `define-mvp-practice-foundation` (PR #2, `fecc81e`) has `ehr-boundary` EB-13 to EB-20 and owns the schema `openpractice-ehr-clinical-facts-1.0.schema.json`. That schema's SHA-256 is `6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec`, which matches its `contracts/SHA256SUMS` and PL-04.
- `ideation/review/openpractice-framing-decisions.md` FD-11 is read from that repository's `main`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template at revision `d20de75`. There is nothing ratified to check against. This design checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements instead. **Planning for every feature of this change is blocked until a constitution is adopted.**

## Owner rulings

Every row is a ruling by **Brett Heap**. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`. The numbering is shared with the other openChart and openPractice changes.

| # | Date | Ruling | Governs |
|---|---|---|---|
| 31 | 2026-11-14 | openPractice is the system of record for the administrative appointment. The EHR owns the encounter and keeps an appointment reference if needed. The 1.0 contracts carry no appointment operations. (Recorded in `define-openpractice-boundary`.) | EN-02 |
| 34 | 2026-11-14 | openChart is the doctor's clinical interface. openPractice is the administrative gateway and holds no clinical content. | PB-02 (references only), PB-04 |
| 35 | 2026-11-14 | For now the physician uses openChart, on mobile or workstation. | EN-06; no requirement depends on a device |
| 62 | 2026-11-14 | When the AI practice modes are someday enabled, every AI order, prescription or diagnosis gets clinician co-review. | CA-07: the co-signature hook takes a later source without redesign |
| 67 | 2026-11-15 | No AI is granted clinical authority now. AI-authored orders, prescriptions and diagnoses stay specified, and off, in `define-ai-authored-clinical-records`. As that change records the ruling, the ratified texts stand, among them openChart intake's bar on any prescription, diagnosis or order created by an intake, API response or extension event. | CA-02, AU-05; CT-1. For additions to the chart, ruling 80 supersedes the first sentence of ruling 67 as the private companion change records it. The rest of ruling 67 stands: limited and full practice stay specified and off. Ruling 80 does not give any AI decision authority: its clause 19 keeps the rule that no AI holds decision authority today |
| 72 | 2026-11-15 | "Draft the openChart clinical-acts foundation change too." | This change |
| 73 | 2026-11-15 | The foundation's scope is encounters, clinical notes, diagnoses, procedures, orders, prescriptions, and authorship, signing and amendment. Left for later changes: results ingestion, care plans and treatment-plan records, immunizations, clinical decision support, and electronic transmission of prescriptions to pharmacies. | The scope; Non-Goals; CT-6, CT-8 |
| 74 | 2026-11-15 | The prescription record is specified in this change, but the prescription feature is not buildable until allergy and interaction checking is specified. A prescription cannot be signed in any deployment where that gate is not met. | RX-02; tasks §2.4 and §3.1; "Required later change" |
| 75 | 2026-11-15 | "Draft the allergy and interaction checking change too." | `define-prescribing-safety-checks`, being drafted |
| 76 | 2026-11-15 | For `define-prescribing-safety-checks`: when the knowledge source is unavailable at signing, a clinician may sign only with a recorded statement that checks were unavailable and that a manual review was done. The prescription is flagged and re-checked when the source returns. A non-clinician author, including any future AI author, can never use that path. | RX-02 (through that change) |
| 77 | 2026-11-15 | For `define-prescribing-safety-checks`: the first checks are allergy, drug–drug interaction and duplicate therapy, plus drug–supplement interaction only where the knowledge source declares support. Later: dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, paediatric and geriatric rules. | "Required later change" |
| 78 | 2026-11-15 | For `define-prescribing-safety-checks`: openChart bundles no drug knowledge. Each practice connects a licensed or verified source through the adapter contract, and no prescription can be signed without one. | RX-02 (through that change); CA-12 (same principle for code sets) |
| 80 | 2026-11-15 | "The rule in one line: anyone or anything the chart can identify may add to it, the chart records exactly where each addition came from, and only a decision by someone authorized to make it counts as a decision." The owner's statement and the wording he approved, with the words "approve 80. accept your recs for 136-150", are reproduced in "Ruling 80" below, in the wording for public repositories. | AN-01 to AN-14; CA-01 to CA-14; AU-01 to AU-07; DX-01, DX-03, EN-04, OR-02, PB-04; the content contract (see "Ruling 80", "Where rulings 80 and 151 are encoded") |
| 82 | 2026-11-15 | For `define-prescribing-safety-checks`: "A verified source that is stale or down uses the outage path, with the medical director alerted. Signing stops after a staleness limit set by policy. A practice that never had a verified source cannot sign." | RX-02 (through that change); "Required later change" item 7 |
| 83 | 2026-11-15 | Asked whether prescriptions for controlled substances, or with an unknown classification, should be refused in this change: "Yes. Controlled-substance prescribing goes into a later change alongside electronic prescribing, where its regulatory requirements can be handled properly." | RX-03, CD-20; Non-Goals; Open Question 7, closed; "Required later change" item 7 |
| 84 | 2026-11-15 | Asked: "openChart's ratified text says no 'API response' shall create a prescription, diagnosis or order. Read broadly, that would block a clinician signing through the API, and block patient-reported allergies from triggering safety alerts." Accepted: "Read it narrowly: it bars automatic creation from intake, and an alert to the clinician isn't a treatment recommendation. Add a small clarifying amendment to the ratified text, so it can't be misread later." | CT-1, settled; the amendment's wording is proposed under "Proposed clarifying amendment (ruling 84)" |
| 85 | 2026-11-15 | Asked about the foundation leading to several features in order, where the protocol says one change, one feature: "Allow the same ordered multi-feature exception you gave openPractice in ruling 1." | tasks §3; CT-14, settled; CD-31 |
| 87 | 2026-11-15 | On which diagnoses openChart publishes to openPractice: "Only confirmed ones. If a published diagnosis is later refuted, a retraction is sent." | PB-02, PB-03, PB-04, DX-01; CD-33 |
| 88 | 2026-11-15 | On retractions after a patient link is revoked or superseded: "Yes. Retractions of facts already published under that link are delivered, as pointers only. No new facts and no reads are served. Otherwise openPractice keeps billing withdrawn facts." | PB-03; CT-15, settled; CD-35 |
| 89 | 2026-11-15 | On the missing retraction reason in `openpractice-ehr-clinical-facts/1.0`: "Add a retraction reason code to the contract now, while 1.0 is still unratified. That is a small follow-up PR in openPractice-spec, …" (the rest of the sentence concerns an openPractice erratum). | CT-16, which stays recorded until that follow-up lands; CD-36 |
| 90 | 2026-11-15 | Recorded in `define-ai-authored-clinical-records`, on quarantining every consult that fails an authorization check: "Yes. Whatever the patient was told should be in front of a clinician, whichever check failed." | AN-01: that writing path's own quarantine applies instead of the identification refusal |
| 92 | 2026-11-15 | On where inbox authority lives: "In the foundation's single grant model, set by the medical director. Clinical roles and authority become their own small first feature, so the inbox does not wait for encounters and notes." | AU-06; feature (1); CD-39 to CD-41 |
| 93 | 2026-11-15 | On a follow-up pull request to openPractice-spec for the merged, unratified openPractice drafts: "Yes, one draft PR carrying: the agent operations Hermes lacks and the consent check; a verifiable entitlement; a clinician-acknowledged status; the representative's relationship and authority; the retraction reason code; …" | CT-16. This change's own rule until that follow-up lands and this change is re-pinned to it: PB-03 keeps using `clinical_fact.entered_in_error`, and CT-16 stays recorded. |
| 98 | 2026-11-15 | On confirming the first medical director: "A second named person confirms; a one-administrator practice records licence verification against the board's public record." | AU-01; CD-38; tasks §2.6 |
| 151 | 2026-11-15 | Made after ruling 80 was approved, about its clause 12 and every medical decision. His words are reproduced in "Ruling 80", under "Ruling 151". Where it and a clause of ruling 80 differ, ruling 151 governs. | CA-04, CA-05, CA-06, CA-07, CA-08, CA-14, AU-01 to AU-05, AU-07, AN-02, AN-07, AN-08, AN-11; the content contract (sign-off evidence) |

Rulings 76 to 78, 82 and 83 belong to `define-prescribing-safety-checks`. They are listed here because RX-02 defers to that change's signing-time conditions, and RX-03 refuses the classifications that ruling 83 refuses. Rulings 79 to 98 were made together on 2026-11-15, when Brett Heap accepted the recommended form of every numbered decision except 80; his words were "accept recomendations. on all but 80". Each row quotes the recommendation he accepted, and the words outside the quotation marks name the question it answered. He ruled decision 80 later that day, as ruling 80, and added ruling 151 to it; both are reproduced in "Ruling 80" below. The rows above are the ones that touch this change.

## Ruling 80

Owner ruling 80 was made by Brett Heap, product owner, on 2026-11-15. Below are sections 1 to 4 of its record, verbatim. This is a public repository, so sections 3 and 4 hold the forms its record gives for public repositories. Two sentences of the approved wording describe a rule of a private companion repository, and they are recorded in full in the private companion changes. Everything else is identical. Clauses are cited as "ruling 80, clause N".

### 1. The owner's statement (his words, verbatim)

"for 80, we want the ai or any system to be able to write into a chart. our july rule is not good. lets change the rule so that any system or human that adds to a chart must be identifies. for the ai, that is the openWallet. for a device, that should be make/model/serial or a medical asset/device ID. This is what is important that we have the timestamp and where the information came from, what added it. Then if the added item to a chart is a decision, then that needs to be regulated by the practice authority of the decision maker. if a system is adding this on behalf of another system or human, that needs to be documented. if the human or system making the decision is not authorized to make that clinical decision, then it still is entered into the chart, but as recomendation not decision and clearly identified as not authorized decision."

### 2. His instruction (verbatim)

"for 80, reorganize this and make it more complete. then bring to me to read and approve"

### 3. The approved wording

He approved the wording below, exactly as it was put to him, with the words "approve 80. accept your recs for 136-150" (2026-11-15). Clauses marked *(added)* were added in the reorganization he asked for; everything else restates his statement. The marks are part of what he approved and stay.

**The rule in one line:** anyone or anything the chart can identify may add to it, the chart records exactly where each addition came from, and only a decision by someone authorized to make it counts as a decision.

**A. Who may add**
1. Any human or system may add to a patient's chart: a clinician, other staff, the patient, an AI, a device or another system. [One sentence of the approved wording stands here. It names an earlier rule of a private companion repository, which this ruling replaces in part, and is recorded in full in that repository's change.]
2. Nothing is added unless the chart can identify what is adding it. An addition it cannot identify is refused, and nothing is stored. *(added)*

**B. How each is identified**

| Who or what | Identified by |
|---|---|
| A clinician or other staff member | Their own named account in the chart *(added)* |
| The patient or their representative | The verified link they come through *(added)* |
| An AI | Its openWallet ID, plus the model and version that produced the content *(model and version added)* |
| A device | Its make, model and serial number, or a medical asset or device ID the chart can resolve to them |
| Any other system: an app, an integration, a relay | Its registered system identity and who operates it *(added)* |

3. Every system is registered with the practice before it can add, and the practice can suspend any system or device at once. *(added)*

**C. What every addition records**

4. **When:** the time the chart received it, and the time the information itself arose where that differs, such as when a reading was taken.
5. **Where the information came from:** the patient's own words, a device reading, an AI consult, a clinician's observation, another organization's record or an earlier chart entry, with a reference to it.
6. **What added it:** the human or system that wrote it into the chart.
7. **On whose behalf:** when a system adds something for another system or a human, the chart records both, and every hand it passed through.
8. This record is permanent and visible to anyone who can read the chart. Nothing in it is edited or deleted; a correction is a new dated addition that points to the old one. *(added)*

**D. Information and decisions**

9. Every addition is either information or a decision. *(added)*
   - Information is an observation, a reading, a statement, a message, a summary or a recommendation.
   - A decision changes the patient's care or what the chart holds as established: a diagnosis, an order, a prescription, a referral, a treatment plan or a sign-off.
   - The chart keeps the list of what counts as a decision.
10. Information needs only the identification above.
11. A decision counts as a decision only when its decision maker held the practice authority for that kind of decision at that moment. The chart records the authority each decision rested on.
    - For a human, that is their licence and what the medical director has granted them.
    - For an AI, it is the mode and scope the medical director has approved for it.
    - A device or a plain integration holds none.
12. When a system adds a decision on someone's behalf, authority is judged on the decision maker, never on the system that carried it. The decision counts as theirs only when the chart can confirm they made it, by their own sign-off or an approval of theirs it can check. Otherwise it is entered as the carrying system's recommendation. *(added)*

**E. A decision made without authority**

13. It is still entered in the chart, in full, as a recommendation and not a decision. Wherever it is shown, it is clearly marked "not an authorized decision" and says which authority was missing.
14. It has no effect. Nothing is ordered, prescribed, sent, billed or treated as established because of it. *(added)*
15. Whoever or whatever submitted it is told at once that it was entered as a recommendation. *(added)*
16. It goes in front of a clinician who holds the authority. They can adopt it, which creates a new decision of their own that points back to it, or decline it. Either way the recommendation stays in the chart as written. *(added)*
17. This applies to humans and systems alike: a staff member who enters an order they are not authorized to give is treated the same way as an AI.

**F. What does not change**

18. Missing authority is never a reason to refuse an addition. These still are: it cannot be identified, the patient cannot be matched, the content is malformed or test data, or the practice has suspended the writer. *(added)*
19. An AI holds no decision authority today. Advice only is the only mode that can be switched on, and limited and full practice stay specified and off (ruling 67). So everything an AI adds now is information or a recommendation.
20. An AI never manages an emergency, and the urgent hand-off to a human stays as it is.
21. Consent, the patient's link, the medical director's pause and narrowing, and clinician review of what an AI told a patient all still apply.
22. [Clause 22 of the approved wording stands here. It keeps two other parts of that private rule as they are, does not bear on the chart, and is recorded in full in the private companion change.]

### 4. What it overrides

It supersedes, for additions to the chart, the first sentence of ruling 67 as the private companion change records it. The rest of ruling 67 stands: limited and full practice stay specified and off.

### Ruling 151

Source: Brett Heap, product owner, 2026-11-15, after "approve 80". His words, verbatim:

"for 12, and any medical decision we need the practitioner to sign off. so we need a logged in user that we use their openWallet and openSig to sign and validate that entry. the openWallet will have the verification of license and the openSig will attest that it is from that wallet."

"12" is clause 12 of the approved wording. These are his words and they are not reorganized. Where ruling 151 and a clause of ruling 80 differ, ruling 151 is the later ruling and governs.

### Where rulings 80 and 151 are encoded

- `chart-additions` AN-01 to AN-14: who may add, identification, registration and suspension, provenance, information and decisions, decisions made on someone's behalf, the recommendation record, its receipt and review, what is still refused, devices, and how drafts relate to recommendations.
- `clinical-act-record`: CA-01 to CA-14, CA-04 being the practitioner's sign-off of ruling 151.
- `clinical-authority`: AU-01 to AU-06, and AU-07, the binding of a practitioner's account to their wallet.
- `clinical-diagnoses-and-procedures` DX-01 and DX-03, `clinical-encounters` EN-04, `clinical-orders` OR-02 and `clinical-acts-publication` PB-04.
- The content contract `openchart-clinical-act-content/1.0`: party kinds and external parties, provenance, the sign-off evidence and statement on signatures and lifecycle events, the recommendation record and the information record.
- Decision 19 below; design calls CD-42 to CD-64; tensions CT-17 to CT-22; Open Questions 8 to 22.

## Goals / Non-Goals

**Goals:**

- Give openChart a clinical record that any identified human or system may add to. It records where each addition came from, only a practitioner's authorized sign-off makes a decision (rulings 80 and 151), and its authorship, signing, amendment, entered-in-error, co-signature and audit rules are the same for every act class.
- Make the record the base that `define-ai-authored-clinical-records` Tier 2 builds on, without redesign: an author type field, an authority-basis reference, an act-type registry with its flags, a co-signature hook and published content schemas.
- Replace the "no billable facts" placeholder of `define-openpractice-boundary` CF-06 with signed, final encounter facts, published by reference with forward-only corrections, without editing that change.
- Honor the ratified rule that intake confers no clinician authority. Clinician records come from patient-reported content only by an explicit, attributed clinician action.
- Fail closed wherever a ruling is silent and the consequence is clinical.

**Non-Goals (ruling 73 and the brief):**

| Out of scope | Pointer |
|---|---|
| Results ingestion | A later governed change (ruling 73). OR-04 refuses completion from external messages. |
| Care plans and treatment-plan records | A later governed change (ruling 73). Tier 2's `treatment_plan_change` stays unsupported (CT-6). |
| Immunizations | A later governed change (ruling 73). |
| Clinical decision support | A later governed change (ruling 73). The narrow prescribing-safety checks are the required change `define-prescribing-safety-checks` (rulings 74 and 75). |
| Electronic transmission of prescriptions and controlled-substance electronic prescribing | A later governed change that needs vendor and regulatory verification (ruling 73; RX-04). |
| Controlled-substance prescribing | A later change alongside electronic prescribing (ruling 83). Until then it is refused (RX-03). |
| Order transmission to external performers | A later governed change (OR-04, CD-19). |
| AI authorship | `define-ai-authored-clinical-records` Tier 2 (ruling 67), after Open Question 12. Until then, an AI's act content is a recommendation record (AN-09). |
| A path for device data | A later governed change (AN-13; Open Question 8). |
| openWallet's licence verification and openSig's attestation | openWallet and openSig, through their own governed changes (CT-20; Open Questions 9 and 11). This change only consumes them. |
| Billing, charge capture and coding validation | openPractice (`define-mvp-practice-foundation`; `define-openpractice-boundary` CF-05). openChart validates only that a code exists in a loaded code set (CA-12). |
| Adopting the constitution, or changing any ratified text | Separate governance |

## Decisions

### 1. One act model, one content schema

Six act classes share one envelope (CA-01, CD-1).

| Act class | Content | FHIR R4-compatible resource |
|---|---|---|
| `encounter` | types, period, participants, location, optional appointment reference, reasons | Encounter |
| `clinical_note` | encounter, note kind and type, text, addendum link, attachments by digest | DocumentReference (CD-26) |
| `diagnosis_of_record` | role (`encounter_diagnosis` or `problem_list`), coding, verification and clinical status, rank, dates | Condition |
| `procedure_performed` | encounter, coding, time, performer, quantity, body site | Procedure |
| `order` | category, text, optional coding, priority, reasons, intended performer, release time | ServiceRequest |
| `prescription` | medication, controlled-substance classification, dosage, quantity, refills, release time, transmission status | MedicationRequest |

The envelope holds:
- act identifier and version, class and type, and the openChart patient triple;
- status, author and recording time;
- signatures, amendment links and the co-signature requirement;
- derivation provenance, the restricted mark and lifecycle events.

`contracts/openchart-clinical-act-content-1.0.schema.json` is the canonical representation of one act version, one recommendation record and one information record, told apart by `record_kind`. It follows the convention of the sibling contracts: JSON Schema draft 2020-12, a URN `$id`, closed objects and `contracts/SHA256SUMS`. It is pinned by digest. `contracts/examples/` holds 77 synthetic fixtures, 27 that must validate and 50 that must fail, each for one reason stated in `examples/expected-failures.json`. `contracts/selftest.py` checks them, and checks that each invalid fixture fails with exactly one error. It passes on jsonschema 4.10.3 and 4.26.0 (task 1.2).

Each class's content is a named definition (`$defs/encounterContent` and so on), so a MINOR version of `openchart-ai-clinical-record-write` can pin it for `act_content` (CD-28).

### 2. Author type, the writer, and the hook for Tier 2

Every act version carries an author type, the author's reference, role and authority basis (CA-02). An act's author type is `clinician`: a named human with an openChart clinical role grant, which covers the `clinician` and `nurse` roles, as MI-12 does (CD-3). Under ruling 80, act content from any other author is not refused: it is entered as a recommendation record that names its author by `kind` (AN-02, AN-09). Every addition, an act included, also names its writer and every party on whose behalf it was written (AN-04). The authority basis is the role grant and its version.

`define-ai-authored-clinical-records` Tier 2 would add the author type `ai` for acts, with an authority basis pointing at its own grant, in a new MINOR version of both contracts and through its own governed change. It can do so only once the owner answers Open Question 12. Until then, an AI's act content is a recommendation record. Nothing in this change's act model needs to change for that.

### 3. Lifecycles

`signed` is an event, not a resting status (CD-4). It moves a draft to `final` (documentation classes), or to `pending_release` or `released` (orders and prescriptions).

| Class | Resting statuses | FHIR status mapping (contract level; to be checked in planning against the FHIR R4 specification) |
|---|---|---|
| `encounter` | `in_progress`, `final`, `amended`, `cancelled`, `entered_in_error` | Encounter.status: `in-progress`; `finished`; `finished`; `cancelled`; `entered-in-error` |
| `clinical_note` | `draft`, `final`, `amended`, `cancelled`, `entered_in_error` | DocumentReference.docStatus: `preliminary`; `final`; `amended`; not exposed; `entered-in-error` |
| `diagnosis_of_record` | as for notes | Condition.verificationStatus from content; `entered-in-error` when entered in error |
| `procedure_performed` | as for notes | Procedure.status: not exposed while draft; `completed`; `completed`; not exposed; `entered-in-error` |
| `order` | `draft`, `pending_release`, `released`, `completed`, `discontinued`, `cancelled`, `entered_in_error` | ServiceRequest.status: `draft`; `on-hold`; `active`; `completed`; `revoked`; `revoked`; `entered-in-error` |
| `prescription` | as for orders | MedicationRequest.status: `draft`; `on-hold`; `active`; `completed`; `stopped`; `cancelled`; `entered-in-error` |

A lifecycle change appends an attributed, dated event. Content changes only by a new version (CA-05).

### 4. Signing: the practitioner's sign-off (ruling 151)

A signature binds these items (CA-04, CD-9, CD-48):
- the signer and the signer's role;
- the role grant and its version;
- a coded attestation statement and its version, whose wording the medical director maintains per act class;
- the time;
- the SHA-256 of the RFC 8785 canonical JSON of the content signed;
- ruling 151's sign-off evidence: the `openwallet_id`, the licence verification relied on, the openSig attestation, the SHA-256 of the provenance, the custody model of the key that signed, and the check's result.

The attestation statement (CD-9) is the practice's coded wording of what the signer attests. The openSig attestation is ruling 151's proof that the signature is from the wallet, made over the sign-off statement: the act and version, the patient, the class and type, the action, the signature role, the signer, the attestation, both digests, the time and a single-use challenge issued at re-authentication (CD-53). openChart requires re-authentication at the moment of signing; the mechanism is decided in planning (CD-10). The practitioner signs off in their own logged-in session (CD-52), with a wallet bound to their account in their own session (AU-07) and a key whose custody evidences that they acted (CD-48). A discontinuation, an entered-in-error mark, a co-signature and the cancellation of a signed order carry the same evidence on their lifecycle events. Authority is checked first. A failure the author can cure by trying again leaves the draft open, and a failure of authority enters the content as a recommendation tied to the draft. Neither is a refusal, and neither cancels the draft (AN-14, Decision 19).

### 5. Amendment, entered in error and drafts

- **Amendment.** A new version references its predecessor, states a reason and carries its own author and signature. Any clinician with sign scope for the class may amend. Every prior version stays readable (CA-05, CD-5).
- **Released orders and prescriptions** are never amended. A change is a discontinuation plus a new act (OR-03, CD-6).
- **Entered in error** is the void. It is marked by the author, a clinician with sign scope, or the medical director, with a coded reason. Content stays for audit (CA-06, CD-7).
- **Drafts** may be revised before they are submitted, with every revision audited; a draft is not yet an addition (CD-60). An abandoned draft is `cancelled`, never deleted (CD-8). A failed sign-off never cancels a draft or an encounter (AN-14, CD-46).

### 6. The co-signature hook (ruling 62)

A co-signature requirement attaches to one act version (CA-07, CD-11). It records:
- its source;
- its mode: `before_effect`, where the act is held as `pending_release` (orders and prescriptions only in this change), or `after_the_fact`;
- a due time;
- a co-signer, who is a named clinician other than the author with co-sign scope;
- one outcome: co-signed, amended by the co-signer, or entered in error.

A co-signature adds the co-signer's signature and a `cosigned` event, both carrying the co-signer's sign-off evidence. While a `before_effect` requirement is pending or escalated, the act is never `released`, `completed` or `discontinued`; the contract enforces both.

When the due time passes, the requirement escalates to the medical director and keeps alerting. It is never closed by a timer, a default or an agent.

In this change the only source is the author's role grant, for example a supervised clinician or a nurse. This maps onto `define-ai-authored-clinical-records` AA-07 and AA-08 one for one:

| AA-07 / AA-08 | This hook |
|---|---|
| Queue at once, with a due time from the grant's window | Requirement with mode `after_the_fact` and due time = signing time + window |
| Confirm | Outcome `cosigned` |
| Amend: a new, dated, clinician-authored act that visibly supersedes the AI act | Outcome: an amendment by the co-signer (CA-05). A new version may have a different author. |
| Void | Outcome: entered in error (CA-06) |
| Overdue escalates to the medical director, re-alerts, never closed by default | Escalation rule of CA-07 |
| No AI or agent co-reviews; an attempt is a recommendation | AU-05, AN-09 |

Tier 2 adds its authority grant as a second `source` value in a MINOR version. An encounter whose signature has an open co-signature requirement is not published until it is co-signed (PB-04).

### 7. Authority

- **Roles.** openChart defines two roles, `clinician` and `nurse`, plus a medical director designation: one per practice, designated by an audited act of an administrative role named in planning (AU-01, CD-12).
- **Independence (CD-34).** No single account can reach clinical signing on its own say-so:
  - the designating account is never the designee;
  - the designee's `clinician` role rests on a licensure attestation recorded by another named human;
  - nobody records an attestation about themselves (AU-03);
  - a grant the medical director records for themselves is flagged `self_granted`, rests on an independently recorded attestation, is shown on every act signed under it, and is listed for the administrative role (AU-02).
- **The first medical director.** One audited bootstrap act by the designating account records three things: the designee's licensure attestation, the `clinician` role and the designation. The role confers no act-class authority, so the first medical director then self-grants each act class under the rule above.
- **Confirming the first designation (ruling 98; CD-38).** A second named human, neither the designating account nor the designee, confirms the first designation. A practice with only one administrator instead records a licence verification against the licensing board's public record. Designations, attestations and self-grants are listed for the administrative role and for the medical director once one exists. This closes the one-person-two-accounts path to prescribing.
- **No medical director, nothing signable.** With no medical director, no grant can be recorded, so nothing can be signed.
- **Inbox scopes (AU-06, ruling 92; CD-39, CD-40).** As ruling 92 directs, the single grant model, set by the medical director, also carries the clinical message inbox's scopes. None of them reaches an act:
  - ownership: actions `own`, `acknowledge`, `reassign`, `raise`, `return`, `split` and `close` over `clinical_inbox_item`, in a `physician` or `nurse` lane, with the medical director's nurse-lane scope for the nurse lane. A `physician`-lane grant goes only to a holder of the `clinician` role, and a nurse's grants stay in the nurse lane and its scope;
  - patient reply: action `reply` over `clinical_communication`, per role and lane, on an attestation;
  - clinical-need markers: actions `mark` and `withdraw` over `clinical_need_marker`, for the `clinician` role only.

  There is no on-call designation: the inbox's cover roster is a schedule that may name only holders of the lane's ownership grant.
- **Grants.** Grants are per person, per act class and per action (`draft`, `sign`, `cosign`, `complete`, `discontinue`), optionally limited to act types. Each grant has an interval, rests on a practice-supplied attestation and may carry a co-signature requirement. Only the medical director records them (AU-02). `System Manager` confers no clinical authority. For a sign-off, a grant confers authority only together with the licence verification in the practitioner's openWallet (CA-04; ruling 151).
- **Consult review scope (CD-37).** A grant may instead carry the scope `review` over the record class `ai_consult_record`, for a person holding the `clinician` role. It lets the holder record AI consult reviews under `define-ai-authored-clinical-records` AG-11. It is not an act class, creates no act and gives no authority over any act. Every other grant rule applies, the self-grant rule included. This settles that change's tension AT-12.
- **Attestations.** Licensure and prescriber facts are attestations supplied by the practice, with an expiry, recorded by someone other than their subject. openChart does not verify them and says so (AU-03, CD-13). Under ruling 151, a sign-off also relies on the licence verification in the practitioner's openWallet, and both must hold (tension CT-18).
- **Prescriptions fail closed.** A prescription-signing grant needs a prescriber attestation in force, and recording one without it is refused (practice configuration, CD-49). An expired attestation stops the grant at once, and a later signing attempt takes no effect and is entered as a recommendation.
- **Checks at the moment of action.** Every action is checked against its decision maker's authority in force at that moment, whatever kind of decision maker it is. An action without that authority takes no effect, and is entered as a recommendation, never refused for that reason. A completion is a record of work done, not a decision: without the `complete` scope it changes nothing and is kept in the act's trail as a report (CD-58). Reductions apply at once (AU-04).
- **Wallet binding (AU-07, CD-54).** A practitioner binds their own wallet to their account, only in their own re-authenticated session, with a proof of possession from a key the wallet declares. One wallet binds to one account. An administrator may suspend a binding but never create one.

### 8. Act-type registry

The registry lists, per class, the act types a practice uses (CA-09, CD-14). Each type has a code, a display name, an interval, a version and two explicit flags, `reserved` and `emergency_management`. The medical director maintains it. The flags do nothing for clinician acts in this change. They are the data that `define-ai-authored-clinical-records` AA-04 to AA-06 read. Under ruling 80, the registry, together with AN-06, is also the chart's list of what counts as a decision: decision content takes effect only when its class and act type are in force in it. Decision content whose class or act type the chart does not define or hold in force, including while the registry is empty, is entered as a recommendation with `no_decision_authority`, never refused and never kept as unmarked information (AN-06, CD-44).

### 9. Patient-reported content stays patient-reported

A clinician may create a draft act from an intake statement only by an explicit action, recorded as derivation provenance (`derived_from`: kind, reference, version, who and when) (CA-11, CD-22). The same applies to a clinical communication record under MI-12, once `define-clinical-message-inbox` lands.

Nothing is created automatically, not even a recommendation. The source statement is never changed, keeps `assertion_kind` patient-reported, and its `verification_state` is never set by this change. The clinician's record is a separate act, signed off by the clinician. This is how the ratified "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order…" is honored: a draft act is created only by a named clinician's authenticated command through the versioned boundary, and takes effect only by that clinician's sign-off (CA-04), and never by intake, a statement, an API response or an extension event (CA-10; tension CT-1).

### 10. Encounters and notes

- **The encounter.** It is opened `in_progress` with one primary performer (EN-01).
- **The appointment.** openPractice owns the appointment (ruling 31). The encounter may hold an opaque appointment reference, and nothing more (EN-02, CD-17). The 1.0 contracts carry no appointment events, so the reference is entered by an authorized user or left absent until a later MINOR version of the link contract adds events. A walk-in has none (openPractice EB-19).
- **Signing the encounter.** It needs all of these: the signer is a participant with encounter sign scope, at least one final note, no attached drafts, and an end time (EN-04, CD-15). The encounter signature is the documentation-final signature.
- **After finalization.** Every change to attached acts goes through a signed encounter amendment, which publication treats as a forward-only correction (EN-05, CD-16).
- **Notes and replies.** Notes are signed by their author, and addenda are separate notes. Clinician replies to patients stay MI-12 communications (EN-03).

### 11. Diagnoses and procedures

- **Diagnoses.** A diagnosis of record is either an encounter diagnosis (with an encounter and an optional rank) or a problem-list condition (with a clinical status). It is always coded and carries a verification status. An uncoded diagnosis cannot be signed (DX-01, CD-25).
- **Kept apart from reports.** Diagnoses stay distinct from patient-reported conditions in storage, display and reads (DX-02).
- **Procedures.** Procedures are coded, attached to an encounter and performed by a participant (DX-03).

### 12. Publication to openPractice: how CF-06's placeholder is replaced

CF-06 reads: "Until a separately governed openChart capability records clinician-authored encounters, diagnoses and procedures, openChart SHALL report `billable_facts_supported: false`…" This change is that capability (PB-01). It replaces the placeholder by meeting CF-06's own condition, not by editing `define-openpractice-boundary`:

1. In a deployment where features (2) and (3) are enabled and the boundary change's publication surface is built, `capability.result` reports `true` (CD-24).
2. In every other deployment CF-06 still governs: the result is `false` and reads return `no_billable_facts`.
3. Disabling feature (3) returns the result to `false` at once.

What is published, field by field, against the canonical schema at `6b2071fe…` (PB-02):

| Contract field | Source in this change |
|---|---|
| `encounter.documentation_final` notification | The encounter becomes `final`. Resource references only, written to PL-14's durable store, and delivered at once on an `active` link or held as a pending final while the link is in `identity_review` (PB-02, PB-03). |
| `encounter.id`, `version` | Encounter act identifier and act version |
| `encounter.status` | `final`/`amended` → `finished`. Facts are read only for those statuses: a non-final encounter, and every withdrawn one (entered in error, restricted, or unrepresentable), reads as `no_billable_facts` (CD-24) |
| `encounter.type`, `period`, `location_ref`, `participants` | Encounter content. Codings as system and code; practitioner references opaque. |
| `conditions[]` | Each `final`/`amended` `encounter_diagnosis` on the encounter whose verification status is `confirmed` (ruling 87; CD-33): category `encounter-diagnosis`, coding (system, code), rank, encounter reference |
| `procedures[]` | Each `final`/`amended` procedure: coding, quantity, `performed`, `performer_ref`, encounter reference |
| `documentation_final` | `final: true`, `signer_ref` and `signed_at` from the encounter version's author signature |
| `clinical_fact.corrected` | An encounter amendment: new versions in `resource_refs`, replaced versions in `supersedes` (PB-03) |
| `clinical_fact.entered_in_error` | A published diagnosis, procedure or encounter marked entered in error; a published diagnosis later refuted, or otherwise amended away from `confirmed` (ruling 87); or a restricted act added to a published encounter (PB-03, CD-33, CD-36). It stays the only retraction until ruling 89's reason code lands (CT-16) |

**Corrections whatever the link state** (PB-03, CD-35). Every correction or retraction of a published fact is written to the durable store whatever the link state:
- on an `active` link, it is delivered at once;
- while the link is in `identity_review`, it is held together with pending finals, and all are delivered in order when the link returns to `active`. Pending finals are re-evaluated first;
- if the link ends `revoked` or `superseded`, retractions are delivered as pointers only, corrections are delivered as retractions of the superseded versions, pending finals are dropped, and no read is served (ruling 88; tension CT-15).

**Withdrawn facts** (PB-03; CA-N2, CA-N3). A published fact whose latest version could no longer be published is retracted with `clinical_fact.entered_in_error`, the only retraction until ruling 89's reason code lands (CT-16), whatever the reason: no longer `confirmed`, moved to the problem list, a coding the schema cannot hold, entered in error, or, for a whole encounter, a restricted act. Every withdrawn encounter then reads as `no_billable_facts`, whatever the reason, so a read never reveals a restricted act.

So openPractice never keeps billing a fact that openChart has corrected or withdrawn.

What is never published (PB-04):
- patient-reported statements and communications;
- encounter diagnoses that are not `confirmed` (ruling 87);
- the problem list, which the contract has no category for;
- notes, orders and prescriptions;
- drafts;
- restricted acts;
- recommendation records, information records, and any addition that is not a decision signed off with authority (AN-09, AN-14);
- encounters awaiting co-signature;
- anything the schema cannot represent. In that case nothing is published for the encounter, and an integration exception is recorded.

A read of a non-final or withdrawn encounter returns `no_billable_facts` (CD-24). Codings drop the version and display, because CF-01 and FD-11 allow a system and a code only (tension CT-11).

openChart still works with no openPractice, and a delivery failure never blocks a clinical act (PB-05).

### 13. Orders

There is one generic record, with five categories (OR-01, CD-18):
- `laboratory`, `imaging`, `referral` and `other`, from the brief;
- `procedure`, from `define-ai-authored-clinical-records`' minimum list.

Release follows signing unless a `before_effect` co-signature or a future release time holds the order in `pending_release` (OR-02). `released` means in force inside openChart. openChart transmits nothing and ingests no result; completion is a named person's explicit act (OR-04, CD-19).

### 14. Prescriptions and the prescribing-safety gate (ruling 74)

The prescription records the prescribing decision (RX-01).

**Gate.** RX-02 makes ruling 74 binding. No prescription, and no new version of one, is signed, co-signed or released in a deployment where the prescribing-safety gate is not met for that step. A deferred release that the gate refuses stays `pending_release`, and a work item goes to the signer; no timer releases it. The co-signer sees the alerts and overrides recorded so far. The gate is met only when three conditions hold:
1. `define-prescribing-safety-checks` is ratified;
2. its capability is built and enabled in that deployment;
3. the signing meets that change's signing-time conditions. Under rulings 76 to 78 these are a connected, licensed or verified knowledge source and a completed check, or the clinician-only outage path with a recorded statement.

Ruling 74 says "specified". This design reads that as ratified, and it adds the runtime conditions so that a deployment cannot sign in the gap between ratification and a working check (CD-30). Feature (5), prescriptions, is not buildable before that change is ratified (tasks §2.4).

**Controlled-substance classification.** The classification is required. `unknown` counts as `controlled`. Signing a prescription classified `controlled` or `unknown` is refused (ruling 83; RX-03, CD-20), and `define-prescribing-safety-checks` refuses it in its gate too. Controlled-substance prescribing goes into a later change alongside electronic prescribing (ruling 83). No rule about controlled substances is asserted.

**No transmission.** There is no transmission, no controlled-substance electronic prescribing, no pharmacy-facing document and no dispense record, and the transmission status is fixed at `none_recorded` (RX-04, CD-21).

### 15. Coding and licensed intellectual property

A coding stores the system, the code, the code-system version (where the practice's code set declares one), the display and the reference of the practice-supplied code-set import (CA-12, CD-23). openChart bundles no code set and asserts no license status for any code system. Bundling anything needs license verification and a governed change. This is consistent with openPractice FD-11's "never licensed content in the repo". openChart goes further than FD-11 in one respect: it does not adopt FD-11's list of license-free sets, because FD-11 governs openPractice (tension CT-12). Synthetic fixtures use synthetic code systems only.

### 16. FHIR R4-compatible mapping (contract level, no conformance claim)

| Act | Resource | Key mappings |
|---|---|---|
| Encounter | Encounter | status (§3); type; period; participant.individual = practitioner reference, participant.type from participation; location; appointment reference only as an identifier |
| Clinical note | DocumentReference (CD-26; Composition is the alternative) | docStatus (§3); type from note type; context.encounter; content as attachment with hash; relatesTo for addenda (`appends`) and amendments (`replaces`) |
| Diagnosis of record | Condition | category `encounter-diagnosis` or `problem-list-item`; code; clinicalStatus; verificationStatus; encounter; onset/abatement dates |
| Procedure performed | Procedure | status (§3); code; performed; performer; encounter; bodySite |
| Order | ServiceRequest | status (§3); intent `order`; category from order category; code; priority; reasonReference; encounter; performer |
| Prescription | MedicationRequest | status (§3); intent `order`; medication; dosageInstruction text; dispenseRequest quantity and refills; substitution; reasonReference |
| Authorship, signatures, co-signatures, derivation, the writer and on whose behalf | Provenance | agent (author, verifier for co-signer, and the writer `added_by`); agent.onBehalfOf for `on_behalf_of`; signature with the content digest; entity `source` for `derived_from` and `source`. A recommendation record is never exposed (CA-13) |

Drafts, cancelled acts and restricted acts are never exposed (CA-13). openChart claims no FHIR certification and no profile or implementation-guide conformance.

### 17. Standalone operation, logs and restricted acts

- **Standalone.** Every capability works with no external system, with two exceptions. A decision's sign-off needs the practitioner's openWallet and openSig (ruling 151; tension CT-19), and prescription signing also needs the gate (CA-14). Where openWallet or openSig cannot be reached, a sign-off attempt leaves its draft open and is recorded (AN-14). The golden-intake tests stay the regression gate.
- **Logs.** Logs and coded reasons carry identifiers only.
- **Restricted acts.** Sensitive categories and minors' records are an open question for counsel (Open Question 3). Meanwhile, a clinician may mark an act `restricted`. A restricted act, and any encounter carrying one, never leaves the chart (CA-15, CD-27). No legal rule is asserted.

### 18. Handoff shape and feature order

There are five ordered features, each gated on ratification (ruling 85; CD-31, CD-41):
1. clinical authority (AU-01 to AU-07), its own first feature (ruling 92), together with the general rule for additions (AN-01 to AN-14; CD-41, PROPOSED), built first and on its own, so that `define-clinical-message-inbox` and `define-ai-authored-clinical-records` Tier 1 can rely on it before any act exists (#3 MT-22);
2. encounter, note and signing (CA-01 to CA-15, EN-01 to EN-06);
3. diagnoses, procedures and publication;
4. orders;
5. prescriptions, gated on ratification of `define-prescribing-safety-checks` (ruling 74).

The shared workflow protocol's default is exactly one Spec Kit feature per OpenSpec change. Ruling 1 approved an ordered multi-feature exception for openPractice. Ruling 85 allows this change the same ordered multi-feature exception (tension CT-14, settled).

### 19. Additions to the chart (rulings 80 and 151)

The capability `chart-additions` (AN-01 to AN-14) holds the general rule for every addition to a patient's chart, whoever or whatever makes it. The other openChart drafts cite it.

- **Who may add (AN-01, AN-03).** Any identified human or system may add.
  - An addition the chart cannot identify, writer or named party, is refused, and nothing is stored. Where ruling 90 requires that what an AI already told a patient stay in front of a clinician, that writing path's own quarantine applies instead.
  - Systems and devices are registered with the practice first, and the practice can suspend any of them at once (CD-43).
  - Practice configuration, the wallet binding of AU-07 included, is not an addition (CD-49).
  - A draft is not yet an addition: it becomes one when it is submitted (CD-60).
- **Identification (AN-02).** Each party has a `kind`: `human`, `patient`, `ai`, `device` or `system`, with the identifying fields of the ruling's table and an `identity_basis` (CD-42). A writer is always verified by the chart.
  - A human is identified by their named account only. Role, licence attestation and wallet are recorded where they apply, and their absence never makes a writer unidentified (CD-55).
  - Another organization's clinician or system is named by `external_ref`, asserted by the system that delivered it. It is never the writer, and such a clinician holds no openChart role (CD-57).
  - A relay that delivers an AI's record is the writer, and the AI is named on whose behalf it wrote. An AI with no openWallet ID, or with one the relay's registration does not cover, cannot be identified (CD-61).
  - A wallet identifier never becomes a person's identifier, as openWallet's ratified rule requires.
- **Provenance (AN-04, AN-05).** Each addition records `received_at`, `occurred_at`, `source` (a kind and a reference), `added_by` and `on_behalf_of`, and may carry the writer's `submission_ref`. The record is permanent from submission and readable in openChart by anyone who can read the chart. A correction points back to what it corrects (`corrects`). The ratified intake path keeps its own identity and audit until a later change aligns it (CT-17).
- **Information and decisions (AN-06, CD-44).** Decision content is:
  - act content of the classes other than the clinical note;
  - content submitted as an act of a class the chart does not define;
  - the kinds clause 9 names;
  - every sign-off.

  Decision content takes effect only when its class and act type are in force in the registry, and otherwise it becomes a recommendation with `no_decision_authority`. A clinical note's content is information, while the practitioner's signature on it is a decision (CD-63). A completion is a record of work done (CD-58). openChart determines the class itself; a declared class is kept but decides nothing.
- **A decision (AN-07, AN-08, CA-04, AU-04).** A decision counts only when its decision maker held the authority at that moment and a practitioner signed it off under ruling 151.
  - A decision added on someone's behalf counts only with that practitioner's own sign-off, which by the fail-closed default must be made in the chart (CD-52; Open Question 17). Otherwise it is the carrying system's recommendation.
  - An AI covered by the delivering relay's registration is the decision maker of what it sends, its identity asserted by the relay (CD-61).
- **The practitioner's sign-off (CA-04, CD-48, CD-53).**
  - The practitioner signs off in their own logged-in session, with re-authentication, and their openWallet and openSig sign and validate the entry.
  - openChart checks four things at that moment:
    - the account is bound to the `openwallet_id` (AU-07);
    - the wallet holds a current licence verification that covers the decision;
    - the openSig attestation verifies against the wallet, over the SHA-256 of the sign-off statement, which binds the act, version, patient, action, role, signer, attestation, both digests, the time and a single-use challenge;
    - the medical director's grant is in force.
  - It accepts only a key of custody `isolated_per_use_authorized`.
  - The signature, or for an action on an existing act its lifecycle event, records the evidence (`sign_off`).
- **When a sign-off fails (AN-14, CD-46).**
  - A failure the author can cure by trying again leaves the draft open, records the attempt, and creates no recommendation. Such failures are a service that cannot be reached, an attestation that did not verify, a failed re-authentication, the wrong key custody, or a check openWallet or openSig does not yet specify. So while they specify nothing, drafts stay drafts.
  - A failure of authority enters the content as a recommendation tied to the draft, which is held, never cancelled. An encounter keeps everything attached to it.
  - Authority is checked before any gate, and a recommendation is never gated.
- **The recommendation record (AN-09 to AN-11, CD-45, CD-47, CD-51, CD-56).**
  - It is `record_kind` `recommendation`. It holds:
    - the proposed action, and the act class and act type as given, whether or not the chart defines them;
    - the content exactly as given, checked only for being well formed, with `content_schema` where another schema declared it;
    - the same provenance as any addition;
    - `not_authorized_decision` and the coded `missing_authority`, with any `path_reason`;
    - the `decision_maker`, and the `claimed_decision_maker` only for AN-08;
    - the `receipt`;
    - its `review`, with every failed adoption.
  - It is never an act of record and is never gated.
  - It goes to a clinician who holds the authority. It escalates as a co-signature requirement does.
  - Adoption applies the act-validity rules and is a sign-off of the clinician's own, carrying `adopted_from`:
    - on a draft the recommendation is tied to, which then becomes the clinician's act;
    - as a new draft, where there is none;
    - as the clinician's own action, for a proposed action on an existing act.
  - A failed adoption is recorded on the recommendation and creates no second one. Declining is recorded with a reason.
  - A repeated submission is answered with the first result (CD-64).
- **A note from a writer without the authority to sign it (AN-14, CD-63)** is kept as information under its writer's name (`record_kind` `information`, marked not signed off). It is never a recommendation, never a final note and never published.
- **Still refused (AN-12).** An addition is still refused, with nothing stored, when:
  - the writer or a named party cannot be identified;
  - the patient cannot be matched;
  - the content is malformed or test data;
  - the practice has suspended the writer.

  Malformed means only content the chart cannot read or that breaks the record's envelope (CD-56; Open Question 18). Test data is recognized only by a declared context or a test patient (CD-62). RX-02's prescribing-safety gate is a safety condition, not authority: a gated signature leaves the prescription a draft, and nothing the clinician wrote is lost.
- **Devices (AN-13).** How a device is identified and what a reading records are defined here. How device data enters the chart is not (Open Question 8).

**What openWallet and openSig specify today** (read on 2026-11-15; both repositories are public):
- **openWallet.** In `opensoft/openWallet-spec` at `a2d554d`, the canonical capability `openxwallet` says:
  - a wallet is a signing key, or a declared set of keys, held by a holder, and a holder may be a practitioner;
  - using a grant needs a signature from the holder's wallet key over the request;
  - custody is declared per key and bounds what a signature evidences;
  - every exercise is attributed to the key that presented it, and revocation is checked at use;
  - a wallet SHALL NOT become a prerequisite for reconstructing a record, resolving a subject or operating a domain, and a wallet identifier is attestation, never identity.

  Its contracts (`opensoft/openWallet-code` at `bb0e9da`) publish the ratified closed custody registry, `openxwallet-custody.registry.yaml`, version 1. In it, `holder_readable` and `isolated_invocable` evidence only the holder's environment, and only `isolated_per_use_authorized` evidences that the holder acted. The contracts also name a practitioner profile as a successor, "gated on a consumer of its own". No requirement or contract of openWallet defines a licence verification yet.
- **openSig.** In `opensoft/openSig-spec`, `main` at `23ebbfe` holds no specification. Two pull requests are open, neither merged:
  - #1 (`8668f30`) is a non-normative brainstorm;
  - #2 (`a05fcee`) is a corporate signing MVP for PDF envelopes with an organizational seal. Its non-goals include personal PKI enrollment and patient or clinical production workflows. It leaves ledger-anchoring wallets out of its anchoring interfaces, and its consumer scenario says that a consumer of a signing completion "cannot independently attest a clinical record".

  Both pull requests' agent instructions say to "Keep clinical attestation and amendments in openChart". Neither openSig's specification leg nor its two pull requests mentions openWallet. Nothing in openSig yet attests that a signature is from a wallet.

So ruling 151's sign-off depends on a licence verification and an attestation that neither project specifies yet (tension CT-20; Open Questions 9 and 11). Until both do, those two checks of CA-04 cannot be made, every sign-off attempt fails in the way the author can cure later, and a practitioner's drafts stay drafts. This change fails closed and invents nothing about either project.

## Minimum contents required by `define-ai-authored-clinical-records`

That change's design, section "Required prerequisite change: the clinical-acts foundation", lists twelve items.

| # | Item | Where this change meets it | Met |
|---|---|---|---|
| 1 | Clinician encounters, with participants, period and status | EN-01, EN-04, CA-03 | Yes |
| 2 | Orders (laboratory, imaging, referral, procedure) with a lifecycle that distinguishes draft, signed, pending release, released or executed, completed, discontinued or countermanded, and voided | OR-01, OR-02, CA-03, CD-18. At `079dd36` that change uses this change's status names (`pending_release`, `released`, `discontinued`, `cancelled`, `entered_in_error`), with signing as an event | Yes (CT-7 resolved) |
| 3 | Prescriptions with the same lifecycle and a classification that marks controlled substances | RX-01, RX-03, RX-04. At `079dd36` that change asks for no dispense or transmission state; `transmission_status` stays reserved at `none_recorded` | Yes (CT-8 resolved) |
| 4 | Diagnoses of record (problem list and encounter diagnoses), with verification status, distinct from patient-reported conditions | DX-01, DX-02 | Yes |
| 5 | Treatment plans, versioned, each change a new dated record | Not provided: ruling 73 leaves treatment-plan records for later. At `079dd36` that change records them as not in the foundation, and as a prerequisite of its `treatment_plan_change` act class | No, by ruling 73, as that change now records (CT-6 resolved) |
| 6 | Authorship on every act: an author type, and clinician signing and co-signature (ruling 72). Author type `ai` and the authority basis that Tier 2 fills wait for a future governed amendment (its AT-10). | CA-02 (an act's author type is `clinician`; act content from an AI is a recommendation record, AN-09), `authority_basis_ref` (the role grant today), CA-04, CA-07, AN-02 (the AI as writer or decision maker) | Yes |
| 7 | An act-type registry with reserved and emergency-management flags | CA-09 | Yes |
| 8 | Roles: clinician, nurse and medical director, with scope per act class | AU-01, AU-02, including the consult review scope that its AG-11 needs (CD-37). At `6989780` that change cites AU-01 as its only medical-director definition | Yes |
| 9 | Amendment, void and countermand as new dated records; nothing edited in place or deleted | CA-05, CA-06, OR-02 (discontinuation as a signed lifecycle record), OR-03 | Yes |
| 10 | Content schemas per act class, published so that a MINOR version of `openchart-ai-clinical-record-write` can pin them | `openchart-clinical-act-content/1.0`, `$defs/<class>Content`, SHA-256 in `contracts/SHA256SUMS` (CA-01, CD-28) | Yes |
| 11 | Reconciliation with the ratified intake text that AT-1 records | CA-10, CA-11, §9; tensions CT-1, CT-2, CT-17 and CT-22 | Yes. CT-1 is read narrowly under ruling 84; CT-17 and CT-22 are recorded for the owner |
| 12 | Billing interplay with CF-02 and CF-06 | PB-01 to PB-05, §12. AI-authored acts are not published, because only `clinician` authors exist in 1.x and CF-02 requires clinician-authored documentation. Recommendation records are never published (PB-04, AN-09) | Yes |

## Required later change: prescribing-safety checks

**`define-prescribing-safety-checks`.** It is required before any prescription can be signed (ruling 74), and is being drafted under ruling 75. Feature (5), prescriptions, depends on its ratification. RX-02 refuses every prescription signature until its gate is met. Its minimum contents:

1. **Clinician-confirmed lists.** A clinician-confirmed allergy and intolerance list and an active medication list. Each reuses this change's act model (author type, signing, amendment, entered in error, provenance) through new act classes in a MINOR version of `openchart-clinical-act-content`. It defines no second signing model.
2. **Reconciliation from intake.** The lists are reconciled from patient-reported medication, supplement and allergy statements only by an explicit, attributed clinician action (CA-11). Nothing is promoted automatically.
3. **Inputs.** A check reads both clinician-confirmed entries and patient-reported statements. A patient-reported entry is shown as patient-reported and is never ignored because it is unconfirmed. An uncoded or free-text entry that cannot be checked produces an explicit "could not be checked" warning and is never skipped silently.
4. **The checks (ruling 77):**
   - allergy (ingredient and class);
   - drug–drug interaction;
   - duplicate therapy;
   - drug–supplement interaction, only where the source declares support.

   Later changes will add dose range, drug–condition, pregnancy and lactation, renal and hepatic adjustment, and paediatric and geriatric rules.
5. **Behaviour.**
   - Checks run when a prescription is drafted or changed, and again at signing.
   - Each alert has a severity.
   - An override needs a recorded reason, and the most severe class needs an explicit override for each alert, never in bulk.
   - Each check records its inputs, the source and its version, the alerts raised and the clinician's response.
   - Alerts are labelled as advice, and the record shows the clinician as responsible.
6. **The knowledge source (ruling 78).**
   - openChart bundles no drug knowledge.
   - A versioned adapter contract, with a canonical schema and SHA256SUMS, covers normalization to ingredients, allergy cross-reference, interaction lookup, a capability declaration and source identity with version and effective date.
   - Nothing is asserted about any vendor, product, database or license; each must be verified before use.
   - Fixtures are synthetic.
7. **Gates, failing closed.**
   - No prescription is signed without a connected, verified source (ruling 78), and a practice that never had a verified source cannot sign (ruling 82). A verified source that is stale or down uses the outage path, with the medical director alerted, and signing stops after a staleness limit set by policy (ruling 82).
   - The outage path is for a clinician only: a recorded statement, a flag, and a re-check when the source returns. A non-clinician author, including any future AI author, never uses it (ruling 76).
   - Go-live needs a recorded legal and regulatory review, which states what it covers and asserts no rule.
   - Prescriptions classified controlled, or of unknown classification, are refused (ruling 83).
8. **The interface RX-02 calls.** One gate decision per signing attempt, with a coded reason, that this change's signing path can rely on.
9. **Boundaries.**
   - Everything except prescription signing works with no source.
   - No clinical content goes to openPractice.
   - A FHIR R4-compatible mapping at contract level (AllergyIntolerance, MedicationStatement or MedicationRequest, DetectedIssue), with no conformance claim.

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which "MUST operate without MedxFactory, MedxEHR or openPractice" | CA-14 and PB-05. Every component works with no external system, with two exceptions: a decision's sign-off needs the practitioner's openWallet and openSig (ruling 151; CT-19), and prescription signing needs the safety gate, which is part of openChart. Where openWallet or openSig cannot be reached, a sign-off attempt leaves its draft open (AN-14). |
| External identifiers must not replace the openChart identifier or merge patients | CA-01. Every act names the openChart triple; the schema refuses any other namespace. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Acts never alter submissions. |
| Statements preserve reported detail | Untouched. Derivation reads a statement and never changes it (CA-11). |
| Amendments preserve accepted history | CA-05, CA-06, CA-08. Nothing is overwritten or deleted. |
| APIs and hooks are authorized and versioned | CA-10. One versioned, authorized boundary; direct writes refused; extensions read only. |
| Intake does not confer clinician or autonomous authority | CA-10, CA-11, DX-02, PB-04, AN-09. **Tensions CT-1 (read narrowly under ruling 84), CT-2, CT-3, CT-17 and CT-22.** |

Six possible conflicts with ratified or published openChart text are recorded: CT-1 to CT-3, CT-17 and CT-22 against the ratified requirements, and CT-4 against the published p4 declaration. No other conflict with ratified text was found.

### Proposed clarifying amendment (ruling 84)

Ruling 84 reads the ratified sentence narrowly: "it bars automatic creation from intake, and an alert to the clinician isn't a treatment recommendation." It also directs "a small clarifying amendment to the ratified text, so it can't be misread later". The ratified sentence is in the canonical `expanded-patient-intake` capability, requirement "Intake does not confer clinician or autonomous authority":

> No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action.

Proposed wording, to follow that sentence in the requirement:

> This bars automatic creation from intake: it does not bar a clinician signing through the API, and an alert to the clinician is not a treatment recommendation.

The owner applies it to the ratified text at ratification, through that text's own governance. This change edits neither the canonical capability nor `specs/001-expanded-patient-intake/`, and adds no MODIFIED delta. The ratified feature text, `specs/001-expanded-patient-intake/spec.md` FR-008, states the same bar in other words. If the owner wants the two texts to match, the same sentence fits there.

## Consistency with the draft changes

| Draft requirement | Relation |
|---|---|
| `define-openpractice-boundary` CF-01, CF-03, CF-04 | Followed: PB-02 publishes exactly CF-01's fields, by reference and minimum necessary; PB-03 is CF-04's forward-only correction. |
| CF-02 | Followed: only final, clinician-signed encounter facts (PB-04). |
| CF-05 | Followed: this change creates no billing data. |
| CF-06 and Open Question 2 | This change is the capability named; CF-06 stops requiring `false` only where this change is enabled (PB-01). **CT-13.** |
| PL-01, PL-03 | Followed: the patient triple. |
| PL-13, PL-14, PL-15 | Reused for logs, delivery and standalone operation (CA-14, PB-02, PB-05). |
| `define-clinical-message-inbox` MI-12, MI-14 | This change is the "separately governed clinical workflow" those requirements defer to. Replies stay communications (EN-03), and a communication becomes a source only by explicit derivation (CA-11). |
| MI-07, task 3.2 (roles) | AU-01 gives the roles and the medical director. **CT-9.** |
| MI Open Question 11 (billability of replies) | Proposed answer (CD-29): a communication is never billable. A clinician who judges an exchange to be a documented service records an encounter, with a note that may derive from the communication. |
| `define-ai-authored-clinical-records` (12 minimum contents) | Table above. **CT-6 to CT-10.** |
| AA-01 | Must conform under ruling 80: an AI act attempted without authority is stored as this change's recommendation record (AN-09, `no_decision_authority`), instead of being refused with nothing stored. That change carries the edit. |
| AA-07, AA-08, AA-09, AA-11 | The hook (§6) and lifecycles (§3) carry them; "pending" for AA-11 is `pending_release`. |
| openPractice EB-13 to EB-16, EB-19 | Followed: final signed documentation, diagnoses and procedures, forward-only corrections, references only, and an appointment reference only. |

## Design calls for owner review

Each item goes beyond the rulings and is proposed, not ruled. Where an item implements a ruling, it cites the ruling, and its mechanics stay a proposed design call. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| CD-1 | One envelope for six act classes; the storage shape is decided in planning. | CA-01 |
| CD-2 | **Under ruling 80.** An act's author type is `clinician`. Act content from any other author is entered as a recommendation record (AN-09), never refused for that reason. Only a later governed change may add an author type for acts, after Open Question 12. | CA-02 |
| CD-3 | The `clinician` author type covers anyone with an openChart clinical role grant, `clinician` or `nurse`, matching MI-12's definition. | CA-02 |
| CD-4 | The status lists and transitions of CA-03. `signed` is an event, not a resting status. | CA-03 |
| CD-5 | Any clinician with sign scope for the class may amend. Each version has its own author and signature. | CA-05 |
| CD-6 | Orders and prescriptions are amended only while `pending_release`. After release, a change is a discontinuation plus a new act. | OR-03 |
| CD-7 | Entered in error may be marked by the author, a clinician with sign scope, or the medical director, with a coded reason. It is the void of AA-09. | CA-06 |
| CD-8 | Draft revisions are audited, and abandoned drafts are cancelled, never deleted. | CA-05 |
| CD-9 | Attestation statements are coded and versioned per act class, with wording maintained by the medical director. A signature binds the RFC 8785 content digest. | CA-04 |
| CD-10 | Re-authentication at every signature. **Proposed fail-closed default**: required; planning chooses the mechanism. | CA-04, EN-06 |
| CD-11 | The co-signature hook: `before_effect` only for orders and prescriptions; `after_the_fact` for all classes; escalation to the medical director; never closed by default. An encounter awaiting co-signature is not published. | CA-07, PB-04 |
| CD-12 | Roles `clinician` and `nurse`, plus a medical director designation. Designation is by an administrative role named in planning. Grants are recorded by the medical director only. With no medical director, nothing is signable. `System Manager` confers nothing. | AU-01, AU-02 |
| CD-13 | Licensure and prescriber facts are practice-supplied attestations that openChart does not verify. **Fail-closed default for prescriptions**: a prescription-signing grant needs a prescriber attestation in force, and expiry stops it at once. Under ruling 151, a sign-off also relies on the licence verification in the practitioner's openWallet, and both must hold (tension CT-18). | AU-03 |
| CD-14 | The registry is maintained by the medical director. Both flags must be set explicitly. They have no effect on clinician acts. | CA-09 |
| CD-15 | Encounter finalization needs a signer who is a participant, at least one final note, no attached drafts, and an end time. | EN-04 |
| CD-16 | After finalization, every change to attached acts goes through a signed encounter amendment. | EN-05 |
| CD-17 | The appointment reference is optional and opaque, entered by an authorized user or absent, until a MINOR version of the link contract adds appointment events. Its absence never blocks anything. | EN-02 |
| CD-18 | The order categories add `procedure` (from the AI change's minimum list) to the brief's laboratory, imaging, referral and other. | OR-01 |
| CD-19 | No order transmission and no results ingestion. Completion is a named person's explicit act. | OR-04 |
| CD-20 | **Under ruling 83.** Signing a prescription classified `controlled` or `unknown` is refused, with reason `controlled_classification_not_permitted`, and `define-prescribing-safety-checks` refuses it in its gate too. `unknown` counts as controlled. Controlled-substance prescribing goes into a later change alongside electronic prescribing. | RX-03 |
| CD-21 | No pharmacy-facing document or message. `transmission_status` is fixed at `none_recorded`. | RX-04 |
| CD-22 | Derivation from intake statements and clinical communications only by explicit action, with provenance. The statement is never changed, and its `verification_state` is never set. | CA-11 |
| CD-23 | A coding carries `code_set_ref` to the practice's import. A code must be in a loaded code set in force. | CA-12 |
| CD-24 | The capability is `true` only where features (2) and (3) are enabled and the boundary surface is built. A read of a non-final encounter, or of any withdrawn encounter, returns `no_billable_facts`, whatever the reason for the withdrawal. | PB-01, PB-02, PB-03 |
| CD-25 | An uncoded diagnosis or procedure cannot be signed. Uncoded reasoning goes in a note. | DX-01, DX-03 |
| CD-26 | Notes map to DocumentReference (the alternative is Composition). `pending_release` maps to `on-hold`. Drafts are never exposed. | CA-13 |
| CD-27 | **Fail-closed default pending counsel** on sensitive categories and minors' records: a clinician may mark an act `restricted`, and a restricted act, or an encounter carrying one, never leaves the chart. No legal rule is asserted. | CA-15, PB-04 |
| CD-28 | The content schema is published now, with each class's content addressable for a MINOR version of `openchart-ai-clinical-record-write`. | CA-01 |
| CD-29 | Answers inbox Open Question 11: a communication is never billable. A clinician who judges an exchange to be a documented service records an encounter whose note may derive from it. | EN-03, CA-11 |
| CD-30 | Reading of ruling 74: "specified" means ratified. The gate also needs the capability built and enabled in the deployment, and the signing-time conditions of `define-prescribing-safety-checks` (rulings 76 to 78). | RX-02 |
| CD-31 | **Under ruling 85.** The handoff is five ordered features, in the order of Decision 18, each gated on ratification and created only after the one before it has landed. | tasks §3 |
| CD-32 | Every read by an integration identity is audited. How reads by chart users are audited is decided in planning. | CA-08 |
| CD-33 | **Under ruling 87.** Only `confirmed` encounter diagnoses are published as billable facts; the problem list is never published, because the contract has no category for it. A published diagnosis that is later refuted is retracted, as the ruling directs, and so is one amended to any other status away from `confirmed`, so that openPractice holds only confirmed diagnoses. The retraction is `clinical_fact.entered_in_error` until ruling 89's reason code lands (CT-16). | PB-02, PB-03, PB-04, DX-01 |
| CD-34 | Authority independence. The designating account is never the medical director. The designee's clinical role rests on a licensure attestation recorded by another named human. Nobody records their own attestation. A medical director's self-grant is flagged, independently attested, shown on acts signed under it, and listed for the administrative role. The first medical director gets the `clinician` role in one audited bootstrap act. | AU-01, AU-02, AU-03 |
| CD-35 | Every correction or retraction of a published fact is queued whatever the link state. It is delivered at once on an `active` link; held, with pending finals, during `identity_review`; and on a revoked or superseded link delivered as pointer-only retractions, as ruling 88 directs. | PB-02, PB-03 |
| CD-36 | A published fact or encounter whose latest version could no longer be published is retracted with `clinical_fact.entered_in_error`, the only retraction the 1.0 contract offers, until ruling 89's reason code lands through the follow-up of ruling 93 (CT-16). Every withdrawn encounter reads the same, so a restricted act is never revealed. | PB-03, CA-15 |
| CD-37 | AU-02 gains a second scope: action `review` over record class `ai_consult_record`. It is recorded only for a `clinician`, creates no act and gives no authority over any act, and every other AU-02 rule applies, the self-grant rule included. It is where `define-ai-authored-clinical-records` AG-11's consult review grant lives (its AT-12). | AU-02, AU-04, AU-05 |
| CD-38 | **Under ruling 98.** The first medical director's designation takes effect only once a second named human, neither the designating account nor the designee, confirms it. A practice with only one administrator instead records a licence verification against the licensing board's public record, naming who performed it, when, and the record consulted. Designations, attestations and self-grants are listed for the medical director as well as the administrative role. Gate: tasks §2.6. | AU-01, AU-02, AU-03 |
| CD-39 | **Under ruling 92.** The inbox scopes of AU-06: ownership (`own`, `acknowledge`, `reassign`, `raise`, `return`, `split`, `close` over `clinical_inbox_item`, lane `physician` or `nurse`, with the medical director's nurse-lane scope; `physician`-lane grants go only to the `clinician` role, and a nurse's grants stay in the nurse lane); patient reply (`reply` over `clinical_communication`, per role and lane, on an attestation); clinical-need marker (`mark`, `withdraw` over `clinical_need_marker`, `clinician` only). None reaches an act; no agent holds one. | AU-06 |
| CD-40 | **Under ruling 92.** No on-call designation. The inbox's cover roster is a schedule that names, per hour and lane, only holders of that lane's ownership grant, the medical director included as last fallback, and a lapsed grant leaves the roster at once. This is simpler than a separate designation and stays safe, because nobody can be rostered without the grant that the inbox already requires. | AU-06 |
| CD-41 | **Under ruling 92**, clinical roles and authority are their own small first feature, so the inbox does not wait for encounters and notes. It is built on its own and ahead of encounters, notes and signing (#3 MT-22), so the inbox and AI Tier 1 can rely on it first. **PROPOSED:** feature (1) also builds the general rule for additions (AN-01 to AN-14), so that the inbox and AI Tier 1 can rely on identification, provenance and the recommendation record before any act exists. Feature (1) also builds the wallet binding of AU-07. This makes feature (1) larger than ruling 92's "small first feature". The alternative, building AN in feature (2), would make the inbox wait for encounters and notes, which ruling 92 avoids. | tasks §3 |
| CD-42 | **PROPOSED.** Each party carries `identity_basis`: `verified_by_chart`, or `asserted_by` with the identified system that vouched for it. A writer is always `verified_by_chart`. A relay is the writer of what it delivers, and the AI is named on whose behalf it wrote, with its `openwallet_id` checked against the relay's registration. An app that relays a device's reading is its writer, and the device is named on whose behalf, `asserted_by` the app. `on_behalf_of` lists the parties from the originator to the writer. | AN-02, AN-04, AN-13 |
| CD-43 | **PROPOSED.** The administrative role named in planning registers systems and devices. That role or the medical director suspends them, at once. A registration records the kind and identity, the operator, who registered it and when, and for a system that delivers an AI's additions, the `openwallet_id` values it may deliver for. No registration is deleted. | AN-03 |
| CD-44 | **PROPOSED; revised in the fix round on `eb95547`.** Decision content is act content of the classes encounter, diagnosis of record, procedure performed, order and prescription, whatever its type; content submitted as an act of a class the chart does not define; the kinds clause 9 names; and the sign-offs of an act: a signature, a new signed version, a co-signature, a discontinuation, an entered-in-error mark and the cancellation of a pending-release order or prescription. A completion is not on the list (CD-58), and a clinical note's content is information (CD-63). Decision content whose class or act type is not in force in the registry, including while it is empty, is a recommendation with `no_decision_authority`, never refused and never unmarked information. A draft revision is not a decision. openChart determines the class itself, and keeps a declared class only as the writer's declaration. | AN-06, CA-01, CA-09 |
| CD-45 | **PROPOSED.** The recommendation record's fields. Its own `entry_class` is `information`, holding the proposed decision in full. It names a `decision_maker`, and a `claimed_decision_maker` when AN-08 applies. It may be marked `restricted` (CA-15). Its `missing_authority` codes are a closed list of nine, each defined in AN-09: `no_grant_in_force`, `no_decision_authority`, `decision_maker_not_confirmed`, `no_practitioner_sign_off`, `wallet_not_bound`, `licence_verification_missing`, `attestation_not_verified`, `signing_service_unavailable` and `practice_attestation_not_in_force`. The last was added so that a disagreement between licence records names the AU-03 record (CT-18). Several may apply at once. The list names only authority. A safety gate is never on it: a recommendation is not gated, the prescribing-safety gate applies when a practitioner adopts the recommendation (AN-11, RX-02), and a writing path's own gate code goes in `path_reason` (CD-51). | AN-08, AN-09 |
| CD-46 | **PROPOSED; revised in the fix round on `eb95547`.** A draft is its author's work in progress, created only with `draft` scope, and only its author signs it off. A failed sign-off never cancels it. Authority is checked first, then the rest of CA-04, then any gate. A failure the author can cure by trying again leaves the draft open, records the attempt and creates no recommendation: a service that cannot be reached, an attestation that did not verify, a failed re-authentication, the wrong key custody, or a check openWallet or openSig does not yet specify. A failure of authority enters the content as one recommendation tied to the draft by `draft_ref`; the draft is held, an encounter keeps everything attached, and on decline the draft returns to its author. A one-step submission that fails curably, or that the gate refuses, is kept as its author's draft. Content from a writer without `draft` scope is a recommendation at once. A decision made with authority stays a decision under a co-signature requirement, and a co-signature without authority is a recommendation. A failed adoption is recorded on the recommendation and creates no second one. | AN-11, AN-14, CA-03, CA-04, CA-07 |
| CD-47 | **PROPOSED; revised in the fix round on `eb95547`.** The submitter is told at once, in the response or receipt (`recorded_as_recommendation`), and a human before they leave the screen where they submitted. A recommendation goes through the writer's existing review path, or else through a review item for the encounter's primary performer, or for the medical director when there is none. Its due time and escalation work as a co-signature requirement's do, and the due time is set by practice policy. Adoption is a sign-off of the adopting clinician's own, carrying `adopted_from`: on the draft the recommendation is tied to, which keeps its identifier and becomes the clinician's act with the drafter kept as writer; as a new draft the clinician may change, where there is none; or as the clinician's own action, for a proposed action on an existing act, whose lifecycle event names the recommendation. Declining records the clinician, the time and a coded reason. | AN-10, AN-11 |
| CD-48 | **PROPOSED; revised in the fix round on `eb95547`.** The four checks of a sign-off at that moment: account bound to the `openwallet_id` (AU-07); a current licence verification in the wallet covering the decision; the openSig attestation verifying against the wallet over the sign-off statement's digest (CD-53); and the grant in force. openChart accepts only a key of custody `isolated_per_use_authorized`, the one model in openWallet's ratified custody registry (`openWallet-code` `bb0e9da`, version 1) that evidences the holder acted. The evidence fields are `action`, `openwallet_id`, `licence_verification` (`ref`, `covers`, `verified_at`), `challenge_ref`, `statement_sha256`, `opensig_attestation_ref`, `provenance_sha256`, `custody_model` and `check`. They are recorded on the signature, and on the lifecycle event of a discontinuation, an entered-in-error mark, a co-signature and a cancellation of a signed act, with that event's attestation code and version. How a failed sign-off is handled is CD-46. | CA-03, CA-04, CA-06, CA-07, AU-04 |
| CD-49 | **PROPOSED.** Practice configuration is not an addition to a patient's chart: grants, attestations, designations, act-type registry entries, system and device registrations, and the wallet bindings of AU-07. Their refusals stay. | AN-01, AU-07 |
| CD-50 | **PROPOSED.** An AI consult review (AU-02), an inbox action or a patient reply (AU-06) attempted without its grant takes no effect: nothing is sent, and no status or item changes. It is recorded as a recommendation, marked not an authorized decision, in the record its own change defines, and never refused for that reason. Whether any of them is a medical decision that needs a practitioner's sign-off under ruling 151 is Open Question 13. | AU-02, AU-04, AU-06 |
| CD-51 | **PROPOSED; revised in the fix round on `eb95547`.** The recommendation record fits any writing path. It may carry `path_reason` (`scheme`, `scheme_version`, `code`): the path's own coded reason, kept beside `missing_authority`, which stays the closed list. The path maps each of its codes to one or more codes of that list. The proposed act keeps its class as given, whether or not this chart defines it, and its act type only where the writer gave one. `proposed.content_schema` (`id`, `version`, `sha256`) names another schema the content was declared under, and is allowed only for `sign` or `new_version`. Adoption creates an act validated under CA-01. A practitioner's own draft names a type in force (CA-09), so a sign-off of a draft whose type was retired is refused and the draft is kept; decision content without a draft is never refused for its class or type. | AN-09, AN-11, CA-09 |
| CD-52 | **PROPOSED.** "Made in the chart." As the fail-closed default, a sign-off counts only when made in the practitioner's own openChart session, so a decision another system carries counts as the practitioner's only through adoption. Ruling 35 has physicians working in openChart for now. An act version is written by a human, in the chart: its writer's `kind` is `human`. Whether a sign-off made with openWallet and openSig in another system, and proved to the chart, also counts is Open Question 17. | AN-08, CA-02, CA-10 |
| CD-53 | **PROPOSED.** The sign-off statement. At re-authentication openChart issues a single-use challenge for one sign-off. The statement is the RFC 8785 canonical JSON of the act identifier and version, the patient triple, the act class and act type, the action, the signature role (`author`, `cosigner` or `actor`), the signer, the attestation code and version, the content and provenance digests, the signing time and the challenge. The openSig attestation is over its SHA-256, recorded as `statement_sha256` with the challenge, so a captured attestation cannot stand in for another action, act or time. | CA-04 |
| CD-54 | **PROPOSED.** The account-to-wallet binding is made only in the practitioner's own re-authenticated session, with a proof of possession from a key the wallet declares. It is audited and listed for the medical director and the administrative role. One wallet binds to one account. Unbinding applies at once. An administrator or the medical director may suspend a binding but never create one. | AU-07, CA-04 |
| CD-55 | **PROPOSED.** A human is identified by their named account only, as the ruling's table says. Clinical role, licence attestation and wallet are recorded where they apply; their absence never makes a writer unidentified, and a sign-off without them fails as CA-04 states. | AN-02 |
| CD-56 | **PROPOSED.** "Malformed" in clause 18 is read narrowly: content the chart cannot read, or that breaks the envelope of the record it arrives in. A recommendation's content is checked only for being a well-formed object, on every path, openChart's own included. The act-validity rules (class content, act types, code sets, the class rules) apply at adoption, and a failure is recorded on the recommendation. The owner is asked (Open Question 18). | AN-09, AN-11, AN-12, CA-09, CA-12, DX-01, DX-03 |
| CD-57 | **PROPOSED.** `external_ref` (issuer, namespace and value) names a human or system party that has no account or registration in this chart, whose identity another system vouches for (`asserted_by`). It is never the writer, and such a human carries no openChart clinical role. | AN-02, AN-04 |
| CD-58 | **PROPOSED.** Recording that an order was carried out is a record of work done, not a medical decision. It needs the `complete` scope and no sign-off under CA-04. One attempted without the scope changes nothing and is kept in the order's trail as a report attributed to its writer, shown to the order's signer. The owner is asked (Open Question 21). | AN-06, AU-04, OR-02 |
| CD-59 | **PROPOSED.** Interoperability reads leave out recommendation records and information records until a governed mapping can carry their marker. In openChart they stay readable, marked, to anyone who can read the chart. The owner is asked (Open Question 19). | CA-13, AN-05 |
| CD-60 | **PROPOSED.** A draft is not yet an addition: AN-05's permanence applies from submission. A draft carries `entry_class` `draft` and no signature, and a signed act carries `entry_class` `decision`. | AN-05, AN-14, CA-05 |
| CD-61 | **PROPOSED.** An AI named with no `openwallet_id`, or with one that the delivering system's registration does not cover, cannot be identified, and the general rule refuses the addition (clause 2), except where a writing path's own quarantine applies under ruling 90. An AI that the delivering relay's registration covers is recorded as the decision maker of what it sends, its identity asserted by the relay. | AN-01, AN-02, AN-08 |
| CD-62 | **PROPOSED.** openChart recognizes test data only by a context the writer declares (`test`, `scenario` or `simulation`), on the submission or in its registration, or by a patient record the practice marks as a test patient. It never infers test data from content. | AN-12 |
| CD-63 | **PROPOSED.** A clinical note's content is information (clause 9: an observation, a summary). The practitioner's signature on a note or an encounter is a sign-off, which is a decision. A note from a writer without the authority to sign it is kept as information under its writer's name (`record_kind` `information`, marked not signed off), never as a "not an authorized decision" recommendation. A note draft so kept is closed as `cancelled` with reason `kept_as_information`, naming the record. Such a note never counts as a final note (EN-04), is never published, and is not exposed through interoperability reads (CD-59). The owner is asked (Open Question 20). | AN-06, AN-14, CA-03, EN-04 |
| CD-64 | **PROPOSED.** A submission that repeats an earlier one, from the same writer with the same `submission_ref`, is answered with the first result and adds nothing, as the AI write path answers a repeat with `duplicate`. | AN-10 |

## Conflicts and tensions

Twenty-two are recorded. CT-6 to CT-10 are resolved by the other drafts' current text. CT-1, CT-14 and CT-15 are settled by owner rulings 84, 85 and 88. CT-16 is ruled (ruling 89) and stays recorded until the follow-up of ruling 93 lands. Each of the other thirteen (CT-2 to CT-5, CT-11 to CT-13 and CT-17 to CT-22) needs the owner's disposition before ratification. None is resolved by this draft on its own authority. **This change does not claim to be free of conflicts.**

| # | Tension | Status |
|---|---|---|
| CT-1 | **Ratified text** (ruling 67: the ratified texts stand). `expanded-patient-intake`, "Intake does not confer clinician or autonomous authority": "No intake, supplement statement, API response or extension event SHALL create a prescription, diagnosis, order, administration, treatment recommendation or autonomous action." Clinician acts are created through openChart's versioned API. This is the same sentence as `define-ai-authored-clinical-records` AT-1, which that change routes to this foundation (its minimum item 11). The ratified feature text, `specs/001-expanded-patient-intake/spec.md` FR-008, says the same: "no API response or event creates a prescription, diagnosis, order, administration, recommendation, or autonomous action". | **Settled by ruling 84: read narrowly.** The sentence "bars automatic creation from intake". A clinician signing through the API is not barred by it: the clinician's authenticated, signed command creates the act, and no intake, statement, API response or extension event does (CA-10, CA-11). The small clarifying amendment that ruling 84 directs is proposed under "Proposed clarifying amendment (ruling 84)", for the owner to apply to this requirement at ratification. No MODIFIED delta is needed. |
| CT-2 | **Ratified text.** The same requirement: "Patient statements SHALL remain visibly patient-reported until an authorized clinical workflow records another assertion." "Until" could be read as letting a statement stop being patient-reported. | Reading proposed: this change is that authorized workflow. It records a separate, signed assertion, and the statement stays patient-reported for good (CA-11, DX-02). This is stricter than the text, not a conflict. Owner confirms. |
| CT-3 | **Ratified text and built code.** The ratified requirements give statements a "verification state". The built field `verification_state` offers `clinician_verified`, which could be read as a clinician assertion made on a patient statement. | This change never sets it (CA-11, CD-22). Owner decides whether `clinician_verified` is retired, defined by a governed change, or left unused. Meanwhile, a statement marked `clinician_verified` by any path is still patient-reported and never a diagnosis. |
| CT-4 | **Published openChart contract.** `contracts/p4-compatibility-declaration.yaml` guarantees "every statement assertion_kind=patient_reported; no prescription, diagnosis, order, administration, or autonomous action is ever emitted". This change's reads and publication emit clinician-authored diagnoses, procedures and, in the chart, orders and prescriptions. | The guarantee is scoped to component p4, the intake API, and stays true for it. This change must publish its own compatibility declaration (task 5.1), and consumers must not read p4's as covering acts. Owner confirms. Same reading as AT-4 of `define-ai-authored-clinical-records`. |
| CT-5 | openChart `AGENTS.md`: "Do not enable autonomous clinical actions by default." Some steps happen automatically: publication notifications, co-signature escalation, and an order's release at the time its signer chose. | Not a conflict by its letter. Each step carries out a named clinician's signed decision, or alerts a human, and decides nothing clinical. Recorded for the owner's confirmation. |
| CT-6 | `define-ai-authored-clinical-records` minimum item 5 (treatment plans) is not provided, because ruling 73 leaves treatment-plan records for later. | **Resolved for that change** at `079dd36`: its item 5 records treatment plans as not in the foundation and as a prerequisite of its `treatment_plan_change` act class. |
| CT-7 | Order and prescription status names. | **Resolved** at `079dd36`: `define-ai-authored-clinical-records` uses `pending_release`, `released`, `discontinued`, `cancelled` and `entered_in_error`, with signing as an event, and maps its own Tier 2-only contract codes in its AD-34. |
| CT-8 | Dispense and transmission states. | **Resolved** at `079dd36`: `define-ai-authored-clinical-records` asks for no dispense or transmission state. `transmission_status` stays reserved at `none_recorded` (RX-04) until a later e-prescribing change. |
| CT-9 | The medical director and clinical roles were defined, or left to planning, in three drafts. | **Resolved.** `define-ai-authored-clinical-records` (at `6989780`) and `define-clinical-message-inbox` (at `e644fb3`, its Decision 15) cite AU-01 to AU-05 as the single definition and define no roles of their own. Their grants live in AU-02 (CD-37) and, under ruling 92, AU-06. |
| CT-10 | Field name. | **Resolved.** `define-ai-authored-clinical-records` has used "author type" since `5a9947f`, still so at `079dd36`, as MI-12 and this change do. No naming difference remains. Under ruling 80 an act keeps `author_type` `clinician`, and every addition's writer, the parties on whose behalf it was written and a recommendation's decision maker are each a party with a `kind` (AN-02). |
| CT-11 | `openpractice-ehr-clinical-facts/1.0` (digest `6b2071fe…`) carries a coding as system and code only, with a code of at most 32 characters. openPractice cannot tell which code-system version a code came from, and this change stores codes of up to 64 characters. | This change publishes system and code only (PB-02). A code that does not fit blocks publication of its encounter, with an integration exception (PB-04). Carrying the version needs a MINOR version of the openPractice contract, owned by `define-mvp-practice-foundation`. Owner item. |
| CT-12 | openPractice FD-11 lets the open-source core ship ICD-10, HCPCS Level II and other sets it calls license-free. openChart bundles no code set and asserts no license status (CA-12). The two systems may therefore load different code-set versions. | Not a conflict: FD-11 governs openPractice, and openChart is stricter. Combined with CT-11, a version mismatch between the two systems is not detectable under 1.0. Owner item. |
| CT-13 | `define-openpractice-boundary`'s design says "No clinician-authored encounters, diagnoses or procedures exist" and "Every statement in openChart is patient-reported". CF-06 holds `false` "until" a capability exists. | Not a conflict with its requirement text: PB-01 meets CF-06's condition without editing it. Those design statements become stale once this change lands, and its Open Question 2 is answered by this change. |
| CT-14 | The shared workflow protocol hands an OpenSpec change to exactly one Spec Kit feature. This change hands off to five ordered features: clinical authority first (#3 MT-22), and prescriptions last (ruling 74). | **Settled by ruling 85**, which allows "the same ordered multi-feature exception" that ruling 1 gave openPractice. The handoff has five ordered features (CD-31). |
| CT-15 | `define-openpractice-boundary` CF-01 limits publication to patients with an `active` `openpractice` link. PB-03 delivers queued retractions, and corrections converted to retractions, after a link ends `revoked` or `superseded`, so that openPractice stops billing facts openChart has withdrawn. | **Settled by ruling 88:** "Retractions of facts already published under that link are delivered, as pointers only. No new facts and no reads are served." CD-35 carries it. This is an exception to CF-01's letter, which `define-openpractice-boundary` may record. |
| CT-16 | `openpractice-ehr-clinical-facts/1.0` offers only `clinical_fact.entered_in_error` as a retraction. PB-03 uses it for a diagnosis amended away from `confirmed`, and for an encounter withdrawn because a restricted act was added, neither of which was entered in error. | **Ruled (ruling 89) and being drafted.** Ruling 89 adds a retraction reason code to `openpractice-ehr-clinical-facts` "now, while 1.0 is still unratified", in a small follow-up pull request to openPractice-spec (ruling 93), which is being drafted now. Until it lands and this change is re-pinned to it, PB-03 keeps using `clinical_fact.entered_in_error`, whose billing effect, retraction, is right but whose reason is misstated. This tension stays recorded until then. |
| CT-17 | **Ratified text.** The ratified intake path (`expanded-patient-intake`) adds patient statements to the chart. Ruling 80 says every addition records its writer and provenance (AN-04). Intake records its own submitting identity and audit, not AN-04's fields. | Not resolved here: this change does not edit the ratified intake capability. The owner decides whether a later governed change brings intake additions under AN-04 (Open Question 15). Meanwhile, the intake path's own identity and audit apply, and no intake addition is a decision. |
| CT-18 | Two sources of licence facts. AU-03 records licensure and prescriber facts as practice-supplied attestations that openChart does not verify. Ruling 98 has a one-administrator practice record a licence verification against the board's public record. Ruling 151 says the practitioner's openWallet holds the verification of licence. | Recorded, not resolved. Every ruled check stays. The practice's attestation under the grant and the wallet's licence verification must both hold for a sign-off (CA-04, AU-03), and ruling 98's check still governs the first designation (AU-01). When they disagree, neither governs alone: the sign-off does not count, and the entry is a recommendation naming the record that does not support it (`practice_attestation_not_in_force`, `licence_verification_missing`, or both; AU-03). The owner decides whether the wallet's verification should replace any of them (Open Question 16). |
| CT-19 | CA-14 says every capability works with no external system. Ruling 151 makes every sign-off depend on the practitioner's openWallet and openSig. | Recorded. Where they cannot be reached, a sign-off attempt leaves its draft open and is recorded, never refused (AN-14). Whether they can run inside a standalone deployment is Open Question 10. |
| CT-20 | Ruling 151 needs a licence verification held in an openWallet, and an openSig attestation that a signature is from that wallet. openWallet at `a2d554d` defines no practitioner profile and no licence verification yet. Its ratified rule also says a wallet SHALL NOT become a prerequisite for operating a domain. openSig has no specification on `main`. Its open pull requests make clinical production workflows a non-goal and keep clinical attestation in openChart, and neither mentions openWallet. | Recorded. This change invents nothing about either project, and fails closed. Until both specify what ruling 151 needs, those checks cannot be made, every sign-off attempt fails in the way the author can cure later, and drafts stay drafts (AN-14; tasks §2.7; Open Questions 9 and 11). openChart's records stay readable and its patients resolvable with no wallet (AN-02), but no decision can take effect without one. Whether that conflicts with openWallet's rule is for the owner. |
| CT-21 | Ruling 80, clause 11, says an AI's authority would be the mode and scope that the medical director approves. Ruling 151 says every medical decision needs the practitioner's sign-off. | Not resolved, as the encoding brief directs. Today no AI holds decision authority (clause 19), so the two never meet. The owner answers before limited or full practice is ever switched on (Open Question 12). |
| CT-22 | **Ratified text.** The canonical requirement "Intake does not confer clinician or autonomous authority" says that no "API response or extension event SHALL create a … treatment recommendation". Under ruling 80, an identified system may add act content through the API, and it is entered as a recommendation record. | Recorded, not resolved. Under ruling 84's narrow reading, the sentence bars automatic creation from intake, and a recommendation from an identified writer is not created from intake. A recommendation creates no prescription, diagnosis, order, administration or autonomous action (CA-10). But the sentence's words "treatment recommendation" do read on such a record, and ruling 84's proposed clarifying sentence does not mention recommendations. The owner decides whether it should. |

## Risks / Trade-offs

- **[A wrong-patient or wrong-content signature]** → Re-authentication at signing; a content digest bound to the signature; entered-in-error handling; nothing deleted.
- **[Patient-reported content mistaken for a clinician's]** → Separate records, explicit derivation, the statement never changed, and labels on every surface.
- **[A recommendation mistaken for a decision]** → No act status. It is never signed, released, published or billed, it is marked "not an authorized decision" wherever it is shown, and it never counts where a decision would (AN-09).
- **[An addition from a writer the chart cannot trust]** → Identification, registration and suspension, an identity basis on every party, and the AI's openWallet ID checked against the delivering system's registration (AN-01 to AN-03).
- **[No decision can take effect until openWallet and openSig specify what ruling 151 needs]** → Every sign-off attempt fails closed, and a practitioner's drafts stay drafts, with every attempt recorded. Nothing is lost, and the same draft can be signed off once the checks can be made (CT-20, tasks §2.7).
- **[A captured attestation replayed for another action]** → The attestation is over a statement that binds the action, the act, the time and a single-use challenge (CD-53).
- **[An administrator binding one person's account to another's wallet]** → Only the practitioner binds, in their own session, with proof of possession; an administrator can only suspend (AU-07).
- **[Prescribing without safety checks]** → RX-02 refuses every signature until `define-prescribing-safety-checks` is ratified, built and satisfied (ruling 74). Controlled and unknown classifications are refused (ruling 83; CD-20).
- **[Over-privileged users]** → Grants per class and action, recorded by the medical director. `System Manager` confers nothing. Reductions apply at once. Independent attestation, a designator who is never the designee, and visible self-grants (CD-34). The first designation is confirmed by a second person or backed by a recorded licence verification (ruling 98; CD-38, gate §2.6), and listings go to the medical director too. Residual risk: two colluding people. Account provisioning and identity proofing are decided in planning and governed by the constitution.
- **[Billing from unfinished documentation]** → Only final, clinician-signed encounter facts are published, after any co-signature, by reference, with forward-only corrections.
- **[Code-set licensing]** → Nothing bundled; practice-supplied sets; verification before any bundling.
- **[Co-signature backlog]** → Escalation to the medical director, who can narrow grants.
- **[A large first build]** → Five ordered features, each gated, with clinical authority first.
- **[No constitution]** → Planning is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly, check the schema digest and run the self-test. Brett Heap disposes the open tensions and CD-1 to CD-51, including the design calls made under rulings 80, 83, 85, 87, 88, 89, 92, 98 and 151, stamps `Ratified by` and sets `Status: ratified`. At ratification he also applies ruling 84's clarifying amendment to the ratified `expanded-patient-intake` requirement.
2. Adopt openChart's constitution through separate governance.
3. Feature (1): clinical authority (roles, the medical director, attestations and every grant scope, AU-06 included, under ruling 92), the confirmation path of ruling 98, and the general rule for additions (AN-01 to AN-14), with system and device registration and the binding of each practitioner's account to their wallet (AU-07). No decision takes effect live until tasks §2.7 is met.
4. Feature (2): acts, signing, encounters and notes, contract tests against the content schema, and the standalone regression suite.
5. Feature (3): diagnoses, procedures and publication, against an openPractice double at the PL-04 digest. Live publication waits for `define-openpractice-boundary` to be ratified and built.
6. Feature (4): orders. Feature (5): prescriptions, only after `define-prescribing-safety-checks` is ratified (ruling 74); every signature, co-signature and release calls that change's gate decision.
7. Land the leg pull requests and the root pin bump for each feature. Archive after the last.
8. Rollback: disable a feature's capability. Signed acts stay readable; nothing is deleted. Disabling feature (3) returns the capability result to `false`.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks planning for every feature. Recommendation: adopt it through separate governance before any feature's plan.
2. **Owner dispositions** of the open tensions (CT-2 to CT-5, CT-11 to CT-13 and CT-17 to CT-22) and of CD-1 to CD-51. Rulings 83, 85, 87, 88, 89, 92 and 98 settled the decisions behind CD-20, CD-31, CD-33, CD-35, CD-36 and CD-38 to CD-41, and rulings 80 and 151 the rules that CD-42 to CD-51 encode; the mechanics in those design calls still need his disposition. These block ratification. Recommendation: dispose of them together, before ratification, starting with the calls marked as put to the owner.
3. **Sensitive record categories and minors' records.** Do some categories, or records of minors, need segmentation, special consent handling or restricted disclosure, and under which rules? This is a question for counsel; this change asserts no legal rule. Meanwhile, CD-27's restricted mark applies, and nothing marked restricted leaves the chart. Recommendation: put it to counsel before feature (3) publishes anything.
4. **Retention** of acts, versions, drafts, audit trails and grants. The owner and counsel decide. Meanwhile, nothing is deleted. Recommendation: keep everything until counsel sets a retention rule in its own change.
5. **The administrative role that designates the medical director**, and how a practice (tenant) is represented. Planning decides, within AU-01. Recommendation: one named practice-administrator role, the same one that registers systems (CD-43).
6. **Appointment references.** When a MINOR version of the link contract adds appointment events, how is the reference filled? `define-openpractice-boundary` and openPractice decide. Meanwhile, CD-17 applies. Recommendation: leave the reference empty until that MINOR version exists.
7. **Controlled-substance prescriptions.** Closed by ruling 83: they are refused in this change, and controlled-substance prescribing goes into a later change alongside electronic prescribing (CD-20).
8. **A path for device data.** Ruling 80 says how a device is identified and what a reading records (AN-13). No openChart draft defines how device data enters the chart. Recommendation: a later governed change of its own defines the path, the device registration it relies on, and how readings are shown. Meanwhile, no operation accepts device readings.
9. **openWallet's licence verification.** What is the "verification of license" held in a practitioner's openWallet? Who issues it, what does it cover, how does openChart read and check it, and how is it revoked? openWallet names a practitioner profile as a successor, gated on a consumer, and defines none yet. Recommendation: the owner directs openWallet to specify that practitioner profile, with openChart as its consumer, before any decision can take effect. Meanwhile, CA-04 fails closed.
10. **openWallet and openSig in a standalone deployment.** Do they run inside the practice's deployment, or as external services? Recommendation: require that a sign-off can be checked inside the deployment, so that CA-14's standalone guarantee also holds for decisions. Meanwhile, a service that cannot be reached makes a sign-off a recommendation.
11. **The openSig attestation.** What does openSig attest, over which digests, and how does openChart verify it against the wallet? openSig has no specification on `main`, and its open pull requests make clinical production workflows a non-goal and keep clinical attestation in openChart. Recommendation: the owner either directs an openSig change for a wallet-bound attestation of a chart entry, or rules that openWallet's own proof of possession (a signature from the holder's key over the request) is that attestation. Either way, the attestation must be over the sign-off statement of CD-53, with its single-use challenge, so that it binds the action, the act and the time. Meanwhile, CA-04 fails closed.
12. **An AI's authority under clause 11 and ruling 151** (CT-21). Recommendation: read ruling 151, the later ruling, as governing, so that an AI with an approved mode and scope still makes only recommendations until a practitioner signs one off; confirm this before limited or full practice is ever switched on. Meanwhile, no AI holds decision authority.
13. **Which other actions are medical decisions** that need a practitioner's sign-off under ruling 151: AI consult reviews (AU-02), inbox actions and patient replies (AU-06). Recommendation: treat a consult review and a clinician's patient reply as needing the sign-off, and inbox ownership actions as workflow that does not. Meanwhile, each needs its grant, and without it takes no effect (CD-50).
14. **Who registers and suspends systems and devices.** Recommendation: the administrative role named in planning registers them, and that role or the medical director suspends them at once (CD-43).
15. **Intake additions and AN-04** (CT-17). Recommendation: a later governed change aligns the intake path's provenance with AN-04, without changing what intake may create.
16. **Two sources of licence facts** (CT-18). Recommendation: keep both until openWallet's licence verification is specified and in use, then decide whether it replaces the practice's attestations for clinical roles. Keep ruling 98's check for the first designation.
17. **Where a carried decision's sign-off may be made** (AN-08, CD-52). Reading A: only in the practitioner's own openChart session, so a decision another system brings counts as the practitioner's only through adoption. Reading B: a practitioner logged in to the other system who signs with their openWallet and openSig, which the chart verifies, has made "their own sign-off". Recommendation: in the chart only in version 1; a sign-off made in another system counts once openWallet and openSig can prove it to the chart. Meanwhile, the fail-closed default applies.
18. **What "malformed" means in clause 18** (CD-56). Reading A: any content that fails the act schema, so a human's uncoded diagnosis is refused while an AI's content kept under its own schema is not. Reading B: only content the chart cannot read or that breaks the record's envelope. Recommendation: reading B, so that clause 17 treats humans and systems alike, with the act-validity rules applied at adoption. Meanwhile, reading B applies.
19. **Whether an interoperability reader is "reading the chart"** (CA-13, CD-59). Reading A: it is not, so recommendations and information records stay out of interoperability reads. Reading B: it is, so they must be exposed, marked. Recommendation: leave them out until a governed mapping can carry the marker, then expose them marked. Meanwhile, they are left out.
20. **Whether a clinical note's content is a decision** (CD-63). Reading A: the chart keeps the list, and a note is an act class, so its content is a decision and a nurse's unsigned note is a "not an authorized decision" recommendation. Reading B: clause 9 calls observations and summaries information, so a note's content is information, and only the practitioner's signature on it is a decision. Recommendation: reading B. Meanwhile, reading B applies.
21. **Whether recording a completion is a medical decision** (CD-58). Recommendation: it is a record of work done, needing the `complete` scope and no ruling-151 sign-off. Meanwhile, that applies.
22. **Who is the decision maker when a relay delivers an AI's decision content** (AN-08, CD-61). Read literally, clause 12 could make it the relay's recommendation, with the AI as the claimed decision maker. Recommendation: an AI that the relay's registration covers is the decision maker, its identity asserted by the relay. An AI the registration does not cover cannot be identified, and the addition is refused (CD-61). This affects `define-ai-authored-clinical-records`.
