# Correction to Discussion #1 (§3.2) — post as a comment, do not edit the original

> **Why a comment, not an edit.** The original post is already public. Editing it silently would
> make the published text differ from what readers saw, which is the same failure mode this
> project exists to flag. Corrections go **on top**, in the open.
>
> **Status: prepared, NOT yet posted.** Post before the follow-up.

---

## Comment text (paste as-is)

**Correction to §3.2 — including a correction to our own earlier correction**

We need to be precise here, because we got this wrong twice.

**1. What we originally said.** In Discussion #1 we used the phrase *"Effects queue"*
(transaction-enqueue / post-commit delivery) as the precise insertion anchor. We borrowed that
term; it was not something we had verified.

**2. Our first correction was overstated.** We then wrote that the term *does not appear in the
prototype's own materials* and withdrew it. **That went too far, and we withdraw the
withdrawal.** Multiple independent write-ups now describe a durable **Effects** queue in the
prototype: enqueue inside the transaction, execute after commit, one row per kind/key,
exponential backoff, `Later` for deferral. The component appears to be real.

What was actually wrong was our **anchor**, not the term's existence. The outbound delivery
point is a *separate* component: the **Outbox** (`src/app/outbox.ts`), whose `send()` is
described as writing the message receipt and the queued reply effect **in one transaction** —
so that "sent" and "recorded" are atomic.

| component | described role |
|---|---|
| **Effects** | general durable side-effect queue |
| **Outbox** | outbound receipts + delivery effects; atomic, ordered, retried |

Restated anchor:

> after the Engine accepts a Worker report, **before `Outbox.send()` enqueues**

**3. We also overstated the gap.** To avoid arguing against a position nobody holds: the
prototype already separates "result ready for review" from "collaboration finished" — there is a
`Report` state machine and a pending-review stage for tickets carrying a PR, plus strict
auto-merge constraints. We are **not** claiming it treats `ready` as delivered.

Our question is narrower: when a Worker's report carries a **natural-language factual
assertion** — "tests passed", "verified", "ready to merge" — where is the evidence for *that
assertion* checked?

A refinement that may make this easier to accept: `Channel` is described as typed
(`acknowledgement`, `answer`, `result`, `attention`). A fact gate could be scoped to
assertion-bearing channels (`result`, `answer`) and leave `acknowledgement` untouched, so normal
workflow is not obstructed.

**Limits we are keeping visible:** we could not fetch the source from our environment —
`raw.githubusercontent.com`, the `contents` API and the `blob` page were all unreachable.
Everything above is second-hand, from third-party write-ups. It must be confirmed against the
repository before being treated as fact. If a maintainer tells us the anchor is wrong, we will
say so publicly.
