# Temporal fidelity probe

A small illustrative fixture for timestamp claims:

> This fixture's mock-signature check detects authored byte changes. It does not
> establish key possession or the accuracy of a stamped `timestamp`.

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five current Event types and the `refs` / `nullifies` fields. It stores no
clock object or temporal score.

```
python3 probe.py
```

## The twin of finding M, on the evidence layer

- **Signer-fidelity fixture:** a configured signature check does not establish
  the signer's mandate interpretation.
- **This fixture:** the deterministic mock-signature check does not establish
  the accuracy of the stamped time.

The timestamp lives inside `signing_bytes`, so it is baked into the event id and
the signature. That cuts two ways:

- changing a timestamp **after** mock-signing fails this fixture's id and
  deterministic hash checks (post-signature mutation, not a temporal claim test);
- stamping a **false** timestamp before this fixture's mock-signing still passes
  its deterministic hash check; that check does not establish clock truth.

`as_of`, revocation, challenge windows, adjudication, and standing all stand on
`event.timestamp`. Policies using that field inherit its accuracy limits.

## The dependency signal carried by `refs`

ARC does not stamp a trusted clock. `B refs A` places A's exact identifier in B
and records a declared dependency or prior-knowledge claim. Because A's identifier
can be computed before A is appended or published, the reference alone does not
prove append, publication, or wall-clock issuance order. The fixture flags a
timestamp only when it conflicts with this declared reference.

## What the probe prints

| readout | what happens | fixture result |
|---------|--------------|---------------|
| 1. post-signature mutation | rewrite a stamped time, keep the old id/sig | **REJECTED** — content hash breaks |
| 2. dependency-inconsistent stamp | claim a time *before* the claimed time of a referenced mandate | fixture reports the claimed-time conflict |
| 3. careful backdate | claim a false time, ref only compatible prior identifiers | passes this fixture's listed checks |
| 4. revocation race | fixture stipulates creation after withdrawal but stamps the act before it | claimed-timestamp policy honors the act under that stipulation |
| 5. concurrent → CONTESTED | order the act and the revocation by the supplied reference graph alone | **CONTESTED** — neither Event references the other |

Plus the mitigation, and its price:

- **configured recent-head source** — require each event to ref a recent head. If
  used as configured in this scenario, the act would reference the revocation and
  the policy would report the authored claimed-time conflict. The fixture does not
  validate the recent-head source or establish that a signer used it.

## What it exposes

- **A signature cannot certify timestamp truth.** A production verifier can check
  a signature over the timestamp bytes against a configured public key; it does
  not establish who controlled the private key or whether the timestamp is accurate.
- **Refs record declared dependencies.** They place named identifiers in the Event
  but do not, without sequencing or availability evidence, prove wall-clock order.
- **The supplied reference graph does not order concurrent events.** When neither
  Event references the other, only the timestamps claim an order. Without accepting
  that timestamp order, this fixture's reference-only policy returns **CONTESTED**.
  Only the claimed timestamp places the authored act before the withdrawal.

## Limits

This fixture uses **mock** signatures and focuses on the timestamp fold rather
than custody. IDs and refs use deterministic content hashes,
so the dependency check can flag a timestamp inconsistent with a named reference.
An Event can record a temporal claim under a declared security profile, but a
reference alone does not make the timestamp accurate or prove issuance order.
External time evidence remains a claim whose treatment depends on the named profile.
