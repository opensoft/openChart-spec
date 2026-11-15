## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-clinical-acts-foundation --strict --no-interactive` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 In this change's `contracts/` directory, run `sha256sum -c SHA256SUMS` and `python3 -I selftest.py`. The self-test needs `jsonschema` 4.18 or later. All 9 valid fixtures must validate, and all 15 invalid fixtures must fail, each for the reason stated in `examples/expected-failures.json`. Record both outputs.
- [ ] 1.3 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The rulings recorded in `design.md` are not ratification. No Spec Kit feature is created before this task is complete.
- [ ] 1.4 Record Brett Heap's disposition of tensions CT-1 to CT-16 (CT-10 is resolved) and design calls CD-1 to CD-36, including owner decision 87 (CD-33). Where a disposition needs an amendment elsewhere, name the change that must carry it:
  - `define-ai-authored-clinical-records` for CT-6, CT-7, CT-8 and CT-9;
  - `define-clinical-message-inbox` for CT-9;
  - `opensoft/openPractice-spec` `define-mvp-practice-foundation` for CT-11 and CT-16;
  - `define-openpractice-boundary` for CT-13 and CT-15.

  If the owner reads CT-1 as governing every openChart API, add a MODIFIED delta to `expanded-patient-intake` in this change before ratification.
- [ ] 1.5 Compare this change with each dependent draft, and record both revisions for each comparison. A mismatch blocks the handoff of the affected feature.
  - **`define-openpractice-boundary`:** the clinical-facts schema digest `6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec` (PL-04), against `sha256sum -c contracts/SHA256SUMS` in `opensoft/openPractice-spec` `define-mvp-practice-foundation` at the compared revision.
  - **`define-ai-authored-clinical-records`:** its twelve minimum contents, against the table in `design.md`.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before planning. This gate blocks planning for every feature.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 `define-openpractice-boundary` is ratified, and its publication surface and durable outbound store (PL-14) are built. This gate blocks live publication in feature (2) only; feature (2) may build against an openPractice double.
- [ ] 2.4 **`define-prescribing-safety-checks` is ratified (owner ruling 74).** It is being drafted under ruling 75, with the minimum contents listed in `design.md`. This gate blocks feature (4) entirely: no task of feature (4) may start before it is met. Even after it is met, RX-02 refuses every prescription signature in any deployment where that change's gate is not met.
- [ ] 2.5 Open Questions 3 to 7 are routed as `design.md` states: counsel for Open Questions 3 and 4, planning for Open Question 5, the boundary change for Open Question 6, and the owner for Open Question 7. Each fails closed meanwhile (CD-27, CD-17, CD-20, and no deletion), so none blocks features (1) to (3).

## 3. Spec Kit Handoff (ordered features; CD-31)

Each feature is created from the assembly root only after task 1.3, and only after the feature before it has landed. Record immutable two-way links between each feature and this change. Each feature maps its requirements and every scenario to executable tasks, without copying them here.

- [ ] 3.1 **Feature (1): encounter, note and signing.** It covers CA-01 to CA-15, AU-01 to AU-05 and EN-01 to EN-06. The plan must decide:
  - the storage of acts, versions, signatures, lifecycle events and audit;
  - the extension of the versioned service boundary;
  - the re-authentication mechanism (CD-10);
  - the administrative role that designates the medical director (Open Question 5);
  - the grant, attestation and act-type registry stores;
  - the code-set import record.
- [ ] 3.2 **Feature (2): diagnoses, procedures and publication to openPractice.** It covers DX-01 to DX-03 and PB-01 to PB-05. Depends on feature (1). Live publication also needs task 2.3.
- [ ] 3.3 **Feature (3): orders.** It covers OR-01 to OR-04. Depends on feature (1).
- [ ] 3.4 **Feature (4): prescriptions.** It covers RX-01 to RX-04. **Depends on feature (1) and on task 2.4**, the ratification of `define-prescribing-safety-checks` (ruling 74). Its signing path calls that change's gate decision.

## 4. openChart Realization

- [ ] 4.1 Complete each linked feature in order. Contract tests validate every act representation against `openchart-clinical-act-content/1.0` at the digest in `contracts/SHA256SUMS`. Feature (2) also runs contract tests against an openPractice double at the PL-04 digest. Every feature keeps the standalone golden-intake round trip passing.
- [ ] 4.2 Attach evidence for each of these:
  - a standalone installation passes the golden-intake round trip with no external system;
  - every act whose author type is not `clinician`, and every act with no named human author, is refused;
  - signed content cannot be edited in place or deleted; amendments are new versions; entered-in-error acts keep their content;
  - every signature records re-authentication, the grant version, the attestation and the content digest, and a lapsed or narrowed grant refuses;
  - a co-signature requirement escalates to the medical director when overdue and is never closed by a timer;
  - with no medical director designated, nothing can be signed; a designator cannot designate itself; a self-recorded attestation is refused; a medical director's self-grant needs an independent attestation and is shown as self-granted;
  - no intake submission, statement, communication, API response or extension event creates an act, and a derived act names its source while the statement stays unchanged and patient-reported;
  - an encounter cannot be signed with a draft attached or without a final note, and later changes go through a signed encounter amendment;
  - publication sends only final, clinician-signed encounter facts for actively linked patients, by reference, with codings as system and code only, and with only `confirmed` encounter diagnoses; corrections and retractions are queued whatever the link state and delivered when the link returns to `active`; a restricted act added to a published encounter, or a published diagnosis refuted later, is retracted; restricted acts, the problem list, notes, orders and prescriptions are never published;
  - a released order is never amended, and no order is transmitted;
  - every prescription signature, co-signature and release is refused where the prescribing-safety gate is not met, including with `System Manager`, and a refused deferred release stays `pending_release`; controlled and unknown classifications are refused; no transmission or dispense state is recorded;
  - no PHI appears in logs, errors or coded reasons;
  - all fixtures are synthetic, and no code set is bundled.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision and a compatibility declaration for the clinical acts, separate from p4's (tension CT-4). It names the supported contract versions: `openchart-clinical-act-content` MAJOR 1, and `openpractice-ehr-clinical-facts` MAJOR 1 with `billable_facts_supported` behaviour under PB-01.
- [ ] 5.2 For each feature, land the code and spec leg pull requests and the assembly root pin bump. Archive this change only after feature (4) has landed, or after the owner explicitly splits feature (4) into its own change. Re-run strict validation on the final revision first.
