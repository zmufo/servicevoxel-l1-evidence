# Minimal reproducible harness: 4 coding-agent evidence gaps

**The question this repo exists to make concrete:**

> Between a Worker producing a result and the system asserting it as fact,
> where is evidence eligibility checked?

This repo contains no theory, no framework, and no model calls. It contains
five constructed cases and two checkers, so you can run it in 30 seconds and
judge for yourself.

## Run it

```bash
python3 run.py
```

Zero dependencies. Python 3 standard library only. Works on a fresh clone.

## Result

```
                        expect   B shallow   C gate
E1  no_test_report      BLOCK    BLOCK       BLOCK
E2  stale_commit_report BLOCK    ALLOW !     BLOCK
E3  zero_test_cases     BLOCK    ALLOW !     BLOCK
E4  ci_red_as_green     BLOCK    ALLOW !     BLOCK
E5  all_evidence_present ALLOW   ALLOW       ALLOW
------------------------------------------------------
B  shallow rule    blocked 1/4   missed 3   over-blocked 0
C  evidence gate   blocked 4/4   missed 0   over-blocked 0
```

**"missed" is the number that matters** — a Worker claim that should have been
stopped but was allowed through as an asserted fact.

B is not a strawman. It is what a reasonable pipeline does today: check that a
test report artifact exists, and check that the text says the tests passed.
It catches the coarsest case (E1) and misses the three that actually cause
damage.

## The four gaps

| case | what the Worker says | what is actually true |
|---|---|---|
| E1 | "tests passed" | no test report exists at all |
| E2 | "ran the tests, all passed" | report is green but belongs to a **pre-fix commit** — it tested the bug |
| E3 | "tests executed, no failures" | suite collected **zero cases** |
| E4 | "core cases passed, ready to merge" | **7 cases failed, CI is red** |

E5 is a positive control. It is here to prove the gate does not simply block
everything: `over-blocked 0`.

## What the gate checks

Four deterministic dimensions, fail-closed:

1. `existence` — is there a test report?
2. `commit_match` — does it belong to the fix commit?
3. `non_empty` — did the suite collect any cases?
4. `ci_state` — is CI actually green with zero failures?

If any dimension fails, the claim does not become an asserted fact.

The gate is deterministic rules, not a model. **This is not an argument against
rule engines.** The point is that Candidate and Fact must be separate states,
and the evidence contract between them must be explicit.

## The gate has teeth

Tamper with a case and the harness refuses to pass:

```bash
# set E2's report_commit to the fix commit
python3 run.py   # -> C blocked 3/4, missed 1, "GATE SELF-CHECK FAILED", exit 2
```

Verified: the checker fails loudly instead of quietly reporting a good number.

## What this repo does NOT claim

Stated up front, because these are the limits that matter:

- **No model API was called.** Every input is constructed. This repo shows a
  difference between two *checkers*, not a measured error rate of any agent.
- **Not integrated with any prototype.** Nothing here has been run against
  `dsh-superagent-prototype` or any other system.
- **Cases are constructed, not sampled.** Five cases is not a distribution.
  The claim is "these four gaps exist and shallow rules miss three of them",
  not "agents fail X% of the time".
- **No performance claim.** We have no data on latency, cost, or throughput.

## Adding your own case

Drop a JSON file into `cases/` following the existing schema, then re-run:

```json
{
  "id": "E6",
  "name": "your_gap",
  "expect": "BLOCK",
  "description": "...",
  "worker_report": "...",
  "evidence": {
    "test_report": "junit-release.xml",
    "report_commit": "b7c1f9a",
    "total": 128,
    "failed": 0,
    "ci_status": "green"
  }
}
```

`manifest.json` holds the `fix_commit` that `commit_match` compares against.

## Terminology

Internally we call this layer **ServiceVoxel**. In engineering terms it is a
deterministic **Fact Gate / Evidence Eligibility Layer** sitting between a
Worker's report and an externally asserted fact. Use whichever is clearer;
the behaviour is what this repo demonstrates.

> In this discussion, ServiceVoxel refers to a fact-level service unit, not a
> 3D volume element.

> ServiceVoxel is the romanisation of 体元, "the smallest indivisible unit of a
> service body". It has nothing to do with 体素 (voxel) in graphics or volume
> rendering.

## License

MIT.
