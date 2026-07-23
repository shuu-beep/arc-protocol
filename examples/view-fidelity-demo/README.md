# View fidelity probe

A small fixture comparing signed record bytes with renderer outputs:

> A signature covers the signed bytes, not an off-log rendering of those bytes.

Stdlib only, single process, mock signatures, no network, no storage. It reuses the
canonical event types and the `view_hash` / `refs` content hashes, and adds **no new
event type, no "view object", no view score** — a rendered-view attestation is an
ordinary `ATTEST` predicate.

```
python3 probe.py
```

## Fixture scenario

The signed canonical bytes **B** are not changed. The fixture supplies renderer
outputs that either reproduce selected payload fields, rewrite a payee label, or omit
the payee. The replay check covers B; the renderer output remains off-log unless an
additional `view.rendered` claim is recorded.

## Relation to findings M and L

- **Finding M** (`../reference-client/signer_fidelity_fixture.py`) varies a signer's
  interpretation of a recorded mandate. This fixture instead varies an authored
  renderer output for the same payload.
- **Finding L** (`../reference-client/approval_seam_fixture.py`) — the escalation return
  path binds an approval to reviewable proposal fields. This fixture tests a separate
  presentation assumption: a deterministic renderer can still omit a field.

## The one thing the log can check, and the one it cannot

This fixture profile places a `view_hash` in the signed payload. Given the same action
bytes and declared renderer, its comparison can reproduce that renderer's output hash.
Equality does not establish which output was displayed or perceived.

## What the probe prints

| readout | what happens | verdict |
|---------|--------------|---------|
| 1. boundary | the log holds B and `id=hash(B)`; no view | resolve-view-from-log **UNKNOWN** |
| 2. matching render | the fixture renderer includes its comparison fields | generator-only comparison reports a match |
| 3. view/bytes mismatch | same mock-signed action, an authored renderer rewrites the payee | fixture checks pass; the payload still names `wallet:attacker` |
| 4. view_hash (half) | the committed hash differs from the declared renderer's output | **MISMATCH** — claimed ≠ recomputed |
| 5. omitted field | pinned renderer reproducibly omits the payee | **MATCH**, replay check passes, fixture comparison reports omission |
| 6. additional claim | a `rendered_view` ATTEST is added | **CLAIMED** — one more record |

A `rendered_view` ATTEST is another claim under the selected profile. It can name a
renderer output hash, but this fixture cannot establish actual display or perception.

## What it exposes

- **A production-profile verifier can check a signature over covered bytes against
  the configured public key; it cannot certify a view.**
  `render(B)` runs off-log and never enters the signature.
- **The fixture's `view_hash` comparison can report a mismatch** between a committed
  hash and the output of its declared renderer.
- **A matching hash is limited evidence.** A renderer that reproducibly omits the
  fixture's payee field still hashes consistently. Equality establishes only a match
  to the declared renderer function and inputs.
- **Actual display and perception are outside this fixture.** Neither is recovered
  from the Event set.

## Limits

This is a probe. Signatures are **mock**: the point is the gap between
bytes and view, not custody — but `id` and `view_hash` are SHA-256 content hashes, so
the fixture performs an equality comparison. The generator separately records which
authored output it associated with each action; observer folds do not receive that
mapping. `view_hash` is a field used by this fixture profile, not a base-protocol
requirement or proof of actual display.
