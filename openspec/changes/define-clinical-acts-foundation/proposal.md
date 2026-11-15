code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: openChart's core clinician-authored clinical record. It has one act model for six act classes: encounter, clinical note, diagnosis of record (encounter diagnosis and problem-list condition), procedure or service performed, a generic order, and the prescription record. The model covers the identification and provenance of every addition to a chart, and the recommendation record for a decision made without authority (owner ruling 80); authorship with an act author type of `clinician`; status lifecycles; signing as the practitioner's sign-off with openWallet and openSig (owner ruling 151); amendment by new versions; entered-in-error handling, a co-signature hook, provenance and audit, and an act-type registry. It also covers clinical roles, the medical director designation and role grants recorded in openChart, with practice-supplied, unverified licensure and prescriber facts; explicit, attributed creation of clinician records from patient-reported intake; codings from practice-supplied code sets; the canonical content schema `openchart-clinical-act-content/1.0`; a FHIR R4-compatible mapping at contract level; and publication of signed, final encounters, their diagnoses and procedures to openPractice under `openpractice-ehr-clinical-facts/1.0`, by reference, with forward-only corrections. Out of scope: results ingestion; care plans and treatment-plan records; immunizations; clinical decision support; allergy and interaction checking (the required later change `define-prescribing-safety-checks`); electronic transmission of prescriptions to pharmacies, controlled-substance electronic prescribing, and controlled-substance prescribing (ruling 83); order transmission; AI authorship of acts (`define-ai-authored-clinical-records`); a path for device data; openWallet's licence verification and openSig's attestation, which this change consumes and does not define; billing and coding validation (openPractice); and any change to the ratified `expanded-patient-intake` requirements.
target_release: Clinical-acts foundation v1, delivered as five ordered Spec Kit features, each gated on ratification (owner ruling 85): (1) clinical authority; (2) encounter, note and signing; (3) diagnoses, procedures and publication to openPractice; (4) orders; (5) prescriptions, which also waits for `define-prescribing-safety-checks` to be ratified (owner ruling 74). The change archives when landed, validator-green open_chart revisions for all five features meet four conditions. They pass contract tests against `openchart-clinical-act-content/1.0` at the recorded digest, and against an openPractice double for publication. They still pass the standalone golden-intake round trip with no external system. They enter decision content made without the authority as a recommendation, never as an act, and never cancel a draft on a failed sign-off. They refuse an addition only for the reasons ruling 80, clause 18 keeps, and until a device path exists no operation of theirs accepts device readings (AN-13). And they refuse every prescription signature where the prescribing-safety gate is not met.
Status: draft
Ratified by: pending. The decisions encoded here rest on rulings Brett Heap made on 2026-11-14 and 2026-11-15, including ruling 72 ("draft the openChart clinical-acts foundation change too"), ruling 73 (the scope) and ruling 74 (the prescription gate), and on rulings 82 to 85, 87 to 89, 92, 93 and 98 from the second batch of 2026-11-15. Later that day he made ruling 80 (who may add to a chart, and what counts as a decision) and ruling 151 (the practitioner's sign-off with openWallet and openSig). They are recorded in `design.md` under "Owner rulings". Rulings are not ratification. The design calls in `design.md`, including those that implement a ruling, are proposed, not ruled. Ratification requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

openChart is the public, neutral clinical chart, and the doctor's clinical interface on mobile or workstation (rulings 34 and 35). Its built scope is patient intake only:
- `OC Patient` and `OC Patient External Identifier`;
- `OC Intake Submission`;
- eight patient-reported statement families.

There are no clinician encounters, notes, diagnoses, procedures, orders or prescriptions. Every statement is patient-reported, and the ratified `expanded-patient-intake` capability keeps it so.

Three draft changes, none yet on main, wait for this foundation:
- **`define-ai-authored-clinical-records`** (openChart-spec#4) lists it as its required prerequisite, with twelve minimum contents. Its Tier 2 adds AI authorship, an authority grant, clinician co-review and reversal on top of the acts defined here. This change defines no AI authorship of acts: under ruling 80, act content an AI adds is entered as a recommendation (AN-09).
- **`define-openpractice-boundary`** (openChart-spec#2): its `openpractice-clinical-fact-publication` capability reports "no billable facts" until a clinical-encounter capability exists (CF-06, Open Question 2). openPractice needs final, signed encounter documentation, diagnoses and procedures, with forward-only corrections and references rather than copies (`opensoft/openPractice-spec` `define-mvp-practice-foundation`, EB-13 to EB-16).
- **`define-clinical-message-inbox`** (openChart-spec#3) records clinician replies as clinical communications (MI-12). It says that only a separately governed clinical workflow may record a clinical fact of record.

This change is that workflow: openChart's core clinician-authored clinical record. Under ruling 80, it also holds the general rule for every addition to a chart, because it holds the act model and the single grant model (ruling 92).

## What Changes

The scope below is ruled (owner ruling 73). Additions to the chart are ruled by rulings 80 and 151; the design calls that encode them are proposed.

- **Additions to the chart** (AN-01 to AN-14; rulings 80 and 151).
  - Any human or system the chart can identify may add to a patient's chart: a clinician, other staff, the patient, an AI, a device or another system. An addition whose writer it cannot identify, or whose writer is an unregistered system or device or is suspended, is refused, and nothing is stored. Another party it cannot identify is recorded as not identified. By default (proposed), an addition for an AI that a registered writer's registration does not cover is held in quarantine in front of a clinician, not added.
  - Each writer is identified by its kind: a named account, the patient's verified link, an AI's openWallet ID with its model and version, a device's make, model and serial or a resolvable device ID, or a registered system and its operator. Another organization's clinician or system is named by its own identifier, vouched for by the system that delivered it. Systems and devices are registered first, and the practice can suspend any of them at once.
  - Every addition records when it was received and when the information arose, where it came from, what wrote it and on whose behalf. That record is permanent and readable by anyone who can read the chart.
  - Decision content takes effect only when its class and act type are in force in the act-type registry. Otherwise it becomes a recommendation, never refused and never unmarked information. A clinical note's content, or any other record of information, is information only when it validates against its kind's closed, published shape, and anything else is a recommendation; and an order's completion is a record of work done; a prescription is never completed in this version. openChart determines the class, and a class the writer claims decides nothing.
  - A decision counts only when its decision maker held the authority at that moment and a practitioner signed it off in their own logged-in session, with their openWallet and openSig (ruling 151). A decision made on someone's behalf counts only with their own sign-off.
  - A decision made without authority is never refused for that reason. It is kept in full, as given, as a recommendation record, marked "not an authorized decision", naming the missing authority, with no effect. Its submitter is told at once, and it goes to a clinician who holds the authority, who adopts it as a decision of their own or declines it.
  - A failed sign-off never loses what the author wrote. A failure the author can cure leaves the draft open, and a failure of authority makes a recommendation tied to the draft, which is held for it. A note from a writer without the authority to sign it is kept as information, and its writer is told at once.
  - openWallet and openSig do not yet specify the licence verification and the attestation that ruling 151 needs. Until they do, those checks cannot be made, so a practitioner's drafts stay drafts and no decision takes effect (tension CT-20).
- **One act model** (CA-01 to CA-15). Six act classes share one envelope and one canonical content schema, `openchart-clinical-act-content/1.0`, pinned by SHA-256 in `contracts/SHA256SUMS`, with synthetic fixtures and a self-test. Every act has:
  - a named practitioner author, with the author type `clinician`. Decision content from any other author is entered as a recommendation record, never refused for that reason, and a note's content from any other author is kept as information;
  - a closed status lifecycle;
  - a signature that is the practitioner's sign-off: re-authentication in their own session, their openWallet's signature with openSig's attestation over a statement that binds the act, the action, the signer's session account, the time, a single-use challenge and, for an encounter, the manifest of every record its signing view showed, the wallet's licence verification and the grant in force (ruling 151). A discontinuation, an entered-in-error mark, a co-signature and the cancellation of a signed order are sign-offs too. An audit verifier recomputes every digest from the stored record;
  - amendments as new versions, never destructive edits;
  - entered-in-error handling;
  - a co-signature hook (before effect, or after the fact within a window, escalating to the medical director);
  - full provenance and audit;
  - an act type from a registry that carries reserved and emergency-management flags.

  Acts are created only by a named practitioner through the versioned service boundary. Nothing is created from intake automatically. Codes come from practice-supplied code sets; openChart bundles none and asserts no license status. Acts have a FHIR R4-compatible mapping at contract level, with no conformance claim.
- **Authority** (AU-01 to AU-07). openChart defines clinical roles (`clinician`, `nurse`) and one medical director per practice. The designating account is never the designee, and the designee's role rests on a licensure attestation recorded by another named human. The first medical director is set up by one audited bootstrap act. Grants per act class and action, plus a `review` scope over `ai_consult_record` for AI consult reviews, are recorded by the medical director, and a self-grant is flagged, independently attested and shown. Licensure and prescriber facts are attestations supplied by the practice, never recorded by their own subject, and not verified by openChart. Under ruling 98, a second person confirms the first designation, or a sole administrator records a licence verification against the licensing board's public record, and these acts are listed for the medical director too. Under ruling 92, inbox authority lives in this grant model, set by the medical director: AU-06 adds the clinical message inbox's ownership, reply and clinical-need marker scopes, none of which reaches an act. A practitioner binds their own wallet to their account, only in their own session, with proof of possession from a key whose custody evidences that the holder acted (AU-07). Every action is checked against its decision maker's authority in force, whatever kind of decision maker it is. An action without that authority takes no effect and is entered as a recommendation, and reductions apply at once. Only a named human practitioner signs off a decision. No AI, agent, device or plain integration holds decision authority today, and no agent or automated process authors, signs or co-signs (ruling 67; ruling 80, clause 19).
- **Encounters and notes** (EN-01 to EN-06):
  - an encounter lifecycle (in progress, final, amended);
  - an optional appointment reference only, since openPractice owns the appointment (ruling 31);
  - signed notes and addenda;
  - finalization only when documentation is complete;
  - a signed encounter amendment for every later change;
  - no requirement depends on form factor (ruling 35).
- **Diagnoses and procedures** (DX-01 to DX-03): coded, clinician-asserted encounter diagnoses and problem-list conditions, kept distinct from patient-reported conditions, and coded procedures performed.
- **Publication to openPractice** (PB-01 to PB-05). This change is the capability that CF-06 waits for. A signed, final encounter, with its coded diagnoses and procedures, is published under `openpractice-ehr-clinical-facts/1.0`:
  - by reference;
  - with codings carrying the system and code only;
  - with encounter diagnoses only when `confirmed`, and a retraction if a published one is later refuted (ruling 87);
  - with forward-only corrections and retractions, queued whatever the link state and delivered when the link returns to `active`. Retractions still reach openPractice, as pointers only, after a link is revoked or superseded (ruling 88). A fact whose latest version could no longer be published is retracted, and every withdrawn encounter reads the same.

  openChart still works with no openPractice.
- **Orders** (OR-01 to OR-04). One generic order record covers laboratory, imaging, referral, procedure and other orders. Its lifecycle is draft, pending release, released, completed, discontinued, cancelled and entered in error. A released order is never amended. A prescription has the same lifecycle without completed: in this version it ends only by a signed discontinuation. openChart transmits no order and ingests no result.
- **Prescriptions** (RX-01 to RX-04). The record of the prescribing decision carries a controlled-substance classification in which unknown counts as controlled.
  - **Binding gate (ruling 74):** no prescription is signed, co-signed or released in any deployment where the prescribing-safety gate of `define-prescribing-safety-checks` is not met.
  - Controlled or unknown prescriptions are refused, and controlled-substance prescribing goes into a later change alongside electronic prescribing (ruling 83).
  - There is no pharmacy transmission, no controlled-substance electronic prescribing and no dispense record.

## Capabilities

### New Capabilities

- `chart-additions` (AN-01 to AN-14): who may add to a chart, identification, registration and suspension, provenance, information and decisions, decisions made on someone's behalf, the recommendation record and its review, what is still refused, devices, and drafts (rulings 80 and 151).
- `clinical-act-record` (CA-01 to CA-15): the shared act model, the content schema, intake derivation, coding, the FHIR mapping, standalone operation and restricted acts.
- `clinical-authority` (AU-01 to AU-07): roles, the medical director, grants and practice-supplied attestations, the grant scopes for AI consult review and the clinical message inbox, and the binding of a practitioner's account to their wallet.
- `clinical-encounters` (EN-01 to EN-06): encounters, notes, finalization and encounter amendments.
- `clinical-diagnoses-and-procedures` (DX-01 to DX-03).
- `clinical-acts-publication` (PB-01 to PB-05): the source of billable facts under `openpractice-ehr-clinical-facts/1.0`.
- `clinical-orders` (OR-01 to OR-04).
- `clinical-prescriptions` (RX-01 to RX-04).

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged. Possible conflicts with ratified openChart text (CT-1 to CT-3, CT-17 and CT-22) and with the published p4 compatibility declaration (CT-4) are recorded as tensions in `design.md`. Ruling 84 reads CT-1's sentence narrowly. The clarifying amendment it directs is proposed in `design.md`, for the owner to apply to the ratified `expanded-patient-intake` requirement at ratification; this change does not edit it.

## Required later changes

- **`define-prescribing-safety-checks`** (REQUIRED before any prescription can be signed; ruling 74; being drafted under ruling 75). Its minimum contents are listed in `design.md` under "Required later change: prescribing-safety checks". Feature (5), prescriptions, depends on its ratification.
- Electronic transmission of prescriptions and controlled-substance electronic prescribing, as a later governed change that needs vendor and regulatory verification (ruling 73). Ruling 83 puts controlled-substance prescribing in that change too.
- Results ingestion; care plans and treatment-plan records; immunizations; clinical decision support beyond the prescribing-safety checks; order transmission (ruling 73; `design.md` "Non-Goals").
- A path for device data into the chart (AN-13; Open Question 8).
- In `opensoft/openWallet`: a practitioner profile holding the licence verification that ruling 151 relies on (Open Question 9). In `opensoft/openSig`: an attestation that a signature over a chart entry is from that wallet, or an owner ruling that openWallet's proof of possession is that attestation (Open Question 11). Until both exist, no decision takes effect live (tasks §2.7).

## What is buildable, in order

| Feature | Contents | Gated on |
|---|---|---|
| (1) Clinical authority and additions | AU-01 to AU-07, AN-01 to AN-14 (CD-41, PROPOSED) | Ratification of this change; openChart's constitution. Going live also needs the confirmation path of ruling 98 (tasks §2.6) |
| (2) Encounter, note and signing | CA-01 to CA-15, EN-01 to EN-06 | Feature (1). A decision takes effect live only once openWallet and openSig specify what ruling 151 needs (tasks §2.7); until then every sign-off attempt fails in the way the author can cure, and a practitioner's drafts stay drafts |
| (3) Diagnoses, procedures and publication | DX-01 to DX-03, PB-01 to PB-05 | Feature (2). Publication also needs `define-openpractice-boundary` ratified and its publication surface built |
| (4) Orders | OR-01 to OR-04 | Feature (2) |
| (5) Prescriptions | RX-01 to RX-04 | Feature (2) and **ratification of `define-prescribing-safety-checks`** (ruling 74) |

## Impact

- **openChart:**
  - act storage for six classes, with versions, signatures, lifecycle events and audit;
  - a role, grant and attestation store, and a medical director designation;
  - addition provenance, a system and device registry, a recommendation store with its review routing, information records for notes a writer could not sign, a quarantine for held items that meets AN-01's minimum, and the binding of each practitioner's account to their wallet;
  - an act-type registry and a code-set import record;
  - an extension of the versioned service boundary;
  - the content schema contract;
  - publication through the PL-14 durable outbound store.

  Every component works with no external system, except that a decision's sign-off needs the practitioner's openWallet and openSig (ruling 151; CT-19), and prescription signing also needs the prescribing-safety gate.
- **Dependents:**
  - `define-ai-authored-clinical-records` gets its prerequisite. Eleven of its twelve minimum contents are met. Treatment plans are not, by ruling 73, and that change now records them as a later prerequisite (CT-6 to CT-8 resolved). Its consult review grant lives in AU-02. Under ruling 80 it must change:
    - the relay is the writer, and the AI is named on whose behalf;
    - an AI the relay's registration covers is the decision maker, and by default (proposed) an addition for one it does not cover is held in that change's quarantine in front of a clinician, not added (CD-61; Open Question 22);
    - an AI act attempted without authority is stored as this change's recommendation record (AN-09) instead of being refused, with its content as given and its own codes mapped to `missing_authority`, always with `no_practitioner_sign_off`, and kept in `path_reason`; an AI's action on an existing record uses AN-09's form (`target`, `target_as_given`);
    - it re-pins the content schema at its new digest.
  - `define-openpractice-boundary` gets the capability that CF-06 and Open Question 2 wait for, without any edit to it.
  - `define-clinical-message-inbox` must publish a closed content shape for each record of information it adds to the chart (AN-06, CD-65). It gets the clinical workflow that MI-12 and MI-14 defer to, the roles and grant scopes it cites (AU-01 to AU-06; AU-06 under ruling 92), clinical authority as feature (1) (ruling 92), and a proposed answer to its Open Question 11. Under ruling 80, an inbox action or reply attempted without its grant takes no effect and is entered as a recommendation (AU-06, CD-50); whether a reply needs ruling 151's sign-off is Open Question 13.
  - `define-prescribing-safety-checks`: a recommendation is never a signature, co-signature or release, and never counts as an active prescription in its checks (AN-09). Its checks may still raise an alert from a pending recommendation, labelled as resting on an entry that is not an authorized decision.
- **Governance:** openChart's constitution (`.specify/memory/constitution.md` in `opensoft/openChart`) is still the unfilled Spec Kit template. A Constitution Check, and with it the plan phase of every feature, needs a constitution adopted through separate governance first.
- **Safety:**
  - every act is a named practitioner's, signed off with their openWallet and openSig (ruling 151);
  - every addition's writer is identified, and where it came from is recorded permanently (ruling 80);
  - a decision made without authority is kept as a recommendation with no effect, never refused for that reason, and a failed sign-off never loses what the author wrote (ruling 80);
  - no AI clinical authority (ruling 67; ruling 80, clause 19);
  - signed content is never edited;
  - prescriptions are gated (ruling 74);
  - synthetic fixtures only;
  - no PHI in logs;
  - sensitive categories are an open question for counsel, with a fail-closed restricted mark meanwhile.
- **Tensions:** twenty-two are recorded in `design.md` as CT-1 to CT-22. CT-6 to CT-10 are resolved; CT-1, CT-14 and CT-15 are settled by rulings 84, 85 and 88; and CT-16 is ruled (ruling 89) and stays recorded until the follow-up of ruling 93 lands. Six of them (CT-1 to CT-4, CT-17 and CT-22) concern ratified openChart text or published openChart contracts. CT-20 records that openWallet and openSig do not yet specify what ruling 151 needs, and CT-21 that ruling 80, clause 11 and ruling 151 differ on an AI's authority. Each other open tension needs the owner's disposition.
