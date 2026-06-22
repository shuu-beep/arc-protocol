# Temporal fidelity probe

A small, deliberately dirty probe one layer below finding M:

> A valid signature proves the key **signed**. It does not prove that the stamped
> `timestamp` is **true**.

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and the `refs` / `nullifies` fields, and adds **no sixth type, no
stored clock, no trusted-timestamp object, and no "temporal score".**

```
python3 probe.py
```

## The twin of finding M, on the evidence layer

- **Finding M** (`../reference-client/signer_fidelity_fixture.py`): a valid
  signature proves a key signed; it does **not** prove the signer read its mandate
  faithfully. The lie is in the *interpretation*.
- **Finding O** (this probe): a valid signature proves a key signed; it does
  **not** prove the stamped time is true. The lie is in the *evidence*.

The timestamp lives inside `signing_bytes`, so it is baked into the event id and
the signature. That cuts two ways:

- changing a timestamp **after** signing breaks the id and the signature — ARC
  catches this (it is post-signature mutation, not a temporal lie);
- stamping a **false** timestamp **before** signing is honestly signed. The
  signature is genuine over a false value — an asserted falsehood, not a forgery.

`as_of`, revocation, challenge windows, adjudication, and standing all stand on
`event.timestamp`. A temporal lie sits one layer *beneath* authority and fidelity.

## The one defence ARC has for free: the refs DAG

ARC never stamps a trusted clock, but you cannot `ref` an id that does not exist
yet — an id is a hash of the event's own bytes. So `B refs A` is tamper-evident
evidence that **B was minted after A**: a partial *causal* order, independent of
any timestamp. A false timestamp is caught **only** when it contradicts that order.

## What the probe prints

| readout | what happens | ARC's verdict |
|---------|--------------|---------------|
| 1. post-signature mutation | rewrite a stamped time, keep the old id/sig | **REJECTED** — content hash breaks |
| 2. careless backdate | claim a time *before* the mandate the act refs | **CAUGHT** — refs DAG lower bound bites |
| 3. careful backdate | claim a false time, ref only the genuine past | **passes everything** |
| 4. revocation race | careful backdate stamped *before* a revocation it never refs | as-of-act-time **HONORS a dead mandate** |
| 5. concurrent → CONTESTED | order the act and the revocation by the DAG alone | **CONTESTED** — the DAG does not order them |

Plus the mitigation, and its price:

- **head-anchor oracle** — require each event to ref a recent head. That forces
  the careful backdate to descend from the revocation, collapsing the concurrency
  and catching the lie — but "recent head" is a clock/sequencer the signer must
  consult honestly. A signer that lies about the head it saw re-opens the gap. The
  mitigation does not make the timestamp true; it **imports a trust root ARC does
  not govern** (finding M's attested-signer move).

## What it exposes

- **A genuine signature cannot certify time.** The key signs a false stamp as
  faithfully as a true one — the same shape as finding M, on the evidence layer.
- **ARC is not blind to time.** The refs DAG gives a partial causal order for
  free, catching the careless backdate and dating revocations relative to what
  they ref. The finding is the **gap** between that causal order and the wall clock.
- **The lie is unobservable exactly in the causal gaps.** For concurrent events —
  neither refs the other — only the timestamp claims an order. Drop trust in it and
  the honest terminal output is **CONTESTED** — finding J's irreducible
  disagreement, now on the **time axis**. The revocation race is that residue with
  money on it: only an unverifiable stamp put the act "before" the revocation.

## Honest limits

This is a **probe, not doctrine.** Signatures are **mock**: the point is the fold
over the timestamp, not custody — but id and refs hashing are **real content
hashes**, so the causal DAG genuinely bites (a careless backdate cannot ref the
future for free). ARC can **preserve** a temporal claim — bind it into the
signature, bound it partially with the DAG — but it cannot make the claim **true**.
Real-world time enters ARC the way the external world always does: as an `ATTEST`
claim, true only as far as a witness, receipt, trusted clock, or policy-specific
adjudication carries it. The signature seals the record, never its referent.
