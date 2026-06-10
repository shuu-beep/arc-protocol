#!/usr/bin/env python3
"""
ARC delegation-graph fixture — multi-level delegation, stdlib only.

What this is
------------
The reference client's seven surfaces fold over the end-to-end-demo's commerce
log, whose delegation is deliberately single-level. This fixture supplies the
missing depth: ONE generated log in which authority propagates through a
multi-level delegation graph, so the tensions the canon leaves open become
visible objects —

    human root
      └─ coordinator agent           (scoped mandate, 50000)
           ├─ negotiator agent       (narrower mandate, 30000; branch later REVOKED)
           │    └─ scout             (OVER-delegated: granted 80000 by a holder of 30000)
           └─ fulfiller agent        (50000)
                └─ courier           (ephemeral: single-use mandate, retired after one act)
    stray key                        (admissible, but no grant chain to THIS root)

No sixth event type, no identity magic, no Sybil fix. Delegation is an ordinary
`AUTHORIZE consent.mandate`; revocation is the existing `nullifies` field on an
`AUTHORIZE consent.withdraw`; escalation is a fresh root `AUTHORIZE
consent.approval`; everything else is ATTEST/KEY. The graph is never stored —
it is a FOLD over the log, and the fold is parameterized by two choices the
canon deliberately does not make:

  * local_root — rooted-ness is computed FROM a chosen root key. There is no
    global registry: fold the same log from a different root and the picture
    inverts (the stray key becomes the root; everyone else becomes unrooted).
    Local attribution exists without global identity enforcement; an unrooted
    key is rendered at weight 0, not blocked.
  * reading — what a withdrawal does to acts that completed under the grant
    before it was withdrawn (the authority-revocation-demo divergence, finding
    G, now applied to a whole lineage):
      - as_of_act_time       preserve completed acts; void going forward only;
      - current_log_cascade  void the grant's whole history, descendants included.

The two readings AGREE about every act after the withdrawal; they disagree only
about the past — including the absurd edge the cascade produces: routinely
retiring a spent single-use courier voids its already-completed delivery.
One act survives even the cascade: the escalated 40000 payment, because its
basis is a direct root approval, not the revoked chain.

Deliberately dirty and small: mock signatures, single process, scripted flow,
generated (not hand-written) events. A fixture for the viewer; a probe when run
directly. Not a delegation spec and not doctrine.

Run:  python3 delegation_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

LOCAL_ROOT = "k:root"
READINGS = ("as_of_act_time", "current_log_cascade")

NAMES = {
    "k:root": "human-root",
    "k:coord": "coordinator",
    "k:nego": "negotiator",
    "k:fulfil": "fulfiller",
    "k:scout": "scout",
    "k:courier": "courier",
    "k:stray": "stray-key",
}


# ---------------------------------------------------------------------------
# The Event and its mock signing — same lean shape as the other probes.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
    predicate: str
    timestamp: str
    refs: tuple[str, ...] = ()
    nullifies: tuple[str, ...] = ()      # prior event ids withdrawn (event-registry §4.6)
    scope: dict[str, Any] | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    signature: str = ""

    def signing_bytes(self) -> bytes:
        body = {
            "type": self.type, "signer": self.signer, "predicate": self.predicate,
            "timestamp": self.timestamp, "refs": self.refs, "nullifies": self.nullifies,
            "scope": self.scope, "payload": self.payload,
        }
        return json.dumps(body, sort_keys=True, default=list).encode()


def stub_sign(signer: str, body: bytes) -> str:
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies."""
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(
        id="ev:" + hashlib.sha256(body).hexdigest()[:12],
        type=type_, signer=signer, predicate=predicate, timestamp=ts,
        signature=stub_sign(signer, body), **kw,
    )


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: signature check + signer anchored by a prior KEY.
    Note what this does NOT check: rooted-ness. The stray key verifies fine —
    anchoring is a log fact, attribution is a fold result. The two are distinct."""
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# The fold: log -> delegation graph. Parameterized by (local_root, reading).
# This is the boundary logic; the viewer renders its output and adds nothing.
# ---------------------------------------------------------------------------

def project_delegation_graph(events: list[Event], *, local_root: str = LOCAL_ROOT,
                             reading: str = "as_of_act_time") -> dict:
    """Fold the log into a delegation graph as seen FROM `local_root`.

    Per node: status (root/active/revoked/severed/spent/unrooted), the claimed
    ceiling on its own grant vs the EFFECTIVE ceiling (the intersection — min —
    of every ceiling on its chain), and each of its acts judged valid or void.

    An act is valid iff (a) it carries an explicit root approval in refs —
    which stands independent of the mandate chain — or (b) its whole grant
    chain was live at the relevant time AND its amount fits the effective
    ceiling. "Live" is where the two readings split:
      as_of_act_time      — a withdrawal voids the grant only at/after the
                            withdrawal's timestamp; completed acts are preserved;
      current_log_cascade — a withdrawal voids the grant's entire history;
                            completed acts under it (and under every descendant
                            grant) collapse retroactively.
    Nothing here is stored; the graph is recomputed from the log on demand."""
    assert reading in READINGS, f"unknown reading {reading!r}"
    by_id = {e.id: e for e in events}
    order = {e.id: i for i, e in enumerate(events)}

    mandates: dict[str, Event] = {}          # grantee key -> its (first) mandate
    children: dict[str, list[str]] = {}      # granter key -> grantee keys
    for e in events:
        if e.type == "AUTHORIZE" and e.predicate == "consent.mandate" and e.refs:
            grantee = e.refs[0]
            if grantee not in mandates:
                mandates[grantee] = e
                children.setdefault(e.signer, []).append(grantee)

    withdrawn: dict[str, Event] = {}         # grant event id -> (first) withdrawal
    for e in events:
        if e.type == "AUTHORIZE" and e.predicate == "consent.withdraw":
            for mid in e.nullifies:
                withdrawn.setdefault(mid, e)

    def chain(key: str) -> list[Event] | None:
        """Grant chain from `key` up to local_root; None if it never gets there."""
        out, k, seen = [], key, set()
        while k != local_root:
            if k in seen or k not in mandates:
                return None
            seen.add(k)
            m = mandates[k]
            out.append(m)
            k = m.signer
        return out

    def live(grant: Event, t: str) -> bool:
        w = withdrawn.get(grant.id)
        if w is None:
            return True
        if reading == "current_log_cascade":
            return False                     # void over the grant's whole history
        return t < w.timestamp               # forward-scoped: void at/after only

    def judge_act(act: Event, ch: list[Event] | None, effective) -> tuple[bool, str]:
        amount = act.payload.get("amount_krw")
        approval = next((by_id[r] for r in act.refs if r in by_id
                         and by_id[r].predicate == "consent.approval"
                         and by_id[r].signer == local_root), None)
        if approval is not None:
            ceil = (approval.scope or {}).get("max_total_krw")
            if live(approval, act.timestamp) and (amount is None or
                                                  (ceil is not None and amount <= ceil)):
                return True, "explicit root approval — stands independent of the mandate chain"
            return False, "root approval withdrawn or exceeded"
        if ch is None:
            return False, "no grant chain to this root — admissible, projected at weight 0"
        if not all(live(g, act.timestamp) for g in ch):
            if reading == "current_log_cascade":
                return False, "a grant in the chain was withdrawn — cascade voids its whole history"
            return False, "the chain was already withdrawn at act time"
        if amount is not None and effective is not None and amount > effective:
            return False, f"exceeds the effective ceiling {effective} (the inherited intersection)"
        return True, "chain live at act time, within effective scope"

    def node(key: str) -> dict:
        ch = chain(key)
        own = mandates.get(key)
        scope = (own.scope or {}) if own else {}
        ceilings = [c for c in ((g.scope or {}).get("max_total_krw") for g in (ch or []))
                    if c is not None]
        claimed = scope.get("max_total_krw")
        effective = min(ceilings) if ceilings else None
        if key == local_root:
            status = "root"
        elif ch is None:
            status = "unrooted"
        elif own.id in withdrawn:
            status = ("spent" if withdrawn[own.id].payload.get("reason") == "single_use_spent"
                      else "revoked")
        elif any(g.id in withdrawn for g in ch[1:]):
            status = "severed"               # its own grant stands; an ancestor's fell
        else:
            status = "active"
        acts = []
        for e in sorted((e for e in events if e.signer == key and e.type == "ATTEST"),
                        key=lambda e: order[e.id]):
            valid, basis = judge_act(e, ch, effective)
            acts.append({"id": e.id, "signer": key, "predicate": e.predicate,
                         "amount": e.payload.get("amount_krw"),
                         "valid": valid, "basis": basis})
        return {
            "key": key, "status": status,
            "claimed_ceiling": claimed, "effective_ceiling": effective,
            "overclaimed": (claimed is not None and effective is not None
                            and claimed > effective),
            "ephemeral": scope.get("uses") == 1,
            "grant_id": own.id if own else None,
            "grant_withdrawn_by": withdrawn[own.id].id if own and own.id in withdrawn else None,
            "acts": acts,
            "children": [node(c) for c in children.get(key, [])],
        }

    keys = [e.payload["key"] for e in events
            if e.type == "KEY" and e.predicate == "id.key_register"]
    unrooted = [node(k) for k in keys if k != local_root and chain(k) is None]
    return {"reading": reading, "local_root": local_root,
            "tree": node(local_root), "unrooted": unrooted}


def divergent_acts(events: list[Event], *, local_root: str = LOCAL_ROOT) -> list[dict]:
    """Acts whose validity FLIPS between the two readings — the projection
    divergence, computed here (not in the viewer's JavaScript)."""
    def flatten(n: dict, out: dict) -> dict:
        for a in n["acts"]:
            out[a["id"]] = a
        for c in n["children"]:
            flatten(c, out)
        return out

    views = {}
    for r in READINGS:
        p = project_delegation_graph(events, local_root=local_root, reading=r)
        acc: dict = {}
        flatten(p["tree"], acc)
        for u in p["unrooted"]:
            flatten(u, acc)
        views[r] = acc
    order = {e.id: i for i, e in enumerate(events)}
    flips = [eid for eid, a in views["as_of_act_time"].items()
             if a["valid"] != views["current_log_cascade"][eid]["valid"]]
    return [{"id": eid,
             "as_of_act_time": views["as_of_act_time"][eid],
             "current_log_cascade": views["current_log_cascade"][eid]}
            for eid in sorted(flips, key=lambda i: order[i])]


# ---------------------------------------------------------------------------
# Participants — each holds one key and emits its OWN events into the ledger.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, self.ledger.now(), **kw)
        self.ledger.append(ev)
        print(f"    -> {self.name} emits {type_} {predicate}  [{ev.id}] @ {ev.timestamp}")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self._clock = 0

    def now(self) -> str:
        self._clock += 1
        # T1 (morning): grants and acts. T2 (afternoon): the branch revocation
        # and one act attempted after it. Events 1..19 are T1; 20..21 are T2.
        hour = 10 if self._clock <= 19 else 16
        return f"2026-06-09T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The generated flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def generate_log() -> list[Event]:
    led = Ledger()
    root = Party(led, "human-root", "k:root")
    coord = Party(led, "coordinator", "k:coord")
    nego = Party(led, "negotiator", "k:nego")
    fulfil = Party(led, "fulfiller", "k:fulfil")

    print("\n1. Identity — the root and its first agents anchor keys")
    for p in (root, coord, nego, fulfil):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Authority propagates — scoped mandates, narrowing downward")
    root.emit("AUTHORIZE", "consent.mandate", refs=("k:coord",),
              scope={"context": "market", "max_total_krw": 50000})
    m_nego = coord.emit("AUTHORIZE", "consent.mandate", refs=("k:nego",),
                        scope={"context": "market", "max_total_krw": 30000})
    coord.emit("AUTHORIZE", "consent.mandate", refs=("k:fulfil",),
               scope={"context": "market", "max_total_krw": 50000})

    print("\n3. The negotiator acts within its mandate")
    nego.emit("ATTEST", "commerce.offer", refs=(m_nego.id,),
              payload={"item": "bulk_produce", "amount_krw": 24000, "context": "market"})

    print("\n4. Over-delegation — the negotiator grants its scout MORE than it holds")
    scout = Party(led, "scout", "k:scout")
    scout.emit("KEY", "id.key_register", payload={"key": scout.key})
    m_scout = nego.emit("AUTHORIZE", "consent.mandate", refs=("k:scout",),
                        scope={"context": "market", "max_total_krw": 80000})
    say("canon", "the over-wide grant is ADMISSIBLE — the fold, not the log, clamps it")
    scout.emit("ATTEST", "commerce.offer", refs=(m_scout.id,),
               payload={"item": "rare_lot", "amount_krw": 50000, "context": "market"})

    print("\n5. Escalation — the negotiator needs 40000, above its 30000 ceiling")
    say("negotiator", "out of mandate; escalating to the human root for this one act")
    approval = root.emit("AUTHORIZE", "consent.approval", refs=("k:nego",),
                         scope={"context": "market", "max_total_krw": 40000})
    nego.emit("ATTEST", "commerce.payment_result", refs=(approval.id, m_nego.id),
              payload={"result": "confirmed", "amount_krw": 40000, "provider": "mock_pay"})

    print("\n6. An ephemeral agent — single-use mandate, retired after one act")
    courier = Party(led, "courier", "k:courier")
    courier.emit("KEY", "id.key_register", payload={"key": courier.key})
    m_courier = fulfil.emit("AUTHORIZE", "consent.mandate", refs=("k:courier",),
                            scope={"context": "market", "max_total_krw": 0, "uses": 1})
    courier.emit("ATTEST", "commerce.fulfillment", refs=(m_courier.id,),
                 payload={"status": "delivered", "context": "market"})
    fulfil.emit("AUTHORIZE", "consent.withdraw", refs=("k:courier",),
                nullifies=(m_courier.id,), payload={"reason": "single_use_spent"})

    print("\n7. A stray key — verifies fine, but no grant chain to this client's root")
    stray = Party(led, "stray", "k:stray")
    stray.emit("KEY", "id.key_register", payload={"key": stray.key})
    stray.emit("ATTEST", "rep.outcome", refs=("k:nego",),
               payload={"result": "negative", "context": "market"})

    print("\n8. Branch revocation (T2) — the coordinator withdraws the negotiator")
    coord.emit("AUTHORIZE", "consent.withdraw", refs=("k:nego",),
               nullifies=(m_nego.id,), payload={"reason": "branch_closed"})
    say("scout", "keeps acting under its own grant — which was never itself withdrawn")
    scout.emit("ATTEST", "commerce.offer", refs=(m_scout.id,),
               payload={"item": "leftover_lot", "amount_krw": 10000, "context": "market"})

    verify_log(led.events)
    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written. "
          "verify_log passes (the stray key included — anchoring is not attribution).")
    return led.events


# ---------------------------------------------------------------------------
# Standalone run — narrate the flow, then fold it both ways and show the split.
# ---------------------------------------------------------------------------

def _walk(n: dict, depth: int = 0) -> None:
    pad = "  " * depth
    nm = NAMES.get(n["key"], n["key"])
    line = f"    {pad}{nm:<14} {n['status']:<8}"
    if n["effective_ceiling"] is not None:
        line += f" auto-sign ≤ {n['effective_ceiling']}"
        if n["overclaimed"]:
            line += f" (claimed {n['claimed_ceiling']} — clamped by inheritance)"
    print(line)
    for a in n["acts"]:
        v = "VALID" if a["valid"] else "VOID "
        amt = f" {a['amount']} KRW" if a["amount"] is not None else ""
        print(f"    {pad}  · {v} {a['predicate']}{amt} — {a['basis']}")
    for c in n["children"]:
        _walk(c, depth + 1)


def main() -> None:
    events = generate_log()

    print("\n--- the same log, folded two ways (finding G, now on a whole lineage) ---")
    for reading in READINGS:
        p = project_delegation_graph(events, reading=reading)
        print(f"\n  reading = {reading}")
        _walk(p["tree"])
        for u in p["unrooted"]:
            _walk(u, depth=1)

    flips = divergent_acts(events)
    print(f"\n--- projection divergence: {len(flips)} act(s) flip between the readings ---")
    for f in flips:
        a, b = f["as_of_act_time"], f["current_log_cascade"]
        amt = f" {a['amount']} KRW" if a["amount"] is not None else ""
        print(f"    {NAMES.get(a['signer'], a['signer'])} · {a['predicate']}{amt}  [{f['id']}]")
        print(f"      as-of-act-time: {'VALID' if a['valid'] else 'VOID'} — {a['basis']}")
        print(f"      cascade:        {'VALID' if b['valid'] else 'VOID'} — {b['basis']}")

    print("\n--- attribution is local: fold the SAME log from a different root ---")
    inv = project_delegation_graph(events, local_root="k:stray")
    print(f"    from k:stray — rooted: ['k:stray']; unrooted: {len(inv['unrooted'])} keys "
          "(everyone else).")
    print("    Rooted-ness is the observer's fold parameter, not a global fact. No global")
    print("    identity registry exists; an unrooted key is weight 0 here, not blocked.")


if __name__ == "__main__":
    main()
