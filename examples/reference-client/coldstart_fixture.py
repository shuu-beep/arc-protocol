#!/usr/bin/env python3
"""
ARC cold-start fixture — legitimacy before anyone can know whom to trust.

What this is
------------
The delegation-graph fixture showed that authority can be attributed locally,
with no global identity — rooted-ness is the observer's fold parameter. This
fixture pushes into the unstable region BEFORE that: the cold start, where
legitimacy is not yet established and the log does not contain enough to
establish it.

The claim under test:

    at cold start the log does not contain the information that would
    distinguish an honest newcomer from a disguised Sybil. The distinction is
    made by an observer's fold POLICY; policies legitimately disagree; and what
    ARC should render is the disagreement itself — not a verdict.

Four newcomers arrive, indistinguishable in kind on the log:

    nova      honest but unlinked — two real trades, one counterparty, no vouch
    mint      a storefront pumped by a disposable swarm (sw1..sw3) whose shared
              operator is NOT in the log — volume that looks like history
    pact1/2   a coalition: mutual vouches, one casual outside tie, zero history
    anointed  granted a mandate by an established root BEFORE any history —
              authority arriving faster than reputation

Three observers fold the SAME log, each with a root and a policy — all three
policies are legitimate folds, and each one fails on a different newcomer:

    observer-P  (root A)  path policy:    weight only via a live vouch/mandate
                          path from my root        -> treats honest nova exactly
                                                      like sybil mint: weight 0
    observer-H  (root A)  history policy: outcomes + distinct counterparties,
                          no path needed            -> ranks mint's fake volume
                                                      ABOVE nova's real history
    observer-T  (root B)  social policy:  vouches transitive to depth 2
                                                     -> admits the coalition,
                                                      until the coalition breaks

Two cuts of the log: "on arrival" and "after the collapse" (the anointing root
withdraws its mandate; the coalition defects internally; two communities rule
the SAME dispute about mint in opposite directions, and observers split along
which ruling they honor). Between the cuts, the anointed agent moves in
OPPOSITE directions under different policies — its authority dies while its
earned reputation survives.

What this fixture refuses to do (deliberately):
  * no composite legitimacy score — each cell shows a categorical reading plus
    the raw events it rests on (a single number would be the social-credit shape);
  * no protocol-level identity verification — the generator KNOWS who is real
    (it wrote the flow), and that knowledge is rendered separately as "the
    omniscient view, available to no observer"; the folds never see it;
  * no onboarding ladder, no minimum-edge doctrine, no new event type. Vouching
    is `ATTEST rep.vouch`, retraction is `ATTEST rep.retraction` + `nullifies`
    — registry-style vocabulary over the five canonical types.

The honest finding: the canon offers a newcomer exactly three exits from the
cold start — earn edges slowly (nova), manufacture volume (mint), or borrow a
weak tie (pact1, anointed) — and no observer can read off the log which exit
produced the appearance in front of them. This is threat-model §18.1's
adoption frontier seen from a single node. A fixture and a probe, not doctrine.

Run:  python3 coldstart_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

NAMES = {
    "k:rootA": "community-A",
    "k:rootB": "community-B",
    "k:elder": "elder",
    "k:nova": "nova",
    "k:mint": "mint",
    "k:sw1": "swarm-1", "k:sw2": "swarm-2", "k:sw3": "swarm-3",
    "k:pact1": "pact-1",
    "k:pact2": "pact-2",
    "k:anointed": "anointed",
}

SUBJECTS = ("k:nova", "k:mint", "k:pact1", "k:pact2", "k:anointed")

# Each observer = a root + a fold policy + which adjudicator it honors.
# All three are legitimate folds; none of them is "the" reading.
OBSERVERS = (
    {"name": "observer-P", "root": "k:rootA", "policy": "path", "honors": "k:rootA",
     "blurb": "weight only via a live vouch/mandate path from my root"},
    {"name": "observer-H", "root": "k:rootA", "policy": "history", "honors": "k:rootA",
     "blurb": "weight from outcome history — counterparties, not paths"},
    {"name": "observer-T", "root": "k:rootB", "policy": "social", "honors": "k:rootB",
     "blurb": "vouches transitive to depth 2 from my root; history ignored"},
)

CUTS = (
    ("on arrival", "2026-06-10T12:00:00Z"),
    ("after the collapse", "2026-06-10T23:59:00Z"),
)

# What only the generator knows. The folds never see this; the viewer renders
# it separately, labeled as available to NO observer.
GROUND_TRUTH = (
    "mint and swarm-1..3 share one operator. The log does not contain this "
    "fact — the swarm registered independent keys and disclosed nothing "
    "(scenario 11: hidden siblings simply omit the linkage).",
    "nova is honest. Nothing in the log distinguishes its thin real history "
    "from the early stage of a patient Sybil.",
    "the pact coalition had zero history and one casual outside tie; its "
    "depth-2 legitimacy under observer-T rested entirely on that single vouch.",
    "which of the three exits — earn, manufacture, borrow — produced each "
    "appearance cannot be read off the log. That absence IS the cold start.",
)


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
    The swarm keys verify fine — anchoring is a log fact, legitimacy is not."""
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
# The fold: log -> one observer's legitimacy reading of one subject, at a cut.
# Boundary logic lives here; the viewer renders the output and adds nothing.
# ---------------------------------------------------------------------------

def _nullified_at(events: list[Event]) -> dict[str, str]:
    """event id -> timestamp of the earliest event that nullifies it."""
    out: dict[str, str] = {}
    for e in events:
        for target in e.nullifies:
            if target not in out or e.timestamp < out[target]:
                out[target] = e.timestamp
    return out


def _edges(events: list[Event], asof: str, kinds: tuple[str, ...],
           dead: dict[str, str], live_only: bool = True):
    """Directed trust edges signer -> refs[0], recorded at or before the cut."""
    preds = {"vouch": ("ATTEST", "rep.vouch"), "mandate": ("AUTHORIZE", "consent.mandate")}
    for e in events:
        if e.timestamp > asof or not e.refs:
            continue
        for kind in kinds:
            t, p = preds[kind]
            if e.type == t and e.predicate == p:
                if live_only and dead.get(e.id, "9999") <= asof:
                    break
                yield (e.signer, e.refs[0], e, kind)
                break


def _bfs(events, root, asof, kinds, dead, *, max_depth=None, live_only=True) -> dict[str, list]:
    """Shortest edge-paths from `root`; {key: [edge events along the path]}."""
    adj: dict[str, list] = {}
    for a, b, e, kind in _edges(events, asof, kinds, dead, live_only):
        adj.setdefault(a, []).append((b, e, kind))
    reach: dict[str, list] = {root: []}
    frontier = [root]
    depth = 0
    while frontier and (max_depth is None or depth < max_depth):
        depth += 1
        nxt = []
        for a in frontier:
            for b, e, kind in adj.get(a, []):
                if b not in reach:
                    reach[b] = reach[a] + [(e, kind)]
                    nxt.append(b)
        frontier = nxt
    return reach


def project_legitimacy(events: list[Event], observer: dict, asof: str) -> dict:
    """One observer's reading of every subject at one cut of the log.

    Returns categorical verdicts plus the exact events each verdict rests on.
    Deliberately NOT a score, and deliberately different per policy — the
    disagreement between observers is the projection's real content. A verdict
    that hangs on a single tie is flagged (`hinge`): remove that one event and
    the subject becomes unreachable — a weak social link carrying
    constitutional weight."""
    dead = _nullified_at(events)
    root, policy, honors = observer["root"], observer["policy"], observer["honors"]

    def adjudication(subject: str):
        """The ruling overlay — only rulings by the adjudicator THIS observer
        honors. Two communities can rule the same dispute in opposite
        directions; observers split along this line."""
        verdicts = []
        resolved = set()
        for e in events:
            if (e.type == "ADJUDICATE" and e.signer == honors
                    and e.timestamp <= asof and subject in e.refs):
                label = {"gov.warning": "warned", "gov.dismissal": "cleared"}.get(
                    e.predicate, e.predicate)
                verdicts.append({"label": label, "id": e.id})
                resolved.update(e.refs)
        open_disputes = [e.id for e in events
                         if e.type == "CHALLENGE" and e.predicate == "dispute.open"
                         and e.timestamp <= asof and subject in e.refs
                         and e.id not in resolved]
        return verdicts, open_disputes

    def hinge_of(path, kinds, max_depth, subject):
        """If removing the path's first edge disconnects the subject, that one
        event is the hinge the whole judgment hangs on."""
        if not path:
            return None
        first = path[0][0]
        adj_dead = dict(dead)
        adj_dead[first.id] = "0000"          # treat the first edge as never live
        reach = _bfs(events, root, asof, kinds, adj_dead, max_depth=max_depth)
        return first.id if subject not in reach else None

    def cell(subject: str) -> dict:
        basis, hinge, detail = [], None, ""
        if policy == "path":
            kinds = ("vouch", "mandate")
            reach = _bfs(events, root, asof, kinds, dead)
            if subject in reach:
                path = reach[subject]
                kind = "MANDATED" if path[-1][1] == "mandate" else "VOUCHED"
                verdict, cat = f"{kind} · depth {len(path)}", "affirm"
                detail = "a live path from my root: " + " → ".join(
                    NAMES.get(e.signer, e.signer) for e, _ in path)
                basis = [e.id for e, _ in path]
                hinge = hinge_of(path, kinds, None, subject)
            else:
                ghost = _bfs(events, root, asof, kinds, dead, live_only=False)
                if subject in ghost:
                    verdict, cat = "PATH DEAD", "dead"
                    wd = [dead.get(e.id) for e, _ in ghost[subject] if e.id in dead]
                    detail = ("a path existed but a grant on it was withdrawn"
                              + (f" at {wd[0]}" if wd else ""))
                    basis = [e.id for e, _ in ghost[subject]]
                else:
                    verdict, cat = "NO PATH", "none"
                    detail = ("no vouch or mandate connects my root to this key — "
                              "weight 0, honest or not")
        elif policy == "history":
            outs = [e for e in events
                    if e.type == "ATTEST" and e.predicate == "rep.outcome"
                    and e.timestamp <= asof and subject in e.refs
                    and dead.get(e.id, "9999") > asof]
            signers = {e.signer for e in outs}
            basis = [e.id for e in outs]
            if not outs:
                verdict, cat = "NO HISTORY", "none"
                detail = "no outcome ever recorded about this key"
            elif len(signers) < 2:
                verdict, cat = "THIN", "thin"
                detail = (f"{len(outs)} outcome(s), all from one counterparty — "
                          "too few independent voices to lean on")
            else:
                verdict, cat = "ENGAGEABLE", "affirm"
                detail = (f"{len(outs)} outcome(s) from {len(signers)} distinct "
                          "counterparties — this policy cannot see whether the "
                          "counterparties are independent")
        else:  # social
            kinds = ("vouch",)
            reach = _bfs(events, root, asof, kinds, dead, max_depth=2)
            if subject in reach:
                path = reach[subject]
                verdict, cat = f"VOUCHED · depth {len(path)}", "affirm"
                detail = "vouch chain: " + " → ".join(
                    NAMES.get(e.signer, e.signer) for e, _ in path)
                basis = [e.id for e, _ in path]
                hinge = hinge_of(path, kinds, 2, subject)
            else:
                full = _bfs(events, root, asof, kinds, dead)
                ghost = _bfs(events, root, asof, kinds, dead, live_only=False)
                if subject in full:
                    verdict, cat = "BEYOND HORIZON", "thin"
                    detail = (f"a vouch chain exists at depth {len(full[subject])}, "
                              "past this observer's transitive horizon of 2")
                    basis = [e.id for e, _ in full[subject]]
                elif subject in ghost:
                    verdict, cat = "TIE RETRACTED", "dead"
                    detail = "the vouch chain that once reached this key was retracted"
                    basis = [e.id for e, _ in ghost[subject]]
                else:
                    verdict, cat = "NO SOCIAL PATH", "none"
                    detail = "no vouch chain from my root, at any depth"
        rulings, open_disputes = adjudication(subject)
        return {"subject": subject, "verdict": verdict, "category": cat,
                "detail": detail, "basis": basis, "hinge": hinge,
                "rulings": rulings, "open_disputes": open_disputes}

    return {"observer": observer["name"], "root": root, "policy": policy,
            "honors": honors, "blurb": observer["blurb"], "asof": asof,
            "cells": {s: cell(s) for s in SUBJECTS}}


def matrix(events: list[Event], asof: str) -> list[dict]:
    """All observers' readings at one cut — the disagreement, computed."""
    return [project_legitimacy(events, o, asof) for o in OBSERVERS]


def changed_cells(events: list[Event]) -> list[dict]:
    """Verdicts that moved between the two cuts — including the ones that move
    in opposite directions for the same subject."""
    before = {(p["observer"], s): c for p in matrix(events, CUTS[0][1])
              for s, c in p["cells"].items()}
    after = {(p["observer"], s): c for p in matrix(events, CUTS[1][1])
             for s, c in p["cells"].items()}
    out = []
    for k in before:
        b, a = before[k], after[k]
        b_label = b["verdict"] + "".join(" · " + r["label"] for r in b["rulings"])
        a_label = a["verdict"] + "".join(" · " + r["label"] for r in a["rulings"])
        if b_label != a_label:
            out.append({"observer": k[0], "subject": k[1],
                        "before": b_label, "after": a_label})
    return out


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
        # Morning: arrivals (events 1..22, before cut 1 at 12:00). Midday: the
        # anointed agent earns real history. Evening: the collapse.
        hour = 9 if self._clock <= 22 else (13 if self._clock <= 24 else 19)
        return f"2026-06-10T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The generated flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def generate_log() -> list[Event]:
    led = Ledger()
    rootA = Party(led, "community-A", "k:rootA")
    rootB = Party(led, "community-B", "k:rootB")
    elder = Party(led, "elder", "k:elder")

    print("\n1. The established world — two community roots and one elder member")
    for p in (rootA, rootB, elder):
        p.emit("KEY", "id.key_register", payload={"key": p.key})
    rootA.emit("ATTEST", "rep.vouch", refs=("k:elder",),
               payload={"context": "market", "note": "long-standing member"})

    print("\n2. nova arrives — honest, unlinked: two real trades, one counterparty")
    nova = Party(led, "nova", "k:nova")
    nova.emit("KEY", "id.key_register", payload={"key": nova.key})
    for n in (1, 2):
        elder.emit("ATTEST", "rep.outcome", refs=("k:nova",),
                   payload={"result": "positive", "context": "market", "trade": n})

    print("\n3. mint arrives — with a disposable swarm whose shared operator is OFF the log")
    mint = Party(led, "mint", "k:mint")
    mint.emit("KEY", "id.key_register", payload={"key": mint.key})
    for k in ("k:sw1", "k:sw2", "k:sw3"):
        sw = Party(led, NAMES[k], k)
        sw.emit("KEY", "id.key_register", payload={"key": k})
        sw.emit("ATTEST", "rep.outcome", refs=("k:mint",),
                payload={"result": "positive", "context": "market"})
    say("generator", "sw1..sw3 are mint's own agents — the log records nothing of it")

    print("\n4. The pact — a coalition of newcomers with one casual outside tie")
    pact1 = Party(led, "pact-1", "k:pact1")
    pact2 = Party(led, "pact-2", "k:pact2")
    pact1.emit("KEY", "id.key_register", payload={"key": pact1.key})
    pact2.emit("KEY", "id.key_register", payload={"key": pact2.key})
    rootB.emit("ATTEST", "rep.vouch", refs=("k:pact1",),
               payload={"context": "market", "note": "met once at a meetup"})
    v_p1p2 = pact1.emit("ATTEST", "rep.vouch", refs=("k:pact2",),
                        payload={"context": "market"})
    pact2.emit("ATTEST", "rep.vouch", refs=("k:pact1",), payload={"context": "market"})
    pact2.emit("ATTEST", "rep.vouch", refs=("k:mint",),
               payload={"context": "market", "note": "coalition reaches outward"})

    print("\n5. anointed arrives — authority BEFORE reputation")
    anointed = Party(led, "anointed", "k:anointed")
    anointed.emit("KEY", "id.key_register", payload={"key": anointed.key})
    say("community-A", "granting a mandate to a key with zero recorded history")
    m_anointed = rootA.emit("AUTHORIZE", "consent.mandate", refs=("k:anointed",),
                            scope={"context": "market", "max_total_krw": 20000})

    print("\n--- cut 1 (12:00): on arrival — fold the matrix here ---")

    print("\n6. Midday — the anointed agent earns REAL history under its mandate")
    elder.emit("ATTEST", "rep.outcome", refs=("k:anointed",),
               payload={"result": "positive", "context": "market"})
    rootB.emit("ATTEST", "rep.outcome", refs=("k:anointed",),
               payload={"result": "positive", "context": "market"})

    print("\n7. Evening — the collapse")
    say("community-A", "confidence lost; withdrawing the anointed mandate")
    rootA.emit("AUTHORIZE", "consent.withdraw", refs=("k:anointed",),
               nullifies=(m_anointed.id,), payload={"reason": "confidence_lost"})
    say("pact-1", "the coalition breaks from the inside")
    pact1.emit("ATTEST", "rep.retraction", refs=("k:pact2",),
               nullifies=(v_p1p2.id,), payload={"reason": "defection"})
    pact1.emit("CHALLENGE", "dispute.open", refs=("k:pact2",),
               payload={"reason": "broke_agreement", "context": "market"})
    say("elder", "mint's outcomes look coordinated; opening a dispute")
    d_mint = elder.emit("CHALLENGE", "dispute.open", refs=("k:mint",),
                        payload={"reason": "suspected_coordinated_outcomes",
                                 "context": "market"})
    say("community-A / community-B", "the SAME dispute, ruled in opposite directions")
    rootA.emit("ADJUDICATE", "gov.warning", refs=("k:mint", d_mint.id),
               payload={"resolves": d_mint.id, "context": "market"})
    rootB.emit("ADJUDICATE", "gov.dismissal", refs=("k:mint", d_mint.id),
               payload={"resolves": d_mint.id, "context": "market"})

    verify_log(led.events)
    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written. "
          "verify_log passes — the swarm included; anchoring is not legitimacy.")
    return led.events


# ---------------------------------------------------------------------------
# Standalone run — narrate, fold the matrix at both cuts, show the movement.
# ---------------------------------------------------------------------------

def main() -> None:
    events = generate_log()

    for label, asof in CUTS:
        print(f"\n--- the matrix at '{label}' ({asof}) — three observers, one log ---")
        for proj in matrix(events, asof):
            print(f"\n  {proj['observer']}  root={NAMES[proj['root']]}  "
                  f"policy={proj['policy']}  honors={NAMES[proj['honors']]}")
            for s, c in proj["cells"].items():
                chips = "".join(f" [{r['label']} by {NAMES[proj['honors']]}]"
                                for r in c["rulings"])
                chips += f" [{len(c['open_disputes'])} open dispute]" if c["open_disputes"] else ""
                hinge = f"  (hinges on one tie: {c['hinge']})" if c["hinge"] else ""
                print(f"    {NAMES[s]:<10} {c['verdict']:<18}{chips}{hinge}")
                print(f"      {c['detail']}")

    print("\n--- what moved between the cuts ---")
    for ch in changed_cells(events):
        print(f"    {ch['observer']:<11} on {NAMES[ch['subject']]:<10} "
              f"{ch['before']}  ->  {ch['after']}")

    print("\n--- the omniscient view — available to NO observer ---")
    for t in GROUND_TRUTH:
        print(f"    * {t}")
    print("""
The finding: no policy reads all four newcomers 'right', and 'right' is not in
the log. The canon's three exits from cold start — earn edges, manufacture
volume, borrow a tie — produce appearances the log cannot tell apart. ARC's
job here is to render that uncertainty, not to resolve it.""")


if __name__ == "__main__":
    main()
