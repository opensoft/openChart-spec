## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-prescribing-safety-checks --strict --no-interactive` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 In this change's `contracts/` directory, run `sha256sum -c SHA256SUMS` and `python3 -I selftest.py`. The self-test needs `jsonschema` 4.18 or later. All 11 valid fixtures must validate, and all 12 invalid fixtures must fail, each for the reason stated in `examples/expected-failures.json`. Record both outputs.
- [ ] 1.3 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The rulings recorded in `design.md` are not ratification. No Spec Kit feature is created before this task is complete.
- [ ] 1.4 Record Brett Heap's disposition of tensions PT-1 to PT-5 and design calls PD-1 to PD-22. Where a disposition needs an amendment elsewhere, name the change that must carry it:
  - `define-clinical-acts-foundation` for PT-3 (CA-01 wording and a MINOR content-schema version);
  - `define-ai-authored-clinical-records` for PT-4.

  If the owner reads PT-1 as making an alert a "treatment recommendation", add a MODIFIED delta to `expanded-patient-intake` in this change before ratification.
- [ ] 1.5 Compare this change with `define-clinical-acts-foundation`: its "Required later change: prescribing-safety checks" list against the table in `design.md`, and its RX-02 against PG-01. Record both revisions. A mismatch blocks the handoff.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance. Then perform a meaningful Constitution Check before planning. This gate blocks planning.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 `define-clinical-acts-foundation` is ratified, and its feature (1) has landed. This gate blocks this change's build.
- [ ] 2.4 Open Questions 3 and 4: in each deployment, the medical director records the legal and regulatory review (PG-04), the source verification (KA-03) and the currency policy (KA-04). This gate blocks go-live in that deployment, not the build; until it is met, PG-01 refuses every signature.
- [ ] 2.5 Open Questions 5 to 8 are routed as `design.md` states. Each fails closed meanwhile, so none blocks the build.

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-prescribing-safety-checks` from the assembly root, after task 2.3. Record immutable two-way links between the feature and this change.
- [ ] 3.2 Verify that the feature maps every requirement (SL-01 to SL-05, PC-01 to PC-08, KA-01 to KA-06, PG-01 to PG-05 and BD-01 to BD-04) and every scenario to executable tasks, without copying them here. The plan must decide:
  - the storage of the lists, the check records and the medical director's verification, currency and review records;
  - the adapter transport and its timeout;
  - the gate decision interface that foundation RX-02 calls;
  - how outage-path work items are routed;
  - the reason-code list for overrides.
- [ ] 3.3 Confirm with the foundation's feature (4) that its signing path calls PG-01, and that this change's capability is enabled before, or together with, that feature in every deployment (PG-05).

## 4. openChart Realization

- [ ] 4.1 Complete the linked feature. Contract tests validate every adapter message against the schema at the digest in `contracts/SHA256SUMS`, and run against an adapter double that serves only the synthetic fixtures and synthetic rules.
- [ ] 4.2 Attach evidence for each of these:
  - a standalone installation passes the golden-intake round trip with no source connected, and only prescription signing is refused;
  - patient-reported allergies and medications are check inputs and are labelled as such;
  - every uncheckable input and every check kind not run raises a visible warning;
  - drug–supplement is checked only where declared;
  - a same-ingredient allergy match is always critical, and an unmapped severity is critical;
  - critical and high alerts and every warning (allergy inputs above all) each need their own response, and only lower-severity alerts can be acknowledged together;
  - checks re-run at co-signature and release; the co-signer sees earlier overrides; a new finding at release holds the prescription; pending prescriptions are inputs;
  - every check record holds inputs, source and version, alerts and responses, and cannot be edited;
  - adapter failures never show "no alerts";
  - no request carries patient identity or labels, and free text is never sent without the recorded agreement;
  - every gate refusal reason is reachable;
  - with no verified source there is no outage path;
  - the outage path accepts only a clinician who has answered every local input individually and recorded the statement with code `prescribing.checks_unavailable_manual_review`; it sets the signed flag `checks_unavailable_at_signing` and re-checks on return;
  - no non-clinician author uses the outage path;
  - `System Manager` cannot bypass the gate;
  - a lapsed legal review refuses every signature;
  - no list, check or alert content reaches openPractice;
  - no PHI appears in logs;
  - all fixtures are synthetic, and no drug data is bundled.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision, the supported adapter contract version (MAJOR 1 and the declared MINOR), and the gate decision interface, for the foundation's feature (4) and for adapter implementers.
- [ ] 5.2 Land the code and spec leg pull requests and the assembly root pin bump. Then archive this change and promote its capabilities, after re-running strict validation on the final revision.
