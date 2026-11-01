#!/usr/bin/env python3
"""
B — shallow rule checker.

This is NOT a strawman. It is what a reasonable pipeline actually does today:

  1. does a test report artifact exist?
  2. does the Worker's text say the tests passed?

It does not check whether the report corresponds to the fix commit,
whether the suite collected any cases, or whether CI is actually green.
Those are exactly the gaps that E2 / E3 / E4 exploit.

Run:  python3 src/shallow_rule_checker.py
"""
import json
import os
import sys

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
    """Return 'ALLOW' or 'BLOCK' plus a reason."""
    ev = case["evidence"]
    text = case["worker_report"].lower()

    has_file = ev["test_report"] is not None
    says_pass = "test" in text and "pass" in text

    if has_file and says_pass:
        return "ALLOW", "test report '%s' exists and text claims pass "
        "(no check of commit match / case count / CI state)" % ev["test_report"]
    if not has_file:
        return "BLOCK", "no test report artifact in the output"
    return "BLOCK", "text does not claim the tests passed"


def main():
    _manifest, cases = load_cases()
    print("B — shallow rule checker")
    print("-" * 60)

    blocked_ok = 0
    missed = 0
    over = 0
    rows = []

    for c in cases:
        state, reason = check(c, _manifest)
        expect = c["expect"]
        correct = state == expect
        if expect == "BLOCK" and state == "BLOCK":
            blocked_ok += 1
        elif expect == "BLOCK" and state == "ALLOW":
            missed += 1
        elif expect == "ALLOW" and state == "BLOCK":
            over += 1

        rows.append({"id": c["id"], "name": c["name"], "expect": expect,
                     "state": state, "correct": correct, "reason": reason})
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
