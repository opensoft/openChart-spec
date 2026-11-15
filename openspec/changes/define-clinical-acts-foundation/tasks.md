## 1. Ratification And Contract Alignment

- [ ] 1.1 Run `openspec validate define-clinical-acts-foundation --strict --no-interactive` on the exact revision proposed for ratification. Record the OpenSpec version, timestamp, revision, exit code and output.
- [ ] 1.2 In this change's `contracts/` directory, run `sha256sum -c SHA256SUMS` and `python3 -I selftest.py`. The self-test must pass with the `jsonschema` versions named in its docstring (tested with 4.10.3 and 4.26.0). All 27 valid fixtures must validate, and all 50 invalid fixtures must fail, each with exactly one error and for the reason stated in `examples/expected-failures.json`. The valid fixtures must include every record kind: `act_version`, `recommendation` and `information`. Record both outputs.
- [ ] 1.3 Obtain Brett Heap's ratification. He stamps `Ratified by` and changes `Status` from `draft` to `ratified` in `proposal.md`, in the same revision. The rulings recorded in `design.md` are not ratification. No Spec Kit feature is created before this task is complete.
- [ ] 1.4 Record Brett Heap's disposition of the open tensions (CT-2 to CT-5, CT-11 to CT-13 and CT-17 to CT-22) and of design calls CD-1 to CD-64, including those made under rulings 80, 83, 85, 87, 88, 89, 92, 98 and 151. CT-6 to CT-10 are resolved; CT-1, CT-14 and CT-15 are settled by rulings 84, 85 and 88; CT-16 is ruled by ruling 89. Where a disposition needs an amendment elsewhere, name the change that must carry it:
  - `opensoft/openPractice-spec` `define-mvp-practice-foundation` for CT-11;
  - the follow-up of ruling 93 in `opensoft/openPractice-spec` for CT-16 (ruling 89's reason code). When it lands, re-pin this change to it and close CT-16;
  - `define-openpractice-boundary` for CT-13, and for ruling 88's exception to CF-01 (CT-15) if that change records it;
  - `opensoft/openWallet` and `opensoft/openSig` for CT-20 (task 2.7);
  - a later governed change to the canonical `expanded-patient-intake` capability, if the owner directs one, for CT-17 and CT-22.

  At ratification, the owner applies ruling 84's clarifying amendment (`design.md`, "Proposed clarifying amendment (ruling 84)") to the canonical `expanded-patient-intake` requirement "Intake does not confer clinician or autonomous authority". This change adds no MODIFIED delta.
- [ ] 1.5 Compare this change with each dependent draft, and record both revisions for each comparison. A mismatch blocks the handoff of the affected feature.
  - **`define-openpractice-boundary`:** the clinical-facts schema digest `6b2071fe61693d144aa91f4fc68e51d0cd7563d66b5cd2086f281a959f7e69ec` (PL-04), against `sha256sum -c contracts/SHA256SUMS` in `opensoft/openPractice-spec` `define-mvp-practice-foundation` at the compared revision.
  - **`define-ai-authored-clinical-records`:** its twelve minimum contents, against the table in `design.md`; the content schema digest it pins, against `contracts/SHA256SUMS`; and its conformance to ruling 80 (the relay as writer and the AI on whose behalf; an AI act attempt stored as a recommendation record, AN-09, with each of its own codes mapped to `missing_authority` and kept in `path_reason`, and its content kept as given with `content_schema`, CD-51; an AI the relay's registration covers as decision maker, CD-61).
  - **`define-clinical-message-inbox`:** an inbox action or reply attempted without its grant is entered as a recommendation (AU-06, CD-50).
  - **`define-prescribing-safety-checks`:** a recommendation gets no gate decision and never counts as a signature, co-signature, release or active prescription in its checks (AN-09); a pending allergy or medication-list recommendation may only raise an alert, labelled as resting on an entry that is not an authorized decision.

## 2. Governance Prerequisites (Routed Open Questions)

- [ ] 2.1 Open Question 1: adopt openChart's constitution through separate governance (it is the unfilled template today). Then perform a meaningful Constitution Check before planning. This gate blocks planning for every feature.
- [ ] 2.2 Open Question 2: owner dispositions (task 1.4). This gate blocks ratification.
- [ ] 2.3 `define-openpractice-boundary` is ratified, and its publication surface and durable outbound store (PL-14) are built. This gate blocks live publication in feature (3) only; feature (3) may build against an openPractice double.
- [ ] 2.4 **`define-prescribing-safety-checks` is ratified (owner ruling 74).** It is being drafted under ruling 75, with the minimum contents listed in `design.md`. This gate blocks feature (5), prescriptions, entirely: no task of feature (5) may start before it is met. Even after it is met, RX-02 refuses every prescription signature in any deployment where that change's gate is not met.
- [ ] 2.5 Open Questions 3 to 6 are routed as `design.md` states: counsel for Open Questions 3 and 4, planning for Open Question 5, and the boundary change for Open Question 6. Each fails closed meanwhile (CD-27, no deletion, and CD-17), so none blocks features (1) to (4). Open Question 7 is closed by ruling 83 (CD-20). Open Questions 8 and 12 to 22 go to the owner, and each fails closed meanwhile: no device operation, no AI decision authority, every unauthorized action a recommendation, every ruled licence check kept, sign-offs only in the chart, recommendations kept out of interoperability reads, and notes from writers who cannot sign kept as information. Open Questions 9 to 11 are task 2.7.
- [ ] 2.6 **Ruling 98 (CD-38), before feature (1) goes live.** The first medical director's designation takes effect only after a second named human confirms it, or, for a practice with a single administrator, after a licence verification against the licensing board's public record is recorded. Feature (1) is built and tested with that path, and no deployment enables live clinical authority until this task is complete. Designations, attestations and self-grants are listed for the medical director as well as the administrative role.
- [ ] 2.7 **Ruling 151, before any decision takes effect live.** `opensoft/openWallet` specifies, through its own governed change, the practitioner's licence verification that a wallet holds, how openChart reads it and how it is revoked (Open Question 9). `opensoft/openSig` specifies an attestation that a signature over a chart entry is from that wallet, or the owner rules that openWallet's proof of possession is that attestation (Open Question 11). The owner answers Open Question 10 (where openWallet and openSig run). Until all three are met, the licence-verification and attestation checks of CA-04 cannot be made. Every sign-off attempt then fails in the way the author can cure later: drafts stay drafts, every attempt is recorded, and no deployment may present any act as signed. Features (1) to (4) may be built and tested against doubles of openWallet and openSig.

## 3. Spec Kit Handoff (ordered features; ruling 85, CD-31)

There are five ordered features (owner ruling 85). Each is created from the assembly root only after task 1.3, and only after the feature before it has landed. Record immutable two-way links between each feature and this change. Each feature maps its requirements and every scenario to executable tasks, without copying them here.

- [ ] 3.1 **Feature (1): clinical authority and additions.** It covers AU-01 to AU-07 and AN-01 to AN-14. Clinical roles and authority are their own first feature (ruling 92), built on its own and ahead of the acts (CD-41; #3 MT-22). Building the general rule for additions in it is a proposed call (CD-41). The plan must decide:
  - the administrative role that designates the medical director, and the attestation-recording permission (Open Question 5);
  - the stores for designations, attestations and grants, including every grant scope (act class, `review` over `ai_consult_record`, and the AU-06 inbox scopes of ruling 92);
  - the ruling-98 confirmation or licence-verification path (task 2.6);
  - the registration and suspension of systems and devices (AN-03, CD-43; Open Question 14), and the binding of each practitioner's account to their wallet, made only in their own session with proof of possession (AU-07, CD-54);
  - the addition-provenance store, the recommendation store, the submitter's receipt, repeat handling by `submission_ref`, and the review routing with failed adoptions (AN-04, AN-09 to AN-11);
  - how test data is declared and test patients are marked (CD-62).
- [ ] 3.2 **Feature (2): encounter, note and signing.** It covers CA-01 to CA-15 and EN-01 to EN-06. Depends on feature (1). The plan must decide:
  - the storage of acts, versions, signatures, lifecycle events and audit;
  - the extension of the versioned service boundary;
  - the re-authentication mechanism and its single-use challenge (CD-10, CD-53), and the sign-off checks of CA-04 against doubles of openWallet and openSig until task 2.7 is met;
  - how a failed sign-off is recorded and its draft kept or held, how a recommendation is tied to its draft, and how a clinician adopts one on the draft, as a new draft or as an action (AN-11, AN-14);
  - the information record for a note whose writer cannot sign it (AN-14, CD-63);
  - the act-type registry store and the code-set import record.
- [ ] 3.3 **Feature (3): diagnoses, procedures and publication to openPractice.** It covers DX-01 to DX-03 and PB-01 to PB-05. Depends on feature (2). Live publication also needs task 2.3.
- [ ] 3.4 **Feature (4): orders.** It covers OR-01 to OR-04. Depends on feature (2).
- [ ] 3.5 **Feature (5): prescriptions.** It covers RX-01 to RX-04. **Depends on feature (2) and on task 2.4**, the ratification of `define-prescribing-safety-checks` (ruling 74). Its signature, co-signature and release paths call that change's gate decision.

## 4. openChart Realization

- [ ] 4.1 Complete each linked feature in order. Contract tests validate every act representation against `openchart-clinical-act-content/1.0` at the digest in `contracts/SHA256SUMS`. Feature (3) also runs contract tests against an openPractice double at the PL-04 digest. Every feature keeps the standalone golden-intake round trip passing.
- [ ] 4.2 Attach evidence for each of these:
  - a standalone installation passes the golden-intake round trip with no external system;
  - an addition whose writer cannot be identified, whose patient cannot be matched, whose content is malformed or test data, or whose writer is suspended, is refused with nothing stored, and no addition is refused for missing authority;
  - every addition records `received_at`, `occurred_at`, its source, its writer and every party on whose behalf it was written, readable by anyone who can read the chart;
  - decision content from an author who is not a practitioner with the authority, a sign-off that fails for authority, decision content whose class or act type is not in force, and a decision added on someone's behalf without their own sign-off, are each entered as one recommendation record, kept as given, marked "not an authorized decision" with its coded missing authority, with no effect; its submitter is told at once, a repeat is answered with the first result, a clinician with the authority reviews it, adoption carries `adopted_from`, and a failed adoption is recorded on it;
  - a failed sign-off never cancels a draft or an encounter; a failure the author can cure leaves the draft open with the attempt recorded, and while openWallet and openSig specify nothing, a practitioner's drafts stay drafts;
  - a note from a writer who cannot sign it is kept as information, marked not signed off, and never counts as a final note;
  - no recommendation is signed, released, published, billed or counted as an active diagnosis, order or prescription;
  - every sign-off, on a signature or on the lifecycle event of a discontinuation, an entered-in-error mark, a co-signature or a cancellation, records the action, the `openwallet_id`, the licence verification, the challenge, the statement's digest, the openSig attestation, the provenance digest and the custody model `isolated_per_use_authorized`; an attestation captured for one action fails for another; a wallet is bound to an account only in that practitioner's own session;
  - signed content cannot be edited in place or deleted; amendments are new versions; entered-in-error acts keep their content;
  - every signature records re-authentication, the grant version, the attestation and the content digest, and under a lapsed or narrowed grant a signing attempt takes no effect and becomes a recommendation tied to the held draft; a completion needs the `complete` scope and no sign-off;
  - a co-signature requirement escalates to the medical director when overdue and is never closed by a timer;
  - with no medical director designated, nothing can be signed; a designator cannot designate itself; a self-recorded attestation is refused; a medical director's self-grant needs an independent attestation and is shown as self-granted; the first designation follows ruling 98; listings reach the medical director;
  - every grant scope (act class, `review` over `ai_consult_record`, and any AU-06 inbox scope) is checked at the moment of action, no scope outside an act class reaches an act, no agent holds one, and an action without its scope takes no effect and becomes a recommendation; a roster entry for anyone without the lane's ownership grant is refused; a `physician`-lane inbox or reply grant is refused for a nurse;
  - no intake submission, statement, communication, API response or extension event creates an act, and a derived act names its source while the statement stays unchanged and patient-reported;
  - an encounter cannot be signed with a draft attached or without a final note, and later changes go through a signed encounter amendment;
  - publication sends only final, clinician-signed encounter facts for actively linked patients, by reference, with codings as system and code only, and with only `confirmed` encounter diagnoses; corrections and retractions are queued whatever the link state and delivered when the link returns to `active`; retractions reach openPractice as pointers only after a link is revoked or superseded; every published fact whose latest version could no longer be published is retracted, and every withdrawn encounter reads as `no_billable_facts`; restricted acts, the problem list, notes, orders and prescriptions are never published;
  - a released order is never amended, and no order is transmitted;
  - every prescription signature, co-signature and release is refused where the prescribing-safety gate is not met, including with `System Manager`, and a refused deferred release stays `pending_release`; controlled and unknown classifications are refused; no transmission or dispense state is recorded;
  - no PHI appears in logs, errors or coded reasons;
  - all fixtures are synthetic, and no code set is bundled.

## 5. Consumer Handoff And Archive

- [ ] 5.1 Publish the passing openChart revision and a compatibility declaration for the clinical acts, separate from p4's (tension CT-4). It names the supported contract versions: `openchart-clinical-act-content` MAJOR 1, and `openpractice-ehr-clinical-facts` MAJOR 1 with `billable_facts_supported` behaviour under PB-01.
- [ ] 5.2 For each feature, land the code and spec leg pull requests and the assembly root pin bump. Archive this change only after feature (5) has landed, or after the owner explicitly splits feature (5) into its own change. Re-run strict validation on the final revision first.
