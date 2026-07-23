# Cache-discipline probe

A small fixture that compares three authored cache shapes around one contextual
Projection. It demonstrates stale and cross-context reuse when a cache key omits
the Event-set and context inputs used by the fixture fold.

Stdlib only, single process, mock signatures, no network, and no persistent
storage. The cache values remain implementation data rather than Event records.

```
python3 probe.py
```

## The scenario

The log contains three positive outcome claims in context `groceries`, for which
the fixture fold returns `standing = good`. All three caches are seeded. The log
then receives a `CHALLENGE` and an `ADJUDICATE gov.suspension`, and the same cache
instances are read again.

Three cache shapes, distinguished only by their **key**:

| shape | key | behaviour |
|-------|-----|-----------|
| **ephemeral** | — (computes, stores nothing) | avoids cross-read staleness in this fixture; buys nothing across reads |
| **event-bound** | `(agent, context, event-id-set hash)` | a changed Event-id list misses in this fixture |
| **convenience** | `(agent,)` | does not bind to the Event list or context |

## What the probe prints

| failure (convenience cache) | result |
|------|--------|
| **1. stale after adjudication** — re-read `groceries` after the new records | serves the earlier `good` result instead of the current fixture fold |
| **2. cross-context reuse** — ask `electronics` (no outcome records there) | serves the cached `groceries` result |
| **3. missing freshness metadata** — inspect the cached value | value-identical to the earlier fold and carries no staleness marker |

Under this fixture's declared input list and fold policy, the ephemeral and
event-bound shapes match a fresh Projection (`suspended` / `unproven`); the
convenience cache reproduces all three stale or cross-context readings.

## What it exposes

- **The comparison is fixture-local.** The ephemeral shape computes on each read.
  The event-bound shape keys on the agent, context, and current fixture Event-id
  hash. The convenience shape keys only on the agent.
- **No shape establishes correctness by itself.** Reuse depends on which inputs
  the implementation includes, when it checks them, and whether Projection and
  policy versions are part of the cache identity.
- **A cached Projection remains derived data.** Treating it as current requires
  an implementation-level invalidation and integrity policy; the base Event
  model does not supply one.

## Limits

This fixture does not define a caching specification or select a cache policy.
It tests three authored shapes in one process, without network transport,
persistent storage, concurrent writes, hostile inputs, or cache-integrity checks.
