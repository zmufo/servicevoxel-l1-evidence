#!/usr/bin/env python3
"""
C — evidence gate (Fact Gate / Evidence Eligibility Layer).

Four dimensions, all deterministic, fail-closed:

  1. existence    — is there a test report at all?
  2. commit match — does the report belong to the fix commit?
                    A green report on pre-fix code tested the bug, not the fix.
  3. non-empty    — did the suite collect any cases?
                    Zero cases passing is not evidence.
  4. CI state     — is CI actually green, with zero failures?

If any dimension fails, the Worker's claim does NOT become an asserted fact.
The gate is placed before the result is enqueued for delivery, i.e. before
it can reach a human, a PR, or another agent.

Run:  python3 src/evidence_gate_checker.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(os.path.dirname(HERE), "cases")


def load_cases():
    with open(os.path.join(CASES, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    cases = []
    for fn in sorted(os.listdir(CASES)):
        if fn.startswith("E") and fn.endswith(".json"):
            with open(os.path.join(CASES, fn), encoding="utf-8") as f:
                cases.append(json.load(f))
    return manifest, cases


def check(case, manifest):
    """Return ('ALLOW'|'BLOCK', reason, per-dimension detail)."""
    ev = case["evidence"]
    fix = manifest["fix_commit"]

    dims = []

    ok = ev["test_report"] is not None
    dims.append(("existence", ok,
                 "report present" if ok else "no test report (evidence absent)"))

    ok = ev["report_commit"] == fix
    dims.append(("commit_match", ok,
                 "report is on the fix commit" if ok else
                 "report commit %s != fix commit %s (tested pre-fix code)"
                 % (ev["report_commit"], fix)))

    ok = ev["total"] is not None and ev["total"] > 0
    dims.append(("non_empty", ok,
                 "collected %s cases" % ev["total"] if ok else
                 "collected %s cases (zero-case 'pass' is not evidence)"
                 % ev["total"]))

    failed = ev["failed"] or 0
    ok = ev["ci_status"] == "green" and failed == 0
    dims.append(("ci_state", ok,
                 "CI green, 0 failures" if ok else
                 "CI %s, %d failing cases" % (ev["ci_status"], failed)))

    bad = [d for d in dims if not d[1]]
    detail = [{"dim": d[0], "ok": d[1], "note": d[2]} for d in dims]
    if bad:
        return "BLOCK", "; ".join("%s: %s" % (d[0], d[2]) for d in bad), detail
    return "ALLOW", "all four dimensions satisfied", detail


def main():
    manifest, cases = load_cases()
    print("C — evidence gate (Fact Gate)")
    print("-" * 60)

    blocked_ok = 0
    missed = 0
    over = 0
    rows = []

    for c in cases:
        state, reason, detail = check(c, manifest)
        expect = c["expect"]
        correct = state == expect
        if expect == "BLOCK" and state == "BLOCK":
            blocked_ok += 1
        elif expect == "BLOCK" and state == "ALLOW":
            missed += 1
        elif expect == "ALLOW" and state == "BLOCK":
            over += 1

        rows.append({"id": c["id"], "name": c["name"], "expect": expect,
                     "state": state, "correct": correct,
                     "reason": reason, "detail": detail})
        mark = "ok" if correct else "XX"
        print("  [%s] %s %-22s expect=%-5s got=%-5s" % (mark, c["id"], c["name"], expect, state))
        if not correct:
            print("        %s" % reason)

    should_block = sum(1 for c in cases if c["expect"] == "BLOCK")
    print("-" * 60)
    print("  blocked %d/%d   missed %d   over-blocked %d"
          % (blocked_ok, should_block, missed, over))
    return rows


if __name__ == "__main__":
    main()
