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
     recomputes from exchange.turns (RFC 8785); and every timestamp of a
     message other than a write names a real calendar day, which openChart
     refuses as malformed otherwise (AW-01). No time a write gives is
     refused: openChart replaces it with the time of receipt, or shows a
     turn's time as not stated (AW-15, AD-70);
  7. the part of AW-06's AI check that a write's own content decides
     (AD-60): every valid write that it holds, because its on_behalf_of
     cannot be read as the AI alone (from the source system's own
     identity) or the AI and then the source system (from a relay), or
     because its AI is not in the form of $defs/aiParty, or because its
     on_behalf_of is beyond its size bound ($defs/onBehalfOfBound), has
     the expected outcome quarantined with that cause (ai_not_identified or
     openwallet_id_missing), and no other write has. Coverage by a
     registration is openChart's to judge, not the message's;
  8. the rule of AW-01 and AD-63 for every valid write: each declaration
     is judged against its form in $defs/declarationForms and against its
     size bound ($defs/declarationBound, $defs/valueBound), which sets it
     aside however it fits its form (each authority
     field against $defs/authorityClaim, each consult turn against
     $defs/consultTurn, the times as AD-70 reads them, the action against
     the target), and the fields set aside, by the names of
     $defs/setAsideField, equal the expected outcome's set_aside, together
     with any field its set_aside_at_receipt names because it depends on
     the time of receipt (AD-74, AD-75);
  9. every examples/*.calendar-invalid.json validates and fails only the
     calendar check.
No fixture is beyond the message limit, 134217728 bytes (128 MiB) as
received or more than 32 levels deep, which openChart checks beside the
schema before it and refuses with schema_invalid (AW-01, AD-63).
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
WRITES = ("consult.write", "act.write")
HELD_BY_CONTENT = ("ai_not_identified", "openwallet_id_missing")
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


def refused_times(doc):
    """Timestamps naming no real calendar day that openChart refuses as malformed. No time a write gives is
    refused: it is replaced with the time of receipt, or shown as not stated (AW-15, AD-70)."""
    return [] if doc.get("message_type") in WRITES else calendar_errors(doc)


def readable_time(schema, value):
    """A time in the form of $defs/timestamp naming a real calendar day, as a comparable instant; None for
    a time openChart cannot read (AD-70). A leap second reads as the second before it."""
    if not isinstance(value, str) or not re.match(schema["$defs"]["timestamp"]["pattern"], value) or calendar_errors(value):
        return None
    head, zone = (value[:-1], "+00:00") if value.endswith("Z") else (value[:-6], value[-6:])
    whole, _, frac = head.partition(".")
    whole = whole[:-2] + "59" if whole.endswith(":60") else whole
    return datetime.datetime.fromisoformat(whole + ("." + (frac + "000000")[:6] if frac else "") + zone)


def set_aside(schema, doc):
    """The fields of a write that openChart sets aside because their values are outside their forms
    (AW-01, AW-06, AD-63, AD-74, AD-75), by the names of $defs/setAsideField."""
    defs = schema["$defs"]
    forms = defs["declarationForms"]["properties"]
    def fits(sub, value):
        return Draft202012Validator({"$defs": defs, **sub}).is_valid(value)
    kind = doc["message_type"]
    known = set(defs["consultWrite" if kind == "consult.write" else "actWrite"]["properties"])
    out = set()
    if set(doc) - known:
        out.add("unknown_property")
    # A single value beyond its size bound is a value outside its form, however it fits its form (AD-74).
    props = defs["consultWrite" if kind == "consult.write" else "actWrite"]["properties"]
    bounds = {"declarationAsGiven": "declarationBound", "valueAsGiven": "valueBound"}
    for field, value in doc.items():
        bound = bounds.get(props.get(field, {}).get("$ref", "").split("/")[-1])
        if bound and not fits(defs[bound], value):
            out.add(field)
    for field, value in doc.items():
        if field not in known or field in out:
            continue
        if field == "authority" and isinstance(value, dict):
            claim = defs["authorityClaim"]["properties"]
            for k, v in value.items():
                if k not in claim:
                    out.add("authority")
                elif not fits(claim[k], v):
                    out.add("authority." + k)
        elif field in forms and field in known and field not in ("sent_at", "started_at", "ended_at", "occurred_at", "action", "target_record_ref"):
            if not fits(forms[field], value):
                out.add(field)
    for field in ("sent_at", "started_at", "ended_at", "occurred_at"):
        if field in doc and field in known and readable_time(schema, doc[field]) is None:
            out.add(field)
    start, end = readable_time(schema, doc.get("started_at")), readable_time(schema, doc.get("ended_at"))
    if start and end and end < start:
        out |= {"started_at", "ended_at"}
    if kind == "act.write":
        target = "target_record_ref" in doc and fits(forms["target_record_ref"], doc["target_record_ref"])
        if "target_record_ref" in doc and not target:
            out.add("target_record_ref")
        if "action" in doc:
            action = doc["action"]
            if not fits(forms["action"], action) or (action == "sign") == target:
                out.add("action")
        content = doc["act_content"]
        if set(content) - {"content", "content_schema"}:
            out.add("unknown_property")
        if "content_schema" in content and not fits(forms["content_schema"], content["content_schema"]):
            out.add("act_content.content_schema")
    else:
        exchange = doc["exchange"]
        if set(exchange) - {"turns", "content_sha256"}:
            out.add("unknown_property")
        turn_form = defs["consultTurn"]
        authors = turn_form["properties"]["author_type"]["enum"]
        if not any(isinstance(turn, dict) and turn.get("author_type") == "ai" for turn in exchange["turns"]):
            out.add("exchange.turns")
        for turn in exchange["turns"]:
            if fits(turn_form, turn):
                continue
            if not isinstance(turn, dict):
                out.add("exchange.turns")
                continue
            found = set()
            if turn.get("author_type") not in authors:
                found.add("exchange.turns.author_type")
            if "at" not in turn or readable_time(schema, turn["at"]) is None:
                found.add("exchange.turns.at")
            if "attachments" in turn and not fits(turn_form["properties"]["attachments"], turn["attachments"]):
                found.add("exchange.turns.attachments")
            evidence = {k: turn[k] for k in ("evidence_refs", "knowledge_basis") if k in turn}
            if evidence and (turn.get("author_type") != "ai" or not all(fits(turn_form["properties"][k], v) for k, v in evidence.items())):
                found.add("exchange.turns.evidence")
            rest = {k: v for k, v in turn.items() if k not in ("author_type", "at", "attachments", "evidence_refs", "knowledge_basis")}
            if set(rest) - set(turn_form["properties"]) or not all(fits(turn_form["properties"][k], v) for k, v in rest.items()) \
                    or not {"turn_id", "seq", "text"} <= set(rest):
                found.add("exchange.turns")
            out |= found or {"exchange.turns"}
    return sorted(out)


def beside_schema(doc):
    """What the schema cannot check (AW-01)."""
    problems = refused_times(doc)
    if doc.get("message_type") == "consult.write":
        if hashlib.sha256(jcs(doc["exchange"]["turns"])).hexdigest() != doc["exchange"]["content_sha256"]:
            problems.append("exchange.content_sha256 does not recompute from exchange.turns")
    return problems


def ai_check(schema, doc):
    """The part of AW-06's AI check that a write's own content decides (AW-02, AD-60), in its order:
    ai_not_identified for an on_behalf_of this path cannot read, one beyond its size bound included, then
    openwallet_id_missing, then
    ai_not_identified for an AI not in the form of $defs/aiParty; None when the content passes."""
    def form(name, value):
        return Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/" + name}).is_valid(value)
    chain, src = doc.get("on_behalf_of"), doc["source_system"]
    if "on_behalf_of" in doc and not form("onBehalfOfBound", chain):
        return "ai_not_identified"
    relay = doc["added_by"].get("system") != src
    if not isinstance(chain, list) or not chain or not all(isinstance(p, dict) for p in chain) or chain[0].get("kind") != "ai":
        return "ai_not_identified"
    if relay and (len(chain) != 2 or not form("systemParty", chain[1]) or chain[1].get("system") != src):
        return "ai_not_identified"
    if not relay and len(chain) != 1:
        return "ai_not_identified"
    if "openwallet_id" not in chain[0]:
        return "openwallet_id_missing"
    if not form("aiParty", chain[0]):
        return "ai_not_identified"
    return None


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
            elif not refused_times(doc):
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
                    held = None if errs else ai_check(schema, doc)
                    if not errs:
                        fields = set(set_aside(schema, doc)) | set(entry.get("set_aside_at_receipt", []))
                        allowed = set(defs["setAsideField"]["enum"])
                        if fields - allowed:
                            failures.append(f"{path.name}: set aside under names $defs/setAsideField lacks: {sorted(fields - allowed)}")
                        if sorted(fields) != sorted(entry.get("set_aside", [])):
                            failures.append(f"{path.name}: sets aside {sorted(fields)}, but its expected outcome says {entry.get('set_aside', [])} (AD-74)")
                    if entry.get("receipt") != "refused":
                        if held and (entry.get("receipt") != "quarantined" or entry.get("code") != held):
                            failures.append(f"{path.name}: the AI check holds it with {held}, but its expected outcome says otherwise (AW-06)")
                        if not held and entry.get("code") in HELD_BY_CONTENT:
                            failures.append(f"{path.name}: names its AI in the form the AI check reads, so it is not held with {entry['code']} (AW-06)")
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
