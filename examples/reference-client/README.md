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
├──────────────────────────────────────────────────────────────────────────────┤
│  cold start — legitimacy matrix (fixture log · three observers · two cuts)     │
├──────────────────────────────────────────────────────────────────────────────┤
│  compromise — blast radius of a stolen hot key (real Ed25519 · 2 moments × 2)  │
├──────────────────────────────────────────────────────────────────────────────┤
│  federation — what a bridge imports (5 observers · 3 moments × 2 readings)      │
├──────────────────────────────────────────────────────────────────────────────┤
│  custody seam — what the approval carries back (real Ed25519 · 2 readings)      │
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
| cold-start matrix | a separate 30-event fixture log (`coldstart_fixture.py`), folded by 3 observers |
| compromise band | a separate 12-event fixture log (`compromise_fixture.py`, **real Ed25519**), folded at 2 moments × 2 revoke readings |
| federation band | a separate 15-event fixture log (`federation_fixture.py`), folded by 5 observers at 3 moments × 2 severance readings |
| custody seam band | a separate 6-event fixture log (`approval_seam_fixture.py`, **real Ed25519**), the sign-time wall + an approval judged under 2 readings (proposal-bound / scope-only) |

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

## The cold-start matrix — uncertainty rendered, not resolved

The last band enters the region *before* legitimacy is established — where the
log does not yet contain enough to establish it. The claim:

> at cold start the log does not contain the information that would
> distinguish an honest newcomer from a disguised Sybil. The distinction is
> made by an observer's fold **policy**; policies legitimately disagree; and
> what ARC renders is the **disagreement itself** — not a verdict.

A third fixture log (`coldstart_fixture.py`, 30 events, runnable standalone)
generates four newcomers that are indistinguishable *in kind* on the log:

* **nova** — honest but unlinked: two real trades, one counterparty, no vouch;
* **mint** — a storefront pumped by a disposable swarm whose shared operator is
  **not in the log** (hidden siblings disclose nothing — scenario 11);
* **pact-1 / pact-2** — a coalition: mutual vouches, one casual outside tie,
  zero history; it breaks from the inside at the second cut;
* **anointed** — granted a mandate by an established root *before any history*:
  authority arriving faster than reputation.

Three observers fold the same log — `(root, policy, honored adjudicator)` —
and each legitimate policy fails on a different newcomer: the **path** observer
treats honest nova exactly like sybil mint (weight 0); the **history** observer
ranks mint's manufactured volume *above* nova's real record; the **social**
observer admits the whole coalition through one casual vouch — flagged in the
cell as *"hinges on one tie"*, a weak social link carrying constitutional
weight — until the coalition defects.

Between the two cuts the collapse lands, and the matrix moves in ways no single
score could express: **anointed's authority dies while its earned reputation
survives** (the same withdrawal read in opposite directions by two observers);
two communities rule the *same dispute* about mint in **opposite directions**
(`gov.warning` vs `gov.dismissal`), and observers split along which ruling they
honor — roots dividing into factions; pact-2 is left with a retracted tie and
an open dispute nobody has adjudicated.

What the band refuses to do is as deliberate as what it shows: no composite
legitimacy score (a single number would be the social-credit shape); no
protocol-level identity verification — the generator's ground truth ("mint and
the swarm share an operator") is rendered in a separate strip labeled
**available to no observer**, and the folds never see it. The honest finding:
the canon offers a newcomer exactly three exits — *earn* edges slowly,
*manufacture* volume, or *borrow* a weak tie — and no observer can read off the
log which exit produced the appearance in front of them. This is the
threat-model's adoption frontier seen from a single node, made visible rather
than solved.

## The compromise band — a stolen hot key, and the exact size of the damage

The last band is the only one on **real Ed25519** (a pure-stdlib RFC-8032
reference, no dependency), because custody's claim cannot be tested on a mock
hash: *a signature proves a key signed, it proves nothing about how the key was
kept.* A cold `root` grants a hot `agent` a narrow mandate (market, ≤30000); the
agent acts once legitimately; then the attacker **exfiltrates the agent's secret
bytes** and forges five events whose signatures genuinely verify.

The honoring grid carries a green **SIG VALID** chip on every row — forgeries
included — and that is the point: *what bounds the damage is never the signature,
it is the mandate fold.* The over-ceiling and out-of-context forgeries fall to
scope; the self-elevation `AUTHORIZE` falls to the tier line (a hot key cannot
forge the cold root, so it cannot mint itself authority); the post-revoke act
falls to time. What gets honored is exactly one in-scope forgery — **25000 KRW**
— and the band reads off the finding it forces:

> blast radius = mandate scope **× detection latency**. Scope sets the height of
> the damage per act; the time until the revoke lands sets its width.

Two toggles drive it. The **revoke reading** (time-scoped / cascade) shows that
neither reading is surgical: time-scoped preserves the in-scope forgery *and* the
honest history; cascade voids the forgery *and* the honest history. The
**moment** toggle (just after the revoke / after the adjudication) shows the
residue revocation cannot reach — just after the revoke, the legitimate 20000 and
the forged 25000 are **byte-indistinguishable**, identical verdicts under both
readings, because on the log they *are* the same act. They separate only *after
the adjudication*, and only because the human supplied off the log the one fact
the log never held — that the 25000 was not theirs (a `CHALLENGE` + an honored
`ADJUDICATE` voiding that single event). The same three-layer split the
revocation probes draw: **signature valid (log) / scope honored (fold) / void
(authority).**

As in the cold-start band, the generator's ground truth — *who actually held the
pen* — is rendered in a separate strip labeled **available to no observer**, and
the honoring grid never receives it. The blast-radius number is the fold
intersected with that strip, so it is a quantity **no observer can compute**:
none can see which honored act was forged. A probe finding extending
[`docs/key-custody.md`](../../docs/key-custody.md) §5/§8, not settled doctrine.

## The federation band — what a bridge imports

The newest band is the first executable slice of federation, deliberately
small: **one log, two community authorities, and observers who must decide what
the other community's adjudication is worth.** A fifth fixture log
(`federation_fixture.py`, 15 events, runnable standalone) stages the conflict:
a cross-community sale is disputed; **community-harbor** rules *suspension* (its
strict rule: late delivery is non-fulfillment); the vendor appeals at home and
**community-orchard** rules *dismissal* (its rule: delivered late is still
delivered). Before any of this, orchard had **recognized harbor's commerce
rulings** — the bridge, an ordinary `AUTHORIZE` (`fed.recognition`) with a
`scope`. After the conflict, orchard severs it (`fed.severance` + `nullifies`).
No new primitive anywhere — and that is half the finding.

Five observers fold the same log, differing only in fold parameters: harbor's
own observer (who holds no bridge — **bridges are directional**); an orchard
observer who reads the bridge as *nothing* (imported rulings weigh 0, the
stray-key treatment); one who reads it as **advisory** (the imported ruling is a
visible flag that moves no standing); one who reads it as **authority** with a
precedence rule (on conflict, local supersedes — *override is a precedence
choice inside a fold, not an event*); and one who reads it as authority with
**no precedence rule**. That last cell is the band's center: when two honored
authorities conflict and nothing ranks them, the projection is **CONTESTED** —
rendered as a literally split chip, because the only thing that would dissolve
it is an authority of last resort, the corner ARC declines.

The severance toggle replays the revocation divergence on the federation side:
under **time-scoped**, severing the bridge moves *nothing* — it bounds future
imports, it does not sort the past, and the contested cell **outlives the bridge
that created it**; under **cascade**, the contested cell "resolves" — but only
because the severed bridge is read as never having existed, voiding every ruling
it carried. Resolution by amnesia, not resolution.

The refusals are load-bearing: a bridge reading is **categorical** (authority /
advisory / ignore), never a numeric trust weight — a community-trust scalar
would be the composite score ARC refuses, one level up. And the omniscient strip
carries the band's quietest point: the goods were in fact delivered (late), both
rulings are sincere, and **no fold keys on the delivery fact — every fold keys
on which authority it honors**. Why orchard recognized harbor in the first place
is not in the log and no fold can read it: the adoption boundary, unchanged. A
probe finding, not doctrine.

## The custody seam — what the approval carries back

The newest band is the second on **real Ed25519**, and it descends from a
question the compromise band left standing: if the key lives behind a separate
signer, what does *escalation* carry? Its fixture (`approval_seam_fixture.py`, 6
events, runnable standalone) splits the agent from the signer so the agent holds
no key — it can only *propose*. The first panel is that **sign-time wall**: an
in-scope payment is SIGNED, an over-ceiling one is ROUTED to a human, and an
out-of-domain forgery and a self-mint-as-root attempt are REFUSED — the last two
*never become events*, because the cold key is not in the process to sign them.

The second panel is the finding. A routed proposal needs an approval **return
path** the one-way proposal seam never had, so a human reviews the exact bytes
("pay 90000 to merchant-rho — the same bytes the signer would sign") and approves
with the cold key. Then the **same approval, in flight back through the untrusted
agent**, is judged under two readings, and the toggle *is* the point: under
**proposal-bound** the approval is tied to the one proposal's content hash, so a
re-aim (different hash), a replay (already spent), and a bare scope token (names
no proposal) all die at sign-time; flip to **scope-only** — the context+amount
token the embodiment fixture carried — and all three turn **SIGNED**. That grid
is the fixture's own `scope_only_would_sign()`, a *computed counterfactual*: a
scope token is a bearer token, and binding is exactly what removes it.

The residue the band leaves visible: binding makes the **human a second signer**.
The approval is only as good as what the human *saw*, so the inbox owes a human's
eyes the same "sign what you saw" property the signer's bytes give — `ROUTE` is
not "defer to a human," it opens a second custody boundary. A probe finding
extending [`docs/key-custody.md`](../../docs/key-custody.md) §5/§8, not doctrine.

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
* **The write path mocks signing; the compromise band does not.** The write
  path signs with the probe's mock scheme (a hash, not Ed25519), and only to show
  the mandate→sign/escalate *decision* — *where* keys live is not its subject.
  The compromise band is the exception: it runs on **real Ed25519** precisely
  because its subject *is* custody, and a mock signature cannot carry the claim
  that a stolen key produces genuine signatures. The two coexist honestly — the
  write path demonstrates routing, the compromise band demonstrates what a real
  signature can and cannot prove.
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
  incentive-incompatibility stands). The stray key is the honest face of that.
* The cold-start matrix takes the once-deferred **cold-start vs unrooted**
  question as far as a viewer can: it shows the indistinguishability and the
  observer disagreement, but it does not (and must not) resolve them.
* **Key custody** has moved from deferred to probed. A design treatment exists
  ([`docs/key-custody.md`](../../docs/key-custody.md)), and the compromise band
  now runs its one probe-able slice (§5) on real keys — the blast radius of a
  stolen hot key. What the band still does *not* settle is everything §8 leaves
  open (a compromised signer, threshold custody, enclave attestation); a viewer
  cannot, and a real client must.
* The federation band is a **first slice, deliberately small**: one bridge, one
  direction, one disputed act. Schism, observer migration, meta-folding (reading
  someone *else's* bridges to discount them), and multi-bridge conflict are
  explicitly out of scope for this cycle. And the band shows what a bridge *is*,
  not what makes one worth issuing — the adoption/incentive question stays open.
* The custody-seam band runs on **real Ed25519** for the same reason the
  compromise band does: "this approval validates against that one proposal" must
  be a fact, not a claim. But it is **not a wallet, not a daemon, not a security
  product** — the "processes" are objects sharing a serializable seam, with no
  network, persistence, or real isolation. The scope-only reading is a *computed
  counterfactual*, not a second live signer. What it does not settle is what
  makes a human's review reliable (ceremony fatigue, §8) and the availability of
  the return path — both stated open, neither solved by a viewer.

## Run

```
python3 build.py                # reuses the end-to-end-demo probe + all five fixtures, writes client.html
open client.html                # any browser; fully self-contained, no server
python3 delegation_fixture.py   # fixture standalone: narrated flow + both fold readings
python3 coldstart_fixture.py    # fixture standalone: narrated flow + the matrix at both cuts
python3 compromise_fixture.py   # fixture standalone: real Ed25519, the blast radius + the residue
python3 federation_fixture.py   # fixture standalone: the bridge, the contested cell, both severance readings
python3 approval_seam_fixture.py # fixture standalone: the sign-time wall + bearer-vs-bound approval
```
