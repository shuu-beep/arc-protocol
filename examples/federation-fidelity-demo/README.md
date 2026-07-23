# Federation bridge-reading probe

A small fixture combining two earlier findings:

> When an act produced under a stipulated drifted reading crosses a federation
> bridge, does the receiving policy re-evaluate the recorded scope locally?

Stdlib only, single process, mock signatures, no network, no storage. It reuses
the five canonical event types — `KEY`, `ATTEST`, `AUTHORIZE`, `CHALLENGE`,
`ADJUDICATE` — and the `scope` / `refs` / `nullifies` fields, and adds **no sixth
type, no stored authority object, and no stored "fidelity score".**

```
python3 probe.py
```

## The two findings it composes

- **Finding J** (`../reference-client/federation_fixture.py`): a community
  recognizes another's authority with a scoped `AUTHORIZE fed.recognition`. The
  bridge routes authority under this fixture; a recognizing fold reads the
  bridge **categorically — binding / advisory / ignored** — and the configured
  policy may return CONTESTED.
- **Finding M** (`../reference-client/signer_fidelity_fixture.py`): verification
  under a declared signature profile can check record bytes against a configured
  public key, but it does not establish who controlled that key or how the signer
  label's associated party interpreted its mandate.

## The scenario

Two communities. **harbor** grants its agent a market mandate with an on-log
ceiling of `30000`. harbor's signer is **drifted** — it mock-signs acts harbor's own
recorded mandate would not authorize. **orchard** recognizes harbor's market
authority over a bridge, then folds harbor's acts.

1. `harbor-principal` grants the agent `AUTHORIZE consent.mandate`,
   `scope = {category:market, max_total_krw:30000}` — the ceiling is **on the log.**
2. `orchard` recognizes harbor: `AUTHORIZE fed.recognition`,
   `scope = {domain:market, community:harbor}` — the bridge (finding J).
3. `harbor-agent` mock-signs three acts under a **stipulated drifted** reading.
   Every one passes this fixture's mock-signature check:
   - `act_in` — 20000 groceries (in-scope under any reading);
   - `act_num` — 40000 bulk order (**numeric** drift: over the recorded ceiling);
   - `act_cat` — 15000 of an ambiguous item harbor calls "market" (**categorical** drift).

"How does orchard honor this act?" is asked only as a **projection** — a fold
parameterized by the bridge-reading. Nothing is stored.

## What the probe prints

The fold matrix — orchard reads each act under three bridge-readings:

| act | binding | advisory | ignored |
|-----|---------|----------|---------|
| `act_in` (20000 groceries) | HONORED | HONORED | NOT_RECOGNIZED |
| `act_num` (40000, numeric drift) | **HONORED** | DECLINED | NOT_RECOGNIZED |
| `act_cat` (15000, categorical drift) | **HONORED** | CONTESTED | NOT_RECOGNIZED |

- `act_in` is HONORED under binding **and** advisory — both configured readings
  accept it.
- `act_num` — binding skips the recorded-ceiling check; advisory's local re-fold
  reports that the ceiling was exceeded.
- `act_cat` — binding skips orchard's classifier; advisory does **not** establish
  a violation. It returns **CONTESTED** because the configured classifiers
  disagree. The result does not establish harbor's private interpretation.

Then orchard, operating **binding**, honors `act_num` and records a mock
payment-result claim on its basis; it severs the bridge (`fed.severance` +
`nullifies`), and a **new** harbor act is dropped while the earlier act and
payment-result record remain in the Event set.

## What it exposes

- **This fixture's bridge-reading selects interpretation behavior.** **Binding**
  returns HONORED after a matching live recognition without local mandate checks;
  **advisory** applies the local reading; **ignored** returns `NOT_RECOGNIZED`.
- **Local re-evaluation checks only recorded fields.** Advisory reports the numeric
  ceiling violation but returns **CONTESTED** for the ambiguous category. It does
  not establish how harbor interpreted the category.
- **Binding does not consume a remote verdict in this fixture.** This configured
  branch treats a matching live recognition as sufficient and does not evaluate
  the recorded mandate scope.
- **Under this preserve-style policy, severance does not remove earlier records.**
  A new harbor act is NOT_RECOGNIZED, while the earlier act and mock payment-result
  record remain available to the fold.

## Limits

This is a probe. Signatures are **mock**: finding M used illustrative
Ed25519 for its in-scope acts; here the point is
reading-semantics across the bridge, not custody, so the control asserts
*event-identity* (the recognized event is the same object whatever harbor's signer
privately read). The probe does not define a federation spec or pick a preferred bridge-reading,
and adds no stored authority object. The result is bounded to this bridge encoding
and these three configured readings; base ARC selects no federation policy.
