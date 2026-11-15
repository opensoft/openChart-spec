## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

This change touches these facts about what is already built. They were checked at `opensoft/openChart-code` revision `30b9645`.

- **DocTypes.** The built DocTypes are `OC Patient`, `OC Patient External Identifier`, `OC Intake Submission`, and eight statement DocTypes: allergy, condition, document reference, goal, medication, observation, supplement and symptom. None holds a message, a clinician-authored record or a work queue.
- **Roles.** Every built DocType grants permissions to `System Manager` only. No clinician, nurse or medical-director role exists.
- **Events.** `emit_submission_event` uses `frappe.publish_realtime`, which never leaves the site.
- **Medx references.** The ratified intake keeps Medx and HealthLinc references as namespaced external identifiers. A test fixture, `tests/fixtures/medx/binding-03-openchart.yaml`, binds HealthLinc, OpenEMR and openChart references to one `medx_patient_id` ("gate G3"). See tension MT-12.

**The openPractice side** is `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation`, PR #6, not yet on main. This change pins it at revision `165aff0`. In this document it is called "the openPractice change", and its identifiers are cited as, for example, "openPractice ER-06". Its capability `escalation-routing` (ER-01 to ER-18) owns the contract `openpractice-clinical-handoff/1.0` and its canonical schema. That change's design lists this inbox as a required companion change, with eleven items; they are checked below under "The openPractice change's companion items".

**This branch is stacked on `define-openpractice-boundary`.** That change is a draft, and this change cites its PL-01 to PL-16, CF-02, CF-05 and CF-06. This change can be ratified only with or after it.

Brett Heap's rulings are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main` (checked at revision `d20de75`). There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. The plan phase waits on adopting a constitution.

## Owner rulings (2026-11-14)

Every row has the same source: **Brett Heap, 2026-11-14, authoring session.** The numbering is shared with the openPractice change. Rows marked "context only" are recorded so the binding text can be checked against them; they add no openChart requirement of their own.

| # | Ruling | Governs |
|---|---|---|
| 34 | openPractice is the gateway and router. Clinical questions go to openChart, the doctor's clinical interface, where the doctor reads and answers them. openPractice keeps only a routing record, with no clinical content. | MI-01, MI-03, MI-11, MI-12 |
| 35 | For now the physician uses openChart on mobile or workstation. This is a current-phase decision and can be revisited. | MI-01 (no requirement depends on a device), MI-21 |
| 39 | There is no master patient identity across HealthLinc, openPractice and openChart. HealthLinc links to each backend through that backend's own link contract. | MI-03, MI-17, MI-18; MT-12 |
| 41 | A payment hold is applied at the gateway (openPractice). It blocks only non-urgent clinical messaging and new non-urgent scheduling, never urgent escalations. | MI-19, MI-25 |
| 43 | openChart owns the queue and the response clock for routed clinical questions. openPractice gets an acknowledgment for each handoff, and alerts the office manager on a missing acknowledgment or on clock expiry. | MI-04, MI-05, MI-06, MI-09 |
| 44 | HealthLinc's AI proposes category and urgency, and openPractice's rules apply them. Staff can re-route a misfiled item but cannot answer outside their lane. A mixed question is split. Urgency is never downgraded. **Amended by ruling 51** (category and urgency may also come from medXfactory's medical AI). | MI-10, MI-12, MI-15, MI-16 |
| 47 | "Draft the openChart companion change too." | This change |
| 50 | Context only. If the access check is unavailable, routine clinical messages still route to openChart. A lapsed membership or a deactivation stops messaging only after notice and a grace period, and a clinician may keep access open for continuity. | openPractice. openChart's part is the clinical-need marker, MI-25. |
| 51 | HealthLinc's in-app AI is a coach, not an MD: general health information with a not-medical-advice statement. Clinical AI doctors live in MedxSoft/medXfactory. HealthLinc is a gateway to the patient's doctor: the patient can connect to their human doctor (through openPractice to openChart) or to medXfactory's medical AI. **Amends ruling 44:** category and urgency may be proposed by HealthLinc's coach or by medXfactory's medical AI, with the same conservative defaults, and openPractice never downgrades. | MI-01, MI-02, MI-03, MI-12, MI-13, MI-14; MT-11 (resolved) |
| 52 | Context only. Non-urgent medical-AI consults sit behind the practice's access check, and a payment hold may withhold them with the same safeguards. Urgent is never withheld. | openPractice and medXfactory. openChart is unaffected (MI-19). |
| 53 | The medical AI's exchanges with a patient are recorded in the chart through medXfactory's own governed path (MedxEHR and openChart). They never pass through openPractice, which holds no clinical content. | MI-12, MI-14, MI-24 |
| 54 | Context only. HealthLinc's coach gives general information only. Anything individualized goes to medXfactory's medical AI or to the doctor. | MI-12 (how coach content is labelled) |
| 56, 57, 58 | Accepted. Cited here by number only. | medXfactory change `define-patient-medical-ai-connection`; not this change |
| 59 | The medical director sets the configuration of medXfactory's AI in one of three modes: advice only, full practice or limited practice. The medXfactory change owns the mode framework and its gates. | MI-26; Decision 13; MT-14 |
| 64 | A separate author is drafting openChart-spec change `define-ai-authored-clinical-records` and MedxEHR-spec change `define-medical-ai-record-overlay`. `define-ai-authored-clinical-records` replaces this change's former item for a "required later practice-mode change". It references this change's clinical-communication record (MI-12) rather than defining a second one. This change states nothing else about either change's content. | MI-12, MI-26; Decision 13; "Related changes being drafted"; MT-14 |

## Goals / Non-Goals

**Goals:**

- Implement openChart's half of `openpractice-clinical-handoff/1.0` against openPractice's canonical schema, verified by digest.
- Make sure every routed clinical item has a named owner, an acknowledgment, a clock and an escalation, so that an urgent item is never blocked, dropped or left unowned.
- Keep clinical content out of openPractice: obtain conversations by reference from the system that holds them, and reply through HealthLinc.
- Give openChart one citable definition of a clinical communication record (MI-12). Keep AI-authored content always distinguishable from clinician-authored content, and never let a communication become a clinical fact of record.
- Keep every ratified `expanded-patient-intake` requirement intact, and keep openChart free of billing and financial status.

**Non-Goals:**

- Encounters, diagnoses, procedures or billable facts. CF-06 is unchanged.
- AI drafting of clinical replies, or any agent action in the inbox.
- AI-authored orders, prescriptions or diagnoses, and the limited-practice and full-practice modes of ruling 59. They wait for openChart-spec change `define-ai-authored-clinical-records`, which is being drafted (ruling 64; Decision 13). Until it is ratified, AI-authored content in the chart is communication only (MI-26).
- An administrative work queue in openChart.
- Defining HealthLinc's or medXfactory's internals. Their sides are stated at contract level only.
- openChart's own link contract with HealthLinc (ruling 39), and openChart's receiving side of medXfactory's governed chart path (ruling 53). Each needs its own change (Open Questions 3 and 4).
- Changing any ratified text, or adopting the constitution inside this change.

## Decisions

### 1. Contract reuse

openChart uses only the messages in the pinned schema, and defines no message of its own toward openPractice (MI-01).

| Message | Direction | openChart's use |
|---|---|---|
| `handoff.offer` | openPractice → openChart | Creates one inbox item per `handoff_id` (MI-04) |
| `handoff.ack` | openChart → openPractice | `accepted` once the item exists durably with a named owner and a running clock; `rejected` with a schema code (MI-04, MI-18) |
| `handoff.urgency_raised` | openPractice → openChart | Raises urgency and moves deadlines only earlier (MI-10) |
| `handoff.status` | openChart → openPractice | `responded`, `clock_expired`, `returned_not_clinical`, `content_unavailable`, `closed` (MI-06) |
| `clinical_need.marker` | openChart → openPractice | A clinician's attributed, coded clinical-need marker (MI-25) |
| `handoff.clinician_urgency_raised` | openChart → openPractice | A clinician's raise to `priority` or `urgent`, with openChart's new `respond_by` (MI-10) |
| `message.ack` | both | openChart acknowledges raises. openPractice acknowledges statuses and markers, with no `handoff_id` for a marker that names no handoff. |

The pinned schema carries `conversation_source`, `conversation_ref`, `clinical_need.marker` and the reject reason `origin_not_verified`. openPractice uses `origin_not_verified` to reject a marker whose urgent origin it cannot verify (openPractice ER-18). openChart never sends that reason.

The pin at `165aff0` also carries:
- the offer field `identity_state` (`linked`, `link_in_review` or `unlinked`). The schema allows `link_in_review` and `unlinked` only for `priority` and `urgent` offers;
- for an `unlinked` offer, `unlinked_identity`, with exactly `legal_name`, `birth_date` and `administrative_sex` from the `openpractice-ehr-patient-link/1.0` snapshot, and no `link_id` or `ehr_patient`;
- `handoff.clinician_urgency_raised`;
- the `handoff.urgency_raised` sources `coach_triage` and `medical_ai_triage`, which replace `healthlinc_triage`.

`link_id` is optional on `handoff.ack`, `handoff.urgency_raised`, `handoff.status` and `handoff.clinician_urgency_raised`. `message.ack` must name a `handoff_id`, a `link_id` or both. openChart's messages about an `unlinked` handoff carry the `handoff_id` and no `link_id`; those about a handoff with a link carry both (MI-06).

### 2. The pinned schema

MI-02 pins `openspec/changes/define-patient-gateway-and-escalation/contracts/openpractice-clinical-handoff-1.0.schema.json` in `opensoft/openPractice-spec`. The pin is at revision `165aff0`, SHA-256 `047f0028dff4867a0e6bf0f6fd95ee2742bf4f2f43aa3044d7259da1dd398771`. The digest matches the line for that file in the change's `contracts/SHA256SUMS`. The pin is updated, in a governed revision of this change, whenever that schema changes.

### 3. Where the conversation comes from

The handoff is reference-only. openChart fetches the conversation by `conversation_ref` from the system that `conversation_source` names, never from openPractice (MI-03, ruling 51):

| `conversation_source` | Held by | Reference | Retrieval |
|---|---|---|---|
| `healthlinc` | HealthLinc, for a coach conversation | `conversation_ref`, namespace `healthlinc` | Required to enable the inbox |
| `medxfactory` | medXfactory, for a medical-AI conversation | `conversation_ref`, namespace `medxfactory` | Required where the practice uses medXfactory's medical AI (MD-12) |

The schema enforces that the namespace matches the source. `healthlinc_message_ref` is HealthLinc's reference for the patient's request. openChart keeps it in the record and uses it for split requests (MI-16).

The reply always goes to HealthLinc against `reply_path_ref`, whichever system holds the conversation, as openPractice ER-05 also states (design call MD-16). A medical-AI exchange reaches the chart only through medXfactory's own governed path (ruling 53). The inbox keeps only its reference, author type, source and retrieval provenance, and never files a copy of it (MI-12, MI-24, design call MD-17).

### 4. Acceptance, clock and deadlines

`handoff.ack` `accepted` is system acceptance: the item exists durably, it has a named owner, and its clock is running (design call MD-1). It does not mean a clinician has read the item. Clinician acknowledgment is an explicit act inside openChart, and escalation runs on it (MI-09).

openChart owns the clock (ruling 43). Deadlines come from an openChart response policy that the medical director approves. Until one is approved, the offer's own `ack_by` and `respond_by` apply. After approval, the earlier of the policy's deadline and the offer's applies. Nothing ever extends a deadline (design call MD-2). The openPractice change's default windows (its design call DC-3) are proposed defaults in an unratified change, not facts. This change adopts no number of its own.

openPractice treats `clock_expired`, or silence past `respond_by`, as `clinical_response_overdue`. It then alerts the office manager and sends a tracked alert to the on-call clinician. For an urgent item it also runs the fallback with emergency guidance (openPractice ER-07, ER-09). openChart therefore behaves as follows (MI-05, MI-06, design call MD-15):
- its effective deadline never falls after `respond_by`;
- it sends `clock_expired` the moment that deadline passes, and `responded` as soon as HealthLinc accepts the reply, each in the same transaction as its cause.

### 5. Ownership, cover and escalation

- Every item has exactly one named owner, a clinician or nurse, in the physician or nurse lane (MI-07).
- Until a lane policy is approved, every item enters the physician lane (design call MD-3).
- openChart keeps its own cover roster, with the medical director as the last fallback. The inbox cannot be enabled with a gap (MI-08, design call MD-4).
- An unacknowledged urgent item escalates to the on-call clinician, then to the medical director, and keeps re-alerting. It never drops, parks or closes (MI-09).
- An expired item stays queued, open and owned until a clinician replies or records a closing outcome. Any clinician authorized for the inbox can find it by its routing id (`handoff_id`), including the on-call clinician named in openPractice's tracked alert (MI-09; MT-7).
- No agent owns, acknowledges, answers, re-routes or closes an item (design call MD-10).

### 6. Urgency

openChart never lowers urgency, by any path. A raise moves deadlines only earlier, and a raise that arrives before its offer is applied when the offer arrives (MI-10). A clinician may raise an item to `priority` or `urgent` inside openChart. openChart reports every such raise as `handoff.clinician_urgency_raised`, with its new `respond_by` and an opaque `raised_by`, over the durable delivery of PL-14 (design call MD-8). The openPractice change then applies three rules (its ER-03, DC-30 and DC-42):
- it shadows the new deadline, never later than its current one;
- a raise to `urgent` gets its urgent path, with emergency guidance if the deadline is missed;
- a raise to `priority` gets a tracked on-call alert, with no guidance for the patient. A raise to `urgent` on an item already answered or closed reopens it inside openChart (design call MD-9).

### 7. Reply, record and authorship

- The reply goes to the patient through HealthLinc. `responded` is reported as soon as HealthLinc accepts it (MI-11, design call MD-15).
- **MI-12 is the single, citable definition of a clinical communication record in openChart.** It gives every piece of content one author type: `patient` (or `representative`), `ai`, `clinician`, `staff`, `system`, or the fail-safe `unknown`. An `ai` type names its source system: HealthLinc's coach or medXfactory's medical AI. MI-12 also states the provenance the record holds, and the rule that a clinical communication is never a diagnosis or a clinical fact of record. MI-13 and MI-14 cite it. `define-ai-authored-clinical-records` references it rather than defining a second record (ruling 64). Nothing is silently overwritten, and a correction is a new version. The storage shape is decided in planning.
- AI-authored and `unknown` content is never recorded, shown or delivered as clinician-authored (MI-13).
- Patient-reported text and AI text never become a diagnosis, a clinical fact or a billable fact (MI-14, design call MD-11).
- Replies honor confidential-communication instructions (PL-16). An unfiled item's reply stays inside the HealthLinc conversation. A withheld reply keeps the item open (MI-22, design call MD-13).
- If HealthLinc reports through `reply.delivery_failed` that an accepted urgent reply was not delivered, `responded` is not final. The item reopens, stays owned and escalates, and the owner is pointed to a permitted channel (MI-11, design call MD-21). openPractice is not told under 1.0 (MT-15).

### 8. Re-routing and splitting

- **An administrative item** is returned with `returned_not_clinical` and is never answered. openChart keeps no administrative queue (MI-15).
- **A mixed item** has its clinical part answered in openChart. openChart asks HealthLinc to split the item and resubmit the administrative part to openPractice (MI-16, design call MD-7). The schema has no status for a partial return (MT-6).

### 9. Identity decision

A handoff resolves the patient only through the links that exist (MI-17, ruling 39):
- the `openpractice` row for the `link_id` (PL-02), on an offer marked `linked`, together with the `ehr_patient` triple under openChart's issuer (PL-03);
- where one exists, HealthLinc's openChart reference for the account.

The offer's `identity_state` is an input, never a resolution. Where it and openChart's own link state differ, the more uncertain governs. There is no demographic matching. `unlinked_identity` (`legal_name`, `birth_date`, `administrative_sex`) is shown as unverified and never used to match or file, and no Medx or medXfactory reference is used (design calls MD-5, MD-19).

| Situation | `routine` | `priority` or `urgent` |
|---|---|---|
| `linked`; `active` row; triple matches; HealthLinc, if it reports one, agrees | Accept and file | Accept and file |
| `link_in_review` (identity review or demographic hold) | Refused by the schema: `schema_invalid` | Accept unfiled; show the uncertainty; open identity review; escalate under MI-09 |
| `linked`, but openChart holds the row in `identity_review` | Reject `link_in_review` | Accept unfiled; show the uncertainty; open identity review; escalate under MI-09 |
| `unlinked`, with `unlinked_identity` | Refused by the schema: `schema_invalid` | Accept unfiled; show the three fields as unverified; open identity review; escalate under MI-09 |
| `linked` but `link_id` unknown to openChart | Reject `link_unknown` | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| `linked` but the row is `revoked` or `superseded` | Reject `link_revoked` (the schema has no superseded code) | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| `linked` but `ehr_patient` does not match the row | Reject `ehr_patient_mismatch` | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| After acceptance: HealthLinc names a different patient, or the link enters review or is revoked | Stays accepted; becomes unfiled; identity review | Same |

The openPractice change's ER-06 offers only `urgent` and `priority` items on a link in review or with no link. At the same time, openPractice runs its fallback for an urgent item, or sends a tracked on-call alert with no guidance for a priority item. A `routine` row marked `linked` in this table covers only a mismatch between openPractice's and openChart's views. An unfiled item is filed only when a link resolves the patient. No human files it by judgment until the owner rules (design call MD-6, Open Question 7).

### 10. Boundaries

- openChart receives no billing, hold or financial status, and never gates an item on such status (MI-19).
- openChart keeps no administrative queue (MI-15).
- With no gateway configured, the inbox is inert. Enabling it needs four things: an openPractice integration identity; HealthLinc retrieval, plus medXfactory retrieval where the practice uses its medical AI; HealthLinc reply delivery and split requests; and full cover. Disabling it withdraws the handoff authorization (MI-20, design call MD-12).

### 11. Clinical-need markers

Ruling 50 lets a clinician keep a patient's clinical messaging and medical-AI consults open for continuity of care. openPractice ER-18 also lets a clinician mark an appointment as clinically needed, so that a payment hold never blocks it. Both are clinical decisions that openPractice must apply, and both travel as `clinical_need.marker` (MI-25):
- kinds `messaging_continuity` and `appointment_needed`;
- a `need_id` that openChart mints and reuses for the withdrawal;
- action `mark` or `withdraw`;
- `marked_by`, an opaque clinician reference, and `marked_at`;
- for `mark` only, `valid_until` and `origin`;
- `related_handoff_id` when the origin is `urgent_escalation`;
- no reason or note.

openChart never learns whether a hold or lapse exists (MI-19). The marker rules beyond the schema are design call MD-18.

### 12. Standalone operation

openChart must operate without MedxFactory, MedxEHR or openPractice, as the ratified text states. It also operates without HealthLinc or medXfactory. Every inbox component is optional (MI-20, PL-15). The standalone golden-intake tests remain the regression gate.

### 13. AI practice modes (rulings 59 and 64)

The medical director sets medXfactory's AI to advice only, limited practice or full practice. medXfactory's change `define-patient-medical-ai-connection` owns the mode framework and its gates (rulings 56 to 58).

This change does not cover AI-authored orders, prescriptions or diagnoses. openChart-spec change `define-ai-authored-clinical-records` is being drafted for them (ruling 64), alongside MedxEHR-spec change `define-medical-ai-record-overlay` on the MedxEHR side. Ruling 59 stands, so until `define-ai-authored-clinical-records` is ratified, MI-26 applies and fails closed:
- all AI-authored content that reaches the chart, by any path, is communication only, recorded under MI-12;
- content that presents itself as an order, a prescription or a diagnosis is held as AI-authored communication, marked as not accepted as a clinical act (design call MD-20);
- the limited-practice and full-practice modes are not buildable in openChart.

The future openChart change that defines the receiving side of medXfactory's governed chart path (Open Question 4) is bound by MI-26 as well.

## The openPractice change's companion items

The openPractice change's design, at `165aff0`, lists eleven items that this change must contain.

| Item in the openPractice change | Where this change meets it |
|---|---|
| Receive offers validated against the schema at digest `047f0028…` | MI-01, MI-02 |
| Answer each offer with `handoff.ack`. Accept an urgent or priority offer in state `link_in_review` or `unlinked` as an unfiled item with the uncertainty shown; never refuse it for that state; never file or link on it automatically. Refuse a routine offer on a link in review with `link_in_review`, and an offer on a revoked or unknown link | MI-04, MI-17, MI-18. Met, except that MI-18 accepts an urgent or priority offer marked `linked` that openChart finds revoked, unknown or mismatched, and does not refuse it (MT-1 residual). |
| Send `handoff.clinician_urgency_raised`, with the new `respond_by` and the clinician's reference, whenever a clinician raises urgency, and never lower urgency | MI-10, MD-8 |
| Own the queue and the clock; report `responded`, `clock_expired`, `returned_not_clinical`, `content_unavailable` and `closed`; send `clock_expired` when the clock runs out and `responded` as soon as a clinician replies | MI-05, MI-06, MD-15 |
| Keep an expired item queued until a clinician responds, and show it by routing id to the on-call clinician who receives openPractice's alert | MI-09 (MT-7 for an on-call clinician without openChart access) |
| Fetch the conversation by `conversation_ref` from whichever system holds it, never through openPractice | MI-03, MI-24 |
| A reply path to HealthLinc that bypasses openPractice | MI-11, MD-16 |
| Apply `handoff.urgency_raised`, and never lower urgency | MI-10 |
| Let a clinician record, attribute and withdraw a clinical-need marker, and send it as `clinical_need.marker` with no reason or note | MI-25, MD-18 |
| Honor confidential-communication instructions (ruling 27) | MI-22 |
| Say how a clinician reads a routed message for a patient with no EB-01 link (its Open Question 5) | Answered by ER-06 and MI-18. An `unlinked` urgent or priority item is offered with `unlinked_identity`. openChart accepts it unfiled, shows the three fields as unverified, and opens an identity review (MT-2, resolved). A routine item stays an openPractice exception. |

## Design calls for owner review

Each item below goes beyond the rulings, and each is proposed, not ruled. Where a ruling is silent on something consequential, the binding text fails closed and cites the design call.

| # | Design call | Where |
|---|---|---|
| MD-1 | `handoff.ack` `accepted` means system acceptance: the item exists durably, with a named owner and a running clock. This follows the schema's own description of `accepted`. Clinician acknowledgment is internal. The alternative, waiting for a clinician before acknowledging, is left to the owner (MT-5). | MI-04 |
| MD-2 | Deadlines: the offer's `ack_by` and `respond_by` apply until openChart's policy is approved, then the earlier of the two. No deadline is ever extended. Until a policy exists, each escalation interval equals the item's acknowledgment window, and an item that arrives late escalates at once. | MI-05, MI-09, MI-10 |
| MD-3 | Until the medical director approves a lane policy, every item enters the physician lane. What nurses may answer comes only from that policy; scope of practice is for the medical director and counsel. | MI-07 |
| MD-4 | openChart keeps its own cover roster, with the medical director as the last fallback. The inbox cannot be enabled with an uncovered hour, and a change that would open a gap is refused. | MI-08 |
| MD-5 | Identity is handled by urgency, and by the more uncertain of the offer's `identity_state` and openChart's own link state. An `urgent` or `priority` offer whose patient cannot be resolved is accepted unfiled, opens an identity review and escalates under MI-09. It is never rejected for identity. A `routine` offer in state `link_in_review` or `unlinked` fails the pinned schema (`schema_invalid`). A `routine` offer marked `linked` whose link openChart finds uncertain is rejected with `link_unknown`, `link_revoked`, `link_in_review` or `ehr_patient_mismatch`. On `handoff.ack`, openChart uses only `schema_invalid`, `unsupported_major_version`, `unauthorized`, `link_unknown`, `link_revoked`, `link_in_review` and `ehr_patient_mismatch`. A superseded link maps to `link_revoked`, because the schema has no separate code. openChart never sends `origin_not_verified`, which is openPractice's reason for rejecting a marker. | MI-18 |
| MD-6 | An unfiled item is filed only when a link resolves the patient. No human files it by judgment until the owner rules. `unlinked_identity` (`legal_name`, `birth_date`, `administrative_sex`) is shown as unverified and never used to match or file. A HealthLinc reference alone does not file an `unlinked` item until openChart's HealthLinc link contract exists (Open Question 3). | MI-17, MI-18 |
| MD-7 | A mixed item's administrative part goes back through a split-and-resubmit request to HealthLinc, not through a new handoff status. | MI-16 |
| MD-8 | A clinician may raise urgency inside openChart, to `priority` or to `urgent`. openChart reports **both** kinds of raise as `handoff.clinician_urgency_raised`, with its new `respond_by` and an opaque `raised_by`, over PL-14's durable delivery. It reports both because the schema allows both values. openChart promises nothing beyond what the openPractice change defines (its ER-03, DC-30 and DC-42): openPractice's shadow deadline never moves later, a raise to `urgent` gets its urgent path with patient guidance on a missed deadline, and a raise to `priority` gets only a tracked on-call alert, with no patient guidance. | MI-10 |
| MD-9 | A raise to `urgent` on an item that is already `responded` or closed reopens it inside openChart. openChart sends no status after `closed`. When the raise is a clinician's, openChart still sends `handoff.clinician_urgency_raised`, because that message is not a status; whether openPractice accepts it after `closed` is Open Question 15. When the raise came from openPractice, openPractice already knows. | MI-10 |
| MD-10 | No agent owns, acknowledges, answers, re-routes or closes an item, and no AI drafts a clinical reply. Content of unknown authorship carries the author type `unknown` (MI-12). | MI-07, MI-12, MI-13 |
| MD-11 | Inbox records are not encounters, diagnoses or procedures. They are never billable, never become intake statements, and AI text never becomes a clinical fact. | MI-12, MI-14 |
| MD-12 | With no gateway the inbox is inert. Enabling it needs integration, HealthLinc retrieval, reply and split, and cover, plus medXfactory retrieval where the practice uses medXfactory's medical AI. An offer that names an unconfigured source is still accepted, and follows MI-03's failure path. Disabling the inbox withdraws the handoff authorization. Apart from ruling 53's path, no patient message reaches openChart without passing through openPractice. | MI-03, MI-20 |
| MD-13 | An unfiled item's reply stays inside the HealthLinc conversation, with every other channel restricted. A reply that PL-16 withholds keeps the item open and owned. | MI-22 |
| MD-14 | One item per `handoff_id`. A conflicting offer for the same `handoff_id` leaves the item unchanged and records an integration exception. | MI-04 |
| MD-15 | Status timing. `clock_expired` is sent the moment openChart's effective deadline passes, which is never after the offer's `respond_by`. `responded` is sent as soon as HealthLinc accepts the reply. Each is written in the same transaction as its cause, so openPractice's `clinical_response_overdue` fallback runs on time. `content_unavailable` is sent at the first failed retrieval for an urgent item, and after the retry policy for any other item. `returned_not_clinical` is the last status for its item. `closed` follows `responded`, or stands alone for an item closed without a reply. An expired item stays queued and is visible by routing id. | MI-03, MI-05, MI-06, MI-09 |
| MD-16 | A reply to a conversation that medXfactory holds still goes to HealthLinc against `reply_path_ref`. This now matches openPractice ER-05 at `165aff0`. It stays a design call only because that change is unratified. | MI-11 |
| MD-17 | For a conversation that medXfactory holds, the inbox item keeps only the reference, the author type and source, and the retrieval provenance. It files no copy, because ruling 53 records the exchange through medXfactory's own path. Whether openChart keeps an audit copy, outside the chart, of what the clinician saw is Open Question 10. | MI-12, MI-24 |
| MD-18 | Clinical-need markers, beyond what the schema fixes, follow these rules. **(a)** openChart mints one `need_id` per marker and reuses it for the withdrawal. **(b)** The clinician must set `valid_until`; there is no default. **(c)** `urgent_escalation` is used only for a marker recorded from an item whose urgency is `urgent` as openPractice offered or raised it. A clinician's raise to `urgent` also counts once openPractice has answered it with `message.ack` `received`, since openPractice's ER-03 then treats the item as urgent. The marker carries that item's `handoff_id` as `related_handoff_id`. **(d)** After `origin_not_verified`, openChart shows the clinician the coded reason and never resends with a different origin on its own. **(e)** `marked_by` is never derived from the clinician's name or login. **(f)** A marker may be recorded only on an `active` link, so a PL-08 hold blocks it (MT-3). **(g)** Any named clinician may record one, since ruling 50 says "a clinician". | MI-25 |
| MD-19 | A handoff never resolves the patient through a Medx or medXfactory reference, even when medXfactory holds the conversation. | MI-17 |
| MD-20 | An AI-authored order, prescription or diagnosis is held as AI-authored communication, marked by code as not accepted as a clinical act, rather than refused. Holding it keeps a record of what the patient was told and creates nothing clinical. MI-26 applies to every path into the chart, including medXfactory's governed path, until `define-ai-authored-clinical-records` is ratified. | MI-26 |
| MD-21 | When HealthLinc's `reply.delivery_failed` callback reports that an accepted urgent reply was not delivered, `responded` is not final. The item reopens, stays owned and escalates under MI-09, and the owner is pointed to a permitted channel (MI-22). openChart sends openPractice nothing, because 1.0 has no status that withdraws `responded` (MT-15). | MI-11 |

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which "MUST operate without MedxFactory, MedxEHR or openPractice" | MI-20 restates it with all three systems, and adds HealthLinc and medXfactory. The inbox is optional, and inert without a gateway. The golden-intake tests remain the gate. |
| External identifiers must not replace the openChart identifier or merge patients | MI-17 and MI-18 resolve only through existing links. Nothing is matched, merged or re-pointed; an unresolved item stays unfiled. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Messages are not intake submissions and never become statements (MI-14). |
| Medication, supplement and other statements preserve reported detail | Untouched. |
| Amendments preserve accepted history | MI-12: communications are never silently overwritten, and corrections are new versions. |
| APIs and hooks are authorized and versioned | MI-01 uses a role narrower than `System Manager`, authorized for subject, tenant, purpose and role. MI-02 versions the contract by MAJOR version and digest. |
| Intake confers no clinician or autonomous authority | MI-12 makes a clinical communication never a diagnosis or clinical fact of record. MI-14 keeps patient text patient-reported. MI-13 bars AI drafting. MI-26 keeps AI-authored content as communication, never an order, prescription or diagnosis. MT-10 records the reading of "autonomous action" that this change relies on. |

**One possible conflict with ratified openChart text is recorded, as MT-10.** No other conflict with ratified text was found.

## Consistency with `define-openpractice-boundary`

| Requirement | Relation |
|---|---|
| PL-01, PL-06 | Kept. No merge, and identity review follows PL-06 (MI-17, MI-18). |
| PL-02, PL-03 | Used to resolve the patient (MI-17). |
| PL-04 | Its pattern is reused for a third pin (MI-02). PL-04's own two pins are unchanged. |
| PL-05 | Its role pattern is reused (MI-01). openChart never creates a link from its own matching (MI-17). |
| PL-08 | **Tension MT-3.** A PL-08 hold also blocks clinical-need markers (MD-18). |
| PL-12 | Its versioning pattern is reused (MI-02). |
| PL-13 | Extended to the handoff contract (MI-21). |
| PL-14 | Reused for handoff messages and markers (MI-06, MI-25). PL-14 lists the two boundary contracts; this change adds a third user of the store and changes nothing in PL-14. |
| PL-15 | Restated (MI-20). |
| PL-16 | Applied to replies (MI-22). **Tension MT-9.** |
| CF-02, CF-05, CF-06 | Kept (MI-14, MI-19). **Tension MT-8** concerns that change's design context. |

## Conflicts and tensions

Fifteen are recorded. MT-2, MT-11 and MT-13 are resolved by the openPractice change's text, which was checked at `165aff0`. MT-1 is resolved too, its last residual by the companion list at `6e411dc`. Eleven tensions (MT-3 to MT-10, MT-12, MT-14 and MT-15) need the owner's disposition before ratification. None is resolved by this draft on its own authority.

| # | Tension | Status |
|---|---|---|
| MT-1 | Earlier, the openPractice change's companion list said that openChart must "refuse an offer on a revoked, unknown or in-review link", and its ER-06 made an active, unreviewed link a precondition. MI-18 accepts urgent and priority offers whose identity is uncertain. | **Resolved for `link_in_review` and `unlinked` offers** by ER-06 at `165aff0`, and by the companion list there, which now requires accepting those offers unfiled. **The residual is resolved by the companion list at `6e411dc`** (text only; the schema and digest are unchanged from `165aff0`). openChart refuses only a routine offer on a revoked or unknown link, and accepts unfiled an urgent or priority offer marked `linked` that it finds revoked, unknown or mismatched, as MI-18 says. |
| MT-2 | Earlier, an urgent item on a link in review, or for a patient with no link, was never offered. The on-call clinician received only a routing id, an urgency and a coded cause, and could not read the message in openChart. | **Resolved by ER-06 at `165aff0`.** Unlinked `urgent` and `priority` items are offered with `unlinked_identity` (`legal_name`, `birth_date` and `administrative_sex`). MI-18 accepts them unfiled, and shows those fields to the clinician as unverified and never matched (MI-17). This answers openPractice Open Question 5. Residual, not a safety tension: a `routine` item on a link in review, or with no link, is still an office-manager exception in openPractice. |
| MT-3 | PL-08 puts a link in `identity_review` during every date-of-birth hold. openPractice EB-05 and EB-08 (in `define-mvp-practice-foundation`) report such a hold in the same state as a linkage conflict. The openPractice change's ER-06 therefore sends both as `identity_state` `link_in_review`, as its tension T-11 records. `routine` items during a hold are still not offered, and MD-18 blocks clinical-need markers during a hold. | **Follow-up**, and the safety part is addressed by ER-06. The openPractice change's T-11 proposes a governed amendment to EB-05, EB-08 and PL-08 that distinguishes a demographic hold from a linkage conflict. After it, `identity_state` could gain a separate value in a MINOR version. This change does not edit PL-08 in `define-openpractice-boundary`. The binding text fails closed: a hold counts as identity review (MI-18, MI-25). |
| MT-4 | openPractice ER-08 takes the windows from an openPractice routing-clock policy. Ruling 43 and MI-05 put the clock, and its windows, in openChart under the medical director's approval. Two policies can disagree. | MD-2 takes the earlier deadline, so openChart's policy can only tighten. Owner to confirm whether one policy record should govern both. |
| MT-5 | `handoff.ack` means system acceptance (MD-1). openPractice ER-09 now fires on `clock_expired` and on silence past `respond_by`, and MD-15 sends `clock_expired` on time. Before `respond_by`, though, openPractice still gets no signal that no clinician has acknowledged an urgent item. | Still open. The options are a status code in a MINOR version, or deferring `handoff.ack` until a clinician acknowledges. openChart's internal escalation (MI-09) is the inner safety net meanwhile. |
| MT-6 | The 1.0 schema has no status for returning only the administrative part of a mixed item. openPractice ER-12 describes splitting only from openPractice's side. | MD-7 routes the split through HealthLinc instead. For a conversation that medXfactory holds, who splits is open (Open Question 14). |
| MT-7 | openPractice ER-13 keeps an on-call roster for its fallback. MI-08 keeps openChart's own cover roster. They can disagree. openPractice's tracked alert goes to openPractice's on-call clinician. MI-09 shows the item by routing id only to a clinician authorized for openChart's inbox. | Owner item, related to openPractice Open Question 6. openChart's roster governs its queue. Every clinician on openPractice's on-call roster also needs inbox access in openChart; planning confirms this. |
| MT-8 | `define-openpractice-boundary`'s design says that "Every statement in openChart is patient-reported" and that no clinician-authored records exist. This change adds clinician-authored replies. | Not a conflict with requirement text. CF-06 still holds, because a reply is not an encounter, a diagnosis or a procedure (MI-12, MD-11). That design statement becomes stale once this change lands. |
| MT-9 | PL-16 withholds any communication that cannot satisfy the patient's instructions. For an urgent reply, withholding delays care. | MI-22 keeps the item open and owned, and tells the owner to use a permitted channel. PL-16 is not weakened. Residual risk, recorded. |
| MT-10 | The ratified requirement "Intake does not confer clinician or autonomous authority" bars any "API response or extension event" from creating an "autonomous action". openChart's `AGENTS.md` says "Do not enable autonomous clinical actions by default." In this change, an API call (the offer) automatically creates an item, assigns an owner, sends alerts and reports status. | Reading proposed: these steps deliver an item to humans and decide nothing about care, so they are not clinical or autonomous actions. The ratified text does not define "autonomous action", so the owner confirms this reading at ratification. |
| MT-11 | The schema first pinned (`2353d99`) could name only HealthLinc as a conversation's holder, but ruling 51 adds medXfactory-held conversations. | **Resolved by the re-pin.** Since `097278c`, and still at `165aff0`, the offer requires `conversation_source` (`healthlinc` or `medxfactory`) and a matching `conversation_ref`. openPractice ER-05 states the same. medXfactory retrieval is live (MI-03). |
| MT-12 | openChart's test fixture `tests/fixtures/medx/binding-03-openchart.yaml` binds HealthLinc, OpenEMR and openChart references to one `medx_patient_id`. Ruling 39 says there is no master identity across HealthLinc, openPractice and openChart. Rulings 51 and 53 bring medXfactory into the patient's path and into the chart. | MI-17 never resolves a handoff through a Medx or medXfactory reference (MD-19). Owner to confirm that the Medx binding is not a master identity for the gateway or chart paths. The medXfactory companion must say how its governed chart path identifies an openChart patient. |
| MT-13 | The schema first pinned had no message for a clinician's continuity decision (ruling 50) or clinically-needed marker. | **Resolved by the re-pin.** Since `097278c`, and still at `165aff0`, the schema defines `clinical_need.marker` (openPractice ER-18), and MI-25 sends it. |
| MT-14 | Ruling 59 lets the medical director set medXfactory's AI to limited or full practice, under gates that medXfactory's change owns. openChart cannot record an AI-authored clinical act until `define-ai-authored-clinical-records` is ratified. A practice could therefore configure a mode in medXfactory whose acts openChart holds only as communication. | MI-26 fails closed. Owner item: medXfactory's gates should refuse limited and full practice for an openChart deployment until `define-ai-authored-clinical-records` is ratified. |
| MT-15 | openPractice closes its routing record when `responded` arrives (openPractice ER-07). If HealthLinc later reports through `reply.delivery_failed` that an accepted urgent reply was not delivered, openPractice is not told, because 1.0 has no status that withdraws `responded`. Its office-manager alert and patient guidance therefore do not run for that failure. | Owner item. MD-21 handles the failure inside openChart: the item reopens and escalates, and the owner reaches the patient through a permitted channel. Options for telling openPractice: a status in a MINOR version of the handoff contract, HealthLinc telling openPractice directly, or reusing `handoff.clinician_urgency_raised` with a new deadline, which would stretch that message's meaning. None is adopted here. |

## Required companion changes (being drafted elsewhere)

None is drafted in this change. Each is stated at contract level only. Nothing here describes HealthLinc's or medXfactory's internals.

**HealthLinc.** The openPractice change names this companion as `opensoft/HealthLinc` change `define-practice-gateway-integration`.

- **H-1. Conversation retrieval by reference.** Given a `conversation_ref` with namespace `healthlinc`, HealthLinc returns the escalated exchange over openChart's own authorized integration, never through openPractice. Each turn carries its author type (MI-12) and time, and coach turns are marked as HealthLinc's coach (rulings 51 and 54). The response also says whether a patient or a representative wrote, and, where HealthLinc keeps one, the openChart patient reference for the account. Errors are coded and carry no PHI.
- **H-2. Reply delivery.** HealthLinc accepts a clinician reply against `reply_path_ref`, whichever system holds the conversation. The reply carries the sender's identity, the author type and the applicable confidential-communication restriction codes (PL-16). HealthLinc can be asked to deliver inside the conversation only (MD-13). Delivery is idempotent by message identifier, and acceptance or refusal is coded. Push text carries no PHI. Clinician-authored and AI-authored content are shown distinctly. For an urgent reply whose delivery fails after HealthLinc accepted it, HealthLinc calls back `reply.delivery_failed` (MI-11).
- **H-3. Split and resubmit.** On openChart's request, which names the `healthlinc_message_ref`, HealthLinc splits a mixed item, resubmits only its administrative part to openPractice as a new inquiry, and acknowledges the request (MD-7).
- **H-4. Emergency guidance stays in the app.** HealthLinc shows its own emergency guidance for urgent submissions, whether or not openChart or openPractice is available. openChart sends no advice codes.
- **H-5. No clinical messaging without a route.** HealthLinc offers no clinical messaging to a practice with no configured gateway (MI-20).

**medXfactory.** The openPractice change assigns the medical-AI side to `MedxSoft/medXfactory` change `define-care-organization-hermes-openpractice-operations`. medXfactory's change `define-patient-medical-ai-connection` owns the practice-mode framework (ruling 59). Which medXfactory change carries M-1 and M-2 is for medXfactory to state.

- **M-1. Conversation retrieval by reference.** Given a `conversation_ref` with namespace `medxfactory`, medXfactory returns the exchange over openChart's own authorized integration, never through openPractice. Each turn carries its author type, with medXfactory's medical AI named as the source. The provenance is enough for openChart to record which exchange the clinician saw. Errors are coded and carry no PHI.
- **M-2. Its governed chart path.** This is the path by which medical-AI exchanges are recorded in the chart (MedxEHR and openChart), never through openPractice (ruling 53). It includes how that path identifies an openChart patient without a master identity (MT-12). openChart's receiving side needs its own openChart change (Open Question 4).

## Related changes being drafted (ruling 64)

- **`opensoft/openChart-spec` change `define-ai-authored-clinical-records`**, being drafted on branch `change/define-ai-authored-clinical-records`. It takes the place of this change's former "required later practice-mode change". The limited-practice and full-practice modes of ruling 59 are not buildable in openChart until it is ratified. Until then, MI-26 holds every AI-authored order, prescription or diagnosis as communication. It references this change's clinical-communication record (MI-12) rather than defining a second one.
- **MedxEHR-spec change `define-medical-ai-record-overlay`**, being drafted. It is the MedxEHR-side counterpart named in ruling 64.

This change states nothing else about either change's content.

## Risks / Trade-offs

- **[A missed urgent message]** → A named owner from acceptance. Escalation to the on-call clinician and then the medical director, with repeated alerts. No rejection on identity grounds. `content_unavailable` and `clock_expired` sent at once, so openPractice's fallback runs on time. An expired item stays queued and visible by routing id. `priority` items with identity problems are escalated like urgent ones. A clinician's raise reaches openPractice. A failed urgent delivery reopens the item.
- **[Wrong-patient filing]** → Resolution only through links, no demographic matching, unfiled items, and `unlinked_identity` (three snapshot fields) shown as unverified and never matched.
- **[Clinical content leaks into openPractice]** → Reference-only handoff. Markers carry no reason. No administrative text is sent. Splits go through HealthLinc. Medical-AI exchanges travel on medXfactory's path.
- **[AI text mistaken for a clinician's]** → An author type and a named source on every piece of content (MI-12). No AI drafting, and no agent action.
- **[An AI-authored order or prescription acted on]** → MI-26 holds it as communication, marked as not accepted as a clinical act, until `define-ai-authored-clinical-records` is ratified (MT-14).
- **[Double alerts]** → openChart's escalation and openPractice's tracked alerts can both fire for one item. This is accepted for safety.
- **[Two clock policies drift]** → The earlier deadline governs (MT-4).
- **[Unfiled records accumulate]** → They are listed for identity review. Manual filing is Open Question 7.
- **[Confidentiality breach through notifications]** → PL-16 restriction codes go to HealthLinc. An unfiled item's reply stays in the conversation.
- **[Contract drift]** → The digest pin and task 1.3.
- **[No constitution]** → The plan phase is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly. Ratify `define-openpractice-boundary` first or together. Brett Heap stamps `Ratified by` and sets `Status: ratified`.
2. Adopt openChart's constitution through separate governance.
3. Wait for the openPractice change to be ratified and to match the pin at `165aff0` by digest.
4. Wait for the HealthLinc companion change, and for the medXfactory companion before any medXfactory retrieval.
5. Create the single Spec Kit feature from the assembly root. Implement against openPractice and source-system doubles, alongside the standalone regression suite.
6. Enable the inbox only with full cover and the HealthLinc capabilities, plus medXfactory retrieval where the practice uses its medical AI. openPractice enables clinical routing afterwards.
7. Rollback: openPractice disables clinical routing first. openChart then disables the inbox, which withdraws the handoff authorization. Open items stay owned until they close, and no record is deleted.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks the plan phase.
2. **Owner dispositions** of MT-3 to MT-10, MT-12, MT-14 and MT-15, and of MD-1 to MD-21. These block ratification.
3. **openChart's HealthLinc link contract (ruling 39).** Which governed openChart change defines it? This blocks live HealthLinc retrieval.
4. **openChart's receiving side of medXfactory's governed chart path (ruling 53).** This needs a separate openChart change. It blocks nothing in the inbox.
5. **A patient with no EB-01 link** (openPractice Open Question 5). Answered by ER-06 at `165aff0` and by MI-18 (MT-2). A `routine` item stays an office-manager exception.
6. **Clinical messaging in an openChart-only deployment.** The owner decides. Meanwhile there is none (MI-20).
7. **Manual filing of an unfiled item** by a named human. The owner and the medical director decide. Meanwhile, filing happens only through a resolved link.
8. **Lane policy and nurse scope.** The medical director decides, with counsel on scope of practice. Meanwhile, every item enters the physician lane.
9. **Response windows.** The medical director decides. Meanwhile, the offer's deadlines apply.
10. **Retention** of clinical-communication records and returned items, and whether openChart keeps an audit copy, outside the chart, of a medXfactory exchange the clinician saw (MD-17). The owner and counsel decide. Meanwhile, nothing is deleted and no copy is kept.
11. **Billability of clinician replies.** This waits for a clinical-encounter capability (`define-openpractice-boundary` Open Question 2). Meanwhile, nothing is billable.
12. **A representative's scope** (openPractice Open Question 2). Counsel decides. openChart shows the submitter kind as reported.
13. **`closed` without `responded`.** Does it satisfy openPractice ER-07's shadow deadline? The openPractice change confirms.
14. **Splitting a medXfactory-held mixed conversation.** MI-16 sends the split request to HealthLinc. The owner, or the openPractice change, decides who splits a conversation that medXfactory holds.
15. **A clinician's raise after `closed`.** Does openPractice accept `handoff.clinician_urgency_raised` for a routing record it has closed (MD-9)? The openPractice change confirms.
