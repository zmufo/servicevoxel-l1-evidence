# Correction to Discussion #1 (§3.2) — post as a comment, do not edit the original

> **Why a comment, not an edit.** The original post is already public. Editing it silently would
> make the published text differ from what readers saw, which is the same failure mode this
> project exists to flag. Corrections go **on top**, in the open.

---

## Comment text (paste as-is)

**Correction to §3.2 — terminology, and a strengthening of the claim**

In §3.2 of the original post we wrote that the "Effects queue" mechanism we referred to is *not
described in the public article* and should be treated as an unvalidated hypothesis.

We are withdrawing that term. **"Effects queue" does not appear in the prototype's own
materials** — we borrowed it, and using it was careless on our part.

Secondary write-ups of the prototype's architecture docs describe the mechanism as a **durable
outbox backed by a single SQLite store, with replies queued and sent after the database
commit**. We have therefore restated our insertion anchor as:

> **before the outbox enqueues** — i.e. before the SQLite transaction commits

This actually *strengthens* the structural claim in §3.3: the point we proposed (after a Worker
produces a result, before that result becomes an external fact) now has a described mechanism
sitting on it rather than nothing.

Two caveats we want to keep visible:

1. This is **second-hand**. It comes from third-party technical write-ups, not from the
   repository's own architecture docs, which we still have not opened. We intend to read them
   before asserting anything as fact about your codebase.
2. We are **not** claiming you have a gap here. We are asking whether this reading is right.

Corrections on either point are welcome — that is most of why we posted.

— filed 2026-11-02

---

## What this changes elsewhere

| File | Change |
|---|---|
| `docs/integration-proposal.md` | §3.2 rewritten; term withdrawn; anchor restated |
| `docs/integration-proposal.zh.md` | same, Chinese |
| `docs/discussion-full.md` | **left unchanged** — it is the record of what was posted |

## What we deliberately did NOT do

- Did not edit the original Discussion post.
- Did not quietly swap the term in already-published text.
- Did not upgrade the claim from "hypothesis" to "confirmed" — it remains *supported by
  second-hand description*, not by source code.
