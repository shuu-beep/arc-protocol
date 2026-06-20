# Federation fidelity-laundering probe

A small, deliberately dirty probe at the composition of two earlier findings:

> When a **drifted signer's act** (finding M) crosses a **federation bridge**
> (finding J), does the bridge **launder the drift?**

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
  bridge *routes* authority, it does not *mint* it; a recognizing fold reads the
  bridge **categorically — binding / advisory / ignored** — and CONTESTED is an
  honest terminal output.
- **Finding M** (`../reference-client/signer_fidelity_fixture.py`): a valid
  signature proves a key signed; it does **not** prove the signer read its mandate
  faithfully. The drifted reading is invisible on in-scope acts and surfaces only
  as honoring-disagreement.

## The scenario

Two communities. **harbor** grants its agent a market mandate with an on-log
ceiling of `30000`. harbor's signer is **drifted** — it signs acts harbor's own
recorded mandate would not authorize. **orchard** recognizes harbor's market
authority over a bridge, then folds harbor's acts.

1. `harbor-principal` grants the agent `AUTHORIZE consent.mandate`,
   `scope = {category:market, max_total_krw:30000}` — the ceiling is **on the log.**
2. `orchard` recognizes harbor: `AUTHORIZE fed.recognition`,
   `scope = {domain:market, community:harbor}` — the bridge (finding J).
3. `harbor-agent` signs three acts under harbor's **own (drifted)** reading. Every
   one of them *verifies* — the signature is honest; the reading is not:
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

- `act_in` is HONORED under binding **and** advisory — in-scope, the laundering is
  invisible here (the finding-M event-identity control).
- `act_num` — binding **laundered** a spend over the recorded ceiling; advisory's
  local re-fold caught it.
- `act_cat` — binding laundered it too; advisory did **not** catch a violation, it
  only **disagreed** (CONTESTED). harbor's fidelity stays unobserved.

Then orchard, operating **binding**, honors `act_num` and records a payment on its
basis; severs the bridge (`fed.severance` + `nullifies`); and a **new** harbor act
is dropped while the already-honored `act_num` — and the payment — persist.

## What it exposes

- **Federation's bridge-reading IS a fidelity choice.** Finding J's categorical
  binding / advisory / ignored maps onto finding M's faithful-vs-drifted axis:
  **binding** imports the remote reading and *launders* the drift; **advisory**
  substitutes the local reading and *exposes* numeric drift; **ignored** transmits
  nothing.
- **Re-folding does not recover fidelity — only catches recorded violations.**
  Advisory catches numeric drift (the crossed bound was on the log) but on an
  ambiguous category it only **disagrees**. Two faithful folds may read a category
  differently; neither certifies the other. Finding M's unobservable layer is not
  closed by the bridge — it is *relocated to the recognizer*.
- **Binding recognition is not free deference.** It makes orchard's clean log
  (finding K) contingent on a signer it can observe even less than its own —
  harbor's. It imports an unobservable trust assumption one community further away.
- **Severance does not un-launder the past.** It bounds the future (a new harbor
  act is NOT_RECOGNIZED), but the act honored under binding, and the money paid on
  it, outlive the bridge — finding J's "resolution by amnesia".

## Honest limits

This is a **probe, not doctrine.** Signatures are **mock**: finding M used real
Ed25519 to make its in-scope acts byte-identical; here the point is
reading-semantics across the bridge, not custody, so the control asserts
*event-identity* (the recognized event is the same object whatever harbor's signer
privately read). Lifting this to a real-signer fixture is a later upgrade. The
probe does not define a federation spec, does not pick the "right" bridge-reading,
and adds no stored authority object. The laundering is a **fold-policy residue at
the composition of findings J and M** — binding recognition routes not just
authority, but unobservable interpretation.
