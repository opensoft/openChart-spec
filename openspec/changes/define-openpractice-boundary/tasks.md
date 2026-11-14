## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-openpractice-boundary --strict` on the exact revision proposed for ratification, and record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. An agent-made, conditional or inferred stamp does not count, and no Spec Kit feature is created before this task is complete.
- [ ] 1.3 Confirm that `opensoft/openPractice-spec` change `define-mvp-practice-foundation` uses the identical identifiers `openpractice-ehr-patient-link/1.0` and `openpractice-ehr-clinical-facts/1.0` and the identical namespaces `openpractice` and `openchart`. Record both revisions compared. A mismatch blocks the handoff.

## 2. Governance Prerequisites

- [ ] 2.1 Adopt openChart's constitution through separate governance. It is the unfilled template today. Then perform a meaningful Constitution Check before the feature's plan phase.
- [ ] 2.2 Record which separately governed change will introduce clinician-authored encounters, diagnoses and procedures. Until it lands, the publication surface returns an explicit no-billable-facts result.

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-openpractice-boundary` from the assembly root, covering both capabilities, and record immutable two-way links between the feature and this change.
- [ ] 3.2 Verify that the feature maps every requirement and scenario to executable tasks without copying them here, and that the owner's answers to the open questions it depends on are recorded. These are Open Questions 2 to 6, 9 and 10.

## 4. openChart Realization

- [ ] 4.1 Complete the linked feature: the `openpractice` namespace convention; versioned link-request, review-resolution and demographic-update commands; a scoped integration role; the namespace-aware identity decision; the immutable store and projection of applied demographic versions; the date-of-birth hold; leaving `sex_recorded` untouched; and the publication surface. Run contract tests for both contracts against an openPractice double.
- [ ] 4.2 Attach evidence for all of the following: a standalone installation with the golden-intake round trip and no openPractice; conflict-to-review with no merge; idempotent, version-ordered acknowledgements; prior values retained; no patient-reported statement published as a diagnosis; no billing, coverage or guarantor data stored; and synthetic-only fixtures.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision and the supported contract versions for openPractice.
- [ ] 5.2 Land the code and spec leg PRs and the assembly root pin bump, then archive this change and promote both capabilities. Re-run strict validation on the final revision before archiving.
