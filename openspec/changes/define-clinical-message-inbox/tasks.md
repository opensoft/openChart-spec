## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-clinical-message-inbox --strict` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The 2026-11-14 rulings recorded in `design.md` are not ratification. `define-openpractice-boundary`, on which this change is stacked, is ratified first or in the same act. No Spec Kit feature is created before this task is complete.
- [ ] 1.3 Compare this change with `opensoft/openPractice-spec` change `define-patient-gateway-and-escalation` (PR #6, not yet on main) on these points:
  - the schema digest in MI-02 against `sha256sum -c contracts/SHA256SUMS` at the compared revision;
  - the contract identifier `openpractice-clinical-handoff/1.0`, its message set, its reject codes and its status codes;
  - the namespaces `healthlinc`, `openpractice` and `openchart`, and the issuer handling;
  - the conversation-source field (ruling 51) and the clinician-decision channel (ruling 50 and the payment-hold marker), once that change's next revision adds them.

  Record both revisions and each digest pair. A mismatch blocks the handoff. When that change's schema changes, update MI-02's pin in a governed revision of this change.
- [ ] 1.4 Record Brett Heap's disposition of tensions MT-1 to MT-14 and design calls MD-1 to MD-20. Where a disposition needs an amendment elsewhere, name the change that must carry it: the openPractice change for MT-1, MT-2, MT-5, MT-6, MT-11 and MT-13; `define-openpractice-boundary` for MT-3; and medXfactory's `define-patient-medical-ai-connection` for MT-14. Otherwise this change yields.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before the plan phase. This gate blocks the plan phase.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 The openPractice change is ratified and matches by digest (task 1.3). This gate blocks live interoperation only; the feature may build against an openPractice double.
- [ ] 2.4 The HealthLinc companion change (items H-1 to H-5 in `design.md`) is ratified. Open Question 3: record which openChart change defines openChart's HealthLinc link contract (ruling 39). This gate blocks enabling the inbox live.
- [ ] 2.5 The medXfactory companion change (items M-1 and M-2) is ratified. Open Question 4: record which openChart change defines openChart's receiving side of medXfactory's governed chart path (ruling 53). This gate blocks medXfactory retrieval only.
- [ ] 2.6 Open Questions 5 to 14 are routed to their owners as `design.md` states. Each fails closed meanwhile, so none blocks the build.
- [ ] 2.7 Record the separately governed openChart change for AI practice modes (ruling 59; items P-1 and P-2 in `design.md`). It is required and not drafted here. This gate blocks only the limited-practice and full-practice modes, which are not buildable in openChart until it is ratified. MI-26 applies meanwhile.

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-clinical-message-inbox` from the assembly root. Record immutable two-way links between the feature and this change.
- [ ] 3.2 Verify that the feature maps every requirement (MI-01 to MI-26) and every scenario to executable tasks, without copying them here. The plan must decide these points:
  - the name and scope of the integration role;
  - the storage shape of the clinical-communication record;
  - the clinician, nurse and medical-director roles;
  - the cover roster;
  - the reuse of the durable outbound store of PL-14.

## 4. openChart Realization

- [ ] 4.1 Complete the linked feature. Contract tests validate every handoff message against the canonical schema at the digest recorded in MI-02, and run against an openPractice double and a double for each conversation source system.
- [ ] 4.2 Attach evidence for each of these:
  - a standalone installation passes the golden-intake round trip with the inbox unconfigured;
  - no urgent item is rejected, dropped or left unowned in any identity case, when content is unavailable, or when nobody is on call;
  - an inbox with an uncovered hour cannot be enabled;
  - urgency is never lowered, and no deadline is ever extended;
  - no PHI appears in logs, notifications, diagnostics or keys;
  - no financial status is requested or stored, and openChart keeps no administrative queue;
  - AI-authored content is never shown as clinician-authored, and its source system is named;
  - no medical-AI exchange is filed through the inbox;
  - an AI-authored order, prescription or diagnosis is held as communication, and creates no clinical act;
  - no billable fact or statement comes from an item;
  - all fixtures are synthetic.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision, and the supported contract version (MAJOR 1 and the declared MINOR), to openPractice.
- [ ] 5.2 Land the code and spec leg pull requests and the assembly root pin bump. Then archive this change and promote the capability, after re-running strict validation on the final revision.
