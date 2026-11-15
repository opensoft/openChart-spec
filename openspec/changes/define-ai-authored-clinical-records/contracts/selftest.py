"""Synthetic self-test for openchart-ai-clinical-record-write 1.0.

Usage (from any directory): python3 -I <path>/contracts/selftest.py
Needs the `jsonschema` package with draft 2020-12 support. Tested with
jsonschema 4.10.3 and 4.26.0, whose error messages differ in places, so each
expected token names a property, a value or a schema keyword rather than a
whole message. It touches no network and no file outside this directory.

Checks:
  1. the schema is a valid draft 2020-12 schema;
  2. every examples/*.valid.json validates, and every other fixture behaves
     the same, both with and without `format` assertion (AW-01, AD-48);
  3. every examples/*.invalid.json fails, within the message kind its
     message_type names, with exactly one error, and that error names the
     token recorded for it in examples/expected-failures.json, so that it
     fails for its stated reason only. Where one broken rule is reported as
     several errors of one object (a party of the wrong kind, a code set
     that lacks the right code and holds a wrong one), the entry states
     error_count and says why;
  4. every invalid fixture has an entry in expected-failures.json and every
     entry has a fixture;
  5. every valid consult.write and act.write has an entry in
     examples/expected-outcomes.json stating what openChart does with it,
     whose codes are codes of this schema, and every entry has a fixture;
  6. beside the schema, for every valid fixture: exchange.content_sha256
     recomputes from exchange.turns (RFC 8785); a write names its parties in
     AW-02's order; and every timestamp names a real calendar day, which
     openChart refuses as malformed otherwise (AW-01);
  7. every examples/*.calendar-invalid.json validates and fails only the
     calendar check.
The digests use canonical JSON with sorted keys and no whitespace, which
equals RFC 8785 for the strings, integers and booleans the fixtures use.
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
SCHEMA = HERE / "openchart-ai-clinical-record-write-1.0.schema.json"
EXAMPLES = HERE / "examples"
MANIFESTS = {"expected-failures.json", "expected-outcomes.json"}
TIME = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,9})?(Z|[+-][0-9]{2}:[0-9]{2})$")


def flatten(errors):
    for err in errors:
        yield err
        yield from flatten(err.context or [])


def describe(err):
    return f"{'/'.join(str(p) for p in err.absolute_path)} {err.message} {list(err.relative_schema_path)}"


def jcs(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def calendar_errors(obj, path="$"):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            found += calendar_errors(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found += calendar_errors(value, f"{path}[{i}]")
    elif isinstance(obj, str):
        m = TIME.match(obj)
        if m:
            try:
                datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                found.append(f"{path} {obj} names no real calendar day")
    return found


def beside_schema(doc):
    """What the schema cannot check (AW-01, AW-02)."""
    problems = calendar_errors(doc)
    kind = doc.get("message_type")
    if kind == "consult.write":
        if hashlib.sha256(jcs(doc["exchange"]["turns"])).hexdigest() != doc["exchange"]["content_sha256"]:
            problems.append("exchange.content_sha256 does not recompute from exchange.turns")
    if kind in ("consult.write", "act.write"):
        src, writer, chain = doc["source_system"], doc["added_by"], doc["on_behalf_of"]
        if writer.get("system") == src:
            if len(chain) != 1:
                problems.append("AW-02: the source system writes, so on_behalf_of names the AI only")
        elif len(chain) != 2 or chain[1].get("system") != src:
            problems.append("AW-02: a relay writes, so on_behalf_of names the AI and then the source system")
    return problems


def branch_errors(schema, validator, doc):
    """The errors of the one message kind the fixture's message_type names."""
    index = None
    for i, ref in enumerate(schema["oneOf"]):
        name = ref["$ref"].split("/")[-1]
        if schema["$defs"][name]["properties"]["message_type"].get("const") == doc.get("message_type"):
            index = i
    top = list(validator.iter_errors(doc))
    if not top:
        return index, []
    mine = [e for e in top[0].context or [] if index is not None and e.relative_schema_path[0] == index]
    return index, mine


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    with_format = Draft202012Validator(schema, format_checker=FormatChecker())
    without_format = Draft202012Validator(schema)
    expected = json.loads((EXAMPLES / "expected-failures.json").read_text(encoding="utf-8"))
    outcomes = json.loads((EXAMPLES / "expected-outcomes.json").read_text(encoding="utf-8"))
    defs = schema["$defs"]
    codes = set(defs["quarantineCause"]["enum"]) | set(defs["pathAuthorityCode"]["enum"])
    results = set(defs["writeReceipt"]["properties"]["result"]["enum"]) - {"duplicate"}
    failures, names = [], set()
    counts = {"valid": 0, "invalid": 0, "calendar-invalid": 0}
    for path in sorted(EXAMPLES.glob("*.json")):
        if path.name in MANIFESTS:
            continue
        names.add(path.name)
        doc = json.loads(path.read_text(encoding="utf-8"))
        errs = list(with_format.iter_errors(doc))
        errs_nf = list(without_format.iter_errors(doc))
        if bool(errs) != bool(errs_nf):
            failures.append(f"{path.name}: behaves differently with and without format assertion")
        if path.name.endswith(".calendar-invalid.json"):
            counts["calendar-invalid"] += 1
            if errs:
                failures.append(f"{path.name}: must pass the schema; got {describe(errs[0])}")
            elif not calendar_errors(doc):
                failures.append(f"{path.name}: must fail the calendar check")
        elif path.name.endswith(".valid.json"):
            counts["valid"] += 1
            if errs:
                failures.append(f"{path.name}: expected valid, got: {describe(list(flatten(errs))[-1])}")
            for problem in beside_schema(doc):
                failures.append(f"{path.name}: {problem}")
            if doc.get("message_type") in ("consult.write", "act.write"):
                entry = outcomes.get(path.name)
                if entry is None:
                    failures.append(f"{path.name}: no entry in expected-outcomes.json")
                else:
                    if entry.get("receipt") not in results:
                        failures.append(f"{path.name}: expected outcome names no receipt result of this schema")
                    for key in ("code", "under_tier2"):
                        if key in entry and entry[key] not in codes:
                            failures.append(f"{path.name}: expected outcome {key} {entry[key]!r} is not a code of this schema")
        elif path.name.endswith(".invalid.json"):
            counts["invalid"] += 1
            entry = expected.get(path.name)
            index, mine = branch_errors(schema, with_format, doc)
            if entry is None:
                failures.append(f"{path.name}: no entry in expected-failures.json")
            elif not errs:
                failures.append(f"{path.name}: expected invalid ({entry['reason']}), but it validated")
            elif index is None:
                failures.append(f"{path.name}: names no message kind of this schema")
            elif len(mine) != entry.get("error_count", 1):
                failures.append(f"{path.name}: {len(mine)} errors within its message kind, not {entry.get('error_count', 1)}; each invalid fixture breaks one rule: "
                                + " | ".join(describe(e) for e in mine))
            elif not any(entry["expect_in_error"] in describe(e) for e in flatten(mine)):
                failures.append(f"{path.name}: failed, but not for its stated reason ({entry['reason']}); got: "
                                + " | ".join(describe(e) for e in flatten(mine)))
        else:
            failures.append(f"{path.name}: a fixture name ends in .valid.json, .invalid.json or .calendar-invalid.json")
    for name in list(expected) + list(outcomes):
        if name not in names:
            failures.append(f"a manifest names a missing fixture: {name}")
    for line in failures:
        print("FAIL", line)
    import importlib.metadata as md
    print(f"selftest (jsonschema {md.version('jsonschema')}, with and without format assertion): "
          f"{counts['valid']} valid, {counts['invalid']} invalid and {counts['calendar-invalid']} calendar-invalid fixtures checked, "
          f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
