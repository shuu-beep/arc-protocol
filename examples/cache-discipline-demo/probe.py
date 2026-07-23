#!/usr/bin/env python3
"""
ARC cache-discipline probe — single file, stdlib only.

What this isolates
------------------
This fixture folds one authored log into a contextual `standing` Projection and
reads it through three cache shapes. It compares whether each shape matches a
fresh call to the same fixture fold after the Event list or context changes.

    ephemeral     — scoped to one computation and discarded.
    event-bound   — keyed by agent, context, and the fixture Event-id hash.
    convenience   — keyed by agent, not by the Event list or context.

Three readings of the convenience cache are printed: reuse after an adjudication
record is appended, reuse across contexts, and a cached value with no freshness
metadata. The comparator is a fresh call to this fixture's fold under its declared
inputs and policy; it is not a claim about world truth or general cache safety.

Scope:
  * stdlib only, single process, no network, no transport, no real storage;
  * signatures are MOCK (a hash) — the finding is about the FOLD and its caches,
    not custody;
  * the five canonical types are reused as-is — no new primitive, no stored
    standing object in the Event log;
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
    """MOCK. This fixture uses a deterministic hash for reproducible replay, not production security; ARC has no selected normative signature suite, so implementations and named profiles select and declare their suite."""
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
            raise ValueError(f"bad mock signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# The fixture Projection: standing for (agent, context), computed on demand.
# ---------------------------------------------------------------------------

def project_standing(events: list[Event], agent: str, context: str) -> dict:
    """Fold the supplied list into the fixture's contextual standing value.

    This function changes its suspension reading only for the ADJUDICATE shape
    checked below. That is authored fixture policy, not a general verifier.
    """
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
    """Fixture cache-key component computed from the sorted Event ids."""
    return hashlib.sha256("".join(sorted(e.id for e in events)).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Three authored cache shapes used for the comparison below.
# ---------------------------------------------------------------------------

Compute = Callable[[], dict]


class EphemeralCache:
    """Scoped to one computation; stores nothing across calls.

    It avoids cross-read reuse in this fixture but buys nothing across reads.
    """
    name = "ephemeral"

    def read(self, events, agent, context, compute: Compute):
        return compute(), "computed on this read"


class EventBoundCache:
    """Keyed by (agent, context, fixture Event-id hash).

    In this generated run, appending the fixture records produces a different
    key and a miss. This does not establish completeness, integrity, version
    identity, or general cache correctness.
    """
    name = "event-bound"

    def __init__(self):
        self.store: dict = {}

    def read(self, events, agent, context, compute: Compute):
        key = (agent, context, log_hash(events))
        if key in self.store:
            return self.store[key], "HIT (event-set hash matched)"
        val = compute()
        self.store[key] = val
        return val, "MISS -> compute for current key"


class ConvenienceCache:
    """Keyed by agent only; it does not bind to the Event list or context."""
    name = "convenience"

    def __init__(self):
        self.store: dict = {}

    def read(self, events, agent, context, compute: Compute):
        key = (agent,)                       # no context, no event binding
        if key in self.store:
            return self.store[key], "HIT (agent-only key; inputs not checked)"
        val = compute()
        self.store[key] = val
        return val, "MISS -> stored under agent-only key"


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

    print(f"\n2. Three positive outcome claims in context '{A}'")
    for c in (c1, c2, c3):
        c.emit("ATTEST", "rep.outcome",
               payload={"subject": "k:agent", "context": A, "result": "positive"})

    eph, evb, conv = EphemeralCache(), EventBoundCache(), ConvenienceCache()

    print(f"\n3. T1 — fold standing(agent, {A}) and seed all three caches")
    fresh_t1 = project_standing(led.events, "k:agent", A)
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", A, lambda: project_standing(led.events, "k:agent", A))
        line(f"{cache.name} read", val, note)
    say("fresh-fold", f"standing='{fresh_t1['standing']}' — all three shapes match this fold")

    print("\n4. T2 — append a CHALLENGE and an ADJUDICATE gov.suspension")
    ch = c1.emit("CHALLENGE", "dispute.open", refs=("k:agent",),
                 payload={"subject": "k:agent", "reason": "non_delivery_claim"})
    community.emit("ADJUDICATE", "gov.suspension", refs=(ch.id,),
                   payload={"subject": "k:agent", "context": A, "resolves": ch.id})
    fresh_now = project_standing(led.events, "k:agent", A)
    say("fresh-fold", f"current fixture fold returns standing='{fresh_now['standing']}'")

    print(f"\n   --- (1) STALE AFTER NEW RECORDS: re-read standing(agent, {A}) ---")
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", A, lambda: project_standing(led.events, "k:agent", A))
        verdict = "STALE — differs from the fresh fixture fold" if val["standing"] != fresh_now["standing"] else "matches fresh fold"
        line(f"{cache.name} read", val, f"{note} => {verdict}")

    print(f"\n   --- (2) CONTEXT LEAKAGE: ask standing(agent, {B}) — agent has ZERO {B} outcomes ---")
    fresh_B = project_standing(led.events, "k:agent", B)
    say("fresh-fold", f"for '{B}' returns standing='{fresh_B['standing']}' (no fixture outcomes there)")
    for cache in (eph, evb, conv):
        val, note = cache.read(led.events, "k:agent", B, lambda: project_standing(led.events, "k:agent", B))
        leaked = (val["context"] != B) or (val["standing"] != fresh_B["standing"])
        verdict = f"CROSS-CONTEXT — served '{val['context']}' result for '{B}'" if leaked else "matches fresh fold"
        line(f"{cache.name} read", val, f"{note} => {verdict}")

    print("\n   --- (3) CACHED VALUE HAS NO FRESHNESS METADATA ---")
    stale = conv.store[("k:agent",)]
    print(f"    convenience cached value : {compact(stale)}")
    print(f"    fresh fold @ T1          : {compact(fresh_t1)}")
    print(f"    fresh fold NOW           : {compact(fresh_now)}")
    print(f"    cached == fresh@T1 ? {stale == fresh_t1}   (byte-identical; no staleness marker)")
    print(f"    cached == fresh NOW ? {stale == fresh_now}   (differs from the current fixture fold)")
    print("    The cached value alone carries no input hash or freshness marker.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events; running replay checks.")
    verify_log(led.events)
    print_finding()


def compact(d: dict) -> str:
    return f"{{standing={d['standing']}, ctx={d['context']}, +{d['positive_outcomes']}}}"


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * The ephemeral shape computes on each read and avoids cross-read reuse.
  * Under this authored Event list, the event-bound shape misses after the
    Event-id list changes and separates the two queried contexts.
  * The agent-only convenience shape reuses the earlier value after new records
    and across contexts. Its stored value contains no freshness metadata.
  * These results do not establish that either of the other shapes is generally
    correct or safe. Reuse also depends on complete relevant inputs, Projection
    and policy version identity, integrity, and implementation invalidation.

This is a single-process fixture, not a caching specification.
""")


if __name__ == "__main__":
    run()
