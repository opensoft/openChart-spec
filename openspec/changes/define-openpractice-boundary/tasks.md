## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-openpractice-boundary --strict` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The 2026-11-14 and 2026-11-15 rulings recorded in `design.md` are not ratification. No Spec Kit feature is created before this task is complete.
- [ ] 1.3 Compare this change with `opensoft/openPractice-spec` change `define-mvp-practice-foundation` on four things:
  - the canonical schema digests cited in PL-04 against that change's `contracts/SHA256SUMS`;
  - the contract identifiers `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0`;
  - the namespaces `openpractice` and `openchart`;
  - the issuer requirements: PL-03 here against EB-02 there.

  Record both revisions and each digest pair. A mismatch blocks the handoff.
- [ ] 1.4 When the follow-up change of ruling 93 lands in `opensoft/openPractice-spec`, re-pin `openpractice-ehr-clinical-facts/1.0` in PL-04 to its revision and digest, and adopt its retraction reason code in CF-04 (ruling 89). Until then the recorded pin stands, and a retraction carries no reason code.
- [ ] 1.5 Obtain Brett Heap's disposition of the ⚑ design calls in `design.md` ("Design calls for owner review"): established links (PL-02, PL-07 to PL-10, PL-16), instructions from a link that has never been established (PL-16), and confirming such a link (PL-06). For the last, also record whether `define-mvp-practice-foundation` extends EB-08's resume rule to every `confirmed` resolution. Compare them with any matching rule that `define-mvp-practice-foundation` adopts for a correction request arriving through a link in review (its EB-09).

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before the plan phase. This gate blocks the plan phase.
- [ ] 2.2 Open Question 2: record which separately governed change introduces clinician-authored encounters, diagnoses and procedures. Until it lands, CF-06 applies: the capability result is false and reads return `no_billable_facts`. This gate blocks billable publication only.
- [ ] 2.3 Open Question 3: closed by ruling 31 (openPractice owns the administrative appointment; openChart owns the encounter). Verify that this change still carries no appointment operations, which wait for a later MINOR version.

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-openpractice-boundary` from the assembly root. It covers both capabilities. Record immutable two-way links between the feature and this change.
- [ ] 3.2 Verify that the feature maps every requirement (PL-01 to PL-16 and CF-01 to CF-06) and every scenario to executable tasks, without copying them here. The plan names and scopes the dedicated integration role (ruling 18), and chooses the durable outbound mechanism (PL-14).

## 4. openChart Realization

- [ ] 4.1 Complete the linked feature. Contract tests validate every message against the canonical schemas at the recorded digests, and run against an openPractice double. The feature covers:
  - issuer configuration and digest-pinned schema validation;
  - the dedicated integration role;
  - the deterministic "agree" check and the namespace-aware identity decision;
  - single-resolver review and revocation;
  - the version store and projection;
  - the date-of-birth suspension;
  - edit refusal and correction requests, through established links only;
  - durable outbound delivery;
  - the publication surface reporting no billable facts.
- [ ] 4.2 Attach evidence for each of these:
  - standalone installation, with the golden-intake round trip and no openPractice;
  - conflicts go to review and never merge;
  - case 2 is never confirmed;
  - a suspended link applies only the latest held version;
  - edits to the projected fields of a patient with an established link are refused and routed;
  - a link that has never been established refuses no edit, sends no correction request, applies and projects nothing, and gives no communication instructions;
  - no PHI appears in logs or reasons;
  - no patient-reported statement is published as a diagnosis;
  - no billing, coverage or guarantor data is stored;
  - all fixtures are synthetic.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision and the supported contract versions (MAJOR 1) to openPractice.
- [ ] 5.2 Land the code and spec leg pull requests and the assembly root pin bump. Then archive this change and promote both capabilities, after re-running strict validation on the final revision.
