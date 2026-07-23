# ARC Canon Fold Demo

> **Status:** Exploratory probe. Single Python file, standard library only, no
> dependencies. This is **not** an implementation of ARC and processes only
> mock data. Signatures are stubbed (a hash, not real cryptography).

This exploratory fixture applies the current ARC object model to an authored
event set. It was the first executable artifact in the repository.

## What it tests

Eleven authored scenarios exercise the current model. The eighth records an
authority-selection gap, the ninth locates that choice in reader policy, and the
eleventh compares identity-policy trade-offs:

1. **This fixture derives a Relationship by folding a mock-signed Event log** — not a stored object.
   Reputation, standing, identity status, and transaction state are all
   *recomputed on demand* from the log and discarded. There is no score field,
   no profile object, no status column anywhere in the program.
   (`docs/object-model.md` §4–§6)

2. **The tested scenarios use five event types.** `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
   `ADJUDICATE` plus a `nullifies` field express identity, an offer, an
   approval, a payment claim, a fulfillment claim, reputation signals, a
   dispute, and a governance decision in these fixtures. Richness lives in
   `predicate` + `payload`, never in new top-level types.
   (`docs/event-registry.md` §4, §9)

3. **This governance Projection changes when ruling Events are added.** Injecting one
   governed dispute (`CHALLENGE` → `ADJUDICATE`) makes the *same* fold produce a
   *different* projection. Nothing already in the log is changed.
   (`docs/authority-and-conflict.md` §5)

4. **Override is a field, not a type.** The fixture includes a
   `consent.approval` `AUTHORIZE` whose `contrary_to` field references a warning
   record. Re-folding surfaces that reference without claiming what a person saw
   or understood. (`docs/event-registry.md` §4.3,
   `docs/authority-and-conflict.md` §7)

5. **The fixture expresses key rotation with `KEY`.** A key rotation is a `KEY`
   Event (`id.key_rotate`) attributed to the old signer label and naming the new
   label. The lineage policy carries records forward; past records stay readable and
   mock-signature-checkable, and a lineage
   read carries prior claim counts and identity readings under one optional
   policy. No separate `KEY_ROTATION` primitive is used.
   (`docs/event-registry.md` §4.1, §4.6)

6. **Key revocation is `nullifies`, not a new type.** A compromised key is
   withdrawn by a `KEY` `id.key_revoke` event whose `nullifies` names the old
   key's register. Withdrawal is *time-scoped*: the key's past events stay
   readable, but anything it signs at/after the revoke timestamp drops out of
   the fold. Post-revocation attempts still pass the deterministic mock-signature
   check but are not honored by this fold. A new key introduced by a rotation
   that preceded the revoke keeps its fixture lineage. No
   `KEY_REVOKE` primitive is introduced — same field, read "going forward."
   (`docs/event-registry.md` §4.6)

7. **Caching is derived state in this fixture.** The classifier distinguishes
   an ephemeral value, a durable unbound value, and an event-bound hint. An
   `event_set_hash` binds only one input dimension; reuse also depends on the
   Projection version, policy, ordering, context, available evidence, and
   implementation checks. A cached value does not issue or replace an
   `ADJUDICATE`.
   (`docs/object-model.md` §10)

8. **Conflicting authorities are representable but not self-resolving.** When two
   configured community keys issue contradictory
   `ADJUDICATE` rulings about the same subject (A suspends, B warns), the five
   types record both as ordinary, mock-signed `ADJUDICATE` Events in one supplied
   Event set. Unlike the locality scenario, neither authored ruling is
   intentionally removed. Base ARC does not pick a winner: a naive whole-log
   fold returns one answer only by keeping the latest ruling by timestamp, while
   an authority-scoped fold shows two conflicting fixture readings.
   Choosing the governing authority requires a selection / federation / bridge
   rule or a human-community choice — a policy *outside* the five event types.
   This is an authority-policy gap, not an Event-shape result.
   (`docs/authority-and-conflict.md` §5)

9. **The resolution gap belongs to policy, not to the event canon.** Building on
   the eighth, three *illustrative* reader policies resolve the very same
   conflicting log — `subscriber-choice` (honor the authority you subscribe to),
   `most-restrictive-wins` (a fixture ordering over recorded ruling predicates),
   and `explicit-precedence` (a reader-supplied ordering).
   The same log yields different fixture labels under different policies; the
   resolution happens entirely in a layer *above* the canon, reading the
   per-authority projections without adding or changing any event. ARC endorses
   **none** of these — they only show the choice is a reader / community /
   federation / bridge concern. This does not dissolve the eighth's limit: the
   base ARC still does not pick a winner.
   (`docs/authority-and-conflict.md` §5)

10. **The fixture expresses delegated authority with `AUTHORIZE`.** An authored
    human-principal key records a scoped, time-bounded `AUTHORIZE` (`consent.mandate`)
    carrying `scope` (category + budget + expiry + a `redelegatable` flag); an
    agent sub-delegates a *narrower* mandate; revocation is the existing
    `nullifies` field. The fold walks each mandate chain back to the human
    principal — whose authority over their own action is inherent — and enforces
    scope-, time-, and redelegation-bounds: over-budget, wrong-category, and
    expired requests are denied, a sub-grant may only narrow, and a forbidden
    re-grant is *represented* yet not *honored*. No `CAPABILITY` / `DELEGATE` /
    `AUTHORITY_TOKEN` primitive. This scenario compares an earlier historical
    authority baseline with the mandate-force view from the full current log;
    they are different event sets, not competing answers about one completed
    act. It emits no completed B act. The same-full-log preserve/cascade honoring
    question is isolated in `examples/authority-revocation-demo`.
    (`docs/delegation-and-spending-mandates.md`, `docs/event-registry.md` §4.3)

11. **Agent multiplication exposes a fixture-policy limit.** One actor
    can run many agents, so many signer labels need not mean many independent
    counterparties. This optional fixture policy counts distinct signer labels
    and groups them only when its Event set contains an `ATTEST` `id.controls`.
    The result is asymmetric: a
    cluster that discloses shared control receives a lower fixture label
    (`higher_fixture_signal` → `insufficient_fixture_signal`); a cluster that
    discloses nothing keeps its prior signal. This fixture does not infer an
    undisclosed shared root. Stored identity graphs, cost gates, or other
    deduplication mechanisms would be separate application/profile policies.
    (`object-model.md` §8, `docs/threat-model.md`)

## Run

```sh
python3 demo.py
```

No install step. Requires Python 3.10+.

## What you should see

The demo builds an authored Event set (a KRW local-food scenario: one bibimbap
merchant, four consumers), runs the Projections, then appends a fourth
transaction with a payment-result claim, no fulfillment claim, a challenge, and
a ruling. The same folds are re-run. Between the two runs:

| Projection | Before | After | Why |
| --- | --- | --- | --- |
| advisory signal | `higher_fixture_signal` | `mixed_fixture_signal` | a negative outcome claim + a challenge entered the fold |
| governance reading | `no_applicable_ruling` | `suspension_ruling_recorded` | an `ADJUDICATE` was added |
| identity reading | `key_recorded` | `suspension_ruling_recorded` | folded from `KEY` + `ADJUDICATE`, recomputed |
| tx_4 reading | `no_transaction_record` | `ruling_recorded` | folded from that transaction's Events |

The two halves of the standing view are kept deliberately separate:

- **advisory signal** is a fixture-policy label over recorded claim counts and
  signer labels. It is not a trust determination and has no authority of its own
  (`authority-and-conflict.md` §5).
- **governance reading** reports an applicable recorded ruling under this
  fixture policy, or `no_applicable_ruling`. It does not infer positive standing
  from the absence of a ruling.

A third scenario then exercises override-against-warning: a brand-new merchant
folds to `advisory = insufficient_fixture_signal`, and an authored `AUTHORIZE`
record carries `contrary_to` pointing at the warning record. The fold reports
`override_detected = True` while the merchant's governance reading stays
`no_applicable_ruling`. The fixture establishes the reference relationship, not
what a person saw or understood.

A fourth scenario observes **event-set disagreement**. The *same* merchant is
folded against two different subsets of the log: Community A holds the full log;
Community B received everything except the suspension `ADJUDICATE`. Each subset
passes the fixture's deterministic mock-signature and signer-registration checks,
yet they disagree: A reads `suspension_ruling_recorded` for governance and
identity, while B reads `no_applicable_ruling` / `key_recorded`. The demo only
observes the difference; it does not resolve it.

Event-set disagreement is a property of locality, not necessarily a bug.
This fixture's replay check and fold agree only over a *shared* event set; a
different replay input can produce a different Projection. Whether two divergent
views should be reconciled is left open here (see `object-model.md` §10).

A fifth scenario tests **key rotation / authored key lineage**. A cafe merchant
builds standing under `k:cafe_old`, then rotates to `k:cafe_new` via a `KEY`
`id.key_rotate` Event attributed to the old signer label under the mock-signature
check. Three readings are printed side by side: the old key folds to
`higher_fixture_signal` / `key_recorded`; the new key alone folds to
`insufficient_fixture_signal` / `no_key_record`; and a lineage fold reads the
rotation chain and carries the earlier fixture signal to the new key. This is a
policy illustration, not external identity verification.

The lineage fold shown is *one* policy (full carry-forward). Partial carry,
standing-only, or no auto-carry are all expressible by changing what the lineage
fold counts. The demo links signer labels and observes the readings; it does
not declare which carry-forward policy is correct.

A sixth scenario tests **key revocation**. A bakery merchant builds history
under `k:bakery_old`, rotates to `k:bakery_new`, then the old key is found
compromised and is withdrawn by a `KEY` `id.key_revoke` event whose `nullifies`
names the old key's register. The fold then reports: the old key's authority is
`honored_going_forward = False`; its *past* history still folds (the register
and pre-revoke Events are kept); two post-revocation attempts attributed to the
old signer label pass the deterministic mock-signature check yet are dropped by
the fold, so their transaction stays `no_transaction_record`; and the new key — introduced
by a rotation that *preceded* the revoke — keeps its lineage and carried-forward
standing. Revoke the key *before* rotating and the rotation event would itself
fall after the cutoff, orphaning the new key; ordering is the policy lever, not a
new type.

`nullifies` carries two readings of "going forward" from the same field: an
ordinary withdrawal takes its target out of force however old it is, while a key
revoke is time-scoped against the revoke timestamp. That distinction is the one
notable finding — it is a fold-policy nuance, not a missing primitive. Either
way the fold honors a `nullifies` only from the target's author or its rotation
lineage (event-registry §4.6); anyone else's withdrawal is evidence, not effect.

A seventh scenario probes **replay cost / projection caching** — a different
axis: not "is the event canon enough?" but "does an optimization on *derived*
data smuggle back the stored profile?" It takes one fixture Projection (the
bibimbap merchant standing) and wraps the result in three cache shapes, then
classifies each by shape: an **ephemeral** cache (not durable) has *no cross-read
reuse*; a **durable, unbound** cache (no `event_set_hash`) is *profile-
like reintroduction*; an **event-bound receipt** (`event_set_hash` +
`projection_name` + `subject` + `context` + `computed_at`) is an *event-bound
hint*. Re-checked against a changed event set (the suspension `ADJUDICATE`
dropped, so the hash differs), an implementation must treat the receipt as stale
and recompute, while the durable-unbound cache cannot detect that input change
and serves its stored value. The cached value does not replace a fresh Projection
under the declared Event set, Projection version, policy, ordering, and context
inputs.

An eighth scenario records an unresolved authority-selection case. Two configured
community keys issue
conflicting `ADJUDICATE` rulings about the same subject `k:merchant_contested`:
community A `gov.suspension`, community B `gov.warning`. Both KEY records and
both ruling records pass the fixture's mock checks and are in one Event set —
so, unlike the locality scenario, no event is missing. The output shows three
readings: the naive whole-log fold returns `warning_ruling_recorded` (it kept the
later-timestamped ruling — an accident); `project_authority_context` under
authority A returns `suspension_ruling_recorded`, under authority B returns
`warning_ruling_recorded`; and
`project_conflicting_governance` reports `conflict = True`, `canonical_winner =
None`. The current types record the conflict, but they do not
*resolve* it. The fixture checks both mock-signed ruling records; it
does **not** imply global agreement on which authority governs. Picking a winner
needs a reader's authority-selection / federation / bridge policy. Base ARC does
not select a universal final authority, so the demo surfaces the conflict and
stops there.

A ninth scenario then shows *where* that resolution lives — in a policy layer
above the canon, not in a new event type. The same conflicting log is run through
three illustrative reader policies: `subscriber-choice` (subscribe to A →
`suspension_ruling_recorded`; subscribe to B → `warning_ruling_recorded`),
`most-restrictive-wins` (the fixture ordering selects the suspension record),
and `explicit-precedence` (the supplied authority order selects one record).
Five resolutions, two distinct outputs, all from the
*same* untouched events — only the selection rule differs. The point is narrow and
deliberate: the gap from scenario 8 is fillable by a reader / community /
federation / bridge choice, and ARC
endorses none of the three policies. This is shown the same way the rotation
scenario showed carry-forward as one policy among several: the demo demonstrates
that the choice is *expressible* as policy, and declines to pick one.

A tenth scenario probes **delegated authority**. A human principal issues a
scoped, time-bounded `AUTHORIZE` `consent.mandate` (category `food`, a budget, an
expiry, `redelegatable = True`) to Agent A; A sub-delegates a narrower,
non-redelegatable mandate to Agent B; B then tries to grant Agent C. The fold
walks each mandate chain back to the principal — whose authority over their own
action is inherent — and enforces the bounds: over-budget, wrong-category, and
expired requests are denied, a sub-grant may only narrow, and B's attempt to
grant C is recorded as an `AUTHORIZE` but not honored by this fold, because B's
mandate forbade redelegation. Revocation is the existing `nullifies` field:
withdrawing one of A's mandates leaves the others intact, and withdrawing A's
food mandate collapses B's downstream authority. The earlier event subset shows
that B held authority before the revoke; the full current log shows that B's
downstream authority is no longer in force. Those are different event sets and
different authority-state questions. Because this scenario emits no completed B
act, completed-act honoring is left to the same-full-log preserve/cascade
comparison in `examples/authority-revocation-demo`. No `CAPABILITY` / `DELEGATE`
primitive is added.

An eleventh scenario examines **agent multiplication / Sybil amplification**.
One actor can run many agents, so distinct signer labels do not establish
independent counterparties. Two clusters each post three positive `rep.outcome`
claims to a target. The naive fixture policy assigns both targets
`higher_fixture_signal`. One cluster also supplies an `ATTEST` `id.controls`, so
the root-aware policy groups its three signer labels and returns
`insufficient_fixture_signal`; the cluster with no shared-root record remains
unchanged. This is an input asymmetry, not a base ARC Sybil policy. A third
reading applies an optional, fallible burst-review trigger and no automatic
penalty.
This fixture begins evaluating an actor when its supplied event set contains shared
records about that actor. Local activity outside that supplied set is not observable
to this Projection.

## What it found (the verdict)

These authored scenarios used the current five Event types plus `nullifies`; none
required another current Event type. This is bounded fixture coverage, not a
general sufficiency result.

- The deterministic replay check covers only identifiers, mock signatures, and
  signer-label registration. It does not verify external claims, keys, anchors,
  identities, payments, fulfillment, or Event-set completeness.
- The Projections are recomputed without a stored profile or score. Identity,
  transaction, reputation, and governance outputs are labeled as fixture
  readings or recorded claims rather than external facts.
- `contrary_to`, key rotation, key revocation, delegation, and conflicting ruling
  records are exercised with the current fields and predicates. The carry-forward,
  revocation, and authority-selection readings remain named fixture policies.
- Cache classification is limited to the three authored shapes. An event-set hash
  binds one input dimension; reuse still depends on Projection version, policy,
  ordering, context, evidence availability, and implementation checks.
- The agent-multiplication scenario shows that distinct signer labels do not
  establish independent counterparties. Its disclosed-root grouping and burst
  review are optional local policies, not base ARC requirements.

## Deliberate limitations

This probe does **not** attempt, and should not be read as solving:

- **Real cryptography.** Signatures are a hash stub, so "revoked key cannot
  sign" is enforced as a *toy fold policy* (drop events at/after the revoke
  timestamp), not by real key invalidation. A deployment profile needs real
  signature verification, declared time/ordering assumptions, and a propagation
  policy for the revoke Event; none of that is modeled here.
- **Sybil resistance.** The fold includes an optional threshold over claim counts
  from distinct signer labels; it does not establish distinct counterparties.
  The eleventh scenario probes its agent-granularity limit: many agents under
  one actor defeat the distinct-signer count unless their shared root is
  voluntarily disclosed — and shows the collapse is asymmetric and the review
  trigger heuristic. It does **not** implement real graph-shape heuristics
  (circularity, velocity, low diversity), a stored identity graph, or a cost
  gate; certain agent-level Sybil resistance is explicitly out of scope, treated
  as an application-policy trade-off rather than a solved problem.
- **Portability, and the limits of the cache model.** Caching is now *probed*
  (seventh scenario), but only as a shape classifier: it labels a cache as no
  cross-read reuse / event-bound hint / profile-like reintroduction and reports
  whether the declared event-set hash matches. It
  does **not** implement a real cache layer, a propagation or eviction protocol,
  or measure actual replay cost; "durable vs ephemeral" is asserted by a flag,
  not enforced by storage. Event-set disagreement is *observed* (fourth scenario)
  but not *resolved*: the demo shows divergent Projection outputs without
  proposing a reconciliation rule. Cross-community portability is still open.
- **Authority selection / federation.** The conflicting-`ADJUDICATE` scenario
  (eighth) *surfaces* competing authority; the ninth *illustrates* three reader
  policies that could resolve it (`subscriber-choice`, `most-restrictive-wins`,
  `explicit-precedence`). Those are illustrative examples, none endorsed:
  `project_conflicting_governance` still returns `canonical_winner = None` on
  purpose, and ARC selects no canonical policy. A real federation protocol,
  bridge / weighting scheme, declared authority relationships, or governance for
  *how readers agree on a policy* is **not** modeled — the demo only shows the
  choice is expressible in a layer above the canon. Which authority a reader
  should honor remains a policy/community decision outside the five event types.

The override-against-warning path is exercised in the third scenario.

## Why Python (and when TypeScript)

Decided 2026-06-01: use Python for this exploratory fixture and TypeScript for a
possible hardened implementation. Python keeps the fold readable and dependency-
free. A future TypeScript port could add local discriminated-union checks; it
would not by itself establish protocol conformance.

## Relationship to the other example

`examples/local-commerce-demo/` is a set of **mock JSON artifacts** describing
scenarios (happy path, new merchant without a declared anchor, payment failure,
collusion, …). This
demo is **executable**: it folds an Event set and shows Projections change. The
artifacts describe authored scenarios; this probe computes fixture readings over
its authored inputs.
