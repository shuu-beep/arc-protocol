#!/usr/bin/env python3
"""
ARC threshold / joint-authority probe — single file, stdlib only.

What this isolates
------------------
Every authority probe so far (canon-fold-demo, authority-revocation-demo,
the reference-client bands) assumes *single-signer* delegation: one AUTHORIZE
grants one key the standing to act. Real authority is often **joint** — a 2-of-3
treasury board, a co-signed spend, an M-of-N committee. `key-custody.md` §8 lists
"threshold custody" as an open question.

This probe asks the smallest version of it:

> Can M-of-N joint authority be represented with the existing five types — and if
> so, *where does the quorum rule live?*

The setup is a 2-of-3 board. The principal grants an agent a spending mandate that
is only honored when **two of three named members approve** a candidate act:

    principal  --AUTHORIZE consent.joint_mandate-->  scope={members:[m1,m2,m3],
                                                            threshold:2, max:30000}
    agent      --AUTHORIZE consent.execute------->  candidate spend (refs mandate)
    m1         --ATTEST   consent.approve-------->  candidate            [1 of 3]
    m2         --ATTEST   consent.approve-------->  candidate            [2 of 3]  quorum
    principal  --AUTHORIZE consent.withdraw------>  nullifies m2's approval

Nothing here is a new event type. The joint set is recorded as **scope on one
ordinary AUTHORIZE** (members + threshold are parameters, exactly like
`max_total_krw` in the revocation probe). Each approval is an ordinary `ATTEST`.
The standing question — "did this act reach quorum?" — is a **projection**: a fold
that *counts* approvals against the recorded threshold. It is never stored.

The core finding
----------------
The threshold *number* lives in an event (scope). The quorum *rule* — what counts
as an approval, whether non-members or duplicates count, how a later revocation
re-reads the count — does NOT. It lives in the fold. So joint authority opens a
fresh observer-relative boundary, on two independent axes the probe crosses:

  * revocation reading (the finding-G axis): revoke a signer after quorum, and
      - as-of-act-time / time-scoped  -> quorum stood -> authorized;
      - retroactive cascade           -> the approval is voided -> below threshold.
  * counting policy (the new axis): the SAME approvals
      - strict   (distinct named members only) -> a stray key does not count;
      - lenient  (any anchored signer)         -> a stray key restores quorum.
    A party holding ONE member key plus a stray key can manufacture a "valid"
    quorum against any counterparty whose fold uses the lenient rule.

And one guard, shown cheaply: quorum cannot *widen* scope. A spend over the
mandate's ceiling is unauthorized even at a full 3-of-3.

Deliberately dirty and small. Explicitly:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the finding is about the FOLD,
    not custody;
  * the five canonical types are reused as-is — no new primitive, no stored
    authority object;
  * this is a probe, not a multisig spec and not doctrine.

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
# The one projection at stake: did a candidate act reach quorum?
#
# Two independent knobs, both OUTSIDE the canon:
#   * retroactive — how a later withdrawal re-reads an approval (finding-G axis).
#   * counting    — which approvals count (the quorum-rule-is-policy axis).
# Nothing here is stored; this is recomputed on demand.
# ---------------------------------------------------------------------------

def project_quorum(events: list[Event], candidate_id: str, *,
                   retroactive: bool, counting: str) -> dict:
    by_id = {e.id: e for e in events}
    act = by_id.get(candidate_id)
    if act is None:
        return {"act": candidate_id, "found": False}

    # the joint mandate this candidate relied on (first such AUTHORIZE in refs)
    mandate = next((by_id[r] for r in act.refs
                    if r in by_id and by_id[r].predicate == "consent.joint_mandate"), None)
    if mandate is None or mandate.scope is None:
        return {"act": candidate_id, "found": True, "authorized": False,
                "reason": "no joint mandate referenced", "count": 0, "threshold": None}

    members = set(mandate.scope.get("members", ()))
    threshold = mandate.scope.get("threshold")
    max_krw = mandate.scope.get("max_total_krw")
    amount = (act.scope or {}).get("total_krw")

    # approvals naming this candidate
    approvals = [e for e in events
                 if e.type == "ATTEST" and e.predicate == "consent.approve"
                 and candidate_id in e.refs]

    # withdrawals: which approvals are voided, under the chosen reading?
    voided: set[str] = set()
    for w in events:
        if w.type == "AUTHORIZE" and w.predicate == "consent.withdraw":
            for nid in w.nullifies:
                # retroactive cascade voids over all history; time-scoped voids
                # only for acts at/after the withdrawal (this act predates it).
                if retroactive or w.timestamp <= act.timestamp:
                    voided.add(nid)

    live = [a for a in approvals if a.id not in voided]

    if counting == "strict":
        # distinct, named members only — a stray key does not count
        approvers = {a.signer for a in live if a.signer in members}
        notes = "distinct named members only"
    elif counting == "lenient":
        # any anchored signer counts — membership not checked
        approvers = {a.signer for a in live}
        notes = "any anchored signer counts (membership ignored)"
    else:
        raise ValueError(f"unknown counting policy {counting!r}")

    count = len(approvers)
    out_of_scope = (max_krw is not None and amount is not None and amount > max_krw)
    quorum_met = threshold is not None and count >= threshold
    authorized = quorum_met and not out_of_scope

    reason = f"{count}/{threshold} approvals [{notes}]"
    if out_of_scope:
        reason += f"; OUT OF SCOPE ({amount} > ceiling {max_krw}) — quorum cannot widen scope"
    return {"act": candidate_id, "found": True, "authorized": authorized,
            "count": count, "threshold": threshold, "out_of_scope": out_of_scope,
            "approvers": sorted(approvers), "reason": reason}


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
        # the board's whole morning of approvals lands at hour 10; the principal's
        # later withdrawal (the only afternoon event) lands at hour 16.
        hour = 10 if self._clock <= 16 else 16
        return f"2026-06-09T{hour:02d}:{self._clock:02d}:00Z"

    def append(self, ev: Event) -> None:
        self.events.append(ev)


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def show(r: dict) -> None:
    print(f"    authorized={r['authorized']}  ({r['reason']})")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    principal = Party(led, "principal", "k:principal")   # grants the joint mandate
    m1 = Party(led, "member-1", "k:m1")                  # board member
    m2 = Party(led, "member-2", "k:m2")                  # board member
    m3 = Party(led, "member-3", "k:m3")                  # board member
    agent = Party(led, "agent", "k:agent")               # treasurer / executor
    stray = Party(led, "stray", "k:stray")               # a registered key, NOT on the board

    print("\n1. Identity — principal, three board members, an agent, and one")
    print("   non-member 'stray' key each anchor a key (KEY id.key_register)")
    for p in (principal, m1, m2, m3, agent, stray):
        p.emit("KEY", "id.key_register", payload={"key": p.key})

    print("\n2. Joint mandate — principal grants the agent a 2-of-3 spending mandate")
    say("principal", "agent may spend treasury funds up to 30000, but only with 2-of-3 board approval")
    mandate = principal.emit("AUTHORIZE", "consent.joint_mandate", refs=("k:agent",),
                             scope={"members": ["k:m1", "k:m2", "k:m3"], "threshold": 2,
                                    "category": "treasury", "max_total_krw": 30000})

    print("\n3. Candidate A (in scope) — agent proposes a 24000 spend needing quorum")
    candA = agent.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                       scope={"total_krw": 24000, "category": "treasury", "payee": "vendor_x"})

    print("\n   m1 approves (ATTEST consent.approve)")
    appr1 = m1.emit("ATTEST", "consent.approve", refs=(candA.id, mandate.id))
    print("\n   --- (1) BELOW THRESHOLD: only one approval so far ---")
    show(project_quorum(as_of(led.events, appr1.timestamp), candA.id,
                        retroactive=False, counting="strict"))

    print("\n   m2 approves (ATTEST consent.approve) — quorum reached")
    appr2 = m2.emit("ATTEST", "consent.approve", refs=(candA.id, mandate.id))
    print("\n   --- (2) QUORUM SATISFIED: two distinct members approved ---")
    show(project_quorum(as_of(led.events, appr2.timestamp), candA.id,
                        retroactive=False, counting="strict"))

    say("agent", "quorum stood; executing and recording the payment")
    payA = agent.emit("ATTEST", "commerce.payment_result", refs=(candA.id,),
                      payload={"result": "confirmed", "amount_krw": 24000, "provider": "mock_pay"})

    say("stray", "a non-board key also signs an approval for candidate A (sets up the counting axis)")
    stray.emit("ATTEST", "consent.approve", refs=(candA.id, mandate.id))

    print("\n4. Candidate B (OVER scope) — agent proposes 50000; the whole board approves")
    candB = agent.emit("AUTHORIZE", "consent.execute", refs=(mandate.id,),
                       scope={"total_krw": 50000, "category": "treasury", "payee": "vendor_y"})
    for m in (m1, m2, m3):
        m.emit("ATTEST", "consent.approve", refs=(candB.id, mandate.id))
    print("\n   --- guard: QUORUM CANNOT WIDEN SCOPE — 3-of-3 but over the ceiling ---")
    show(project_quorum(led.events, candB.id, retroactive=False, counting="strict"))

    print("\n5. Revocation after quorum — principal withdraws member-2's approval on A")
    say("principal", "member-2 should no longer count toward candidate A; withdrawing that approval")
    principal.emit("AUTHORIZE", "consent.withdraw", refs=("k:m2", mandate.id),
                   nullifies=(appr2.id,), payload={"reason": "member_standing_withdrawn"})

    print("\n   --- (3) SIGNER REVOKED AFTER QUORUM, and (4) the readings DIVERGE on candidate A ---")
    print("   asof = the moment of reliance (payment recorded):", payA.timestamp)
    rows = [
        ("as-of-act-time          (strict)", as_of(led.events, payA.timestamp), False, "strict"),
        ("current-log time-scoped  (strict)", led.events, False, "strict"),
        ("current-log cascade      (strict)", led.events, True, "strict"),
        ("current-log cascade      (LENIENT)", led.events, True, "lenient"),
    ]
    for label, evs, retro, counting in rows:
        r = project_quorum(evs, candA.id, retroactive=retro, counting=counting)
        flag = "  <-- quorum 'restored' by a non-member" if (counting == "lenient" and r["authorized"]) else ""
        print(f"    {label}: authorized={r['authorized']}  ({r['reason']}){flag}")

    print(f"\nGenerated log: {len(led.events)} signed events. verify_log passes.")
    verify_log(led.events)
    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * Can M-of-N be represented in the five types?
      Yes. The joint set is scope on ONE ordinary AUTHORIZE (members + threshold,
      like any other scope parameter); each approval is an ordinary ATTEST; the
      revocation is the existing `nullifies` field. NO sixth type, no stored
      authority object, no "multisig" primitive.
  * Where does the quorum RULE live?
      Not in any event. The threshold *number* is recorded, but "did this reach
      quorum?" is a PROJECTION — a fold that counts approvals on demand. The
      counting rule (distinct? members-only? non-members?) is a fold policy.
  * Does that make joint authority observer-relative?
      Yes, on two independent axes the probe crosses:
        - revocation reading (finding-G axis): revoke a signer after quorum, and
          as-of-act-time / time-scoped preserve the act while a retroactive
          cascade drops it below threshold — the SAME nullify, two answers;
        - counting policy: strict (distinct named members) rejects a stray key
          that lenient (any anchored signer) counts. A party with ONE member key
          plus a stray key can manufacture a valid quorum against any counterparty
          whose fold uses the lenient rule. The threshold is itself an attack
          surface — not because a type is missing, but because the rule is policy.
  * Does reaching quorum widen what may be done?
      No. Candidate B is unauthorized at a full 3-of-3 because it exceeds the
      mandate ceiling. Quorum satisfies the approval requirement; it does not
      enlarge scope. Scope and quorum are separate gates, both folds.

No sixth type was required. Joint authority is representable; the quorum rule is a
fold-policy residue — the same shape as findings B/C/D/G — and it adds a second
observer-relative boundary, now on the count itself. This is a probe, not a
multisig spec and not doctrine.
""")


if __name__ == "__main__":
    run()
