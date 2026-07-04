#!/usr/bin/env python3
"""
ARC authority-revocation probe — single file, stdlib only.

What this isolates
------------------
The delegation probe in `examples/canon-fold-demo` (scenario 10, finding G) noted
in passing that revoking a delegation does NOT, on its own, tell you whether an
act already *completed* under that delegation stays valid. This probe pulls that
one question out on its own and shows the divergence directly.

The setup is the smallest one that makes the question bite — a delegation chain
with a real downstream party who relied on then-valid authority:

    human (principal)  --AUTHORIZE consent.mandate-->  agent A      [time T1]
    agent A            --AUTHORIZE consent.execute-->   the purchase [time T1]
    agent A / merchant --ATTEST payment / fulfillment-> done         [time T1]
    human              --AUTHORIZE consent.withdraw-->  revokes A     [time T2]

At T1 the purchase was backed by a live mandate; the merchant fulfilled in
reliance on it. At T2 the human revokes A's mandate. The SAME signed revoke
event then reads two ways, and the two readings produce *different answers* to
"was that purchase a validly authorized transaction?":

  * as-of-act-time  — replay the log as it stood at the act -> mandate live
                      -> authorized. A later revoke withdraws authority going
                      forward only; the past act is preserved.
  * current-log     — replay the whole log now. This is itself ambiguous:
      - time-scoped reading: the revoke is "going forward", the act predates it
                      -> still authorized (agrees with as-of-act-time);
      - retroactive cascade: treat the mandate as void over its whole history
                      -> the act it backed collapses too -> NOT authorized.

The finding is not a missing event type. The revoke is one ordinary event (the
existing `nullifies` field on an `AUTHORIZE consent.withdraw`, event-registry
§4.6 — no sixth type). What the canon does NOT fix is which of these readings a
projection uses. That is a fold-policy choice sitting above the canon, the same
shape as findings B/C/D/G.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519);
  * the five canonical types are reused as-is — no new primitive;
  * this is a probe, not a revocation spec and not doctrine.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

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
    """Verification IS replay: signature check + signer anchored by a prior KEY."""
    registered: set[str] = set()
    for ev in events:
        if ev.signature != stub_sign(ev.signer, ev.signing_bytes()):
            raise ValueError(f"bad signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


def as_of(events: list[Event], t: str) -> list[Event]:
    """Replay input restricted to events recorded at or before `t` (object-model
    §5). No new mechanism: a fold is over whatever event subset the reader holds."""
    return [e for e in events if e.timestamp <= t]


# ---------------------------------------------------------------------------
# The one projection at stake: was a delegated purchase validly authorized?
# ---------------------------------------------------------------------------

def project_authorization(events: list[Event], act_id: str, *, retroactive: bool) -> dict:
    """Fold the log to answer: was `act_id` backed by a live mandate?

    The act references the mandate it relied on (refs). The mandate is a live
    grant unless an `AUTHORIZE consent.withdraw` names it in `nullifies`. The ONE
    knob is how that withdrawal is read against the act's own timestamp:

      * retroactive=False (time-scoped) — the withdrawal voids the mandate only
        for acts at/after the withdrawal timestamp; an earlier act is preserved.
      * retroactive=True  (cascade)     — the withdrawal voids the mandate over
        its whole history; the earlier act it backed collapses too.

    Nothing here is stored; this is recomputed on demand."""
    by_id = {e.id: e for e in events}
    act = by_id.get(act_id)
    if act is None:
        return {"act": act_id, "found": False}

    # the mandate this act relied on (first AUTHORIZE consent.mandate in refs)
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.mandate"), None)
    if mandate is None:
        return {"act": act_id, "found": True, "mandate": None, "authorized": False,
                "reason": "no mandate referenced"}

    # withdrawals that name this mandate in `nullifies`
    withdrawals = [e for e in events
                   if e.type == "AUTHORIZE" and e.predicate == "consent.withdraw"
                   and mandate.id in e.nullifies]
    voided_by = None
    for w in withdrawals:
        if retroactive or w.timestamp <= act.timestamp:
            voided_by = w
            break

    authorized = voided_by is None
    return {
        "act": act_id, "found": True, "mandate": mandate.id,
        "authorized": authorized,
        "reason": ("mandate live at act time" if authorized
                   else f"mandate withdrawn by {voided_by.id}"
                        + (" (cascaded onto a completed act)" if retroactive else "")),
    }


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
        # The whole T1 transaction lands in the morning; the revoke (step 4) and
        # the later dispute/adjudication (step 5) land in the afternoon.
        hour = 10 if self._clock <= 8 else 16
        return f"2026-06-08T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    human = Party(led, "human", "k:human")          # the principal / buyer
    agentA = Party(led, "agent-A", "k:agentA")       # buyer's delegated agent
    merchant = Party(led, "merchant", "k:merchant")  # downstream relying party

    print("\n1. Identity — each party anchors a key (KEY id.key_register)")
    for p in (human, agentA, merchant):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Delegation at T1 — the human grants agent A a scoped mandate")
    say("human", "agent A may buy groceries up to 30000 KRW, expiring tonight")
    mandate = human.emit("AUTHORIZE", "consent.mandate", refs=("k:agentA",),
                         scope={"category": "groceries", "max_total_krw": 30000,
                                "expires_at": "2026-06-08T23:59:00Z"})

    print("\n3. Commerce at T1 — agent A acts WITHIN the live mandate; it completes")
    offer = merchant.emit("ATTEST", "commerce.offer",
                          payload={"item": "weekly_groceries", "price_krw": 24000})
    say("agent-A", "offer is in scope and the mandate is live; executing")
    act = agentA.emit("AUTHORIZE", "consent.execute", refs=(mandate.id, offer.id, "k:merchant"),
                      scope={"total_krw": 24000})
    agentA.emit("ATTEST", "commerce.payment_result", refs=(act.id, "k:merchant"),
                payload={"result": "confirmed", "amount_krw": 24000, "provider": "mock_pay"})
    say("merchant", "payment confirmed; fulfilling in reliance on A's authority")
    merchant.emit("ATTEST", "commerce.fulfillment", refs=(act.id,),
                  payload={"status": "delivered"})

    print("\n--- snapshot: BEFORE revocation (log as it stands at T1) ---")
    snapshot(led, act.id, as_of_t="2026-06-08T10:59:00Z")

    print("\n4. Revocation at T2 — later, the human withdraws agent A's mandate")
    say("human", "I no longer trust agent A; withdrawing the mandate")
    human.emit("AUTHORIZE", "consent.withdraw", refs=("k:agentA",), nullifies=(mandate.id,),
               payload={"reason": "agent_no_longer_trusted"})

    print("\n--- snapshot: AFTER revocation, CURRENT-LOG view (retroactive cascade) ---")
    print("    reads the whole log now and lets the withdrawal void the mandate's")
    print("    whole history -> the completed purchase collapses with it.")
    show(project_authorization(led.events, act.id, retroactive=True))

    print("\n--- snapshot: AFTER revocation, AS-OF-ACT-TIME view (preserve) ---")
    print("    replays the log as it stood at the act -> the revoke is not yet")
    print("    present -> the purchase stays a validly authorized transaction.")
    show(project_authorization(as_of(led.events, act.timestamp), act.id, retroactive=False))

    print("\n    (for contrast: CURRENT-LOG read time-scoped — revoke is 'going")
    print("     forward', the act predates it — AGREES with as-of-act-time:)")
    show(project_authorization(led.events, act.id, retroactive=False))

    # ---- the boundary: revocation is a fact; reopening a past act is a verdict ----
    print("\n5. Reopening one past act WITHOUT global collapse")
    say("human", "I think that specific purchase was actually unauthorized; disputing it")
    dispute = human.emit("CHALLENGE", "dispute.open", refs=(act.id, "k:merchant"),
                         payload={"reason": "claims_act_exceeded_mandate"})
    say("community", "reviews the one disputed act and rules it void — this act only")
    merchant_community = Party(led, "community", "k:community")
    merchant_community.emit("KEY", "id.key_register", payload={"key": "k:community"})
    merchant_community.emit("ADJUDICATE", "gov.act_voided", refs=(act.id, dispute.id),
                            payload={"resolves": dispute.id})
    print("    A CHALLENGE + ADJUDICATE reopens THIS act by id. The revoke did not")
    print("    do that on its own, and nothing else in the log was touched. Voiding a")
    print("    past act is an authority decision, not a side effect of revocation.")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes.")
    verify_log(led.events)
    print_finding()


def snapshot(led: Ledger, act_id: str, as_of_t: str) -> None:
    verify_log(led.events)
    show(project_authorization(as_of(led.events, as_of_t), act_id, retroactive=False))


def show(r: dict) -> None:
    print(f"    authorized={r['authorized']}  ({r['reason']})")


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Does revocation poison past authorized actions?
      Only under the retroactive-cascade reading. The time-scoped / as-of-act-time
      reading preserves them. The canon does not pick; both are valid folds.
  * Does it only affect future reliance?
      Under the time-scoped reading, yes — "withdrawn going forward".
  * Can a later challenge reopen a past act without automatic global collapse?
      Yes. A CHALLENGE + ADJUDICATE names ONE act by id (step 5). Revocation alone
      does not reopen anything; reopening is a separate, scoped authority decision.
  * Is revocation an event-log fact, a projection result, or an authority decision?
      All three live at different layers, and the probe keeps them apart:
        - the revoke itself is an EVENT FACT (one AUTHORIZE consent.withdraw);
        - whether it cascades onto a completed act is a PROJECTION choice;
        - whether that past act is punished/voided is an AUTHORITY decision (ADJUDICATE).
  * Where is the boundary between buyer protection and anti-social-credit?
      Honoring relied-upon authority (as-of-act-time) protects the counterparty who
      acted in good faith. A permanent, automatic, identity-keyed retroactive collapse
      would be a stored verdict about a party — the social-credit shape ARC refuses.
      So the automatic retroactive collapse is the reading to refuse as a DEFAULT —
      but ARC picks no default: cascade-vs-preserve stays a projection choice
      (authority-and-conflict §9, and this probe's own line above: "The canon does
      not pick"), and reopening a specific past act is always an explicit,
      per-act ADJUDICATE, never a side effect of the revocation.

No sixth type was added; the divergence is a fold-policy residue, not a missing
primitive. This is a probe, not final doctrine and not a revocation spec.
""")


if __name__ == "__main__":
    run()
