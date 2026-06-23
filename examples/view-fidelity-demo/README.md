# View fidelity probe — WYSINWYS

A small, deliberately dirty probe on a wall the signer never sees coming:

> **What You See Is Not What You Sign.**
> A signature seals the signed bytes. It does not seal the displayed view.
> Same bytes, different view. **deterministic ≠ faithful.**

Stdlib only, single process, mock signatures, no network, no storage. It reuses the
canonical event types and the `view_hash` / `refs` content hashes, and adds **no new
event type, no "view object", no view score** — a rendered-view attestation is an
ordinary `ATTEST` predicate.

```
python3 probe.py
```

## The failure is in the render layer, not the signer

The signer is **not malicious**, the **key is sound**, and the signed canonical bytes
**B are not tampered with**. And yet, if the view-generator / summarizer / UI renderer
between the bytes and the eyes is lossy or adversarial, the view the signer **saw** and
the bytes the signer **signed** diverge. `render(B) ≠ B`, and only the bytes are signed.

## This is not finding M, and it is the residue under finding L

- **Finding M** (`../reference-client/signer_fidelity_fixture.py`) — the signer SEES B
  in full and **interprets** it unfaithfully; the fault is *reading*. Here the signer
  reads faithfully but is shown `render(B) ≠ B`; the fault is one step earlier, in
  *presentation*. M's signer is omniscient about B and varies in reading; this signer is
  **blind to B** and sees only `render(B)`.
- **Finding L** (`../reference-client/approval_seam_fixture.py`) — the escalation return
  path owes the human a "sign what you saw" property: one projection for both review and
  signing. But that mitigation **assumes a faithful renderer.** Bytes are not human-
  cognizable (JSON, hashes, addresses), so *some* renderer is unavoidable, and L silently
  trusted it. This probe pricks exactly that trust dependency — it is the residue **under**
  L's mitigation, not a restatement of it.

## The one thing the log can check, and the one it cannot

ARC can bind a `view_hash` into the signed payload and let anyone recompute it from a
**pinned deterministic renderer**. That folds. But the hash certifies **correspondence**
to the pinned renderer's output — never the **fidelity** of that renderer.

## What the probe prints

| readout | what happens | verdict |
|---------|--------------|---------|
| 1. boundary | the log holds B and `id=hash(B)`; no view | resolve-view-from-log **UNKNOWN** |
| 2. faithful render | a faithful renderer shows the critical fields | sign-what-you-saw holds — *by assumption* |
| 3. WYSINWYS attack | same signed action, an adversarial renderer rewrites the payee | **verify passes**, view UNFAITHFUL, money to attacker |
| 4. view_hash (half) | careless attacker commits the doctored view's hash | **CAUGHT** — claimed ≠ recomputed |
| 5. the residue | pinned renderer reproducibly OMITS the payee | **MATCH**, verify passes, view still UNFAITHFUL |
| 6. mitigation price | a `rendered_view` ATTEST is added | **CLAIMED** — one more record, trust relocated |

Plus the price, in full:

- **rendered_view ATTEST / signed preview / renderer attestation** are more signed
  records. They **relocate** trust into the renderer (or a runtime attestor) — exactly
  finding M's attested-signer, finding O's head-oracle, the world-axis trusted-oracle.
  None proves the human's eyes received a faithful view. The renderer is a **mandatory
  trust dependency**: for any human approval, a renderer is always in the trusted base,
  and ARC does not govern it.

## What it exposes

- **A genuine signature cannot certify the view.** It seals the bytes B; `render(B)`
  runs off-log and never enters the signature.
- **ARC is not blind to the view.** A `view_hash` recomputed from a pinned renderer
  catches a *careless* mismatch — the render-correspondence layer folds.
- **deterministic ≠ faithful.** A renderer that reproducibly omits a critical field
  hashes consistently; an honest commitment over it matches on recompute, and the view
  is still unfaithful. The hash proves the view came from the renderer, never that the
  renderer is faithful — the same shape as finding M, on the render layer.
- **The renderer is a mandatory, ungoverned trust dependency**, and below it the human's
  perception is unreachable from the log.

## Honest limits

This is a **probe, not doctrine.** Signatures are **mock**: the point is the gap between
bytes and view, not custody — but `id` and `view_hash` are **real content hashes**, so
the recompute check genuinely bites. What each signer actually *saw*, and whether it was
*faithful*, live in an omniscient strip **no observer and no fold can read** — exactly
the gap the probe is about. ARC can **preserve** a view claim — bind a `view_hash` into
the bytes, recompute it from a pinned renderer — but it cannot make the displayed view
**faithful**, and it cannot reach the human's perception.

**Standing — not promoted to a finding letter.** This looks like a sharpening of findings
L and M with one narrow new wrinkle: the renderer as a mandatory, off-log, deterministic-
yet-unfaithful trust dependency at the presentation layer (a candidate "P", to be judged
after review, not asserted here). The signature seals the signed bytes, never the
displayed view.
