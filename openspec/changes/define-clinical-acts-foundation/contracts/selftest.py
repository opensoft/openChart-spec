"""Synthetic self-test for openchart-clinical-act-content 1.0.

Usage (from any directory): python3 -I <path>/contracts/selftest.py
Needs the `jsonschema` package (4.18 or later). It touches no network and
no file outside this directory.

Checks:
  1. the schema is a valid draft 2020-12 schema;
  2. every examples/*.valid.json validates;
  3. every examples/*.invalid.json fails, and at least one error names the
     token recorded for it in examples/expected-failures.json;
  4. every invalid fixture has an entry, and every entry has a fixture.
Exit status 0 only when every check passes.
"""
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


def main():
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    expected = json.loads((EXAMPLES / "expected-failures.json").read_text())
    failures = []
    valid = invalid = 0
    names = set()
    for path in sorted(EXAMPLES.glob("*.json")):
        if path.name == "expected-failures.json":
            continue
        names.add(path.name)
        errors = list(validator.iter_errors(json.loads(path.read_text())))
        if path.name.endswith(".valid.json"):
            valid += 1
            if errors:
                failures.append(f"{path.name}: expected valid, got: {describe(errors[0])}")
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
        else:
            failures.append(f"{path.name}: fixture name must end in .valid.json or .invalid.json")
    for name in expected:
        if name not in names:
            failures.append(f"expected-failures.json names a missing fixture: {name}")
    for line in failures:
        print("FAIL", line)
    print(f"selftest: {valid} valid and {invalid} invalid fixtures checked, {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
