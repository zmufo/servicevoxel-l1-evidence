> **Status: prepared, NOT yet posted.**
> Per the review advice, GitHub Discussions should not be bumped repeatedly in a
> short window. Post this only if discussion #1 receives no reply for 2–3 days.
> Keep it short. No theory. One concrete question.

---

Following up with something runnable rather than more prose.

We put the four evidence-gap cases into a minimal harness in this repo, under
`minrepro/`. Zero dependencies, Python 3 standard library only:

```bash
cd minrepro && python3 run.py
```

Result:

```
B  shallow rule    blocked 1/4   missed 3   over-blocked 0
C  evidence gate   blocked 4/4   missed 0   over-blocked 0
```

Each case is a standalone JSON file in `minrepro/cases/`, so new gaps can be
added by dropping in a file. The four are: no test report, report on a stale
(pre-fix) commit, zero collected cases, and CI red asserted as green. A fifth
case is a positive control, to show the gate does not simply block everything.

The gate itself is four deterministic checks — report exists, commit matches the
fix, case count non-zero, CI green — with no model involved. So this is not an
argument against rules; it is an argument that `Candidate` and `Fact` should be
distinct states with an explicit evidence contract between them.

**The concrete question:** would a report-validation hook, sitting between the
Worker's report and whatever enqueues it for external delivery (the outbox),
be a reasonable extension point? Or is that validation intentionally left to
something outside the prototype?

To be explicit about limits: every case is constructed input, no model API was
called, and nothing here has been run against the prototype. The harness shows
a difference between two checkers, not a measured error rate of any agent.
