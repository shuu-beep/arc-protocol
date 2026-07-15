#!/usr/bin/env python3
"""
ARC temporal fidelity probe — single file, stdlib only.

What this isolates
------------------
Finding M (signer_fidelity_fixture) said: a valid signature proves a key signed;
it does NOT prove the signer read its mandate faithfully. This probe is M's twin
one layer down — on the EVIDENCE layer rather than the custody/signer layer.

  > A valid signature proves the key signed. It does NOT prove that the stamped
  > `timestamp` is true.

The timestamp lives inside `signing_bytes`, so it is baked into the event id and
the signature. That cuts two ways, and the cut is the whole finding:

  * Changing a timestamp AFTER signing changes the id and breaks the signature.
    ARC catches this — it is post-signature mutation, not a temporal lie.
  * Stamping a FALSE timestamp BEFORE signing is honestly signed. The signature
    is genuine over a false value. This is not a forgery; it is an asserted
    falsehood — exactly finding M's shape, moved from "what the mandate meant"
    to "when the act happened".

Why it matters: `as_of`, revocation, challenge windows, adjudication, and standing
all stand on `event.timestamp`. A temporal lie sits one layer BENEATH authority and
fidelity. If the clock can lie, everything folded over it inherits the lie.

The one structural defence ARC has for free
-------------------------------------------
ARC never stamps a trusted clock, but it does have the `refs` content-hash DAG.
You cannot ref an id that does not exist yet — an id is a hash of the event's own
bytes — so `B refs A` is real, tamper-evident evidence that **B was minted after A**.
That gives a partial *causal* order over events, independent of any timestamp.

A false timestamp is caught ONLY when it contradicts that causal order:

  * careless backdate — the event refs something NEWER than its claimed time. The
    ref pins a lower bound the claim violates. CAUGHT by the DAG, no clock needed.
  * careful backdate  — the event refs only genuinely-older events. Nothing in the
    DAG contradicts the claim. UNDETECTABLE by ARC vocabulary alone.

So ARC is NOT blind to time — refs give a partial order for free. The finding is
the GAP between that causal order and the wall clock: temporal fidelity is
unobservable exactly in the causal gaps, where two events are concurrent (neither
refs the other) and only an unverifiable timestamp claims to order them.

The five readouts
-----------------
  1. post-signature mutation — the baseline ARC DOES catch (id/signature break).
  2. careless backdate       — refs the future; the DAG's lower bound bites.
  3. careful backdate        — refs only the genuine past; passes every check.
  4. revocation race         — a careful backdate stamped before a revocation it
                               never refs; a claimed-timestamp time-scoped fold
                               honors an act really minted after withdrawal.
  5. concurrent -> CONTESTED — the residue: the act and the revocation are causally
                               concurrent; only the timestamp orders them; drop that
                               trust and the order — hence the verdict — is CONTESTED.
                               (finding J's honest-terminal output, on the time axis.)

Plus the named mitigation and why it is not free:
  head-anchor oracle — require each event to ref a recent head. That forces the act
  to descend from the revocation, collapsing the concurrency and catching the lie —
  but "recent head" is a clock/sequencer the signer must honestly consult: a trust
  root ARC does not govern (finding M's attested-signer shape). A signer that lies
  about the head it saw re-opens the gap.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the FOLD over the
    timestamp, not custody. But id and refs hashing are REAL content hashes, so the
    causal DAG genuinely bites: a careless backdate cannot ref the future for free;
  * the five canonical types are reused as-is — no new primitive, no stored clock,
    no trusted-timestamp object, no stored "temporal score";
  * this is a probe, not a protocol spec and not doctrine.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Any

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}


# ---------------------------------------------------------------------------
# The Event and its mock signing — same lean shape as the other probes. The
# timestamp is part of signing_bytes, so it is baked into both the id and the
# signature. That is the hinge of the whole probe.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    id: str
    type: str
    signer: str
    predicate: str
    timestamp: str                       # the CLAIM. honestly signed, not necessarily true.
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
    """MOCK. Real ARC uses Ed25519; a hash stands in so replay still verifies.

    The signature is a function of (signer, bytes). The bytes include the
    timestamp, so the signature is honest over WHATEVER time was stamped — true
    or false. The mock makes finding O free: a real key would sign a false time
    just as faithfully as a true one.
    """
    return "stub:" + hashlib.sha256(signer.encode() + body).hexdigest()[:16]


def content_id(body: bytes) -> str:
    return "ev:" + hashlib.sha256(body).hexdigest()[:12]


def make(type_: str, signer: str, predicate: str, ts: str, **kw) -> Event:
    assert type_ in CANONICAL_TYPES, f"non-canonical type {type_!r} — forbidden"
    partial = Event(id="", type=type_, signer=signer, predicate=predicate, timestamp=ts, **kw)
    body = partial.signing_bytes()
    return Event(id=content_id(body), type=type_, signer=signer, predicate=predicate,
                 timestamp=ts, signature=stub_sign(signer, body), **kw)


def verify_log(events: list[Event]) -> None:
    """Verification IS replay: id integrity + signature + signer anchored by a KEY.

    Note what verify_log CANNOT see: whether a timestamp is TRUE. Every event
    below verifies — the signature is honest over whatever time was claimed.
    A true clock is not a signature property; ARC does not add one.
    """
    registered: set[str] = set()
    for ev in events:
        body = ev.signing_bytes()
        if ev.id != content_id(body):
            raise ValueError(f"id does not match content on {ev.id} (post-signature mutation)")
        if ev.signature != stub_sign(ev.signer, body):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# The causal order — derived ONLY from refs, never from timestamps. This is the
# evidence the DAG gives for free: B refs A  =>  B was minted after A.
# ---------------------------------------------------------------------------

def causal_ancestors(by_id: dict[str, Event], ev_id: str) -> set[str]:
    """Transitive closure of refs: everything that must have existed before ev."""
    seen: set[str] = set()
    stack = list(by_id[ev_id].refs)
    while stack:
        r = stack.pop()
        if r in seen or r not in by_id:
            continue
        seen.add(r)
        stack.extend(by_id[r].refs)
    return seen


def causal_violations(events: list[Event]) -> list[tuple[str, str]]:
    """A timestamp claim is caught iff it contradicts the DAG: an event must be
    strictly later than every event it (transitively) refs. Returns the
    (event, ancestor) pairs where the claim is impossible — the careless backdates."""
    by_id = {e.id: e for e in events}
    bad: list[tuple[str, str]] = []
    for e in events:
        for a in causal_ancestors(by_id, e.id):
            if not (by_id[a].timestamp < e.timestamp):
                bad.append((e.id, a))
    return bad


def concurrent(by_id: dict[str, Event], a_id: str, b_id: str) -> bool:
    """Causally concurrent: neither is an ancestor of the other. The DAG says
    nothing about their order; only their timestamps claim to."""
    return (a_id not in causal_ancestors(by_id, b_id)
            and b_id not in causal_ancestors(by_id, a_id))


# ---------------------------------------------------------------------------
# The folds at stake. Both stand on `event.timestamp` — which is the exposure.
# ---------------------------------------------------------------------------

def honoring_by_claimed_act_time(events: list[Event], act_id: str) -> dict:
    """Read the full log, trust the act's CLAIMED timestamp, and decide whether
    this time-scoped policy honors the act. This is not the earlier-event-subset
    historical baseline in authority-revocation-demo — and that distinction is
    exactly what a careful backdate exploits."""
    by_id = {e.id: e for e in events}
    act = by_id[act_id]
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.mandate"), None)
    if mandate is None:
        return {"verdict": "NO_MANDATE", "reason": "act refs no mandate"}
    revoked = next((r for r in events
                    if mandate.id in r.nullifies and r.timestamp <= act.timestamp), None)
    if revoked is None:
        return {"verdict": "HONORED",
                "reason": f"at claimed {act.timestamp} the mandate was live "
                          f"(no revocation stamped at or before the claim)"}
    return {"verdict": "DECLINED", "reason": f"revoked by {revoked.id} @ {revoked.timestamp}"}


def honoring_by_causality(events: list[Event], act_id: str, rev_id: str) -> dict:
    """Drop trust in the timestamp; order the act and the revocation by the DAG
    alone. If the DAG cannot order them, neither can ARC — the verdict is CONTESTED."""
    by_id = {e.id: e for e in events}
    if rev_id in causal_ancestors(by_id, act_id):
        return {"verdict": "DECLINED", "reason": "act causally descends from the revocation"}
    if act_id in causal_ancestors(by_id, rev_id):
        return {"verdict": "HONORED", "reason": "revocation causally descends from the act"}
    return {"verdict": "CONTESTED",
            "reason": "act and revocation are causally concurrent — the DAG does not "
                      "order them; only an unverifiable timestamp claims to"}


# ---------------------------------------------------------------------------
# Participants and ledger. Unlike the other probes, the ledger here lets a party
# STAMP a chosen time — because lying about the clock is the whole point. The
# real mint order is tracked separately, for the omniscient strip only.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, *, claim: str, real: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, claim, **kw)
        self.ledger.append(ev, real)
        flag = "" if claim == real else f"   << claims {claim}, REALLY minted {real}"
        print(f"    -> {self.name} {type_} {predicate}  [{ev.id}] @ {claim}{flag}")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.real_mint: dict[str, str] = {}   # event id -> true mint time (omniscient)

    def append(self, ev: Event, real: str) -> None:
        self.events.append(ev)
        self.real_mint[ev.id] = real

    def events_by_id(self) -> dict[str, Event]:
        return {e.id: e for e in self.events}


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    principal = Party(led, "principal", "k:principal")   # grants and revokes the mandate
    agent     = Party(led, "agent",     "k:agent")       # the backdating signer

    print("\n1. Identity — principal and agent each anchor a key")
    principal.emit("KEY", "id.key_register", claim="2026-06-10T09:50:00Z",
                   real="2026-06-10T09:50:00Z", payload={"key": principal.key})
    agent.emit("KEY", "id.key_register", claim="2026-06-10T09:51:00Z",
               real="2026-06-10T09:51:00Z", payload={"key": agent.key})

    print("\n2. Mandate — principal grants the agent a market mandate (real 10:00)")
    mandate = principal.emit("AUTHORIZE", "consent.mandate", claim="2026-06-10T10:00:00Z",
                             real="2026-06-10T10:00:00Z", refs=("k:agent",),
                             scope={"category": "market", "max_total_krw": 30000})

    print("\n3. Revocation — principal revokes the mandate (real 10:05)")
    say("principal", "the agent's mandate is withdrawn as of now")
    revocation = principal.emit("AUTHORIZE", "consent.withdraw", claim="2026-06-10T10:05:00Z",
                                real="2026-06-10T10:05:00Z", refs=(mandate.id,),
                                nullifies=(mandate.id,))

    # -- Readout 1: post-signature mutation — the baseline ARC catches ----------
    print("\n4. Readout 1 — POST-SIGNATURE MUTATION (the lie ARC DOES catch)")
    honest = make("ATTEST", agent.key, "commerce.receipt", "2026-06-10T10:02:00Z",
                  refs=(mandate.id,), payload={"item": "groceries"})
    tampered = replace(honest, timestamp="2026-06-10T09:30:00Z")   # rewrite the clock, keep id+sig
    print(f"    minted [{honest.id}] @ {honest.timestamp}, then rewrote its timestamp to "
          f"{tampered.timestamp} keeping the old id/sig")
    try:
        verify_log(led.events + [tampered])
        print("    verify_log PASSED — (should not happen)")
    except ValueError as exc:
        print(f"    verify_log REJECTS it: {exc}")
    print("    Changing a stamped time after signing breaks the content hash. This is the")
    print("    easy half — and it is the ONLY half a signature defends.")

    # -- Readout 2: careless backdate — the DAG bites --------------------------
    print("\n5. Readout 2 — CARELESS BACKDATE (refs the future; the refs DAG bites)")
    careless = agent.emit("ATTEST", "commerce.receipt", claim="2026-06-10T09:55:00Z",
                          real="2026-06-10T10:06:00Z", refs=(mandate.id,),
                          payload={"item": "groceries", "note": "stamped before the mandate it refs"})
    viol = [(e, a) for (e, a) in causal_violations(led.events) if e == careless.id]
    for e, a in viol:
        print(f"    causal check: {e} claims {careless.timestamp} but refs {a} "
              f"(@ {led.events_by_id()[a].timestamp}) — impossible, an event is later than what it refs")
    print("    The ref pins a lower bound the claim violates. No clock was needed to catch it.")

    # -- Readout 3: careful backdate — undetectable ----------------------------
    print("\n6. Readout 3 — CAREFUL BACKDATE (refs only the genuine past; nothing bites)")
    careful = agent.emit("AUTHORIZE", "consent.execute", claim="2026-06-10T10:01:00Z",
                         real="2026-06-10T10:06:00Z", refs=(mandate.id,),
                         scope={"total_krw": 20000, "category": "market"},
                         payload={"item": "groceries"})
    cv = [(e, a) for (e, a) in causal_violations(led.events) if e == careful.id]
    print(f"    causal check on {careful.id}: {'VIOLATION' if cv else 'no violation — passes'}")
    print(f"    It claims 10:01 (after the mandate it refs @ 10:00) and refs nothing newer.")
    print(f"    verify_log: ", end="")
    verify_log(led.events)
    print("passes. Every structural check is green. The clock is a lie and ARC cannot see it.")

    # -- Readout 4: revocation race --------------------------------------------
    print("\n7. Readout 4 — REVOCATION RACE (the careful backdate beats a real revocation)")
    say("agent", "I really act at 10:06 — AFTER the 10:05 revocation — but I stamp 10:01")
    claimed_time_fold = honoring_by_claimed_act_time(led.events, careful.id)
    print(f"    claimed-timestamp time-scoped fold: {claimed_time_fold['verdict']}  "
          f"({claimed_time_fold['reason']})")
    print(f"    The revocation @ 10:05 is real, but the act never refs it and claims 10:01,")
    print(f"    so this full-log policy honors an act really minted after withdrawal.")
    print(f"    The careful backdate wins the race, and ARC's vocabulary cannot call it.")

    # -- Readout 5: the residue — concurrent -> CONTESTED ----------------------
    print("\n8. Readout 5 — CONCURRENT -> CONTESTED (the residue beneath the race)")
    by_id = led.events_by_id()
    print(f"    Are the act [{careful.id}] and the revocation [{revocation.id}] causally ordered?")
    print(f"      act refs:        {careful.refs}")
    print(f"      revocation refs: {revocation.refs}")
    print(f"      concurrent? {concurrent(by_id, careful.id, revocation.id)} "
          f"(both ref the mandate; neither refs the other)")
    c_fold = honoring_by_causality(led.events, careful.id, revocation.id)
    print(f"    order-by-causality fold: {c_fold['verdict']}  ({c_fold['reason']})")
    print("    The revocation race is THIS residue with money on it: the only thing that")
    print("    ordered the act before the revocation was a timestamp no one can verify.")
    print("    Remove that trust and the honest terminal output is CONTESTED — finding J's")
    print("    irreducible disagreement, now on the TIME axis. Representable, not resolvable.")

    # -- The mitigation, and its price -----------------------------------------
    print("\n9. Mitigation — HEAD-ANCHOR ORACLE (closes the race; imports a trust root)")
    head_at_real_mint = revocation.id   # at real 10:06 the head is the 10:05 revocation
    anchored = head_at_real_mint in (careful.refs)
    print(f"    A head-anchor rule requires each event to ref a recent head.")
    print(f"    At the act's REAL mint time (10:06) the head is the revocation [{revocation.id}].")
    print(f"    Does the careful backdate ref it? {anchored}.")
    print(f"    Honest compliance would force the act to ref the revocation -> the revocation")
    print(f"    becomes a causal ancestor -> claim 10:01 < 10:05 fails the causal check -> CAUGHT.")
    print(f"    But 'the recent head' is a clock/sequencer the signer must consult HONESTLY.")
    print(f"    That is a trust root ARC does not govern (finding M's attested-signer shape):")
    print(f"    a signer that lies about the head it saw re-opens the very gap it was to close.")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes "
          f"(every timestamp, true or false, is honestly signed).")
    verify_log(led.events)

    print("\n--- omniscient view — available to NO observer (folds never read this) ---")
    for ev in led.events:
        claim, real = ev.timestamp, led.real_mint[ev.id]
        mark = "  <-- BACKDATED" if claim != real else ""
        print(f"    [{ev.id}] {ev.predicate:<18} claims {claim}  | real {real}{mark}")
    print("    The log carries the claimed times. It does NOT carry the real ones.")
    print("    The refs DAG bounds them only partially; in the gaps, the clock is unverifiable.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can ARC detect a false timestamp on a genuine signature?
      In general, NO. The timestamp is inside signing_bytes, so a key signs a false
      time as honestly as a true one. A signature proves the key signed; it does not
      prove the clock. (Twin of finding M, on the evidence layer.)
  * What CAN ARC detect about time?
      - post-signature mutation: rewriting a stamped time breaks the content hash;
      - careless backdate: an event that refs something newer than its claimed time
        contradicts the refs DAG's causal lower bound;
      - the after-the-fact record: revocations, nullifications, and conflicting later
        attestations are themselves events, and the DAG dates them relative to refs.
      So ARC is not blind to time — the refs DAG gives a partial causal order for free.
  * What CAN ARC NOT detect?
      - whether the signer honestly observed the claimed time;
      - whether `as_of` corresponds to real-world time;
      - a CAREFUL backdate: an event stamped false but refs only the genuine past.
        It passes verify_log and the causal check, and a claimed-timestamp
        time-scoped fold will honor an act really minted after withdrawal.
  * Where exactly is the lie unobservable?
      In the causal GAPS. For concurrent events — neither refs the other — the DAG
      gives no order; only the timestamp claims one. Drop trust in the timestamp and
      the order is genuinely CONTESTED. The revocation race is that residue with
      stakes: the act and the revocation are concurrent, and only an unverifiable
      stamp put the act "before" the revocation.
  * Does the mitigation close it?
      Head-anchoring (ref a recent head) collapses the concurrency and catches the
      careful backdate — but it relocates trust to a head-oracle / sequencer / clock,
      a root ARC does not govern (finding M's attested-signer move). It does not make
      the timestamp true; it imports something that asserts it.

Conclusion: ARC can PRESERVE a temporal claim — bind it into the signature, bound it
partially with the refs DAG — but it cannot make the claim TRUE. Real-world time
enters ARC the way the external world always does: as an ATTEST claim, true only as
far as a witness, receipt, trusted clock, or policy-specific adjudication carries it.
Temporal fidelity, like signer fidelity, is a property of the world the log cannot
seal — the signature seals the record, never its referent.

No sixth type was required. No stored clock, no trusted-timestamp object, no temporal
score. The gap is a fold-policy residue between causal order and wall-clock order.
This is a probe, not a protocol spec and not doctrine.
""")


if __name__ == "__main__":
    run()
