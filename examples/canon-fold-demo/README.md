# ARC Canon Fold Demo

> **Status:** Exploratory probe. Single Python file, standard library only, no
> dependencies. This is **not** an implementation of ARC and processes only
> mock data. Signatures are stubbed (a hash, not real cryptography).

A minimal working demonstration that tests whether the ARC canon survives
contact with code. It is the first executable artifact in the repo; everything
prior is documentation.

## What it tests

Three claims from the canon, each made concrete:

1. **A Relationship is a fold over a signed Event log** — not a stored object.
   Reputation, standing, identity status, and transaction state are all
   *recomputed on demand* from the log and discarded. There is no score field,
   no profile object, no status column anywhere in the program.
   (`docs/object-model.md` §4–§6)

2. **Five event types suffice.** `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
   `ADJUDICATE` plus a `nullifies` field express identity, an offer, an
   approval, a payment claim, a fulfillment claim, reputation signals, a
   dispute, and a governance decision — with no sixth type. Richness lives in
   `predicate` + `payload`, never in new top-level types.
   (`docs/event-registry.md` §4, §9)

3. **Governance works by adding events, never by mutating state.** Injecting one
   governed dispute (`CHALLENGE` → `ADJUDICATE`) makes the *same* fold produce a
   *different* projection. Nothing already in the log is changed.
   (`docs/authority-and-conflict.md` §5)

4. **Override is a field, not a type.** When a projection raises a friction
   warning and a human approves anyway over their own risk, the record is an
   ordinary `consent.approval` `AUTHORIZE` carrying `contrary_to` — not a new
   event type. The override grants no commons authority and changes no party's
   standing; re-folding later still surfaces that the approval was made against
   a warning. (`docs/event-registry.md` §4.3, `docs/authority-and-conflict.md` §7)

5. **Identity continuity survives key rotation with no sixth type.** A key
   rotation is a `KEY` event (`id.key_rotate`) signed by the old key, naming the
   new key. Provenance carries forward, past events stay valid, and a lineage
   read recovers the prior reputation, standing, and identity — all from `KEY`
   (+ `ATTEST`, with `nullifies` available for the revoke case). No
   `KEY_ROTATION` primitive is introduced. (`docs/event-registry.md` §4.1, §4.6)

## Run

```sh
python3 demo.py
```

No install step. Requires Python 3.10+.

## What you should see

The demo builds a hand-written log (a KRW local-food scenario: one bibimbap
merchant, four consumers), runs the projections, then appends a fourth
transaction that is paid-but-not-fulfilled, disputed, and adjudicated. The same
folds are re-run. Between the two runs:

| Projection | Before | After | Why |
| --- | --- | --- | --- |
| advisory signal | `trusted` | `limited` | a negative outcome + an open dispute entered the fold |
| governance standing | `in_good_standing` | `suspended` | **only** because an `ADJUDICATE` was added |
| identity status | `verified` | `suspended` | folded from `KEY` + `ADJUDICATE`, recomputed |
| tx_4 state | `intent` | `resolved` | folded from that transaction's events |

The two halves of the standing view are kept deliberately separate:

- **advisory signal** is a computed risk hint. It may raise friction; it may not
  punish. A projection has no authority of its own (`authority-and-conflict.md`
  §5).
- **governance standing** is a commons fact that *only* an `ADJUDICATE` can
  change. No projection and no ordinary key can produce a suspension.

A third scenario then exercises override-against-warning: a brand-new merchant
folds to `advisory = unproven` (a friction signal), the human approves anyway,
and the approval is recorded as an `AUTHORIZE` with `contrary_to` pointing at
the warning. The fold reports `override_detected = True` while the merchant's
`governance standing` stays `in_good_standing` — the override accepted personal
risk without touching the commons.

A fourth scenario observes **event-set disagreement**. The *same* merchant is
folded against two different subsets of the log: Community A holds the full log;
Community B received everything except the suspension `ADJUDICATE`. Each subset
replays correctly on its own (signatures and provenance check out), yet they
disagree — A reads `suspended` / `suspended`, B reads `in_good_standing` /
`verified`. The demo only observes the difference; it does not resolve it.

Event-set disagreement is a property of locality, not necessarily a bug.
"Verification is replay" guarantees agreement only over a *shared* event set; a
different replay input is a different — but still valid — projection. Whether two
divergent views should be reconciled, or are the expected consequence of local
trust, is left open here (see `object-model.md` §10).

A fifth scenario tests **key rotation / identity continuity**. A cafe merchant
builds standing under `k:cafe_old`, then rotates to `k:cafe_new` via a `KEY`
`id.key_rotate` event signed by the old key. Three readings are printed side by
side: the old key still folds to `trusted` / `verified` (its history is intact);
the new key *alone* folds to `unproven` / `unverified` (a stranger if the link
is ignored); and a lineage fold — which reads the rotation chain — recovers
`trusted` / `verified` for the new key. Continuity is carried forward with no
external cost gate and no sixth type.

The lineage fold shown is *one* policy (full carry-forward). Partial carry,
standing-only, or no auto-carry are all expressible by changing what the lineage
fold counts. The demo links the identities and observes the readings; it does
not declare which carry-forward policy is correct.

## What it found (the verdict)

For this slice, the canon held:

- The five types were sufficient; no capability in the scenario forced a sixth.
- Projection-on-demand worked with no stored profile or score.
- "Verification is replay" was real: every run re-checks signatures and key
  provenance before folding, and any party folding the same events gets the
  same view.
- Governance-by-appending worked: the `ADJUDICATE` dominated the governance
  portion of the standing view without touching prior events, and demoting it
  to an `ATTEST` would have lost exactly the commons authority the canon
  reserves for it.
- Override needed no new type: an `AUTHORIZE` with `contrary_to` carried the
  "approved against a warning" fact, kept it auditable on re-fold, and left
  commons standing untouched — confirming override is a field, not a primitive.
- Key rotation needed no sixth type: a `KEY` `id.key_rotate` anchored the new
  key and the rotation chain carried reputation, standing, and identity forward.
  The existing single-key folds ran unchanged; only a small lineage reader was
  added. The five types passed this re-test of sufficiency.

## Deliberate limitations

This probe does **not** attempt, and should not be read as solving:

- **Real cryptography.** Signatures are a hash stub. Key *rotation* is exercised
  (provenance carry-forward), but key *revocation* — the `nullifies` / `KEY`
  `id.key_revoke` case — is described, not run, so the chain stays walkable.
- **Sybil resistance.** The fold includes a toy down-weight (trust counts only
  from *distinct* counterparties), gesturing at `object-model.md` §8. Real
  graph-shape heuristics (circularity, velocity, low diversity) are out of scope.
- **Portability and caching.** Of the known tensions in `object-model.md` §10,
  replay cost and caching re-introducing a profile are untouched here. Event-set
  disagreement is now *observed* (fourth scenario) but not *resolved*: the demo
  shows divergent-but-valid projections without proposing a reconciliation rule.

The override-against-warning path *is* exercised (see the third scenario above);
it is no longer a gap.

A failed result would have been useful too; this one happens to pass for the
slice it covers.

## Why Python (and when TypeScript)

Decided 2026-06-01: **exploration = Python, hardening = TS.** This demo's job is
to probe whether the canon survives execution, where readability of the fold and
zero ceremony matter most. If it graduates into a reference implementation, the
port to TypeScript — with the event types as a discriminated union — becomes a
second, stricter test of whether the five types are genuinely closed.

## Relationship to the other example

`examples/local-commerce-demo/` is a set of **mock JSON artifacts** describing
scenarios (happy path, fake merchant, payment failure, collusion, …). This
demo is **executable**: it folds an event log and shows projections change. The
two are complementary — the artifacts describe *what should happen*; this probe
tests whether the canon's machinery can *compute* it.
