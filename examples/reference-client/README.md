# ARC reference client

An illustrative ARC viewer, not a runtime or production implementation. Its
seven base Commerce surfaces share one mock-signed fixture log; additional bands
use named independent fixture logs. The client selects these UI surfaces rather
than claiming a one-to-one Canon UI.

Each surface renders a projection over its named fixture log. In these fixtures,
a mandate identifies what an agent key may sign without another approval record.

## What you see

```
┌─ delegation tree    ─┬─ approval inbox       ─┬─ projection viewer        ─┐
│  authorization viewer│  signed commitments    │  challenge / adjudication  │
├──────────────────────┴────────────────────────┴────────────────────────────┤
│  live proposal — scripted write-path evaluation                               │
├──────────────────────────────────────────────────────────────────────────────┤
│  event log — the source the seven surfaces fold over (click to inspect)       │
├──────────────────────────────────────────────────────────────────────────────┤
│  delegation graph — fixture log · two readings                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  cold start — policy matrix (fixture log · three observers · two cuts)         │
├──────────────────────────────────────────────────────────────────────────────┤
│  compromise — fixture-classified exposure (illustrative Ed25519 · 2 × 2)        │
├──────────────────────────────────────────────────────────────────────────────┤
│  federation — what a bridge imports (5 observers · 3 moments × 2 readings)      │
├──────────────────────────────────────────────────────────────────────────────┤
│  approval return — reviewable-field binding (illustrative Ed25519 · 2 readings) │
└──────────────────────────────────────────────────────────────────────────────┘
```

The base panels share the Commerce log; the later bands use separate logs:

| surface | sourced from |
| --- | --- |
| delegation tree | `KEY id.key_register` ×4 + the `AUTHORIZE` mandate edge |
| authorization viewer | the base log's one-transaction `AUTHORIZE consent.approval` (not standing authority — the write path's `consent.mandate` is a separate, tagged event) |
| approval inbox | the same `AUTHORIZE`, shown resolved |
| signed commitments | `ATTEST commerce.offer / payment_result / fulfillment` |
| projection viewer | `project_merchant_standing` at three cuts of the log |
| challenge / adjudication | `CHALLENGE dispute.open` + `ADJUDICATE gov.warning` |
| event log | all 11 generated events (+ the write-path mandate and any auto-signed proposal, tagged) |
| delegation graph | a separate 21-event fixture log (`delegation_fixture.py`), folded two ways |
| cold-start policy matrix | a separate 30-event fixture log (`coldstart_fixture.py`), folded by 3 observers |
| compromise band | a separate 14-event fixture log (`compromise_fixture.py`, **illustrative Ed25519**), folded at 2 moments × 2 revoke readings |
| federation band | a separate 15-event fixture log (`federation_fixture.py`), folded by 5 observers at 3 moments × 2 severance readings |
| approval-return band | a separate 7-event fixture log (`approval_seam_fixture.py`, **illustrative Ed25519**), signer decisions + an approval judged under 2 readings (proposal-bound / scope-only) |

The projection viewer's snapshot toggle shows this fixture-policy reading:
standing is `in_good_standing → in_good_standing → warned`, changing on the
`ADJUDICATE` rather than the `CHALLENGE`, while `open_disputes` goes `0 → 1 → 0`.
The fixture recomputes those values from appended events rather than mutating a
stored projection.

## The write-path fixture

Below the panels, a band shows how this scripted runtime evaluates proposed events.
The fixture represents proposed records with one `Proposal` shape and routes them
through `evaluate()`, rather than exposing a writer per Event type. It checks each proposal
against the active mandate — an explicit `AUTHORIZE consent.mandate` the fixture root
grants for the write path; the base log's one-time `consent.approval` licenses
only its own transaction ([event-registry.md](../../docs/event-registry.md) §6)
and is never read as standing authority — and routes it:

| proposal | decision | why |
| --- | --- | --- |
| `ATTEST rep.outcome` (context lunch) | **AUTO-SIGNED** → event log | in scope — no additional approval record required |
| `ATTEST commerce.payment_result` 20000 KRW | **ESCALATED** → approval inbox | amount exceeds the mandate ceiling (8000) |
| `AUTHORIZE consent.approval` | **ESCALATED** → approval inbox | this fixture routes `AUTHORIZE` for root-side handling |

In this fixture, mandate scope determines whether a proposal is mock-signed or
routed as a PENDING item for a root-side decision. The scripted runtime passes
proposal fields to the fixture evaluator; this path does not model key custody.
The write-path mandate and mock-signed Event pass the fixture's deterministic
replay check with the log they extend.

## The delegation-graph fixture

The bottom band uses multi-level delegation. It folds a **separate
generated fixture log** (`delegation_fixture.py`, 21 events, also runnable on
its own) into a multi-level delegation graph:

```
human root
  └─ coordinator (≤50000)
       ├─ negotiator (≤30000; branch later REVOKED)
       │    └─ scout (OVER-delegated: granted 80000 by a holder of 30000)
       └─ fulfiller (≤50000)
            └─ courier (EPHEMERAL: single-use mandate, retired after one act)
stray key (passes the mock replay check; no grant chain to this root → weight 0)
```

The graph is not authoritative protocol state. The fixture computes it from the
log, and the generated HTML embeds that pre-rendered output. The fold is
parameterized by two choices the Canon does not make:

* **`local_root`** — rooted-ness is computed *from a chosen root key*. Fold the
  same log from `k:stray` and the rooted classifications change. This
  fixture uses no global identity registry. An unrooted key renders at weight 0; it is not
  blocked. The fixture does not test cross-principal identity linkage or Sybil
  resistance.
* **`reading`** — whether the current projection continues to honor acts that
  *completed* under the grant before it was withdrawn (the authority-revocation-
  demo divergence, applied to a whole lineage). Both policies fold the same full
  current log. The fixture assigns act-time authorization flags separately:

| act | fixture `authorized_at_act` | preserve · full current log | cascade · full current log |
| --- | --- | --- | --- |
| negotiator's in-scope 24000 offer | **True** | **HONORED** | **NOT HONORED** by this projection |
| courier's completed delivery | **True** | **HONORED** | **NOT HONORED** by this projection |
| negotiator's escalated 40000 payment | **True** | **HONORED** | **HONORED** — its basis is a direct root approval, not the withdrawn chain |
| every act *after* the withdrawal that depends on the withdrawn chain | **False** | **NOT HONORED** | **NOT HONORED** |

Other cases represented without a new event type: the scout's
over-wide grant is **admissible** (the log does not police it) but the fold
clamps its effective ceiling to the chain's intersection, flagging claimed ≠
effective; the scout's own grant is never withdrawn, yet its lineage is
**severed** when an ancestor's falls; each node's effective ceiling *is* the
escalation boundary — what it may sign without another approval record, beyond which only a
fresh root `AUTHORIZE` carries an act. Delegation, over-delegation, escalation,
retirement and revocation are all `KEY`/`ATTEST`/`AUTHORIZE` with existing
fields (`scope`, `refs`, `nullifies`).

Both readings are pre-rendered by the Python fold; the page's JavaScript only
toggles between them and inspects raw events. The boundary logic never moves
into the viewer.

## The cold-start policy matrix

The cold-start band compares three illustrative observer policies over an
authored fixture log. It does not define an exhaustive Canon taxonomy.

> the disclosed records do not establish hidden operator identity or real-world
> outcome quality; observer policies can therefore return different readings.

A third fixture log (`coldstart_fixture.py`, 30 events, runnable standalone)
generates four visibly different record patterns whose hidden operators remain
unknown to the folds:

* **nova** — unlinked: two outcome attestations, one counterparty, no vouch;
* **mint** — three outcome claims from keys that the generator privately
  stipulates share one operator; that relationship is not in the log;
* **linked-1 / linked-2** — mutual vouches, one outside tie, and no outcome
  history at the first cut;
* **pre-authorized** — granted a mandate by an established root before any
  recorded outcome history.

Three observers fold the same log — `(root, policy, honored adjudicator)` —
and each fixture policy has a different blind spot: the **path** observer
gives nova and mint weight 0; the **history** observer
ranks mint's authored volume *above* nova's thin record; the **social**
observer admits the linked pair through one casual vouch — flagged in the
cell as *"hinges on one tie"* because removing that Event changes this policy's
result — until the tie is retracted.

Between the two cuts, the policies return different results: the path policy no
longer includes the pre-authorized key after withdrawal, while the history policy retains its
prior outcome records;
two communities rule the *same dispute* about mint in **opposite directions**
(`gov.warning` vs `gov.dismissal`), and observers return different results based
on which ruling they honor. The linked-2 row retains a retracted tie and an open
dispute at the second cut.

The band computes no composite score and performs no protocol-level identity
verification. The generator's private stipulation ("mint and three authored
counterparties share an operator") is rendered as **generator-only stipulation**, and
the folds never receive it. This fixture groups
three illustrative strategies — earned outcome claims, authored volume, and a
borrowed tie. The visible records distinguish those paths, while not proving
hidden operator identity or real-world quality.

## The compromise band — a stolen hot key under one fixture policy

The compromise and approval-return bands use an **illustrative Ed25519** reference
implementation. A cold `root` grants a hot `agent` a narrow mandate (market,
≤30000); the fixture records one pre-compromise act, then stipulates secret-byte
exfiltration and generates five attacker-authored records whose signatures pass
the fixture verifier.

The honoring grid carries a green **SIG CHECK PASS** chip on every row — attacker
records included. Under this fixture policy, the over-ceiling and out-of-context
records fall to
scope; the self-elevation `AUTHORIZE` is not root-signed and is not honored by
this fold; the post-revoke act
falls to time. This selected fold honors one in-scope attacker record — **25000
KRW** — producing fixture-classified honored exposure, not executed loss:

> scope and pre-withdrawal time are two modeled controls. This fixture does not
> provide an exact general damage formula or execute a payment.

Two toggles drive it. The **revoke reading** (time-scoped / cascade) shows that
neither reading isolates the private attacker-authored class: time-scoped honors the in-scope attacker-authored record
*and* the pre-compromise history; cascade declines to honor both record classes. The
**moment** toggle (just after the revoke / after the adjudication) shows two
different records receiving the same fold verdict under both readings. They have
different payloads, IDs, and bytes; they separate in this projection only *after
the adjudication*, after the fixture adds a root `CHALLENGE` and an honored
`ADJUDICATE` voiding that single event, signed by the market
community's adjudicating key — the fold counts a per-act void only from an
adjudicator the reader honors, so the disputant's own on-log self-ruling moves
nothing; event-registry §4.5. The three displayed layers are **fixture signature
check passes (record) / scope honored (fold) / void
(authority).**

As in the cold-start band, the generator's private authorship classification is
rendered as a generator-only stipulation, and
the honoring grid never receives it. The displayed exposure number intersects
the selected fold with that private classification; it is not an exact general
loss measure or an observer-computable value. See
[`docs/key-custody.md`](../../docs/key-custody.md) §5/§8 for the broader topic.

## The federation band — what a bridge imports

The federation band uses one fixture log, two community authorities, and
observers configured to interpret imported adjudication differently. A fifth fixture log
(`federation_fixture.py`, 15 events, runnable standalone) stages the conflict:
a cross-community sale is disputed; **community-harbor** rules *suspension* (its
strict rule: late delivery is non-fulfillment); the vendor appeals at home and
**community-orchard** rules *dismissal* (its rule: delivered late is still
delivered). Before any of this, orchard had **recognized harbor's commerce
rulings** — the bridge, an ordinary `AUTHORIZE` (`fed.recognition`) with a
`scope`. After the conflict, orchard severs it (`fed.severance` + `nullifies`).

Five observers fold the same log, differing only in fold parameters: harbor's
own observer (who holds no bridge — **bridges are directional**); an orchard
observer who reads the bridge as *nothing* (imported rulings weigh 0, the
stray-key treatment); one who reads it as **advisory** (the imported ruling is a
visible flag that moves no standing); one who reads it as **authority** with a
precedence rule (on conflict, local supersedes — *override is a precedence
choice inside a fold, not an event*); and one who reads it as authority with
**no precedence rule**. When two honored
authorities conflict and nothing ranks them, this projection returns
**CONTESTED**. That is one fixture-policy result, not a base ARC prohibition on
final-authority topologies.

The severance toggle replays the revocation divergence on the federation side:
under **time-scoped**, severing the bridge changes no displayed cell because it
bounds future imports; under **cascade**, the current projection excludes rulings
previously imported through the severed bridge. The original `ADJUDICATE` Events
remain in the log.

The fixture encodes a categorical bridge reading (authority /
advisory / ignore), not a numeric bridge weight. Such a weight would be a
different application-policy design. The private strip stipulates a
late delivery and the two authored rulings; the log contains a payment-result and
delivery claim, not ground truth. The folds key on which authority each observer
honors. Why orchard recognized harbor in the first place
is not in the log and no fold reads it.

## The approval return path

The approval-return band uses **illustrative Ed25519**. Its fixture
(`approval_seam_fixture.py`, runnable standalone) separates the agent from the
signer, so the agent can submit proposals but does not hold either signing key.
The first panel shows the signer-side decisions for in-scope, over-ceiling,
out-of-domain, and self-mint proposals.

A routed proposal is reviewed by a simulated cold-root ceremony. The review body
contains proposal fields such as amount and payee; Event signing later adds
envelope fields including signer and timestamp. The ceremony emits a separate
approval record bound to the proposal-field hash.

The band compares two fixture readings. Under **proposal-bound**, the signer
refuses a different proposal hash, an approval already present in its in-process
consumed set, and a scope-only approval that names no proposal. It also checks the
approval's illustrative signature, cold-root signer, and membership in this
fixture log. Under the computed **scope-only** counterfactual, the same three
authored attempts would be signed because only context and amount are checked.

The fixture does not establish what a person saw or understood. It demonstrates
only the named proposal-binding, membership, signature, and in-process consumption
checks.

## Why a viewer (and not a runtime)

The reference client selects surfaces for these fixture records; Canon does not
prescribe these UI surfaces. Commerce, community, and career presentations are
application- or profile-level views over records expressed with the five Event
types.

## Fixture scope

* The Commerce log is programmatically generated from the hand-authored
  `examples/end-to-end-demo/flow.py` fixture and reused verbatim.
* **The write path uses deterministic mock signing; two bands use illustrative
  Ed25519.** The write
  path signs with the probe's mock scheme (a hash, not Ed25519), and only to show
  the mandate→sign/escalate *decision* — *where* keys live is not its subject.
  The compromise and approval-return bands use an **illustrative Ed25519**
  implementation. The write path demonstrates routing; those bands test the
  record checks explicitly named by their fixtures.
* The proposals are scripted and do not use an MCP wire or live agent runtime.
  The fixture covers proposal routing only.
* Projections are computed by the fixture fold, **not re-implemented** in the
  page. The HTML renders the precomputed output.
* The commerce log's delegation is **single-level** (one per-purchase
  AUTHORIZE), so the delegation-tree card is shallow. Multi-level delegation
  lives in the delegation-graph band, which folds over its **own generated
  fixture log** — a separate log from the Commerce fixture.
  The seven surfaces and the write path still fold over the commerce log alone.
* The graph shows the **local-attribution side** of agent multiplication only:
  within one observer's root, sub-agents have explicit grant paths; across
  principals nothing here forces attribution (the scenario-11
  incentive-incompatibility remains untested). The stray key illustrates that case.
* The cold-start policy matrix shows three illustrative readings of the visible
  records. It does not infer hidden operator identity or real-world outcome quality.
* A design treatment of **key custody** exists
  ([`docs/key-custody.md`](../../docs/key-custody.md)), and the compromise band
  runs one fixture case (§5) on illustrative keys — fixture-classified
  honored exposure after a stipulated compromise. Compromised-signer behavior,
  threshold custody, and enclave attestation remain outside this fixture.
* The federation band is a **first slice, deliberately small**: one bridge, one
  direction, one disputed act. Schism, observer migration, meta-folding (reading
  someone *else's* bridges to discount them), and multi-bridge conflict are
  explicitly out of scope for this cycle. The band tests one bridge encoding,
  not what makes one worth issuing — the adoption/incentive question stays open.
* The approval-return band uses **illustrative Ed25519** and checks signature, key
  registration, and signer-side proposal binding as separate fixture operations.
  The "processes" are Python objects sharing serializable data, with no network,
  persistence, or process isolation. The scope-only reading is a *computed
  counterfactual*, not a second live signer. What it does not settle is what
  makes a person's review reliable or how the return path remains available.

## Run

```
python3 build.py                # reuses the end-to-end-demo probe + all five fixtures, writes client.html
open client.html                # any browser; fully self-contained, no server
python3 delegation_fixture.py   # fixture standalone: narrated flow + both fold readings
python3 coldstart_fixture.py    # fixture standalone: narrated flow + the matrix at both cuts
python3 compromise_fixture.py   # fixture standalone: illustrative Ed25519, selected-fold exposure
python3 federation_fixture.py   # fixture standalone: the bridge, the contested cell, both severance readings
python3 approval_seam_fixture.py # fixture standalone: signer decisions + scope-only counterfactual
```
