#!/usr/bin/env python3
"""
Run both checkers over every case and write results/comparison.json.

Zero dependencies. Python 3 standard library only.

    python3 run.py

Expected output:

    B  shallow rule    blocked 1/4   missed 3
    C  evidence gate   blocked 4/4   missed 0   over-blocked 0

The single number that matters is "missed": a Worker claim that should have
been stopped but was allowed to become an asserted fact.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import shallow_rule_checker as B  # noqa: E402
import evidence_gate_checker as C  # noqa: E402

RESULTS = os.path.join(HERE, "results")


def score(cases, rows):
    should_block = [r for r in rows if r["expect"] == "BLOCK"]
    blocked_ok = sum(1 for r in should_block if r["state"] == "BLOCK")
    missed = len(should_block) - blocked_ok
    over = sum(1 for r in rows if r["expect"] == "ALLOW" and r["state"] == "BLOCK")
    correct = sum(1 for r in rows if r["correct"])
    return {
        "should_block": len(should_block),
        "blocked_ok": blocked_ok,
        "missed": missed,
        "over_blocked": over,
        "correct": correct,
        "total": len(rows),
    }


def main():
    manifest, cases = C.load_cases()
    b_rows = []
    c_rows = []
    for c in cases:
        st_b, rs_b = B.check(c, manifest)
        b_rows.append({"id": c["id"], "name": c["name"], "expect": c["expect"],
                       "state": st_b, "correct": st_b == c["expect"], "reason": rs_b})
        st_c, rs_c, detail = C.check(c, manifest)
        c_rows.append({"id": c["id"], "name": c["name"], "expect": c["expect"],
                       "state": st_c, "correct": st_c == c["expect"],
                       "reason": rs_c, "detail": detail})

    b_score = score(cases, b_rows)
    c_score = score(cases, c_rows)

    print("=" * 66)
    print("Worker claim: %s" % manifest["claim_under_test"])
    print("=" * 66)
    print("%-4s %-22s %-7s %-9s %-9s" % ("", "", "expect", "B shallow", "C gate"))
    print("-" * 66)
    for i, c in enumerate(cases):
        flag_b = "" if b_rows[i]["correct"] else " !"
        flag_c = "" if c_rows[i]["correct"] else " !"
        print("%-4s %-22s %-7s %-9s %-9s" % (
            c["id"], c["name"], c["expect"],
            b_rows[i]["state"] + flag_b, c_rows[i]["state"] + flag_c))
    print("-" * 66)
    print("%-14s blocked %d/%d   missed %d   over-blocked %d"
          % ("B shallow rule", b_score["blocked_ok"], b_score["should_block"],
             b_score["missed"], b_score["over_blocked"]))
    print("%-14s blocked %d/%d   missed %d   over-blocked %d"
          % ("C evidence gate", c_score["blocked_ok"], c_score["should_block"],
             c_score["missed"], c_score["over_blocked"]))
    print("=" * 66)

    out = {
        "claim_under_test": manifest["claim_under_test"],
        "note": "All inputs constructed. No model API was called.",
        "cases": [{"id": c["id"], "name": c["name"], "expect": c["expect"]} for c in cases],
        "B_shallow_rule": {"rows": b_rows, "score": b_score},
        "C_evidence_gate": {"rows": c_rows, "score": c_score},
    }
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, "comparison.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nwrote %s" % path)

    if c_score["missed"] != 0 or c_score["over_blocked"] != 0:
        print("GATE SELF-CHECK FAILED")
        sys.exit(2)


if __name__ == "__main__":
    main()
