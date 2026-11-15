## Context

openChart is an original Frappe v15 application, `open_chart`, kept in `opensoft/openChart-code`. Its canonical, ratified capability is [`openspec/specs/expanded-patient-intake/spec.md`](../../specs/expanded-patient-intake/spec.md).

This change touches these facts about what is already built. They were checked at `opensoft/openChart-code` revision `30b9645`.

- **DocTypes.** The built DocTypes are `OC Patient`, `OC Patient External Identifier`, `OC Intake Submission`, and eight statement DocTypes: allergy, condition, document reference, goal, medication, observation, supplement and symptom. None holds a message, a clinician-authored record or a work queue.
- **Roles.** Every built DocType grants permissions to `System Manager` only. No clinician, nurse or medical-director role exists.
- **Events.** `emit_submission_event` uses `frappe.publish_realtime`, which never leaves the site.
- **Medx references.** The ratified intake keeps Medx and HealthLinc references as namespaced external identifiers. A test fixture, `tests/fixtures/medx/binding-03-openchart.yaml`, binds HealthLinc, OpenEMR and openChart references to one `medx_patient_id` ("gate G3"). See tension MT-12.

**The openPractice side** is `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation`, merged by PR #6 and now on `opensoft/openPractice-spec` `main` at `0a82fc2`, still draft and unratified. This change pins it at revision `0a82fc2`. In this document it is called "the openPractice change", and its identifiers are cited as, for example, "openPractice ER-06". Its capability `escalation-routing` (ER-01 to ER-18) owns the contract `openpractice-clinical-handoff/1.0` and its canonical schema. That change's design lists this inbox as a required companion change, with twelve items; they are checked below under "The openPractice change's companion items".

**The conversation-retrieval contract,** `openchart-conversation-retrieval/1.0`, is owned by this change (ruling 69). Its canonical schema is `contracts/openchart-conversation-retrieval-1.0.schema.json` in this change's directory, listed in `contracts/SHA256SUMS`. HealthLinc and medXfactory implement it (Decision 14).

**Clinical roles and grants** come from `define-clinical-acts-foundation` (openChart-spec#5), another author's draft, read here at `c9e3e7a`. Its clinical-authority capability, AU-01 to AU-06, is the single definition of clinical roles, the medical director and grants in openChart, and AU-06 is PROPOSED pending owner decision 92 (Decision 15).

**This branch is stacked on `define-openpractice-boundary`.** That change is a draft, and this change cites its PL-01 to PL-16, CF-02, CF-05 and CF-06. This change can be ratified only with or after it.

Brett Heap's rulings are tabulated below. **Rulings are not ratification.** This change stays `Status: draft` until he stamps `Ratified by` in `proposal.md`.

**Constitution status.** openChart's `.specify/memory/constitution.md`, in the assembly root `opensoft/openChart`, is the unfilled Spec Kit template on `main` (checked at revision `d20de75`). There is nothing ratified to check against. This design therefore checks against openChart's `AGENTS.md` and the ratified `expanded-patient-intake` requirements. The plan phase waits on adopting a constitution.

## Owner rulings

Rows 34 to 64 have the same source: **Brett Heap, 2026-11-14, authoring session.** Rows 65 to 71 are Brett Heap's rulings as relayed to this draft by its parent author on 2026-11-15. The numbering is shared with the openPractice change. Rows marked "context only" are recorded so the binding text can be checked against them; they add no openChart requirement of their own.

| # | Ruling | Governs |
|---|---|---|
| 34 | openPractice is the gateway and router. Clinical questions go to openChart, the doctor's clinical interface, where the doctor reads and answers them. openPractice keeps only a routing record, with no clinical content. | MI-01, MI-03, MI-11, MI-12 |
| 35 | For now the physician uses openChart on mobile or workstation. This is a current-phase decision and can be revisited. | MI-01 (no requirement depends on a device), MI-21 |
| 39 | There is no master patient identity across HealthLinc, openPractice and openChart. HealthLinc links to each backend through that backend's own link contract. | MI-03, MI-17, MI-18; MT-12 |
| 41 | A payment hold is applied at the gateway (openPractice). It blocks only non-urgent clinical messaging and new non-urgent scheduling, never urgent escalations. | MI-19, MI-25 |
| 43 | openChart owns the queue and the response clock for routed clinical questions. openPractice gets an acknowledgment for each handoff, and alerts the office manager on a missing acknowledgment or on clock expiry. | MI-04, MI-05, MI-06, MI-09 |
| 44 | HealthLinc's AI proposes category and urgency, and openPractice's rules apply them. Staff can re-route a misfiled item but cannot answer outside their lane. A mixed question is split. Urgency is never downgraded. **Amended by ruling 51** (category and urgency may also come from medXfactory's medical AI). | MI-10, MI-12, MI-15, MI-16 |
| 45 | Cited by number only. AH-05 exception 1 in openPractice change `define-actors-agents-and-work-inbox` cites it for an agent's read-only answers to the patient. | MI-12 (`openpractice_agent` turns) |
| 47 | "Draft the openChart companion change too." | This change |
| 50 | Context only. If the access check is unavailable, routine clinical messages still route to openChart. A lapsed membership or a deactivation stops messaging only after notice and a grace period, and a clinician may keep access open for continuity. | openPractice. openChart's part is the clinical-need marker, MI-25. |
| 51 | HealthLinc's in-app AI is a coach, not an MD: general health information with a not-medical-advice statement. Clinical AI doctors live in MedxSoft/medXfactory. HealthLinc is a gateway to the patient's doctor: the patient can connect to their human doctor (through openPractice to openChart) or to medXfactory's medical AI. **Amends ruling 44:** category and urgency may be proposed by HealthLinc's coach or by medXfactory's medical AI, with the same conservative defaults, and openPractice never downgrades. | MI-01, MI-02, MI-03, MI-12, MI-13, MI-14; MT-11 (resolved) |
| 52 | Context only. Non-urgent medical-AI consults sit behind the practice's access check, and a payment hold may withhold them with the same safeguards. Urgent is never withheld. | openPractice and medXfactory. openChart is unaffected (MI-19). |
| 53 | The medical AI's exchanges with a patient are recorded in the chart through medXfactory's own governed path (MedxEHR and openChart). They never pass through openPractice, which holds no clinical content. **Refined by ruling 70.** | MI-12, MI-14, MI-24 |
| 54 | Context only. HealthLinc's coach gives general information only. Anything individualized goes to medXfactory's medical AI or to the doctor. | MI-12 (how coach content is labelled) |
| 56, 57, 58 | Accepted. Cited here by number only. Ruling 66 trims ruling 56. | medXfactory change `define-patient-medical-ai-connection`; not this change |
| 59 | The medical director sets the configuration of medXfactory's AI in one of three modes: advice only, full practice or limited practice. The medXfactory change owns the mode framework and its gates. | MI-26; Decision 13; MT-14 |
| 64 | A separate author is drafting openChart-spec change `define-ai-authored-clinical-records` and MedxEHR-spec change `define-medical-ai-record-overlay`. `define-ai-authored-clinical-records` replaces this change's former item for a "required later practice-mode change". It references this change's clinical-communication record (MI-12) rather than defining a second one. This change cites `define-ai-authored-clinical-records` (openChart-spec#4) only by its requirement, design-call and tension IDs. | MI-12 (origin `ai_consult`), MI-20, MI-24, MI-26; Decision 13; MD-20, MD-28; "Related changes being drafted"; MT-14 |
| 65 | The chart keeps its own record of the medical director's authorization and checks every AI write against it. Owned by `define-ai-authored-clinical-records`; cited only. | MI-26; Decision 13 |
| 66 | Context only. An advice-only patient-consult class: answers may reach the patient without prior sign-off. They give information, assessment and next steps, with no diagnosis language and no treatment directives, and carry AI disclosure and red-flag routing. The medical director's sampled review replaces review-before-send for this class only. Trims ruling 56. | medXfactory. openChart: MI-12, MI-13 and MI-26 (such answers are AI content, never shown as clinician-reviewed) |
| 67 | The never-grantable rule stays. Limited and full practice stay specified but off. | MI-26 (the hold lasts until Tier 2 is in force for the act type); Decision 13; MT-14 (resolved) |
| 68 | Context only. Hermes's administrative patient messages are separated from clinical ones in medXfactory's local policy. Administrative messages follow ruling 45's guardrails with no clinical review. Consent and data-sharing conditions still apply. | medXfactory. openChart: nothing beyond MI-12's author types and MD-25's consent handling |
| 69 | openChart owns one neutral conversation-retrieval contract, which HealthLinc and medXfactory implement. | MI-01, MI-02, MI-03, MI-11, MI-16, MI-23; Decision 14; H-1 to H-3, M-1 |
| 70 | The medical AI's records reach openChart through MedxEHR, which relays them with receipts. medXfactory does not write to openChart directly. The write path belongs to `define-ai-authored-clinical-records`; cited only. **Refines ruling 53.** | MI-20, MI-24, MI-26; Decision 3; MD-20 (the inbox defers to that write path); M-2; Open Question 4 |
| 71 | When a patient writes straight to the doctor with no AI triage, HealthLinc asks a red-flag checklist. Any red flag means urgent, with emergency guidance; none means routine; a skipped checklist means priority. The patient may raise urgency, never lower it. The openPractice change's handoff schema carries the urgency source `patient_checklist` at `0a82fc2`. | MI-02, MI-12, MI-23; H-4 |

## Goals / Non-Goals

**Goals:**

- Implement openChart's half of `openpractice-clinical-handoff/1.0` against openPractice's canonical schema, verified by digest.
- Make sure every routed clinical item has a named owner, an acknowledgment, a clock and an escalation, so that an urgent item is never blocked, dropped or left unowned.
- Keep clinical content out of openPractice: obtain conversations by reference from the system that holds them, and reply through HealthLinc.
- Own one neutral conversation-retrieval contract, `openchart-conversation-retrieval/1.0`, that every system holding patient conversations implements (ruling 69).
- Give openChart one citable definition of a clinical communication record (MI-12), for inbox items and for AI consult records (origin `ai_consult`). Keep AI-authored content always distinguishable from clinician-authored content, and never let a communication become a clinical fact of record.
- Keep every ratified `expanded-patient-intake` requirement intact, and keep openChart free of billing and financial status.

**Non-Goals:**

- Encounters, diagnoses, procedures or billable facts. CF-06 is unchanged.
- AI drafting of clinical replies, or any agent action in the inbox.
- AI-authored orders, prescriptions or diagnoses, and the limited-practice and full-practice modes of ruling 59. They wait for openChart-spec change `define-ai-authored-clinical-records`, which is being drafted (ruling 64; Decision 13). Until its Tier 2 is in force for an act type, AI-authored content is communication only (MI-26).
- An administrative work queue in openChart.
- Defining clinical roles, the medical director or grants. They come from `define-clinical-acts-foundation` AU-01 to AU-06 (Decision 15).
- Defining HealthLinc's or medXfactory's internals. Their sides are stated at contract level only: each implements `openchart-conversation-retrieval/1.0`.
- openChart's own link contract with HealthLinc (ruling 39), which needs its own change (Open Question 3).
- openChart's receiving side of MedxEHR's relay of the medical AI's records (ruling 70), which belongs to `define-ai-authored-clinical-records` (Open Question 4).
- Changing any ratified text, or adopting the constitution inside this change.

## Decisions

### 1. Contract reuse

openChart uses only the messages in the pinned schema, and defines no message of its own toward openPractice (MI-01). Toward the systems that hold conversations, it uses only its own retrieval contract (Decision 14).

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

The pin at `0a82fc2` also carries:
- `conversation_source` `healthlinc` for any conversation HealthLinc holds: a coach conversation, a direct message to the doctor or an administrative thread;
- the offer field `identity_state` (`linked`, `link_in_review` or `unlinked`). The schema allows `link_in_review` and `unlinked` only for `priority` and `urgent` offers;
- for an `unlinked` offer, `unlinked_identity`, with exactly `legal_name`, `birth_date` and `administrative_sex` from the `openpractice-ehr-patient-link/1.0` snapshot, and no `link_id` or `ehr_patient`;
- `handoff.clinician_urgency_raised`;
- the `handoff.urgency_raised` sources `coach_triage` and `medical_ai_triage`, which replace `healthlinc_triage`, and `patient_checklist`, a patient's raise through HealthLinc's red-flag checklist (ruling 71), alongside `staff`, `agent_proposal` and `routing_rule`.

`link_id` is optional on `handoff.ack`, `handoff.urgency_raised`, `handoff.status` and `handoff.clinician_urgency_raised`. `message.ack` must name a `handoff_id`, a `link_id` or both. openChart's messages about an `unlinked` handoff carry the `handoff_id` and no `link_id`; those about a handoff with a link carry both (MI-06).

### 2. The pinned schema

MI-02 pins `openspec/changes/define-patient-gateway-and-escalation/contracts/openpractice-clinical-handoff-1.0.schema.json` in `opensoft/openPractice-spec`. The pin is at revision `0a82fc2`, the openPractice-spec `main` commit that merged PR #6, SHA-256 `19dff20f95cd31afdef02270119a123a7c4662a4fcc5b20ef09d5b9cd5d91e2d`. The digest matches the line for that file in the change's `contracts/SHA256SUMS` at that revision. Since the previous pin, the schema has changed only in its descriptions and by adding the urgency source `patient_checklist`. The pin is updated, in a governed revision of this change, whenever that schema changes.

### 3. Where the conversation comes from

The handoff is reference-only. openChart fetches the conversation by `conversation_ref` from the system that `conversation_source` names, never from openPractice, with `conversation.retrieve` under its own retrieval contract (MI-03; rulings 51 and 69; Decision 14):

| `conversation_source` | Held by | Reference | Retrieval |
|---|---|---|---|
| `healthlinc` | HealthLinc, for any conversation it holds: a coach conversation, a direct message to the doctor or an administrative thread | `conversation_ref`, namespace `healthlinc` | Required to enable the inbox |
| `medxfactory` | medXfactory, for a medical-AI conversation | `conversation_ref`, namespace `medxfactory` | Required where the practice uses medXfactory's medical AI (MD-12) |

The schema enforces that the namespace matches the source. `healthlinc_message_ref` is HealthLinc's reference for the patient's request. openChart keeps it in the record and uses it for split requests (MI-16).

The reply always goes to HealthLinc as `reply.deliver` against `reply_path_ref`, whichever system holds the conversation, as openPractice ER-05 also states (design call MD-16). The medical AI's records reach the chart only through MedxEHR, which relays them with receipts; medXfactory does not write to openChart directly (ruling 70, refining ruling 53). That write path belongs to `define-ai-authored-clinical-records`, and this change only cites it. For a medXfactory-held conversation, the inbox keeps per-turn metadata keyed by `turn_id`, the `snapshot_ref`, the `consent_ref` and the retrieval provenance, and never a copy of any turn's text (MI-12, MI-24, design calls MD-17 and MD-27).

### 4. Acceptance, clock and deadlines

`handoff.ack` `accepted` is system acceptance: the item exists durably, it has a named owner, and its clock is running (design call MD-1). It does not mean a clinician has read the item. Clinician acknowledgment is an explicit act inside openChart, and escalation runs on it (MI-09).

openChart owns the clock (ruling 43). Deadlines come from an openChart response policy that the medical director approves. Until one is approved, the offer's own `ack_by` and `respond_by` apply. After approval, the earlier of the policy's deadline and the offer's applies. Nothing ever extends a deadline (design call MD-2). The openPractice change's default windows (its design call DC-3) are proposed defaults in an unratified change, not facts. This change adopts no number of its own.

openPractice treats `clock_expired`, or silence past `respond_by`, as `clinical_response_overdue`. It then alerts the office manager and sends a tracked alert to the on-call clinician. For an urgent item it also runs the fallback with emergency guidance (openPractice ER-07, ER-09). openChart therefore behaves as follows (MI-05, MI-06, design call MD-15):
- its effective deadline never falls after `respond_by`;
- it sends `clock_expired` the moment that deadline passes, and `responded` as soon as HealthLinc accepts the reply, each in the same transaction as its cause.

### 5. Ownership, cover and escalation

- Every item has exactly one named owner, who holds the foundation's `clinician` or `nurse` role (AU-01) and `own` over `clinical_inbox_item` for its lane, `physician` or `nurse` (AU-06; MI-07).
- Until a lane policy is approved and the medical director records the nurse-lane scope (AU-06), every item enters the physician lane (design call MD-3).
- openChart keeps its own cover roster, with the medical director as the last fallback. The inbox cannot be enabled with a gap, and a grant lapse that opens one is closed by MI-08's warnings, alerts and fallbacks (design call MD-4).
- An unacknowledged urgent item escalates to the on-call clinician, then to the medical director, and keeps re-alerting. It never drops, parks or closes (MI-09).
- An expired item stays queued, open and owned until a clinician replies or records a closing outcome. Any holder of a `clinical_inbox_item` grant can find it by its routing id (`handoff_id`), including the on-call clinician named in openPractice's tracked alert (MI-09; MT-7).
- No agent owns, acknowledges, answers, re-routes or closes an item (design call MD-10).

### 6. Urgency

openChart never lowers urgency, by any path. A raise moves deadlines only earlier, and a raise that arrives before its offer is applied when the offer arrives (MI-10). A clinician may raise an item to `priority` or `urgent` inside openChart. openChart reports every such raise as `handoff.clinician_urgency_raised`, with its new `respond_by` and an opaque `raised_by`, over the durable delivery of PL-14 (design call MD-8). The openPractice change then applies three rules (its ER-03, DC-30 and DC-42):
- it shadows the new deadline, never later than its current one;
- a raise to `urgent` gets its urgent path, with emergency guidance if the deadline is missed;
- a raise to `priority` gets a tracked on-call alert, with no guidance for the patient. A raise to `urgent` on an item already answered or closed reopens it inside openChart (design call MD-9).

### 7. Reply, record and authorship

- The reply goes to the patient through HealthLinc, as `reply.deliver`. `responded` is reported as soon as HealthLinc accepts it with `message.ack` `received` (MI-11, design call MD-15).
- **MI-12 is the single, citable definition of a clinical communication record in openChart.** Each record has an origin: `handoff` for an inbox item, or `ai_consult` for a consult record that `define-ai-authored-clinical-records` writes, whose provenance and full exchange that change defines (design call MD-28). It gives every retrieved turn, keyed by `turn_id`, one author type: `patient` (or `representative`), `ai`, `clinician`, `staff`, `system`, or the fail-safe `unknown`. It also gives the turn a source token: `healthlinc`, `medxfactory` or `openpractice_agent`. An `ai` turn names its source: HealthLinc's coach, medXfactory's medical AI, or an openPractice agent's administrative answer with its answer type and version or its approver. A patient's own turn is never shown as AI content. Every urgency source maps to an author type, and `patient_checklist` maps to `patient` (design call MD-24). MI-12 also states the provenance the record holds, and the rule that a clinical communication is never a diagnosis or a clinical fact of record. MI-13 and MI-14 cite it. `define-ai-authored-clinical-records` references it rather than defining a second record (ruling 64). Nothing is silently overwritten, and a correction is a new version. The storage shape is decided in planning.
- AI-authored and `unknown` content is never recorded, shown or delivered as clinician-authored (MI-13).
- Patient-reported text and AI text never become a diagnosis, a clinical fact or a billable fact (MI-14, design call MD-11).
- Replies honor confidential-communication instructions (PL-16). An unfiled item's reply stays inside the HealthLinc conversation. A withheld reply keeps the item open (MI-22, design call MD-13).
- If HealthLinc reports through `reply.delivery_failed` that an accepted reply was not delivered, `responded` is not final. The item reopens and stays owned, an `urgent` item escalates, and the owner is pointed to a permitted channel (MI-11, design calls MD-21 and MD-26). openPractice is not told under the handoff contract 1.0 (MT-15).

### 8. Re-routing and splitting

- **An administrative item** is returned with `returned_not_clinical` and is never answered. openChart keeps no administrative queue (MI-15).
- **A mixed item** has its clinical part answered in openChart. openChart asks HealthLinc, with `split.request`, to split the item and resubmit the administrative part to openPractice (MI-16, design call MD-7). The schema has no status for a partial return (MT-6).

### 9. Identity decision

A handoff resolves the patient only through the links that exist (MI-17, ruling 39):
- the `openpractice` row for the `link_id` (PL-02), on an offer marked `linked`, together with the `ehr_patient` triple under openChart's issuer (PL-03);
- where one exists, the openChart reference that the conversation's holder reports for the account (`ehr_patient` in `conversation.result`), as a cross-check only.

The offer's `identity_state` is an input, never a resolution. Where it and openChart's own link state differ, the more uncertain governs. There is no demographic matching. `unlinked_identity` (`legal_name`, `birth_date`, `administrative_sex`) is shown as unverified and never used to match or file, and no Medx or medXfactory reference is used (design calls MD-5, MD-19).

| Situation | `routine` | `priority` or `urgent` |
|---|---|---|
| `linked`; `active` row; triple matches; the holder, if it reports one, agrees | Accept and file | Accept and file |
| `link_in_review` (identity review or demographic hold) | Refused by the schema: `schema_invalid` | Accept unfiled; show the uncertainty; open identity review; escalate under MI-09 |
| `linked`, but openChart holds the row in `identity_review` | Reject `link_in_review` | Accept unfiled; show the uncertainty; open identity review; escalate under MI-09 |
| `unlinked`, with `unlinked_identity` | Refused by the schema: `schema_invalid` | Accept unfiled; show the three fields as unverified; open identity review; escalate under MI-09 |
| `linked` but `link_id` unknown to openChart | Reject `link_unknown` | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| `linked` but the row is `revoked` or `superseded` | Reject `link_revoked` (the schema has no superseded code) | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| `linked` but `ehr_patient` does not match the row | Reject `ehr_patient_mismatch` | Accept unfiled; open identity review; escalate under MI-09 (MT-1, resolved) |
| After acceptance: the holder names a different patient, or the link enters review or is revoked | Stays accepted; becomes unfiled; identity review | Same |

The openPractice change's ER-06 offers only `urgent` and `priority` items on a link in review or with no link. At the same time, openPractice runs its fallback for an urgent item, or sends a tracked on-call alert with no guidance for a priority item. A `routine` row marked `linked` in this table covers only a mismatch between openPractice's and openChart's views. An unfiled item is filed only when a link resolves the patient. No human files it by judgment until the owner rules (design call MD-6, Open Question 7).

### 10. Boundaries

- openChart receives no billing, hold or financial status, and never gates an item on such status (MI-19).
- openChart keeps no administrative queue (MI-15).
- With no gateway configured, the inbox is inert. Enabling it needs four things: an openPractice integration identity; retrieval from HealthLinc under the retrieval contract, plus retrieval from medXfactory where the practice uses its medical AI; HealthLinc's declared `reply_delivery`, `delivery_failure_callback` and `split`; and full cover. Disabling it withdraws the handoff authorization (MI-20, design calls MD-12 and MD-23).

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

openChart must operate without MedxFactory, MedxEHR or openPractice, as the ratified text states. It also operates without HealthLinc or medXfactory, with no conversation source configured. Every inbox component is optional (MI-20, PL-15). The standalone golden-intake tests remain the regression gate.

### 13. AI practice modes (rulings 59, 64, 65 and 67)

The medical director sets medXfactory's AI to advice only, limited practice or full practice. medXfactory's change `define-patient-medical-ai-connection` owns the mode framework and its gates (rulings 56 to 58). Ruling 66 trims ruling 56 with an advice-only patient-consult class whose answers may reach the patient without prior sign-off. Ruling 67 keeps the never-grantable rule, and keeps limited and full practice specified but off.

This change does not cover AI-authored orders, prescriptions or diagnoses. openChart-spec change `define-ai-authored-clinical-records` is being drafted for them (ruling 64), alongside MedxEHR-spec change `define-medical-ai-record-overlay` on the MedxEHR side. Ruling 59 stands, so until Tier 2 of `define-ai-authored-clinical-records` is in force for an act type, MI-26 applies and fails closed. Ratification alone does not end the hold: that change's AA-01 refuses every `act.write` with `tier2_not_in_force` until `define-clinical-acts-foundation` (openChart-spec#5) is ratified and built and a future governed amendment puts Tier 2 in force (ruling 67). Meanwhile:
- AI-authored content is communication only, recorded under MI-12;
- on the paths the inbox controls, content that presents itself as an order, a prescription or a diagnosis is held as AI-authored communication, marked as not accepted as a clinical act; on that change's write path, the inbox defers to it (design call MD-20);
- the limited-practice and full-practice modes are not buildable in openChart.

Ruling 65 places the chart's own record of the medical director's authorization, and the check of every AI write against it, in `define-ai-authored-clinical-records`. Ruling 70 sends the medical AI's records to openChart through MedxEHR's relay, whose openChart side also belongs there. This change cites both and defines neither. It answers that change's tensions AT-5 (MI-26's hold), AT-6 (MI-12's origins, MD-28) and AT-7 (MD-20).

### 14. The conversation-retrieval contract (ruling 69)

openChart owns one neutral contract, `openchart-conversation-retrieval/1.0`, for every system that holds a patient conversation. HealthLinc and medXfactory implement it (H-1 to H-3, M-1). Its canonical schema is `contracts/openchart-conversation-retrieval-1.0.schema.json`, SHA-256 `bff486443f76f406d4dc99f24fabc34d6e36727fca9e0eb142875c807e5e41ff`, listed in `contracts/SHA256SUMS`. MI-02 and MI-03 pin it and own it, and MI-23's tests run against a double of it. It follows the handoff schema's style: the same envelope, closed objects, a random-UUID `message_id` as the idempotency key, coded errors only, and no PHI in any reference (design call MD-22).

| Message | Direction | Needs |
|---|---|---|
| `capabilities.request` | openChart → holder | Nothing |
| `capabilities.result` | holder → openChart | Nothing. The holder answers a request, or sends it unprompted when its capabilities change. |
| `conversation.retrieve` | openChart → holder | Nothing: every holder supports retrieval |
| `conversation.result` | holder → openChart | Nothing |
| `reply.deliver` | openChart → holder | `reply_delivery` |
| `reply.delivery_failed` | holder → openChart | `delivery_failure_callback` |
| `split.request` | openChart → holder | `split` |
| `message.ack` | both | Nothing. It acknowledges a reply, a callback, a split request or an unprompted declaration, and carries every refusal. |

- **Capability declaration.** A holder declares its versions and optional capabilities in `capabilities.result`. The latest declaration by `declared_at` governs. openChart never sends a message for a capability the holder has not declared, and a holder that receives one anyway refuses it with `capability_not_supported`.
- **Per-turn vocabulary.** Each turn carries `turn_id`, `position`, `author_type` (MI-12's types), `source`, `authored_at`, `request_turn` and plain-text `content`. It may carry `in_reply_to` and `shared_basis`, and an `ai` turn may carry `ai_mode`, `disclosure_code`, `model_ref`, `advice_statement_ref` (design call MD-30) and `emergency_guidance` (design call MD-33). A result may carry `origin_conversation_ref` (design call MD-32). An `openpractice_agent` turn must carry exactly one of `agent_answer_type` and `approved_by`, and a `clinician` turn must carry `reply_id` (design call MD-24).
- **Source tokens.** `healthlinc`, `medxfactory` and `openpractice_agent`. A token is added only in a MINOR version.
- **Request turns and consent.** `conversation.retrieve` carries the item's `urgency`, and `conversation.result` echoes it and requires `consent_ref` and at least one turn. At least one turn is a request turn (`request_turn` true), written by the patient or a representative, with non-empty text. For `priority` and `urgent`, a request turn carries `shared_basis` `urgent_escalation`, and the result carries `patient_told_at`. Beyond that, a result may report `turns_withheld` and may mark each turn's `shared_basis` (`consent_scope`, `patient_confirmed` or `urgent_escalation`); any `urgent_escalation` turn also needs `patient_told_at` (design calls MD-25 and MD-29).
- **Errors.** One set of seventeen codes: `schema_invalid`, `unsupported_major_version`, `unauthorized`, `idempotency_conflict`, `capability_not_supported`, `conversation_not_found`, `reference_not_found`, `result_mismatch`, `consent_not_granted`, `reply_path_invalid`, `temporarily_unavailable`, and the six delivery-failure reasons. `failure_reason` is limited to those six (design call MD-26).
- **Versioning and issuers.** MAJOR.MINOR, compatible exactly within a MAJOR, as PL-12 requires for the boundary contracts. A sender uses the highest MINOR both sides have declared. A breaking change needs a new MAJOR and a new digest, recorded in this change and in each implementing change. Every issuer is a configured, stable identifier, unique across deployments and never derived from a host path, and references are compared as (issuer, namespace, value) triples, as PL-03 requires.
- **Standalone.** openChart works with no holder configured (MI-20). The contract adds no dependency to any other openChart operation.
- **Content.** Plain text only in 1.0, with no attachments (design call MD-27). Content travels only between a holder and openChart, never through openPractice.

### 15. Clinical roles and grants (`define-clinical-acts-foundation`)

openChart-spec change `define-clinical-acts-foundation` (openChart-spec#5), read here at `c9e3e7a`, holds the single definition of clinical roles, the medical director and grants: its clinical-authority capability, AU-01 to AU-06, which it builds as its own feature (1). AU-06, PROPOSED pending owner decision 92, carries the inbox's scopes. This change cites them by requirement ID, uses AU-06's action, record-class and lane names exactly, and defines no role or grant of its own. This answers the foundation's tension CT-9.

| What the inbox relies on | Where it comes from |
|---|---|
| The `clinician` and `nurse` roles: owners, the `clinician` author type (MI-12), markers | AU-01 |
| The medical director: the response and lane policies, the last fallback owner, escalation, cover | AU-01; as an owner, also AU-06's `own` for the lane |
| Grants recorded only by the medical director, never by default, by role name or by `System Manager` | AU-02 |
| Owning, acknowledging, reassigning, raising urgency, returning and splitting an item, in lane `physician` or `nurse` | AU-06: `own`, `acknowledge`, `reassign`, `raise`, `return`, `split` over `clinical_inbox_item` (MI-07 to MI-10, MI-15, MI-16) |
| What the nurse lane may triage or answer | AU-06: the nurse-lane scope the medical director records |
| Replying to a patient | AU-06: `reply` over `clinical_communication`, per role and lane, on an AU-03 attestation (MI-11) |
| Recording or withdrawing a clinical-need marker | AU-06: `mark` and `withdraw` over `clinical_need_marker`, `clinician` role only (MI-25) |
| On-call cover | AU-06: no designation; the roster names only holders of the lane's `own` grant (MI-08) |
| Every action checked against the grant in force, with reductions applied at once | AU-04 |
| Only named humans act | AU-05; MD-10 for the inbox |
| Recording an item's closing outcome | Not defined: tension MT-24 |
| Resolving identity review | PL-06 and PL-08 of `define-openpractice-boundary`, which name no clinical role |

Anyone without the grant in force for an action and lane fails closed (design call MD-31). A grant lapse can leave a roster slot empty, because AU-06 removes the holder at once and a lapse is not a refusable roster change. MI-08 therefore keeps a human reaching every item (design call MD-4).

## The openPractice change's companion items

The openPractice change's design, at `0a82fc2`, lists twelve items that this change must contain.

| Item in the openPractice change | Where this change meets it |
|---|---|
| Receive offers validated against the schema at digest `19dff20f…` | MI-01, MI-02 |
| Answer each offer with `handoff.ack`. Accept an urgent or priority offer in state `link_in_review` or `unlinked` as an unfiled item with the uncertainty shown; never refuse it for that state; never file or link on it automatically. Refuse a routine offer on a link in review with `link_in_review`, and a routine offer on a revoked or unknown link. Accept unfiled an urgent or priority offer marked `linked` that openChart finds revoked, unknown or mismatched | MI-04, MI-17, MI-18. Met (MT-1, resolved). |
| Send `handoff.clinician_urgency_raised`, with the new `respond_by` and the clinician's reference, whenever a clinician raises urgency, and never lower urgency | MI-10, MD-8 |
| Own the queue and the clock; report `responded`, `clock_expired`, `returned_not_clinical`, `content_unavailable` and `closed`; send `clock_expired` when the clock runs out and `responded` as soon as a clinician replies | MI-05, MI-06, MD-15 |
| Keep an expired item queued until a clinician responds, and show it by routing id to the on-call clinician who receives openPractice's alert | MI-09 (MT-7 for an on-call clinician without openChart access) |
| Fetch the conversation by `conversation_ref` from whichever system holds it, never through openPractice | MI-03, under openChart's own retrieval contract (Decision 14); MI-24 |
| Accept `patient_checklist` as a source of `handoff.urgency_raised` (ruling 71) | MI-02, MI-12 (recorded as `patient`), MI-23 |
| A reply path to HealthLinc that bypasses openPractice | MI-11 (`reply.deliver`), MD-16 |
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
| MD-3 | Until the medical director approves a lane policy, every item enters the physician lane. What nurses may answer comes only from that policy; scope of practice is for the medical director and counsel. The nurse lane's scope is the one the medical director records under AU-06 (PROPOSED pending owner decision 92). Until a lane policy is approved and that scope is recorded, the nurse lane stays closed and every item enters the `physician` lane. | MI-07 |
| MD-4 | openChart keeps its own cover roster: a schedule naming, per hour and lane, only holders of that lane's `own` grant, the medical director included as the last fallback (AU-06). The inbox cannot be enabled with an uncovered hour, and a roster or account change that would open a gap is refused. A grant lapse is not such a change, and AU-06 removes the holder at once, so a gap can still open. MI-08 closes it: warnings before scheduled ends; at once, an alert to the medical director and the administrative role of AU-01; a `nurse`-lane slot falling back to the `physician` lane, and a `physician`-lane slot to the medical director when they hold `own`; otherwise an alert to every grant holder for the lane, repeated each escalation interval. No offer is accepted without a named owner. It waits unacknowledged, so openPractice's missing-acknowledgment alert and urgent fallback run at `ack_by`. | MI-04, MI-07, MI-08, MI-09 |
| MD-5 | Identity is handled by urgency, and by the more uncertain of the offer's `identity_state` and openChart's own link state. An `urgent` or `priority` offer whose patient cannot be resolved is accepted unfiled, opens an identity review and escalates under MI-09. It is never rejected for identity. A `routine` offer in state `link_in_review` or `unlinked` fails the pinned schema (`schema_invalid`). A `routine` offer marked `linked` whose link openChart finds uncertain is rejected with `link_unknown`, `link_revoked`, `link_in_review` or `ehr_patient_mismatch`. On `handoff.ack`, openChart uses only `schema_invalid`, `unsupported_major_version`, `unauthorized`, `link_unknown`, `link_revoked`, `link_in_review` and `ehr_patient_mismatch`. A superseded link maps to `link_revoked`, because the schema has no separate code. openChart never sends `origin_not_verified`, which is openPractice's reason for rejecting a marker. | MI-18 |
| MD-6 | An unfiled item is filed only when a link resolves the patient. No human files it by judgment until the owner rules. `unlinked_identity` (`legal_name`, `birth_date`, `administrative_sex`) is shown as unverified and never used to match or file. A HealthLinc reference alone does not file an `unlinked` item until openChart's HealthLinc link contract exists (Open Question 3). | MI-17, MI-18 |
| MD-7 | A mixed item's administrative part goes back through `split.request` to HealthLinc, which resubmits it, not through a new handoff status. openChart sends the request only while HealthLinc declares `split`; otherwise the item stays open and owned with a coded exception. | MI-16 |
| MD-8 | A holder of `raise` over `clinical_inbox_item` (AU-06) may raise urgency inside openChart, to `priority` or to `urgent`. openChart reports **both** kinds of raise as `handoff.clinician_urgency_raised`, with its new `respond_by` and an opaque `raised_by`, over PL-14's durable delivery. It reports both because the schema allows both values. openChart promises nothing beyond what the openPractice change defines (its ER-03, DC-30 and DC-42): openPractice's shadow deadline never moves later, a raise to `urgent` gets its urgent path with patient guidance on a missed deadline, and a raise to `priority` gets only a tracked on-call alert, with no patient guidance. | MI-10 |
| MD-9 | A raise to `urgent` on an item that is already `responded` or closed reopens it inside openChart. openChart sends no status after `closed`. When the raise is a clinician's, openChart still sends `handoff.clinician_urgency_raised`, because that message is not a status; whether openPractice accepts it after `closed` is Open Question 15. When the raise came from openPractice, openPractice already knows. | MI-10 |
| MD-10 | No agent owns, acknowledges, answers, re-routes or closes an item, and no AI drafts a clinical reply. Content of unknown authorship carries the author type `unknown` (MI-12). | MI-07, MI-12, MI-13 |
| MD-11 | Inbox records are not encounters, diagnoses or procedures. They are never billable, never become intake statements, and AI text never becomes a clinical fact. | MI-12, MI-14 |
| MD-12 | With no gateway the inbox is inert; the clinical communication record is not (MD-28). Enabling it needs integration, HealthLinc retrieval with the three capabilities of MD-23, and cover, plus medXfactory retrieval where the practice uses medXfactory's medical AI. An offer that names an unconfigured source is still accepted, and follows MI-03's failure path. Disabling the inbox withdraws the handoff authorization. No patient message reaches openChart except through an openPractice handoff. The medical AI's records arrive only through MedxEHR's relay (ruling 70), which this change does not define. | MI-03, MI-20 |
| MD-13 | An unfiled item's reply stays inside the HealthLinc conversation (`delivery_scope` `conversation_only`), with every other channel restricted. A reply that PL-16 withholds keeps the item open and owned. | MI-22 |
| MD-14 | One item per `handoff_id`. A conflicting offer for the same `handoff_id` leaves the item unchanged and records an integration exception. | MI-04 |
| MD-15 | Status timing. `clock_expired` is sent the moment openChart's effective deadline passes, which is never after the offer's `respond_by`. `responded` is sent as soon as HealthLinc accepts the reply. Each is written in the same transaction as its cause, so openPractice's `clinical_response_overdue` fallback runs on time. `content_unavailable` is sent at the first failed retrieval for an urgent or priority item, so that openPractice's fallback or tracked on-call alert runs at once, and after the retry policy for a routine item. A retrieval fails under MD-29's test. `returned_not_clinical` is the last status for its item. `closed` follows `responded`, or stands alone for an item closed without a reply. An expired item stays queued and is visible by routing id. | MI-03, MI-05, MI-06, MI-09 |
| MD-16 | A reply to a conversation that medXfactory holds still goes to HealthLinc, as `reply.deliver` against `reply_path_ref`, so medXfactory need declare no optional capability. This now matches openPractice ER-05 at `0a82fc2`. It stays a design call only because that change is unratified. | MI-11 |
| MD-17 | For a conversation that medXfactory holds, the inbox item keeps only per-turn metadata keyed by `turn_id` (author type, source and time), the `snapshot_ref`, the `consent_ref` and the retrieval provenance, with no text. It files no copy, because the medical AI's records reach the chart through MedxEHR's relay (ruling 70). The no-copy rule applies to inbox items only, never to an `ai_consult` record (MD-28). Whether openChart keeps an audit copy, outside the chart, of what the clinician saw is Open Question 10. | MI-12, MI-24 |
| MD-18 | Clinical-need markers, beyond what the schema fixes, follow these rules. **(a)** openChart mints one `need_id` per marker and reuses it for the withdrawal. **(b)** The clinician must set `valid_until`; there is no default. **(c)** `urgent_escalation` is used only for a marker recorded from an item whose urgency is `urgent` as openPractice offered or raised it. A clinician's raise to `urgent` also counts once openPractice has answered it with `message.ack` `received`, since openPractice's ER-03 then treats the item as urgent. The marker carries that item's `handoff_id` as `related_handoff_id`. **(d)** After `origin_not_verified`, openChart shows the clinician the coded reason and never resends with a different origin on its own. **(e)** `marked_by` is never derived from the clinician's name or login. **(f)** A marker may be recorded only on an `active` link, so a PL-08 hold blocks it (MT-3). **(g)** Any named holder of `mark` over `clinical_need_marker` may record one, and AU-06 records that grant only for the `clinician` role, as ruling 50's "a clinician" requires. | MI-25 |
| MD-19 | A handoff never resolves the patient through a Medx or medXfactory reference, even when medXfactory holds the conversation. A holder's `ehr_patient` is only a cross-check: it never resolves a patient on its own, and a disagreeing one makes the item unfiled. | MI-17 |
| MD-20 | On the paths the inbox controls, inbox retrieval and its `handoff` records, an AI-authored order, prescription or diagnosis is held as AI-authored communication, marked by code as not accepted as a clinical act, rather than refused. Holding it keeps a record of what the patient was told and creates nothing clinical. On the write path of `define-ai-authored-clinical-records`, MedxEHR's relay (ruling 70), the inbox defers to that change: an `act.write` is refused and stores no content (its AD-7), and act-like content inside a consult record is handled by its AC-05. MI-26 holds until Tier 2 of that change is in force for the act type, not merely until it is ratified, because its AA-01 refuses every act write until then. This answers that change's tensions AT-5 and AT-7. | MI-26 |
| MD-21 | When HealthLinc's `reply.delivery_failed` callback reports that an accepted reply was not delivered, `responded` is not final. The item reopens and stays owned, an `urgent` item escalates under MI-09, and the owner is pointed to a permitted channel (MI-22). A non-urgent item is not escalated. openChart sends openPractice nothing, because 1.0 has no status that withdraws `responded` (MT-15). | MI-11 |
| MD-22 | The retrieval contract's shape. One contract serves every holder, in the handoff schema's style. Retrieval is required. Reply delivery, the delivery-failure callback and split are optional capabilities declared in `capabilities.result`, which `capabilities.request` solicits or the holder sends unprompted on a change. The latest declaration governs. openChart never sends a message for an undeclared capability, and a holder refuses one with `capability_not_supported`. One `message.ack` carries every acknowledgment and refusal, and one set of seventeen error codes serves the whole contract. `conversation.result` names a `snapshot_ref` that identifies what the clinician saw. | MI-02, MI-03; Decision 14 |
| MD-23 | Enabling the inbox needs HealthLinc to declare `reply_delivery`, `delivery_failure_callback` and `split`, because MI-11, MI-16 and MD-21 depend on them. medXfactory needs only retrieval, since replies go through HealthLinc (MD-16). If HealthLinc withdraws one of them while the inbox is enabled, openChart keeps accepting offers, keeps every item owned, sends no message for the withdrawn capability, and shows the coded cause to each affected owner and to the medical director. It does not disable the inbox on its own, because refused offers would delay urgent items. | MI-11, MI-16, MI-20 |
| MD-24 | Turn sources and authorship. The source token names the system that produced or relayed the turn. A human's turn carries its holder's token with its own author type, and display follows the author type, so a patient's turn is never shown as AI content. An `openpractice_agent` turn is `ai` and carries exactly one of the answer type and version or the approving staff member; the answer type has the shape of `answerTypeRef` in openPractice change `define-actors-agents-and-work-inbox`, at `1086321`, on openPractice-spec `main` at `0a82fc2`. A `clinician` turn must carry a `reply_id`, and openChart shows it as clinician-authored only when that id matches its own reply record; otherwise it shows `unknown`. Urgency sources map to author types as MI-12 states, with `patient_checklist` as `patient`. | MI-12, MI-13 |
| MD-25 | Consent. `consent_ref` is required and recorded. The patient's consent decides what else is shared, never whether the request is. Every result carries at least one request turn, and for a `priority` or `urgent` item the request turns are always shared as `urgent_escalation`, with the patient told (`patient_told_at`). The schema refuses a result that breaks either rule. The basis `urgent_escalation` covers `priority` items too. A holder may withhold other turns that the patient's consent does not allow, and reports only their count; openChart then shows the owner a partial view and never presents it as the whole conversation. A `consent_not_granted` refusal is a failed retrieval under MI-03. openChart never asks a holder to widen what the patient's consent allows. | MI-03, MI-12 |
| MD-26 | Delivery failure. HealthLinc's names are adopted unchanged as canonical: `reply_message_id`, `reply_id`, `handoff_id`, `reply_path_ref`, `failure_reason` and `failed_at`, with its six `failure_reason` codes. The one structural choice is that `failure_reason` is a subset of the contract's single error set rather than a separate list. openChart retries a reply only when HealthLinc is unreachable or answers `temporarily_unavailable`; any other refusal goes to the owner with its code. | MI-11 |
| MD-27 | Content is plain text in 1.0, with no attachments, up to 20,000 characters a turn; that limit is a proposed figure for the owner to confirm. For a conversation medXfactory holds, openChart records each turn's metadata and no text (MI-24). | MI-12, MI-24 |
| MD-28 | Record origins. MI-12 defines one clinical communication record with two origins: `handoff` for an inbox item, and `ai_consult` for a consult record that `define-ai-authored-clinical-records` writes through its `consult.write`. That change defines the `ai_consult` provenance (model and version, evidence, mode, authority and digest) and holds the full exchange (its AC-01 to AC-03), with turns of author type `patient`, `representative` or `ai` only (its AC-02). MI-12's author types, its not-a-fact-of-record rule and its versioning apply to both origins. The handoff provenance, MI-20's inertness and MI-24's no-copy rule apply to `handoff` records only, so an `ai_consult` record exists without the inbox or openPractice. This answers that change's tension AT-6 and its design call AD-3. The alternative that AT-6 names, moving the record into its own capability, is left to the owner. | MI-12, MI-20, MI-24 |
| MD-29 | Successful retrieval. A retrieval succeeds only with a schema-valid `conversation.result` that answers it: the same `handoff_id` and `conversation_ref`, and the urgency openChart sent. The schema cannot compare a result with its retrieve, so openChart checks those three and refuses a mismatch with `result_mismatch`, a new code in the contract's one set. Every other outcome is a failed retrieval under MI-03: a refusal, silence, `schema_invalid` (an empty result, a result without a request turn, or a priority or urgent result without the escalation share included) and `result_mismatch`. A failed retrieval of an urgent or priority item is reported as `content_unavailable` at once (MD-15), so openPractice's fallback or tracked on-call alert runs. Withheld turns beyond the request turns make a retrieval partial, not failed. When an item's urgency rises to priority or urgent, openChart retrieves again with the new urgency; content already retrieved stays visible meanwhile. | MI-03, MI-12 |
| MD-30 | AI-turn provenance. An `ai` turn may carry `ai_mode` (`advice_only`, `limited_practice` or `full_practice`: ruling 59's modes, with the values of `mode` in openChart-spec#4's `openchart-ai-clinical-record-write/1.0` at `5a9947f`), `disclosure_code` (a code), `model_ref` (the model identifier and version as one reference) and `advice_statement_ref` (an opaque reference to the statement shown). All four are optional, and the schema refuses them on any non-AI turn. openChart records them per turn (MI-12) and shows them with the turn. Any that is absent is shown as not stated, and openChart never infers a mode, so an absent `ai_mode` never reads as advice-only. They are the holder's statement, not openChart's check: checking an AI write against the medical director's authorization belongs to `define-ai-authored-clinical-records` (ruling 65). | MI-12, MI-13 |
| MD-31 | Authority fails closed. The inbox defines no role or grant of its own (Decision 15). It relies on AU-06 of `define-clinical-acts-foundation`, PROPOSED pending owner decision 92, for the ownership, reply and marker scopes and for the roster rule. A person without the grant in force for an action and lane takes none of that action: no owning, acknowledging, reassigning, raising, returning, splitting, replying or marking. The inbox cannot be enabled until the foundation's feature (1) is built with AU-06 in force (MI-20). If owner decision 92 rejects AU-06, no one holds an inbox grant, so the inbox cannot be enabled, and markers are refused. | MI-07, MI-08, MI-11, MI-20, MI-25 |
| MD-32 | Origin reference. A result may name, in `origin_conversation_ref`, the earlier conversation this one began from, at the same holder or another, in the conversationRef shape (issuer, holder token, value). openChart records and shows it, and never retrieves it on its own. Reading it is a separate retrieval from the holder it names, under that holder's consent rules, at a named clinician's explicit request. Version 1.0 defines no purpose for that retrieval, because `clinical_handoff` requires a request turn that an origin conversation need not hold, so openChart reads no origin conversation until a MINOR version adds a purpose. | MI-03, MI-12 |
| MD-33 | Emergency-guidance marker. An `ai` turn may carry `emergency_guidance`: a non-empty array of unique codes from a closed, neutral list (`call_emergency_services`, `go_to_emergency_department`, `contact_crisis_line`, `contact_poison_control`, `seek_urgent_care`). It is an array because one turn can give more than one kind of guidance. The list asserts no medical specifics, and a value is added only in a MINOR version. The schema refuses the marker on a non-AI turn, and requires non-empty text on a turn that carries it. openChart shows the turn prominently, with its codes, wherever the turn or its item is shown. The marker never replaces the text, and never changes the item's urgency, owner or clock: it is the holder's statement, and urgency changes only by the paths of MI-10. | MI-12, MI-13 |

## Consistency with ratified `expanded-patient-intake` requirements

| Ratified requirement | How this change stays consistent |
|---|---|
| Original standalone Frappe application, which "MUST operate without MedxFactory, MedxEHR or openPractice" | MI-20 restates it with all three systems, and adds HealthLinc, medXfactory and the case of no conversation source configured. The inbox is optional, and inert without a gateway. The golden-intake tests remain the gate. |
| External identifiers must not replace the openChart identifier or merge patients | MI-17 and MI-18 resolve only through existing links. Nothing is matched, merged or re-pointed; an unresolved item stays unfiled. |
| Intake submissions are versioned, auditable and idempotent | Untouched. Messages are not intake submissions and never become statements (MI-14). |
| Medication, supplement and other statements preserve reported detail | Untouched. |
| Amendments preserve accepted history | MI-12: communications are never silently overwritten, and corrections are new versions. |
| APIs and hooks are authorized and versioned | MI-01 uses a role narrower than `System Manager`, authorized for subject, tenant, purpose and role. MI-02 versions both inbox contracts by MAJOR version and digest. |
| Intake confers no clinician or autonomous authority | MI-12 makes a clinical communication never a diagnosis or clinical fact of record. MI-14 keeps patient text patient-reported. MI-13 bars AI drafting. MI-26 keeps AI-authored content as communication, never an order, prescription or diagnosis. MT-10 records the reading of "autonomous action" that this change relies on. |

**One possible conflict with ratified openChart text is recorded, as MT-10.** No other conflict with ratified text was found.

## Consistency with `define-openpractice-boundary`

| Requirement | Relation |
|---|---|
| PL-01, PL-06 | Kept. No merge, and identity review follows PL-06 (MI-17, MI-18). |
| PL-02, PL-03 | Used to resolve the patient (MI-17). PL-03's issuer rule is reused for the retrieval contract (Decision 14). |
| PL-04 | Its pattern is reused for a third pin (MI-02). PL-04's own two pins are unchanged. |
| PL-05 | Its role pattern is reused (MI-01). openChart never creates a link from its own matching (MI-17). |
| PL-08 | **Tension MT-3.** A PL-08 hold also blocks clinical-need markers (MD-18). |
| PL-12 | Its versioning pattern is reused for both inbox contracts (MI-02). |
| PL-13 | Extended to both inbox contracts (MI-21). |
| PL-14 | Reused for handoff messages and markers (MI-06, MI-25). PL-14 lists the two boundary contracts; this change adds a third user of the store and changes nothing in PL-14. |
| PL-15 | Restated (MI-20). |
| PL-16 | Applied to replies (MI-22). **Tension MT-9.** |
| CF-02, CF-05, CF-06 | Kept (MI-14, MI-19). **Tension MT-8** concerns that change's design context. |

## Conflicts and tensions

Twenty-four are recorded. MT-2, MT-11 and MT-13 are resolved by the openPractice change's text, checked again at `0a82fc2`. MT-1 is resolved too, by the companion list that `0a82fc2` still carries. MT-14 is resolved by ruling 67. MT-17 to MT-22 are resolved by AU-06 of `define-clinical-acts-foundation` at `c9e3e7a`, PROPOSED pending owner decision 92. Thirteen tensions (MT-3 to MT-10, MT-12, MT-15, MT-16, MT-23 and MT-24) need the owner's disposition before ratification. None is resolved by this draft on its own authority.

| # | Tension | Status |
|---|---|---|
| MT-1 | Earlier, the openPractice change's companion list said that openChart must "refuse an offer on a revoked, unknown or in-review link", and its ER-06 made an active, unreviewed link a precondition. MI-18 accepts urgent and priority offers whose identity is uncertain. | **Resolved** by ER-06 and by the openPractice change's companion list, both as they stand at `0a82fc2`. The list requires accepting unfiled an urgent or priority offer in state `link_in_review` or `unlinked`, or marked `linked` with a link that openChart finds revoked, unknown or mismatched. openChart refuses only a routine offer on a revoked or unknown link, and accepts unfiled an urgent or priority offer marked `linked` that it finds revoked, unknown or mismatched, as MI-18 says. |
| MT-2 | Earlier, an urgent item on a link in review, or for a patient with no link, was never offered. The on-call clinician received only a routing id, an urgency and a coded cause, and could not read the message in openChart. | **Resolved by ER-06**, unchanged at `0a82fc2`. Unlinked `urgent` and `priority` items are offered with `unlinked_identity` (`legal_name`, `birth_date` and `administrative_sex`). MI-18 accepts them unfiled, and shows those fields to the clinician as unverified and never matched (MI-17). This answers openPractice Open Question 5. Residual, not a safety tension: a `routine` item on a link in review, or with no link, is still an office-manager exception in openPractice. |
| MT-3 | PL-08 puts a link in `identity_review` during every date-of-birth hold. openPractice EB-05 and EB-08 (in `define-mvp-practice-foundation`) report such a hold in the same state as a linkage conflict. The openPractice change's ER-06 therefore sends both as `identity_state` `link_in_review`, as its tension T-11 records. `routine` items during a hold are still not offered, and MD-18 blocks clinical-need markers during a hold. | **Follow-up**, and the safety part is addressed by ER-06. The openPractice change's T-11 proposes a governed amendment to EB-05, EB-08 and PL-08 that distinguishes a demographic hold from a linkage conflict. After it, `identity_state` could gain a separate value in a MINOR version. This change does not edit PL-08 in `define-openpractice-boundary`. The binding text fails closed: a hold counts as identity review (MI-18, MI-25). |
| MT-4 | openPractice ER-08 takes the windows from an openPractice routing-clock policy. Ruling 43 and MI-05 put the clock, and its windows, in openChart under the medical director's approval. Two policies can disagree. | MD-2 takes the earlier deadline, so openChart's policy can only tighten. Owner to confirm whether one policy record should govern both. |
| MT-5 | `handoff.ack` means system acceptance (MD-1). openPractice ER-09 now fires on `clock_expired` and on silence past `respond_by`, and MD-15 sends `clock_expired` on time. Before `respond_by`, though, openPractice still gets no signal that no clinician has acknowledged an urgent item. | Still open. The options are a status code in a MINOR version, or deferring `handoff.ack` until a clinician acknowledges. openChart's internal escalation (MI-09) is the inner safety net meanwhile. The same gap applies to an accepted item that loses every possible owner after a grant lapse (MI-08): openPractice learns of it only from `clock_expired`. |
| MT-6 | The 1.0 schema has no status for returning only the administrative part of a mixed item. openPractice ER-12 describes splitting only from openPractice's side. | MD-7 routes the split through HealthLinc instead. For a conversation that medXfactory holds, who splits is open (Open Question 14). |
| MT-7 | openPractice ER-13 keeps an on-call roster for its fallback. MI-08 keeps openChart's own cover roster. They can disagree. openPractice's tracked alert goes to openPractice's on-call clinician. MI-09 shows the item by routing id only to a holder of a `clinical_inbox_item` grant (AU-06). | Owner item, related to openPractice Open Question 6. openChart's roster governs its queue. Every clinician on openPractice's on-call roster also needs `own` over `clinical_inbox_item` in openChart (AU-06); planning confirms this. |
| MT-8 | `define-openpractice-boundary`'s design says that "Every statement in openChart is patient-reported" and that no clinician-authored records exist. This change adds clinician-authored replies. | Not a conflict with requirement text. CF-06 still holds, because a reply is not an encounter, a diagnosis or a procedure (MI-12, MD-11). That design statement becomes stale once this change lands. |
| MT-9 | PL-16 withholds any communication that cannot satisfy the patient's instructions. For an urgent reply, withholding delays care. | MI-22 keeps the item open and owned, and tells the owner to use a permitted channel. PL-16 is not weakened. Residual risk, recorded. |
| MT-10 | The ratified requirement "Intake does not confer clinician or autonomous authority" bars any "API response or extension event" from creating an "autonomous action". openChart's `AGENTS.md` says "Do not enable autonomous clinical actions by default." In this change, an API call (the offer) automatically creates an item, assigns an owner, sends alerts and reports status. | Reading proposed: these steps deliver an item to humans and decide nothing about care, so they are not clinical or autonomous actions. The ratified text does not define "autonomous action", so the owner confirms this reading at ratification. |
| MT-11 | The schema first pinned (`2353d99`) could name only HealthLinc as a conversation's holder, but ruling 51 adds medXfactory-held conversations. | **Resolved by the re-pin.** Since `097278c`, and still at `0a82fc2`, the offer requires `conversation_source` (`healthlinc` or `medxfactory`) and a matching `conversation_ref`. openPractice ER-05 states the same. medXfactory retrieval is live (MI-03). |
| MT-12 | openChart's test fixture `tests/fixtures/medx/binding-03-openchart.yaml` binds HealthLinc, OpenEMR and openChart references to one `medx_patient_id`. Ruling 39 says there is no master identity across HealthLinc, openPractice and openChart. Rulings 51 and 53 bring medXfactory into the patient's path and into the chart. | MI-17 never resolves a handoff through a Medx or medXfactory reference (MD-19). Owner to confirm that the Medx binding is not a master identity for the gateway or chart paths. The changes that own ruling 70's relay must say how it identifies an openChart patient; openChart's side belongs to `define-ai-authored-clinical-records`. |
| MT-13 | The schema first pinned had no message for a clinician's continuity decision (ruling 50) or clinically-needed marker. | **Resolved by the re-pin.** Since `097278c`, and still at `0a82fc2`, the schema defines `clinical_need.marker` (openPractice ER-18), and MI-25 sends it. |
| MT-14 | Ruling 59 lets the medical director set medXfactory's AI to limited or full practice, under gates that medXfactory's change owns. openChart cannot record an AI-authored clinical act until Tier 2 of `define-ai-authored-clinical-records` is in force for the act type. A practice could therefore configure a mode in medXfactory whose acts openChart holds only as communication. | **Resolved by ruling 67:** limited and full practice stay specified but off, so no practice can configure them. MI-26 still fails closed until Tier 2 of `define-ai-authored-clinical-records` is in force for the act type. |
| MT-15 | openPractice closes its routing record when `responded` arrives (openPractice ER-07). If HealthLinc later reports through `reply.delivery_failed` that an accepted urgent reply was not delivered, openPractice is not told, because 1.0 has no status that withdraws `responded`. Its office-manager alert and patient guidance therefore do not run for that failure. | Owner item. MD-21 handles the failure inside openChart: the item reopens and escalates, and the owner reaches the patient through a permitted channel. Options for telling openPractice: a status in a MINOR version of the handoff contract, HealthLinc telling openPractice directly, or reusing `handoff.clinician_urgency_raised` with a new deadline, which would stretch that message's meaning. None is adopted here. |
| MT-16 | The retrieval contract lets a holder withhold turns that the patient's consent does not allow, or return only those the patient confirmed. The clinician may then answer without a turn that mattered clinically. | **Narrowed**; residual risk, for the owner and counsel. Consent can no longer hide the request: every result carries the request turn, and a priority or urgent item's request turns are always shared with the patient told. A result without them is a failed retrieval, reported as `content_unavailable` so that openPractice's fallback runs (MD-25, MD-29). Other turns may still be withheld. The clinician sees a partial view with the count, and can still reach the patient. |
| MT-17 | Inbox ownership. The inbox needs a named human to own, acknowledge, reassign, raise, return and split routed clinical items, and to find them by routing id. `define-clinical-acts-foundation` grants authority only per act class and action (AU-02), and an inbox item is not an act. | **Resolved, PROPOSED pending owner decision 92**, by AU-06 of `define-clinical-acts-foundation` at `c9e3e7a`: `own`, `acknowledge`, `reassign`, `raise`, `return` and `split` over `clinical_inbox_item`, lane `physician` or `nurse`, checked under AU-04. Recording MI-07's closing outcome is not covered (MT-24). |
| MT-18 | Nurse triage. The nurse lane needs a scope that says what a nurse may triage or answer. The foundation defines the `nurse` role (AU-01) but no inbox scope for it. | **Resolved, PROPOSED pending owner decision 92**, by AU-06 at `c9e3e7a`: a `nurse`-lane grant names the nurse-lane scope that the medical director records. |
| MT-19 | Reply authority. A reply to a patient is a clinical communication (MI-12), not an act; the foundation keeps replies as communications (its EN-03) and defines no grant for them. | **Resolved, PROPOSED pending owner decision 92**, by AU-06 at `c9e3e7a`: `reply` over `clinical_communication`, per role and lane, on an AU-03 attestation in force. |
| MT-20 | Clinical-need markers. Recording or withdrawing a continuity exception or a clinically-needed marker (MI-25; ruling 50) is a clinical decision that openPractice applies. The foundation defines no grant for it. | **Resolved, PROPOSED pending owner decision 92**, by AU-06 at `c9e3e7a`: `mark` and `withdraw` over `clinical_need_marker`, recorded only for the `clinician` role. These match MI-25's `mark` and `withdraw`. |
| MT-21 | On-call cover. The inbox's cover roster names an on-call person for every hour, with the medical director as the last fallback (MI-08). The foundation defines no on-call designation. | **Resolved, PROPOSED pending owner decision 92**, by AU-06 at `c9e3e7a`: no on-call designation; the roster is a schedule that names only holders of the lane's `own` grant, and a lapsed grant leaves it at once. The gap a lapse can open is closed in MI-08 (MD-4). |
| MT-22 | Delivery order. The foundation builds AU-01 to AU-05 in its feature (1), together with encounters, notes and signing. The inbox needs only the clinical-authority capability. | **Resolved, PROPOSED pending owner decision 92**, together with the foundation's five-feature plan (its owner decision 85): at `c9e3e7a`, clinical authority (AU-01 to AU-06) is its own feature (1), built ahead of encounters, notes and signing (its CD-41). |
| MT-23 | Consult association and who may read it. MI-24 lets an inbox item show its association with an `ai_consult` record that names the same conversation (`define-ai-authored-clinical-records` AC-01). That change lets only clinicians authorized for the patient's chart, and the medical director, read a consult record (its AC-06, and AC-11 for a quarantined one). An unfiled item has no chart, and its owner need not be authorized for the patient's chart. The shared conversation reference could also tie an unfiled item to a patient, which MI-17 forbids. | **Open, cross-change.** MI-24 fails closed meanwhile: the association shows only on a filed item, only to a reader that change allows, and never resolves or files a patient. The owner confirms, or that change narrows AC-01's association. |
| MT-24 | Closing an item. MI-07 requires a closing outcome recorded by a named human, and MI-06 reports `closed`. AU-06 names `own`, `acknowledge`, `reassign`, `raise`, `return` and `split` over `clinical_inbox_item`, but no action for recording a closing outcome. | **Open.** `define-clinical-acts-foundation` would need to add a closing action, for example `close`, to the `clinical_inbox_item` scope. Meanwhile no item closes except by `return` (MI-15): an answered item stays open and owned, and openChart sends no `closed`. openPractice closes its routing record on `responded` (its ER-07), so no patient-facing path waits on `closed`. |

**Tensions recorded in openChart-spec#4.** `define-ai-authored-clinical-records`, read at `5a9947f`, records three tensions with this change, and this change addresses them: AT-5 by MI-26, whose hold now lasts until Tier 2 is in force for the act type; AT-6 by MI-12's record origins, with MI-20's inertness and MI-24's no-copy rule scoped to inbox items (MD-28); and AT-7 by MD-20, which holds act-like content as communication only on the inbox's own paths and defers to that change on its write path. Their disposition stays with the owner.

## Required companion changes (being drafted elsewhere)

None is drafted in this change. Each is stated at contract level only. Nothing here describes HealthLinc's or medXfactory's internals. HealthLinc and medXfactory each implement `openchart-conversation-retrieval/1.0` at the digest recorded in MI-02 (ruling 69; Decision 14).

**HealthLinc.** The openPractice change names this companion as `opensoft/HealthLinc` change `define-practice-gateway-integration`.

- **H-1. Retrieval under the contract.** HealthLinc implements `openchart-conversation-retrieval/1.0` as the holder `healthlinc`, for every conversation it holds (coach conversations, direct messages to the doctor and administrative threads), over openChart's own authorized integration and never through openPractice. It answers `conversation.retrieve` for a `conversation_ref` with namespace `healthlinc` with `conversation.result`, or refuses with a code from the contract's error set. Each turn carries its `turn_id`, MI-12 author type and source token. The patient's turns are `patient`, coach turns are `ai` with source `healthlinc` (rulings 51 and 54), and a relayed openPractice agent answer has source `openpractice_agent` with its answer type and version or its approver. The result carries `consent_ref` and, where HealthLinc keeps one, the account's openChart reference as `ehr_patient`. It echoes the retrieve's `urgency` and marks the request turns with `request_turn`; for a priority or urgent item, it shares them as `urgent_escalation` with the patient told. Its AI turns may carry `ai_mode`, `disclosure_code`, `model_ref`, `advice_statement_ref` and `emergency_guidance`, and a result may name its `origin_conversation_ref`.
- **H-2. Reply delivery and its failure callback.** HealthLinc declares `reply_delivery` and `delivery_failure_callback` in `capabilities.result`. It accepts `reply.deliver` against `reply_path_ref`, whichever system holds the conversation. It honors `channel_restrictions` and `delivery_scope` `conversation_only` (MD-13), and answers with `message.ack`, idempotently by `message_id`. When a reply it accepted cannot be delivered, it sends `reply.delivery_failed` with one of the six `failure_reason` codes (MI-11, MD-26). Push text carries no PHI, and clinician-authored and AI-authored content are shown distinctly.
- **H-3. Split.** HealthLinc declares `split`. On `split.request`, whose `request_ref` is the handoff's `healthlinc_message_ref`, it splits a mixed item, resubmits only its administrative part to openPractice as a new inquiry, and acknowledges with `message.ack` (MD-7).
- **H-4. Emergency guidance stays in the app.** HealthLinc shows its own emergency guidance for urgent submissions, whether or not openChart or openPractice is available. That includes the guidance ruling 71 attaches to a red flag on its checklist. openChart sends no advice codes.
- **H-5. No clinical messaging without a route.** HealthLinc offers no clinical messaging to a practice with no configured gateway (MI-20).

**medXfactory.** The openPractice change assigns the medical-AI side to `MedxSoft/medXfactory` change `define-care-organization-hermes-openpractice-operations`. medXfactory's change `define-patient-medical-ai-connection` owns the practice-mode framework (ruling 59). Which medXfactory change carries M-1 and M-2 is for medXfactory to state.

- **M-1. Retrieval under the contract.** medXfactory implements `openchart-conversation-retrieval/1.0` as the holder `medxfactory`, over openChart's own authorized integration and never through openPractice. It answers `conversation.retrieve` for a `conversation_ref` with namespace `medxfactory`. Its medical AI's turns are `ai` with source `medxfactory`, and the patient's and representative's turns are `patient` and `representative`. The result carries `consent_ref`, and a `snapshot_ref` that lets openChart record which exchange the clinician saw. Like every holder, medXfactory echoes the `urgency`, marks the request turns, and shares them as `urgent_escalation` with the patient told for a priority or urgent item. It may give each AI turn's mode, disclosure, model, advice statement and emergency-guidance codes, and name the conversation the exchange began from. medXfactory need declare no optional capability, since replies go through HealthLinc (MD-16). medXfactory has dropped its own retrieval contract and will implement this one.
- **M-2. Records through MedxEHR.** medXfactory sends the medical AI's records to MedxEHR, which relays them to openChart with receipts. medXfactory does not write to openChart directly, and nothing passes through openPractice (ruling 70, refining ruling 53). On openChart's side, that write path belongs to `define-ai-authored-clinical-records` (Open Question 4). How the relay identifies an openChart patient without a master identity is for the changes that own it (MT-12).

## Related changes being drafted (rulings 64, 65 and 70)

- **`opensoft/openChart-spec` change `define-ai-authored-clinical-records`** (openChart-spec#4), being drafted on branch `change/define-ai-authored-clinical-records`, and read here at `5a9947f` and again at `083aef3`, where its AC-11 keeps a consult refused at the grant checks as a quarantined `ai_consult` record (MI-12; MT-23). It takes the place of this change's former "required later practice-mode change". The limited-practice and full-practice modes of ruling 59 are not buildable in openChart until the conditions of its AA-01 hold, and MI-26 holds AI-authored content as communication until its Tier 2 is in force for the act type. Its consult records are clinical communication records of origin `ai_consult` (MI-12, MD-28). It references this change's clinical-communication record (MI-12) rather than defining a second one. It also owns the chart's own record of the medical director's authorization and the check of every AI write against it (ruling 65), and the write path by which MedxEHR relays the medical AI's records to openChart (ruling 70).
- **`opensoft/openChart-spec` change `define-clinical-acts-foundation`** (openChart-spec#5), being drafted. `define-ai-authored-clinical-records` names it as the required prerequisite of its Tier 2 (its AA-01). Read here at `c9e3e7a`, its clinical-authority capability (AU-01 to AU-06), built as its own feature (1), is also the inbox's single source of clinical roles, the medical director and grants (Decision 15), and a prerequisite of the inbox (MD-31). Its AU-06, PROPOSED pending owner decision 92, carries the inbox's scopes and resolves MT-17 to MT-22. MT-24 asks it for one more action.
- **MedxEHR-spec change `define-medical-ai-record-overlay`**, being drafted. It is the MedxEHR-side counterpart named in ruling 64.

This change states nothing else about these changes' content beyond those rulings and the identifiers cited here.

## Risks / Trade-offs

- **[A missed urgent message]** → A named owner from acceptance. Escalation to the on-call clinician and then the medical director, with repeated alerts. No rejection on identity grounds. `content_unavailable` and `clock_expired` sent at once, so openPractice's fallback runs on time. An expired item stays queued and visible by routing id. `priority` items with identity problems are escalated like urgent ones. A clinician's raise reaches openPractice. A failed urgent delivery reopens the item.
- **[Wrong-patient filing]** → Resolution only through links, no demographic matching, unfiled items, and `unlinked_identity` (three snapshot fields) shown as unverified and never matched.
- **[Clinical content leaks into openPractice]** → Reference-only handoff. Markers carry no reason. No administrative text is sent. Splits go through HealthLinc. The medical AI's records travel through MedxEHR's relay (ruling 70).
- **[AI text mistaken for a clinician's]** → An author type and a named source on every piece of content (MI-12). No AI drafting, and no agent action.
- **[An AI-authored order or prescription acted on]** → In an inbox item, MI-26 holds it as communication, marked as not accepted as a clinical act, until Tier 2 of `define-ai-authored-clinical-records` is in force for its act type. On that change's write path, its AA-01 refuses every act write meanwhile (MD-20, MT-14).
- **[Double alerts]** → openChart's escalation and openPractice's tracked alerts can both fire for one item. This is accepted for safety.
- **[Two clock policies drift]** → The earlier deadline governs (MT-4).
- **[Unfiled records accumulate]** → They are listed for identity review. Manual filing is Open Question 7.
- **[Confidentiality breach through notifications]** → PL-16 restriction codes go to HealthLinc. An unfiled item's reply stays in the conversation.
- **[A clinically relevant turn withheld under consent]** → Every result carries the request turn, and a priority or urgent item's request turns are always shared; a result without them is a failed retrieval, reported as `content_unavailable` (MD-29). Other withheld turns show as a partial view with their count (MD-25). Residual risk, recorded as MT-16.
- **[A holder's capability lapses]** → openChart sends nothing a holder has not declared, keeps every item owned, and tells the owner and the medical director (MD-23).
- **[No live inbox without AU-06]** → The inbox fails closed: it cannot be enabled until `define-clinical-acts-foundation`'s feature (1) is built with AU-06 in force, PROPOSED pending owner decision 92 (MD-31), so openPractice routes no clinical item to it.
- **[A grant lapse empties a roster slot]** → MI-08's warnings, alerts and fallbacks keep a human reaching every item, and no offer is accepted without a named owner (MD-4).
- **[Contract drift]** → The digest pins, and tasks 1.3 and 1.5.
- **[No constitution]** → The plan phase is blocked until a constitution is adopted.

## Migration Plan

1. Validate strictly. Ratify `define-openpractice-boundary` first or together. Brett Heap stamps `Ratified by` and sets `Status: ratified`.
2. Adopt openChart's constitution through separate governance.
3. Wait for the openPractice change to be ratified and to match the pin at `0a82fc2` by digest.
4. Wait for the HealthLinc companion change, which implements the retrieval contract at its recorded digest, for the medXfactory companion before any medXfactory retrieval, and for `define-clinical-acts-foundation`'s feature (1), clinical authority (AU-01 to AU-06), with AU-06's inbox scopes accepted under owner decision 92.
5. Create the single Spec Kit feature from the assembly root. Implement against an openPractice double and retrieval-contract doubles, alongside the standalone regression suite.
6. Enable the inbox only with full cover and HealthLinc's three declared capabilities, plus medXfactory retrieval where the practice uses its medical AI. openPractice enables clinical routing afterwards.
7. Rollback: openPractice disables clinical routing first. openChart then disables the inbox, which withdraws the handoff authorization. Open items stay owned until they close, and no record is deleted.

## Open Questions

Each question is routed in `tasks.md` §2 to the gate it blocks.

1. **Constitution adoption.** openChart's constitution is the unfilled template. This blocks the plan phase.
2. **Owner dispositions** of MT-3 to MT-10, MT-12, MT-15, MT-16, MT-23 and MT-24, of MD-1 to MD-33, and of owner decision 92 on `define-clinical-acts-foundation`'s AU-06. These block ratification.
3. **openChart's HealthLinc link contract (ruling 39).** Which governed openChart change defines it? This blocks live HealthLinc retrieval.
4. **openChart's receiving side of MedxEHR's relay of the medical AI's records (ruling 70).** Answered by ruling 70: it belongs to `define-ai-authored-clinical-records`. It blocks nothing in the inbox.
5. **A patient with no EB-01 link** (openPractice Open Question 5). Answered by ER-06, unchanged at `0a82fc2`, and by MI-18 (MT-2). A `routine` item stays an office-manager exception.
6. **Clinical messaging in an openChart-only deployment.** The owner decides. Meanwhile there is none (MI-20).
7. **Manual filing of an unfiled item** by a named human. The owner and the medical director decide. Meanwhile, filing happens only through a resolved link.
8. **Lane policy and nurse scope.** The medical director decides, with counsel on scope of practice, and records the nurse-lane scope under AU-06 of `define-clinical-acts-foundation`. Meanwhile, every item enters the physician lane.
9. **Response windows.** The medical director decides. Meanwhile, the offer's deadlines apply.
10. **Retention** of clinical-communication records and returned items, and whether openChart keeps an audit copy, outside the chart, of a medXfactory exchange the clinician saw (MD-17). The owner and counsel decide. Meanwhile, nothing is deleted and no copy is kept.
11. **Billability of clinician replies.** This waits for a clinical-encounter capability (`define-openpractice-boundary` Open Question 2). Meanwhile, nothing is billable. `define-clinical-acts-foundation` proposes an answer (its CD-29).
12. **A representative's scope** (openPractice Open Question 2). Counsel decides. openChart shows the submitter kind as reported.
13. **`closed` without `responded`.** Does it satisfy openPractice ER-07's shadow deadline? The openPractice change confirms.
14. **Splitting a medXfactory-held mixed conversation.** MI-16 sends the split request to HealthLinc. The owner, or the openPractice change, decides who splits a conversation that medXfactory holds.
15. **A clinician's raise after `closed`.** Does openPractice accept `handoff.clinician_urgency_raised` for a routing record it has closed (MD-9)? The openPractice change confirms.
