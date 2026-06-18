# Cache-discipline probe

A small, deliberately dirty probe that makes one of ARC's headline claims
executable — and shows where it bends:

> ARC's defense against becoming a social-credit database is that it **does not
> store the relationship** — standing is a Projection, recomputed on demand, never
> a stored record.

`object-model.md` §8 and canon-fold-demo's **finding B** already concede the soft
spot: a *cached* projection "can re-introduce a profile-shaped artifact," and call
that a **discipline question, not a primitive.** This probe pins that down on real
folds.

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types and adds **no sixth type and no stored standing
object.**

```
python3 probe.py
```

## The scenario

The agent earns three good outcomes in context `groceries` → a fresh fold returns
`standing = good`. All three caches are seeded. Then a dispute is adjudicated and
the community **suspends** the agent (`CHALLENGE` → `ADJUDICATE gov.suspension`).
The same caches are read again.

Three cache shapes, distinguished only by their **key**:

| shape | key | behaviour |
|-------|-----|-----------|
| **ephemeral** | — (computes, stores nothing) | safe by structure; never outlives a fold — but buys nothing across reads |
| **event-bound** | `(agent, context, event-set hash)` | a log change misses and refolds |
| **convenience** | `(agent,)` + a TTL | does not bind to the events or the context |

## What the probe prints

| failure (convenience cache) | result |
|------|--------|
| **1. revocation survival** — re-read `groceries` after suspension | serves `good` for a **suspended** agent |
| **2. context leakage** — ask `electronics` (zero evidence there) | serves the `groceries` standing → a universal score |
| **3. stale ≡ fresh** — compare the cached value | byte-identical to the earlier fresh fold; **no staleness marker** |

The ephemeral and event-bound caches return the correct (suspended / unproven)
answers; the convenience cache reproduces all three failures.

## What it exposes

- **Is "don't store the relationship" a *structural* defense?** Not on its own.
  The Event/Projection split prevents a stored profile only while caches are
  disciplined. The property is **contingent on cache shape** — finding B made
  executable and sharpened.
- **No shape is "absolutely safe."** *ephemeral* is safe only because it never
  persists (it is just recompute). *event-bound* merely **narrows** the staleness
  window; its correctness rests on three disciplines the canon does not enforce —
  the hash must cover every event the fold reads, it must be checked on **every**
  read, and context must be in the key. Relax any one and it slides toward the
  convenience failure; at its most correct it is indistinguishable from memoized
  recompute.
- **The stored-profile artifact needs no new primitive.** A suspended agent served
  as "good" is a stored status outliving its evidence — the social-credit shape —
  reached purely by undisciplined caching.
- **The deeper tension (finding-H shaped, on the projection layer):** the only safe
  rule is "never authoritative, always recompute," which negates the cache's reason
  to exist at the trust boundary. The safe cache and the useful cache pull against
  each other.

## Honest limits

This is a **probe, not doctrine,** and a **sharpening of finding B,** not a new
constitutional finding. It does not define a caching spec, does not pick a cache
policy, and adds no stored object. The result is the same shape as findings
B/C/D/G and the trust trilemma: the canon does not dissolve the problem, it
**relocates** it to caching discipline.
