## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-ai-authored-clinical-records --strict --no-interactive` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 Run `sha256sum -c SHA256SUMS` in this change's `contracts/` directory, and run the schema self-test over `contracts/examples/` (19 fixtures must validate, 29 must fail, each for its stated reason). Record both outputs.
- [ ] 1.3 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The rulings of 2026-11-14 and 2026-11-15 recorded in `design.md` are not ratification. No Spec Kit feature is created before this task is complete.
- [ ] 1.4 Record Brett Heap's disposition of the tensions still open (AT-5 to AT-8, AT-10 to AT-13 and the residual reading under AT-1) and of design calls AD-2 to AD-43. AD-1 is ruled (ruling 65); ruling 67 disposes AT-1, AT-2 and AT-4. Where a disposition needs an amendment elsewhere, name the change that must carry it: `define-clinical-message-inbox` for AT-5, AT-6 and AT-7; `define-openpractice-boundary` or the clinical-acts foundation for AT-8; the AI system's change for AT-9; the future governed amendment of ruling 67 for AT-10 and for the ratified sentences of AT-1 and AT-2; `define-clinical-acts-foundation` (openChart-spec#5) for AT-12, and its CA-07 for AT-11 at the Tier 2 amendment.
- [ ] 1.5 Compare this change with `MedxSoft/MedxEHR-spec` change `define-medical-ai-record-overlay` on the contract id `openchart-ai-clinical-record-write`, version `1.0`, the schema digest in `contracts/SHA256SUMS`, and every term in `design.md` "Terms used in both changes". Record both revisions. A mismatch blocks the handoff.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before planning. This gate blocks planning for both tiers.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 `define-clinical-message-inbox` is ratified first or together, because Tier 1 reuses its clinical-communication record (AD-3). This gate blocks Tier 1's build.
- [ ] 2.4 Open Question 3 is answered by ruling 72: another author drafted `define-clinical-acts-foundation` as openChart-spec#5; `design.md` lists what this change needs of it. **This gate blocks Tier 2 entirely:** no Tier 2 task in §4 may start, and neither practice mode may be enabled, until the foundation is ratified and built and a future governed amendment puts Tier 2 in force (ruling 67). `treatment_plan_change` also waits for the later treatment-plan change (ruling 73), and AI prescriptions also wait for `define-prescribing-safety-checks` (openChart-spec#6) and its gate (AA-03).
- [ ] 2.5 Open Questions 4 to 7 are routed to their owners as `design.md` states. Each fails closed meanwhile, so none blocks the Tier 1 build.
- [ ] 2.6 `define-clinical-acts-foundation` (openChart-spec#5) is ratified, and its feature (1), clinical authority (AU-01 to AU-06), which carries the clinical roles and authority Tier 1 relies on (AU-01 to AU-05), is built. **This gate blocks Tier 1's build:** the medical director (AG-02) and the consult review grant (AG-11) rest on it.

## 3. Spec Kit Handoff

- [ ] 3.1 Create the single openChart Spec Kit feature for `define-ai-authored-clinical-records` from the assembly root. Record immutable two-way links between the feature and this change. The feature's task list builds Tier 1 first and holds Tier 2 behind task 2.4.
- [ ] 3.2 Verify that the feature maps every requirement (AW-01 to AW-14, AG-01 to AG-10, AC-01 to AC-10 and AA-01 to AA-12) and every scenario to executable tasks, without copying them here. The plan must decide these points:
  - the name and scope of the write-path integration role, and how an AI system is registered;
  - how the medical director and clinician roles of openChart-spec#5 AU-01 and AU-02 are consumed, and the record of the consult review grant (AG-11, AT-12);
  - the storage of the grant, legal-review, review-policy and refusal records;
  - the consult record's fields on the clinical-communication record;
  - the durable outbound mechanism (the PL-14 pattern);
  - the sampling method, which the AI system cannot predict.

## 4. openChart Realization

Ruling 63 sets the build order: advice only, then limited practice, then full practice. Rulings 66 and 67 put only Tier 1 in scope to build.

- [ ] 4.1 **Tier 1 (buildable after §2.1 to §2.3 and §2.6).** Complete the linked feature for the write path, the `advice_only` grant record, the legal-review record, the review policy, the consult record, the consult review grant (AG-11), quarantine (AC-11), review selection, the review workflow and its escalation, and the AI-authorship labels. Every `act.write` is refused with `tier2_not_in_force`. Every consult record carries the ruling-66 label (AC-04), and the built-in codes `red_flag` and `advice_scope_breach` always select a consult for review (AC-07). Contract tests validate every message against the schema at the recorded digest and run against an AI-system double.
- [ ] 4.2 Attach Tier 1 evidence for each of these:
  - a standalone installation passes the golden-intake round trip with no AI system registered;
  - every refusal reason the Tier 1 path can produce, and that a refused write stores no clinical content;
  - idempotency, duplicates and conflicting duplicates;
  - every patient-link case, with no demographic matching and no merge;
  - scenario and simulation writes are refused;
  - a consult that ended before a pause is recorded, and one after it is refused;
  - an AI-system notice can pause or narrow and can never widen;
  - the medical director is the AU-01 designee, and only a named clinician holding a consult review grant records a review;
  - a consult refused at the grant checks is quarantined, labelled with its coded cause, reviewed within the fixed window (shorter when urgent), listed for the responsible clinician or the fallback recipients, readable only by clinicians authorized for the chart and the medical director, and never reported as accepted; a repeat with different content is refused `conflicting_duplicate`; a consult refused at an earlier step stores nothing;
  - registration is refused without an AU-01 designation; a manual suspension (lifted by the medical director only) and a deregistration refuse everything at once; a cap suspension stops only non-urgent consults, emergency and `red_flag` consults are still quarantined and listed urgently and never count toward the cap, and while no medical director is designated the administrative role may lift a cap suspension; a refused write that declared the emergency indicator or `red_flag` keeps the flags and is listed urgently without content only when operational and from a registered, non-deregistered identity, with the per-source digest and the alarm threshold; every standing change is notified under the 15-minute clock; the grant readback answers as AW-14 states;
  - a direct identity for a relay-only source is refused;
  - review selection by sample and by every built-in trigger, review by a named clinician only, and escalation of an overdue review;
  - AI authorship is labelled on every surface, the patient's included, and is never shown as clinician-authored;
  - no consult record becomes a diagnosis, statement or billable fact;
  - every consult record carries the ruling-66 label on clinician and patient views, and a reviewer's `advice_scope_breach` finding alerts the medical director;
  - a write whose source token is `healthlinc`, `openpractice_agent` or `openchart` is refused;
  - every `act.write` is refused with `tier2_not_in_force`;
  - a readback answers only the writing source system, with digests and codes only;
  - no PHI appears in logs, receipts, notifications or keys;
  - all fixtures are synthetic.
- [ ] 4.3 **Tier 2, limited practice. BLOCKED until task 2.4 is complete, including the future governed amendment of ruling 67.** After the foundation is ratified and built, a governed revision of this change pins the foundation's content schemas in a MINOR version of the contract. Then complete the Tier 2 layer for `limited_practice`: acceptance under a current grant, allowlist and condition checks, the reserved list, emergency refusal, the co-review queue and its escalation, void and countermand, the bar on superseding clinician content, and narrowing and pause.
- [ ] 4.4 **Tier 2, full practice. BLOCKED until task 4.3 is complete.** Complete the Tier 2 layer for `full_practice`, including reserved-act clearance from the recorded legal review.
- [ ] 4.5 Attach Tier 2 evidence for each of these: no act is accepted without a current grant that it matches in every field; a reserved act is refused unless cleared; emergency management is always refused; every accepted act enters co-review with its window; an overdue co-review escalates and is never closed by default; pending (`pending_release`) acts are held or cancelled on narrowing or pause and never released on the AI's authority; an AI prescription is accepted only on an `open` prescribing-safety gate decision and never on the outage path; `treatment_plan_change` is refused with `act_type_unsupported` until the treatment-plan change exists; no AI act modifies or supersedes clinician-authored content; every act shows its authority; every refused attempt is visible to the patient's doctor.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision, the supported contract version (MAJOR 1 and the declared MINOR) and a compatibility declaration for the write path, separate from p4's (tension AT-4).
- [ ] 5.2 Land the code and spec leg pull requests and the assembly root pin bump for each tier. Archive this change only when both tiers have landed, or after the owner explicitly splits Tier 2 into its own change, and after re-running strict validation on the final revision.
