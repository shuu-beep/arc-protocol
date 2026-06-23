# Execution / outcome fidelity probe

A small, deliberately dirty probe on the third side of the same wall findings M and
O meet:

> A valid signature on a `commerce.fulfillment` event proves a key **asserted** a
> delivery. It does not prove a **delivery**.

Stdlib only, single process, mock signatures, no network, no storage. It reuses the
five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and the `refs` field, and adds **no sixth type, no stored delivery
oracle, no "outcome score".**

```
python3 probe.py
```

## The third leg of the fidelity trilogy

One wall, seen from three sides — each says *a valid signature proves a key signed,
nothing more*:

- **Finding M** (`../reference-client/signer_fidelity_fixture.py`) — the
  **interpretation** axis: a signature does not prove the signer read its mandate
  faithfully.
- **Finding O** (`../temporal-fidelity-demo/`) — the **time** axis: a signature does
  not prove the stamped `timestamp` is true.
- **This probe** — the **world** axis: a signature does not prove the runtime did,
  or the world matched, what the event claims.

The claim about the world lives in `payload`, so it is baked into the event id and
the signature. The key signs `"delivered"` exactly as faithfully whether or not a
parcel ever moved. The signature certifies authorship, never the referent.

## This axis is ARC's openly-declared boundary — so the probe earns its place after it

ARC executes no payment and performs no delivery
([architecture.md](../../docs/architecture.md) §4.2,
[liability-boundaries.md](../../docs/liability-boundaries.md)). So readout 1 is not a
surprise: it is the boundary, stated honestly. The finding is what the dispute
machinery does — and does **not** — recover *after* the boundary:

- ARC is **not silent** about the world. Two contradictory claims about one referent
  (agent: `delivered`; principal: `not_received`) both verify, and the log **exposes
  the contradiction** — the event-registry's "partially exposed"
  ([event-registry.md](../../docs/event-registry.md) §2.4).
- But exposing a contradiction is not resolving it. Every instrument that looks like
  proof — a carrier receipt, a witness, a counter-claim — is **another signed
  record**, only as good as its signer. Stack N receipts and the fact-question is as
  open as at N = 0. **The proofs regress; the referent stays out of reach.**
- `ADJUDICATE` **terminates** the regress; it does not **verify** the world. The
  ruling is an `ATTEST`-shaped claim by a more-authoritative key — it can be **final
  and wrong**. **Finality is a property of authority; fidelity is a property of the
  world. finality ≠ fidelity** (finding F, on the execution axis).

## What the probe prints

| readout | what happens | ARC's verdict |
|---------|--------------|---------------|
| 1. the boundary | agent signs `commerce.fulfillment: delivered` | **verifies** — record sealed, referent unproven |
| 2. detectable contradiction | principal signs `not_received` for the same referent | **CONTESTED** — log exposes the conflict, cannot resolve it |
| 3. the regress | add a carrier receipt; principal counters | still **CONTESTED** — one more record, not the fact |
| 4. adjudication | commons rules `delivered` | **FINAL** — and the omniscient truth is `not_delivered` |
| 5. the residue | drop the privileged adjudicator | **CONTESTED** — finding J, on the world axis |

Plus the mitigation, and its price:

- **trusted oracle** — elevate one signer's `ATTEST` to ground truth (an escrow
  release wired to a carrier-API confirmation, an IoT delivery sensor, a provider
  settlement webhook). The dispute resolves deterministically — but "the oracle" is
  a key ARC does not govern, and it can lie or err exactly as any signer. The
  mitigation does not make the claim true; it **relocates** the unobservable
  referent-fidelity into a privileged key (finding M's attested-signer move, finding
  O's head-oracle move — the same move, on the world axis).

## What it exposes

- **A genuine signature cannot certify the world.** The key signs a false delivery
  as faithfully as a true one — the same shape as M and O, on the world axis.
- **ARC is not blind to the world.** It binds a claim to a signer, makes it
  tamper-evident, exposes contradictions among claims, and routes them to a
  `CHALLENGE`. The finding is the **gap** between exposing a contradiction and
  recovering the fact.
- **No quantity of records crosses that gap.** Receipts, witnesses, counter-claims —
  each is another record about the referent, never the referent. The proofs regress.
- **Adjudication buys finality, not fidelity.** Subtract the authority that elevates
  one signer to the last word and the honest terminal output of "did it happen?" is
  **CONTESTED** — finding J's irreducible disagreement, now on the **world axis**.

## Honest limits

This is a **probe, not doctrine.** Signatures are **mock**: the point is the fold
over the claims, not custody — but id and refs hashing are **real content hashes**,
so the contradiction the log exposes is genuine, not staged. The world's real state
(`not_delivered`) lives in an omniscient strip **no observer and no fold can read** —
exactly the gap the probe is about. ARC can **preserve** a claim about the world —
bind it to a signer, make it tamper-evident, expose contradictions, route them to the
commons, and seal a final ruling — but it cannot make the claim **true**. Execution
and outcome enter ARC the way the external world always does: as an `ATTEST` claim,
true only as far as a receipt, witness, or policy-specific adjudication carries it.
The signature seals the record, never its referent.
