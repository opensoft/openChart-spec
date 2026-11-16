"""Synthetic self-test for openchart-clinical-act-content 1.0.

Usage (from any directory): python3 -I <path>/contracts/selftest.py
Needs the `jsonschema` package, with draft 2020-12 support. Tested with
jsonschema 4.10.3 and 4.26.0, which report the error of a `false`
subschema at different paths, so no expected token depends on that path.
It touches no network and no file outside this directory.

Checks:
  1. the schema is a valid draft 2020-12 schema;
  2. every examples/*.valid.json validates;
  3. every examples/*.invalid.json fails, and at least one error names the
     token recorded for it in examples/expected-failures.json;
  4. every invalid fixture has an entry, and every entry has a fixture;
  5. every invalid fixture fails with exactly one error, so it fails for one
     reason only;
  6. the valid fixtures cover every record kind: act_version,
     recommendation and information (owner ruling 80);
  7. the integrity verifier of CA-08 passes every valid fixture:
     - each content and provenance digest, and each sign-off statement
       digest, recomputes from the record's own fields (design call CD-53);
     - each author signature is by the act's author;
     - a co-signed event's sign-off equals the co-signer signature's;
     - no challenge serves two sign-offs, within a record or across the
       valid fixture set, which stands in for one store (an identical
       copy, such as a co-signed event's, is one sign-off);
     - every time and every date is a real calendar time or date (the
       schema patterns check ranges only, so 30 February passes them);
     - an act signed after a hold carries adopted_from, or its hold was
       released by decline before it was signed, and a draft carries
       held_for exactly while its last hold event is held;
     - an encounter signature's manifest digest recomputes from every act
       and information record of the fixture set that referenced the
       encounter at signed_at: received by then, the latest version of
       each act received by then, except an act cancelled by then (its
       status at signed_at is worked out from its lifecycle events), and
       never a recommendation;
     - an item released from quarantine is dated by its release:
       first_received_at <= released_at <= received_at, and a held item
       ends once: no two records of the store carry the same
       held_item_ref;
     - a retrieved_at is never later than received_at, and a defaulted
       time is the time the path received the item: retrieved_at where it is
       recorded, otherwise a released item's first_received_at, otherwise
       received_at; a time as declared that was kept beside it is later than
       that time (design call CD-73);
     - a signed act records a signed lifecycle event (reported, not a
       crash, when it is missing);
     - each sign-off's evidence agrees with itself (design calls CD-75 to
       CD-78 and CD-81, PROPOSED): the openSig attestation's challenge_ref
       is the statement's, its challenge_digest is sha256: and
       statement_sha256, and its key_fingerprint is the sign-off's; the
       licence facts the grant names (covers) equal the verification's, and
       for a signature its grant_ref is the signature's authority basis; the
       verification was checked before the sign-off and is relied on before
       its reliance bound and less than 12 months after its check (owner
       ruling 213; design call CD-81); the revocation list used was issued
       before the sign-off, by the verification's verifier, its recorded age
       is its age at the sign-off, and it is flagged stale exactly when that
       age is over 72 hours (owner ruling 212); the verifier key is held for
       the licensing authority the verification names, and the sign-off is
       not on a later day than the licence's own expiry where one is stated
       (design calls CD-75 and CD-81), the day counted by the check's
       practice_date, which is within one day of checked_at's date in UTC;
       the attestation seals the authenticator flags, user_present and
       user_verified true and backup_eligible and backup_state equal to the
       sign-off's, a missing flag counting as a mismatch; and the sealed
       custody carries a model and a custody_basis equal to the sign-off's
       (design calls CD-48, CD-76, CD-83 and CD-85). The self-test does not verify Ed25519
       signatures: the synthetic fixtures carry placeholders, and the
       production audit verifier re-verifies openSig's signature, the sealed
       proof and the licence verification (CA-08);
  8. every examples/*.integrity-invalid.json validates against the schema
     and fails the verifier, naming the token recorded for it.
The digests use canonical JSON with sorted keys and no whitespace, which
equals RFC 8785 for the strings, integers and booleans the fixtures use; a
production verifier uses a full RFC 8785 implementation.
Exit status 0 only when every check passes.
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = HERE / "openchart-clinical-act-content-1.0.schema.json"
EXAMPLES = HERE / "examples"


def flatten(errors):
    for err in errors:
        yield err
        yield from flatten(err.context or [])


def describe(err):
    return f"{'/'.join(str(p) for p in err.absolute_path)} {err.message} {list(err.absolute_schema_path)}"


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


TIME = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$")


def times(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from times(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from times(v, f"{path}/{i}")
    elif isinstance(obj, str) and TIME.match(obj):
        yield path, obj


DATE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")


def dates(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from dates(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from dates(v, f"{path}/{i}")
    elif isinstance(obj, str) and DATE.match(obj):
        yield path, obj


def real_date(value):
    try:
        datetime.date(*(int(x) for x in DATE.match(value).groups()))
    except ValueError:
        return False
    return True


def identity(record):
    return (record.get("record_kind"), record.get("act_id") or record.get("recommendation_id") or record.get("information_id"),
            record.get("act_version"))


def real_time(value):
    y, mo, d, h, mi, s = (int(x) for x in TIME.match(value).groups()[:6])
    try:
        datetime.date(y, mo, d)
    except ValueError:
        return False
    return h < 24 and mi < 60 and (s < 60 or (s == 60 and mi == 59))


def manifest_of(encounter_id, signed_at, records):
    """The manifest of the records an encounter's signing view showed (EN-04, CD-53)."""
    at = parse(signed_at)
    latest, entries = {}, []
    for r in records:
        if r.get("record_kind") not in ("act_version", "information"):
            continue
        if r.get("act_id") == encounter_id or (r.get("content") or {}).get("encounter_ref", {}).get("act_id") != encounter_id:
            continue
        if parse(r["provenance"]["received_at"]) > at:
            continue
        if r["record_kind"] == "information":
            entries.append({"record_kind": "information", "id": r["information_id"], "content_sha256": sha(r["content"])})
        elif not cancelled_by(r, at) and r["act_version"] > latest.get(r["act_id"], (0, None))[0]:
            latest[r["act_id"]] = (r["act_version"], r)
    for _, r in latest.values():
        entries.append({"record_kind": "act_version", "id": r["act_id"], "version": r["act_version"], "content_sha256": sha(r["content"])})
    return sha(sorted(entries, key=lambda e: (e["record_kind"], e["id"], e.get("version", 0))))


def cancelled_by(record, at):
    """Whether the act's status at the time at was cancelled, worked out from its lifecycle events."""
    return any(e["event"] == "cancelled" and parse(e["at"]) <= at for e in record["lifecycle"])


def sign_offs(record):
    offs = [(f"signatures/{i}", s["sign_off"]) for i, s in enumerate(record.get("signatures", []))]
    offs += [(f"lifecycle/{i}", ev["sign_off"]) for i, ev in enumerate(record.get("lifecycle", [])) if "sign_off" in ev]
    return offs


def parse(value):
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def verify(record, records=()):
    """The integrity verifier of CA-08 for one record. records is the set an encounter's manifest is recomputed from."""
    problems = [f"{path}: {value} is not a real calendar time" for path, value in times(record) if not real_time(value)]
    problems += [f"{path}: {value} is not a real calendar date" for path, value in dates(record) if not real_date(value)]
    release = record.get("provenance", {}).get("released_from_quarantine")
    if release:
        for other in records:
            rel2 = (other.get("provenance") or {}).get("released_from_quarantine")
            if rel2 and rel2["held_item_ref"] == release["held_item_ref"] and identity(other) != identity(record):
                problems.append(f"provenance/released_from_quarantine: held_item_ref {release['held_item_ref']} already ended in {identity(other)[1]}; a held item ends once")
    if release and all(real_time(v) for v in (release["first_received_at"], release["released_at"], record["provenance"]["received_at"])):
        first, released, received = (parse(v) for v in (release["first_received_at"], release["released_at"], record["provenance"]["received_at"]))
        if received < released:
            problems.append("provenance/received_at precedes its release from quarantine: a released item is dated by its release")
        if released < first:
            problems.append("provenance/released_from_quarantine: released before it first arrived")
    prov_ = record.get("provenance") or {}
    retrieved, received = prov_.get("retrieved_at"), prov_.get("received_at")
    if retrieved and real_time(retrieved) and received and real_time(received) and parse(retrieved) > parse(received):
        problems.append("provenance/retrieved_at: an item is retrieved no later than the chart receives it")
    if prov_.get("occurred_at_defaulted"):
        occurred = prov_.get("occurred_at")
        release_ = prov_.get("released_from_quarantine")
        first = release_.get("first_received_at") if isinstance(release_, dict) else None
        expected = retrieved or first or received
        if not (occurred and real_time(occurred) and expected and real_time(expected) and parse(occurred) == parse(expected)):
            problems.append("provenance/occurred_at_defaulted: a defaulted time is the time the path received the item: retrieved_at where recorded, otherwise a released item's first arrival, otherwise received_at")
        declared = prov_.get("occurred_at_as_declared")
        if declared and occurred and real_time(declared) and real_time(occurred) and parse(declared) <= parse(occurred):
            problems.append("provenance/occurred_at_as_declared: kept as declared, but it is not later than the time the path received the item")
    if record.get("record_kind") != "act_version":
        return problems
    content, provenance = record["content"], record["provenance"]
    base = {"act_id": record["act_id"], "act_version": record["act_version"], "patient": record["patient"],
            "act_class": record["act_class"], "act_type": record["act_type"],
            "content_sha256": sha(content), "provenance_sha256": sha(provenance)}

    def check(so, role, signer, attestation, at, where):
        if so["provenance_sha256"] != sha(provenance):
            problems.append(f"{where}: provenance_sha256 does not recompute")
        statement = dict(base, action=so["action"], signature_role=role, signer_ref=signer,
                         attestation=attestation, signed_at=at, challenge_ref=so["challenge_ref"])
        if "manifest_sha256" in so:
            statement["manifest_sha256"] = so["manifest_sha256"]
        if sha(statement) != so["statement_sha256"]:
            problems.append(f"{where}: statement_sha256 does not recompute from the record and its signer")

    def evidence(so, where, grant=None):
        att, lv = so["opensig_attestation"], so["licence_verification"]
        if att["challenge_ref"] != so["challenge_ref"]:
            problems.append(f"{where}: the attestation challenge_ref is not the statement's challenge")
        if att["challenge_digest"] != "sha256:" + so["statement_sha256"]:
            problems.append(f"{where}: the attestation's challenge_digest is not the statement's digest")
        if att["key_fingerprint"] != so["key_fingerprint"]:
            problems.append(f"{where}: the attestation seals a key_fingerprint other than the sign-off's")
        cov = lv["covers"]
        if any(cov[k] != lv[k] for k in ("authority", "jurisdiction", "licence_class")):
            problems.append(f"{where}: the licence the grant names (covers) is not the licence the verification states")
        if grant is not None and cov["grant_ref"] != grant:
            problems.append(f"{where}: covers names a grant other than the signature's authority basis")
        at = so["check"]["checked_at"]
        stamps = (at, lv["verified_at"], lv["rely_until"], lv["revocation_list"]["issued_at"])
        if all(real_time(v) for v in stamps):
            at, verified, rely, listed = (parse(v) for v in stamps)
            if not verified <= at:
                problems.append(f"{where}: the licence was verified after the sign-off")
            if not at < rely:
                problems.append(f"{where}: the sign-off is past the verification's rely_until")
            try:
                cap = verified.replace(year=verified.year + 1)
            except ValueError:  # 29 February
                cap = verified.replace(year=verified.year + 1, day=28)
            if not at < cap:
                problems.append(f"{where}: the sign-off relies on a verification more than 12 months after its check")
            if listed > at:
                problems.append(f"{where}: the revocation list used was issued after the sign-off")
            elif int((at - listed).total_seconds()) != lv["revocation_list"]["age_seconds"]:
                problems.append(f"{where}: the revocation list's age_seconds is not its age at the sign-off")
        custody = att.get("custody") if isinstance(att.get("custody"), dict) else {}
        if "model" not in custody or custody["model"] != so.get("custody_model"):
            problems.append(f"{where}: the custody the sign-off records is not the custody the attestation sealed")
        if "custody_basis" not in custody or custody["custody_basis"] != so.get("custody_basis"):
            problems.append(f"{where}: the custody basis the sign-off records is not the basis the attestation sealed")
        flags = att.get("authenticator_flags")
        if not isinstance(flags, dict):
            problems.append(f"{where}: the attestation seals no authenticator flags, so neither user verification nor the backup flags are shown")
        else:
            if flags.get("user_present") is not True or flags.get("user_verified") is not True:
                problems.append(f"{where}: the sealed authenticator flags do not show the user present and verified, which every sign-off needs")
            if any(k not in flags or flags[k] != so.get(k) for k in ("backup_eligible", "backup_state")):
                problems.append(f"{where}: the backup flags the sign-off records are not those the attestation sealed")
        if lv["authority"] not in lv["verifier_key"]["held_for"]:
            problems.append(f"{where}: the verifier key is not held for the licensing authority the verification names")
        day = None
        if real_time(so["check"]["checked_at"]):
            day = parse(so["check"]["checked_at"]).date()
            pdate = so["check"].get("practice_date")
            if pdate and DATE.match(pdate) and real_date(pdate):
                local = datetime.date.fromisoformat(pdate)
                if abs((local - day).days) > 1:
                    problems.append(f"{where}: check/practice_date is more than a day from the date of checked_at, so it is not that time's date in any time zone")
                day = local
        exp = lv.get("licence_expires_on")
        if exp and day and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", exp):
            try:
                if day > datetime.date.fromisoformat(exp):
                    problems.append(f"{where}: the sign-off relies on the verification after the licence's own expiry")
            except ValueError:
                problems.append(f"{where}: licence_expires_on is not a real calendar date")
        if lv["revocation_list"]["stale"] != (lv["revocation_list"]["age_seconds"] > 72 * 3600):
            problems.append(f"{where}: the revocation list's stale flag is not whether it was over 72 hours old at the sign-off")
        if lv["revocation_list"]["verifier_ref"] != lv["verifier_ref"]:
            problems.append(f"{where}: the revocation list is not the verification's verifier's")

    cosigner_offs = []
    for i, s in enumerate(record.get("signatures", [])):
        if s["content_sha256"] != sha(content):
            problems.append(f"signatures/{i}: content_sha256 does not recompute")
        check(s["sign_off"], s["signature_role"], s["signer_ref"], s["attestation"], s["signed_at"], f"signatures/{i}")
        evidence(s["sign_off"], f"signatures/{i}", s["authority_basis_ref"])
        if s["signature_role"] == "author" and s["signer_ref"] != record["author"]["author_ref"]:
            problems.append(f"signatures/{i}: the author signature is not by the act's author")
        if s["signature_role"] == "cosigner":
            cosigner_offs.append(s["sign_off"])
    for i, ev in enumerate(record["lifecycle"]):
        if "sign_off" not in ev:
            continue
        role = "cosigner" if ev["event"] == "cosigned" else "actor"
        check(ev["sign_off"], role, ev["by_ref"], ev["attestation"], ev["at"], f"lifecycle/{i}")
        evidence(ev["sign_off"], f"lifecycle/{i}")
        if ev["event"] == "cosigned" and ev["sign_off"] not in cosigner_offs:
            problems.append(f"lifecycle/{i}: the co-signed event's sign-off differs from the co-signer signature's")

    seen = {}
    offs = sign_offs(record)
    for where, so in offs:
        first = seen.setdefault(so["challenge_ref"], (where, so))
        if first[0] != where and first[1] != so:
            problems.append(f"{where}: its challenge already served the sign-off at {first[0]}")
    me = (record["act_id"], record["act_version"])
    for other in records:
        if other.get("record_kind") != "act_version":
            continue
        for _, so2 in sign_offs(other):
            for where, so in offs:
                if so["challenge_ref"] == so2["challenge_ref"] and ((other["act_id"], other["act_version"]) != me or so != so2):
                    problems.append(f"{where}: its challenge already served a sign-off of {other['act_id']} version {other['act_version']} in the store")

    holds = [(i, ev) for i, ev in enumerate(record["lifecycle"]) if ev["event"] in ("held", "hold_released")]
    signed_at = next((i for i, ev in enumerate(record["lifecycle"]) if ev["event"] == "signed"), None)
    if record.get("signatures") and signed_at is None:
        problems.append("lifecycle: the act is signed but records no signed event")
    elif record.get("signatures"):
        held_before = [h for h in holds if h[0] < signed_at]
        if held_before and held_before[-1][1]["event"] == "held":
            problems.append("the act was signed while its draft was on hold: no hold_released precedes the signature")
        elif held_before and held_before[-1][1].get("reason_code") == "adopted" and "adopted_from" not in record:
            problems.append("the hold was released by adoption, but the act carries no adopted_from")
    else:
        on_hold = bool(holds) and holds[-1][1]["event"] == "held"
        if on_hold != ("held_for" in record):
            problems.append("held_for does not match the last hold event")

    if record["act_class"] == "encounter" and records:
        for i, s in enumerate(record.get("signatures", [])):
            if "manifest_sha256" in s["sign_off"] and s["sign_off"]["manifest_sha256"] != manifest_of(record["act_id"], s["signed_at"], records):
                problems.append(f"signatures/{i}: manifest_sha256 does not recompute from the records its signing view showed")
    return problems


def main():
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    expected = json.loads((EXAMPLES / "expected-failures.json").read_text())
    failures = []
    valid = invalid = integrity = 0
    names = set()
    kinds = set()
    valid_set = [json.loads(p.read_text()) for p in sorted(EXAMPLES.glob("*.valid.json"))]
    for path in sorted(EXAMPLES.glob("*.json")):
        if path.name == "expected-failures.json":
            continue
        names.add(path.name)
        record = json.loads(path.read_text())
        errors = list(validator.iter_errors(record))
        if path.name.endswith(".valid.json"):
            valid += 1
            kinds.add(record.get("record_kind"))
            if errors:
                failures.append(f"{path.name}: expected valid, got: {describe(errors[0])}")
            for problem in verify(record, valid_set):
                failures.append(f"{path.name}: integrity: {problem}")
        elif path.name.endswith(".integrity-invalid.json"):
            integrity += 1
            entry = expected.get(path.name)
            problems = verify(record, valid_set)
            if entry is None:
                failures.append(f"{path.name}: no entry in expected-failures.json")
            elif errors:
                failures.append(f"{path.name}: must pass the schema and fail only the verifier; schema error: {describe(errors[0])}")
            elif not any(entry["expect_in_error"] in p for p in problems):
                failures.append(f"{path.name}: the verifier did not report its stated reason ({entry['reason']}); got: {problems}")
        elif path.name.endswith(".invalid.json"):
            invalid += 1
            entry = expected.get(path.name)
            if entry is None:
                failures.append(f"{path.name}: no entry in expected-failures.json")
            elif not errors:
                failures.append(f"{path.name}: expected invalid ({entry['reason']}), but it validated")
            elif not any(entry["expect_in_error"] in describe(e) for e in flatten(errors)):
                failures.append(
                    f"{path.name}: failed, but not for its stated reason ({entry['reason']}); first error: {describe(errors[0])}"
                )
            elif len(errors) != 1:
                failures.append(f"{path.name}: failed with {len(errors)} errors; each invalid fixture must break exactly one rule")
        else:
            failures.append(f"{path.name}: fixture name must end in .valid.json, .invalid.json or .integrity-invalid.json")
    for kind in ("act_version", "recommendation", "information"):
        if kind not in kinds:
            failures.append(f"no valid fixture of record_kind {kind}")
    for name in expected:
        if name not in names:
            failures.append(f"expected-failures.json names a missing fixture: {name}")
    for line in failures:
        print("FAIL", line)
    print(f"selftest: {valid} valid, {invalid} invalid and {integrity} integrity-invalid fixtures checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
