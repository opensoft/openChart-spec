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
  7. the integrity verifier of CA-08 passes every valid fixture: each
     content and provenance digest, and each sign-off statement digest,
     recomputes from the record's own fields (design call CD-53); each
     author signature is by the act's author; and a co-signed event's
     sign-off equals the co-signer signature's. An encounter's manifest
     digest is not recomputed here, because the attached records are other
     records;
  8. every examples/*.integrity-invalid.json validates against the schema
     and fails the verifier, naming the token recorded for it.
The digests use canonical JSON with sorted keys and no whitespace, which
equals RFC 8785 for the strings, integers and booleans the fixtures use; a
production verifier uses a full RFC 8785 implementation.
Exit status 0 only when every check passes.
"""
import hashlib
import json
import pathlib
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


def verify(record):
    """The integrity verifier of CA-08 for one act version. Returns the problems found."""
    if record.get("record_kind") != "act_version":
        return []
    problems = []
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

    cosigner_offs = []
    for i, s in enumerate(record.get("signatures", [])):
        if s["content_sha256"] != sha(content):
            problems.append(f"signatures/{i}: content_sha256 does not recompute")
        check(s["sign_off"], s["signature_role"], s["signer_ref"], s["attestation"], s["signed_at"], f"signatures/{i}")
        if s["signature_role"] == "author" and s["signer_ref"] != record["author"]["author_ref"]:
            problems.append(f"signatures/{i}: the author signature is not by the act's author")
        if s["signature_role"] == "cosigner":
            cosigner_offs.append(s["sign_off"])
    for i, ev in enumerate(record["lifecycle"]):
        if "sign_off" not in ev:
            continue
        role = "cosigner" if ev["event"] == "cosigned" else "actor"
        check(ev["sign_off"], role, ev["by_ref"], ev["attestation"], ev["at"], f"lifecycle/{i}")
        if ev["event"] == "cosigned" and ev["sign_off"] not in cosigner_offs:
            problems.append(f"lifecycle/{i}: the co-signed event's sign-off differs from the co-signer signature's")
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
            for problem in verify(record):
                failures.append(f"{path.name}: integrity: {problem}")
        elif path.name.endswith(".integrity-invalid.json"):
            integrity += 1
            entry = expected.get(path.name)
            problems = verify(record)
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
