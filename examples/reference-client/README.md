# ARC reference client

The first *visible* face of ARC. Not a runtime, not an implementation: a viewer
that renders the seven core client surfaces over a single signed event log, plus
one **write path** — a single proposal verb routed by the mandate boundary — to
make two claims legible to a human eye —

> **every surface is a projection over one closed event log**, and
> **a mandate is what an agent may sign without re-asking.**

## What you see

```
┌─ delegation tree    ─┬─ approval inbox       ─┬─ projection viewer        ─┐
│  mandate viewer      │  signed commitments    │  challenge / adjudication  │
├──────────────────────┴────────────────────────┴────────────────────────────┤
│  live proposal — the write path (runtime proposes · the boundary decides)    │
├──────────────────────────────────────────────────────────────────────────────┤
│  event log — the source the seven surfaces fold over (click to inspect)       │
├──────────────────────────────────────────────────────────────────────────────┤
│  delegation graph — authority as a visible object (fixture log · two readings)│
└──────────────────────────────────────────────────────────────────────────────┘
```

Every panel is sourced from the same log:

| surface | sourced from |
| --- | --- |
| delegation tree | `KEY id.key_register` ×4 + the `AUTHORIZE` mandate edge |
| mandate viewer | the `AUTHORIZE consent.approval` scope |
| approval inbox | the same `AUTHORIZE`, shown resolved |
| signed commitments | `ATTEST commerce.offer / payment_result / fulfillment` |
| projection viewer | `project_merchant_standing` at three cuts of the log |
| challenge / adjudication | `CHALLENGE dispute.open` + `ADJUDICATE gov.warning` |
| event log | all 11 generated events (+ any auto-signed proposal, tagged) |
| delegation graph | a separate 21-event fixture log (`delegation_fixture.py`), folded two ways |

The projection viewer's snapshot toggle shows the central fact directly:
governance is `in_good_standing → in_good_standing → warned`, moving **only on
the ADJUDICATE**, never on the dispute — and `open_disputes` goes `0 → 1 → 0`.
A dispute is not a verdict; governance moves by *adding events*, never by
mutating stored state.

## The write path — one verb, the boundary decides

Below the panels, a band shows what happens when a BYO runtime *proposes* events.
There is exactly one verb — `propose_event(type, payload)` — closed the same way
the Canon is (no writer per event type). The ARC client checks each proposal
against the active mandate and routes it:

| proposal | decision | why |
| --- | --- | --- |
| `ATTEST rep.outcome` (context lunch) | **AUTO-SIGNED** → event log | in scope — signed without re-asking the human |
| `ATTEST commerce.payment_result` 20000 KRW | **ESCALATED** → approval inbox | amount exceeds the mandate ceiling (8000) |
| `AUTHORIZE consent.approval` | **ESCALATED** → approval inbox | an agent cannot sign its own mandate (no self-elevation) |

This is the operational meaning of a mandate: in-scope proposals are signed
autonomously; out-of-scope ones become PENDING items a human/root must decide.
The key never crosses the proposal boundary — the runtime proposes, the client
signs. The auto-signed event verifies against the same log it extends.

## The delegation graph — authority as a visible object

The bottom band goes past single-level delegation. It folds a **separate
generated fixture log** (`delegation_fixture.py`, 21 events, also runnable on
its own) into a multi-level delegation graph:

```
human root
  └─ coordinator (≤50000)
       ├─ negotiator (≤30000; branch later REVOKED)
       │    └─ scout (OVER-delegated: granted 80000 by a holder of 30000)
       └─ fulfiller (≤50000)
            └─ courier (EPHEMERAL: single-use mandate, retired after one act)
stray key (verifies fine; no grant chain to this root → weight 0)
```

The graph is never stored — it is a fold over the log, parameterized by the two
choices the canon deliberately does not make:

* **`local_root`** — rooted-ness is computed *from a chosen root key*. Fold the
  same log from `k:stray` and the picture inverts: attribution is local, with no
  global identity registry. An unrooted key renders at weight 0; it is not
  blocked. Sybil stays deliberately unsolved — the band makes the asymmetry
  visible instead of pretending to close it.
* **`reading`** — what a withdrawal does to acts that *completed* under the
  grant before it was withdrawn (the authority-revocation-demo divergence,
  applied to a whole lineage). The toggle switches between:

| | as-of-act-time · preserve | current-log · cascade |
| --- | --- | --- |
| negotiator's in-scope 24000 offer | **VALID** | **VOID** — whole history collapses |
| courier's completed delivery | **VALID** | **VOID** — retiring a spent single-use agent poisons its own finished work |
| negotiator's escalated 40000 payment | **VALID** | **VALID** — its basis is a direct root approval, not the revoked chain |
| every act *after* the withdrawal | VOID | VOID — the readings agree about the future, they disagree only about the past |

Other tensions the fold makes visible without a new event type: the scout's
over-wide grant is **admissible** (the log does not police it) but the fold
clamps its effective ceiling to the chain's intersection, flagging claimed ≠
effective; the scout's own grant is never withdrawn, yet its lineage is
**severed** when an ancestor's falls; each node's effective ceiling *is* the
escalation boundary — what it may sign without re-asking, beyond which only a
fresh root `AUTHORIZE` carries an act. Delegation, over-delegation, escalation,
retirement and revocation are all `KEY`/`ATTEST`/`AUTHORIZE` with existing
fields (`scope`, `refs`, `nullifies`).

Both readings are pre-rendered by the Python fold; the page's JavaScript only
toggles between them and inspects raw events. The boundary logic never moves
into the viewer.

## Why a viewer (and not a runtime)

ARC's value is the coordination/trust boundary, not agent execution. The
reference client's job is to make the trust loop *legible* — exactly the
surfaces that correspond 1:1 to the closed Canon event set. Domain skins
(commerce / community / career) are not core surfaces; they are skill packs
that render *into* these generic surfaces, the same way every domain need is
expressed through the five canonical event types rather than a sixth type.

## Honest scope (deliberate)

* The log is **not authored here** — it is generated by the real probe
  `examples/end-to-end-demo/flow.py` and reused verbatim. What the viewer shows
  is real generated data, not a hand-built mock.
* **Mock signing only; no key custody.** The write path signs with the probe's
  mock scheme (a hash, not Ed25519), and only to show the mandate→sign/escalate
  *decision*. It does **not** address the deferred questions — **key custody**
  (where keys live, multi-device) and **cold-start vs unrooted** — which a viewer
  cannot answer and a real client must.
* **No MCP wire, no agent brain.** The proposals are scripted, not produced by a
  live runtime. The point is the boundary's routing, not the runtime.
* Projections are computed by the probe's own fold, **not re-implemented** in
  the page. The HTML is pure presentation; authority over "what the log means"
  stays in the probe.
* The commerce log's delegation is **single-level** (one per-purchase
  AUTHORIZE), so the delegation-tree card is shallow. Multi-level delegation
  lives in the delegation-graph band, which folds over its **own generated
  fixture log** — a second log, stated plainly, not smuggled into the first.
  The seven surfaces and the write path still fold over the commerce log alone.
* The graph shows the **local-attribution side** of agent multiplication only:
  within one observer's root, sub-agents are trivially attributed; across
  principals nothing here forces attribution (the scenario-11
  incentive-incompatibility stands). The stray key is the honest face of that —
  and of the still-open **cold-start** question: a fresh honest root looks
  exactly like an unrooted key until it earns edges.

## Run

```
python3 build.py                # reuses the end-to-end-demo probe + the fixture, writes client.html
open client.html                # any browser; fully self-contained, no server
python3 delegation_fixture.py   # the fixture standalone: narrated flow + both fold readings
```
