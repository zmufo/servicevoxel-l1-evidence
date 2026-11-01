# Integration Proposal: A Fact Gate Before Irreversible Effects

**Repository:** `zmufo/servicevoxel-l1-evidence`
**Target upstream:** `deepseek-ai/dsh-superagent-prototype`
**Status:** Proposal only. **Not integrated. Not executed against the prototype.**

---

## 1. TL;DR

We are not proposing a new standard, and we are not proposing to replace anything in your architecture.

We are proposing **one narrow insertion point**: before a Worker's conclusion is allowed to become an externally-visible fact or trigger an irreversible effect, assert that the conclusion has evidence that (a) exists, (b) matches the subject under test, (c) is internally consistent, and (d) comes from a source in a known state.

If any check fails, the conclusion is marked `UNCONFIRMED` and is **not** allowed to proceed. Fail closed.

We bring four test cases that can be run against this in about 30 minutes, with a zero-dependency reproduction script already in this repository.

---

## 2. What we are explicitly NOT proposing

This is the part we most want to be read correctly.

| Layer | Question it answers | Owner |
|---|---|---|
| Authorization / Mandate | *Who may let whom do what?* (permission boundary) | Already in your design |
| Watchdog | *Is progress being made? Has direction drifted?* (process) | Already in your design |
| **ServiceVoxel (our proposal)** | *Does this conclusion qualify as a fact?* (evidential standing) | **Our proposal** |

These are **serial, not competing**. Ours sits *before* authorization: ask "does this qualify as a fact" first, then "is the action permitted."

**We are not proposing to:**
- Replace Router, Worker, or Watchdog
- Add a model call on the hot path (the gate is deterministic; no LLM required)
- Enforce a schema on your internal types
- Change how Worker sessions are isolated

---

## 3. Where the gate goes

### 3.1 What we can confirm from public material

From the published article and the repository README:

- Router: resident, dispatches, does not execute.
- Worker: isolated context, full tool access, reports status and results back to Router.
- Watchdog: separate session, timer-driven external control loop; judges whether Workers are making substantive progress and whether direction has drifted.
- The prototype is research code; **some designs discussed in the article are future directions and are not implemented in this prototype.**

### 3.2 What we CANNOT confirm — read this before trusting §3.3

**We have not read the implementation source.** Our understanding comes from the public article and README only.

In earlier discussions we referred to an "Effects queue" with transaction-enqueue / post-commit delivery semantics as the precise insertion anchor. **That mechanism is not described in the public article.** It should be treated as a **hypothesis to be validated against the source**, not as an established fact about the prototype.

We are flagging this ourselves rather than quietly dropping it, because the insertion point is the load-bearing claim of this proposal.

### 3.3 The proposal, stated as a falsifiable claim

Irrespective of the exact mechanism, the claim is structural:

> **There exists a point after a Worker produces a result and before that result becomes an external fact or an irreversible side effect. That point is where an evidence assertion belongs.**

If no such single point exists, the maintainers know better than we do and we would like to be corrected.

```
Worker → result/Candidate → [ FACT GATE ] → authorized → effect
                                  │
                                  └─ fail → mark UNCONFIRMED, do not proceed
```

---

## 4. Why Watchdog is not sufficient here

This is not a criticism of Watchdog. It is a scope distinction.

Watchdog asks: *did the Worker make progress, and is it going the right way?*

The gate asks: *is this specific claim supported by evidence?*

A Worker can make excellent progress in exactly the right direction and still produce a conclusion whose evidence is stale, empty, or pointed at a different subject. Progress and evidential standing are different properties.

Our `L1-SILENCE-001` evidence pack contains nine real model responses exhibiting precisely this shape: the observation channel had failed (`probe_status=DEAD`), yet the response asserted "database instance unavailable" **with no acknowledgement of uncertainty anywhere in the text**. The task was completed. The direction was correct. The conclusion was not supported.

---

## 5. Worked example: coding-agent evidence gaps

We chose this framing because `dsh-superagent-prototype` is itself a coding agent.

Four constructed cases (`evidence/` sibling directory, `L1-CODING-EVIDENCE-GAP-001`):

| # | Gap | Why it is dangerous |
|---|---|---|
| E1 | No test report at all | Claimed verification with nothing behind it |
| E2 | Test report belongs to an **older commit** | Green evidence for code that is no longer the code under test |
| E3 | Zero test cases, reported as passing | Empty suite presented as success |
| E4 | CI red, reported as green | Explicitly contradicted by the source of truth |

Results across three防线 (defense lines):

| Group | Correctly blocked | **Wrongly allowed** | Over-blocked |
|---|---|---|---|
| A — pass-through (no gate) | 0/4 | **4** | 0 |
| B — shallow rule (report exists + keyword) | 1/4 | **3** | 0 |
| C — evidence gate | **4/4** | **0** | **0** |

**The finding that matters:** B blocks only E1. It misses E2, E3, E4 — the three that actually cause damage, because they *look* like valid evidence.

A shallow check is not useless. It is just calibrated to the wrong failure mode: it catches absence, not mismatch.

---

## 6. Minimal interface

Illustrative TypeScript, shaped to your stack. Not a PR — a sketch.

```typescript
/** A pointer to a piece of evidence. Never the evidence itself. */
interface EvidenceRef {
  /** Identifier of the artifact: file path, CI run id, command digest, ... */
  locator: string;
  /** What this evidence is about. Must match the candidate's subject. */
  subject: string;
  /** Digest of the subject at the time evidence was produced. */
  subjectDigest: string;
  /** Source state: did the producing system itself succeed? */
  sourceStatus: "PASS" | "FAIL" | "UNKNOWN";
  /** Non-empty content assertion: e.g. test count > 0. */
  volume: number;
  producedAt: string;
}

interface Candidate {
  claim: string;
  subject: string;
  subjectDigest: string;
  evidence: EvidenceRef[];
}

type Verdict =
  | { ok: true }
  | { ok: false; reason: string };

function factGate(c: Candidate): Verdict {
  if (c.evidence.length === 0) {
    return { ok: false, reason: "NO_EVIDENCE" };
  }
  for (const e of c.evidence) {
    if (e.subject !== c.subject || e.subjectDigest !== c.subjectDigest) {
      return { ok: false, reason: "SUBJECT_MISMATCH" };
    }
    if (e.volume <= 0) {
      return { ok: false, reason: "EMPTY_EVIDENCE" };
    }
    if (e.sourceStatus !== "PASS") {
      return { ok: false, reason: "SOURCE_NOT_PASS" };
    }
  }
  return { ok: true };
}
```

Two properties we consider non-negotiable:

1. **Fail closed.** If the gate cannot evaluate, the answer is `UNCONFIRMED`, never `OK`.
2. **Digest comparison, not recency.** "Recent" is not "matching." A report is valid only if the subject digest matches.

---

## 7. What we cannot claim

This section is the most important part of this document. Everything above is bounded by it.

- **We have not integrated with the prototype.** Nothing here has been run against `dsh-superagent-prototype`.
- **We have not read the implementation source.** The insertion point in §3.3 is a structural claim, not a verified code location.
- **The coding-agent cases did not call any model API.** Inputs were constructed. What they demonstrate is the *capability difference between three defense lines*, **not** that DeepSeek's prototype would fail these cases.
- **`L1-SILENCE-001` used a single model** (`deepseek-chat`) across 3 seeds and 9 responses. It does **not** generalize to "LLMs behave this way." It is evidence about one model on one scenario family.
- **No error-rate reduction is claimed.** We have no before/after measurement on a real system.

If a reader takes away "DeepSeek's agent has a security hole," they have misread this document.

---

## 8. How to check this in ~30 minutes

```bash
git clone https://github.com/zmufo/servicevoxel-l1-evidence.git
cd servicevoxel-l1-evidence
bash verify.sh          # note: `bash verify.sh`, not `./verify.sh`
```

`verify.sh` requires only `python3` and its standard library. It re-runs the ten frozen criteria and prints TRUE/FALSE per criterion. The criteria are frozen with a SHA-256 recorded in `evidence/01-SILENCE/pre_run_gate_v1.0.json`, computed **before** judgment — so the criteria cannot be tuned to fit the results after the fact.

Current output: **10/10 TRUE**.

---

## 9. Questions we would like answered

1. Is there a single point between "Worker produced result" and "result becomes external fact or effect"? If it is not singular, where are the actual boundaries?
2. Do Workers currently carry any structured provenance with their results, or is the result text the only artifact?
3. Where would you prefer a deterministic pre-effect assertion to live — Worker side, Router side, or the effect-dispatch layer?

We are asking, not proposing to decide.

---

*Prepared by the ServiceVoxel working group. Corrections welcome — especially about §3.2.*
