# Authority Revocation probe

A small, deliberately dirty probe that isolates one question the delegation probe
(`examples/canon-fold-demo`, scenario 10 / finding G) raised but did not pull apart:

> After authority is revoked, does a current reader continue to honor an action
> that already *completed* under that authority?

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

The as-of-act-time fold establishes a historical baseline from an earlier event
subset. After revocation, the same full current log is projected under preserve
and cascade policies.

## The invariant facts and policy choice (printed by the probe)

The historical baseline is an **earlier event subset**: it replays the log as of
the act, before the later revoke exists. It establishes
`authorized_at_act=True`; it is not the same-events policy comparison.

Against the **same full current log**, both policies agree on the facts and differ
only on current honoring:

| policy | authorized_at_act | mandate_in_force_now | completed_act_honored_now |
|--------|-------------------|-----------------------|---------------------------|
| preserve | **True** | **False** | **True** |
| cascade | **True** | **False** | **False** — not honored by this projection |

The historical authorization fact and current mandate state do not diverge. The
reader policy for honoring the completed act does. That is the finding.

## What it exposes

- **What stays invariant?** The purchase was authorized at act time, and the
  mandate is no longer in force now. Preserve and cascade agree on both facts.
- **Does a current reader continue to honor the completed act?** Preserve says
  yes; cascade says no. The canon picks no current-honoring policy.
- **What is the as-of-act-time view?** A historical baseline over an earlier
  event subset that excludes the later revoke — not the same-events comparison.
- **Does revocation affect future reliance?** Yes. The mandate is withdrawn going
  forward under both policies.
- **Can a later challenge reopen a past act without automatic global collapse?**
  Yes (step 5). A `CHALLENGE` + `ADJUDICATE` names *one* act by id. Revocation
  alone reopens nothing; reopening is a separate, scoped authority decision.
- **Is revocation an event-log fact, a projection result, or an authority decision?**
  All three, at different layers — and the probe keeps them apart:
  - the revoke is an **event fact** (one `AUTHORIZE consent.withdraw`);
  - whether a reader **honors the completed act now** is a **projection choice**;
  - whether that past act is **voided/punished** is an **authority decision** (`ADJUDICATE`).
- **Where is the boundary between buyer protection and anti-social-credit?**
  A preserve policy protects the good-faith counterparty. A permanent, automatic,
  identity-keyed refusal to honor all past acts would be a stored verdict about a
  *party* — the social-credit shape ARC refuses. So cascade is the reading to
  refuse as a *default* — but ARC picks no default: current honoring stays a
  projection choice
  ([authority-and-conflict.md](../../docs/authority-and-conflict.md) §9), and
  reopening a specific past act is always an explicit, per-act `ADJUDICATE`.

## Honest limits

This is a **probe, not doctrine.** It does not pick the "right" reading, does not
define a revocation spec, does not solve federation, and adds no universal
reputation semantics. The result is the same shape as findings B/C/D/G: the hard
case stays inside the five types, and what leaks out is a **current-honoring
fold-policy choice, not a missing primitive.**
