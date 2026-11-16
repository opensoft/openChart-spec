"""Synthetic self-test for openchart-conversation-retrieval 1.0.

Usage (from any directory): python3 -I <path>/contracts/selftest.py
Needs the `jsonschema` package with draft 2020-12 support. Tested with
jsonschema 4.10.3 and 4.26.0, whose error messages differ in places, so each
expected token names a property, a value or a schema keyword rather than a
whole message. It touches no network and no file outside this directory.

Checks:
  1. the schema is a valid draft 2020-12 schema with no `format` keyword,
     and defines the eight message types and the seventeen error codes of
     design Decision 14;
  2. every examples/*.valid.json validates, and every fixture behaves the
     same with and without `format` assertion;
  3. every examples/*.invalid.json fails, within the message kind its
     message_type names, with exactly one error, and that error names the
     token recorded for it in examples/expected-failures.json, so that it
     fails for its stated reason only. Where one broken rule is reported as
     several errors, the entry states error_count and says why; a fixture
     whose message_type names no message kind says so in no_message_kind;
  4. every invalid, mismatch-invalid and calendar-invalid fixture has an
     entry in expected-failures.json, every valid conversation.result has an
     entry in examples/expected-outcomes.json, and every entry has a fixture;
  5. beside the schema, for every valid fixture: every timestamp names a real
     calendar day, which openChart refuses as schema_invalid otherwise. A
     turn's authored_at, source and ai_identity are left to check 6, which
     judges them per turn;
  6. openChart's reading of each turn of a valid conversation.result gives
     the outcome its entry records (MI-03, MI-12, design calls MD-22 and
     MD-37), against the retrieval time the entry records:
     - authored_at (defaulted_times): a time that is missing, later than
       the retrieval time plus five minutes, or not a timestamp naming a real
       calendar day is defaulted to the retrieval time, recorded as missing,
       later or unreadable; only a later time, which openChart can read, is
       kept as declared. No turn is held for its time;
     - source: a value that is not one of the schema's source tokens, or
       none, is a speaker openChart cannot read. A turn that is not an ai
       turn is then kept, its speaker recorded as not identified
       (speakers_not_identified);
     - over_bound_values: an authored_at, source or ai_identity beyond its
       outer bound ($defs boundedValue, or aiIdentity for ai_identity) is
       one openChart could not read, of which only the SHA-256 and the
       length of its canonical JSON are kept; an ai_identity beyond it
       makes the turn ai_not_identified. The bound read here agrees with
       the schema's $defs for every such value in the examples;
     - an ai turn's identification (ai_turns): `identified`, or the cause
       that makes it an unidentified AI turn: ai_not_identified when its
       speaker cannot be read, whatever its ai_identity, or when its
       ai_identity is beyond its outer bound; otherwise the first
       cause that applies, in this order: openwallet_id_missing (no
       openwallet_id), ai_not_identified (a property other than the three,
       a value that is not a string, or a value outside its form:
       openwallet_id as the clinical-acts foundation's walletId, model as
       ^[A-Za-z0-9._:/@+-]{1,128}$, model_version as the foundation's
       versionLabel, or no model or no model_version), and
       openwallet_id_not_covered (judged against the stand-in registration
       in examples/holder-registrations.json);
     - held_turns: each ai turn of a conversation HealthLinc holds that is
       not identified, whose text openChart holds outside the chart, with its
       identification cause. A conversation medXfactory holds is recorded by
       reference only (MI-24), so none of its turns is held;
  7. openChart's match of a result with its retrieve (MI-03, MD-29) passes
     for every valid result whose entry names the retrieve it answers, and
     every examples/*.mismatch-invalid.json validates and fails only that
     match, with result_mismatch, naming the token recorded for it;
  8. every examples/*.calendar-invalid.json validates and fails only the
     calendar check;
  9. beside the schema, every request turn of a valid priority or urgent
     result is shared as urgent_escalation, which the schema enforces on
     every request turn (MI-03, MD-25);
 10. a valid result whose entry names an earlier result in re_retrieval_of
     re-retrieves the same item and conversation, and openChart's comparison
     of each turn with the earlier one gives the outcome recorded (MI-12): a
     turn is a new version when its text, author type, source, authored_at
     or ai_identity differs, and unchanged otherwise; a turn held in the
     earlier result whose new version is not held is listed in
     corrected_held_turns, which flags the held turn as having a corrected
     turn;
 11. every fixture is within the contract's limit of 16 MiB for a message a
     holder sends, and, built in memory from a valid result by lengthening
     one turn's authored_at, a message of exactly the limit validates and
     is read per turn, while one byte more is refused beside the schema;
 12. for every valid result of a conversation HealthLinc holds, the times
     of the additions openChart makes from it meet the clinical-acts
     foundation's rules for them (its AN-04 and verifier at f1cfe74):
     each turn it keeps, filed when retrieved and filed later, carries
     retrieved_at, and a defaulted occurred_at equal to it; the handoff
     record filed after its conversation is retrieved carries retrieved_at
     too, and one filed before carries none and defaults to its own
     received_at, which it never changes. retrieved_at is never later
     than received_at, and a declared time kept beside a default is later
     than the default.
Every fixture is synthetic. Exit status 0 only when every check passes.
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA = HERE / "openchart-conversation-retrieval-1.0.schema.json"
EXAMPLES = HERE / "examples"
MANIFESTS = {"expected-failures.json", "expected-outcomes.json", "holder-registrations.json"}
MESSAGE_TYPES = {
    "capabilities.request", "capabilities.result", "conversation.retrieve", "conversation.result",
    "reply.deliver", "reply.delivery_failed", "split.request", "message.ack",
}
TIME = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]{1,9})?(Z|([+-])([0-9]{2}):([0-9]{2}))")
CLOCK_SKEW = datetime.timedelta(minutes=5)
PER_TURN = ("authored_at", "source", "ai_identity")
# The clinical-acts foundation's forms for an AI party (openchart-clinical-act-content 1.0,
# SHA-256 3c2e1afdb2d365bd84ef9f5f159e9addb6c93d7c2048af33da3cb9396b9548ec: $defs walletId and
# versionLabel, and party.model for an AI party), which the AI write path's contract also uses.
WALLET_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}")
MODEL = re.compile(r"[A-Za-z0-9._:/@+-]{1,128}")
VERSION_LABEL = re.compile(r"[A-Za-z0-9._:+-]{1,64}")
AI_IDENTITY_KEYS = {"openwallet_id", "model", "model_version"}
OUTCOMES = {"identified", "openwallet_id_missing", "ai_not_identified", "openwallet_id_not_covered"}
HELD_CAUSES = OUTCOMES - {"identified"}
CHANGE_FIELDS = ("content", "author_type", "source", "authored_at", "ai_identity")
MISSING = object()
# openChart's outer bound for a judged value ($defs boundedScalar, boundedValue and aiIdentity).
BOUND_CHARS = 1024
BOUND_ITEMS = 16
# The contract's limit for a message a holder sends, in bytes of UTF-8 JSON as received.
MESSAGE_LIMIT = 16 * 1024 * 1024
FILED_LATER = datetime.timedelta(hours=7, minutes=30)
FILED_FIRST = datetime.timedelta(minutes=1)


def flatten(errors):
    for err in errors:
        yield err
        yield from flatten(err.context or [])


def describe(err):
    return f"{'/'.join(str(p) for p in err.absolute_path)} {err.message} {list(err.relative_schema_path)}"


def uses_format(node):
    if isinstance(node, dict):
        return "format" in node or any(uses_format(v) for v in node.values())
    if isinstance(node, list):
        return any(uses_format(v) for v in node)
    return False


def without_per_turn_fields(doc):
    """A copy of the message without the turn fields that check 6 judges per turn."""
    doc = json.loads(json.dumps(doc))
    if doc.get("message_type") == "conversation.result":
        for turn in doc.get("payload", {}).get("turns", []):
            for key in PER_TURN:
                turn.pop(key, None)
    return doc


def calendar_errors(obj, path="$"):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            found += calendar_errors(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            found += calendar_errors(value, f"{path}[{i}]")
    elif isinstance(obj, str):
        m = TIME.fullmatch(obj)
        if m:
            try:
                datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                found.append(f"{path} {obj} names no real calendar day")
    return found


def read_time(value, pattern):
    """A timestamp as openChart reads it, or None when it cannot be read."""
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        return None
    m = TIME.fullmatch(value)
    year, month, day, hour, minute, second = (int(m.group(i)) for i in range(1, 7))
    if m.group(8) == "Z":
        zone = datetime.timezone.utc
    else:
        sign = 1 if m.group(9) == "+" else -1
        zone = datetime.timezone(sign * datetime.timedelta(hours=int(m.group(10)), minutes=int(m.group(11))))
    try:
        # A leap second (second 60) is read as the last second of its minute.
        return datetime.datetime(year, month, day, hour, minute, min(second, 59), tzinfo=zone)
    except ValueError:
        return None


def judge_time(value, retrieved_at, pattern):
    """openChart's reading of a turn's authored_at: declared, or defaulted because it is missing, later or unreadable."""
    if value is MISSING:
        return "missing"
    when = read_time(value, pattern)
    if when is None:
        return "unreadable"
    return "later" if when > retrieved_at + CLOCK_SKEW else "declared"


def bounded_scalar(value):
    return (isinstance(value, str) and len(value) <= BOUND_CHARS) or value is None or \
        isinstance(value, (bool, int, float))


def bounded_value(value):
    """Within openChart's outer bound for a turn's authored_at or source ($defs boundedValue)."""
    if bounded_scalar(value):
        return True
    if isinstance(value, list):
        return len(value) <= BOUND_ITEMS and all(bounded_scalar(v) for v in value)
    if isinstance(value, dict):
        return len(value) <= BOUND_ITEMS and all(len(k) <= BOUND_CHARS and bounded_scalar(v) for k, v in value.items())
    return False


def identity_in_bound(value):
    """Within openChart's outer bound for an ai_identity ($defs aiIdentity)."""
    return isinstance(value, dict) and len(value) <= BOUND_ITEMS and all(
        len(k) <= BOUND_CHARS and bounded_value(v) for k, v in value.items())


def in_bound(field, value):
    return identity_in_bound(value) if field == "ai_identity" else bounded_value(value)


def jcs(value):
    """Canonical JSON: equal to RFC 8785 for the values in these examples, which hold no
    floating-point number and no member name outside the Basic Multilingual Plane."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def kept_of_over_bound(value):
    """What openChart keeps of a value beyond its outer bound: its SHA-256 and its length, never the value."""
    text = jcs(value)
    return {"sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "length": len(text)}


def over_bound_values(doc):
    """The per-turn values of a result beyond their outer bound, by turn and field."""
    out = {}
    for turn in doc["payload"]["turns"]:
        for field in PER_TURN:
            if field in turn and not in_bound(field, turn[field]):
                out.setdefault(turn["turn_id"], {})[field] = kept_of_over_bound(turn[field])
    return out


def within_message_limit(raw):
    return len(raw) <= MESSAGE_LIMIT


def speaker_readable(turn, source_tokens):
    return any(turn.get("source", MISSING) == token for token in source_tokens)


def identify(turn, covered, source_tokens):
    """openChart's identification step for an ai turn (MD-37). Returns identified or the cause."""
    if not speaker_readable(turn, source_tokens):
        return "ai_not_identified"
    if "ai_identity" in turn and not identity_in_bound(turn["ai_identity"]):
        return "ai_not_identified"
    ident = turn.get("ai_identity", {})
    if not isinstance(ident, dict) or "openwallet_id" not in ident:
        return "openwallet_id_missing"
    forms = (("openwallet_id", WALLET_ID), ("model", MODEL), ("model_version", VERSION_LABEL))
    if set(ident) - AI_IDENTITY_KEYS or any(
            key not in ident or not isinstance(ident[key], str) or form.fullmatch(ident[key]) is None
            for key, form in forms):
        return "ai_not_identified"
    if ident["openwallet_id"] not in covered:
        return "openwallet_id_not_covered"
    return "identified"


def judge_turns(doc, covered, retrieved_at, pattern, source_tokens):
    """openChart's per-turn reading of a schema-valid result: identification, held turns, defaulted times
    and speakers recorded as not identified."""
    ai_turns, held, defaulted, speakers = {}, {}, {}, []
    by_reference = doc["payload"]["conversation_ref"]["namespace"] == "medxfactory"
    for turn in doc["payload"]["turns"]:
        turn_id = turn["turn_id"]
        time = judge_time(turn.get("authored_at", MISSING), retrieved_at, pattern)
        if time != "declared":
            defaulted[turn_id] = time
        if turn["author_type"] == "ai":
            ai_turns[turn_id] = identify(turn, covered, source_tokens)
            if ai_turns[turn_id] != "identified" and not by_reference:
                held[turn_id] = ai_turns[turn_id]
        elif not speaker_readable(turn, source_tokens):
            speakers.append(turn_id)
    return ai_turns, held, defaulted, speakers


def provenance_times(authored_at, retrieved_at, received_at, pattern, carries_retrieval=True):
    """The time fields of an addition openChart makes from a retrieval (MI-12, MD-22, MD-35)."""
    prov = {"received_at": received_at}
    if carries_retrieval:
        prov["retrieved_at"] = retrieved_at
        time = judge_time(authored_at, retrieved_at, pattern)
        if time == "declared":
            prov["occurred_at"] = read_time(authored_at, pattern)
        else:
            prov["occurred_at"], prov["occurred_at_defaulted"] = retrieved_at, True
            if time == "later":
                prov["occurred_at_as_declared"] = read_time(authored_at, pattern)
    else:
        # a handoff record filed before its conversation is retrieved: fixed at filing, never changed
        prov["occurred_at"], prov["occurred_at_defaulted"] = received_at, True
    return prov


def time_problems(prov):
    """The clinical-acts foundation's checks of an addition's times (its AN-04 and verifier at f1cfe74),
    for an item that was not released from quarantine."""
    problems = []
    retrieved, received = prov.get("retrieved_at"), prov["received_at"]
    if retrieved is not None and retrieved > received:
        problems.append("retrieved_at is later than received_at")
    if prov.get("occurred_at_defaulted"):
        if prov["occurred_at"] != (retrieved if retrieved is not None else received):
            problems.append("a defaulted occurred_at is not retrieved_at where recorded, otherwise received_at")
        declared = prov.get("occurred_at_as_declared")
        if declared is not None and declared <= prov["occurred_at"]:
            problems.append("occurred_at_as_declared is not later than the defaulted time")
    return problems


def addition_times(doc, held, retrieved_at, pattern):
    """The times of every addition openChart makes from a result of a conversation HealthLinc holds:
    each kept turn, filed when retrieved and filed later, and the handoff record filed after its
    conversation is retrieved and filed before it."""
    out = []
    turns = doc["payload"]["turns"]
    for turn in turns:
        if turn["turn_id"] in held:
            continue
        for received in (retrieved_at, retrieved_at + FILED_LATER):
            out.append((turn["turn_id"], provenance_times(turn.get("authored_at", MISSING), retrieved_at, received, pattern)))
    request = next(t for t in turns if t.get("request_turn") is True)
    out.append(("handoff filed after retrieval", provenance_times(
        request.get("authored_at", MISSING), retrieved_at, retrieved_at + FILED_LATER, pattern)))
    out.append(("handoff filed before retrieval", provenance_times(
        request.get("authored_at", MISSING), retrieved_at, retrieved_at - FILED_FIRST, pattern, carries_retrieval=False)))
    return out


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False) if value is not MISSING else None


def compare(earlier, later):
    """openChart's comparison of a re-retrieved turn with the earlier one (MI-12)."""
    before = {t["turn_id"]: t for t in earlier["payload"]["turns"]}
    out = {}
    for turn in later["payload"]["turns"]:
        old = before.get(turn["turn_id"])
        if old is None:
            out[turn["turn_id"]] = "new_turn"
        elif all(canonical(old.get(f, MISSING)) == canonical(turn.get(f, MISSING)) for f in CHANGE_FIELDS):
            out[turn["turn_id"]] = "unchanged"
        else:
            out[turn["turn_id"]] = "new_version"
    return out


def escalation_problems(doc):
    """Request turns of a priority or urgent result that are not shared as urgent_escalation (MI-03, MD-25)."""
    payload = doc["payload"]
    if payload.get("urgency") not in ("priority", "urgent"):
        return []
    return [t.get("turn_id") for t in payload.get("turns", [])
            if t.get("request_turn") is True and t.get("shared_basis") != "urgent_escalation"]


def triple(ref):
    return (ref["issuer"], ref["namespace"], ref["value"])


def match(retrieve, result):
    """openChart's test that a schema-valid result answers its retrieve (MI-03, MD-29)."""
    rq, rs = retrieve["payload"], result["payload"]
    if rs["handoff_id"] != rq["handoff_id"]:
        return "result_mismatch: handoff_id differs from the retrieve's"
    if triple(rs["conversation_ref"]) != triple(rq["conversation_ref"]):
        return "result_mismatch: conversation_ref differs from the retrieve's"
    if rs["urgency"] != rq["urgency"]:
        return "result_mismatch: urgency differs from the urgency openChart sent"
    if not any(t["request_turn"] and triple(t["request_ref"]) == triple(rq["request_ref"]) for t in rs["turns"]):
        return "result_mismatch: no request turn carries the retrieve's request_ref"
    return None


def branch_errors(schema, validator, doc):
    """The errors of the one message kind the fixture's message_type names."""
    index = None
    for i, ref in enumerate(schema["oneOf"]):
        name = ref["$ref"].split("/")[-1]
        if schema["$defs"][name]["properties"]["message_type"].get("const") == doc.get("message_type"):
            index = i
    top = list(validator.iter_errors(doc))
    if not top or index is None:
        return index, top
    return index, [e for e in top[0].context or [] if e.relative_schema_path[0] == index]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    with_format = Draft202012Validator(schema, format_checker=FormatChecker())
    without_format = Draft202012Validator(schema)
    timestamp = re.compile(schema["$defs"]["timestamp"]["pattern"])
    source_tokens = schema["$defs"]["sourceToken"]["enum"]
    expected = load(EXAMPLES / "expected-failures.json")
    outcomes = load(EXAMPLES / "expected-outcomes.json")
    registrations = load(EXAMPLES / "holder-registrations.json")
    failures, names = [], set()
    counts = {"valid": 0, "invalid": 0, "mismatch-invalid": 0, "calendar-invalid": 0, "ai turns": 0,
              "held turns": 0, "defaulted times": 0, "speakers not identified": 0, "re-retrievals": 0,
              "over-bound values": 0, "addition times": 0}
    bound_checks = {"ai_identity": Draft202012Validator({"$ref": "#/$defs/aiIdentity", "$defs": schema["$defs"]}),
                    "source": Draft202012Validator({"$ref": "#/$defs/boundedValue", "$defs": schema["$defs"]})}
    bound_checks["authored_at"] = bound_checks["source"]

    if uses_format(schema):
        failures.append("the schema uses a format keyword; every rule is checked by pattern")
    types = {schema["$defs"][r["$ref"].split("/")[-1]]["properties"]["message_type"]["const"] for r in schema["oneOf"]}
    if types != MESSAGE_TYPES:
        failures.append(f"message types {sorted(types)} are not the eight of Decision 14")
    if len(set(schema["$defs"]["errorCode"]["enum"])) != 17:
        failures.append("the contract does not have seventeen error codes")

    for path in sorted(EXAMPLES.glob("*.json")):
        if path.name in MANIFESTS:
            continue
        names.add(path.name)
        doc = load(path)
        if not within_message_limit(path.read_bytes()):
            failures.append(f"{path.name}: beyond the contract's message limit of {MESSAGE_LIMIT} bytes")
        if doc.get("message_type") == "conversation.result" and isinstance(doc.get("payload"), dict):
            for turn in doc["payload"].get("turns", []):
                for field in PER_TURN:
                    if isinstance(turn, dict) and field in turn and \
                            in_bound(field, turn[field]) != bound_checks[field].is_valid(turn[field]):
                        failures.append(f"{path.name}: the outer bound read here disagrees with the schema's for {field}")
        errs = list(with_format.iter_errors(doc))
        if bool(errs) != bool(list(without_format.iter_errors(doc))):
            failures.append(f"{path.name}: behaves differently with and without format assertion")
        entry = expected.get(path.name)
        if path.name.endswith(".mismatch-invalid.json") or path.name.endswith(".calendar-invalid.json"):
            kind = "mismatch-invalid" if path.name.endswith(".mismatch-invalid.json") else "calendar-invalid"
            counts[kind] += 1
            if entry is None:
                failures.append(f"{path.name}: no entry in expected-failures.json")
                continue
            if errs:
                failures.append(f"{path.name}: must pass the schema; got {describe(errs[0])}")
                continue
            calendar = calendar_errors(without_per_turn_fields(doc))
            if kind == "calendar-invalid":
                if not any(entry["expect_in_error"] in c for c in calendar):
                    failures.append(f"{path.name}: must fail the calendar check ({entry['reason']}); got {calendar}")
                continue
            if calendar:
                failures.append(f"{path.name}: {calendar[0]}")
            got = match(load(EXAMPLES / entry["retrieve"]), doc)
            if got is None or entry["expect_in_error"] not in got:
                failures.append(f"{path.name}: must fail the match with its retrieve ({entry['reason']}); got {got}")
        elif path.name.endswith(".valid.json"):
            counts["valid"] += 1
            if errs:
                failures.append(f"{path.name}: expected valid, got: {describe(list(flatten(errs))[-1])}")
                continue
            for problem in calendar_errors(without_per_turn_fields(doc)):
                failures.append(f"{path.name}: {problem}")
            if doc.get("message_type") != "conversation.result":
                continue
            for turn_id in escalation_problems(doc):
                failures.append(f"{path.name}: {turn_id}: a request turn of a priority or urgent result is not "
                                "shared as urgent_escalation, yet the schema accepted it")
            out = outcomes.get(path.name)
            if out is None:
                failures.append(f"{path.name}: no entry in expected-outcomes.json")
                continue
            retrieved_at = read_time(out.get("retrieved_at"), timestamp)
            if retrieved_at is None:
                failures.append(f"{path.name}: its entry records no readable retrieved_at")
                continue
            covered = set(registrations.get(doc["issuer"], {}).get("openwallet_ids", []))
            ai_turns, held, defaulted, speakers = judge_turns(doc, covered, retrieved_at, timestamp, source_tokens)
            want_ai = out.get("ai_turns", {})
            if set(ai_turns) != set(want_ai):
                failures.append(f"{path.name}: expected-outcomes.json does not list exactly its ai turns")
            for turn_id, want in want_ai.items():
                if want not in OUTCOMES:
                    failures.append(f"{path.name}: {turn_id}: {want!r} is not an identification outcome")
                elif turn_id in ai_turns:
                    counts["ai turns"] += 1
                    if ai_turns[turn_id] != want:
                        failures.append(f"{path.name}: {turn_id}: identification gave {ai_turns[turn_id]}, not {want}")
            want_held = out.get("held_turns")
            if want_held is None or any(cause not in HELD_CAUSES for cause in want_held.values()):
                failures.append(f"{path.name}: its entry does not record held_turns with known causes")
            elif held != want_held:
                failures.append(f"{path.name}: held turns {held}, not {want_held}")
            else:
                counts["held turns"] += len(held)
            if defaulted != out.get("defaulted_times"):
                failures.append(f"{path.name}: defaulted times {defaulted}, not {out.get('defaulted_times')}")
            else:
                counts["defaulted times"] += len(defaulted)
            over = over_bound_values(doc)
            if over != out.get("over_bound_values"):
                failures.append(f"{path.name}: over-bound values {over}, not {out.get('over_bound_values')}")
            else:
                counts["over-bound values"] += sum(len(v) for v in over.values())
            if doc["payload"]["conversation_ref"]["namespace"] == "healthlinc":
                for name, prov in addition_times(doc, held, retrieved_at, timestamp):
                    counts["addition times"] += 1
                    for problem in time_problems(prov):
                        failures.append(f"{path.name}: {name}: {problem}")
            if speakers != out.get("speakers_not_identified"):
                failures.append(f"{path.name}: speakers not identified {speakers}, not {out.get('speakers_not_identified')}")
            else:
                counts["speakers not identified"] += len(speakers)
            if "answers" in out:
                got = match(load(EXAMPLES / out["answers"]), doc)
                if got is not None:
                    failures.append(f"{path.name}: must answer {out['answers']}; got {got}")
            if "re_retrieval_of" in out:
                rr = out["re_retrieval_of"]
                earlier_path = EXAMPLES / rr["result"]
                if not earlier_path.exists():
                    failures.append(f"{path.name}: names a missing earlier result: {rr['result']}")
                    continue
                earlier = load(earlier_path)
                ep, lp = earlier["payload"], doc["payload"]
                if ep["handoff_id"] != lp["handoff_id"] or triple(ep["conversation_ref"]) != triple(lp["conversation_ref"]):
                    failures.append(f"{path.name}: is not a re-retrieval of {rr['result']}")
                    continue
                counts["re-retrievals"] += 1
                got = compare(earlier, doc)
                if got != rr["turns"]:
                    failures.append(f"{path.name}: re-retrieval comparison {got}, not {rr['turns']}")
                earlier_out = outcomes.get(rr["result"], {})
                earlier_held = earlier_out.get("held_turns", {})
                corrected = [t for t in earlier_held if got.get(t) == "new_version" and t not in held]
                if corrected != rr.get("corrected_held_turns"):
                    failures.append(f"{path.name}: corrected held turns {corrected}, not {rr.get('corrected_held_turns')}")
        elif path.name.endswith(".invalid.json"):
            counts["invalid"] += 1
            index, mine = branch_errors(schema, with_format, doc)
            if entry is None:
                failures.append(f"{path.name}: no entry in expected-failures.json")
            elif not errs:
                failures.append(f"{path.name}: expected invalid ({entry['reason']}), but it validated")
            elif index is None and not entry.get("no_message_kind"):
                failures.append(f"{path.name}: names no message kind of this schema")
            elif index is not None and entry.get("no_message_kind"):
                failures.append(f"{path.name}: names a message kind, but its entry says it names none")
            elif len(mine) != entry.get("error_count", 1):
                failures.append(f"{path.name}: {len(mine)} errors within its message kind, not {entry.get('error_count', 1)}; "
                                "each invalid fixture breaks one rule: " + " | ".join(describe(e) for e in mine))
            elif not any(entry["expect_in_error"] in describe(e) for e in flatten(mine)):
                failures.append(f"{path.name}: failed, but not for its stated reason ({entry['reason']}); got: "
                                + " | ".join(describe(e) for e in flatten(mine)))
        else:
            failures.append(f"{path.name}: a fixture name ends in .valid.json, .invalid.json, "
                            ".mismatch-invalid.json or .calendar-invalid.json")
    base_path = EXAMPLES / "conversation-result-healthlinc-mixed-turns.valid.json"
    base = load(base_path)
    base["payload"]["turns"][1]["authored_at"] = ""
    empty = len(json.dumps(base, ensure_ascii=False).encode("utf-8"))
    for extra, want_within in ((0, True), (1, False)):
        base["payload"]["turns"][1]["authored_at"] = "x" * (MESSAGE_LIMIT - empty + extra)
        raw = json.dumps(base, ensure_ascii=False).encode("utf-8")
        if within_message_limit(raw) != want_within or len(raw) != MESSAGE_LIMIT + extra:
            failures.append(f"a message of {len(raw)} bytes is {'within' if within_message_limit(raw) else 'beyond'} the limit")
        elif want_within:
            if list(without_format.iter_errors(base)):
                failures.append("a message of exactly the limit fails the schema")
            over = over_bound_values(base)
            if list(over) != [base["payload"]["turns"][1]["turn_id"]] or list(over[base["payload"]["turns"][1]["turn_id"]]) != ["authored_at"]:
                failures.append(f"a message of exactly the limit: over-bound values {list(over)}")
    for name in list(expected) + list(outcomes):
        if name not in names:
            failures.append(f"a manifest names a missing fixture: {name}")
    for name, out in outcomes.items():
        if "answers" in out and out["answers"] not in names:
            failures.append(f"{name}: names a missing retrieve: {out['answers']}")
    for line in failures:
        print("FAIL", line)
    import importlib.metadata as md
    print(f"selftest (jsonschema {md.version('jsonschema')}, with and without format assertion): "
          f"{counts['valid']} valid, {counts['invalid']} invalid, {counts['mismatch-invalid']} mismatch-invalid and "
          f"{counts['calendar-invalid']} calendar-invalid fixtures checked, {counts['ai turns']} ai turns identified, "
          f"{counts['held turns']} turns held, {counts['defaulted times']} times defaulted, "
          f"{counts['speakers not identified']} speakers not identified, "
          f"{counts['re-retrievals']} re-retrievals compared, {counts['over-bound values']} over-bound values kept "
          f"by digest and length, {counts['addition times']} additions' times checked, the message limit checked, "
          f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
