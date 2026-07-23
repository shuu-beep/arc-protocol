#!/usr/bin/env python3
"""
ARC delegation-graph fixture — multi-level delegation, stdlib only.

What this is
------------
The reference client's base Commerce log uses single-level delegation. This
fixture provides a separate generated log for a multi-level delegation graph:

    human root
      └─ coordinator agent           (scoped mandate, 50000)
           ├─ negotiator agent       (narrower mandate, 30000; later withdrawn)
           │    └─ scout             (granted 80000 by a holder of 30000)
           └─ fulfiller agent        (50000)
                └─ courier           (ephemeral: single-use mandate, retired after one act)
    stray key                        (no grant chain to the selected root)

The fixture encodes delegation with `AUTHORIZE consent.mandate`, withdrawal with
`AUTHORIZE consent.withdraw` plus `nullifies`, and escalation with a root
`AUTHORIZE consent.approval`; the remaining records are ATTEST or KEY. The graph
is a fold over the log parameterized by two fixture choices that Canon does not
select:

  * local_root — rootedness is computed from a chosen root key. This fixture
    uses no global identity registry: fold the same log from a different root and the picture
    inverts (the stray key becomes the root; everyone else becomes unrooted).
    Local attribution exists without global identity enforcement; an unrooted
    key is rendered at weight 0, not blocked.
  * reading — whether the current projection continues to honor acts that
    completed under the grant before it was withdrawn (the authority-revocation-
    demo divergence applied to a whole lineage). Both readings consume the same
    full current log:
      - preserve  continue to honor historically authorized completed acts;
      - cascade   do not honor acts that depend on the withdrawn grant.

The two readings agree about the descendant act emitted after withdrawal and
differ on current honoring of pre-withdrawal acts. Under cascade, the completed
courier delivery is not honored by the current projection. The escalated 40000
payment remains honored because its basis is a direct root approval rather than
the withdrawn chain.

This is a single-process scripted fixture with deterministic mock signatures,
not a delegation specification.

Run:  python3 delegation_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

LOCAL_ROOT = "k:root"
READINGS = ("preserve", "cascade")

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
    """MOCK. This teaching fixture uses a deterministic hash for reproducible replay, not production security; ARC has no selected normative signature suite, so implementations and named profiles select and declare their suite."""
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
    """Fixture replay check: deterministic mock signature and prior KEY
    registration only. Rootedness and authority are separate fixture folds."""
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
                             reading: str = "preserve") -> dict:
    """Fold the log into a delegation graph as seen from `local_root`.

    Per node: status (root/active/revoked/severed/spent/unrooted), the claimed
    ceiling on its own grant vs the effective ceiling (the intersection — min —
    of every ceiling on its chain), and whether each act is honored now.

    An act is honored now iff (a) it carries an explicit root approval in refs —
    which stands independent of the mandate chain — or (b) its whole grant chain
    supports it under the selected current-honoring policy and its amount fits
    the effective ceiling:
      preserve — a later withdrawal does not remove support from a completed act;
      cascade  — the current projection does not honor acts that depend on a
                 withdrawn grant, including descendant grants.
    For the pre-withdrawal rows that differ, this fixture assigns
    `authorized_at_act=True`; it does not independently derive complete act-time
    authority. Current honoring then changes by policy.
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

    def grant_supports_act(grant: Event, t: str) -> bool:
        w = withdrawn.get(grant.id)
        if w is None:
            return True
        if reading == "cascade":
            return False                     # not honored by this current projection
        return t < w.timestamp               # preserve completed pre-withdrawal acts

    def judge_act(act: Event, ch: list[Event] | None, effective) -> tuple[bool, str]:
        amount = act.payload.get("amount_krw")
        approval = next((by_id[r] for r in act.refs if r in by_id
                         and by_id[r].predicate == "consent.approval"
                         and by_id[r].signer == local_root), None)
        if approval is not None:
            ceil = (approval.scope or {}).get("max_total_krw")
            if grant_supports_act(approval, act.timestamp) and (amount is None or
                                                                (ceil is not None and amount <= ceil)):
                return True, "explicit root approval — honored independently of the mandate chain"
            return False, "root approval withdrawn or exceeded"
        if ch is None:
            return False, "no grant chain to this root — admissible, projected at weight 0"
        if not all(grant_supports_act(g, act.timestamp) for g in ch):
            if reading == "cascade":
                return False, "a grant in the chain was withdrawn — not honored by the cascade projection"
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
            honored_now, basis = judge_act(e, ch, effective)
            acts.append({"id": e.id, "signer": key, "predicate": e.predicate,
                         "amount": e.payload.get("amount_krw"),
                         "honored_now": honored_now, "basis": basis})
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
    """Acts whose current honoring differs between the two readings — the projection
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
    flips = [eid for eid, a in views["preserve"].items()
             if a["honored_now"] != views["cascade"][eid]["honored_now"]]
    return [{"id": eid,
             "authorized_at_act": True,
             "preserve": views["preserve"][eid],
             "cascade": views["cascade"][eid]}
            for eid in sorted(flips, key=lambda i: order[i])]


# ---------------------------------------------------------------------------
# Participants — each holds one key and emits its own events into the ledger.
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

    print("\n2. Scoped mandate chain — ceilings narrow down the fixture graph")
    root.emit("AUTHORIZE", "consent.mandate", refs=("k:coord",),
              scope={"context": "market", "max_total_krw": 50000})
    m_nego = coord.emit("AUTHORIZE", "consent.mandate", refs=("k:nego",),
                        scope={"context": "market", "max_total_krw": 30000})
    coord.emit("AUTHORIZE", "consent.mandate", refs=("k:fulfil",),
               scope={"context": "market", "max_total_krw": 50000})

    print("\n3. The negotiator acts within its mandate")
    nego.emit("ATTEST", "commerce.offer", refs=(m_nego.id,),
              payload={"item": "bulk_produce", "amount_krw": 24000, "context": "market"})

    print("\n4. Over-delegation — the negotiator grants its scout a higher stated ceiling")
    scout = Party(led, "scout", "k:scout")
    scout.emit("KEY", "id.key_register", payload={"key": scout.key})
    m_scout = nego.emit("AUTHORIZE", "consent.mandate", refs=("k:scout",),
                        scope={"context": "market", "max_total_krw": 80000})
    say("fixture", "the replay check accepts the grant; this fold clamps its effective ceiling")
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

    print("\n7. A stray key — passes the mock replay check, but has no grant chain to this client's root")
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
    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events. "
          "The replay check passes with the stray key included; key registration "
          "does not establish attribution to this fixture root.")
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
        v = "HONORED    " if a["honored_now"] else "NOT HONORED"
        amt = f" {a['amount']} KRW" if a["amount"] is not None else ""
        print(f"    {pad}  · {v} {a['predicate']}{amt} — {a['basis']}")
    for c in n["children"]:
        _walk(c, depth + 1)


def main() -> None:
    events = generate_log()

    print("\n--- the full current log, folded under two honoring policies ---")
    for reading in READINGS:
        p = project_delegation_graph(events, reading=reading)
        print(f"\n  reading = {reading}")
        _walk(p["tree"])
        for u in p["unrooted"]:
            _walk(u, depth=1)

    flips = divergent_acts(events)
    print(f"\n--- projection divergence: {len(flips)} act(s) differ between the readings ---")
    for f in flips:
        a, b = f["preserve"], f["cascade"]
        amt = f" {a['amount']} KRW" if a["amount"] is not None else ""
        print(f"    {NAMES.get(a['signer'], a['signer'])} · {a['predicate']}{amt}  [{f['id']}]")
        print(f"      authorized_at_act={f['authorized_at_act']}  (fixture assumption)")
        print(f"      preserve: {'HONORED' if a['honored_now'] else 'NOT HONORED'} — {a['basis']}")
        print(f"      cascade:  {'HONORED' if b['honored_now'] else 'NOT HONORED'} — {b['basis']}")

    print("\n--- fold the same log from a different selected root ---")
    inv = project_delegation_graph(events, local_root="k:stray")
    print(f"    from k:stray — rooted: ['k:stray']; unrooted: {len(inv['unrooted'])} keys "
          "(everyone else).")
    print("    Rooted-ness is this projection's fold parameter. This fixture uses no")
    print("    global identity registry; an unrooted key is weight 0 here, not blocked.")


if __name__ == "__main__":
    main()
