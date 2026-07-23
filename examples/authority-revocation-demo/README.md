# Authority Revocation probe

A small probe that isolates one question the delegation probe
(`examples/canon-fold-demo`, scenario 10 / finding G) raised but did not pull apart:

> After a withdrawal record is appended, does a current reader continue to honor
> an earlier recorded act that references the withdrawn mandate?

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE`. It does not define a wire format or revocation specification.

```
python3 probe.py
```

## The scenario

An authored delegation-chain fixture with a downstream-party record:

1. **T1** — the human (principal/buyer) grants agent A a scoped spending mandate
   (`AUTHORIZE consent.mandate`).
2. **T1** — agent A records a purchase authorization that the fixture's limited
   reference-and-withdrawal check returns as positive because it finds no earlier
   withdrawal of the referenced mandate
   (`AUTHORIZE consent.execute`); mock payment and fulfillment attestations follow.
3. **T2** — later, the human records a mandate withdrawal (`AUTHORIZE consent.withdraw`
   carrying `nullifies` — the existing field, event-registry §4.6).

The as-of-act-time fold applies the limited check to an earlier Event subset.
After the withdrawal record, the same full current log is projected under
preserve and cascade policies.

## The fixture readings and policy choice (printed by the probe)

The historical baseline is an **earlier Event subset** that excludes the later
withdrawal record. Under the fixture's limited reference-and-time comparison,
`authorized_at_act=True`; this is not a complete authority validation.

Against the **same full current log**, both policies return the same two fixture
readings and differ only on current honoring:

| policy | authorized_at_act | mandate_in_force_now | completed_act_honored_now |
|--------|-------------------|-----------------------|---------------------------|
| preserve | **True** | **False** | **True** |
| cascade | **True** | **False** | **False** — not honored by this projection |

The two limited readings are shared; the result for current honoring depends on
the selected fixture policy.

## What it exposes

- **What is shared in this fixture?** Its limited check returns
  `authorized_at_act=True` and finds a recorded withdrawal when computing
  `mandate_in_force_now=False`. Preserve and cascade agree on both outputs.
- **Does a current reader continue to honor the earlier recorded act?** Preserve says
  yes; cascade says no. The canon picks no current-honoring policy.
- **What is the as-of-act-time view?** A historical baseline over an earlier
  Event subset that excludes the later withdrawal record — not the same-events
  comparison.
- **What does the later challenge section record?** Its `CHALLENGE` and
  `ADJUDICATE` reference one act by id. The fixture does not project legal,
  payment, or operational consequences from those records.
- **Which layers does the fixture distinguish?**
  - the withdrawal is a **mock-signed Event** (`AUTHORIZE consent.withdraw`);
  - whether a reader **honors the completed act now** is a **projection choice**;
  - the later `ADJUDICATE` is a separate ruling record referencing that act.
- **Where does the fixture leave current honoring?** A preserve policy continues
  honoring the recorded act; a cascade policy does not. Base ARC selects no default:
  current honoring stays a projection choice
  ([authority-and-conflict.md](../../docs/authority-and-conflict.md) §9), and
  this fixture records a separate, per-act `ADJUDICATE` for its later ruling.

## Limits

This fixture does not define a revocation specification, select a default
current-honoring policy, validate full mandate scope or lineage, or determine
legal, payment, or operational consequences.
