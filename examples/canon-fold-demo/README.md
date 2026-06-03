# ARC Canon Fold Demo

> **Status:** Exploratory probe. Single Python file, standard library only, no
> dependencies. This is **not** an implementation of ARC and processes only
> mock data. Signatures are stubbed (a hash, not real cryptography).

A minimal working demonstration that tests whether the ARC canon survives
contact with code. It is the first executable artifact in the repo; everything
prior is documentation.

## What it tests

Eight claims from the canon, each made concrete — the eighth finds a limit:

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
   (+ `ATTEST`). No `KEY_ROTATION` primitive is introduced.
   (`docs/event-registry.md` §4.1, §4.6)

6. **Key revocation is `nullifies`, not a new type.** A compromised key is
   withdrawn by a `KEY` `id.key_revoke` event whose `nullifies` names the old
   key's register. Withdrawal is *time-scoped*: the key's past events stay
   readable, but anything it signs at/after the revoke timestamp drops out of
   the fold, so forged post-revocation events verify yet are never honored. A
   new key anchored by a rotation that preceded the revoke keeps its lineage. No
   `KEY_REVOKE` primitive is introduced — same field, read "going forward."
   (`docs/event-registry.md` §4.6)

7. **Caching a projection must not become a stored profile.** Caching is not in
   the canon and adds no event type; it is derived data. A cache is safe only if
   it is *ephemeral* (scoped to one replay, discarded) or *event-bound* (carries
   the `event_set_hash` it was computed over and is reused only as a hint while
   that hash matches). A *durable, unbound* cache is read without replay, cannot
   notice the event set change, and detaches from the log — it quietly becomes
   the score/status object the model refuses to keep. No cache is authority:
   even one asserting good standing cannot override an `ADJUDICATE`.
   (`docs/object-model.md` §10)

8. **Conflicting authorities are representable but not self-resolving** — the one
   claim that finds a *limit*. When two valid communities issue contradictory
   `ADJUDICATE` rulings about the same subject (A suspends, B warns), the five
   types record both fine — each is an ordinary, validly-signed `ADJUDICATE`, and
   both replay in the one shared log. No event is missing; this is not the
   locality case. But the canon does **not** pick a winner: a naive whole-log
   fold returns one answer only by keeping the latest ruling by timestamp (an
   accident), while an authority-scoped fold shows two valid, conflicting answers.
   Choosing the governing authority requires a selection / federation / bridge
   rule or a human-community choice — a policy *outside* the five event types.
   This is an authority-policy gap, not an event-type gap; a sixth type would not
   tell you which authority wins. (`docs/authority-and-conflict.md` §5)

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

A sixth scenario tests **key revocation**. A bakery merchant builds history
under `k:bakery_old`, rotates to `k:bakery_new`, then the old key is found
compromised and is withdrawn by a `KEY` `id.key_revoke` event whose `nullifies`
names the old key's register. The fold then reports: the old key's authority is
`honored_going_forward = False`; its *past* history still folds (the register
and pre-revoke events are kept); two **forged** events signed by the old key
*after* the revoke pass `verify_log` (the signature is valid) yet are dropped by
the fold, so their transaction never leaves `intent`; and the new key — anchored
by a rotation that *preceded* the revoke — keeps its lineage and carried-forward
standing. Revoke the key *before* rotating and the rotation event would itself
fall after the cutoff, orphaning the new key; ordering is the policy lever, not a
new type.

`nullifies` carries two readings of "going forward" from the same field: an
ordinary withdrawal voids its target outright (timeless), while a key revoke is
time-scoped against the revoke timestamp. That distinction is the one notable
finding — it is a fold-policy nuance, not a missing primitive.

A seventh scenario probes **replay cost / projection caching** — a different
axis: not "is the event canon enough?" but "does an optimization on *derived*
data smuggle back the stored profile?" It takes one real projection (the
bibimbap merchant standing) and wraps the result in three cache shapes, then
classifies each by shape: an **ephemeral** cache (not durable) is a *safe
optimization*; a **durable, unbound** cache (no `event_set_hash`) is *profile-
like reintroduction*; an **event-bound receipt** (`event_set_hash` +
`projection_name` + `subject` + `context` + `computed_at`) is *conditionally
safe*. Re-checked against a changed event set (the suspension `ADJUDICATE`
dropped, so the hash differs), the receipt self-invalidates and forces a
recompute, while the durable-unbound cache cannot even detect the change and
serves a stale answer. And no cache is authority: the durable one asserts
`in_good_standing`, yet the authoritative fold still reads `suspended` because
the `ADJUDICATE` is in the log. Caching is allowed, but only when scoped or
event-bound and never authoritative.

An eighth scenario is the adversarial one, and it **finds a limit** — by design,
the probe is allowed to fail usefully here. Two valid communities issue
conflicting `ADJUDICATE` rulings about the same subject `k:merchant_contested`:
community A `gov.suspension`, community B `gov.warning`. Both have valid `KEY`
roots, both rulings are validly signed, and **both are in the one shared log** —
so, unlike the locality scenario, no event is missing. The output shows three
readings: the naive whole-log fold returns `warned` (it merely kept the
later-timestamped ruling — an accident); `project_authority_context` under
authority A returns `suspended`, under authority B returns `warned`; and
`project_conflicting_governance` reports `conflict = True`, `canonical_winner =
None`. The five types *represent* the conflict without strain, but they do not
*resolve* it. "Verification is replay" guarantees both rulings are genuine; it
does **not** imply global agreement on which authority governs. Picking a winner
needs an authority-selection / federation / bridge rule or a human-community
choice — a policy outside the canon. ARC, by design, has no single final
authority, so the demo surfaces the conflict and stops there.

## What it found (the verdict)

For this slice, the canon largely held — with one honest limit (the eighth):

- The five types were sufficient to *represent* every scenario; no capability
  forced a sixth type. (Resolving competing authority is a separate matter — see
  the last bullet.)
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
- Key revocation needed no sixth type: a `KEY` `id.key_revoke` using the
  existing `nullifies` field withdrew the old key's forward authority without
  mutating any prior event or erasing its history. The one nuance worth naming:
  `nullifies` had to be read *time-scoped* for a key revoke (honored before the
  revoke, dropped at/after) versus *timeless* for an ordinary withdrawal — a
  fold-policy distinction, not a missing primitive. Holder authority over one's
  own key stayed separate from commons `ADJUDICATE`.
- Caching was nuanced, not free: it adds no event type, but it is only safe when
  the cache is ephemeral, or event-bound (`event_set_hash`) and treated as a
  hint. A durable, unbound cache *is* the stored profile/score/status the model
  refuses to keep — it just relocates the storage one layer out into derived
  data. So the §10 replay-cost tension resolves to a discipline, not a primitive:
  scope it, bind it to the event set, and never let it be authoritative. The
  `ADJUDICATE`-only rule for commons standing held even with a cache present.
- Conflicting authority is where the canon's reach ends — usefully. Two valid
  communities can issue contradictory `ADJUDICATE` rulings about one subject, and
  the five types *represent* the conflict without strain (both are ordinary,
  validly-signed `ADJUDICATE` events that replay). What they cannot do by
  themselves is *choose* which authority governs: a naive fold "resolves" the
  conflict only by timestamp accident, and the canon offers no principled winner
  (`canonical_winner = None`). The missing piece is an authority-selection /
  federation / bridge policy or a human-community choice — deliberately outside
  the event set, because ARC's design refuses a single final authority. **This is
  an authority-policy gap, not an event-type gap.** Adding a sixth type would let
  you *store* a verdict but still would not tell you whose verdict is right; the
  honest move is to surface the conflict, not to invent a primitive that hides it.

## Deliberate limitations

This probe does **not** attempt, and should not be read as solving:

- **Real cryptography.** Signatures are a hash stub, so "revoked key cannot
  sign" is enforced as a *toy fold policy* (drop events at/after the revoke
  timestamp), not by real key invalidation. A real deployment needs actual
  signature verification, trustworthy timestamps, and a propagation story for
  the revoke event itself; none of that is modeled here. Both key *rotation* and
  key *revocation* are now exercised in code.
- **Sybil resistance.** The fold includes a toy down-weight (trust counts only
  from *distinct* counterparties), gesturing at `object-model.md` §8. Real
  graph-shape heuristics (circularity, velocity, low diversity) are out of scope.
- **Portability, and the limits of the cache model.** Caching is now *probed*
  (seventh scenario), but only as a shape classifier: it labels a cache safe /
  conditionally safe / profile-like and shows event-bound self-invalidation. It
  does **not** implement a real cache layer, a propagation or eviction protocol,
  or measure actual replay cost; "durable vs ephemeral" is asserted by a flag,
  not enforced by storage. Event-set disagreement is *observed* (fourth scenario)
  but not *resolved*: the demo shows divergent-but-valid projections without
  proposing a reconciliation rule. Cross-community portability is still open.
- **Authority selection / federation.** The conflicting-`ADJUDICATE` scenario
  (eighth) *surfaces* competing authority but does not resolve it. No
  authority-selection policy, federation protocol, bridge rule, weighting, or
  precedence order is implemented or endorsed — `project_conflicting_governance`
  reports the disagreement and returns `canonical_winner = None` on purpose.
  Which authority a reader should honor, and how communities federate or bridge
  their rulings, is left entirely to policy outside the five event types.

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
