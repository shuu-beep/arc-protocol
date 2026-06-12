#!/usr/bin/env python3
"""
ARC federation fixture — what it means to partially trust another community.

What this is
------------
The cold-start fixture showed legitimacy as a relation between an observer's
fold policy and the log. This fixture takes the next step the repo has so far
deferred: ONE log, TWO community authorities, and observers who must decide
what another community's adjudication is worth. The first executable slice of
federation — deliberately small.

The claim under test:

    a bridge between communities needs no new primitive. Recognition is a
    scoped AUTHORIZE; severance is `nullifies`; whether an imported ruling
    binds, advises, or weighs nothing is the observer's fold reading; and
    where two honored authorities conflict with no precedence rule, the
    honest projection is the disagreement itself — CONTESTED, not a verdict.

The scenario (15 events, none hand-written):

    vendor trades in two communities. A cross-community sale lands in a
    dispute in harbor's market; community-harbor rules SUSPENSION (its strict
    rule: late delivery is non-fulfillment). The vendor appeals at home;
    community-orchard rules DISMISSAL (its rule: delivered late is still
    delivered). Before any of this, orchard had recognized harbor's commerce
    rulings — an AUTHORIZE `fed.recognition`, the bridge. After the conflict,
    orchard severs it (`fed.severance` + `nullifies`).

Five observers fold the SAME log at three moments:

    obs-harbor             honors harbor only. Would follow a bridge — harbor
                           never issued one. Bridges are directional.
    obs-orchard-closed     honors orchard only; bridge read as nothing —
                           imported rulings weigh 0 (the stray-key treatment).
    obs-orchard-advisory   bridge read as ADVISORY — imported rulings are
                           visible flags that move no standing.
    obs-orchard-authority  bridge read as AUTHORITY, with a precedence rule:
                           on conflict, the local ruling supersedes.
    obs-orchard-flat       bridge read as AUTHORITY, NO precedence rule —
                           when honored authorities conflict, both stay live.

Three moments: after harbor's ruling / after orchard's contrary ruling /
after the severance. The severance is read two ways (the finding-G divergence
arriving on the federation side):

    time_scoped   rulings imported while the bridge was live STAY imported;
                  severance bounds only future imports
    cascade       a severed bridge is read as if it never was — every ruling
                  it carried drops out of the past as well

What this fixture refuses to do (deliberately):
  * no trust scalar — a bridge reading is categorical (authority / advisory /
    ignore), never a 0.7. A numeric community-trust weight would be the
    composite score ARC refuses, one level up;
  * no super-adjudicator and no protocol-level conflict resolution — ARC has
    no authority of last resort, so CONTESTED is an honest terminal output,
    not an error state;
  * no new event type and no federation primitive. The bridge is an AUTHORIZE
    with predicate `fed.recognition` and a `scope`; the severance is an
    AUTHORIZE with `nullifies`. If this had not sufficed, THAT would have
    been the finding;
  * signing is the mock hash scheme of the other fixtures — custody is not
    the question here, and real signatures would prove nothing about it.

Known unknown, stated up front: WHY orchard recognized harbor — the adoption
and incentive question — is not in the log and no fold below can read it. The
probe shows what a bridge IS; what makes one worth issuing stays the open
problem it has been (threat-model §18.1). A fixture and a probe, not doctrine.

Run:  python3 federation_fixture.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

NAMES = {
    "k:harbor": "community-harbor",
    "k:orchard": "community-orchard",
    "k:vendor": "vendor",
    "k:buyerH": "buyer-harbor",
    "k:buyerO": "buyer-orchard",
}

SUBJECT = "k:vendor"

VERDICT_LABEL = {"gov.suspension": "suspended", "gov.dismissal": "cleared"}

# Each observer = a root + which adjudicators it honors directly + how it reads
# a bridge issued by an authority it honors + what happens on conflict. All of
# these are fold parameters; none of them is an event.
OBSERVERS = (
    {"name": "obs-harbor", "root": "k:harbor", "honors": ("k:harbor",),
     "bridge_reading": "authority", "precedence": None,
     "blurb": "honors harbor only; would follow a bridge, but harbor issued "
              "none — bridges are directional"},
    {"name": "obs-orchard-closed", "root": "k:orchard", "honors": ("k:orchard",),
     "bridge_reading": "ignore", "precedence": None,
     "blurb": "honors orchard only; reads the bridge as nothing — an imported "
              "ruling weighs 0, like a stray key"},
    {"name": "obs-orchard-advisory", "root": "k:orchard", "honors": ("k:orchard",),
     "bridge_reading": "advisory", "precedence": None,
     "blurb": "follows orchard's bridge as ADVISORY — imported rulings are "
              "visible and weightless"},
    {"name": "obs-orchard-authority", "root": "k:orchard", "honors": ("k:orchard",),
     "bridge_reading": "authority", "precedence": "local_supersedes",
     "blurb": "follows the bridge as AUTHORITY; on conflict, the local ruling "
              "supersedes the import"},
    {"name": "obs-orchard-flat", "root": "k:orchard", "honors": ("k:orchard",),
     "bridge_reading": "authority", "precedence": None,
     "blurb": "follows the bridge as AUTHORITY with no precedence rule — "
              "conflicting honored rulings both stay live"},
)

MOMENTS = (
    ("after harbor's ruling", "2026-06-13T14:00:00Z"),
    ("after orchard's contrary ruling", "2026-06-13T16:00:00Z"),
    ("after the bridge is severed", "2026-06-13T18:00:00Z"),
)

READINGS = ("time_scoped", "cascade")

# What only the generator knows. No fold below receives any of it.
GROUND_TRUTH = (
    "the goods were delivered, two days late; the courier's note never entered "
    "the log. harbor's strict market rule reads late as non-fulfillment; "
    "orchard's rule accepts late delivery. Both rulings are sincere "
    "applications of each community's own rule to the same facts.",
    "no fold below keys on the delivery fact — every fold keys on which "
    "authority it honors. An observer can knowingly import a ruling that is "
    "procedurally legitimate and factually wrong; the log cannot tell it which.",
    "why orchard recognized harbor in the first place is not recorded and is "
    "not representable as a fold input — the adoption question, unchanged.",
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
    Both communities' rulings verify identically — the log holds no fact that
    ranks one authority above the other."""
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
# The fold: log -> one observer's reading of the vendor's standing, at one
# moment, under one severance reading. Boundary logic lives here; the viewer
# renders the output and adds nothing.
# ---------------------------------------------------------------------------

def _bridges(events: list[Event], observer: dict, asof: str, drop: tuple = ()) -> list[dict]:
    """Recognition grants issued by an authority THIS observer honors, with
    their severance (if any). A bridge issued by an authority the observer
    does not honor is invisible here — a bridge routes authority the observer
    already grants; it cannot mint any."""
    out = []
    for e in events:
        if (e.type == "AUTHORIZE" and e.predicate == "fed.recognition"
                and e.signer in observer["honors"] and e.timestamp <= asof
                and e.refs and e.id not in drop):
            sev = next((s for s in events
                        if e.id in s.nullifies and s.timestamp <= asof), None)
            out.append({"event": e, "recognized": e.refs[0],
                        "domain": (e.scope or {}).get("domain"),
                        "severed_at": sev.timestamp if sev else None})
    return out


def _import_live(bridge: dict, ruling: Event, reading: str) -> bool:
    """Was this ruling carried by this bridge, under this severance reading?
        time_scoped  imported iff the ruling landed while the bridge was live;
                     severance bounds FUTURE imports only
        cascade      a severed bridge is read as if it never was — everything
                     it carried drops out of the past as well"""
    if bridge["event"].timestamp > ruling.timestamp:
        return False                      # a bridge cannot carry an earlier ruling
    if bridge["severed_at"] is None:
        return True
    if reading == "time_scoped":
        return ruling.timestamp < bridge["severed_at"]
    return False                          # cascade: severed = never


def project_federation(events: list[Event], observer: dict, asof: str,
                       reading: str = "time_scoped", _drop: tuple = ()) -> dict:
    """One observer's reading of the vendor's standing at one moment.

    Every ADJUDICATE about the subject is classified for THIS observer:
        local      signed by an authority the observer honors directly
        imported   carried by a live honored bridge, read as AUTHORITY
        advisory   carried by a live honored bridge, read as ADVISORY —
                   visible, weightless on standing
        foreign    no honored path — weight 0, rendered but never folded

    Standing is then resolved from the binding (local + imported) verdicts.
    Where they conflict: a precedence rule (a fold parameter, not an event)
    may pick one; with no precedence rule the output is CONTESTED — both
    rulings live, the disagreement itself. Nothing is stored; recomputed from
    the log on demand."""
    assert reading in READINGS, f"unknown reading {reading!r}"
    bridges = _bridges(events, observer, asof, drop=_drop)
    rulings = [e for e in events if e.type == "ADJUDICATE"
               and SUBJECT in e.refs and e.timestamp <= asof]

    verdicts = []
    for r in rulings:
        label = VERDICT_LABEL.get(r.predicate, r.predicate)
        if r.signer in observer["honors"]:
            verdicts.append({"label": label, "by": r.signer, "status": "local",
                             "id": r.id, "via": None})
            continue
        br = next((b for b in bridges if b["recognized"] == r.signer
                   and b["domain"] == r.payload.get("context")
                   and _import_live(b, r, reading)), None)
        if br is None or observer["bridge_reading"] == "ignore":
            via = br["event"].id if br else None
            verdicts.append({"label": label, "by": r.signer, "status": "foreign",
                             "id": r.id, "via": via})
        elif observer["bridge_reading"] == "authority":
            verdicts.append({"label": label, "by": r.signer, "status": "imported",
                             "id": r.id, "via": br["event"].id})
        else:  # advisory
            verdicts.append({"label": label, "by": r.signer, "status": "advisory",
                             "id": r.id, "via": br["event"].id})

    binding = [v for v in verdicts if v["status"] in ("local", "imported")]
    labels = sorted({v["label"] for v in binding})
    if not binding:
        standing, category = "in good standing", "good"
        if any(v["status"] == "advisory" for v in verdicts):
            detail = "no binding ruling — standing rests on history alone"
        elif any(v["status"] == "foreign" for v in verdicts):
            detail = ("a ruling exists but no honored bridge carries it — "
                      "weight 0, exactly the stray-key treatment")
        else:
            detail = "no honored ruling touches the vendor — history only"
    elif len(labels) == 1:
        standing = labels[0]
        category = "warn" if standing == "suspended" else "affirm"
        v = binding[-1]
        if v["status"] == "local":
            detail = f"ruled by {NAMES[v['by']]}, an authority this fold honors directly"
        else:
            detail = (f"ruled by {NAMES[v['by']]} and imported as BINDING through "
                      "the live bridge — the standing rests on the bridge")
    else:
        local = [v for v in binding if v["status"] == "local"]
        if observer["precedence"] == "local_supersedes" and local:
            standing = local[-1]["label"]
            category = "warn" if standing == "suspended" else "affirm"
            for v in binding:
                if v["status"] == "imported":
                    v["status"] = "overridden"
            detail = ("two honored rulings conflict; the LOCAL one supersedes — "
                      "override is a precedence choice in this fold, not an "
                      "event on the log")
        else:
            standing, category = "CONTESTED", "contested"
            detail = ("two honored authorities ruled in opposite directions and "
                      "this fold has no precedence rule — both rulings stay "
                      "live; the honest projection is the set, not a pick")

    advisory = [v for v in verdicts if v["status"] == "advisory"]
    if advisory:
        detail += ("; an imported ruling is visible as ADVISORY and moves "
                   "no standing")

    # the hinge: if removing one bridge event flips the standing, the whole
    # judgment hangs on that single grant (the cold-start hinge, federated)
    hinge = None
    if not _drop:
        for bid in sorted({v["via"] for v in verdicts if v["via"]}):
            alt = project_federation(events, observer, asof, reading, _drop=(bid,))
            if alt["cell"]["standing"] != standing:
                hinge = bid
                break

    basis = [v["id"] for v in verdicts] + sorted({v["via"] for v in verdicts if v["via"]})
    return {"observer": observer["name"], "root": observer["root"],
            "honors": observer["honors"], "bridge_reading": observer["bridge_reading"],
            "precedence": observer["precedence"], "blurb": observer["blurb"],
            "asof": asof, "reading": reading,
            "cell": {"standing": standing, "category": category, "labels": labels,
                     "verdicts": verdicts, "detail": detail, "hinge": hinge,
                     "basis": basis}}


def matrix(events: list[Event], asof: str, reading: str = "time_scoped") -> list[dict]:
    """All observers' readings at one moment — the disagreement, computed."""
    return [project_federation(events, o, asof, reading) for o in OBSERVERS]


def _cell_signature(cell: dict) -> str:
    sig = cell["standing"]
    if cell["standing"] == "CONTESTED":
        sig += " (" + " / ".join(cell["labels"]) + ")"
    adv = [v["label"] for v in cell["verdicts"] if v["status"] == "advisory"]
    if adv:
        sig += " · advisory: " + ", ".join(adv)
    return sig


def moved_cells(events: list[Event], reading: str = "time_scoped") -> list[dict]:
    """Standings that moved between consecutive moments, under one reading.
    The asymmetry to notice: under time_scoped the severance moves NOTHING —
    it only bounds future imports; under cascade it rewrites the past."""
    out = []
    prev = None
    for label, asof in MOMENTS:
        cur = {p["observer"]: _cell_signature(p["cell"])
               for p in matrix(events, asof, reading)}
        if prev is not None:
            for obs, sig in cur.items():
                if prev[1][obs] != sig:
                    out.append({"observer": obs, "from_moment": prev[0],
                                "to_moment": label, "before": prev[1][obs],
                                "after": sig})
        prev = (label, cur)
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
        # Morning: the standing world + the bridge (events 1..9, before any
        # dispute). Midday: the cross-community sale, the dispute, harbor's
        # ruling (10..12, before moment 1 at 14:00). Afternoon: the appeal and
        # orchard's contrary ruling (13..14, before moment 2 at 16:00).
        # Evening: the severance (15, before moment 3 at 18:00).
        c = self._clock
        hour = 9 if c <= 9 else (13 if c <= 12 else (15 if c <= 14 else 17))
        return f"2026-06-13T{hour:02d}:{c:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The generated flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def generate_log() -> list[Event]:
    led = Ledger()
    harbor = Party(led, "community-harbor", "k:harbor")
    orchard = Party(led, "community-orchard", "k:orchard")
    vendor = Party(led, "vendor", "k:vendor")
    buyer_h = Party(led, "buyer-harbor", "k:buyerH")
    buyer_o = Party(led, "buyer-orchard", "k:buyerO")

    print("\n1. Two communities, one vendor with history in both")
    for p in (harbor, orchard, vendor, buyer_h, buyer_o):
        p.emit("KEY", "id.key_register", payload={"key": p.key})
    for n in (1, 2):
        buyer_h.emit("ATTEST", "rep.outcome", refs=("k:vendor",),
                     payload={"result": "positive", "context": "commerce", "trade": n})
    buyer_o.emit("ATTEST", "rep.outcome", refs=("k:vendor",),
                 payload={"result": "positive", "context": "commerce", "trade": 1})

    print("\n2. The bridge — orchard recognizes harbor's commerce rulings")
    say("community-orchard", "recognition is a scoped AUTHORIZE; nothing new")
    bridge = orchard.emit("AUTHORIZE", "fed.recognition", refs=("k:harbor",),
                          scope={"domain": "commerce"},
                          payload={"note": "harbor's commerce rulings are "
                                           "recognized in this community"})

    print("\n3. A cross-community sale lands in a dispute in harbor's market")
    buyer_o.emit("ATTEST", "commerce.payment_result", refs=("k:vendor",),
                 payload={"result": "confirmed", "amount_krw": 30000,
                          "context": "commerce"})
    dispute = buyer_o.emit("CHALLENGE", "dispute.open", refs=("k:vendor",),
                           payload={"reason": "paid_but_not_delivered",
                                    "context": "commerce"})
    say("community-harbor", "strict market rule: late delivery is non-fulfillment")
    harbor.emit("ADJUDICATE", "gov.suspension", refs=("k:vendor", dispute.id),
                payload={"resolves": dispute.id, "context": "commerce",
                         "finding": "non-fulfillment under harbor market rules"})

    print("\n--- moment 1 (14:00): after harbor's ruling ---")

    print("\n4. The vendor appeals at home; orchard rules the OTHER way")
    appeal = vendor.emit("CHALLENGE", "dispute.appeal", refs=("k:vendor",),
                         payload={"reason": "delivered_late_but_delivered",
                                  "context": "commerce"})
    say("community-orchard", "orchard's rule: delivered late is still delivered")
    orchard.emit("ADJUDICATE", "gov.dismissal", refs=("k:vendor", appeal.id),
                 payload={"resolves": appeal.id, "context": "commerce",
                          "finding": "delivery confirmed; lateness is not "
                                     "non-fulfillment here"})

    print("\n--- moment 2 (16:00): after orchard's contrary ruling ---")

    print("\n5. The severance — orchard withdraws its recognition of harbor")
    say("community-orchard", "the conflict exposed incompatible market rules")
    orchard.emit("AUTHORIZE", "fed.severance", nullifies=(bridge.id,),
                 payload={"reason": "incompatible_rulings_on_shared_commerce"})

    print("\n--- moment 3 (18:00): after the bridge is severed ---")

    verify_log(led.events)
    print(f"\nGenerated log: {len(led.events)} signed events, none hand-written. "
          "verify_log passes — both communities' rulings verify identically.")
    return led.events


# ---------------------------------------------------------------------------
# Standalone run — narrate, fold the matrix at each moment, show the movement.
# ---------------------------------------------------------------------------

def _print_matrix(events: list[Event], label: str, asof: str, reading: str) -> None:
    print(f"\n--- '{label}' ({asof}) · severance reading: {reading} ---")
    for p in matrix(events, asof, reading):
        cell = p["cell"]
        hinge = f"  (hinges on the bridge: {cell['hinge']})" if cell["hinge"] else ""
        print(f"  {p['observer']:<22} {_cell_signature(cell):<32}{hinge}")
        print(f"      {cell['detail']}")
        for v in cell["verdicts"]:
            via = f" via {v['via']}" if v["via"] else ""
            print(f"      · {v['label']} by {NAMES[v['by']]} [{v['id']}] — "
                  f"{v['status']}{via}")


def main() -> None:
    events = generate_log()

    for label, asof in MOMENTS:
        _print_matrix(events, label, asof, "time_scoped")
    print("\n--- moment 3 again, under the CASCADE severance reading ---")
    _print_matrix(events, MOMENTS[2][0], MOMENTS[2][1], "cascade")

    for reading in READINGS:
        moves = moved_cells(events, reading)
        print(f"\n--- what moved between the moments ({reading}) ---")
        if not moves:
            print("    nothing")
        for m in moves:
            print(f"    {m['observer']:<22} {m['from_moment']} -> {m['to_moment']}: "
                  f"{m['before']}  ->  {m['after']}")
        if reading == "time_scoped" and not any(
                m["to_moment"] == MOMENTS[2][0] for m in moves):
            print("    (note: the severance moved NOTHING under time_scoped — "
                  "it bounds future imports; it does not sort the past)")

    print("\n--- the omniscient view — available to NO observer ---")
    for t in GROUND_TRUTH:
        print(f"    * {t}")

    print("""
The findings, offered as probe results, not doctrine:
  * the bridge needed nothing new: recognition is a scoped AUTHORIZE,
    severance is `nullifies`, and preserve-vs-cascade arrived for free — with
    the same divergence as every revocation before it. Severing a bridge
    bounds FUTURE imports; it does not sort the past. Time-scoped keeps the
    contested cell after the severance; cascade clears it only by voiding the
    bridge's whole history — resolution by amnesia, not resolution.
  * imported status is not a property of the ruling. The same ADJUDICATE is
    binding to one fold, advisory to a second, weightless to a third. The
    three-layer split again: the ruling is a log fact; importing it is a fold
    choice; only what to do about it is an authority's decision.
  * override is not an event — it is a precedence choice inside a fold. And
    where a fold honors two authorities with no precedence rule, CONTESTED is
    the honest terminal output: the only thing that would dissolve it is an
    authority of last resort, the corner ARC declines.
  * a bridge is directional and cannot mint trust. Orchard's recognition of
    harbor moves nothing for an observer who does not already honor orchard —
    a bridge routes authority the observer already grants; it creates none.
  * why orchard recognized harbor is not in the log and cannot fold — the
    adoption boundary, exactly where the methodology limit said it would be.""")


if __name__ == "__main__":
    main()
