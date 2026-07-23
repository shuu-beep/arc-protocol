# Execution / outcome fidelity probe

A small fixture examining the same record/world distinction as findings M and O:

> For a `commerce.fulfillment` record, a successful signature check under a
> declared security profile shows that the verifier accepted the configured
> public key, signature, and bytes under that profile. It does not establish who
> controlled the signing key or that delivery occurred.

Stdlib only, single process, mock signatures, no network, no storage. It reuses the
five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and the `refs` field, and adds **no sixth type, no stored delivery
oracle, no "outcome score".**

```
python3 probe.py
```

## A third fidelity check

Three fixtures examine related limits. Under a declared production signature
profile, successful verification can establish that the checked signature
matches the configured public key and bytes. It does not establish who
controlled the private key, interpretation, time, or world truth:

- **Finding M** (`../reference-client/signer_fidelity_fixture.py`) — the
  **interpretation** axis: a signature does not prove the signer read its mandate
  faithfully.
- **Finding O** (`../temporal-fidelity-demo/`) — the **time** axis: a signature does
  not prove the stamped `timestamp` is true.
- **This probe** — the **world** axis: a signature does not prove the runtime did,
  or the world matched, what the event claims.

The claim about the world lives in `payload`, so it is covered by the fixture id
and mock signature. The fixture mock-signs `"delivered"` whether or not its
stipulated world state matches. The deterministic hash preserves the record
bytes, not human authorship or the referent.

## Record and referent boundary

ARC executes no payment and performs no delivery
([architecture.md](../../docs/architecture.md) §4.2,
[liability-boundaries.md](../../docs/liability-boundaries.md)). The fixture examines
what its dispute records and named policies do — and do not — establish:

- Two contradictory claims about one referent (agent: `delivered`; principal:
  `not_received`) both pass the fixture replay check, and the comparison reports
  the contradiction — the event-registry's "partially exposed"
  ([event-registry.md](../../docs/event-registry.md) §2.4).
- But exposing a contradiction is not resolving it. Every instrument that looks like
  proof — a carrier receipt, a witness, a counter-claim — is **another evidence
  record** whose evidentiary weight depends on the named profile and observer
  policy. Additional receipts do not by themselves establish the referent.
- Under this fixture's authority policy, an `ADJUDICATE` selects a terminal ruling.
  The ruling remains a recorded claim and does not establish the external outcome.

## What the probe prints

| readout | what happens | fixture output |
|---------|--------------|---------------|
| 1. the boundary | agent mock-signs `commerce.fulfillment: delivered` | fixture check passes — referent unproven |
| 2. detectable contradiction | principal mock-signs `not_received` for the same referent | **CONTESTED** — the selected comparison reports the conflict |
| 3. additional claim | add a carrier receipt; principal counters | still **CONTESTED** under the same comparison |
| 4. adjudication | configured adjudicator rules `delivered` | **FINAL under this fixture policy** — fixture stipulation is `not_delivered` |
| 5. without the privileged policy | omit the configured adjudicator | **CONTESTED** under the unprivileged claim comparison |

External-attestor policy:

- **privileged external attestor** — give one signer's `ATTEST` decisive weight under a named policy (an escrow
  release wired to a carrier-API confirmation, an IoT delivery sensor, a provider
  settlement webhook). This produces a deterministic result under that policy, but
  the attestor's record remains a claim and may be inaccurate.

## What it exposes

- **A record signature cannot certify the world.** A production verifier can
  check a signature over bytes against a configured public key; it does not
  establish the payload's referent or who controlled the private key.
- **The fixture can compare recorded claims.** It reports contradictions and can
  route a disputed record to a `CHALLENGE`; it does not recover the external fact.
- **Additional records do not by themselves establish the referent.** Receipts,
  witnesses, and counter-claims require an evidence and authority policy.
- **Adjudication is interpreted by a named authority policy.** Without the policy
  that gives one signer the last word, this fixture returns **CONTESTED**.

## Limits

This is a probe. Signatures are **mock**: the point is the fold
over authored claims, not custody. IDs and refs use deterministic content hashes,
so the fixture preserves its staged contradiction. The stipulated state
(`not_delivered`) lives in a generator-only strip **no observer fold receives**.
Within this fixture, the deterministic hashes preserve the authored record bytes,
the comparison identifies contradictory payloads, and the named policy selects a
ruling. None of those checks establishes the external outcome. A production profile
must declare its signature and evidence policies.
