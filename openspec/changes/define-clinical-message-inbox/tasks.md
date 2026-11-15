## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-clinical-message-inbox --strict` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The 2026-11-14 rulings recorded in `design.md` are not ratification. `define-openpractice-boundary`, on which this change is stacked, is ratified first or in the same act. No Spec Kit feature is created before this task is complete.
- [ ] 1.3 Compare this change with `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation` (on `opensoft/openPractice-spec` `main` at `0a82fc2`, still draft and unratified) on these points:
  - the schema digest in MI-02 against `sha256sum -c contracts/SHA256SUMS` at the compared revision;
  - the contract identifier `openpractice-clinical-handoff/1.0`, its message set, its reject codes and its status codes;
  - the namespaces `healthlinc`, `openpractice` and `openchart`, and the issuer handling;
  - `conversation_source` and `conversation_ref` (ruling 51), and `clinical_need.marker` with its `origin_not_verified` rejection (openPractice ER-18);
  - `identity_state`, `unlinked_identity` (`legal_name`, `birth_date`, `administrative_sex`), `handoff.clinician_urgency_raised`, the `coach_triage` and `medical_ai_triage` sources, and the optional `link_id` for an unlinked handoff, all as pinned at `0a82fc2`;
  - the urgency source `patient_checklist` (ruling 71), as pinned at `0a82fc2`, recorded as `patient` (MI-12);
  - ER-06 and ER-03 at the compared revision, against MI-18 and MI-10.

  Record both revisions and each digest pair. A mismatch blocks the handoff. When that change's schema changes, update MI-02's pin in a governed revision of this change.
- [ ] 1.4 Record Brett Heap's disposition of tensions MT-3 to MT-10, MT-12, MT-15 and MT-16, and of design calls MD-1 to MD-30. MT-1, MT-2, MT-11 and MT-13 are resolved by the openPractice change's text as it stands at `0a82fc2`, and MT-14 by ruling 67; record that confirmation. Where a disposition needs an amendment elsewhere, name the change that must carry it: the openPractice change for MT-5, MT-6 and MT-15, and `define-openpractice-boundary` for MT-3 (the follow-up the openPractice change's T-11 proposes). Otherwise this change yields. Record also that tensions AT-5, AT-6 and AT-7 of openChart-spec#4 are addressed here, by MI-26, by MI-12 with MD-28, and by MD-20.
- [ ] 1.5 Run `sha256sum -c contracts/SHA256SUMS` in this change's directory, and confirm that the digest of `openchart-conversation-retrieval-1.0.schema.json` matches MI-02. Compare it with the digest that each implementing change records: the HealthLinc companion (H-1 to H-3) and the medXfactory companion (M-1). A mismatch blocks interoperation with that holder. Any change to the retrieval schema is a governed revision of this change that records the new digest in MI-02 and in `contracts/SHA256SUMS`.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before the plan phase. This gate blocks the plan phase.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 The openPractice change is ratified and matches by digest (task 1.3). This gate blocks live interoperation only; the feature may build against an openPractice double.
- [ ] 2.4 The HealthLinc companion change (items H-1 to H-5 in `design.md`), which implements `openchart-conversation-retrieval/1.0`, is ratified. Open Question 3: record which openChart change defines openChart's HealthLinc link contract (ruling 39). This gate blocks enabling the inbox live.
- [ ] 2.5 The medXfactory companion change (items M-1 and M-2) is ratified. This gate blocks medXfactory retrieval only. Open Question 4 is answered by ruling 70: openChart's receiving side of MedxEHR's relay belongs to `define-ai-authored-clinical-records` (task 2.7).
- [ ] 2.6 Open Questions 5 to 14 are routed to their owners as `design.md` states. Each fails closed meanwhile, so none blocks the build.
- [ ] 2.7 Track openChart-spec change `define-ai-authored-clinical-records`, which is being drafted under ruling 64, with MedxEHR-spec change `define-medical-ai-record-overlay`. This gate blocks only the limited-practice and full-practice modes of ruling 59, which are not buildable in openChart until the conditions of that change's AA-01 hold, among them `define-clinical-acts-foundation` (openChart-spec#5) ratified and built. MI-26 applies until Tier 2 is in force for the act type. Confirm that the change references MI-12, with origin `ai_consult`, rather than defining a second clinical-communication record. Confirm also that it carries the chart's own record of the medical director's authorization and the check of AI writes against it (ruling 65), and openChart's side of MedxEHR's relay (ruling 70).

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-clinical-message-inbox` from the assembly root. Record immutable two-way links between the feature and this change.
- [ ] 3.2 Verify that the feature maps every requirement (MI-01 to MI-26) and every scenario to executable tasks, without copying them here. The plan must decide these points:
  - the name and scope of the integration role;
  - the storage shape of the clinical-communication record;
  - the clinician, nurse and medical-director roles;
  - the cover roster;
  - the reuse of the durable outbound store of PL-14;
  - the retrieval-contract client, and the record of each holder's declared capabilities.

## 4. openChart Realization

- [ ] 4.1 Complete the linked feature. Contract tests validate every handoff and retrieval message against its canonical schema at the digest recorded in MI-02, and run against an openPractice double and a retrieval-contract double for each holder.
- [ ] 4.2 Attach evidence for each of these:
  - a standalone installation passes the golden-intake round trip with the inbox unconfigured;
  - no urgent item is rejected, dropped or left unowned in any identity case, when content is unavailable, or when nobody is on call;
  - an inbox with an uncovered hour cannot be enabled;
  - urgency is never lowered, and no deadline is ever extended;
  - no PHI appears in logs, notifications, diagnostics or keys;
  - no financial status is requested or stored, and openChart keeps no administrative queue;
  - AI-authored content is never shown as clinician-authored, and its source is named; a patient's turn is never shown as AI content; a clinician claim without a matching reply is shown as `unknown`;
  - no message is sent for a capability a holder has not declared;
  - every retrieval result carries the request turn; a priority or urgent item's request turns are shared with the patient told; a result without them is a failed retrieval, reported as `content_unavailable`; and a view that the patient's consent leaves partial is shown as partial, with its count;
  - an AI turn's mode, disclosure, model and advice statement are shown when given, and shown as not stated when absent;
  - no medical-AI exchange is filed through the inbox;
  - an AI-authored order, prescription or diagnosis in an inbox item is held as communication, and creates no clinical act;
  - the inbox's inertness and MI-24's no-copy rule apply to inbox items only, never to an `ai_consult` record;
  - a `priority` offer is never rejected for identity, `unlinked_identity` is never matched or filed, and no message about an `unlinked` handoff carries a `link_id`;
  - a clinician's raise is sent as `handoff.clinician_urgency_raised`, and a failed delivery reopens its item, escalating it when it is urgent;
  - no billable fact or statement comes from an item;
  - all fixtures are synthetic.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision, and the supported version of each contract (MAJOR 1 and the declared MINOR), to openPractice and to each holder.
- [ ] 5.2 Land the code and spec leg pull requests and the assembly root pin bump. Then archive this change and promote the capability, after re-running strict validation on the final revision.
