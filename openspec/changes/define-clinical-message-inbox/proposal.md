code_surface: openChart (the open_chart Frappe application in opensoft/openChart-code). In scope: a clinical message inbox that receives `openpractice-clinical-handoff/1.0` offers from openPractice, validated against openPractice's canonical schema pinned by path and digest; acknowledgment of every offer; ownership of the queue and the response clock; named owners in physician and nurse lanes, with reassignment, absence and on-call cover; escalation of unacknowledged urgent items to the on-call clinician and then the medical director; retrieval of the escalated conversation by reference from the system that holds it (HealthLinc for a coach conversation, medXfactory for a medical-AI conversation); the clinician's reply to the patient through HealthLinc; one canonical clinical-communication record (MI-12) with author type, source system and provenance, never a diagnosis or clinical fact of record; re-routing of administrative and mixed items; identity resolution through existing links only, with identity review; clinicians' clinical-need markers (`messaging_continuity`, `appointment_needed`) sent to openPractice as `clinical_need.marker`; and status reports to openPractice over PL-14's durable outbound delivery. Out of scope: billing, payment-hold or financial status; any administrative work queue; encounters, diagnoses, procedures or billable facts (CF-06 is unchanged); AI drafting of clinical replies; AI-authored orders, prescriptions or diagnoses, and the limited-practice and full-practice modes of ruling 59 (openChart-spec change `define-ai-authored-clinical-records`, being drafted under ruling 64; until it is ratified, AI-authored content in the chart is communication only, MI-26); HealthLinc's and medXfactory's internals; openChart's link contract with HealthLinc and its receiving side of medXfactory's governed chart path (Open Questions 3 and 4); and any change to the ratified `expanded-patient-intake` requirements.
target_release: openPractice gateway v1 (clinical routing). The change archives when a landed, validator-green open_chart revision meets three conditions. First, it passes contract tests for every handoff message against an openPractice double at the recorded schema digest, and for retrieval, reply and split requests against a double for each conversation source system. Second, it still passes the standalone golden-intake round trip with no openPractice, HealthLinc or medXfactory configured. Third, it reports no billable facts.
Status: draft
Ratified by: pending. The decisions encoded here rest on rulings that Brett Heap made on 2026-11-14 for the openPractice patient gateway (companion change `opensoft/openPractice-spec` `define-patient-gateway-and-escalation`, PR #6, not yet on main). They are recorded in `design.md` under "Owner rulings (2026-11-14)". Rulings are not ratification. The design calls in `design.md` are proposed, not ruled. Ratification still requires Brett Heap to stamp this line and change `Status` to `ratified`. This artifact was drafted by an agent.

## Why

openPractice is becoming the patient app's gateway and router (ruling 34). Clinical questions go to openChart, the doctor's clinical interface, where the doctor reads and answers them. openPractice keeps only a routing record, with no clinical content.

HealthLinc is the patient's gateway to their doctor (ruling 51). Through it, the patient can reach their human doctor, through openPractice to openChart, or medXfactory's medical AI. HealthLinc's own in-app AI is a coach that gives general information only (rulings 51 and 54). The medical AI's exchanges reach the chart through medXfactory's own governed path, never through openPractice (ruling 53).

The openPractice side is `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation`, PR #6, not yet on main. Its capability `escalation-routing` (ER-01 to ER-17) defines the reference-only contract `openpractice-clinical-handoff/1.0`. Its design lists an openChart clinical message inbox as a required companion change, and ruling 47 asked for this change to be drafted.

openChart has no inbox today. Its built DocTypes are `OC Patient`, `OC Patient External Identifier`, `OC Intake Submission` and eight patient-reported statement families. None holds a message, a clinician-authored record or a clinical work queue.

This change specifies openChart's half of the handoff contract. It reuses every message and code in openPractice's canonical schema, pinned by digest, and defines no message of its own toward openPractice. It also states, at contract level, what openChart needs from HealthLinc and from medXfactory.

## What Changes

- **Inbox and contract.** openChart receives routed clinical items under `openpractice-clinical-handoff/1.0`, from a dedicated integration role. It validates every message against the canonical schema, pinned by path and SHA-256 digest at the openPractice change's revision `097278c` (MI-01, MI-02).
- **Content by reference.** openChart fetches the escalated conversation by `conversation_ref` from the system `conversation_source` names: HealthLinc for a coach conversation, or medXfactory for a medical-AI conversation. It never fetches content from openPractice. When retrieval fails, the item stays open and owned, and openChart reports `content_unavailable` (MI-03).
- **Acknowledgment and clock.** openChart acknowledges every offer, idempotently. It owns the queue and the response clock (ruling 43), with windows from an openChart policy that the medical director approves. Until one is approved, openChart uses the offer's own deadlines; openPractice's proposed defaults are not adopted as facts. No deadline is ever extended (MI-04, MI-05).
- **Status back to openPractice.** openChart reports `responded`, `clock_expired`, `returned_not_clinical`, `content_unavailable` and `closed` through the durable outbound delivery of PL-14 (MI-06).
- **Ownership and cover.** Every item has one named clinician or nurse owner, in a physician or nurse lane. Reassignment, absence and on-call cover keep it owned. An unacknowledged urgent item escalates to the on-call clinician and then to the medical director. No agent acts in the inbox (MI-07 to MI-09).
- **Urgency.** openChart never lowers urgency. It applies `handoff.urgency_raised` and moves deadlines only earlier (MI-10).
- **Reply and record.** The clinician's reply goes to the patient through HealthLinc. MI-12 is the single, citable definition of a clinical communication record. It gives each piece of content an author type (patient, AI or clinician, among others, with `unknown` as a fail-safe that is never clinician-authored), and an AI author names its source: HealthLinc's coach or medXfactory's medical AI. It records provenance, and it rules that a clinical communication is never a diagnosis or a clinical fact of record. AI-authored and clinician-authored content are always distinguishable. Patient-reported and AI text never becomes a diagnosis, a clinical fact or a billable fact. A medical-AI exchange reaches the chart only through medXfactory's governed path, so the inbox keeps it by reference only (MI-11 to MI-14, MI-24).
- **Re-routing.** A clinician returns an administrative item without answering it. A mixed item is split through HealthLinc, and only its clinical part is answered. openChart keeps no administrative queue (MI-15, MI-16).
- **Identity.** A handoff resolves the patient only through the links that exist (ruling 39; PL-02, PL-03). There is no matching, and no Medx or medXfactory reference is used. An unresolved identity goes to identity review. A non-urgent offer is rejected with the schema's code. An urgent item is accepted unfiled, with the uncertainty shown, and still reaches a clinician (MI-17, MI-18).
- **Boundaries.** openChart receives no billing, payment-hold or financial status (ruling 41). It still operates without openPractice, and with no gateway configured the inbox is inert (MI-19, MI-20).
- **Clinical-need markers.** A named clinician can record and withdraw a `messaging_continuity` marker (ruling 50) or an `appointment_needed` marker. openChart attributes it and sends it to openPractice as `clinical_need.marker`, as codes only: a `need_id`, mark or withdraw, `valid_until`, and an origin, with the urgent handoff's id for an `urgent_escalation` origin (MI-25).
- **AI practice modes.** The medical director sets medXfactory's AI to advice only, limited practice or full practice (ruling 59); medXfactory's change owns that framework (rulings 56 to 58). This change does not cover AI-authored orders, prescriptions or diagnoses. openChart-spec change `define-ai-authored-clinical-records` is being drafted for them, with MedxEHR-spec change `define-medical-ai-record-overlay` (ruling 64). Ruling 59 stands, so until that change is ratified, AI-authored content that reaches the chart is communication only, with its source named. An AI-authored order, prescription or diagnosis is held as communication and creates no clinical act. The limited-practice and full-practice modes are not buildable in openChart until then (MI-26).
- **Safety.** No PHI in logs, errors, notifications, diagnostics or keys. Replies honor confidential-communication instructions (PL-16). Contract tests cover the boundary (MI-21 to MI-23).

## Capabilities

### New Capabilities

- `clinical-message-inbox` (MI-01 to MI-26): openChart's side of `openpractice-clinical-handoff/1.0`, its retrieval and reply needs toward HealthLinc and medXfactory, and the clinical queue behind them.

### Modified Capabilities

None. The ratified `expanded-patient-intake` requirements are cited and left unchanged.

## Required companion changes (being drafted elsewhere)

Both are stated at contract level in `design.md`. Neither is drafted in this change; each is being drafted in its own repository (rulings 47 to 49 and 55).

- **HealthLinc, `opensoft/HealthLinc` change `define-practice-gateway-integration` (H-1 to H-5):**
  - conversation retrieval by reference, with an author type on every turn;
  - reply delivery against the reply-path reference, honoring coded channel restrictions;
  - a split-and-resubmit request for mixed items;
  - emergency guidance that stays in the app, whatever openChart's or openPractice's availability;
  - no clinical messaging where no route exists.
- **medXfactory, `MedxSoft/medXfactory` (M-1, M-2; see `design.md` for the change ids):**
  - conversation retrieval by reference for medical-AI conversations, with the source named;
  - its governed path for recording medical-AI exchanges in the chart (ruling 53), never through openPractice.

## Related changes being drafted (ruling 64)

- **`opensoft/openChart-spec` change `define-ai-authored-clinical-records`**, being drafted by a separate author. It replaces this change's former item for a "required later practice-mode change". The limited-practice and full-practice modes of ruling 59 are not buildable in openChart until it is ratified. It references this change's clinical-communication record (MI-12) rather than defining a second one.
- **MedxEHR-spec change `define-medical-ai-record-overlay`**, being drafted, on the MedxEHR side.

This change states nothing else about either change's content.

## Impact

- **openChart:**
  - a new clinical-communication record and inbox;
  - a dedicated integration role;
  - an openChart response policy and lane policy, approved by the medical director;
  - a cover roster;
  - attributed clinical-need markers;
  - reuse of the durable outbound store of PL-14;
  - retrieval clients for each conversation source.
- **Dependencies:**
  - This branch is stacked on the draft change `define-openpractice-boundary`, and cites PL-01 to PL-16 and CF-02, CF-05 and CF-06. This change can be ratified only with or after it.
  - `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation` (PR #6, not yet on main) owns the handoff contract and schema, pinned here at revision `097278c`.
  - The HealthLinc and medXfactory companion changes are required. They are being drafted in their own repositories, and none is on main.
- **Governance:** openChart's constitution is still the unfilled template. A Constitution Check, and with it the plan phase, needs a constitution adopted through separate governance first.
- **Safety:** synthetic fixtures only; no PHI in logs or notifications; no clinical or autonomous decision by any agent or rule; no billing or financial data.
- **Tensions:** fourteen are recorded in `design.md` as MT-1 to MT-14. MT-11 and MT-13 were resolved by the re-pin to `097278c`. The other twelve are conflicts or mismatches with the openPractice change, with `define-openpractice-boundary` and with medXfactory's mode framework, and one of them is a possible conflict with ratified openChart text (MT-10). Each of the twelve needs the owner's disposition.
