# Authority Revocation probe

A small, deliberately dirty probe that isolates one question the delegation probe
(`examples/canon-fold-demo`, scenario 10 / finding G) raised but did not pull apart:

> When authority is revoked, what happens to an action that already *completed*
> under that authority?

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and adds **no sixth type, no wire format, no spec.**

```
python3 probe.py
```

## The scenario

A delegation chain with a real downstream party who relied on then-valid authority:

1. **T1** — the human (principal/buyer) grants agent A a scoped spending mandate
   (`AUTHORIZE consent.mandate`).
2. **T1** — agent A, acting *within the live mandate*, executes a purchase
   (`AUTHORIZE consent.execute`); payment and fulfillment complete. The merchant
   fulfills **in reliance on A's then-valid authority**.
3. **T2** — later, the human revokes A's mandate (`AUTHORIZE consent.withdraw`
   carrying `nullifies` — the existing field, event-registry §4.6).

Then the **same** completed purchase is re-projected three ways.

## The divergence (printed by the probe)

| view | reading of the revoke | authorized? |
|------|----------------------|-------------|
| before revocation | log as it stood at T1 | **True** |
| after — current-log, **retroactive cascade** | mandate void over its whole history; the act it backed collapses | **False** |
| after — **as-of-act-time** | replay as the log stood at the act; the revoke is not yet present | **True** |
| after — current-log, time-scoped (for contrast) | revoke is "going forward"; the act predates it | **True** |

The one signed revoke event produces **different answers** depending only on the
fold. That is the finding.

## What it exposes

- **Does revocation poison past authorized actions?** Only under the
  retroactive-cascade reading. The time-scoped / as-of-act-time reading preserves
  them. The canon picks neither.
- **Does it only affect future reliance?** Under the time-scoped reading, yes —
  "withdrawn going forward".
- **Can a later challenge reopen a past act without automatic global collapse?**
  Yes (step 5). A `CHALLENGE` + `ADJUDICATE` names *one* act by id. Revocation
  alone reopens nothing; reopening is a separate, scoped authority decision.
- **Is revocation an event-log fact, a projection result, or an authority decision?**
  All three, at different layers — and the probe keeps them apart:
  - the revoke is an **event fact** (one `AUTHORIZE consent.withdraw`);
  - whether it **cascades** onto a completed act is a **projection choice**;
  - whether that past act is **voided/punished** is an **authority decision** (`ADJUDICATE`).
- **Where is the boundary between buyer protection and anti-social-credit?**
  Honoring relied-upon authority (as-of-act-time) protects the good-faith
  counterparty. A permanent, automatic, identity-keyed retroactive collapse would
  be a stored verdict about a *party* — the social-credit shape ARC refuses. So
  ARC keeps revocation future-scoped by default and leaves reopening a specific
  past act to an explicit, per-act `ADJUDICATE`.

## Honest limits

This is a **probe, not doctrine.** It does not pick the "right" reading, does not
define a revocation spec, does not solve federation, and adds no universal
reputation semantics. The result is the same shape as findings B/C/D/G: the hard
case stays inside the five types, and what leaks out is a **fold-policy choice,
not a missing primitive.**
