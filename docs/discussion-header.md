Hi — we have been reading the Super-agent architecture article and the `dsh-superagent-prototype` README.

**We are not proposing a new standard, and we are not asking anyone to adopt anything.** We would like to ask one narrow, testable question about a gap we believe exists in the architecture.

## The question

When a Worker finishes a task and reports its result, **what decides whether that result is allowed to become an externally asserted fact?**

From the public materials, we can see three layers:

| Layer | What it governs |
|---|---|
| **Mandate / Authorization** | *Who* may ask the agent to do work (permission boundary) |
| **Watchdog session** | *Process* — is the Worker making progress, has it drifted off target |
| **?** | *Evidence eligibility of the conclusion* |

We could not find a layer that answers the third question. If we have missed it, we would genuinely like to be corrected — that is the fastest way to resolve this.

## What we are actually claiming

**One falsifiable structural proposition**, nothing more:

> Between "a Worker produces a result" and "that result becomes an externally asserted fact," there exists a point at which an evidence-eligibility check can be inserted.

If the maintainers say no such point exists — or that an existing mechanism already covers it — **we are falsified**, and we will say so publicly.

## What we have NOT done (please read before judging the numbers)

This matters more than the proposal itself:

1. **We have not integrated with the prototype.** No code of ours has run against it.
2. **The L1-CEG mock demo did not call any model API.** All inputs were constructed. It demonstrates a *difference in capability between three classes of guard* — it does **not** show that DeepSeek's prototype makes these mistakes.
3. **We have not read the implementation source.** Our reading comes from the public article and README. An earlier term we used ("effects queue") appears nowhere in the public writeup, so we treat the insertion point as a hypothesis to be checked against source, not as established fact.
4. **The 9 real responses come from a single model** (deepseek-chat) across 3 seeds. They do not generalise to "how LLMs behave."

We also have **no data showing any error-rate reduction**. Anyone citing us should not imply we do.

## The one thing we think is worth your time

We built a small comparison in a coding-agent setting, because `dsh-superagent` *is* a coding agent:

| Guard | Correct interceptions | Missed |
|---|---|---|
| A: pass-through | 0 / 4 | 4 |
| B: shallow rule (report exists? text contains "passed"?) | 1 / 4 | 3 |
| C: evidence-eligibility gate | 4 / 4 | 0 |

The four gaps: **report belongs to an older commit**, **zero test cases presented as a pass**, **CI red presented as green**, and **no report at all**.

The result we find most useful is the *middle* column: a shallow check catches the crudest failure (no report) but misses the three that actually cause damage. A shallow guard is not useless — it just stops at the outermost layer.

## Terminology note

ServiceVoxel is the romanisation of 体元 — *the smallest indivisible unit of a
service body*. It has nothing to do with 体素 (voxel) in computer graphics or
volume rendering. In this discussion, ServiceVoxel refers to a fact-level
service unit, not a 3D volume element.

In engineering terms, what we are describing is a deterministic **Fact Gate /
Evidence Eligibility Layer**: a check that sits between a Worker's report and
that report becoming an externally asserted fact.

## Invitation

We published the full criteria, the frozen hashes, the nine real responses, and a zero-dependency verification script here:

`https://github.com/zmufo/servicevoxel-l1-evidence`

`bash verify.sh` reproduces every number we cite, using nothing but `python3` stdlib.

If you have five minutes, the most valuable thing you could tell us is simply: **where, if anywhere, does the prototype currently check the evidence eligibility of a Worker's conclusion?** That single answer either confirms or kills our proposition.

Full proposal follows.

---

