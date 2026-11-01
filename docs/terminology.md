# Terminology: ServiceVoxel is *not* "体素" (voxel)

> **中文版为准。** This file is the English version; `terminology.zh.md` is authoritative.
> Both carry the same definitions.

## 1. The problem

`ServiceVoxel` contains the substring **"Voxel"**.

In computer graphics, **voxel** is a standard term meaning *volumetric pixel* — the
three-dimensional analogue of a pixel, a sample point on a regular grid in 3D space.
Its established Chinese translation is **体素 (tǐ sù)**.

Our term is **体元 (tǐ yuán)**.

Both contain 体. A Chinese reader who sees `ServiceVoxel` will, with good reason,
assume it renders as 体素 and read the whole project as something to do with 3D
graphics, volumetric rendering, or spatial data structures.

**It is not.** This document states, once and in a checkable form, what 体元 means and
what it does not mean.

## 2. What 体元 means

| Component | Meaning | Not |
|---|---|---|
| **体** | 业务体 / 服务体 — a *body of service*, i.e. one bounded business engagement (one dispatch, one fulfilment, one closed-loop task) | **Not** 体积 (volume / spatial extent) |
| **元** | 元 — the smallest indivisible unit; the atomic element that cannot be further decomposed | **Not** 元素 in the chemical sense, **not** 像素 (pixel) |

**体元 = the smallest indivisible unit of a service body.**

Concretely: the minimum unit of a business fact that carries an assertable
truth-value — who promised what to whom, under which time window, against which
object, and what was actually delivered.

Two coordinates are always kept separate, and this separation is the point:

- **派单坐标 (dispatch coordinate)** — the promised / nominal value
- **履约坐标 (fulfilment coordinate)** — the actually delivered value

A 体元 records both without collapsing either into the other.

## 3. Comparison table

| | 体素 / voxel (graphics) | 体元 / ServiceVoxel (this project) |
|---|---|---|
| Domain | Computer graphics, volumetric rendering, medical imaging | Service governance, fact adjudication |
| What it names | A sample point on a 3D grid | An atomic unit of business fact |
| Spatial? | Yes — defined by x,y,z position | No — defined by identity, time window, and object |
| Has a truth-value? | No — it is a data sample | Yes — it is either adjudicated or un-adjudicated |
| Key operation | Rendering, interpolation, ray marching | Evidence eligibility check, coordinate separation |
| Chinese | 体素 **tǐ sù** | 体元 **tǐ yuán** |

## 4. Why the English name still contains "Voxel"

This is a deliberate, imperfect choice, and we state it plainly rather than defend it.

The word was chosen for the **metaphor of composability**: a voxel is the smallest unit
out of which a volume is built; a 体元 is the smallest unit out of which an auditable
service record is built. The metaphor is about *granularity and composability*, nothing else.

The metaphor does **not** extend to:

- spatial position or geometry
- rendering or visualisation
- volumetric data structures
- grid sampling

**The Chinese term 体元 is the definitional one.** The English `ServiceVoxel` is a
proper name; if the two ever diverge, 体元 governs.

## 5. Rendering rules

- **Do not translate ServiceVoxel as 体素.** This is the single most consequential rule here.
- When writing in Chinese, use **体元** on first occurrence; `ServiceVoxel` may follow in parentheses.
- When writing in English, use **ServiceVoxel** on first occurrence; a gloss such as
  *"体元 — atomic unit of service fact, unrelated to graphics voxels"* is welcome and encouraged.
- Never write **服务体素**. That string is wrong and should be corrected wherever it appears.

## 6. Why this file exists at all

A project whose entire claim is *"a conclusion must carry evidence eligibility before it
becomes a fact"* cannot tolerate its own central term drifting into a different concept.

An unresolved naming collision is the same failure mode this repository exists to
catch: **one label pointing at two different things.** If `ServiceVoxel` is quietly read
as 体素 by half its audience, then every downstream statement about it becomes
ambiguous — and no amount of hash verification downstream can repair an ambiguity
introduced at the naming layer.

So the collision is declared here, in the open, before it propagates.

---

*Related: `integration-proposal.md` (English entry point), `terminology.zh.md` (authoritative Chinese).*
