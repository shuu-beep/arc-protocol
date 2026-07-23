#!/usr/bin/env python3
"""
ARC view-fidelity fixture — signed bytes and displayed view may differ.

Single file, stdlib only, single process.

What this isolates
------------------
A fixture action's canonical bytes B are not changed. The fixture supplies renderer
outputs that reproduce, rewrite, or omit selected payload fields. The mock signature
check covers B, not the off-log renderer output.

Finding M varies a signer's interpretation of a recorded mandate. This fixture
instead varies an authored renderer output for the same payload.

Its relation to finding L
-------------------------
Finding L binds an approval to reviewable proposal fields. This fixture tests a
separate presentation assumption: a deterministic renderer can still omit a field.

The one thing the log can check, and the one it cannot
------------------------------------------------------
This fixture profile places a `view_hash` in the signed payload. Given the same action
bytes and declared renderer, its comparison can recompute the output hash and report a
mismatch. Hash equality proves only equality to that renderer output — not which output
was displayed or perceived.
A renderer that reproducibly omits a critical field is deterministic, its output hashes
consistently, and the commitment matches while the view remains lossy.
The fixture therefore treats a matching hash as limited evidence about one declared
renderer function and its inputs.

The six readouts
----------------
  1. boundary            — the Event set contains B and a deterministic id check;
                           it does not carry a renderer output.
  2. matching control    — a renderer includes the fixture's comparison fields.
  3. view/bytes mismatch — the same mock-signed action, an adversarial renderer rewrites the
                           payee; the mock replay check still covers unchanged B.
  4. mitigation (half)   — view_hash comparison reports the mismatch
                           (claimed_view_hash != recomputed_view_hash).
  5. omitted field       — a deterministic renderer omits the field reproducibly;
                           claimed == recomputed and the replay check passes.
  6. additional claim    — a rendered_view ATTEST records a claimed output hash; it
                           does not establish actual display or perception.

Fixture limits:
  * stdlib only, single process, no network, no transport, no storage;
  * signatures are MOCK (a hash, not Ed25519) — the point is the gap between bytes and
    view, not custody. IDs and view_hash use SHA-256 content hashes, so the recompute
    check detects the authored mismatch under the same renderer and inputs;
  * the canonical types are reused as-is — no new type, no "view object", no view score.
    A rendered_view attestation is an ordinary ATTEST predicate, not a new primitive;
  * a generator-only mapping records which authored renderer output was associated
    with each action; observer folds do not receive it;
  * `view_hash` is a field used by this fixture profile, not a base-protocol requirement;
  * this is a probe, not a protocol specification.

Run:  python3 probe.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable

CANONICAL_TYPES = {"KEY", "ATTEST", "AUTHORIZE", "CHALLENGE", "ADJUDICATE"}

# Fields selected by this fixture for its renderer-output comparison. They are not
# base-protocol requirements and the fold does not read them.
CRITICAL_FIELDS = ("payee", "amount_krw")


# ---------------------------------------------------------------------------
# The Event and its mock signing — the same lean shape as the other probes. The
# canonical bytes B are what gets signed; the rendered view V is NOT in here.
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
    """Deterministic fixture hash, not a signature or proof of key possession.

    It covers the signer label and bytes B so mutation is detectable; it says
    nothing about the displayed view.
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
    """Fixture replay check: id, deterministic mock signature, key registration.

    It cannot establish the displayed view, human perception, completeness, or
    production signature conformance.
    """
    registered: set[str] = set()
    for ev in events:
        body = ev.signing_bytes()
        if ev.id != content_id(body):
            raise ValueError(f"id does not match content on {ev.id} (post-signature mutation)")
        if ev.signature != stub_sign(ev.signer, body):
            raise ValueError(f"bad mock signature on {ev.id}")
        is_root = ev.type == "KEY" and ev.predicate == "id.key_register"
        if not is_root and ev.signer not in registered:
            raise ValueError(f"signer {ev.signer} not anchored by a KEY register ({ev.id})")
        if is_root:
            registered.add(ev.payload["key"])


# ---------------------------------------------------------------------------
# Renderers. Each turns canonical bytes B into an authored text output V. They are
# pure functions that run off-log; the Event set contains B, not V.
# ---------------------------------------------------------------------------

def _payload_of(action: Event) -> dict:
    return action.payload


def faithful_render(action: Event) -> str:
    """Include every field selected for this fixture's comparison."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  to:  {p['payee']}\n"
            f"  for: {p.get('item','-')}")


def adversarial_render(action: Event) -> str:
    """Render the same action with a rewritten, benign-looking payee label."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  to:  Merchant-A (trusted)\n"          # <-- not p['payee']
            f"  for: {p.get('item','-')}")


def careful_omit_render(action: Event) -> str:
    """Deterministic and reproducible — and reproducibly DROPS the payee line.
    Its output hashes consistently and a matching commitment passes recompute."""
    p = _payload_of(action)
    return (f"APPROVE PAYMENT\n"
            f"  pay: {p['amount_krw']} KRW\n"
            f"  for: {p.get('item','-')}")          # <-- payee line structurally omitted


def view_hash(view: str) -> str:
    """Fixture-profile content hash of one renderer output."""
    return "vh:" + hashlib.sha256(view.encode()).hexdigest()[:12]


def recompute_view_hash(action: Event, pinned_renderer: Callable[[Event], str]) -> str:
    """Recompute using the supplied action bytes and declared renderer.

    Hash equality proves equality to that output only; it does not establish which
    view was displayed, perceived, or semantically faithful.
    """
    return view_hash(pinned_renderer(action))


# ---------------------------------------------------------------------------
# Generator-only comparison. Observer folds do not receive which renderer output
# was associated with an action or the result of this fixture-specific field check.
# ---------------------------------------------------------------------------

def is_faithful(view: str, action: Event) -> bool:
    p = _payload_of(action)
    return all(str(p.get(fname)) in view for fname in CRITICAL_FIELDS)


def resolve_view_from_log(events: list[Event], action_id: str) -> dict:
    """Read a claimed renderer-output hash from the log, if present.

    The claim does not establish actual display, perception, or semantic fidelity.
    """
    attest = next((e for e in events
                   if e.type == "ATTEST" and e.predicate == "view.rendered"
                   and e.payload.get("action") == action_id), None)
    if attest is None:
        return {"verdict": "UNKNOWN",
                "reason": "no event carries a renderer-output claim for this action"}
    return {"verdict": "CLAIMED", "view_hash": attest.payload.get("view_hash"), "by": attest.signer,
            "reason": f"{attest.signer} attests a renderer-output hash; this does not "
                      f"establish actual display or perception"}


# ---------------------------------------------------------------------------
# Participants and ledger. The ledger carries mock-signed canonical bytes. The
# generator separately tracks an authored renderer-output mapping; no fold reads it.
# ---------------------------------------------------------------------------

class Party:
    def __init__(self, ledger: "Ledger", name: str, key: str):
        self.ledger, self.name, self.key = ledger, name, key

    def emit(self, type_: str, predicate: str, ts: str, **kw) -> Event:
        ev = make(type_, self.key, predicate, ts, **kw)
        self.ledger.append(ev)
        print(f"    -> {self.name} {type_} {predicate}  [{ev.id}]")
        return ev


class Ledger:
    def __init__(self) -> None:
        self.events: list[Event] = []
        self.saw: dict[str, tuple[str, bool]] = {}   # generator-only output mapping

    def append(self, ev: Event) -> None:
        self.events.append(ev)

    def record_view(self, action_id: str, view: str, action: Event) -> None:
        self.saw[action_id] = (view, is_faithful(view, action))


def say(who: str, msg: str) -> None:
    print(f"  [{who}] {msg}")


def show_view(label: str, view: str) -> None:
    print(f"    {label} authored output:")
    for line in view.splitlines():
        print(f"        | {line}")


# ---------------------------------------------------------------------------
# The flow — run once, top to bottom.
# ---------------------------------------------------------------------------

def run() -> None:
    led = Ledger()
    principal = Party(led, "principal", "k:principal")   # grants the mandate
    signer    = Party(led, "signer",    "k:signer")      # fixture signer label
    renderer  = Party(led, "renderer",  "k:renderer")    # the view-generator, used in the mitigation

    print("\n0. Identity + mandate")
    for p in (principal, signer, renderer):
        p.emit("KEY", "id.key_register", "2026-06-14T09:00:00Z", payload={"key": p.key})
    mandate = principal.emit("AUTHORIZE", "consent.mandate", "2026-06-14T10:00:00Z",
                             refs=("k:signer",),
                             scope={"category": "market", "max_total_krw": 100000})

    # The canonical bytes B contain a payment payload naming wallet:attacker. B is
    # unchanged while the authored renderer output varies.
    def action_payload(view_hash_value: str | None = None) -> dict:
        p = {"payee": "wallet:attacker", "amount_krw": 50000, "item": "electronics"}
        if view_hash_value is not None:
            p["view_hash"] = view_hash_value
        return p

    # -- Readout 1: boundary ---------------------------------------------------
    print("\n1. Readout 1 — RECORD BYTES / RENDERER OUTPUT")
    b1 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T11:00:00Z",
                     refs=(mandate.id,), payload=action_payload())
    print("    verify_log: ", end=""); verify_log(led.events); print("passes.")
    print(f"    The log holds B and id=hash(B) [{b1.id}]. It carries NO record of the view.")
    r = resolve_view_from_log(led.events, b1.id)
    print(f"    resolve-view-from-log: {r['verdict']}  ({r['reason']})")

    # -- Readout 2: matching renderer-output control ---------------------------
    print("\n2. Readout 2 — MATCHING RENDERER OUTPUT (fixture control)")
    v_faithful = faithful_render(b1)
    led.record_view(b1.id, v_faithful, b1)
    show_view("(matching renderer)", v_faithful)
    print(f"    comparison fields present? {is_faithful(v_faithful, b1)} — payee and amount match B.")
    print("    This is a generator-only comparison, not evidence of actual display or review.")

    # -- Readout 3: view/bytes mismatch -----------------------------------------
    print("\n3. Readout 3 — VIEW / BYTES MISMATCH")
    b3 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T12:00:00Z",
                     refs=(mandate.id,), payload=action_payload())
    v_adv = adversarial_render(b3)
    led.record_view(b3.id, v_adv, b3)
    show_view("(adversarial renderer)", v_adv)
    say("fixture", "the authored renderer output names Merchant-A")
    print(f"    The same mock-signed action (payload payee = wallet:attacker)")
    print(f"    rendered differently — the renderer rewrote the payee. The signer signs B;")
    print(f"    verify_log: ", end="")
    verify_log(led.events); print("passes.")
    print(f"    matches fixture critical fields? {is_faithful(v_adv, b3)}. B is untampered,")
    print("    and its payload still names wallet:attacker; this fixture executes no payment.")
    print("    The Event set does not establish which renderer output was displayed.")

    # -- Readout 4: committed/declared-renderer mismatch -----------------------
    print("\n4. Readout 4 — view_hash comparison reports a mismatch")
    pinned = faithful_render   # the system pins a renderer and commits its output hash
    print("    This fixture profile commits a view_hash into the payload. A reader with the same")
    print("    action bytes and declared renderer can recompute it. This case commits the")
    print("    hash of the alternate authored output:")
    claimed = view_hash(v_adv)                       # hash of the adversarial view it showed
    b4 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T13:00:00Z",
                     refs=(mandate.id,), payload=action_payload(claimed))
    recomputed = recompute_view_hash(b4, pinned)
    print(f"    claimed_view_hash   = {claimed}")
    print(f"    recomputed (pinned) = {recomputed}")
    caught = claimed != recomputed
    print(f"    => {'MISMATCH' if caught else 'MATCH'} — the committed view does not match what the")
    print("       declared renderer produces from B. This detects the authored mismatch.")

    # -- Readout 5: matching hash with an omitted field ------------------------
    print("\n5. Readout 5 — MATCHING HASH WITH AN OMITTED FIELD")
    pinned_careful = careful_omit_render   # the PINNED renderer is itself reproducibly lossy
    v_omit = careful_omit_render(b1)
    matching_commit = view_hash(v_omit)              # commitment matching the pinned output
    b5 = signer.emit("AUTHORIZE", "consent.execute", "2026-06-14T14:00:00Z",
                     refs=(mandate.id,), payload=action_payload(matching_commit))
    led.record_view(b5.id, v_omit, b5)
    show_view("(pinned deterministic renderer)", v_omit)
    recomputed5 = recompute_view_hash(b5, pinned_careful)
    print(f"    claimed_view_hash   = {matching_commit}")
    print(f"    recomputed (pinned) = {recomputed5}")
    print(f"    => {'MATCH' if matching_commit == recomputed5 else 'mismatch'}; verify_log: ", end="")
    verify_log(led.events); print("passes.")
    print(f"    comparison fields present? {is_faithful(v_omit, b5)} — the payee line is omitted.")
    print("    The hash matches the declared renderer's output. It does not establish that")
    print("    this output was displayed, perceived, or semantically faithful.")

    # -- Readout 6: additional renderer claim ----------------------------------
    print("\n6. Readout 6 — ADDITIONAL RENDERER CLAIM")
    rv = renderer.emit("ATTEST", "view.rendered", "2026-06-14T14:30:00Z",
                       refs=(b5.id,),
                       payload={"action": b5.id, "view_hash": matching_commit})
    rr = resolve_view_from_log(led.events, b5.id)
    print(f"    rendered_view ATTEST added [{rv.id}]. resolve-view-from-log now: {rr['verdict']}")
    print(f"      ({rr['reason']})")
    print("    The rendered_view ATTEST is one more claim under this fixture profile.")
    print("    It does not establish which output was displayed or perceived.")

    print(f"\nGenerated log: {len(led.events)} mock-signed fixture Events; the listed replay checks pass.")
    verify_log(led.events)

    print("\n--- generator-only display mapping (observer folds do not receive this) ---")
    print("    action payload payee  ->  wallet:attacker (50000 KRW; no payment executed)")
    for aid, (view, faithful) in led.saw.items():
        first = view.splitlines()[0]
        shown_payee = "Merchant-A" if "Merchant-A" in view else ("(omitted)" if "to:" not in view else "wallet:attacker")
        mark = "FIELDS MATCH" if faithful else "FIELDS DIFFER/OMITTED"
        print(f"    [{aid}] authored output payee={shown_payee:<14} -> {mark}")
    print("    The Event set carries B, not an off-log rendering. This fixture compares")
    print("    view_hash only with the declared renderer output; it does not establish display.")

    print_finding()


def print_finding() -> None:
    print("""
What this probe exposes
-----------------------
  * What does the Event set establish about renderer output?
      It holds B and id=hash(B), not an off-log rendering. A view.rendered ATTEST,
      when present, is a claim carrying an output hash.
  * What does this fixture's view_hash comparison check?
      It compares a committed hash with the output of one declared deterministic
      renderer over the supplied action bytes.
  * What does a matching hash not establish?
      It does not establish which renderer ran, which output was displayed, or what
      a person perceived. The omitted-payee case matches its declared renderer.
  * Is this base ARC behavior?
      No. view_hash and the selected comparison fields belong to this fixture profile;
      they are not base-protocol requirements.

No new event type is introduced; a rendered_view attestation is an ordinary ATTEST
predicate in this fixture. This is a probe, not a protocol specification.
""")


if __name__ == "__main__":
    run()
