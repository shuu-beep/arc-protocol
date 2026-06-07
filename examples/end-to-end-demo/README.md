# ARC end-to-end flow demo

A small, deliberately dirty probe that runs **one full interaction** and lets
the event log fall out of it.

```
python3 flow.py
```

## What this is

`examples/canon-fold-demo` folds a *hand-built* log to test whether the five
canonical event types are sufficient. This demo asks the complementary
question: **does a real interaction actually produce such a log?**

Four participants each hold a key and emit their own signed events:

```
human  <->  consumer-agent  <->  merchant-agent
  |                                    |
approval                          fulfillment
  |                                    |
payment attest  ->  dispute  ->  adjudication
```

The flow runs top to bottom, no branches:

1. **Identity** — each participant anchors a key (`KEY id.key_register`).
2. **Offer** — the merchant agent publishes `ATTEST commerce.offer`.
3. **Approval** — the consumer agent *cannot* approve; it asks the human, who
   signs `AUTHORIZE consent.approval`. Approval is the hard gate, not auto-execution.
4. **Payment** — recorded only as a claim about an external transfer
   (`ATTEST commerce.payment_result`). ARC never moves money.
5. **Fulfillment** — the merchant agent attests delivery (`ATTEST commerce.fulfillment`).
6. **Dispute** — the unhappy consumer opens `CHALLENGE dispute.open` and logs a
   negative `ATTEST rep.outcome`.
7. **Adjudication** — the community rules with `ADJUDICATE gov.warning`.

## What it shows

The **same** merchant-standing projection is recomputed three times:

| Snapshot | governance | open disputes |
| --- | --- | --- |
| after fulfillment | `in_good_standing` | 0 |
| after dispute | `in_good_standing` | 1 |
| after adjudication | `warned` | 0 |

Two things to notice:

- A dispute alone does **not** change commons standing. Governance moves only
  when an `ADJUDICATE` is added — never by mutating stored state
  ([authority-and-conflict.md](../../docs/authority-and-conflict.md)). The
  projection changes because the log grew, not because anything was overwritten.
- Every event in the final 11-event log was emitted by a participant during the
  flow. None was hand-written, and nothing derived is stored — the standing is
  recomputed on demand each time.

## Honest limits

This is a probe, not an implementation:

- stdlib only, single process, no network, no transport layer;
- signatures are **mock** (a hash, not Ed25519);
- payment is **mock** (an `ATTEST` claim, no funds move);
- no new event type — the five canonical types are reused as-is.

It demonstrates that the canonical events *compose into a real flow*. It does
not demonstrate that ARC is built.
