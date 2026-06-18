#!/usr/bin/env python3
"""
ARC cache-discipline probe — single file, stdlib only.

What this isolates
------------------
ARC's headline claim (README, object-model.md §6) is that *not storing the
relationship* is the **structural** defense against becoming a social-credit
database — standing is a Projection, recomputed on demand, never a stored record.
But object-model.md §8 and canon-fold-demo's finding B already concede the soft
spot: a *cached* projection "can re-introduce a profile-shaped artifact," and call
that a **discipline question, not a primitive.** Nothing executable pins it down.

This probe pins it down. It folds one log into a `standing` projection, then reads
it back through three cache shapes and asks: does the Event/Projection split, on
its own, actually prevent the social-credit artifact — or only the discipline?

    ephemeral     — scoped to one computation, discarded; never outlives a fold.
    event-bound   — keyed by the event-set hash; a log change misses and refolds.
    convenience   — keyed by agent (+ a TTL), NOT by the events; persists blindly.

Three failures of the convenience cache, each printed:
  1. revocation survival — a governance suspension lands; the cache keeps serving
     the pre-suspension "good standing." A stored status that outlives its
     evidence IS the social-credit shape.
  2. context leakage   — a standing computed in one context is served for another,
     collapsing into the universal score ARC forbids.
  3. indistinguishable stale vs fresh — the stale cached value is *value-identical*
     to a fresh fold's earlier result, carrying no marker of its own staleness. A
     reader cannot tell a poisoned cache from a correct one without recomputing —
     which is the work the cache existed to skip.

The finding is the same shape as canon-fold-demo's finding B, made executable and
sharpened: the anti-social-credit property is **contingent on cache shape, not
structural**, and the safe shape and the useful shape pull against each other.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no real storage;
  * signatures are MOCK (a hash) — the finding is about the FOLD and its caches,
    not custody;
  * the five canonical types are reused as-is — no new primitive, no stored
    standing object;
  * this is a probe, not a caching spec and not doctrine.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


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
    nullifies: tuple[str, ...] = ()
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
# The projection: standing for (agent, context), folded on demand. NEVER stored.
# ---------------------------------------------------------------------------

def project_standing(events: list[Event], agent: str, context: str) -> dict:
    """Fold the log into a contextual standing. Recomputed every call; the result
    is a value, not a record. Governance moves it only via ADJUDICATE (finding E)."""
    outcomes = [e for e in events
                if e.type == "ATTEST" and e.predicate == "rep.outcome"
                and e.payload.get("subject") == agent
                and e.payload.get("context") == context]
    positives = sum(1 for e in outcomes if e.payload.get("result") == "positive")

    # a suspension applies to the queried context (or agent-wide if it names none)
    suspended = any(e for e in events
                    if e.type == "ADJUDICATE" and e.predicate == "gov.suspension"
                    and e.payload.get("subject") == agent
                    and e.payload.get("context") in (None, context))

    if suspended:
        standing = "suspended"
    elif positives >= 2:
        standing = "good"
    elif positives == 1:
        standing = "emerging"
    else:
        standing = "unproven"

    return {"agent": agent, "context": context, "standing": standing,
            "positive_outcomes": positives, "basis": sorted(e.id for e in outcomes)}


def log_hash(events: list[Event]) -> str:
    """Event-set hash (object-model finding B's `event_set_hash`): any change to the
    log changes it. Hashing every id is conservative — and that conservatism is the
    tell that an event-bound read is really a memoized recompute."""
    return hashlib.sha256("".join(sorted(e.id for e in events)).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Three cache shapes. Each answers the same question; only the KEY differs, and
# the key is the whole story.
# ---------------------------------------------------------------------------

Compute = Callable[[], dict]


class EphemeralCache:
    """Scoped to one computation; stores nothing across calls. Safe by structure —
    it can never outlive the fold, so it can never become a stored profile. (Safe,
    yes — but it also buys nothing across reads: it is just 'recompute'.)"""
    name = "ephemeral"

    def read(self, events, agent, context, compute: Compute):
        return compute(), "always fresh (nothing persists)"


class EventBoundCache:
    """Keyed by (agent, context, event-set hash). A log change misses and refolds.
    This NARROWS the staleness window — it does not close it, and it is not 'safe'
    in the absolute. Its correctness rests on three disciplines the canon does not
    enforce: the hash must cover every event the fold reads; it must be checked on
    EVERY read; and context must be in the key. Drop any one and it degrades toward
    the convenience cache. At its most correct (full re-hash every read) it is
    indistinguishable from memoized recompute."""
    name = "event-bound"

    def __init__(self):
        self.store: dict = {}

    def read(self, events, agent, context, compute: Compute):
        key = (agent, context, log_hash(events))
        if key in self.store:
            return self.store[key], "HIT (event-set hash matched)"
        val = compute()
        self.store[key] = val
        return val, "MISS -> refold (log changed)"


class ConvenienceCache:
    """Keyed by agent only, with an implicit 'it was fresh recently' TTL. It does
    NOT bind to the events or the context. This is the shape that quietly becomes a
    stored profile."""
    name = "convenience"

    def __init__(self):
        self.store: dict = {}

    def read(self, events, agent, context, compute: Compute):
        key = (agent,)                       # no context, no event binding
        if key in self.store:
            return self.store[key], "HIT (stale-blind: never re-checked the log)"
        val = compute()
        self.store[key] = val
        return val, "MISS -> computed once, then served forever"


# ---------------------------------------------------------------------------
# Ledger / parties — minimal.
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
        hour = 10 if self._clock <= 8 else 16   # the suspension lands in the afternoon
        return f"2026-06-10T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def line(label: str, val: dict, note: str) -> None:
    print(f"    {label:<26} standing={val['standing']:<9} "
          f"(ctx={val['context']}, +{val['positive_outcomes']})  [{note}]")


# ---------------------------------------------------------------------------
# The flow.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    agent = Party(led, "agent", "k:agent")          # the SUBJECT whose standing we fold
    c1 = Party(led, "buyer-1", "k:c1")
    c2 = Party(led, "buyer-2", "k:c2")
    c3 = Party(led, "buyer-3", "k:c3")
    community = Party(led, "community", "k:community")
    A, B = "groceries", "electronics"

    print("\n1. Identity — subject agent, three counterparties, a community (KEY register)")
    for p in (agent, c1, c2, c3, community):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print(f"\n2. Evidence in context '{A}' — three good outcomes attested about the agent")
    for c in (c1, c2, c3):
        c.emit("ATTEST", "rep.outcome",
               payload={"subject": "k:agent", "context": A, "result": "positive"})

    eph, evb, conv = EphemeralCache(), EventBoundCache(), ConvenienceCache()

    print(f"\n3. T1 — fold standing(agent, {A}) and seed all three caches")
    fresh_t1 = project_standing(led.events, "k:agent", A)
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", A, lambda: project_standing(led.events, "k:agent", A))
        line(f"{cache.name} read", val, note)
    say("note", f"true standing now = '{fresh_t1['standing']}' — all caches agree, all correct")

    print("\n4. T2 — a dispute is adjudicated; the community SUSPENDS the agent")
    ch = c1.emit("CHALLENGE", "dispute.open", refs=("k:agent",),
                 payload={"subject": "k:agent", "reason": "non_delivery_claim"})
    community.emit("ADJUDICATE", "gov.suspension", refs=(ch.id,),
                   payload={"subject": "k:agent", "context": A, "resolves": ch.id})
    fresh_now = project_standing(led.events, "k:agent", A)
    say("truth", f"a fresh fold now returns standing='{fresh_now['standing']}'")

    print(f"\n   --- (1) REVOCATION SURVIVAL: re-read standing(agent, {A}) after the suspension ---")
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", A, lambda: project_standing(led.events, "k:agent", A))
        verdict = "STALE — still serving the suspended agent as good" if val["standing"] != fresh_now["standing"] else "correct"
        line(f"{cache.name} read", val, f"{note} => {verdict}")

    print(f"\n   --- (2) CONTEXT LEAKAGE: ask standing(agent, {B}) — agent has ZERO {B} outcomes ---")
    fresh_B = project_standing(led.events, "k:agent", B)
    say("truth", f"a fresh fold for '{B}' returns standing='{fresh_B['standing']}' (no evidence there)")
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", B, lambda: project_standing(led.events, "k:agent", B))
        leaked = (val["context"] != B) or (val["standing"] != fresh_B["standing"])
        verdict = f"LEAKED — served '{val['context']}' standing for '{B}' = a universal score" if leaked else "correct"
        line(f"{cache.name} read", val, f"{note} => {verdict}")

    print("\n   --- (3) STALE IS INDISTINGUISHABLE FROM FRESH ---")
    stale = conv.store[("k:agent",)]
    print(f"    convenience cached value : {compact(stale)}")
    print(f"    fresh fold @ T1          : {compact(fresh_t1)}")
    print(f"    fresh fold NOW           : {compact(fresh_now)}")
    print(f"    cached == fresh@T1 ? {stale == fresh_t1}   (byte-identical; no staleness marker)")
    print(f"    cached == fresh NOW ? {stale == fresh_now}   (the cache silently contradicts the log)")
    print("    A reader holding only the cached value cannot tell it is stale without")
    print("    recomputing — which is the work the cache existed to skip.")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes.")
    verify_log(led.events)
    print_finding()


def compact(d: dict) -> str:
    return f"{{standing={d['standing']}, ctx={d['context']}, +{d['positive_outcomes']}}}"


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Is "not storing the relationship" a STRUCTURAL anti-social-credit defense?
      Not on its own. The Event/Projection split prevents a stored profile only
      while caches are disciplined. The defense is CONTINGENT ON CACHE SHAPE — a
      sharpening of canon-fold-demo's finding B, here made executable.
  * What does each shape actually buy?
      - ephemeral  — safe by structure (never outlives a fold), but buys nothing
        across reads: it is just recompute.
      - event-bound — narrows the staleness window; NOT "absolutely safe." Its
        correctness rests on three disciplines the canon does not enforce (the
        hash covers every event read / it is checked on every read / context is in
        the key). At its most correct it is memoized recompute; relax any
        discipline and it slides toward the convenience failure.
      - convenience — keyed by the party, not the events: it becomes a stored
        profile, and reproduces all three failures below.
  * The three failures of an undisciplined cache:
      1. revocation survival — a suspended agent is still served as "good"; a
         stored status outliving its evidence IS the social-credit shape.
      2. context leakage — one context's standing is served for another, collapsing
         into the universal score ARC explicitly refuses.
      3. indistinguishable stale vs fresh — the stale value is byte-identical to an
         earlier fresh fold and carries no marker of its own staleness. You cannot
         detect the poisoning without recomputing.
  * The deeper tension (finding-H shaped, on the projection layer):
      The only safe rule is "never authoritative, always recompute" — which negates
      the cache's reason to exist at the trust boundary. The safe cache and the
      useful cache pull against each other. The canon does not resolve this; it
      relocates it to caching discipline, the same move as B/C/D/G and the trust
      trilemma — relocation, not dissolution.

No sixth type was added, and no stored standing object: the social-credit artifact
is reachable with NO new primitive, purely by undisciplined caching. This is a
probe and a sharpening of finding B, not a caching spec and not doctrine.
""")


if __name__ == "__main__":
    run()
